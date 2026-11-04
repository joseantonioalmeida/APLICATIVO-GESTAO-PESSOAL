from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime

import httpx
import pytest
from fastapi import FastAPI
from testcontainers.community.postgres import PostgresContainer

from api_gestao_pessoal.dependencias import obter_relogio
from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.settings import Settings

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.banco import limpar_dados
from ..apoio.relogio import RelogioFixo
from ..conftest import FabricaCliente

# 09:00 em São Paulo: hoje = 2026-10-13.
INSTANTE_INICIAL = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)


@pytest.fixture
def relogio() -> RelogioFixo:
    return RelogioFixo(INSTANTE_INICIAL)


@pytest.fixture
def app_painel(
    settings_teste: Settings, banco_migrado: str, relogio: RelogioFixo
) -> FastAPI:
    app = criar_app(settings_teste)
    app.dependency_overrides[obter_relogio] = lambda: relogio
    return app


@pytest.fixture
async def cliente(
    app_painel: FastAPI, criar_cliente: FabricaCliente
) -> AsyncIterator[httpx.AsyncClient]:
    async with criar_cliente(app_painel) as c:
        yield c


@pytest.fixture
async def usuario(cliente: httpx.AsyncClient) -> UsuarioTeste:
    return await criar_usuario(cliente)


@pytest.fixture(autouse=True)
def limpeza(
    banco_migrado: str, container_postgres: PostgresContainer
) -> Iterator[None]:
    yield
    limpar_dados(banco_migrado, container_postgres)
