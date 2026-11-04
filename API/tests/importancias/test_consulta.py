from datetime import timedelta
from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.identidade import codigo_de_erro
from ..apoio.relogio import RelogioFixo
from .util import URL, criar, listar, nomes, situacao


async def cenario(cliente, usuario) -> dict[str, dict]:
    """Atrasada, hoje, próximas (outubro e novembro) e concluída."""
    return {
        "atrasada": await criar(
            cliente,
            usuario,
            nome="Fatura do cartão",
            data_compromisso="2026-10-09",
            possui_despesa=True,
            valor_previsto="480",
        ),
        "hoje": await criar(
            cliente,
            usuario,
            nome="Pagamento da internet",
            data_compromisso="2026-10-13",
            horario="08:00",
            possui_despesa=True,
            valor_previsto="99.90",
        ),
        "compra": await criar(
            cliente,
            usuario,
            nome="Compra do mês",
            data_compromisso="2026-10-19",
            possui_despesa=True,
            valor_previsto="245.30",
        ),
        "aniv": await criar(
            cliente,
            usuario,
            nome="Aniversário da mãe",
            data_compromisso="2026-10-26",
        ),
        "nov": await criar(
            cliente,
            usuario,
            nome="Licenciamento",
            data_compromisso="2026-11-05",
            possui_despesa=True,
            valor_previsto="120",
        ),
        "feita": await criar(
            cliente,
            usuario,
            nome="Mensalidade da academia",
            data_compromisso="2026-10-01",
        ),
    }


