from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, criar_usuario
from ..apoio.identidade import codigo_de_erro
from ..financeiro.util import categoria as categoria_financeira
from ..financeiro.util import receita
from ..importancias.util import criar, lembretes_no_banco, listar
from .util import (
    BASE,
    URL_IMP,
    criar_conta,
    despesa_avulsa,
    obter_importancia,
    pagar,
    resumo,
)

LEMBRETE = {"antecedencia_dias": 1, "horario": "09:00"}


def totais(resumo_mes: dict) -> tuple:
    """Valores que não podem mudar ao vincular uma despesa existente."""
    return (
        resumo_mes["receitas"],
        resumo_mes["despesas"],
        resumo_mes["saldo"],
        resumo_mes["grafico_diario"],
        resumo_mes["categorias_despesa"],
        resumo_mes["comparacao"],
    )


async def vincular(cliente, usuario, importancia_id, movimentacao_id):
    return await cliente.put(
        f"{URL_IMP}/{importancia_id}/pagamento",
        json={"movimentacao_id": movimentacao_id},
        headers=usuario.cabecalhos,
    )


async def test_vincular_despesa_existente_11_6_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    conta = await criar_conta(cliente, usuario, lembrete=LEMBRETE)
    mov = await despesa_avulsa(
        cliente,
        usuario,
        valor="105",
        nome="Internet paga no débito",
        data_movimentacao="2026-10-10",
    )
    antes = totais(await resumo(cliente, usuario))
    r = await vincular(cliente, usuario, conta["id"], mov["id"])
    assert r.status_code == HTTPStatus.OK, r.text
    assert r.json()["pago"] is True
    assert r.json()["situacao"] == "CONCLUIDA"
    assert r.json()["pagamento"]["valor"] == "105.00"
    assert r.json()["pagamento"]["data_movimentacao"] == "2026-10-10"
    # Totais, valor, categoria e data da despesa não mudam; sem duplicar.
    assert totais(await resumo(cliente, usuario)) == antes
    det = await cliente.get(
        f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
    )
    assert det.json()["valor"] == "105.00"
    assert det.json()["data_movimentacao"] == "2026-10-10"
    assert det.json()["importancia"]["id"] == conta["id"]
    assert lembretes_no_banco(banco_migrado, conta["id"])[0][0] == "CANCELADO"
    # Nova tentativa da mesma operação: mesmo resultado.
    again = await vincular(cliente, usuario, conta["id"], mov["id"])
    assert again.status_code == HTTPStatus.OK
    assert again.json()["pagamento"]["movimentacao_id"] == mov["id"]
    assert totais(await resumo(cliente, usuario)) == antes


