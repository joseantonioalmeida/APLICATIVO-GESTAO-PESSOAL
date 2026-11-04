from datetime import UTC, datetime
from decimal import Decimal
from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.identidade import codigo_de_erro
from ..apoio.relogio import RelogioFixo
from .util import BASE, despesa, movimentacoes, receita, resumo


async def test_saldo_9_4_1_e_negativo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await receita(cliente, usuario, valor="2450.75")
    await despesa(cliente, usuario, valor="1230.40", nome="Despesas do mês")
    r = await resumo(cliente, usuario)
    assert (r["receitas"], r["despesas"], r["saldo"]) == (
        "2450.75",
        "1230.40",
        "1220.35",
    )
    await despesa(cliente, usuario, valor="2000", nome="Despesa grande")
    r2 = await resumo(cliente, usuario)
    assert r2["saldo"] == "-779.65"


async def test_centavos_exatos_9_4_3(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await receita(cliente, usuario, valor="0.10", nome="Receita A")
    await receita(cliente, usuario, valor="0.20", nome="Receita B")
    await despesa(cliente, usuario, valor="0.10", nome="Despesa A")
    r = await resumo(cliente, usuario)
    assert (r["receitas"], r["despesas"], r["saldo"]) == (
        "0.30",
        "0.10",
        "0.20",
    )


async def test_estrutura_do_resumo_e_coerencia(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await receita(
        cliente, usuario, valor="2450.75", data_movimentacao="2026-10-13"
    )
    await despesa(
        cliente,
        usuario,
        valor="600",
        nome="Aluguel",
        categoria_nome="Moradia",
        data_movimentacao="2026-10-02",
    )
    await despesa(
        cliente,
        usuario,
        valor="245.30",
        nome="Mercado",
        data_movimentacao="2026-10-12",
    )
    await despesa(
        cliente,
        usuario,
        valor="89.90",
        nome="Restaurante",
        data_movimentacao="2026-10-12",
    )
    await despesa(
        cliente,
        usuario,
        valor="32.50",
        nome="Uber",
        categoria_nome="Transporte",
        data_movimentacao="2026-10-10",
    )
    await despesa(
        cliente,
        usuario,
        valor="12",
        nome="Outra coisa",
        categoria_nome="Outros",
        data_movimentacao="2026-10-01",
    )
    r = await resumo(cliente, usuario)
    assert r["mes"] == "2026-10"
    assert r["periodo"] == {"inicio": "2026-10-01", "fim": "2026-10-31"}
    grafico = r["grafico_diario"]
    assert len(grafico) == 31
    assert grafico[0]["data"] == "2026-10-01"
    assert grafico[2] == {
        "data": "2026-10-03",
        "receitas": "0.00",
        "despesas": "0.00",
    }
    # 9.2.4: gráfico e categorias batem com os indicadores.
    assert sum(Decimal(d["receitas"]) for d in grafico) == Decimal(
        r["receitas"]
    )
    assert sum(Decimal(d["despesas"]) for d in grafico) == Decimal(
        r["despesas"]
    )
    cats = r["categorias_despesa"]
    assert sum(Decimal(c["total"]) for c in cats) == Decimal(r["despesas"])
    assert [c["categoria"]["nome"] for c in cats] == [
        "Moradia",
        "Alimentação",
        "Transporte",
        "Outros",
    ]
    assert cats[1]["total"] == "335.20"
    assert len(r["ultimas_movimentacoes"]) == 5
    assert r["ultimas_movimentacoes"][0]["nome"] == "Salário"


async def test_meses_de_28_29_30_e_31_dias(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    esperado = {"2026-02": 28, "2028-02": 29, "2026-04": 30, "2026-10": 31}
    for mes, dias in esperado.items():
        r = await resumo(cliente, usuario, mes)
        assert len(r["grafico_diario"]) == dias, mes
        assert r["receitas"] == "0.00"
        assert r["categorias_despesa"] == []


async def test_mes_invalido(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for mes in ("2026-13", "2026-1", "outubro", "1999-12", "2101-01"):
        r = await cliente.get(
            f"{BASE}/resumo", params={"mes": mes}, headers=usuario.cabecalhos
        )
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, mes


async def test_recebimento_de_setembro_cadastrado_em_outubro_compoe_setembro(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """9.4.2: mudar a data move o lançamento entre os meses."""
    r1 = await receita(
        cliente, usuario, valor="100", data_movimentacao="2026-09-20"
    )
    assert (await resumo(cliente, usuario, "2026-09"))["receitas"] == "100.00"
    assert (await resumo(cliente, usuario, "2026-10"))["receitas"] == "0.00"
    p = await cliente.patch(
        f"{BASE}/movimentacoes/{r1['id']}",
        json={"data_movimentacao": "2026-10-05"},
        headers=usuario.cabecalhos,
    )
    assert p.status_code == HTTPStatus.OK
    assert (await resumo(cliente, usuario, "2026-09"))["receitas"] == "0.00"
    assert (await resumo(cliente, usuario, "2026-10"))["receitas"] == "100.00"
    assert (
        len((await movimentacoes(cliente, usuario, mes="2026-10"))["itens"])
        == 1
    )


async def test_comparacao_do_mes_atual_usa_o_mesmo_intervalo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    # Hoje é 13/10. Base: 01–13/09. Lançamento de 20/09 fica fora da base.
    await despesa(
        cliente,
        usuario,
        valor="1000",
        nome="Base setembro",
        data_movimentacao="2026-09-05",
    )
    await despesa(
        cliente,
        usuario,
        valor="500",
        nome="Fora do intervalo",
        data_movimentacao="2026-09-20",
    )
    await despesa(
        cliente,
        usuario,
        valor="1100",
        nome="Atual",
        data_movimentacao="2026-10-05",
    )
    await receita(cliente, usuario, valor="50", data_movimentacao="2026-10-02")
    r = await resumo(cliente, usuario, "2026-10")
    d = r["comparacao"]["despesas"]
    assert d["intervalo_atual"] == {
        "inicio": "2026-10-01",
        "fim": "2026-10-13",
    }
    assert d["intervalo_anterior"] == {
        "inicio": "2026-09-01",
        "fim": "2026-09-13",
    }
    assert (d["total_atual"], d["total_anterior"]) == ("1100.00", "1000.00")
    assert (d["variacao_percentual"], d["tendencia"]) == ("10.0", "AUMENTO")
    rec = r["comparacao"]["receitas"]
    assert (rec["variacao_percentual"], rec["tendencia"]) == (None, "SEM_BASE")


async def test_comparacao_de_mes_encerrado_e_estabilidade_reducao_e_zeros(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await despesa(
        cliente,
        usuario,
        valor="100",
        nome="Julho",
        data_movimentacao="2026-07-10",
    )
    await despesa(
        cliente,
        usuario,
        valor="100",
        nome="Agosto",
        data_movimentacao="2026-08-31",
    )
    await despesa(
        cliente,
        usuario,
        valor="75",
        nome="Setembro",
        data_movimentacao="2026-09-30",
    )
    ago = (await resumo(cliente, usuario, "2026-08"))["comparacao"]["despesas"]
    assert ago["intervalo_atual"] == {
        "inicio": "2026-08-01",
        "fim": "2026-08-31",
    }
    assert ago["intervalo_anterior"] == {
        "inicio": "2026-07-01",
        "fim": "2026-07-31",
    }
    assert (ago["variacao_percentual"], ago["tendencia"]) == (
        "0.0",
        "ESTABILIDADE",
    )
    setembro = (await resumo(cliente, usuario, "2026-09"))["comparacao"][
        "despesas"
    ]
    assert (setembro["variacao_percentual"], setembro["tendencia"]) == (
        "-25.0",
        "REDUCAO",
    )
    vazio = (await resumo(cliente, usuario, "2026-05"))["comparacao"][
        "receitas"
    ]
    assert (vazio["variacao_percentual"], vazio["tendencia"]) == (
        None,
        "SEM_MOVIMENTACAO",
    )


async def test_mes_futuro_nao_tem_variacao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await resumo(cliente, usuario, "2026-12")
    for tipo in ("receitas", "despesas"):
        c = r["comparacao"][tipo]
        assert c["tendencia"] == "NAO_APLICAVEL"
        assert c["variacao_percentual"] is None
        assert c["intervalo_atual"] is None


async def test_mes_atual_limita_o_anterior_ao_ultimo_dia_do_mes_anterior(
    cliente: httpx.AsyncClient, relogio: RelogioFixo
) -> None:
    relogio._instante = datetime(2026, 3, 31, 15, 0, tzinfo=UTC)
    usuario = await criar_usuario(cliente)  # token emitido no novo "agora"
    r = await resumo(cliente, usuario, "2026-03")
    d = r["comparacao"]["despesas"]
    assert d["intervalo_atual"] == {
        "inicio": "2026-03-01",
        "fim": "2026-03-31",
    }
    assert d["intervalo_anterior"] == {
        "inicio": "2026-02-01",
        "fim": "2026-02-28",
    }


async def test_arredondamento_meio_para_cima(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    # 1000 -> 1000.50: +0,05% -> 0,1 (ROUND_HALF_UP).
    await despesa(
        cliente,
        usuario,
        valor="1000",
        nome="Base",
        data_movimentacao="2026-09-01",
    )
    await despesa(
        cliente,
        usuario,
        valor="1000.50",
        nome="Atual",
        data_movimentacao="2026-10-01",
    )
    d = (await resumo(cliente, usuario))["comparacao"]["despesas"]
    assert d["variacao_percentual"] == "0.1"


async def test_isolamento_entre_usuarios(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    outro = await criar_usuario(cliente)
    mov = await receita(cliente, usuario)
    assert (await resumo(cliente, outro))["receitas"] == "0.00"
    for metodo in ("GET", "PATCH", "DELETE"):
        r = await cliente.request(
            metodo,
            f"{BASE}/movimentacoes/{mov['id']}",
            headers=outro.cabecalhos,
            json={"nome": "Invadida"} if metodo == "PATCH" else None,
        )
        assert r.status_code == HTTPStatus.NOT_FOUND, metodo
        assert codigo_de_erro(r) == "RECURSO_NAO_ENCONTRADO"
