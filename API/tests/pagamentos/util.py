"""Auxiliares dos testes de pagamentos (vínculo despesa-importância)."""

from http import HTTPStatus
from typing import Any

import httpx

from ..apoio.api import UsuarioTeste, chave_nova
from ..financeiro.util import BASE
from ..financeiro.util import categoria as categoria_financeira
from ..importancias.util import URL as URL_IMP
from ..importancias.util import criar as criar_importancia
from ..importancias.util import obter as obter_importancia

__all__ = [
    "BASE",
    "URL_IMP",
    "criar_conta",
    "obter_importancia",
    "pagar",
    "despesa_avulsa",
    "resumo",
]


async def criar_conta(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, **campos: Any
) -> dict[str, Any]:
    """Importância com despesa (padrão: internet de R$ 99,90 em 20/10)."""
    dados = {
        "nome": "Pagamento da internet",
        "possui_despesa": True,
        "valor_previsto": "99.90",
        "data_compromisso": "2026-10-20",
    } | campos
    return await criar_importancia(cliente, usuario, **dados)


async def pagar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    importancia_id: str | None,
    *,
    esperado: int = HTTPStatus.CREATED,
    chave: str | None = None,
    **campos: Any,
) -> httpx.Response:
    """POST de despesa (com ou sem vínculo); devolve a resposta HTTP."""
    corpo: dict[str, Any] = {
        "nome": "Pagamento da internet",
        "valor": "105.00",
        "categoria_id": await categoria_financeira(
            cliente, usuario, "DESPESA", "Contas"
        ),
        "data_movimentacao": "2026-10-13",
    } | campos
    if importancia_id is not None:
        corpo["importancia_id"] = importancia_id
    r = await cliente.post(
        f"{BASE}/despesas",
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )
    assert r.status_code == esperado, r.text
    return r


async def despesa_avulsa(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, **campos: Any
) -> dict[str, Any]:
    r = await pagar(cliente, usuario, None, **campos)
    return r.json()


async def resumo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, mes: str = "2026-10"
) -> dict[str, Any]:
    r = await cliente.get(
        f"{BASE}/resumo", params={"mes": mes}, headers=usuario.cabecalhos
    )
    return r.json()
