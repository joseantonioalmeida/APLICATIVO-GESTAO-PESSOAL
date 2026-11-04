from datetime import date
from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste
from ..apoio.identidade import codigo_de_erro
from .util import (
    URL,
    criar,
    lembretes_no_banco,
    listar,
    nomes,
    obter,
    situacao,
)

LEMBRETE = {"antecedencia_dias": 1, "horario": "09:00"}


async def todas(cliente, usuario, **params) -> list[dict]:
    itens: list[dict] = []
    cursor = None
    while True:
        p = {"limite": 50, **params}
        if cursor:
            p["cursor"] = cursor
        pagina = await listar(cliente, usuario, **p)
        itens += pagina["itens"]
        cursor = pagina["proximo_cursor"]
        if cursor is None:
            return itens


async def do_mes(cliente, usuario, mes: str) -> list[dict]:
    return (
        await listar(cliente, usuario, filtro="ESTE_MES", mes=mes, limite=50)
    )["itens"]


async def test_mensal_dia_31_e_data_final_inclusiva(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """8.6.4: 31/01, último dia de fevereiro e 31/03 (data final inclusiva)."""
    await criar(
        cliente,
        usuario,
        nome="Condomínio",
        data_compromisso="2027-01-31",
        repeticao={
            "periodicidade": "MENSAL",
            "termino": "ATE_DATA",
            "data_final": "2027-03-31",
        },
    )
    assert [
        i["data_compromisso"]
        for i in await do_mes(cliente, usuario, "2027-01")
    ] == ["2027-01-31"]
    assert [
        i["data_compromisso"]
        for i in await do_mes(cliente, usuario, "2027-02")
    ] == ["2027-02-28"]
    assert [
        i["data_compromisso"]
        for i in await do_mes(cliente, usuario, "2027-03")
    ] == ["2027-03-31"]
    assert await do_mes(cliente, usuario, "2027-04") == []


async def test_anual_29_de_fevereiro(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Aniversário bissexto",
        data_compromisso="2028-02-29",
        repeticao={"periodicidade": "ANUAL"},
    )
    assert [
        i["data_compromisso"]
        for i in await do_mes(cliente, usuario, "2029-02")
    ] == ["2029-02-28"]
    assert [
        i["data_compromisso"]
        for i in await do_mes(cliente, usuario, "2032-02")
    ] == ["2032-02-29"]


async def test_horizonte_de_12_meses_em_todos_e_proximos(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Assinatura semanal",
        data_compromisso="2026-10-14",
        repeticao={"periodicidade": "SEMANAL"},
    )
    avulsa = await criar(
        cliente, usuario, nome="Avulsa distante", data_compromisso="2030-05-01"
    )
    resumo = await listar(cliente, usuario, filtro="TODOS", limite=1)
    assert resumo["horizonte_proximas"] == "2027-10-31"
    todos = await todas(cliente, usuario, filtro="TODOS")
    datas = [
        i["data_compromisso"]
        for i in todos
        if i["nome"] == "Assinatura semanal"
    ]
    assert datas[0] == "2026-10-14"
    assert datas[-1] == "2027-10-27"  # última quarta antes do horizonte
    assert len(datas) == len(set(datas)) == 55
    # Registros avulsos não têm horizonte; contagem = resultado completo.
    assert avulsa["id"] in [i["id"] for i in todos]
    assert resumo["grupos"]["proximas"] == len(todos) == 56
    proximos = await todas(cliente, usuario, filtro="PROXIMOS")
    assert len(proximos) == 56
    assert (await listar(cliente, usuario, filtro="CONCLUIDOS"))["total"] == 0


async def test_totais_dos_grupos_cobrem_o_resultado_completo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Mensal",
        data_compromisso="2026-08-13",
        repeticao={"periodicidade": "MENSAL"},
    )
    r = await listar(cliente, usuario, limite=5)
    # Ago, set (atrasadas), 13/10 (hoje), nov/2026 a out/2027 (12 próximas).
    assert r["grupos"] == {
        "atrasadas": 2,
        "hoje": 1,
        "proximas": 12,
        "concluidas": 0,
    }
    assert r["total"] == 15
    assert len(r["itens"]) == 5
    assert r["proximo_cursor"] is not None


async def test_cada_ocorrencia_tem_situacao_e_lembrete_proprios(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Aluguel",
        data_compromisso="2026-10-20",
        possui_despesa=True,
        valor_previsto="600",
        repeticao={"periodicidade": "MENSAL"},
        lembrete=LEMBRETE,
    )
    out = (await do_mes(cliente, usuario, "2026-10"))[0]
    nov = (await do_mes(cliente, usuario, "2026-11"))[0]
    assert out["recorrente"] is True
    assert out["valor_previsto"] == "600.00"
    det_nov = await obter(cliente, usuario, nov["id"])
    assert det_nov["numero_ocorrencia"] == 2
    assert det_nov["serie"]["periodicidade"] == "MENSAL"
    assert det_nov["lembrete"]["agendado_para"].startswith(
        "2026-11-19T12:00:00"
    )
    assert lembretes_no_banco(banco_migrado, nov["id"])[0][:2] == (
        "PENDENTE",
        1,
    )
    # Concluir uma ocorrência com despesa exige pagamento.
    r = await situacao(cliente, usuario, out["id"], "CONCLUIDA")
    assert codigo_de_erro(r) == "CONCLUSAO_EXIGE_PAGAMENTO"


