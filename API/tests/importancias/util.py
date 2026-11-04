"""Auxiliares dos testes de importâncias."""

from http import HTTPStatus
from typing import Any

import httpx
import psycopg

from ..apoio.api import UsuarioTeste, chave_nova
from ..apoio.banco import url_libpq

URL = "/api/v1/importancias"
HOJE = "2026-10-13"


async def categoria(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, nome: str = "Contas"
) -> str:
    r = await cliente.get(
        "/api/v1/categorias/importancias", headers=usuario.cabecalhos
    )
    return next(c["id"] for c in r.json() if c["nome"] == nome)


async def criar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    *,
    esperado: int = HTTPStatus.CREATED,
    chave: str | None = None,
    **campos: Any,
) -> dict[str, Any]:
    corpo: dict[str, Any] = {
        "nome": "Pagamento da internet",
        "categoria_id": await categoria(cliente, usuario),
        "data_compromisso": "2026-10-20",
    } | campos
    r = await cliente.post(
        URL,
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )
    assert r.status_code == esperado, r.text
    return r.json()


async def listar(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, **params: Any
) -> dict[str, Any]:
    r = await cliente.get(URL, params=params, headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()


async def nomes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, **params: Any
) -> list[str]:
    return [
        i["nome"]
        for i in (await listar(cliente, usuario, limite=50, **params))["itens"]
    ]


async def obter(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, id_: str
) -> dict[str, Any]:
    r = await cliente.get(f"{URL}/{id_}", headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()


async def situacao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, id_: str, valor: str
) -> httpx.Response:
    return await cliente.put(
        f"{URL}/{id_}/situacao",
        json={"situacao": valor},
        headers=usuario.cabecalhos,
    )


def lembretes_no_banco(banco: str, importancia_id: str) -> list[tuple]:
    """`(situacao, versao, agendado_para, enviado_em)` do lembrete."""
    with psycopg.connect(url_libpq(banco)) as conexao:
        linhas = conexao.execute(
            "SELECT situacao, versao_agendamento, agendado_para, enviado_em "
            "FROM lembrete_importancia WHERE importancia_id = %s",
            (importancia_id,),
        )
        return [tuple(linha) for linha in linhas]


def campo_de_erro(corpo: dict[str, Any]) -> dict[str, str]:
    return {c["campo"]: c["codigo"] for c in corpo["campos"]}
