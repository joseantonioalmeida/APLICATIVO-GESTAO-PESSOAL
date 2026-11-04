"""Idempotência de cadastros (arquitetura §8.4, DEC-MV-15)."""

import enum
import hashlib
import json
import uuid
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import RequisicaoIdempotente
from api_gestao_pessoal.models.enums import SituacaoRequisicao
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import ContextoUsuario


class AcaoIdempotente(enum.StrEnum):
    """Ações que exigem `Idempotency-Key` (arquitetura §4.3)."""

    CADASTRAR_ATIVIDADE = "CADASTRAR_ATIVIDADE"
    CADASTRAR_IMPORTANCIA = "CADASTRAR_IMPORTANCIA"
    CADASTRAR_RECEITA = "CADASTRAR_RECEITA"
    CADASTRAR_DESPESA = "CADASTRAR_DESPESA"


@dataclass(frozen=True, slots=True)
class RespostaIdempotente:
    """Resposta a devolver: nova ou reaproveitada (`reexecucao`)."""

    status: int
    corpo: dict[str, Any]
    reexecucao: bool


def hash_do_conteudo(
    acao: AcaoIdempotente,
    parametros: Mapping[str, str],
    conteudo: BaseModel,
) -> str:
    """SHA-256 do conteúdo normalizado (a chave não entra no hash)."""
    canonico = json.dumps(
        {
            "acao": acao.value,
            "parametros": dict(parametros),
            "corpo": conteudo.model_dump(mode="json"),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonico.encode()).hexdigest()


async def executar_idempotente(  # noqa: PLR0913
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    *,
    acao: AcaoIdempotente,
    chave: str,
    conteudo: BaseModel,
    status_sucesso: int,
    operacao: Callable[[], Awaitable[BaseModel]],
    parametros: Mapping[str, str] | None = None,
) -> RespostaIdempotente:
    """Executa `operacao` uma única vez por `(usuário, ação, chave)`.

    Sob a trava EXCLUSIVA do usuário, registra a chave, executa e grava a
    resposta na mesma transação. Uma nova tentativa recebe o replay.
    """
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    conteudo_hash = hash_do_conteudo(acao, parametros or {}, conteudo)
    novo_id = await sessao.scalar(
        pg_insert(RequisicaoIdempotente)
        .values(
            id=uuid.uuid7(),
            usuario_id=contexto.usuario_id,
            chave=chave,
            acao=acao.value,
            conteudo_hash=conteudo_hash,
            situacao=SituacaoRequisicao.EM_PROCESSAMENTO,
        )
        .on_conflict_do_nothing(index_elements=["usuario_id", "acao", "chave"])
        .returning(RequisicaoIdempotente.id)
    )
    if novo_id is None:
        existente = await sessao.scalar(
            select(RequisicaoIdempotente).where(
                RequisicaoIdempotente.usuario_id == contexto.usuario_id,
                RequisicaoIdempotente.acao == acao.value,
                RequisicaoIdempotente.chave == chave,
            )
        )
        if existente is None:
            msg = "requisição idempotente desapareceu após o conflito"
            raise RuntimeError(msg)
        if existente.conteudo_hash != conteudo_hash:
            raise ErroNegocio(CodigoErro.CHAVE_IDEMPOTENCIA_REUTILIZADA)
        if (
            existente.situacao != SituacaoRequisicao.CONCLUIDA
            or existente.codigo_resposta is None
            or existente.resposta is None
        ):
            msg = "estado impossível: EM_PROCESSAMENTO confirmado"
            raise RuntimeError(msg)
        return RespostaIdempotente(
            existente.codigo_resposta, existente.resposta, reexecucao=True
        )
    resposta = await operacao()
    corpo = resposta.model_dump(mode="json")
    await sessao.execute(
        update(RequisicaoIdempotente)
        .where(RequisicaoIdempotente.id == novo_id)
        .values(
            situacao=SituacaoRequisicao.CONCLUIDA,
            codigo_resposta=status_sucesso,
            resposta=corpo,
            concluida_em=contexto.agora,
        )
    )
    return RespostaIdempotente(status_sucesso, corpo, reexecucao=False)
