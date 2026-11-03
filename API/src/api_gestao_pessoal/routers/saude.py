import asyncio
import logging

from fastapi import APIRouter, Request
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.schemas.saude import SituacaoSaude

logger = logging.getLogger(__name__)

TIMEOUT_PRONTO_S = 2

router = APIRouter(tags=["saúde"])


@router.get("/saude")
async def saude() -> SituacaoSaude:
    return SituacaoSaude(situacao="ativo")


@router.get("/saude/pronto")
async def saude_pronto(request: Request) -> SituacaoSaude:
    try:
        async with asyncio.timeout(TIMEOUT_PRONTO_S):
            async with request.app.state.engine.connect() as conexao:
                await conexao.execute(text("SELECT 1"))
    except (DBAPIError, OSError, TimeoutError) as exc:
        logger.warning(
            "banco indisponível na verificação de prontidão: %s",
            type(exc).__name__,
        )
        raise ErroNegocio(CodigoErro.SERVICO_INDISPONIVEL) from None
    return SituacaoSaude(situacao="pronto")