async def test_conflitos_ao_vincular(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar_conta(cliente, usuario, nome="Conta A")
    b = await criar_conta(cliente, usuario, nome="Conta B")
    m1 = await despesa_avulsa(cliente, usuario, nome="Despesa 1")
    m2 = await despesa_avulsa(cliente, usuario, nome="Despesa 2")
    assert (
        await vincular(cliente, usuario, a["id"], m1["id"])
    ).status_code == HTTPStatus.OK
    # Despesa já vinculada a outra importância.
    r = await vincular(cliente, usuario, b["id"], m1["id"])
    assert r.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(r) == "DESPESA_JA_VINCULADA"
    # Importância já paga por outra despesa.
    r2 = await vincular(cliente, usuario, a["id"], m2["id"])
    assert r2.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(r2) == "IMPORTANCIA_JA_PAGA"
    assert r2.json()["detalhes"] == {"movimentacao_id": m1["id"]}
    # Sem despesa prevista.
    sem = await criar(cliente, usuario, nome="Sem despesa")
    r3 = await vincular(cliente, usuario, sem["id"], m2["id"])
    assert codigo_de_erro(r3) == "IMPORTANCIA_SEM_DESPESA"
    # Receita não pode quitar importância.
    rec = await receita(cliente, usuario)
    r4 = await vincular(cliente, usuario, b["id"], rec["id"])
    assert r4.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r4.json()["campos"][0]["codigo"] == "MOVIMENTACAO_NAO_E_DESPESA"
    # 404: inexistente e de outro usuário.
    inexistente = "01900000-0000-7000-8000-000000000000"
    assert (
        await vincular(cliente, usuario, inexistente, m2["id"])
    ).status_code == HTTPStatus.NOT_FOUND
    assert (
        await vincular(cliente, usuario, b["id"], inexistente)
    ).status_code == HTTPStatus.NOT_FOUND
    outro = await criar_usuario(cliente)
    assert (
        await vincular(cliente, outro, b["id"], m2["id"])
    ).status_code == HTTPStatus.NOT_FOUND
    # Nada mudou em B.
    assert (await obter_importancia(cliente, usuario, b["id"]))[
        "pago"
    ] is False


async def test_nao_vincula_despesa_excluida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    mov = await despesa_avulsa(cliente, usuario)
    await cliente.delete(
        f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
    )
    assert (
        await vincular(cliente, usuario, conta["id"], mov["id"])
    ).status_code == HTTPStatus.NOT_FOUND


async def test_trocar_o_vinculo_exige_confirmacao_11_5_6(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    a = await criar_conta(cliente, usuario, nome="Conta A", lembrete=LEMBRETE)
    b = await criar_conta(
        cliente, usuario, nome="Conta B", data_compromisso="2026-10-25"
    )
    mov = (await pagar(cliente, usuario, a["id"])).json()
    url = f"{BASE}/movimentacoes/{mov['id']}"
    sem = await cliente.patch(
        url, json={"importancia_id": b["id"]}, headers=usuario.cabecalhos
    )
    assert sem.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(sem) == "CONFIRMACAO_VINCULO_NECESSARIA"
    assert (await obter_importancia(cliente, usuario, a["id"]))["pago"] is True
    ok = await cliente.patch(
        url,
        json={
            "importancia_id": b["id"],
            "confirmar_alteracao_vinculo": True,
            "valor": "110",
        },
        headers=usuario.cabecalhos,
    )
    assert ok.status_code == HTTPStatus.OK, ok.text
    assert ok.json()["importancia"]["id"] == b["id"]
    assert ok.json()["valor"] == "110.00"
    # A anterior volta a pendente (lembrete reativado); a nova fica paga.
    assert (await obter_importancia(cliente, usuario, a["id"]))[
        "situacao"
    ] == "PENDENTE"
    assert lembretes_no_banco(banco_migrado, a["id"])[0][0] == "PENDENTE"
    nova = await obter_importancia(cliente, usuario, b["id"])
    assert nova["pago"] is True
    assert nova["pagamento"]["valor"] == "110.00"
    # Um único lançamento nos totais.
    assert (await resumo(cliente, usuario))["despesas"] == "110.00"


async def test_remover_o_vinculo_mantem_a_despesa_nos_totais(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    mov = (await pagar(cliente, usuario, conta["id"])).json()
    url = f"{BASE}/movimentacoes/{mov['id']}"
    sem = await cliente.patch(
        url, json={"importancia_id": None}, headers=usuario.cabecalhos
    )
    assert codigo_de_erro(sem) == "CONFIRMACAO_VINCULO_NECESSARIA"
    ok = await cliente.patch(
        url,
        json={"importancia_id": None, "confirmar_alteracao_vinculo": True},
        headers=usuario.cabecalhos,
    )
    assert ok.status_code == HTTPStatus.OK
    assert ok.json()["importancia"] is None
    assert (await resumo(cliente, usuario))["despesas"] == "105.00"
    assert (await obter_importancia(cliente, usuario, conta["id"]))[
        "situacao"
    ] == "PENDENTE"


async def test_vincular_pelo_patch_uma_despesa_sem_vinculo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    mov = await despesa_avulsa(cliente, usuario)
    r = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"importancia_id": conta["id"]},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    assert (await obter_importancia(cliente, usuario, conta["id"]))[
        "pago"
    ] is True
    # Mesmo vínculo de novo: sem erro.
    again = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"importancia_id": conta["id"]},
        headers=usuario.cabecalhos,
    )
    assert again.status_code == HTTPStatus.OK


async def test_patch_de_vinculo_e_atomico_e_so_para_despesas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar_conta(cliente, usuario, nome="Conta A")
    b = await criar_conta(cliente, usuario, nome="Conta B")
    await pagar(cliente, usuario, b["id"])
    mov = await despesa_avulsa(cliente, usuario, valor="50")
    # B já está paga: o PATCH inteiro falha, inclusive o campo `valor`.
    r = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"importancia_id": b["id"], "valor": "75"},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(r) == "IMPORTANCIA_JA_PAGA"
    det = await cliente.get(
        f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
    )
    assert det.json()["valor"] == "50.00"
    assert det.json()["importancia"] is None
    rec = await receita(cliente, usuario)
    r2 = await cliente.patch(
        f"{BASE}/movimentacoes/{rec['id']}",
        json={"importancia_id": a["id"]},
        headers=usuario.cabecalhos,
    )
    assert r2.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r2.json()["campos"][0]["codigo"] == "SOMENTE_DESPESA"
    inexistente = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"importancia_id": "01900000-0000-7000-8000-000000000000"},
        headers=usuario.cabecalhos,
    )
    assert inexistente.status_code == HTTPStatus.NOT_FOUND


