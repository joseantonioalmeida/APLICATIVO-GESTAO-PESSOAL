from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime

import httpx
import psycopg
import pytest
from fastapi import FastAPI
from testcontainers.community.postgres import PostgresContainer

from api_gestao_pessoal.dependencias import obter_relogio
from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.settings import Settings

from ..apoio.banco import limpar_dados, url_libpq
from ..apoio.relogio import RelogioFixo
from ..conftest import FabricaCliente
from .rotas_teste_nucleo import router as router_teste

INSTANTE_INICIAL = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)


@pytest.fixture(scope="session", autouse=True)
def tabela_de_teste(banco_migrado: str) -> Iterator[None]:
    """Tabela auxiliar que registra os efeitos da rota de teste."""
    with psycopg.connect(url_libpq(banco_migrado), autocommit=True) as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS teste_nucleo_registro ("
            "id uuid PRIMARY KEY, usuario_id uuid NOT NULL, valor text)"
        )
    yield
    with psycopg.connect(url_libpq(banco_migrado), autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS teste_nucleo_registro")


@pytest.fixture
def relogio() -> RelogioFixo:
    return RelogioFixo(INSTANTE_INICIAL)


@pytest.fixture
def app_nucleo(
    settings_teste: Settings, banco_migrado: str, relogio: RelogioFixo
) -> FastAPI:
    app = criar_app(settings_teste)
    app.include_router(router_teste)
    app.dependency_overrides[obter_relogio] = lambda: relogio
    return app


@pytest.fixture
async def cliente(
    app_nucleo: FastAPI, criar_cliente: FabricaCliente
) -> AsyncIterator[httpx.AsyncClient]:
    async with criar_cliente(app_nucleo) as c:
        yield c


@pytest.fixture(autouse=True)
def limpeza(
    banco_migrado: str, container_postgres: PostgresContainer
) -> Iterator[None]:
    yield
    with psycopg.connect(url_libpq(banco_migrado), autocommit=True) as c:
        c.execute("TRUNCATE teste_nucleo_registro")
    limpar_dados(banco_migrado, container_postgres)
