"""Ambiente do Alembic (async), sem importar a aplicação FastAPI."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from api_gestao_pessoal.models import Base

config = context.config

if config.config_file_name is not None and config.attributes.get(
    "configurar_logging", True
):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def obter_url() -> str:
    """URL de `config.attributes` (testes) ou das Settings."""
    url = config.attributes.get("url_banco")
    if url:
        return url
    from api_gestao_pessoal.settings import obter_settings

    return obter_settings().DATABASE_URL.get_secret_value()


def executar_migracoes_offline() -> None:
    context.configure(
        url=obter_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def executar_migracoes(conexao: Connection) -> None:
    context.configure(
        connection=conexao,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def executar_migracoes_async() -> None:
    engine = create_async_engine(obter_url(), poolclass=pool.NullPool)
    async with engine.connect() as conexao:
        await conexao.run_sync(executar_migracoes)
    await engine.dispose()


def executar_migracoes_online() -> None:
    conexao = config.attributes.get("connection")
    if isinstance(conexao, Connection):
        executar_migracoes(conexao)
    else:
        asyncio.run(executar_migracoes_async())


if context.is_offline_mode():
    executar_migracoes_offline()
else:
    executar_migracoes_online()
