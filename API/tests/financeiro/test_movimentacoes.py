from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste
from ..apoio.identidade import codigo_de_erro
from .util import BASE, categoria, despesa, movimentacoes, receita, resumo


async def test_lista_ordenada_e_filtros(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await despesa(
        cliente, usuario, nome="Mercado", data_movimentacao="2026-10-12"
    )
    await despesa(
        cliente,
        usuario,
        nome="Restaurante Bom",
        data_movimentacao="2026-10-11",
    )
    await receita(
        cliente, usuario, nome="Salário", data_movimentacao="2026-10-13"
    )
    await despesa(
        cliente, usuario, nome="Padaria", data_movimentacao="2026-10-12"
    )
    todas = await movimentacoes(cliente, usuario)
    # Mesma data: o cadastrado mais recentemente vem primeiro.
    assert [i["nome"] for i in todas["itens"]] == [
        "Salário",
        "Padaria",
        "Mercado",
        "Restaurante Bom",
    ]
    assert todas["filtros_ativos"] is False
    assert todas["possui_movimentacoes_mes"] is True
    assert todas["mes"] == "2026-10"
    desp = await movimentacoes(cliente, usuario, tipo="DESPESA")
    assert {i["tipo"] for i in desp["itens"]} == {"DESPESA"}
    assert desp["filtros_ativos"] is True
    rec = await movimentacoes(cliente, usuario, tipo="RECEITA")
    assert [i["nome"] for i in rec["itens"]] == ["Salário"]
    busca = await movimentacoes(cliente, usuario, busca=" RESTAURANTE ")
    assert [i["nome"] for i in busca["itens"]] == ["Restaurante Bom"]
    alim = await categoria(cliente, usuario, "DESPESA", "Alimentação")
    cat = await movimentacoes(cliente, usuario, categoria_id=alim)
    assert len(cat["itens"]) == 3
    # Os filtros não mudam os totais do resumo (9.2.5, 9.4.4).
    assert (await resumo(cliente, usuario))["despesas"] == "735.90"
    vazio = await movimentacoes(cliente, usuario, busca="inexistente")
    assert vazio["itens"] == []
    assert vazio["possui_movimentacoes_mes"] is True


async def test_mes_sem_movimentacoes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await movimentacoes(cliente, usuario, mes="2026-01")
    assert r["itens"] == []
    assert r["possui_movimentacoes_mes"] is False


async def test_categoria_incompativel_com_o_tipo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    receita_cat = await categoria(cliente, usuario, "RECEITA", "Vendas")
    r = await cliente.get(
        f"{BASE}/movimentacoes",
        params={"tipo": "DESPESA", "categoria_id": receita_cat},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ok = await cliente.get(
        f"{BASE}/movimentacoes",
        params={"categoria_id": receita_cat},
        headers=usuario.cabecalhos,
    )
    assert ok.status_code == HTTPStatus.OK
    inexistente = await cliente.get(
        f"{BASE}/movimentacoes",
        params={"categoria_id": "01900000-0000-7000-8000-000000000000"},
        headers=usuario.cabecalhos,
    )
    assert inexistente.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_paginacao_sem_duplicar(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for i in range(23):
        await despesa(
            cliente,
            usuario,
            nome=f"Despesa {i:02d}",
            valor="1.50",
            data_movimentacao=f"2026-10-{i // 3 + 1:02d}",
        )
    vistos: list[str] = []
    cursor = None
    paginas = 0
    while True:
        params = {"limite": 10}
        if cursor:
            params["cursor"] = cursor
        pagina = await movimentacoes(cliente, usuario, **params)
        vistos += [i["id"] for i in pagina["itens"]]
        paginas += 1
        cursor = pagina["proximo_cursor"]
        if cursor is None:
            break
    assert paginas == 3
    assert len(vistos) == len(set(vistos)) == 23
    r = await cliente.get(
        f"{BASE}/movimentacoes",
        params={"cursor": "lixo"},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(r) == "CURSOR_INVALIDO"


async def test_cursor_de_outro_filtro_e_recusado(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for i in range(3):
        await despesa(cliente, usuario, nome=f"Despesa {i}")
    primeira = await movimentacoes(cliente, usuario, limite=1)
    r = await cliente.get(
        f"{BASE}/movimentacoes",
        params={
            "limite": 1,
            "cursor": primeira["proximo_cursor"],
            "tipo": "DESPESA",
        },
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(r) == "CURSOR_INVALIDO"


async def test_edicao_atualiza_o_mesmo_lancamento(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """10.5.4: 100 -> 120 sem manter uma segunda receita."""
    mov = await receita(cliente, usuario, valor="100", descricao="Original")
    r = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"valor": "120", "nome": "Serviço entregue", "forma": "PIX"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK
    corpo = r.json()
    assert corpo["id"] == mov["id"]
    assert corpo["tipo"] == "RECEITA"
    assert corpo["valor"] == "120.00"
    assert corpo["descricao"] == "Original"
    assert corpo["forma"] == "PIX"
    resumo_mes = await resumo(cliente, usuario)
    assert resumo_mes["receitas"] == "120.00"
    sem_forma = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"forma": None, "descricao": None},
        headers=usuario.cabecalhos,
    )
    assert sem_forma.json()["forma"] is None
    assert sem_forma.json()["descricao"] is None


async def test_edicao_valida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    mov = await despesa(cliente, usuario)
    url = f"{BASE}/movimentacoes/{mov['id']}"
    for corpo in (
        {"valor": "0"},
        {"valor": "1.234"},
        {"nome": None},
        {"valor": None},
        {"categoria_id": None},
        {"data_movimentacao": None},
        {"tipo": "RECEITA", "valor": "abc"},
    ):
        r = await cliente.patch(url, json=corpo, headers=usuario.cabecalhos)
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, corpo
    futura = await cliente.patch(
        url,
        json={"data_movimentacao": "2026-12-01"},
        headers=usuario.cabecalhos,
    )
    assert futura.json()["campos"][0]["codigo"] == "DATA_FUTURA"
    forma = await cliente.patch(
        url, json={"forma": "DEPOSITO"}, headers=usuario.cabecalhos
    )
    assert forma.json()["campos"][0]["codigo"] == "FORMA_INCOMPATIVEL"
    receita_cat = await categoria(cliente, usuario, "RECEITA", "Vendas")
    cat = await cliente.patch(
        url, json={"categoria_id": receita_cat}, headers=usuario.cabecalhos
    )
    assert cat.json()["campos"][0]["codigo"] == "CATEGORIA_INVALIDA"
    # O tipo é imutável: o campo é ignorado.
    ignorado = await cliente.patch(
        url,
        json={"tipo": "RECEITA", "nome": "Segue despesa"},
        headers=usuario.cabecalhos,
    )
    assert ignorado.json()["tipo"] == "DESPESA"


async def test_exclusao_remove_dos_totais_e_e_idempotente(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    mov = await receita(cliente, usuario, valor="100")
    d = await despesa(cliente, usuario, valor="30")
    assert (await resumo(cliente, usuario))["saldo"] == "70.00"
    r = await cliente.delete(
        f"{BASE}/movimentacoes/{d['id']}", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    again = await cliente.delete(
        f"{BASE}/movimentacoes/{d['id']}", headers=usuario.cabecalhos
    )
    assert again.status_code == HTTPStatus.NO_CONTENT
    assert (await resumo(cliente, usuario))["saldo"] == "100.00"
    assert [
        i["id"] for i in (await movimentacoes(cliente, usuario))["itens"]
    ] == [mov["id"]]
    detalhe = await cliente.get(
        f"{BASE}/movimentacoes/{d['id']}", headers=usuario.cabecalhos
    )
    assert detalhe.status_code == HTTPStatus.NOT_FOUND
    edicao = await cliente.patch(
        f"{BASE}/movimentacoes/{d['id']}",
        json={"nome": "Volta"},
        headers=usuario.cabecalhos,
    )
    assert edicao.status_code == HTTPStatus.NOT_FOUND
    inexistente = await cliente.delete(
        f"{BASE}/movimentacoes/01900000-0000-7000-8000-000000000000",
        headers=usuario.cabecalhos,
    )
    assert inexistente.status_code == HTTPStatus.NOT_FOUND


async def test_despesa_maior_que_a_receita_e_aceita_11_6_2(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await receita(cliente, usuario, valor="100")
    await despesa(cliente, usuario, valor="130")
    assert (await resumo(cliente, usuario))["saldo"] == "-30.00"


async def test_total_da_consulta_independe_da_paginacao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for i in range(3):
        await despesa(cliente, usuario, nome=f"Compra numero {i}")
    await receita(cliente, usuario, nome="Salario do mes")
    r = await cliente.get(
        f"{BASE}/movimentacoes",
        params={"limite": 2, "tipo": "DESPESA"},
        headers=usuario.cabecalhos,
    )
    corpo = r.json()
    assert len(corpo["itens"]) == 2
    assert corpo["total"] == 3
    r = await cliente.get(f"{BASE}/movimentacoes", headers=usuario.cabecalhos)
    assert r.json()["total"] == 4
