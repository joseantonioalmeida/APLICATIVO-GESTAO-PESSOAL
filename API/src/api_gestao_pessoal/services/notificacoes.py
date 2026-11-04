"""Leitura e marcação de notificações internas (§8.6.5).

As notificações são criadas pelo processador de lembretes. Aqui só se
listam, contam e marcam como lidas; ler não conclui nem paga nada (4.1.9).
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import (
    Importancia,
    LembreteImportancia,
    Notificacao,
)
from api_gestao_pessoal.schemas.comum import Pagina
from api_gestao_pessoal.schemas.notificacao import (
    ImportanciaDaNotificacao,
    NaoLidasResposta,
    NotificacaoItem,
)
from api_gestao_pessoal.services.paginacao import (
    codificar_cursor,
    decodificar_cursor,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import ContextoUsuario

ORDENACAO = "criada_em_desc"


def _consulta() -> Any:  # noqa: ANN401
    return (
        select(Notificacao, Importancia.id, Importancia.excluida_em)
        .join(
            LembreteImportancia,
            LembreteImportancia.id == Notificacao.lembrete_id,
        )
        .join(
            Importancia, Importancia.id == LembreteImportancia.importancia_id
        )
    )


def _item(linha: Any) -> NotificacaoItem:  # noqa: ANN401
    notificacao, importancia_id, excluida_em = linha
    return NotificacaoItem(
        id=notificacao.id,
        titulo=notificacao.titulo,
        mensagem=notificacao.mensagem,
        criada_em=notificacao.criada_em,
        lida=notificacao.lida_em is not None,
        importancia=ImportanciaDaNotificacao(
            id=importancia_id, disponivel=excluida_em is None
        ),
    )


async def listar(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    *,
    limite: int,
    cursor: str | None,
) -> Pagina[NotificacaoItem]:
    """Mais recentes primeiro, com paginação keyset."""
    consulta = _consulta().where(Notificacao.usuario_id == contexto.usuario_id)
    if cursor is not None:
        chaves = decodificar_cursor(cursor, ORDENACAO, {})
        try:
            criada = datetime.fromisoformat(chaves[0])
            ultimo_id = uuid.UUID(chaves[1])
        except (ValueError, TypeError, IndexError) as exc:
            raise ErroNegocio(CodigoErro.CURSOR_INVALIDO) from exc
        consulta = consulta.where(
            tuple_(Notificacao.criada_em, Notificacao.id) < (criada, ultimo_id)
        )
    linhas: list[Any] = list(
        (
            await sessao.execute(
                consulta.order_by(
                    Notificacao.criada_em.desc(), Notificacao.id.desc()
                ).limit(limite + 1)
            )
        ).all()
    )
    pagina = linhas[:limite]
    proximo = None
    if len(linhas) > limite:
        ultima = pagina[-1][0]
        proximo = codificar_cursor(
            ORDENACAO, {}, [ultima.criada_em.isoformat(), str(ultima.id)]
        )
    return Pagina(itens=[_item(x) for x in pagina], proximo_cursor=proximo)


async def contar_nao_lidas(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> NaoLidasResposta:
    """Notificações com `lida_em` nulo."""
    total = await sessao.scalar(
        select(func.count()).where(
            Notificacao.usuario_id == contexto.usuario_id,
            Notificacao.lida_em.is_(None),
        )
    )
    return NaoLidasResposta(quantidade=int(total or 0))


async def marcar_lida(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    notificacao_id: uuid.UUID,
) -> NotificacaoItem:
    """Define `lida_em` se nulo (idempotente); não altera a importância."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    linha = (
        await sessao.execute(
            _consulta().where(
                Notificacao.id == notificacao_id,
                Notificacao.usuario_id == contexto.usuario_id,
            )
        )
    ).first()
    if linha is None:
        raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
    if linha[0].lida_em is None:
        linha[0].lida_em = contexto.agora
        await sessao.flush()
    return _item(linha)
