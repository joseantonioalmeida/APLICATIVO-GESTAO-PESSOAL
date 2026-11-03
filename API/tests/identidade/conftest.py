from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
import psycopg
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer

from api_gestao_pessoal.dependencias import (
    obter_enviador_email,
    obter_relogio,
)
from api_gestao_pessoal.email import EnviadorEmailMemoria
from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.settings import Settings

from ..apoio.banco import limpar_dados, url_libpq
from ..apoio.relogio import RelogioFixo
from ..conftest import FabricaCliente
from .rotas_teste_identidade import router as router_teste

INSTANTE_INICIAL = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class Ambiente:
    """Recursos de um teste de identidade, agrupados."""

    app: FastAPI
    cliente: httpx.AsyncClient
    relogio: RelogioFixo
    enviador: EnviadorEmailMemoria
    banco: str


@pytest.fixture
def relogio() -> RelogioFixo:
    return RelogioFixo(INSTANTE_INICIAL)


@pytest.fixture
def enviador() -> EnviadorEmailMemoria:
    return EnviadorEmailMemoria()


@pytest.fixture
def app_identidade(
    settings_teste: Settings,
    banco_migrado: str,
    relogio: RelogioFixo,
    enviador: EnviadorEmailMemoria,
) -> FastAPI:
    app = criar_app(settings_teste)
    app.include_router(router_teste)
    app.dependency_overrides[obter_relogio] = lambda: relogio
    app.dependency_overrides[obter_enviador_email] = lambda: enviador
    return app


@pytest.fixture
async def cliente(
    app_identidade: FastAPI, criar_cliente: FabricaCliente
) -> AsyncIterator[httpx.AsyncClient]:
    async with criar_cliente(app_identidade) as c:
        yield c


@pytest.fixture
def ambiente(
    app_identidade: FastAPI,
    cliente: httpx.AsyncClient,
    relogio: RelogioFixo,
    enviador: EnviadorEmailMemoria,
    banco_migrado: str,
) -> Ambiente:
    return Ambiente(app_identidade, cliente, relogio, enviador, banco_migrado)


@pytest.fixture(autouse=True)
def limpeza(
    banco_migrado: str, container_postgres: PostgresContainer
) -> Iterator[None]:
    yield
    limpar_dados(banco_migrado, container_postgres)


@pytest.fixture
async def monitor(banco_migrado: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(banco_migrado, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
def abrir_bloqueadora(
    banco_migrado: str,
) -> Iterator[Callable[[], psycopg.Connection]]:
    """Fábrica de conexões bloqueadoras (transação aberta, sem commit)."""
    abertas: list[psycopg.Connection] = []

    def abrir() -> psycopg.Connection:
        conexao = psycopg.connect(url_libpq(banco_migrado))
        abertas.append(conexao)
        return conexao

    yield abrir
    for conexao in abertas:
        conexao.rollback()
        conexao.close()
