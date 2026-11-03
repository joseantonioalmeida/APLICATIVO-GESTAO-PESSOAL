from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api_gestao_pessoal.settings import Settings


def criar_engine(settings: Settings) -> AsyncEngine:
    opcoes = (
        f"-c statement_timeout={settings.DB_STATEMENT_TIMEOUT_MS} "
        f"-c lock_timeout={settings.DB_LOCK_TIMEOUT_MS} "
        "-c idle_in_transaction_session_timeout="
        f"{settings.DB_IDLE_IN_TRANSACTION_TIMEOUT_MS}"
    )
    return create_async_engine(
        settings.DATABASE_URL.get_secret_value(),
        hide_parameters=True,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT_S,
        connect_args={
            "connect_timeout": settings.DB_CONNECT_TIMEOUT_S,
            "options": opcoes,
        },
    )


def criar_fabrica_sessoes(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
    )


async def obter_sessao(request: Request) -> AsyncIterator[AsyncSession]:
    """Abre uma sessão por requisição.

    Sem commit nem rollback explícitos: o `close()` desfaz o que não foi
    confirmado pelo router.
    """
    fabrica = request.app.state.fabrica_sessoes
    async with fabrica() as sessao:
        yield sessao


SessaoDep = Annotated[AsyncSession, Depends(obter_sessao, scope="function")]
