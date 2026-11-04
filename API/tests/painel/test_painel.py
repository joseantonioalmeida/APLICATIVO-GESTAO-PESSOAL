"""CT-F10: painel inicial (arquitetura §8.10 e tela 4)."""

from http import HTTPStatus
from typing import Any

import httpx

from ..apoio.api import UsuarioTeste
from ..atividades.util import URL as URL_ATIVIDADES
from ..atividades.util import criar as criar_atividade
from ..financeiro.util import BASE, despesa, receita
from ..importancias.util import criar as criar_importancia
from ..importancias.util import situacao as situacao_importancia
from ..pagamentos.util import pagar

PAINEL = "/api/v1/painel"


async def situacao_atividade(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, id_: str, valor: str
) -> httpx.Response:
    return await cliente.put(
        f"{URL_ATIVIDADES}/{id_}/situacao",
        json={"situacao": valor},
        headers=usuario.cabecalhos,
    )


async def bloco(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, nome: str
) -> dict[str, Any]:
    r = await cliente.get(f"{PAINEL}/{nome}", headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()


async def test_exige_autenticacao(cliente: httpx.AsyncClient) -> None:
    for nome in ("atividades-hoje", "financeiro", "importancias"):
        r = await cliente.get(f"{PAINEL}/{nome}")
        assert r.status_code == HTTPStatus.UNAUTHORIZED


# ---------------------------------------------------------------- financeiro


async def test_financeiro_vazio_mostra_zeros(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    p = await bloco(cliente, usuario, "financeiro")
    assert p["hoje"] == "2026-10-13"
    assert p["mes_referencia"] == "2026-10"
    assert p["mes"]["receitas"] == "0.00"
    assert p["mes"]["saldo"] == "0.00"
    assert p["dia"] == {
        "receitas": "0.00",
        "despesas": "0.00",
        "saldo": "0.00",
    }
    assert p["movimentacoes_recentes"] == []
    assert p["mes"]["comparacao_despesas"]["tendencia"] == "SEM_MOVIMENTACAO"


async def test_saldo_do_mes_4_3_1_igual_ao_financeiro(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await receita(
        cliente, usuario, valor="2450.75", data_movimentacao="2026-10-05"
    )
    await despesa(
        cliente, usuario, valor="1230.40", data_movimentacao="2026-10-06"
    )
    p = await bloco(cliente, usuario, "financeiro")
    assert p["mes"]["receitas"] == "2450.75"
    assert p["mes"]["despesas"] == "1230.40"
    assert p["mes"]["saldo"] == "1220.35"
    resumo = await cliente.get(
        f"{BASE}/resumo", params={"mes": "2026-10"}, headers=usuario.cabecalhos
    )
    assert resumo.json()["saldo"] == p["mes"]["saldo"]
    assert (
        resumo.json()["comparacao"]["despesas"]
        == p["mes"]["comparacao_despesas"]
    )
    # Consultar outro mês no Financeiro não altera o painel.
    await cliente.get(
        f"{BASE}/resumo", params={"mes": "2026-09"}, headers=usuario.cabecalhos
    )
    assert (await bloco(cliente, usuario, "financeiro"))["mes"][
        "saldo"
    ] == "1220.35"


async def test_resumo_do_dia_4_3_2_ignora_ontem(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await receita(cliente, usuario, valor="100.00")
    await despesa(cliente, usuario, valor="30.00")
    await despesa(
        cliente, usuario, valor="999.00", data_movimentacao="2026-10-12"
    )
    p = await bloco(cliente, usuario, "financeiro")
    assert p["dia"] == {
        "receitas": "100.00",
        "despesas": "30.00",
        "saldo": "70.00",
    }
    assert p["mes"]["despesas"] == "1029.00"


async def test_recentes_ate_cinco_do_mes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    for dia in range(1, 8):
        await receita(
            cliente,
            usuario,
            nome=f"Venda dia {dia}",
            data_movimentacao=f"2026-10-{dia:02d}",
        )
    await receita(
        cliente, usuario, nome="Mês passado", data_movimentacao="2026-09-30"
    )
    nomes = [
        m["nome"]
        for m in (await bloco(cliente, usuario, "financeiro"))[
            "movimentacoes_recentes"
        ]
    ]
    assert nomes == [f"Venda dia {d}" for d in (7, 6, 5, 4, 3)]


async def test_exclusao_retira_dos_totais(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await receita(cliente, usuario, valor="100.00")
    resposta = await cliente.delete(
        f"{BASE}/movimentacoes/{r['id']}", headers=usuario.cabecalhos
    )
    assert resposta.status_code == HTTPStatus.NO_CONTENT
    p = await bloco(cliente, usuario, "financeiro")
    assert p["mes"]["receitas"] == "0.00"
    assert p["movimentacoes_recentes"] == []


# --------------------------------------------------------------- atividades


async def test_atividades_vazio_e_dia_da_semana(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    p = await bloco(cliente, usuario, "atividades-hoje")
    assert p["hoje"] == "2026-10-13"
    assert p["dia_semana"] == "TERCA"
    assert (p["total"], p["concluidas"], p["previa"]) == (0, 0, [])
    assert p["pendencias_anteriores"] == {
        "quantidade": 0,
        "data_mais_antiga": None,
    }


async def test_totais_consideram_todas_4_3_3(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    ids = []
    for i in range(5):
        a = await criar_atividade(
            cliente,
            usuario,
            nome=f"Atividade {i}",
            horario_inicial=f"{8 + i:02d}:00",
            horario_final=f"{8 + i:02d}:30",
        )
        ids.append(a["id"])
    for i in (0, 1):
        await situacao_atividade(cliente, usuario, ids[i], "CONCLUIDA")
    p = await bloco(cliente, usuario, "atividades-hoje")
    assert (p["total"], p["concluidas"]) == (5, 2)
    # Pendentes primeiro, por horário; a prévia tem três itens.
    assert [x["nome"] for x in p["previa"]] == [
        "Atividade 2",
        "Atividade 3",
        "Atividade 4",
    ]
    await situacao_atividade(cliente, usuario, ids[2], "CONCLUIDA")
    p = await bloco(cliente, usuario, "atividades-hoje")
    assert p["concluidas"] == 3
    assert [x["nome"] for x in p["previa"]] == [
        "Atividade 3",
        "Atividade 4",
        "Atividade 0",
    ]


async def test_pendencias_anteriores_no_painel(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_atividade(cliente, usuario, data="2026-10-09")
    await criar_atividade(
        cliente, usuario, data="2026-10-11", nome="Outra tarefa"
    )
    p = await bloco(cliente, usuario, "atividades-hoje")
    assert p["pendencias_anteriores"] == {
        "quantidade": 2,
        "data_mais_antiga": "2026-10-09",
    }
    assert p["total"] == 0


async def test_atividade_recorrente_aparece_hoje(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_atividade(
        cliente,
        usuario,
        data="2026-10-06",
        repeticao={"periodicidade": "SEMANAL", "termino": "SEM_DATA_FINAL"},
    )
    p = await bloco(cliente, usuario, "atividades-hoje")
    assert p["total"] == 1  # 13/10 é a 2ª ocorrência semanal
    assert p["pendencias_anteriores"]["quantidade"] == 1  # 06/10


# --------------------------------------------------------------- importâncias


async def test_importancias_vazio(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    p = await bloco(cliente, usuario, "importancias")
    assert p == {
        "hoje": "2026-10-13",
        "mes_referencia": "2026-10",
        "pendentes_mes": 0,
        "proximas": [],
        "atrasadas_quantidade": 0,
    }


async def test_outro_mes_e_atrasos_4_3_5(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_importancia(
        cliente, usuario, nome="Atrasada antiga", data_compromisso="2026-08-10"
    )
    await criar_importancia(
        cliente, usuario, nome="Atrasada do mês", data_compromisso="2026-10-02"
    )
    p = await bloco(cliente, usuario, "importancias")
    # Prévia vazia não esconde os atrasos; o mês conta as do próprio mês.
    assert p["proximas"] == []
    assert p["atrasadas_quantidade"] == 2
    assert p["pendentes_mes"] == 1
    await criar_importancia(
        cliente, usuario, nome="Mês que vem", data_compromisso="2026-11-05"
    )
    p = await bloco(cliente, usuario, "importancias")
    assert [i["nome"] for i in p["proximas"]] == ["Mês que vem"]
    assert p["pendentes_mes"] == 1  # não conta o mês seguinte
    assert p["atrasadas_quantidade"] == 2


async def test_proximas_ordenadas_com_horario_e_limite_tres(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_importancia(
        cliente, usuario, nome="Sem horario", data_compromisso="2026-10-14"
    )
    await criar_importancia(
        cliente,
        usuario,
        nome="Com horario",
        data_compromisso="2026-10-14",
        horario="18:00",
    )
    await criar_importancia(
        cliente, usuario, nome="Hoje mesmo", data_compromisso="2026-10-13"
    )
    await criar_importancia(
        cliente, usuario, nome="Mais adiante", data_compromisso="2026-10-30"
    )
    p = await bloco(cliente, usuario, "importancias")
    assert [i["nome"] for i in p["proximas"]] == [
        "Hoje mesmo",
        "Com horario",
        "Sem horario",
    ]
    assert p["proximas"][0]["prazo"] == "HOJE"
    assert p["pendentes_mes"] == 4


async def test_concluida_sai_do_painel(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar_importancia(cliente, usuario, nome="Para concluir")
    await situacao_importancia(cliente, usuario, a["id"], "CONCLUIDA")
    p = await bloco(cliente, usuario, "importancias")
    assert (p["pendentes_mes"], p["proximas"]) == (0, [])


async def test_pagamento_4_3_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_importancia(
        cliente,
        usuario,
        nome="Conta de internet",
        possui_despesa=True,
        valor_previsto="99.90",
    )
    fin = await bloco(cliente, usuario, "financeiro")
    assert fin["mes"]["despesas"] == "0.00"  # previsão não altera o saldo
    assert (await bloco(cliente, usuario, "importancias"))[
        "pendentes_mes"
    ] == 1
    r = await pagar(cliente, usuario, conta["id"], valor="105.00")
    assert r.status_code == HTTPStatus.CREATED
    fin = await bloco(cliente, usuario, "financeiro")
    assert fin["mes"]["despesas"] == "105.00"
    assert fin["dia"]["despesas"] == "105.00"
    imp = await bloco(cliente, usuario, "importancias")
    assert (imp["pendentes_mes"], imp["proximas"]) == (0, [])


async def test_serie_sem_fim_entrega_tres_proximas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_importancia(
        cliente,
        usuario,
        nome="Aluguel mensal",
        data_compromisso="2026-10-05",
        repeticao={"periodicidade": "MENSAL"},
    )
    p = await bloco(cliente, usuario, "importancias")
    assert [i["data_compromisso"] for i in p["proximas"]] == [
        "2026-11-05",
        "2026-12-05",
        "2027-01-05",
    ]
    assert p["atrasadas_quantidade"] == 1  # 05/10 ainda pendente
    assert p["pendentes_mes"] == 1


async def test_serie_anual_busca_alem_do_horizonte(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_importancia(
        cliente,
        usuario,
        nome="Licenciamento",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "ANUAL"},
    )
    p = await bloco(cliente, usuario, "importancias")
    assert [i["data_compromisso"] for i in p["proximas"]] == [
        "2026-10-20",
        "2027-10-20",
        "2028-10-20",
    ]
