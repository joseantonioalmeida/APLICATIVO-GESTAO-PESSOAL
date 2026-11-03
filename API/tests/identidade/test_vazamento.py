import io
import json
import logging
from collections.abc import Iterator
from datetime import timedelta
from http import HTTPStatus
from typing import Any

import httpx
import pytest
from fastapi import APIRouter, FastAPI

from api_gestao_pessoal import seguranca
from api_gestao_pessoal.dependencias import (
    obter_enviador_email,
    obter_relogio,
)
from api_gestao_pessoal.email import EnviadorEmailMemoria, FalhaEnvioEmail
from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.rastreamento import (
    FORMATO_LOG,
    NOME_LOGGER,
    FiltroIdRequisicao,
)
from api_gestao_pessoal.settings import Settings

from ..apoio.identidade import (
    URL_LOGIN,
    URL_REGISTRO,
    URL_USUARIO_ATUAL,
    SequenciaCodigos,
    redefinir,
    solicitar,
    verificar,
)
from ..apoio.relogio import RelogioFixo
from .conftest import Ambiente
from .rotas_teste_identidade import router as router_contexto

NOME = "Sentinela Nome Silva"
EMAIL = "sentinela.email@exemplo.com"
SENHA = "Sentinela-Senha-9x!"
NOVA_SENHA = "Sentinela-Nova-7q!"
CODIGO = "48151623"
CHAVES_ERRO = {"codigo", "mensagem", "campos", "detalhes", "id_requisicao"}

router_falhas = APIRouter(prefix="/teste-falhas")


@router_falhas.get("/inesperado")
async def erro_inesperado() -> None:
    msg = "falha sintética sem dados"
    raise RuntimeError(msg)


@router_falhas.get("/envio")
async def falha_de_envio() -> None:
    raise FalhaEnvioEmail("SMTPException")


@pytest.fixture
def app_identidade(
    settings_teste: Settings,
    relogio: RelogioFixo,
    enviador: EnviadorEmailMemoria,
) -> FastAPI:
    """App com log em DEBUG e as rotas de falha (substitui a do conftest)."""
    app = criar_app(settings_teste.model_copy(update={"LOG_NIVEL": "DEBUG"}))
    app.include_router(router_contexto)
    app.include_router(router_falhas)
    app.dependency_overrides[obter_relogio] = lambda: relogio
    app.dependency_overrides[obter_enviador_email] = lambda: enviador
    return app


@pytest.fixture
def saida_formatada() -> Iterator[io.StringIO]:
    """Saída do logger real, com o formato e o filtro da aplicação."""
    fluxo = io.StringIO()
    handler = logging.StreamHandler(fluxo)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(FORMATO_LOG))
    handler.addFilter(FiltroIdRequisicao())
    logger = logging.getLogger(NOME_LOGGER)
    logger.addHandler(handler)
    yield fluxo
    logger.removeHandler(handler)


class Verificador:
    """Confere que valores sensíveis só aparecem onde são permitidos."""

    def __init__(self) -> None:
        self.sentinelas = [NOME, EMAIL, SENHA, NOVA_SENHA, CODIGO]

    def sucesso(
        self, resposta: httpx.Response, chaves: set[str], permitidos: set[str]
    ) -> dict[str, Any]:
        assert resposta.status_code < HTTPStatus.BAD_REQUEST, resposta.text
        corpo = resposta.json()
        assert set(corpo) == chaves
        restante = {k: v for k, v in corpo.items() if k not in permitidos}
        for valor in self.sentinelas:
            assert valor not in json.dumps(restante, ensure_ascii=False)
        return corpo

    def erro(self, resposta: httpx.Response, status: int) -> None:
        assert resposta.status_code == status
        assert set(resposta.json()) == CHAVES_ERRO
        assert resposta.json()["detalhes"] is None
        for valor in self.sentinelas:
            assert valor not in resposta.text


