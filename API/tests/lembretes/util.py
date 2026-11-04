"""Auxiliares dos testes do processador de lembretes e notificações."""

from datetime import datetime
from typing import Any, LiteralString

import httpx
import psycopg
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api_gestao_pessoal.services.processamento_lembretes import (
    ResultadoCiclo,
    executar_ciclo,
)

from ..apoio.api import UsuarioTeste
from ..apoio.banco import url_libpq
from ..apoio.relogio import RelogioFixo

URL_NOTIFICACOES = "/api/v1/notificacoes"


async def ciclo(
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    *,
    lote: int = 100,
    janela_dias: int = 8,
) -> ResultadoCiclo:
    def agora() -> datetime:
        return relogio.agora()

    return await executar_ciclo(
        fabrica, agora, lote=lote, janela_dias=janela_dias
    )


def consultar(banco: str, sql: LiteralString, *params: Any) -> list[tuple]:
    with psycopg.connect(url_libpq(banco)) as conexao:
        return [tuple(linha) for linha in conexao.execute(sql, params)]


def notificacoes_no_banco(banco: str) -> list[tuple]:
    """`(titulo, mensagem, versao)` ordenadas por criação."""
    return consultar(
        banco,
        "SELECT titulo, mensagem, versao_agendamento FROM notificacao "
        "ORDER BY criada_em, id",
    )


async def listar_notificacoes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, **params: Any
) -> dict[str, Any]:
    r = await cliente.get(
        URL_NOTIFICACOES, params=params, headers=usuario.cabecalhos
    )
    assert r.status_code == 200, r.text
    return r.json()
