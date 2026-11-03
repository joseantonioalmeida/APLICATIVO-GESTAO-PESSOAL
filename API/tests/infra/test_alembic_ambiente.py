from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command

from ..apoio.migracoes import REVISAO_INICIAL

RAIZ = Path(__file__).resolve().parents[2]
ALEMBIC_INI = RAIZ / "alembic.ini"


def _config(url: str) -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.attributes["url_banco"] = url
    cfg.attributes["configurar_logging"] = False
    return cfg


def test_upgrade_head_com_revisao_inicial(url_banco_teste: str) -> None:
    cfg = _config(url_banco_teste)
    command.upgrade(cfg, "head")
    assert ScriptDirectory.from_config(cfg).get_heads() == [REVISAO_INICIAL]
    command.check(cfg)


async def test_upgrade_com_conexao_compartilhada(
    url_banco_teste: str,
) -> None:
    cfg = _config(url_banco_teste)

    def aplicar(conexao: Connection) -> None:
        cfg.attributes["connection"] = conexao
        command.upgrade(cfg, "head")

    engine = create_async_engine(url_banco_teste, poolclass=NullPool)
    try:
        async with engine.connect() as conexao:
            await conexao.run_sync(aplicar)
    finally:
        await engine.dispose()


def test_env_sem_app_e_sem_url() -> None:
    env = (RAIZ / "alembic" / "env.py").read_text(encoding="utf-8")
    assert "api_gestao_pessoal.main" not in env
    assert "postgresql" not in env
    linhas = ALEMBIC_INI.read_text(encoding="utf-8").splitlines()
    assert not any(linha.startswith("sqlalchemy.url") for linha in linhas)
