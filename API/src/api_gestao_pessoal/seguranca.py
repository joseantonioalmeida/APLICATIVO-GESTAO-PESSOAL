"""Argon2, JWT e geradores de segredos (D-07, arquitetura §8.2)."""

import hashlib
import re
import secrets
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import anyio
import anyio.to_thread
import argon2
import argon2.exceptions
import jwt
from pydantic import SecretStr

TAMANHO_SV = 16
PADRAO_SV = re.compile(r"^[0-9a-f]{16}$")
ALGORITMO_JWT = "HS256"
TIPO_TOKEN = "access"
CLAIMS_TOKEN = frozenset({"sub", "iat", "exp", "typ", "sv"})
TAMANHO_MAXIMO_TOKEN = 4096
TAMANHO_HASH_ARGON2 = 32
TAMANHO_SAL_ARGON2 = 16
DIGITOS_CODIGO = 8
BYTES_TOKEN_REDEFINICAO = 32


@dataclass(frozen=True, slots=True)
class ParametrosArgon2:
    """Custos do Argon2id."""

    time_cost: int
    memory_cost_kib: int
    parallelism: int


class HashArmazenadoInvalido(Exception):
    """Hash armazenado ilegível; não carrega dados."""


class HasherSenha:
    """Argon2id assíncrono, com limitador dedicado de hashes simultâneos."""

    def __init__(
        self, parametros: ParametrosArgon2, limitador: anyio.CapacityLimiter
    ) -> None:
        self._hasher = argon2.PasswordHasher(
            time_cost=parametros.time_cost,
            memory_cost=parametros.memory_cost_kib,
            parallelism=parametros.parallelism,
            hash_len=TAMANHO_HASH_ARGON2,
            salt_len=TAMANHO_SAL_ARGON2,
            type=argon2.Type.ID,
        )
        self._limitador = limitador
        self._ficticio: str | None = None

    async def _executar[T](
        self, funcao: Callable[..., T], *argumentos: object
    ) -> T:
        return await anyio.to_thread.run_sync(
            funcao,
            *argumentos,
            abandon_on_cancel=False,
            limiter=self._limitador,
        )

    async def gerar(self, segredo: str) -> str:
        """Hash Argon2id do segredo."""
        return await self._executar(self._hasher.hash, segredo)

    async def verificar(self, hash_armazenado: str, segredo: str) -> bool:
        """`True` se casar; `False` só para divergência de segredo."""
        try:
            return await self._executar(
                self._hasher.verify, hash_armazenado, segredo
            )
        except argon2.exceptions.VerifyMismatchError:
            return False
        except (
            argon2.exceptions.VerificationError,
            argon2.exceptions.InvalidHashError,
        ):
            raise HashArmazenadoInvalido from None

    async def preparar_ficticio(self) -> None:
        """Calcula, uma vez, o hash usado contra e-mails inexistentes."""
        self._ficticio = await self.gerar(secrets.token_urlsafe(32))

    async def verificar_ficticio(self, segredo: str) -> None:
        """Verifica contra o hash fictício e descarta o resultado."""
        if self._ficticio is None:
            msg = "hash fictício não preparado"
            raise RuntimeError(msg)
        await self.verificar(self._ficticio, segredo)


def carimbo(senha_hash: str) -> str:
    """Carimbo de credencial (`sv`): prefixo do SHA-256 do hash da senha."""
    return hashlib.sha256(senha_hash.encode()).hexdigest()[:TAMANHO_SV]


def gerar_codigo() -> str:
    """Código de 8 dígitos, com zeros à esquerda preservados."""
    return f"{secrets.randbelow(10**DIGITOS_CODIGO):0{DIGITOS_CODIGO}d}"


def gerar_token_redefinicao() -> str:
    """Token de alta entropia para autorizar a redefinição."""
    return secrets.token_urlsafe(BYTES_TOKEN_REDEFINICAO)


def hash_token(token: str) -> str:
    """SHA-256 hexadecimal do token (alta entropia)."""
    return hashlib.sha256(token.encode()).hexdigest()


class TokenInvalido(Exception):
    """Token recusado; não carrega dados."""


@dataclass(frozen=True, slots=True)
class TokenEmitido:
    """JWT emitido e seu instante de expiração."""

    token: str
    expira_em: datetime


@dataclass(frozen=True, slots=True)
class ClaimsToken:
    """Claims aceitas de um token válido."""

    usuario_id: uuid.UUID
    sv: str


@dataclass(frozen=True, slots=True)
class ConfiguracaoToken:
    """Segredo e validade dos tokens."""

    segredo: SecretStr
    validade: timedelta


def emitir_token(
    usuario_id: uuid.UUID,
    senha_hash: str,
    agora: datetime,
    configuracao: ConfiguracaoToken,
) -> TokenEmitido:
    """Emite o JWT; `iat` e `exp` em segundos inteiros."""
    base = agora.replace(microsecond=0)
    iat = int(base.timestamp())
    exp = iat + int(configuracao.validade.total_seconds())
    token = jwt.encode(
        {
            "sub": str(usuario_id),
            "iat": iat,
            "exp": exp,
            "typ": TIPO_TOKEN,
            "sv": carimbo(senha_hash),
        },
        configuracao.segredo.get_secret_value(),
        algorithm=ALGORITMO_JWT,
    )
    return TokenEmitido(
        token=token, expira_em=datetime.fromtimestamp(exp, UTC)
    )


def _exigir(condicao: bool) -> None:
    if not condicao:
        raise TokenInvalido


def _validar_claims(
    payload: dict[str, Any],
    agora: datetime,
    configuracao: ConfiguracaoToken,
) -> ClaimsToken:
    _exigir(set(payload) == CLAIMS_TOKEN)
    _exigir(payload["typ"] == TIPO_TOKEN)
    sub, iat, exp, sv = (payload[c] for c in ("sub", "iat", "exp", "sv"))
    _exigir(isinstance(sub, str))
    try:
        usuario_id = uuid.UUID(sub)
    except ValueError:
        raise TokenInvalido from None
    _exigir(str(usuario_id) == sub)
    _exigir(type(iat) is int and type(exp) is int)
    validade_s = int(configuracao.validade.total_seconds())
    _exigir(0 < exp - iat <= validade_s)
    _exigir(iat <= agora.timestamp() < exp)
    _exigir(isinstance(sv, str) and PADRAO_SV.fullmatch(sv) is not None)
    return ClaimsToken(usuario_id=usuario_id, sv=sv)


def decodificar_token(
    token: str, agora: datetime, configuracao: ConfiguracaoToken
) -> ClaimsToken:
    """Valida assinatura e claims; o tempo vem só do `agora` recebido."""
    try:
        payload = jwt.decode(
            token,
            configuracao.segredo.get_secret_value(),
            algorithms=[ALGORITMO_JWT],
            options={
                "verify_signature": True,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_aud": False,
                "verify_iss": False,
                "require": ["sub", "iat", "exp", "typ", "sv"],
            },
        )
    except jwt.InvalidTokenError:
        raise TokenInvalido from None
    return _validar_claims(payload, agora, configuracao)
