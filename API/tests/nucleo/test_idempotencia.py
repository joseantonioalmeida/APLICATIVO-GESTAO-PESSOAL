import asyncio
from http import HTTPStatus

import httpx

from ..apoio.api import chave_nova, criar_usuario
from ..apoio.esquema import consultar
from ..apoio.identidade import codigo_de_erro

URL = "/teste-nucleo/registros"


def contar_registros(banco: str) -> int:
    return len(consultar(banco, "SELECT id FROM teste_nucleo_registro"))


def contar_requisicoes(banco: str) -> int:
    return len(consultar(banco, "SELECT id FROM requisicao_idempotente"))


async def test_chave_ausente_e_invalida(cliente: httpx.AsyncClient) -> None:
    usuario = await criar_usuario(cliente)
    ausente = await cliente.post(
        URL, json={"valor": "a"}, headers=usuario.cabecalhos
    )
    assert ausente.status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(ausente) == "IDEMPOTENCIA_CHAVE_AUSENTE"
    for chave in ("curta", "x" * 65, "com espaco 1234567890123"):
        invalida = await cliente.post(
            URL,
            json={"valor": "a"},
            headers={**usuario.cabecalhos, "Idempotency-Key": chave},
        )
        assert invalida.status_code == HTTPStatus.BAD_REQUEST
        assert codigo_de_erro(invalida) == "IDEMPOTENCIA_CHAVE_INVALIDA"


async def test_mesma_chave_um_unico_efeito_e_replay_identico(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    usuario = await criar_usuario(cliente)
    cab = {**usuario.cabecalhos, "Idempotency-Key": chave_nova()}
    primeira = await cliente.post(URL, json={"valor": "a"}, headers=cab)
    segunda = await cliente.post(URL, json={"valor": "a"}, headers=cab)
    assert primeira.status_code == segunda.status_code == HTTPStatus.CREATED
    assert "Idempotency-Replayed" not in primeira.headers
    assert segunda.headers["Idempotency-Replayed"] == "true"
    assert primeira.content == segunda.content
    assert contar_registros(banco_migrado) == 1
    assert contar_requisicoes(banco_migrado) == 1


async def test_mesma_chave_outro_conteudo(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    usuario = await criar_usuario(cliente)
    cab = {**usuario.cabecalhos, "Idempotency-Key": chave_nova()}
    await cliente.post(URL, json={"valor": "a"}, headers=cab)
    for _ in range(2):
        outra = await cliente.post(URL, json={"valor": "b"}, headers=cab)
        assert outra.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert codigo_de_erro(outra) == "CHAVE_IDEMPOTENCIA_REUTILIZADA"
    assert contar_registros(banco_migrado) == 1


async def test_chaves_distintas_sao_cadastros_distintos(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    usuario = await criar_usuario(cliente)
    for _ in range(2):
        cab = {**usuario.cabecalhos, "Idempotency-Key": chave_nova()}
        resposta = await cliente.post(
            URL, json={"valor": "igual"}, headers=cab
        )
        assert resposta.status_code == HTTPStatus.CREATED
    assert contar_registros(banco_migrado) == 2


async def test_chave_e_por_usuario(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    chave = chave_nova()
    for _ in range(2):
        usuario = await criar_usuario(cliente)
        resposta = await cliente.post(
            URL,
            json={"valor": "a"},
            headers={**usuario.cabecalhos, "Idempotency-Key": chave},
        )
        assert resposta.status_code == HTTPStatus.CREATED
        assert "Idempotency-Replayed" not in resposta.headers
    assert contar_registros(banco_migrado) == 2


async def test_falha_nao_deixa_efeito_nem_registro(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    usuario = await criar_usuario(cliente)
    cab = {**usuario.cabecalhos, "Idempotency-Key": chave_nova()}
    falha = await cliente.post(
        URL, params={"falhar": "true"}, json={"valor": "a"}, headers=cab
    )
    assert falha.status_code == HTTPStatus.NOT_FOUND
    assert contar_registros(banco_migrado) == 0
    assert contar_requisicoes(banco_migrado) == 0
    # Nova tentativa com a mesma chave reavalia o estado e executa.
    ok = await cliente.post(URL, json={"valor": "a"}, headers=cab)
    assert ok.status_code == HTTPStatus.CREATED
    assert contar_registros(banco_migrado) == 1


async def test_envios_simultaneos_com_a_mesma_chave(
    cliente: httpx.AsyncClient, banco_migrado: str
) -> None:
    usuario = await criar_usuario(cliente)
    cab = {**usuario.cabecalhos, "Idempotency-Key": chave_nova()}
    respostas = await asyncio.gather(*[
        cliente.post(URL, json={"valor": "a"}, headers=cab) for _ in range(5)
    ])
    assert {r.status_code for r in respostas} == {HTTPStatus.CREATED}
    assert len({r.content for r in respostas}) == 1
    assert sum("Idempotency-Replayed" in r.headers for r in respostas) == 4
    assert contar_registros(banco_migrado) == 1
