from collections.abc import AsyncIterator, Iterator

import pytest
from alembic.config import Config
from sqlalchemy import Connection, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer

from api_gestao_pessoal.database import criar_fabrica_sessoes

from ..apoio.banco import garantir_banco_descartavel, limpar_dados
from ..apoio.migracoes import config_alembic


@pytest.fixture
def conexao(banco_migrado: str) -> Iterator[Connection]:
    """Conexão com transação aberta e revertida ao fim do teste."""
    engine = create_engine(banco_migrado, poolclass=NullPool)
    ligacao = engine.connect()
    transacao = ligacao.begin()
    try:
        yield ligacao
    finally:
        transacao.rollback()
        ligacao.close()
        engine.dispose()


@pytest.fixture
async def sessao_orm(banco_migrado: str) -> AsyncIterator[AsyncSession]:
    """Sessão ORM cuja transação é revertida ao fim do teste."""
    engine = create_async_engine(banco_migrado, poolclass=NullPool)
    sessao = criar_fabrica_sessoes(engine)()
    try:
        yield sessao
    finally:
        await sessao.rollback()
        await engine.dispose()


@pytest.fixture
async def fabrica_sessoes(
    banco_migrado: str, container_postgres: PostgresContainer
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Fábrica de sessões que confirmam transações; limpa ao final."""
    engine = create_async_engine(banco_migrado, poolclass=NullPool)
    try:
        yield criar_fabrica_sessoes(engine)
    finally:
        await engine.dispose()
        limpar_dados(banco_migrado, container_postgres)


@pytest.fixture
def config_migracao(
    banco_migrado: str, container_postgres: PostgresContainer
) -> Config:
    """Config do Alembic para o container, depois da guarda."""
    garantir_banco_descartavel(banco_migrado, container_postgres)
    return config_alembic(banco_migrado)
