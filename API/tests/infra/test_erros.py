import logging
import re
from http import HTTPStatus

import pytest
from fastapi import FastAPI

from api_gestao_pessoal.erros import CodigoErro

from ..conftest import FabricaCliente

ID_ENVIADO = "teste-12345678"
SEGREDO = "segredo-super-123"
TAMANHO_ID_GERADO = 32
PADRAO_ID_GERADO = re.compile(rf"^[0-9a-f]{{{TAMANHO_ID_GERADO}}}$")


async def test_erro_negocio_formato(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.get(
            "/teste/erro-negocio", headers={"X-Request-ID": ID_ENVIADO}
        )
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert resposta.headers["X-Teste"] == "1"
    assert resposta.headers["X-Request-ID"] == ID_ENVIADO
    assert resposta.json() == {
        "codigo": "VALIDACAO",
        "mensagem": "Mensagem de teste",
        "campos": [
            {
                "campo": "nome",
                "codigo": "NOME_OBRIGATORIO",
                "mensagem": "Informe o nome",
            }
        ],
        "detalhes": {"chave": "valor"},
        "id_requisicao": ID_ENVIADO,
    }


async def test_validacao_sem_eco(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.post(
            "/teste/validacao",
            json={"nome": "ab", "senha": SEGREDO, "quantidade": "x"},
        )
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    corpo = resposta.json()
    assert corpo["codigo"] == CodigoErro.VALIDACAO
    pares = {(c["campo"], c["codigo"]) for c in corpo["campos"]}
    assert ("nome", "TAMANHO_MINIMO") in pares
    assert ("quantidade", "FORMATO_INVALIDO") in pares
    assert SEGREDO not in resposta.text


async def test_corpo_malformado(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.post(
            "/teste/validacao",
            content="{",
            headers={"Content-Type": "application/json"},
        )
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    corpo = resposta.json()
    assert corpo["codigo"] == CodigoErro.CORPO_INVALIDO
    assert corpo["campos"] == []


async def test_rota_inexistente(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.get("/nao-existe")
    assert resposta.status_code == HTTPStatus.NOT_FOUND
    assert resposta.json()["codigo"] == CodigoErro.RECURSO_NAO_ENCONTRADO


async def test_metodo_nao_permitido(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.delete("/saude")
    assert resposta.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert resposta.json()["codigo"] == CodigoErro.METODO_NAO_PERMITIDO
    assert "GET" in resposta.headers["Allow"]


async def test_excecao_inesperada(
    app_teste: FastAPI,
    criar_cliente: FabricaCliente,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR, logger="api_gestao_pessoal"):
        async with criar_cliente(app_teste) as cliente:
            resposta = await cliente.get(
                "/teste/excecao", headers={"X-Request-ID": ID_ENVIADO}
            )
    assert resposta.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resposta.json()["codigo"] == CodigoErro.ERRO_INTERNO
    assert "falha interna de teste" not in resposta.text
    assert "Traceback" in caplog.text
    assert "falha interna de teste" in caplog.text
    assert any(
        getattr(r, "id_requisicao", None) == ID_ENVIADO for r in caplog.records
    )


async def test_id_requisicao_propagado_e_gerado(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        valido = await cliente.get(
            "/saude", headers={"X-Request-ID": ID_ENVIADO}
        )
        ausente = await cliente.get("/saude")
        invalido = await cliente.get("/saude", headers={"X-Request-ID": "x"})
    assert valido.headers["X-Request-ID"] == ID_ENVIADO
    assert PADRAO_ID_GERADO.match(ausente.headers["X-Request-ID"])
    assert PADRAO_ID_GERADO.match(invalido.headers["X-Request-ID"])
