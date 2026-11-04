import functools
from typing import Literal, Self

from email_validator import EmailNotValidError, validate_email
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TAMANHO_MINIMO_SEGREDO_BYTES = 32
KIB_MINIMOS_POR_PISTA = 8
PISO_PRODUCAO_TIME_COST = 3
PISO_PRODUCAO_MEMORIA_KIB = 65536


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    DATABASE_URL: SecretStr
    AMBIENTE: Literal["desenvolvimento", "teste", "producao"] = (
        "desenvolvimento"
    )
    LOG_NIVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=5, ge=0, le=50)
    DB_POOL_TIMEOUT_S: float = Field(default=10, gt=0)
    DB_CONNECT_TIMEOUT_S: int = Field(default=5, ge=1, le=60)
    DB_STATEMENT_TIMEOUT_MS: int = Field(default=15000, ge=100)
    DB_LOCK_TIMEOUT_MS: int = Field(default=5000, ge=50)
    DB_IDLE_IN_TRANSACTION_TIMEOUT_MS: int = Field(default=30000, ge=1000)
    JWT_SEGREDO: SecretStr
    JWT_VALIDADE_MINUTOS: int = Field(default=1440, ge=5, le=1440)
    ARGON2_TIME_COST: int = Field(default=3, ge=1, le=10)
    ARGON2_MEMORY_COST_KIB: int = Field(default=65536, ge=8, le=1048576)
    ARGON2_PARALLELISM: int = Field(default=4, ge=1, le=16)
    ARGON2_MAX_CONCORRENTES: int = Field(default=4, ge=1, le=32)
    EMAIL_MODO: Literal["smtp", "memoria", "console"] = "smtp"
    SMTP_HOST: str | None = Field(default=None, min_length=1, max_length=253)
    SMTP_PORTA: int = Field(default=587, ge=1, le=65535)
    SMTP_SEGURANCA: Literal["starttls", "tls", "nenhuma"] = "starttls"
    SMTP_USUARIO: str | None = None
    SMTP_SENHA: SecretStr | None = None
    SMTP_REMETENTE: str | None = None
    SMTP_TIMEOUT_S: float = Field(default=10, gt=0, le=30)
    CORS_ORIGENS: list[str] = Field(default_factory=list)
    LEMBRETES_INTERVALO_S: int = Field(default=60, ge=1, le=3600)
    LEMBRETES_LOTE: int = Field(default=100, ge=1, le=10000)
    LEMBRETES_JANELA_DIAS: int = Field(default=8, ge=1, le=60)

    @field_validator("DATABASE_URL")
    @classmethod
    def validar_esquema_da_url(cls, valor: SecretStr) -> SecretStr:
        if not valor.get_secret_value().startswith("postgresql+psycopg://"):
            msg = "DATABASE_URL deve usar o esquema postgresql+psycopg://"
            raise ValueError(msg)
        return valor

    @field_validator("JWT_SEGREDO")
    @classmethod
    def validar_segredo_jwt(cls, valor: SecretStr) -> SecretStr:
        tamanho = len(valor.get_secret_value().encode("utf-8"))
        if tamanho < TAMANHO_MINIMO_SEGREDO_BYTES:
            msg = "JWT_SEGREDO deve ter pelo menos 32 bytes"
            raise ValueError(msg)
        return valor

    @field_validator("SMTP_REMETENTE")
    @classmethod
    def validar_remetente(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        try:
            validado = validate_email(
                valor.strip().lower(),
                check_deliverability=False,
                allow_smtputf8=False,
            )
        except EmailNotValidError:
            msg = "SMTP_REMETENTE deve ser um e-mail válido"
            raise ValueError(msg) from None
        return validado.ascii_email

    @model_validator(mode="after")
    def validar_combinacoes(self) -> Self:
        problemas = [
            *self._problemas_argon2(),
            *self._problemas_smtp(),
            *self._problemas_producao(),
        ]
        if problemas:
            raise ValueError("; ".join(problemas))
        return self

    def _problemas_argon2(self) -> list[str]:
        minimo = KIB_MINIMOS_POR_PISTA * self.ARGON2_PARALLELISM
        if self.ARGON2_MEMORY_COST_KIB < minimo:
            return [
                "ARGON2_MEMORY_COST_KIB deve ser pelo menos "
                "8 vezes ARGON2_PARALLELISM"
            ]
        return []

    def _problemas_smtp(self) -> list[str]:
        problemas: list[str] = []
        if self.EMAIL_MODO == "smtp":
            if self.SMTP_HOST is None:
                problemas.append("SMTP_HOST é obrigatório com EMAIL_MODO=smtp")
            if self.SMTP_REMETENTE is None:
                problemas.append(
                    "SMTP_REMETENTE é obrigatório com EMAIL_MODO=smtp"
                )
        if (self.SMTP_USUARIO is None) != (self.SMTP_SENHA is None):
            problemas.append("SMTP_USUARIO e SMTP_SENHA devem vir juntos")
        tem_credenciais = self.SMTP_USUARIO is not None
        if tem_credenciais and self.SMTP_SEGURANCA == "nenhuma":
            problemas.append(
                "credenciais SMTP exigem SMTP_SEGURANCA diferente de nenhuma"
            )
        return problemas

    def _problemas_producao(self) -> list[str]:
        if self.AMBIENTE != "producao":
            return []
        problemas: list[str] = []
        if self.EMAIL_MODO != "smtp":
            problemas.append(
                f"EMAIL_MODO={self.EMAIL_MODO} é proibido em producao"
            )
        if self.SMTP_SEGURANCA == "nenhuma":
            problemas.append("SMTP_SEGURANCA=nenhuma é proibido em producao")
        if self.ARGON2_TIME_COST < PISO_PRODUCAO_TIME_COST:
            problemas.append("ARGON2_TIME_COST deve ser >= 3 em producao")
        if self.ARGON2_MEMORY_COST_KIB < PISO_PRODUCAO_MEMORIA_KIB:
            problemas.append(
                "ARGON2_MEMORY_COST_KIB deve ser >= 65536 em producao"
            )
        return problemas


@functools.lru_cache(maxsize=1)
def obter_settings() -> Settings:
    # DATABASE_URL é obrigatório e vem do ambiente / .env, não de argumentos;
    # o Pyright só enxerga os parâmetros do __init__ sintetizado.
    return Settings()  # pyright: ignore[reportCallIssue]
