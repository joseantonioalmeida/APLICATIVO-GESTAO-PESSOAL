"""Endpoints de notificações (F9)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ContextoDep
from api_gestao_pessoal.schemas.comum import Pagina
from api_gestao_pessoal.schemas.notificacao import (
    NaoLidasResposta,
    NotificacaoItem,
)
from api_gestao_pessoal.services import notificacoes
from api_gestao_pessoal.services.paginacao import (
    LIMITE_MAXIMO,
    LIMITE_PADRAO,
)

router = APIRouter(prefix="/notificacoes", tags=["notificações"])

# Rota estática antes das rotas com `{id}` (arquitetura §9).


@router.get("")
async def listar_notificacoes(
    sessao: SessaoDep,
    contexto: ContextoDep,
    limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PADRAO,
    cursor: Annotated[str | None, Query()] = None,
) -> Pagina[NotificacaoItem]:
    return await notificacoes.listar(
        sessao, contexto, limite=limite, cursor=cursor
    )


@router.get("/nao-lidas")
async def notificacoes_nao_lidas(
    sessao: SessaoDep, contexto: ContextoDep
) -> NaoLidasResposta:
    return await notificacoes.contar_nao_lidas(sessao, contexto)


@router.post("/{notificacao_id}/leitura")
async def marcar_como_lida(
    notificacao_id: uuid.UUID, sessao: SessaoDep, contexto: ContextoDep
) -> NotificacaoItem:
    resposta = await notificacoes.marcar_lida(sessao, contexto, notificacao_id)
    await sessao.commit()
    return resposta
