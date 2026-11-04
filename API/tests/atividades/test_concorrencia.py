import asyncio
import uuid
from collections.abc import Iterator
from http import HTTPStatus

import httpx
import psycopg
import pytest

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.banco import url_libpq
from ..apoio.esquema import consultar
from .util import URL, criar, listar

pytestmark = pytest.mark.concorrencia


@pytest.fixture
def bloqueadora(banco_migrado: str) -> Iterator[psycopg.Connection]:
    conexao = psycopg.connect(url_libpq(banco_migrado))
    yield conexao
    conexao.rollback()
    conexao.close()


def travar_como_escritor(
    conexao: psycopg.Connection, usuario_id: uuid.UUID
) -> None:
    conexao.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
        (f"minhavida:usuario:{usuario_id}",),
    )


async def test_geracoes_simultaneas_geram_uma_linha_por_posicao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Diária",
        data="2026-10-13",
        repeticao={"periodicidade": "DIARIA"},
    )
    respostas = await asyncio.gather(*[
        cliente.get(
            URL,
            params={"data": "2026-11-20"},
            headers=usuario.cabecalhos,
        )
        for _ in range(6)
    ])
    assert {r.status_code for r in respostas} == {HTTPStatus.OK}
    assert all(r.json()["indicadores"]["total"] == 1 for r in respostas)
    linhas = consultar(
        banco_migrado, "SELECT numero_ocorrencia FROM atividade"
    )
    numeros = [linha[0] for linha in linhas]
    assert len(numeros) == len(set(numeros)) == 2


async def test_leitura_espera_a_escrita_em_andamento(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    bloqueadora: psycopg.Connection,
) -> None:
    """CT-F5-27: a leitura só termina depois do commit do escritor."""
    travar_como_escritor(bloqueadora, usuario.id)
    tarefa = asyncio.create_task(listar(cliente, usuario))
    await asyncio.sleep(0.4)
    assert not tarefa.done()
    bloqueadora.commit()
    resposta = await asyncio.wait_for(tarefa, 5)
    assert resposta["indicadores"]["total"] == 0


async def test_escritas_do_mesmo_usuario_sao_serializadas(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    bloqueadora: psycopg.Connection,
) -> None:
    travar_como_escritor(bloqueadora, usuario.id)
    tarefa = asyncio.create_task(criar(cliente, usuario, nome="Aguardando"))
    await asyncio.sleep(0.4)
    assert not tarefa.done()
    bloqueadora.rollback()
    await asyncio.wait_for(tarefa, 5)
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 1


async def test_usuarios_diferentes_nao_se_bloqueiam(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    bloqueadora: psycopg.Connection,
) -> None:

    outro = await criar_usuario(cliente)
    travar_como_escritor(bloqueadora, usuario.id)
    resposta = await asyncio.wait_for(listar(cliente, outro), 3)
    assert resposta["indicadores"]["total"] == 0


async def test_conclusao_concorrente_com_exclusao_de_serie(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    primeira = await criar(
        cliente,
        usuario,
        nome="Semanal",
        data="2026-10-13",
        repeticao={
            "periodicidade": "SEMANAL",
            "termino": "ATE_DATA",
            "data_final": "2026-10-27",
        },
    )
    segunda = (await listar(cliente, usuario, data="2026-10-20"))["itens"][0]
    concluir, excluir = await asyncio.gather(
        cliente.put(
            f"{URL}/{segunda['id']}/situacao",
            json={"situacao": "CONCLUIDA"},
            headers=usuario.cabecalhos,
        ),
        cliente.delete(
            f"{URL}/{primeira['id']}",
            params={"alcance": "ESTA_E_PROXIMAS"},
            headers=usuario.cabecalhos,
        ),
    )
    assert excluir.status_code == HTTPStatus.NO_CONTENT
    # Ou a conclusão veio antes (preservada) ou depois (404): nunca meio-termo.
    if concluir.status_code == HTTPStatus.OK:
        detalhe = await cliente.get(
            f"{URL}/{segunda['id']}", headers=usuario.cabecalhos
        )
        assert detalhe.json()["situacao"] == "CONCLUIDA"
    else:
        assert concluir.status_code == HTTPStatus.NOT_FOUND
