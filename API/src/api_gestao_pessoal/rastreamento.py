import logging
import re
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import override

from fastapi import Request, Response

ID_REQUISICAO: ContextVar[str | None] = ContextVar(
    "id_requisicao", default=None
)
PADRAO_ID_REQUISICAO = re.compile(r"^[A-Za-z0-9-]{8,64}$")
CABECALHO_ID_REQUISICAO = "X-Request-ID"
NOME_LOGGER = "api_gestao_pessoal"
FORMATO_LOG = (
    "%(asctime)s %(levelname)s %(name)s [%(id_requisicao)s] %(message)s"
)
_MARCA_HANDLER = "_handler_api_gestao_pessoal"


async def middleware_id_requisicao(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    recebido = request.headers.get(CABECALHO_ID_REQUISICAO, "")
    if PADRAO_ID_REQUISICAO.match(recebido):
        valor = recebido
    else:
        valor = uuid.uuid4().hex
    request.state.id_requisicao = valor
    token = ID_REQUISICAO.set(valor)
    try:
        resposta = await call_next(request)
        resposta.headers[CABECALHO_ID_REQUISICAO] = valor
        return resposta
    finally:
        ID_REQUISICAO.reset(token)


class FiltroIdRequisicao(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "id_requisicao"):
            record.id_requisicao = ID_REQUISICAO.get() or "-"
        return True


def configurar_logging(nivel: str) -> None:
    """Configura o logger da aplicação de forma idempotente."""
    logger = logging.getLogger(NOME_LOGGER)
    logger.setLevel(nivel)
    logger.propagate = True
    if any(getattr(h, _MARCA_HANDLER, False) for h in logger.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(FORMATO_LOG))
    handler.addFilter(FiltroIdRequisicao())
    setattr(handler, _MARCA_HANDLER, True)
    logger.addHandler(handler)
