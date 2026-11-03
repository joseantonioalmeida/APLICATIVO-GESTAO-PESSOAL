import logging
from collections.abc import Callable
from http import HTTPStatus

import psycopg
import pytest
from fastapi import FastAPI

from api_gestao_pessoal.erros import CodigoErro
from api_gestao_pessoal.rastreamento import FORMATO_LOG
from api_gestao_pessoal.settings import Settings

from ..apoio.banco import url_libpq
from ..apoio.rotas_teste import (
    CHAVE_TRAVA,
    SENTINELA_LINHA,
    SENTINELA_UNICO,
    criar_app_teste,
)
from ..conftest import FabricaCliente

pytestmark = pytest.mark.usefixtures("limpar_registros")

LOCK_TIMEOUT_CURTO_MS = 200
ID_REGRESSAO_LOG = "regressao-log-0001"


async def test_commit_no_router_persiste(
    app_teste: FastAPI,
    criar_cliente: FabricaCliente,
    contar_registros: Callable[[], int],
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.post("/teste/registros", json={"valor": "a"})
    assert resposta.status_code == HTTPStatus.CREATED
    assert contar_registros() == 1


async def test_erro_apos_escrita_desfaz(
    app_teste: FastAPI,
    criar_cliente: FabricaCliente,
    contar_registros: Callable[[], int],
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.post("/teste/registros/erro-apos-escrita")
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert resposta.json()["mensagem"] == "erro de teste"
    assert contar_registros() == 0


async def test_dependencia_e_endpoint_mesma_sessao(
    app_teste: FastAPI,
    criar_cliente: FabricaCliente,
    contar_registros: Callable[[], int],
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.post("/teste/registros/com-dependencia")
    assert resposta.status_code == HTTPStatus.CREATED
    assert resposta.json()["mesma_sessao"] is True
    assert contar_registros() == 1


async def test_falha_no_commit_nao_responde_sucesso(
    app_teste: FastAPI,
    criar_cliente: FabricaCliente,
    contar_registros: Callable[[], int],
) -> None:
    async with criar_cliente(app_teste) as cliente:
        resposta = await cliente.post("/teste/registros/falha-no-commit")
    assert resposta.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resposta.json()["codigo"] == CodigoErro.ERRO_INTERNO
    assert contar_registros() == 0


async def test_conexoes_devolvidas_ao_pool(
    app_teste: FastAPI, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(app_teste) as cliente:
        sucesso = await cliente.post("/teste/registros", json={"valor": "a"})
        erro = await cliente.post("/teste/registros/erro-apos-escrita")
        assert sucesso.status_code == HTTPStatus.CREATED
        assert erro.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
        assert app_teste.state.engine.pool.checkedout() == 0


@pytest.mark.concorrencia
async def test_lock_timeout_vira_503(
    settings_teste: Settings,
    criar_cliente: FabricaCliente,
    url_banco_teste: str,
) -> None:
    ajustada = settings_teste.model_copy(
        update={"DB_LOCK_TIMEOUT_MS": LOCK_TIMEOUT_CURTO_MS}
    )
    app = criar_app_teste(ajustada)
    with psycopg.connect(url_libpq(url_banco_teste), autocommit=True) as lock:
        lock.execute("SELECT pg_advisory_lock(%s)", (CHAVE_TRAVA,))
        async with criar_cliente(app) as cliente:
            bloqueada = await cliente.post("/teste/trava")
            lock.execute("SELECT pg_advisory_unlock(%s)", (CHAVE_TRAVA,))
            liberada = await cliente.post("/teste/trava")
    assert bloqueada.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert bloqueada.json()["codigo"] == CodigoErro.CONFLITO_CONCORRENCIA
    assert bloqueada.headers["Retry-After"] == "1"
    assert liberada.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ("rota", "esperados"),
    [
        (
            "/teste/registros/falha-no-commit",
            ("sqlstate=23505", "restricao=uq_registro_unico"),
        ),
        (
            "/teste/registros/violacao-nao-nulo",
            ("sqlstate=23502", "coluna=valor"),
        ),
    ],
)
async def test_erro_banco_500_sem_valores_no_log(
    app_teste: FastAPI,
    criar_cliente: FabricaCliente,
    caplog: pytest.LogCaptureFixture,
    rota: str,
    esperados: tuple[str, str],
) -> None:
    with caplog.at_level(logging.ERROR, logger="api_gestao_pessoal"):
        async with criar_cliente(app_teste) as cliente:
            resposta = await cliente.post(
                rota, headers={"X-Request-ID": ID_REGRESSAO_LOG}
            )
    assert resposta.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resposta.json()["codigo"] == CodigoErro.ERRO_INTERNO
    registros = [
        r for r in caplog.records if r.name == "api_gestao_pessoal.erros"
    ]
    assert registros, "o erro de banco não foi registrado"
    formatador = logging.Formatter(FORMATO_LOG)
    saida = "\n".join(formatador.format(r) for r in registros)
    saida += "\n" + caplog.text
    for sentinela in (SENTINELA_UNICO, SENTINELA_LINHA):
        assert sentinela not in saida
        assert sentinela not in resposta.text
    assert "DETAIL" not in saida
    for trecho in esperados:
        assert trecho in saida
    assert f"[{ID_REGRESSAO_LOG}]" in saida
