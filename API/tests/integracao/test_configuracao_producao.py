"""CT-F11-03: configuração de produção (segredos e e-mail reais)."""

import pytest
from pydantic import SecretStr, ValidationError

from ..conftest import SEGREDO_JWT_TESTE, SettingsTeste

BASE = {
    "DATABASE_URL": SecretStr("postgresql+psycopg://u:p@127.0.0.1/db"),
    "AMBIENTE": "producao",
    "JWT_SEGREDO": SecretStr(SEGREDO_JWT_TESTE),
    "EMAIL_MODO": "smtp",
    "SMTP_HOST": "smtp.exemplo.com",
    "SMTP_REMETENTE": "nao-responda@exemplo.com",
}


def test_producao_valida() -> None:
    s = SettingsTeste(**BASE)  # pyright: ignore[reportArgumentType]
    assert s.EMAIL_MODO == "smtp"
    assert s.LEMBRETES_JANELA_DIAS == 8
    assert s.CORS_ORIGENS == []


@pytest.mark.parametrize("modo", ["memoria", "console"])
def test_producao_recusa_email_sem_envio_real(modo: str) -> None:
    with pytest.raises(ValidationError, match="proibido em producao"):
        SettingsTeste(**{**BASE, "EMAIL_MODO": modo})  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize("campo", ["DATABASE_URL", "JWT_SEGREDO"])
def test_segredos_sao_obrigatorios(campo: str) -> None:
    dados = {k: v for k, v in BASE.items() if k != campo}
    with pytest.raises(ValidationError):
        SettingsTeste(**dados)  # pyright: ignore[reportArgumentType]


def test_producao_exige_smtp_completo() -> None:
    dados = {k: v for k, v in BASE.items() if k != "SMTP_HOST"}
    with pytest.raises(ValidationError, match="SMTP_HOST"):
        SettingsTeste(**dados)  # pyright: ignore[reportArgumentType]