async def fluxo_cadastro_e_login(
    cliente: httpx.AsyncClient, verificador: Verificador
) -> str:
    corpo = {
        "nome_completo": NOME,
        "email": EMAIL,
        "senha": SENHA,
        "confirmar_senha": SENHA,
        "data_nascimento": "1990-01-01",
        "fuso_horario": "America/Sao_Paulo",
    }
    registro = await cliente.post(URL_REGISTRO, json=corpo)
    verificador.sucesso(
        registro,
        {"id", "nome_completo", "email", "data_nascimento", "fuso_horario"},
        {"nome_completo", "email"},
    )
    duplicado = await cliente.post(URL_REGISTRO, json=corpo)
    verificador.erro(duplicado, HTTPStatus.CONFLICT)
    invalido = await cliente.post(
        URL_REGISTRO,
        json=corpo | {"email": "sentinela-invalido", "confirmar_senha": "x"},
    )
    verificador.erro(invalido, HTTPStatus.UNPROCESSABLE_CONTENT)
    login = await cliente.post(
        URL_LOGIN, json={"email": EMAIL, "senha": SENHA}
    )
    token = verificador.sucesso(
        login,
        {"access_token", "token_type", "expira_em"},
        {"access_token"},
    )["access_token"]
    verificador.sentinelas.append(token)
    errado = await cliente.post(
        URL_LOGIN, json={"email": EMAIL, "senha": NOVA_SENHA}
    )
    verificador.erro(errado, HTTPStatus.UNAUTHORIZED)
    return token


async def fluxo_usuario_atual(
    cliente: httpx.AsyncClient, verificador: Verificador, token: str
) -> None:
    atual = await cliente.get(
        URL_USUARIO_ATUAL, headers={"Authorization": f"Bearer {token}"}
    )
    verificador.sucesso(
        atual,
        {"id", "nome_completo", "email", "data_nascimento", "fuso_horario"},
        {"nome_completo", "email"},
    )
    recusado = await cliente.get(
        URL_USUARIO_ATUAL, headers={"Authorization": f"Bearer {token}x"}
    )
    verificador.erro(recusado, HTTPStatus.UNAUTHORIZED)


async def fluxo_recuperacao(
    cliente: httpx.AsyncClient, verificador: Verificador
) -> None:
    inexistente = await solicitar(cliente, "sentinela.outro@exemplo.com")
    verificador.erro(inexistente, HTTPStatus.NOT_FOUND)
    pedido = await solicitar(cliente, EMAIL)
    verificador.sucesso(pedido, {"expira_em", "reenvio_permitido_em"}, set())
    errada = await verificar(cliente, EMAIL, "00000000")
    verificador.erro(errada, HTTPStatus.BAD_REQUEST)
    certa = await verificar(cliente, EMAIL, CODIGO)
    token = verificador.sucesso(
        certa, {"token_redefinicao", "expira_em"}, {"token_redefinicao"}
    )["token_redefinicao"]
    verificador.sentinelas.append(token)
    repetida = await verificar(cliente, EMAIL, CODIGO)
    verificador.erro(repetida, HTTPStatus.CONFLICT)
    diferentes = await cliente.post(
        "/api/v1/auth/recuperacao/redefinir",
        json={
            "token_redefinicao": token,
            "nova_senha": NOVA_SENHA,
            "confirmar_senha": SENHA,
        },
    )
    verificador.erro(diferentes, HTTPStatus.UNPROCESSABLE_CONTENT)
    trocada = await redefinir(cliente, token, NOVA_SENHA)
    verificador.sucesso(trocada, {"mensagem"}, set())
    de_novo = await redefinir(cliente, token, NOVA_SENHA)
    verificador.erro(de_novo, HTTPStatus.BAD_REQUEST)


async def fluxo_falhas(ambiente: Ambiente, verificador: Verificador) -> None:
    ambiente.relogio.avancar(timedelta(seconds=60))
    ambiente.enviador.falha_programada = FalhaEnvioEmail("SMTPException")
    envio = await solicitar(ambiente.cliente, EMAIL)
    verificador.erro(envio, HTTPStatus.SERVICE_UNAVAILABLE)
    inesperado = await ambiente.cliente.get("/teste-falhas/inesperado")
    verificador.erro(inesperado, HTTPStatus.INTERNAL_SERVER_ERROR)
    de_envio = await ambiente.cliente.get("/teste-falhas/envio")
    verificador.erro(de_envio, HTTPStatus.INTERNAL_SERVER_ERROR)


async def test_sem_vazamento(
    ambiente: Ambiente,
    saida_formatada: io.StringIO,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caplog.set_level(logging.DEBUG, logger=NOME_LOGGER)
    monkeypatch.setattr(seguranca, "gerar_codigo", SequenciaCodigos(CODIGO))
    verificador = Verificador()
    token = await fluxo_cadastro_e_login(ambiente.cliente, verificador)
    await fluxo_usuario_atual(ambiente.cliente, verificador, token)
    await fluxo_recuperacao(ambiente.cliente, verificador)
    await fluxo_falhas(ambiente, verificador)
    registros = caplog.text + saida_formatada.getvalue()
    assert "erro inesperado" in registros
    for valor in verificador.sentinelas:
        assert valor not in caplog.text
        assert valor not in saida_formatada.getvalue()
