import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError
from testcontainers.community.postgres import PostgresContainer

from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.settings import Settings, obter_settings

from ..apoio.banco import garantir_banco_descartavel
from ..conftest import FabricaCliente

URL_VALIDA = "postgresql+psycopg://usuario:senha@127.0.0.1:5432/banco"
VARIAVEIS_SETTINGS = (
    "DATABASE_URL",
    "AMBIENTE",
    "LOG_NIVEL",
    "DB_POOL_SIZE",
    "DB_MAX_OVERFLOW",
    "DB_POOL_TIMEOUT_S",
    "DB_CONNECT_TIMEOUT_S",
    "DB_STATEMENT_TIMEOUT_MS",
    "DB_LOCK_TIMEOUT_MS",
    "DB_IDLE_IN_TRANSACTION_TIMEOUT_MS",
    "JWT_SEGREDO",
    "JWT_VALIDADE_MINUTOS",
    "ARGON2_TIME_COST",
    "ARGON2_MEMORY_COST_KIB",
    "ARGON2_PARALLELISM",
    "ARGON2_MAX_CONCORRENTES",
    "EMAIL_MODO",
    "SMTP_HOST",
    "SMTP_PORTA",
    "SMTP_SEGURANCA",
    "SMTP_USUARIO",
    "SMTP_SENHA",
    "SMTP_REMETENTE",
    "SMTP_TIMEOUT_S",
)
POOL_DO_AMBIENTE = 7
STATEMENT_TIMEOUT_DO_ENV_MS = 123
SEGREDO_SINTETICO = "segredo-sintetico-de-configuracao-0123456789"


@pytest.fixture
def ambiente_limpo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[None]:
    for nome in VARIAVEIS_SETTINGS:
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.chdir(tmp_path)
    obter_settings.cache_clear()
    yield
    obter_settings.cache_clear()


def test_settings_exige_database_url(ambiente_limpo: None) -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        obter_settings()


def test_settings_rejeita_esquema_sem_eco(
    ambiente_limpo: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:segredo@h/db")
    with pytest.raises(ValidationError) as erro:
        obter_settings()
    mensagem = str(erro.value)
    assert "postgresql+psycopg://" in mensagem
    assert "segredo" not in mensagem


def test_settings_padroes(
    ambiente_limpo: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", URL_VALIDA)
    monkeypatch.setenv("JWT_SEGREDO", SEGREDO_SINTETICO)
    monkeypatch.setenv("SMTP_HOST", "smtp.exemplo.com")
    monkeypatch.setenv("SMTP_REMETENTE", "nao-responda@exemplo.com")
    s = obter_settings()
    assert s.AMBIENTE == "desenvolvimento"
    assert s.LOG_NIVEL == "INFO"
    assert s.DB_POOL_SIZE == 5
    assert s.DB_MAX_OVERFLOW == 5
    assert s.DB_POOL_TIMEOUT_S == 10
    assert s.DB_CONNECT_TIMEOUT_S == 5
    assert s.DB_STATEMENT_TIMEOUT_MS == 15000
    assert s.DB_LOCK_TIMEOUT_MS == 5000
    assert s.DB_IDLE_IN_TRANSACTION_TIMEOUT_MS == 30000
    assert s.DATABASE_URL.get_secret_value() == URL_VALIDA
    assert "senha" not in repr(s)
    assert s.JWT_VALIDADE_MINUTOS == 1440
    assert s.ARGON2_TIME_COST == 3
    assert s.ARGON2_MEMORY_COST_KIB == 65536
    assert s.ARGON2_PARALLELISM == 4
    assert s.ARGON2_MAX_CONCORRENTES == 4
    assert s.EMAIL_MODO == "smtp"
    assert s.SMTP_PORTA == 587
    assert s.SMTP_SEGURANCA == "starttls"
    assert s.SMTP_TIMEOUT_S == 10
    assert s.SMTP_USUARIO is None
    assert s.SMTP_SENHA is None
    assert SEGREDO_SINTETICO not in repr(s)


def test_importacao_sem_efeitos(tmp_path: Path) -> None:
    ambiente = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    resultado = subprocess.run(
        [
            sys.executable,
            "-c",
            "import api_gestao_pessoal.main, api_gestao_pessoal.database, "
            "api_gestao_pessoal.models",
        ],
        env=ambiente,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr


def test_obter_settings_cacheado(
    ambiente_limpo: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", URL_VALIDA)
    monkeypatch.setenv("JWT_SEGREDO", SEGREDO_SINTETICO)
    monkeypatch.setenv("EMAIL_MODO", "memoria")
    assert obter_settings() is obter_settings()


async def test_criar_app_usa_settings_injetadas(
    settings_teste: Settings, criar_cliente: FabricaCliente
) -> None:
    app = criar_app(settings_teste)
    async with criar_cliente(app):
        assert app.state.settings is settings_teste


def test_guarda_recusa_banco_alheio(
    container_postgres: PostgresContainer,
) -> None:
    with pytest.raises(RuntimeError, match="banco descartável"):
        garantir_banco_descartavel(
            "postgresql+psycopg://u:p@outro:5432/minhavida_teste",
            container_postgres,
        )


def test_settings_teste_ignora_ambiente_e_env(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        f"DB_STATEMENT_TIMEOUT_MS={STATEMENT_TIMEOUT_DO_ENV_MS}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DB_POOL_SIZE", str(POOL_DO_AMBIENTE))
    monkeypatch.setenv("LOG_NIVEL", "DEBUG")
    monkeypatch.setenv("EMAIL_MODO", "memoria")
    # Controle positivo: a classe de produção enxerga o ambiente alterado.
    # JWT_SEGREDO é obrigatório e vai explícito, como DATABASE_URL.
    controle = Settings(
        DATABASE_URL=SecretStr(URL_VALIDA),
        JWT_SEGREDO=SecretStr(SEGREDO_SINTETICO),
    )
    assert controle.DB_POOL_SIZE == POOL_DO_AMBIENTE
    assert controle.LOG_NIVEL == "DEBUG"
    assert controle.DB_STATEMENT_TIMEOUT_MS == STATEMENT_TIMEOUT_DO_ENV_MS
    assert controle.EMAIL_MODO == "memoria"
    # A fixture usada pelos testes ignora ambiente e .env.
    s: Settings = request.getfixturevalue("settings_teste")
    assert s.DB_POOL_SIZE == 5
    assert s.LOG_NIVEL == "INFO"
    assert s.DB_STATEMENT_TIMEOUT_MS == 15000
    assert s.AMBIENTE == "teste"
    # Sem env_file, a fonte dotenv não abre nenhum arquivo.
    assert type(s).model_config.get("env_file") is None
