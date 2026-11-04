"""CT-F9: endpoints de notificações (arquitetura §9.6)."""

from datetime import timedelta
from http import HTTPStatus

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.relogio import RelogioFixo
from ..importancias.util import criar
from .util import URL_NOTIFICACOES, ciclo, listar_notificacoes

LEMBRETE = {"antecedencia_dias": 3, "horario": "09:00"}


async def _gerar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    quantidade: int = 1,
) -> list[dict]:
    criadas = [
        await criar(
            cliente, usuario, nome=f"Conta numero {i}", lembrete=LEMBRETE
        )
        for i in range(quantidade)
    ]
    relogio.avancar(timedelta(days=4))
    await ciclo(fabrica, relogio)
    relogio.avancar(-timedelta(days=4))  # o token do usuário expiraria
    return criadas


async def test_exige_autenticacao(cliente: httpx.AsyncClient) -> None:
    for caminho in ("", "/nao-lidas"):
        r = await cliente.get(URL_NOTIFICACOES + caminho)
        assert r.status_code == HTTPStatus.UNAUTHORIZED


async def test_lista_vazia_e_contador_zero(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    assert await listar_notificacoes(cliente, usuario) == {
        "itens": [],
        "proximo_cursor": None,
    }
    r = await cliente.get(
        f"{URL_NOTIFICACOES}/nao-lidas", headers=usuario.cabecalhos
    )
    assert r.json() == {"quantidade": 0}


async def test_listar_contar_e_marcar_como_lida(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
) -> None:
    criadas = await _gerar(cliente, usuario, fabrica, relogio)
    pagina = await listar_notificacoes(cliente, usuario)
    (item,) = pagina["itens"]
    assert item["lida"] is False
    assert item["titulo"] == "Lembrete: Conta numero 0"
    assert item["importancia"] == {"id": criadas[0]["id"], "disponivel": True}
    nao_lidas = await cliente.get(
        f"{URL_NOTIFICACOES}/nao-lidas", headers=usuario.cabecalhos
    )
    assert nao_lidas.json() == {"quantidade": 1}

    for _ in range(2):  # idempotente
        r = await cliente.post(
            f"{URL_NOTIFICACOES}/{item['id']}/leitura",
            headers=usuario.cabecalhos,
        )
        assert r.status_code == HTTPStatus.OK
        assert r.json()["lida"] is True
    nao_lidas = await cliente.get(
        f"{URL_NOTIFICACOES}/nao-lidas", headers=usuario.cabecalhos
    )
    assert nao_lidas.json() == {"quantidade": 0}
    # Ler não conclui a importância.
    r = await cliente.get(
        f"/api/v1/importancias/{criadas[0]['id']}", headers=usuario.cabecalhos
    )
    assert r.json()["situacao"] == "PENDENTE"


async def test_importancia_excluida_fica_indisponivel(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
) -> None:
    (imp,) = await _gerar(cliente, usuario, fabrica, relogio)
    r = await cliente.delete(
        f"/api/v1/importancias/{imp['id']}", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    (item,) = (await listar_notificacoes(cliente, usuario))["itens"]
    assert item["importancia"]["disponivel"] is False
    assert "Conta numero 0" in item["mensagem"]  # texto congelado


async def test_outro_usuario_nao_ve_nem_le(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
) -> None:
    await _gerar(cliente, usuario, fabrica, relogio)
    (item,) = (await listar_notificacoes(cliente, usuario))["itens"]
    outro = await criar_usuario(cliente)
    assert (await listar_notificacoes(cliente, outro))["itens"] == []
    r = await cliente.post(
        f"{URL_NOTIFICACOES}/{item['id']}/leitura", headers=outro.cabecalhos
    )
    assert r.status_code == HTTPStatus.NOT_FOUND
    r = await cliente.post(
        f"{URL_NOTIFICACOES}/nao-e-uuid/leitura", headers=outro.cabecalhos
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_paginacao_mais_recentes_primeiro(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
) -> None:
    await _gerar(cliente, usuario, fabrica, relogio, quantidade=5)
    vistos: list[str] = []
    cursor = None
    while True:
        params = {"limite": 2} | ({"cursor": cursor} if cursor else {})
        pagina = await listar_notificacoes(cliente, usuario, **params)
        vistos += [i["id"] for i in pagina["itens"]]
        cursor = pagina["proximo_cursor"]
        if cursor is None:
            break
    assert len(vistos) == 5
    assert len(set(vistos)) == 5


async def test_cursor_invalido(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await cliente.get(
        URL_NOTIFICACOES,
        params={"cursor": "lixo"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json()["codigo"] == "CURSOR_INVALIDO"
