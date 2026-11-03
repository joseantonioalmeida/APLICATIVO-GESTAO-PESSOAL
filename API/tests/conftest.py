import secrets
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import override

import httpx
import pytest
from fastapi import FastAPI
from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from testcontainers.community.postgres import PostgresContainer

from alembic import command
from api_gestao_pessoal.settings import Settings

from .apoio.banco import NOME_BANCO_TESTE, garantir_banco_descartavel
from .apoio.migracoes import config_alembic

IMAGEM_POSTGRES = "postgres:15-alpine"
SEGREDO_JWT_TESTE = "segredo-sintetico-de-testes-0123456789"

FabricaCliente = Callable[
    [FastAPI], AbstractAsyncContextManager[httpx.AsyncClient]
]


@pytest.fixture(scope="session")
def container_postgres() -> Iterator[PostgresContainer]:
    with PostgresContainer(
        IMAGEM_POSTGRES,
        username="minhavida",
        password=secrets.token_urlsafe(16),
        dbname=NOME_BANCO_TESTE,
        driver="psycopg",
    ) as container:
        yield container


@pytest.fixture(scope="session")
def url_banco_teste(container_postgres: PostgresContainer) -> str:
    url = container_postgres.get_connection_url()
    garantir_banco_descartavel(url, container_postgres)
    return url


@pytest.fixture(scope="session")
def banco_migrado(
    container_postgres: PostgresContainer, url_banco_teste: str
) -> str:
    """Aplica `upgrade head` uma vez por sessão e devolve a URL."""
    garantir_banco_descartavel(url_banco_teste, container_postgres)
    command.upgrade(config_alembic(url_banco_teste), "head")
    return url_banco_teste


class SettingsTeste(Settings):
    """Settings herméticas: só valores explícitos e padrões do contrato.

    Ignora variáveis de ambiente, `.env` e segredos em arquivo.
    """

    # A fonte dotenv é construída antes do hook abaixo; sem env_file,
    # nenhum arquivo .env é aberto.
    model_config = SettingsConfigDict(env_file=None)

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings,)


@pytest.fixture
def settings_teste(url_banco_teste: str) -> Settings:
    return SettingsTeste(
        DATABASE_URL=SecretStr(url_banco_teste),
        AMBIENTE="teste",
        JWT_SEGREDO=SecretStr(SEGREDO_JWT_TESTE),
        EMAIL_MODO="memoria",
        ARGON2_TIME_COST=1,
        ARGON2_MEMORY_COST_KIB=8,
        ARGON2_PARALLELISM=1,
    )


@pytest.fixture
async def criar_cliente() -> FabricaCliente:
    @asynccontextmanager
    async def fabrica(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
        async with app.router.lifespan_context(app):
            transporte = httpx.ASGITransport(
                app=app, raise_app_exceptions=False
            )
            async with httpx.AsyncClient(
                transport=transporte, base_url="http://teste"
            ) as cliente:
                yield cliente

    return fabrica
