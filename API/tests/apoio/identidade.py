"""Apoio dos testes de identidade: cliente, banco e portão de largada."""

import asyncio
import time
import uuid
from collections.abc import Coroutine, Sequence
from datetime import datetime
from http import HTTPStatus
from typing import Any, NamedTuple

import httpx
import psycopg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .banco import INTERVALO_POLLING_S
from .esquema import consultar

ESPERA_FOR_UPDATE = "%FROM recuperacao_senha%FOR UPDATE%"
ESPERA_INSERT_USUARIO = "%INSERT INTO usuario%"
ESPERA_INSERT_RECUPERACAO = "%INSERT INTO recuperacao_senha%"
ESPERA_UPDATE_USUARIO = "%UPDATE usuario SET%"

URL_REGISTRO = "/api/v1/auth/registro"
URL_LOGIN = "/api/v1/auth/login"
URL_SOLICITAR = "/api/v1/auth/recuperacao/solicitar"
URL_VERIFICAR = "/api/v1/auth/recuperacao/verificar"
URL_REDEFINIR = "/api/v1/auth/recuperacao/redefinir"
URL_USUARIO_ATUAL = "/api/v1/usuarios/me"

SENHA_PADRAO = "senha-valida-123"
CODIGO_PADRAO = "00012345"

Requisicao = Coroutine[Any, Any, httpx.Response]


class LinhaRecuperacao(NamedTuple):
    """Linha de `recuperacao_senha`, lida por outra conexão."""

    usuario_id: uuid.UUID
    codigo_hash: str
    expira_em: datetime
    tentativas: int
    verificado_em: datetime | None
    token_redefinicao_hash: str | None
    utilizado_em: datetime | None


class SequenciaCodigos:
    """Substitui `seguranca.gerar_codigo`; repete o último código."""

    def __init__(self, *codigos: str) -> None:
        self._codigos = codigos
        self.chamadas = 0

    def __call__(self) -> str:
        indice = min(self.chamadas, len(self._codigos) - 1)
        self.chamadas += 1
        return self._codigos[indice]


async def registrar(
    cliente: httpx.AsyncClient, **campos: Any
) -> dict[str, Any]:
    """Registro válido com padrões sintéticos; exige 201."""
    senha = campos.get("senha", SENHA_PADRAO)
    corpo = {
        "nome_completo": "Pessoa Teste",
        "email": f"{uuid.uuid7().hex}@exemplo.com",
        "senha": senha,
        "confirmar_senha": senha,
        "data_nascimento": "1990-01-01",
        "fuso_horario": "America/Sao_Paulo",
    } | campos
    resposta = await cliente.post(URL_REGISTRO, json=corpo)
    assert resposta.status_code == HTTPStatus.CREATED, resposta.text
    return resposta.json()


async def entrar(cliente: httpx.AsyncClient, email: str, senha: str) -> str:
    """Login válido; devolve o `access_token` (exige 200)."""
    resposta = await cliente.post(
        URL_LOGIN, json={"email": email, "senha": senha}
    )
    assert resposta.status_code == HTTPStatus.OK, resposta.text
    return resposta.json()["access_token"]


async def solicitar(cliente: httpx.AsyncClient, email: str) -> httpx.Response:
    """POST de solicitação do código de recuperação."""
    return await cliente.post(URL_SOLICITAR, json={"email": email})


async def verificar(
    cliente: httpx.AsyncClient, email: str, codigo: str
) -> httpx.Response:
    """POST de verificação do código."""
    return await cliente.post(
        URL_VERIFICAR, json={"email": email, "codigo": codigo}
    )


async def redefinir(
    cliente: httpx.AsyncClient, token: str, nova_senha: str
) -> httpx.Response:
    """POST de redefinição, com a confirmação idêntica."""
    return await cliente.post(
        URL_REDEFINIR,
        json={
            "token_redefinicao": token,
            "nova_senha": nova_senha,
            "confirmar_senha": nova_senha,
        },
    )


