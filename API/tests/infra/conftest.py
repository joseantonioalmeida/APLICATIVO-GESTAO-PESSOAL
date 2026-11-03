from collections.abc import Callable, Iterator

import psycopg
import pytest
from fastapi import FastAPI
from testcontainers.community.postgres import PostgresContainer

from api_gestao_pessoal.settings import Settings

from ..apoio.banco import garantir_banco_descartavel, url_libpq
from ..apoio.rotas_teste import criar_app_teste


@pytest.fixture(scope="session")
def schema_infra(
    container_postgres: PostgresContainer, url_banco_teste: str
) -> Iterator[None]:
    garantir_banco_descartavel(url_banco_teste, container_postgres)
    with psycopg.connect(url_libpq(url_banco_teste), autocommit=True) as c:
        c.execute("CREATE SCHEMA IF NOT EXISTS teste_infra")
        c.execute(
            "CREATE TABLE IF NOT EXISTS teste_infra.registro ("
            "id uuid PRIMARY KEY, valor text NOT NULL, unico text, "
            "CONSTRAINT uq_registro_unico UNIQUE (unico) "
            "DEFERRABLE INITIALLY DEFERRED)"
        )
    yield
    garantir_banco_descartavel(url_banco_teste, container_postgres)
    with psycopg.connect(url_libpq(url_banco_teste), autocommit=True) as c:
        c.execute("DROP SCHEMA IF EXISTS teste_infra CASCADE")


@pytest.fixture
def limpar_registros(
    schema_infra: None,
    container_postgres: PostgresContainer,
    url_banco_teste: str,
) -> Iterator[None]:
    yield
    garantir_banco_descartavel(url_banco_teste, container_postgres)
    with psycopg.connect(url_libpq(url_banco_teste), autocommit=True) as c:
        c.execute("TRUNCATE teste_infra.registro")


@pytest.fixture
def contar_registros(url_banco_teste: str) -> Callable[[], int]:
    """Conta linhas por uma conexão independente da aplicação."""

    def contar() -> int:
        with psycopg.connect(url_libpq(url_banco_teste)) as c:
            linha = c.execute(
                "SELECT count(*) FROM teste_infra.registro"
            ).fetchone()
        assert linha is not None
        return linha[0]

    return contar


@pytest.fixture
def app_teste(settings_teste: Settings) -> FastAPI:
    return criar_app_teste(settings_teste)