async def test_importancias_disponiveis_para_pagamento(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    paga = await criar_conta(
        cliente, usuario, nome="Já paga", data_compromisso="2026-10-14"
    )
    await pagar(cliente, usuario, paga["id"])
    await criar(
        cliente, usuario, nome="Sem despesa", data_compromisso="2026-10-15"
    )
    excluida = await criar_conta(
        cliente, usuario, nome="Excluída", data_compromisso="2026-10-16"
    )
    await cliente.delete(
        f"{URL_IMP}/{excluida['id']}", headers=usuario.cabecalhos
    )
    await criar_conta(
        cliente,
        usuario,
        nome="Energia elétrica",
        data_compromisso="2026-10-25",
        valor_previsto="152.34",
    )
    await criar_conta(
        cliente, usuario, nome="Internet fibra", data_compromisso="2026-10-18"
    )
    r = await cliente.get(
        f"{URL_IMP}/disponiveis-pagamento", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.OK
    assert [
        (i["nome"], i["data_compromisso"], i["valor_previsto"])
        for i in r.json()["itens"]
    ] == [
        ("Internet fibra", "2026-10-18", "99.90"),
        ("Energia elétrica", "2026-10-25", "152.34"),
    ]
    busca = await cliente.get(
        f"{URL_IMP}/disponiveis-pagamento",
        params={"busca": "ENERGIA"},
        headers=usuario.cabecalhos,
    )
    assert [i["nome"] for i in busca.json()["itens"]] == ["Energia elétrica"]
    p1 = await cliente.get(
        f"{URL_IMP}/disponiveis-pagamento",
        params={"limite": 1},
        headers=usuario.cabecalhos,
    )
    p2 = await cliente.get(
        f"{URL_IMP}/disponiveis-pagamento",
        params={"limite": 1, "cursor": p1.json()["proximo_cursor"]},
        headers=usuario.cabecalhos,
    )
    assert [i["nome"] for i in p1.json()["itens"] + p2.json()["itens"]] == [
        "Internet fibra",
        "Energia elétrica",
    ]
    assert p2.json()["proximo_cursor"] is None
    ruim = await cliente.get(
        f"{URL_IMP}/disponiveis-pagamento",
        params={"cursor": "x"},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(ruim) == "CURSOR_INVALIDO"
    assert (
        await cliente.get(f"{URL_IMP}/disponiveis-pagamento")
    ).status_code == HTTPStatus.UNAUTHORIZED


async def test_despesas_disponiveis_para_vinculo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    vinculada = (await pagar(cliente, usuario, conta["id"])).json()
    antiga = await despesa_avulsa(
        cliente, usuario, nome="Mercado antigo", data_movimentacao="2026-10-01"
    )
    recente = await despesa_avulsa(
        cliente,
        usuario,
        nome="Mercado recente",
        data_movimentacao="2026-10-12",
    )
    await receita(cliente, usuario)
    excluida = await despesa_avulsa(cliente, usuario, nome="Excluída")
    await cliente.delete(
        f"{BASE}/movimentacoes/{excluida['id']}", headers=usuario.cabecalhos
    )
    r = await cliente.get(
        f"{BASE}/despesas/disponiveis-vinculo", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.OK
    assert [i["id"] for i in r.json()["itens"]] == [
        recente["id"],
        antiga["id"],
    ]
    assert vinculada["id"] not in [i["id"] for i in r.json()["itens"]]
    assert set(r.json()["itens"][0]) == {
        "id",
        "nome",
        "data_movimentacao",
        "valor",
    }
    busca = await cliente.get(
        f"{BASE}/despesas/disponiveis-vinculo",
        params={"busca": "antigo"},
        headers=usuario.cabecalhos,
    )
    assert [i["id"] for i in busca.json()["itens"]] == [antiga["id"]]
    p1 = await cliente.get(
        f"{BASE}/despesas/disponiveis-vinculo",
        params={"limite": 1},
        headers=usuario.cabecalhos,
    )
    p2 = await cliente.get(
        f"{BASE}/despesas/disponiveis-vinculo",
        params={"limite": 1, "cursor": p1.json()["proximo_cursor"]},
        headers=usuario.cabecalhos,
    )
    assert [i["id"] for i in p1.json()["itens"] + p2.json()["itens"]] == [
        recente["id"],
        antiga["id"],
    ]


async def test_resumo_nunca_conta_o_previsto_nem_duas_vezes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario, valor_previsto="500")
    mov = await despesa_avulsa(cliente, usuario, valor="480.50")
    assert (await resumo(cliente, usuario))["despesas"] == "480.50"
    await vincular(cliente, usuario, conta["id"], mov["id"])
    assert (await resumo(cliente, usuario))["despesas"] == "480.50"
    todas = (await listar(cliente, usuario, filtro="CONCLUIDOS"))["itens"]
    assert [i["pagamento"]["valor"] for i in todas] == ["480.50"]
    cat = await categoria_financeira(cliente, usuario, "DESPESA", "Contas")
    assert cat