async def obter_token_redefinicao(
    cliente: httpx.AsyncClient, email: str, codigo: str = CODIGO_PADRAO
) -> str:
    """Solicita e verifica o código; devolve o token de redefinição."""
    solicitacao = await solicitar(cliente, email)
    assert solicitacao.status_code == HTTPStatus.OK, solicitacao.text
    verificacao = await verificar(cliente, email, codigo)
    assert verificacao.status_code == HTTPStatus.OK, verificacao.text
    return verificacao.json()["token_redefinicao"]


def codigo_de_erro(resposta: httpx.Response) -> str:
    """Código de topo do erro padronizado."""
    return resposta.json()["codigo"]


def linha_recuperacao(
    url: str, usuario_id: uuid.UUID | str
) -> LinhaRecuperacao | None:
    """Linha de recuperação do usuário, por conexão independente."""
    alvo = uuid.UUID(str(usuario_id))
    linhas = consultar(
        url,
        "SELECT usuario_id, codigo_hash, expira_em, tentativas, "
        "verificado_em, token_redefinicao_hash, utilizado_em "
        "FROM recuperacao_senha",
    )
    for linha in linhas:
        if linha[0] == alvo:
            return LinhaRecuperacao(*linha)
    return None


async def aguardar_espera_por_trava(
    monitor: AsyncEngine,
    quantidade: int,
    padrao: str,
    timeout: float = 5.0,
) -> None:
    """Espera, por polling, exatamente `quantidade` sessões paradas em lock.

    Conta só sessões `active` esperando por `Lock` cuja consulta casa com
    `padrao`. Passar da quantidade falha na hora; vencer o prazo também.
    """
    consulta = text(
        "SELECT count(*) FROM pg_stat_activity "
        "WHERE datname = current_database() AND state = 'active' "
        "AND wait_event_type = 'Lock' AND pid <> pg_backend_pid() "
        "AND query ILIKE :padrao"
    )
    limite = time.monotonic() + timeout
    atual = -1
    while time.monotonic() < limite:
        async with monitor.connect() as conexao:
            atual = (
                await conexao.execute(consulta, {"padrao": padrao})
            ).scalar_one()
        if atual == quantidade:
            return
        if atual > quantidade:
            msg = (
                f"esperava {quantidade} sessão(ões) em espera por "
                f"{padrao!r}; observadas: {atual}"
            )
            raise AssertionError(msg)
        await asyncio.sleep(INTERVALO_POLLING_S)
    msg = (
        f"esperava {quantidade} sessão(ões) em espera por {padrao!r} "
        f"em {timeout}s; observadas: {atual}"
    )
    raise TimeoutError(msg)


async def _desfazer_e_encerrar(
    bloqueadora: psycopg.Connection,
    tarefas: Sequence[asyncio.Task[httpx.Response]],
) -> None:
    bloqueadora.rollback()
    await asyncio.gather(*tarefas, return_exceptions=True)


async def disparar_simultaneas(
    bloqueadora: psycopg.Connection,
    monitor: AsyncEngine,
    requisicoes: Sequence[Requisicao],
    padrao: str,
    quantidade: int,
) -> list[httpx.Response]:
    """Dispara todas, espera a contagem exata, desfaz a bloqueadora."""
    tarefas = [asyncio.create_task(r) for r in requisicoes]
    try:
        await aguardar_espera_por_trava(monitor, quantidade, padrao)
    except BaseException:
        await _desfazer_e_encerrar(bloqueadora, tarefas)
        raise
    bloqueadora.rollback()
    return list(await asyncio.gather(*tarefas))


async def disparar_em_ordem(
    bloqueadora: psycopg.Connection,
    monitor: AsyncEngine,
    requisicoes: Sequence[Requisicao],
    padrao: str,
) -> list[httpx.Response]:
    """Dispara uma a uma, esperando 1, 2, ... paradas; depois libera."""
    tarefas: list[asyncio.Task[httpx.Response]] = []
    try:
        for posicao, requisicao in enumerate(requisicoes, start=1):
            tarefas.append(asyncio.create_task(requisicao))
            await aguardar_espera_por_trava(monitor, posicao, padrao)
    except BaseException:
        await _desfazer_e_encerrar(bloqueadora, tarefas)
        raise
    bloqueadora.rollback()
    return list(await asyncio.gather(*tarefas))