async def test_todos_agrupa_e_ordena(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    itens = await cenario(cliente, usuario)
    await situacao(cliente, usuario, itens["feita"]["id"], "CONCLUIDA")
    r = await listar(cliente, usuario)
    assert r["filtro"] == "TODOS"
    assert r["grupos"] == {
        "atrasadas": 1,
        "hoje": 1,
        "proximas": 3,
        "concluidas": 1,
    }
    assert r["total"] == 6
    assert [(i["grupo"], i["nome"]) for i in r["itens"]] == [
        ("ATRASADAS", "Fatura do cartão"),
        ("HOJE", "Pagamento da internet"),
        ("PROXIMAS", "Compra do mês"),
        ("PROXIMAS", "Aniversário da mãe"),
        ("PROXIMAS", "Licenciamento"),
        ("CONCLUIDAS", "Mensalidade da academia"),
    ]
    assert r["possui_importancias"] is True
    assert r["horizonte_proximas"] == "2027-10-31"
    assert r["mes"] is None
    assert r["rotulo_periodo"] is None
    assert r["itens"][2]["prazo"] == "EM_DIAS"
    assert r["itens"][2]["dias_ate_vencimento"] == 6


async def test_filtros_7_2(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    itens = await cenario(cliente, usuario)
    await situacao(cliente, usuario, itens["feita"]["id"], "CONCLUIDA")
    assert await nomes(cliente, usuario, filtro="VENCENDO_HOJE") == [
        "Pagamento da internet"
    ]
    assert await nomes(cliente, usuario, filtro="ATRASADOS") == [
        "Fatura do cartão"
    ]
    assert await nomes(cliente, usuario, filtro="PROXIMOS") == [
        "Compra do mês",
        "Aniversário da mãe",
        "Licenciamento",
    ]
    assert await nomes(cliente, usuario, filtro="CONCLUIDOS") == [
        "Mensalidade da academia"
    ]
    este = await listar(cliente, usuario, filtro="ESTE_MES", limite=50)
    assert [i["nome"] for i in este["itens"]] == [
        "Fatura do cartão",
        "Pagamento da internet",
        "Compra do mês",
        "Aniversário da mãe",
        "Mensalidade da academia",
    ]
    assert este["mes"] == "2026-10"
    assert este["rotulo_periodo"] == "Este mês"
    nov = await listar(cliente, usuario, filtro="ESTE_MES", mes="2026-11")
    assert [i["nome"] for i in nov["itens"]] == ["Licenciamento"]
    assert nov["rotulo_periodo"] == "Mês selecionado"
    # Próximos não depende do mês consultado antes (7.4.3).
    assert "Licenciamento" in await nomes(cliente, usuario, filtro="PROXIMOS")


async def test_mes_so_com_este_mes_e_validacao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await cliente.get(
        URL,
        params={"filtro": "TODOS", "mes": "2026-10"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json()["campos"][0]["campo"] == "mes"
    for params in (
        {"mes": "2026-13", "filtro": "ESTE_MES"},
        {"filtro": "OUTRO"},
        {"limite": 0},
        {"limite": 51},
    ):
        assert (
            await cliente.get(URL, params=params, headers=usuario.cabecalhos)
        ).status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_busca_e_estados_vazios(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    vazio = await listar(cliente, usuario)
    assert vazio["possui_importancias"] is False
    assert vazio["itens"] == []
    await cenario(cliente, usuario)
    assert await nomes(cliente, usuario, busca="  CARTÃO ".lower()) == [
        "Fatura do cartão"
    ]
    semresultado = await listar(cliente, usuario, busca="inexistente")
    assert semresultado["itens"] == []
    assert semresultado["possui_importancias"] is True
    assert semresultado["total"] == 0


async def test_pendente_de_hoje_vira_atrasada_no_dia_seguinte_7_4_2(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, relogio: RelogioFixo
) -> None:
    i = await criar(
        cliente, usuario, nome="Conta de hoje", data_compromisso="2026-10-13"
    )
    feita = await criar(
        cliente, usuario, nome="Conta feita", data_compromisso="2026-10-13"
    )
    await situacao(cliente, usuario, feita["id"], "CONCLUIDA")
    assert await nomes(cliente, usuario, filtro="VENCENDO_HOJE") == [
        "Conta de hoje"
    ]
    relogio.avancar(timedelta(hours=20))  # 05:00 do dia 14, no fuso do usuário
    assert await nomes(cliente, usuario, filtro="VENCENDO_HOJE") == []
    assert await nomes(cliente, usuario, filtro="ATRASADOS") == [
        "Conta de hoje"
    ]
    atrasada = (await listar(cliente, usuario, filtro="ATRASADOS"))["itens"][0]
    assert atrasada["prazo"] == "ATRASADA"
    assert atrasada["dias_ate_vencimento"] == -1
    assert i["id"] == atrasada["id"]
    # Concluída nunca fica atrasada.
    assert await nomes(cliente, usuario, filtro="CONCLUIDOS") == [
        "Conta feita"
    ]


async def test_paginacao_atravessa_os_grupos(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for i in range(3):
        await criar(
            cliente,
            usuario,
            nome=f"Atrasada {i}",
            data_compromisso=f"2026-10-0{i + 1}",
        )
    for i in range(4):
        await criar(
            cliente,
            usuario,
            nome=f"Próxima {i}",
            data_compromisso=f"2026-10-2{i}",
        )
    feitas = [
        await criar(
            cliente, usuario, nome=f"Feita {i}", data_compromisso="2026-10-05"
        )
        for i in range(2)
    ]
    for f in feitas:
        await situacao(cliente, usuario, f["id"], "CONCLUIDA")
    for tamanho in (1, 2, 3, 4):
        vistos: list[str] = []
        cursor = None
        paginas = 0
        while True:
            params = {"limite": tamanho}
            if cursor:
                params["cursor"] = cursor
            pagina = await listar(cliente, usuario, **params)
            assert pagina["total"] == 9
            assert pagina["grupos"] == {
                "atrasadas": 3,
                "hoje": 0,
                "proximas": 4,
                "concluidas": 2,
            }
            vistos += [i["id"] for i in pagina["itens"]]
            paginas += 1
            cursor = pagina["proximo_cursor"]
            if cursor is None:
                break
        assert len(vistos) == len(set(vistos)) == 9, tamanho
        assert paginas == -(-9 // tamanho), tamanho
    r = await cliente.get(
        URL, params={"cursor": "lixo"}, headers=usuario.cabecalhos
    )
    assert codigo_de_erro(r) == "CURSOR_INVALIDO"
    primeira = await listar(cliente, usuario, limite=1)
    outro = await cliente.get(
        URL,
        params={
            "limite": 1,
            "cursor": primeira["proximo_cursor"],
            "filtro": "PROXIMOS",
        },
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(outro) == "CURSOR_INVALIDO"


async def test_sem_horario_vem_depois_na_mesma_data(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente, usuario, nome="Sem horário", data_compromisso="2026-10-20"
    )
    await criar(
        cliente,
        usuario,
        nome="Tarde",
        data_compromisso="2026-10-20",
        horario="15:00",
    )
    await criar(
        cliente,
        usuario,
        nome="Cedo",
        data_compromisso="2026-10-20",
        horario="08:00",
    )
    assert await nomes(cliente, usuario) == ["Cedo", "Tarde", "Sem horário"]
    pag = []
    cursor = None
    while True:
        params = {"limite": 1}
        if cursor:
            params["cursor"] = cursor
        p = await listar(cliente, usuario, **params)
        pag += [i["nome"] for i in p["itens"]]
        cursor = p["proximo_cursor"]
        if not cursor:
            break
    assert pag == ["Cedo", "Tarde", "Sem horário"]


async def test_concluidas_mais_recentes_primeiro(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, relogio: RelogioFixo
) -> None:
    a = await criar(cliente, usuario, nome="Primeira feita")
    b = await criar(cliente, usuario, nome="Segunda feita")
    await situacao(cliente, usuario, a["id"], "CONCLUIDA")
    relogio.avancar(timedelta(minutes=5))
    await situacao(cliente, usuario, b["id"], "CONCLUIDA")
    assert await nomes(cliente, usuario, filtro="CONCLUIDOS") == [
        "Segunda feita",
        "Primeira feita",
    ]


async def test_isolamento_entre_usuarios(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    outro = await criar_usuario(cliente)
    minha = await criar(cliente, usuario)
    assert (await listar(cliente, outro))["total"] == 0
    for metodo, caminho, corpo in (
        ("GET", f"{URL}/{minha['id']}", None),
        ("PATCH", f"{URL}/{minha['id']}", {"nome": "Invadida"}),
        ("PUT", f"{URL}/{minha['id']}/situacao", {"situacao": "CONCLUIDA"}),
        ("DELETE", f"{URL}/{minha['id']}", None),
    ):
        r = await cliente.request(
            metodo, caminho, headers=outro.cabecalhos, json=corpo
        )
        assert r.status_code == HTTPStatus.NOT_FOUND, metodo
    assert (await listar(cliente, usuario))["total"] == 1
