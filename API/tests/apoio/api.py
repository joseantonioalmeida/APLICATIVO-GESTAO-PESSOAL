"""Apoio dos testes de API: usuário autenticado e cabeçalhos."""

import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from .identidade import SENHA_PADRAO, entrar, registrar


@dataclass(frozen=True, slots=True)
class UsuarioTeste:
    """Usuário registrado e autenticado nos testes."""

    id: uuid.UUID
    email: str
    cabecalhos: dict[str, str]


async def criar_usuario(
    cliente: httpx.AsyncClient, **campos: Any
) -> UsuarioTeste:
    """Registra e autentica um usuário sintético."""
    dados = await registrar(cliente, **campos)
    token = await entrar(cliente, dados["email"], SENHA_PADRAO)
    return UsuarioTeste(
        id=uuid.UUID(dados["id"]),
        email=dados["email"],
        cabecalhos={"Authorization": f"Bearer {token}"},
    )


def chave_nova() -> str:
    """`Idempotency-Key` válida e única."""
    return uuid.uuid4().hex
