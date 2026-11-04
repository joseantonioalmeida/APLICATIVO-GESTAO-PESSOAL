from http import HTTPStatus

import httpx
import psycopg

from ..apoio.api import criar_usuario
from ..apoio.banco import url_libpq

URL = "/api/v1/categorias"


async def test_exige_autenticacao(cliente: httpx.AsyncClient) -> None:
    for caminho in ("atividades", "importancias", "financeiras?tipo=DESPESA"):
        resposta = await cliente.get(f"{URL}/{caminho}")
        assert resposta.status_code == HTTPStatus.UNAUTHORIZED


async def test_atividades_com_outros_por_ultimo(
    cliente: httpx.AsyncClient,
) -> None:
    usuario = await criar_usuario(cliente)
    resposta = await cliente.get(
        f"{URL}/atividades", headers=usuario.cabecalhos
    )
    assert resposta.status_code == HTTPStatus.OK
    nomes = [c["nome"] for c in resposta.json()]
    assert nomes == [
        "Estudo",
        "Lazer",
        "Pessoal",
        "Saúde",
        "Trabalho",
        "Outros",
    ]
    assert set(resposta.json()[0]) == {"id", "nome"}


async def test_importancias(cliente: httpx.AsyncClient) -> None:
    usuario = await criar_usuario(cliente)
    resposta = await cliente.get(
        f"{URL}/importancias", headers=usuario.cabecalhos
    )
    nomes = [c["nome"] for c in resposta.json()]
    assert len(nomes) == 8
    assert nomes[-1] == "Outros"
    assert "Contas" in nomes


async def test_financeiras_por_tipo(cliente: httpx.AsyncClient) -> None:
    usuario = await criar_usuario(cliente)
    receitas = await cliente.get(
        f"{URL}/financeiras",
        params={"tipo": "RECEITA"},
        headers=usuario.cabecalhos,
    )
    despesas = await cliente.get(
        f"{URL}/financeiras",
        params={"tipo": "DESPESA"},
        headers=usuario.cabecalhos,
    )
    assert [c["nome"] for c in receitas.json()][-1] == "Outros"
    assert {c["tipo"] for c in receitas.json()} == {"RECEITA"}
    assert {c["tipo"] for c in despesas.json()} == {"DESPESA"}
    assert len(receitas.json()) == 6
    assert len(despesas.json()) == 10


async def test_tipo_obrigatorio_e_validado(cliente: httpx.AsyncClient) -> None:
    usuario = await criar_usuario(cliente)
    ausente = await cliente.get(
        f"{URL}/financeiras", headers=usuario.cabecalhos
    )
    assert ausente.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    invalido = await cliente.get(
        f"{URL}/financeiras", params={"tipo": "X"}, headers=usuario.cabecalhos
    )
    assert invalido.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_categoria_inativa_nao_aparece(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    usuario = await criar_usuario(cliente)
    with psycopg.connect(url_libpq(banco_migrado), autocommit=True) as c:
        c.execute(
            "UPDATE categoria_atividade SET ativa = false WHERE nome='Lazer'"
        )
    try:
        resposta = await cliente.get(
            f"{URL}/atividades", headers=usuario.cabecalhos
        )
        assert "Lazer" not in [c["nome"] for c in resposta.json()]
    finally:
        with psycopg.connect(url_libpq(banco_migrado), autocommit=True) as c:
            c.execute(
                "UPDATE categoria_atividade SET ativa = true "
                "WHERE nome = 'Lazer'"
            )
