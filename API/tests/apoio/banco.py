"""Apoio de testes: guarda de banco descartável e espera de bloqueios."""

import asyncio
import time

import psycopg
from psycopg import sql
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.community.postgres import PostgresContainer

NOME_BANCO_TESTE = "minhavida_teste"
PORTA_POSTGRES = 5432
INTERVALO_POLLING_S = 0.02

TABELAS_DOMINIO = (
    "notificacao",
    "lembrete_importancia",
    "movimentacao_financeira",
    "importancia",
    "serie_importancia",
    "atividade",
    "serie_atividade",
    "recuperacao_senha",
    "requisicao_idempotente",
    "usuario",
)


def garantir_banco_descartavel(url: str, container: PostgresContainer) -> None:
    """Recusa qualquer alvo que não seja o container de teste."""
    alvo = make_url(url)
    esperado_host = container.get_container_host_ip()
    esperada_porta = int(container.get_exposed_port(PORTA_POSTGRES))
    if (
        alvo.host != esperado_host
        or alvo.port != esperada_porta
        or alvo.database != NOME_BANCO_TESTE
    ):
        msg = "alvo não é o banco descartável de teste"
        raise RuntimeError(msg)


def url_libpq(url: str) -> str:
    """Converte a URL do SQLAlchemy para o formato aceito pelo libpq."""
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def limpar_dados(url: str, container: PostgresContainer) -> None:
    """Esvazia as tabelas de domínio; preserva catálogos e alembic_version.

    Sem RESTART IDENTITY (não há identidades) e sem CASCADE: uma lista
    incompleta falha, em vez de apagar outra tabela (REC-MV-034).
    """
    garantir_banco_descartavel(url, container)
    instrucao = sql.SQL("TRUNCATE {}").format(
        sql.SQL(", ").join(sql.Identifier(t) for t in TABELAS_DOMINIO)
    )
    with psycopg.connect(url_libpq(url), autocommit=True) as conexao:
        conexao.execute(instrucao)


async def aguardar_bloqueio(
    engine: AsyncEngine, quantidade: int, timeout: float = 5.0
) -> None:
    """Aguarda, por polling, `quantidade` sessões esperando por um lock."""
    consulta = text(
        "SELECT count(*) FROM pg_stat_activity "
        "WHERE datname = current_database() AND wait_event_type = 'Lock'"
    )
    limite = time.monotonic() + timeout
    atual = 0
    while time.monotonic() < limite:
        async with engine.connect() as conexao:
            atual = (await conexao.execute(consulta)).scalar_one()
        if atual >= quantidade:
            return
        await asyncio.sleep(INTERVALO_POLLING_S)
    msg = (
        f"esperava {quantidade} sessão(ões) bloqueada(s) em {timeout}s; "
        f"observadas: {atual}"
    )
    raise TimeoutError(msg)
