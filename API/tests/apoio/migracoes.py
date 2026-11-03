"""Apoio de testes: configuração do Alembic contra o banco descartável."""

from pathlib import Path

from alembic.config import Config

RAIZ = Path(__file__).resolve().parents[2]
ALEMBIC_INI = RAIZ / "alembic.ini"
REVISAO_INICIAL = "0001"


def config_alembic(url: str) -> Config:
    """Config do Alembic com a URL do container, sem logging de arquivo."""
    cfg = Config(str(ALEMBIC_INI))
    cfg.attributes["url_banco"] = url
    cfg.attributes["configurar_logging"] = False
    return cfg
