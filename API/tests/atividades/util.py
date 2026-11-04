"""Auxiliares dos testes de atividades."""

from http import HTTPStatus
from typing import Any

import httpx

from ..apoio.api import UsuarioTeste, chave_nova

URL = "/api/v1/atividades"
HOJE = "2026-10-13"


async def categoria(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, nome: str = "Estudo"
) -> str:
    resposta = await cliente.get(
        "/api/v1/categorias/atividades", headers=usuario.cabecalhos
    )
    return next(c["id"] for c in resposta.json() if c["nome"] == nome)


async def criar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    *,
    esperado: int = HTTPStatus.CREATED,
    chave: str | None = None,
    **campos: Any,
) -> dict[str, Any]:
    """POST de atividade com padrões válidos; devolve o corpo."""
    corpo: dict[str, Any] = {
        "nome": "Estudar para a prova",
        "categoria_id": await categoria(cliente, usuario),
        "data": HOJE,
        "horario_inicial": "08:00",
        "horario_final": "10:00",
        "confirmar_sobreposicao": True,
    } | campos
    resposta = await cliente.post(
        URL,
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )
    assert resposta.status_code == esperado, resposta.text
    return resposta.json()


async def listar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    **params: Any,
) -> dict[str, Any]:
    resposta = await cliente.get(
        URL, params={"data": HOJE} | params, headers=usuario.cabecalhos
    )
    assert resposta.status_code == HTTPStatus.OK, resposta.text
    return resposta.json()


async def nomes_do_dia(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, data: str
) -> list[str]:
    dia = await listar(cliente, usuario, data=data, limite=50)
    return [i["nome"] for i in dia["itens"]]


def campo_de_erro(corpo: dict[str, Any]) -> dict[str, str]:
    """`{campo: codigo}` dos erros de validação."""
    return {c["campo"]: c["codigo"] for c in corpo["campos"]}