async def test_ocorrencia_materializada_no_passado_nasce_sem_lembrete_ativo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    i = await criar(
        cliente,
        usuario,
        nome="Série com lembrete",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "SEMANAL"},
        lembrete=LEMBRETE,
    )
    # Hoje é 13/10: todas as ocorrências são futuras.
    segunda = [
        x
        for x in await do_mes(cliente, usuario, "2026-10")
        if x["data_compromisso"] == "2026-10-27"
    ][0]
    assert lembretes_no_banco(banco_migrado, segunda["id"])[0][0] == "PENDENTE"
    assert i["id"]


async def test_edicao_somente_esta_isola_e_repeticao_exige_alcance(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Streaming",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "MENSAL"},
    )
    nov = (await do_mes(cliente, usuario, "2026-11"))[0]
    r = await cliente.patch(
        f"{URL}/{nov['id']}",
        json={"nome": "Streaming promocional"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK
    assert [i["nome"] for i in await do_mes(cliente, usuario, "2026-10")] == [
        "Streaming"
    ]
    assert [i["nome"] for i in await do_mes(cliente, usuario, "2026-12")] == [
        "Streaming"
    ]
    rep = await cliente.patch(
        f"{URL}/{nov['id']}",
        json={"repeticao": {"periodicidade": "SEMANAL"}},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(rep) == "REPETICAO_EXIGE_ALCANCE_SERIE"


async def test_edicao_esta_e_proximas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Streaming",
        data_compromisso="2026-10-20",
        possui_despesa=True,
        valor_previsto="39.90",
        repeticao={"periodicidade": "MENSAL"},
        lembrete=LEMBRETE,
    )
    out = (await do_mes(cliente, usuario, "2026-10"))[0]
    dez = (await do_mes(cliente, usuario, "2026-12"))[0]
    r = await cliente.patch(
        f"{URL}/{dez['id']}",
        json={
            "nome": "Streaming premium",
            "valor_previsto": "59.90",
            "data_compromisso": "2026-12-22",
            "alcance": "ESTA_E_PROXIMAS",
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    assert r.json()["data_compromisso"] == "2026-12-22"
    assert r.json()["valor_previsto"] == "59.90"
    # Anteriores preservadas.
    assert (await obter(cliente, usuario, out["id"]))["nome"] == "Streaming"
    assert (await obter(cliente, usuario, out["id"]))[
        "valor_previsto"
    ] == "39.90"
    nov = (await do_mes(cliente, usuario, "2026-11"))[0]
    assert nov["nome"] == "Streaming"
    # Próximas seguem a nova referência (dia 22) e os novos padrões.
    jan = (await do_mes(cliente, usuario, "2027-01"))[0]
    assert (jan["nome"], jan["data_compromisso"], jan["valor_previsto"]) == (
        "Streaming premium",
        "2027-01-22",
        "59.90",
    )
    # O lembrete da linha alterada acompanhou a data (versão 2).
    assert lembretes_no_banco(banco_migrado, dez["id"])[0][:2] == (
        "PENDENTE",
        2,
    )


async def test_edicao_de_serie_com_data_final_invalida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Streaming",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "MENSAL"},
    )
    nov = (await do_mes(cliente, usuario, "2026-11"))[0]
    r = await cliente.patch(
        f"{URL}/{nov['id']}",
        json={
            "repeticao": {
                "periodicidade": "MENSAL",
                "termino": "ATE_DATA",
                "data_final": "2026-11-01",
            },
            "alcance": "ESTA_E_PROXIMAS",
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json()["campos"][0]["campo"] == "repeticao.data_final"


async def test_exclusao_somente_esta_e_esta_e_proximas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Streaming",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "MENSAL"},
        lembrete=LEMBRETE,
    )
    nov = (await do_mes(cliente, usuario, "2026-11"))[0]
    dez = (await do_mes(cliente, usuario, "2026-12"))[0]
    jan = (await do_mes(cliente, usuario, "2027-01"))[0]
    r = await cliente.delete(f"{URL}/{nov['id']}", headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.NO_CONTENT
    for _ in range(2):  # não reaparece ao recarregar
        assert await do_mes(cliente, usuario, "2026-11") == []
    assert lembretes_no_banco(banco_migrado, nov["id"])[0][0] == "CANCELADO"
    r2 = await cliente.delete(
        f"{URL}/{dez['id']}",
        params={"alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert r2.status_code == HTTPStatus.NO_CONTENT
    assert len(await do_mes(cliente, usuario, "2026-10")) == 1
    assert await do_mes(cliente, usuario, "2026-12") == []
    assert await do_mes(cliente, usuario, "2027-01") == []
    assert lembretes_no_banco(banco_migrado, jan["id"])[0][0] == "CANCELADO"
    assert (await listar(cliente, usuario, filtro="PROXIMOS"))["total"] == 1


async def test_avulsa_vira_serie_ao_editar(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    i = await criar(
        cliente, usuario, nome="Plano de saúde", data_compromisso="2026-10-20"
    )
    r = await cliente.patch(
        f"{URL}/{i['id']}",
        json={
            "repeticao": {
                "periodicidade": "MENSAL",
                "termino": "ATE_DATA",
                "data_final": "2026-12-20",
            }
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    assert r.json()["recorrente"] is True
    assert r.json()["numero_ocorrencia"] == 1
    assert r.json()["serie"]["data_final"] == "2026-12-20"
    assert len(await do_mes(cliente, usuario, "2026-11")) == 1
    assert len(await do_mes(cliente, usuario, "2026-12")) == 1
    assert await do_mes(cliente, usuario, "2027-01") == []


async def test_uma_so_ocorrencia_por_posicao_apos_varias_consultas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Mensal",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "MENSAL"},
    )
    for _ in range(3):
        assert await nomes(
            cliente, usuario, filtro="ESTE_MES", mes="2026-12"
        ) == ["Mensal"]
    assert date.fromisoformat("2026-12-20")
