"""Schemas de autenticação e recuperação de senha (arquitetura §9.1)."""

import re
import unicodedata
from datetime import date, datetime
from typing import Annotated, Literal

import email_validator
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    ValidationInfo,
    field_validator,
)
from pydantic_core import PydanticCustomError

from api_gestao_pessoal.tempo import fuso_valido

TAMANHO_MAXIMO_EMAIL = 254
TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128
TAMANHO_MAXIMO_NOME = 150
TAMANHO_MAXIMO_TOKEN_REDEFINICAO = 128
PADRAO_DATA_CIVIL = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
PADRAO_CODIGO = re.compile(r"[0-9]{8}")

MENSAGEM_EMAIL_INVALIDO = "Informe um e-mail válido"
MENSAGEM_SENHA_FRACA = (
    "A senha informada não atende os requisitos necessários de 8 caracteres"
)
MENSAGEM_SENHAS_DIFERENTES = "As senhas devem ser idênticas"
MENSAGEM_NOME_OBRIGATORIO = "Informe o nome completo"
MENSAGEM_NOME_INVALIDO = "O nome não pode conter caracteres de controle"
MENSAGEM_DATA_INVALIDA = "Informe uma data válida"
MENSAGEM_FUSO_INVALIDO = "Fuso horário inválido"
MENSAGEM_CODIGO_FORMATO = "O código deve conter 8 dígitos numéricos"
MENSAGEM_SENHA_LONGA = "Informe no máximo 128 caracteres."
MENSAGEM_NOME_LONGO = "Informe no máximo 150 caracteres."


def canonicalizar_email(valor: str) -> str | None:
    """Forma canônica do e-mail (R9.9), ou `None` se não for possível."""
    candidato = valor.strip().lower()
    try:
        validado = email_validator.validate_email(
            candidato, check_deliverability=False, allow_smtputf8=False
        )
    except email_validator.EmailNotValidError:
        return None
    ascii_email = validado.ascii_email
    if ascii_email is None or len(ascii_email) > TAMANHO_MAXIMO_EMAIL:
        return None
    return ascii_email


def _email_valido(valor: object) -> str:
    canonico = canonicalizar_email(valor) if isinstance(valor, str) else None
    if canonico is None:
        raise PydanticCustomError("EMAIL_INVALIDO", MENSAGEM_EMAIL_INVALIDO)
    return canonico


def _senha_nova(valor: object) -> str:
    if not isinstance(valor, str) or len(valor) < TAMANHO_MINIMO_SENHA:
        raise PydanticCustomError("SENHA_FRACA", MENSAGEM_SENHA_FRACA)
    if len(valor) > TAMANHO_MAXIMO_SENHA:
        raise PydanticCustomError("TAMANHO_MAXIMO", MENSAGEM_SENHA_LONGA)
    return valor


def _nome_completo(valor: object) -> str:
    nome = valor.strip() if isinstance(valor, str) else ""
    if not nome:
        raise PydanticCustomError(
            "NOME_COMPLETO_OBRIGATORIO", MENSAGEM_NOME_OBRIGATORIO
        )
    if any(unicodedata.category(c) == "Cc" for c in nome):
        raise PydanticCustomError(
            "NOME_COMPLETO_INVALIDO", MENSAGEM_NOME_INVALIDO
        )
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise PydanticCustomError("TAMANHO_MAXIMO", MENSAGEM_NOME_LONGO)
    return nome


def _data_civil(valor: object) -> date:
    erro = PydanticCustomError("DATA_INVALIDA", MENSAGEM_DATA_INVALIDA)
    if not isinstance(valor, str) or not PADRAO_DATA_CIVIL.fullmatch(valor):
        raise erro
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise erro from None


def _fuso(valor: object) -> str:
    if not isinstance(valor, str) or not fuso_valido(valor):
        raise PydanticCustomError("FUSO_INVALIDO", MENSAGEM_FUSO_INVALIDO)
    return valor


def _codigo(valor: object) -> str:
    if not isinstance(valor, str) or not PADRAO_CODIGO.fullmatch(valor):
        raise PydanticCustomError("CODIGO_FORMATO", MENSAGEM_CODIGO_FORMATO)
    return valor


def _exigir_igual(valor: str, senha: object) -> str:
    """Confirmação idêntica à senha já validada (se ela foi aceita)."""
    if senha is not None and valor != senha:
        raise PydanticCustomError(
            "SENHAS_DIFERENTES", MENSAGEM_SENHAS_DIFERENTES
        )
    return valor


EmailCanonico = Annotated[str, BeforeValidator(_email_valido)]
SenhaNova = Annotated[str, BeforeValidator(_senha_nova)]
NomeCompleto = Annotated[str, BeforeValidator(_nome_completo)]
DataCivil = Annotated[date, BeforeValidator(_data_civil)]
FusoHorario = Annotated[str, BeforeValidator(_fuso)]
CodigoVerificacao = Annotated[str, BeforeValidator(_codigo)]


class RegistroEntrada(BaseModel):
    """Corpo do cadastro de conta."""

    nome_completo: NomeCompleto = Field(default=None, validate_default=True)
    email: EmailCanonico
    senha: SenhaNova = Field(default=None, validate_default=True)
    confirmar_senha: str
    data_nascimento: DataCivil
    fuso_horario: FusoHorario

    @field_validator("confirmar_senha")
    @classmethod
    def confirmar(cls, valor: str, info: ValidationInfo) -> str:
        return _exigir_igual(valor, info.data.get("senha"))


class LoginEntrada(BaseModel):
    """Corpo do login; o e-mail é canonicalizado pelo service."""

    email: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_EMAIL)
    senha: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_SENHA)


class SolicitarCodigoEntrada(BaseModel):
    """Corpo da solicitação do código de recuperação."""

    email: EmailCanonico


class VerificarCodigoEntrada(BaseModel):
    """Corpo da verificação do código de recuperação."""

    email: EmailCanonico
    codigo: CodigoVerificacao = Field(default=None, validate_default=True)


class RedefinirSenhaEntrada(BaseModel):
    """Corpo da redefinição de senha."""

    token_redefinicao: str = Field(
        min_length=1, max_length=TAMANHO_MAXIMO_TOKEN_REDEFINICAO
    )
    nova_senha: SenhaNova = Field(default=None, validate_default=True)
    confirmar_senha: str

    @field_validator("confirmar_senha")
    @classmethod
    def confirmar(cls, valor: str, info: ValidationInfo) -> str:
        return _exigir_igual(valor, info.data.get("nova_senha"))


class TokenResposta(BaseModel):
    """Token de acesso emitido no login."""

    access_token: str
    token_type: Literal["bearer"]
    expira_em: datetime


class SolicitacaoCodigoResposta(BaseModel):
    """Prazos da emissão do código."""

    expira_em: datetime
    reenvio_permitido_em: datetime


class VerificacaoCodigoResposta(BaseModel):
    """Token que autoriza a redefinição."""

    token_redefinicao: str
    expira_em: datetime


class MensagemResposta(BaseModel):
    """Resposta com uma mensagem literal."""

    mensagem: str
