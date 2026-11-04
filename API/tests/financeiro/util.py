"""Auxiliares dos testes do financeiro."""

from http import HTTPStatus
from typing import Any

import httpx

from ..apoio.api import UsuarioTeste, chave_nova

BASE = "/api/v1/financeiro"
HOJE = "2026-10-13"


async def categoria(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    tipo: str,
    nome: str,
) -> str:
    r = await cliente.get(
        "/api/v1/categorias/financeiras",
        params={"tipo": tipo},
        headers=usuario.cabecalhos,
    )
    return next(c["id"] for c in r.json() if c["nome"] == nome)


async def receita(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    *,
    esperado: int = HTTPStatus.CREATED,
    chave: str | None = None,
    **campos: Any,
) -> dict[str, Any]:
    corpo: dict[str, Any] = {
        "nome": "Salário",
        "valor": "2450.75",
        "categoria_id": await categoria(
            cliente, usuario, "RECEITA", "Salário"
        ),
        "data_movimentacao": HOJE,
    } | campos
    r = await cliente.post(
        f"{BASE}/receitas",
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )
    assert r.status_code == esperado, r.text
    return r.json()


async def despesa(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    *,
    esperado: int = HTTPStatus.CREATED,
    chave: str | None = None,
    categoria_nome: str = "Alimentação",
    **campos: Any,
) -> dict[str, Any]:
    corpo: dict[str, Any] = {
        "nome": "Mercado",
        "valor": "245.30",
        "categoria_id": await categoria(
            cliente, usuario, "DESPESA", categoria_nome
        ),
        "data_movimentacao": HOJE,
    } | campos
    r = await cliente.post(
        f"{BASE}/despesas",
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )
    assert r.status_code == esperado, r.text
    return r.json()


async def resumo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, mes: str | None = None
) -> dict[str, Any]:
    params = {"mes": mes} if mes else {}
    r = await cliente.get(
        f"{BASE}/resumo", params=params, headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()


async def movimentacoes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, **params: Any
) -> dict[str, Any]:
    r = await cliente.get(
        f"{BASE}/movimentacoes", params=params, headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()
