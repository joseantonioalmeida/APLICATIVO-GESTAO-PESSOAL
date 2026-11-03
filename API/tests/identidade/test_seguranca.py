import asyncio
import threading
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import anyio
import anyio.to_thread
import argon2
import jwt
import pytest
from pydantic import SecretStr

from api_gestao_pessoal.seguranca import (
    ConfiguracaoToken,
    HashArmazenadoInvalido,
    HasherSenha,
    ParametrosArgon2,
    TokenInvalido,
    carimbo,
    decodificar_token,
    emitir_token,
)

from ..conftest import SEGREDO_JWT_TESTE

PARAMETROS_PRODUCAO = ParametrosArgon2(3, 65536, 4)
PARAMETROS_TESTE = ParametrosArgon2(1, 8, 1)
CONFIGURACAO = ConfiguracaoToken(
    SecretStr(SEGREDO_JWT_TESTE), timedelta(days=1)
)
AGORA = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)
VAGAS = 2
CHAMADAS = 5


class Medidor:
    """Conta quantos `hash` rodam ao mesmo tempo, sem usar `sleep`."""

    def __init__(self) -> None:
        self.ativas = 0
        self.maxima = 0
        self.chamadas = 0
        self.travas = threading.Lock()
        self.dois_dentro = threading.Event()
        self.terceiro_entrou = threading.Event()
        self.liberar = threading.Event()

    def executar(self) -> str:
        with self.travas:
            self.ativas += 1
            self.chamadas += 1
            self.maxima = max(self.maxima, self.ativas)
            if self.ativas == VAGAS:
                self.dois_dentro.set()
            if self.ativas > VAGAS:
                self.terceiro_entrou.set()
        self.liberar.wait(timeout=10)
        with self.travas:
            self.ativas -= 1
        return "hash-medido"


async def verificar_limitador(monkeypatch: pytest.MonkeyPatch) -> Medidor:
    medidor = Medidor()

    def hash_medido(_hasher: object, _senha: object) -> str:
        return medidor.executar()

    monkeypatch.setattr(argon2.PasswordHasher, "hash", hash_medido)
    hasher = HasherSenha(PARAMETROS_TESTE, anyio.CapacityLimiter(VAGAS))
    tarefas = [
        asyncio.create_task(hasher.gerar(f"senha-{i}"))
        for i in range(CHAMADAS)
    ]
    try:
        assert await anyio.to_thread.run_sync(medidor.dois_dentro.wait, 10)
        # Com o limitador, a terceira chamada não entra enquanto as duas
        # primeiras estiverem presas.
        assert not await anyio.to_thread.run_sync(
            medidor.terceiro_entrou.wait, 0.3
        )
    finally:
        medidor.liberar.set()
        await asyncio.gather(*tarefas)
    return medidor


async def test_hasher(monkeypatch: pytest.MonkeyPatch) -> None:
    hasher = HasherSenha(PARAMETROS_PRODUCAO, anyio.CapacityLimiter(1))
    gerado = await hasher.gerar("senha-sintetica-123")
    assert gerado.startswith("$argon2id$v=19$m=65536,t=3,p=4$")
    assert await hasher.verificar(gerado, "senha-sintetica-123") is True
    assert await hasher.verificar(gerado, "outra-senha-123") is False
    with pytest.raises(HashArmazenadoInvalido) as erro:
        await hasher.verificar("hash-corrompido", "qualquer")
    assert erro.value.args == ()
    medidor = await verificar_limitador(monkeypatch)
    assert medidor.maxima == VAGAS
    assert medidor.chamadas == CHAMADAS


def claims_validas(usuario_id: uuid.UUID) -> dict[str, Any]:
    iat = int(AGORA.timestamp())
    return {
        "sub": str(usuario_id),
        "iat": iat,
        "exp": iat + 86400,
        "typ": "access",
        "sv": carimbo("hash"),
    }


def codificar(claims: dict[str, Any]) -> str:
    return jwt.encode(claims, SEGREDO_JWT_TESTE, algorithm="HS256")


def test_token_unidade() -> None:
    usuario_id = uuid.uuid7()
    emitido = emitir_token(
        usuario_id, "hash", AGORA.replace(microsecond=999999), CONFIGURACAO
    )
    assert emitido.expira_em == AGORA + timedelta(days=1)
    claims = decodificar_token(emitido.token, AGORA, CONFIGURACAO)
    assert claims.usuario_id == usuario_id
    assert claims.sv == carimbo("hash")
    valido = codificar(claims_validas(usuario_id))
    ultimo_segundo = AGORA + timedelta(days=1) - timedelta(seconds=1)
    assert decodificar_token(valido, ultimo_segundo, CONFIGURACAO)
    recusados = [
        (valido, AGORA - timedelta(seconds=1)),
        (valido, AGORA + timedelta(days=1)),
        (codificar(claims_validas(usuario_id) | {"iat": True}), AGORA),
        (codificar(claims_validas(usuario_id) | {"extra": 1}), AGORA),
        (codificar(claims_validas(usuario_id) | {"exp": 1e12}), AGORA),
        (codificar(claims_validas(usuario_id) | {"sv": "XYZ"}), AGORA),
    ]
    for token, instante in recusados:
        with pytest.raises(TokenInvalido):
            decodificar_token(token, instante, CONFIGURACAO)
