from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste
from ..apoio.esquema import consultar
from ..apoio.identidade import codigo_de_erro
from .util import URL, criar, listar, nomes_do_dia

SEMANAL = {
    "periodicidade": "SEMANAL",
    "termino": "ATE_DATA",
    "data_final": "2026-10-22",
}


async def ids_do_dia(cliente, usuario, data) -> list[str]:
    return [
        i["id"] for i in (await listar(cliente, usuario, data=data))["itens"]
    ]


async def criar_semanal(cliente, usuario) -> dict:

    return await criar(
        cliente,
        usuario,
        nome="Treino na academia",
        data="2026-10-08",
        horario_inicial="17:00",
        horario_final="18:30",
        repeticao=SEMANAL,
    )


async def test_semanal_gera_08_15_e_22(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """6.5.5: concluir a primeira não modifica as demais."""
    primeira = await criar_semanal(cliente, usuario)
    assert primeira["serie"]["periodicidade"] == "SEMANAL"
    assert primeira["numero_ocorrencia"] == 1
    assert primeira["recorrente"] is True
    for dia in ("2026-10-08", "2026-10-15", "2026-10-22"):
        assert await nomes_do_dia(cliente, usuario, dia) == [
            "Treino na academia"
        ]
    for dia in ("2026-10-09", "2026-10-29", "2026-10-01"):
        assert await nomes_do_dia(cliente, usuario, dia) == []
    resposta = await cliente.put(
        f"{URL}/{primeira['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    assert resposta.status_code == HTTPStatus.OK
    for dia in ("2026-10-15", "2026-10-22"):
        item = (await listar(cliente, usuario, data=dia))["itens"][0]
        assert item["situacao"] == "PENDENTE"


async def test_mensal_dia_31(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:

    await criar(
        cliente,
        usuario,
        nome="Pagar condomínio",
        data="2027-01-31",
        repeticao={"periodicidade": "MENSAL"},
    )
    assert await nomes_do_dia(cliente, usuario, "2027-02-28") == [
        "Pagar condomínio"
    ]
    assert await nomes_do_dia(cliente, usuario, "2027-02-27") == []
    assert await nomes_do_dia(cliente, usuario, "2027-03-31") == [
        "Pagar condomínio"
    ]
    assert await nomes_do_dia(cliente, usuario, "2027-04-30") == [
        "Pagar condomínio"
    ]


async def test_diaria_sem_data_final_e_materializacao_unica(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:

    await criar(
        cliente,
        usuario,
        nome="Beber água",
        data="2026-10-13",
        repeticao={"periodicidade": "DIARIA"},
    )
    for _ in range(3):
        assert await nomes_do_dia(cliente, usuario, "2026-12-25") == [
            "Beber água"
        ]
    linhas = consultar(
        banco_migrado, "SELECT numero_ocorrencia FROM atividade ORDER BY 1"
    )
    assert [linha[0] for linha in linhas] == [1, *range(74, 75)] or len(
        linhas
    ) == 2


async def test_exclusao_somente_esta_nao_reaparece(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    primeira = await criar_semanal(cliente, usuario)
    segunda_id = (await listar(cliente, usuario, data="2026-10-15"))["itens"][
        0
    ]["id"]
    r = await cliente.delete(f"{URL}/{segunda_id}", headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.NO_CONTENT
    for _ in range(2):  # recarregar não recria a lápide
        assert await nomes_do_dia(cliente, usuario, "2026-10-15") == []
    assert await nomes_do_dia(cliente, usuario, "2026-10-08") == [
        "Treino na academia"
    ]
    assert await nomes_do_dia(cliente, usuario, "2026-10-22") == [
        "Treino na academia"
    ]
    assert primeira["id"]


async def test_exclusao_esta_e_proximas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    primeira = await criar_semanal(cliente, usuario)
    await cliente.put(
        f"{URL}/{primeira['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    segunda_id = (await listar(cliente, usuario, data="2026-10-15"))["itens"][
        0
    ]["id"]
    terceira_id = (await listar(cliente, usuario, data="2026-10-22"))["itens"][
        0
    ]["id"]
    r = await cliente.delete(
        f"{URL}/{segunda_id}",
        params={"alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    assert await nomes_do_dia(cliente, usuario, "2026-10-08") == [
        "Treino na academia"
    ]
    assert await nomes_do_dia(cliente, usuario, "2026-10-15") == []
    assert await nomes_do_dia(cliente, usuario, "2026-10-22") == []
    detalhe = await cliente.get(
        f"{URL}/{terceira_id}", headers=usuario.cabecalhos
    )
    assert detalhe.status_code == HTTPStatus.NOT_FOUND
    # A série não gera mais nada depois da interrupção.
    assert await nomes_do_dia(cliente, usuario, "2026-10-29") == []
    primeira_depois = await cliente.get(
        f"{URL}/{primeira['id']}", headers=usuario.cabecalhos
    )
    assert primeira_depois.json()["situacao"] == "CONCLUIDA"
    assert primeira_depois.json()["serie"]["numero_final"] == 1


async def test_exclusao_da_primeira_com_proximas_zera_a_serie(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    primeira = await criar_semanal(cliente, usuario)
    r = await cliente.delete(
        f"{URL}/{primeira['id']}",
        params={"alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    for dia in ("2026-10-08", "2026-10-15", "2026-10-22"):
        assert await nomes_do_dia(cliente, usuario, dia) == []


async def test_exclusao_esta_e_proximas_de_concluida_e_invalida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    primeira = await criar_semanal(cliente, usuario)
    await cliente.put(
        f"{URL}/{primeira['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    r = await cliente.delete(
        f"{URL}/{primeira['id']}",
        params={"alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert codigo_de_erro(r) == "ALCANCE_INVALIDO"
    edicao = await cliente.patch(
        f"{URL}/{primeira['id']}",
        json={"nome": "Nome novo", "alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(edicao) == "ALCANCE_INVALIDO"
    repeticao = await cliente.patch(
        f"{URL}/{primeira['id']}",
        json={"repeticao": {"periodicidade": "DIARIA"}},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(repeticao) == "REPETICAO_EXIGE_ALCANCE_SERIE"


async def test_edicao_somente_esta_nao_mexe_nas_outras(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_semanal(cliente, usuario)
    segunda_id = (await listar(cliente, usuario, data="2026-10-15"))["itens"][
        0
    ]["id"]
    r = await cliente.patch(
        f"{URL}/{segunda_id}",
        json={"nome": "Treino especial", "horario_final": "19:00"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK
    assert await nomes_do_dia(cliente, usuario, "2026-10-15") == [
        "Treino especial"
    ]
    assert await nomes_do_dia(cliente, usuario, "2026-10-22") == [
        "Treino na academia"
    ]
    repeticao = await cliente.patch(
        f"{URL}/{segunda_id}",
        json={"repeticao": {"periodicidade": "DIARIA"}},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(repeticao) == "REPETICAO_EXIGE_ALCANCE_SERIE"


async def test_edicao_esta_e_proximas_preserva_anteriores_e_concluidas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    primeira = await criar_semanal(cliente, usuario)
    segunda = (await listar(cliente, usuario, data="2026-10-15"))["itens"][0]
    terceira = (await listar(cliente, usuario, data="2026-10-22"))["itens"][0]
    await cliente.put(
        f"{URL}/{terceira['id']}/situacao",
        json={"situacao": "CONCLUIDA"},
        headers=usuario.cabecalhos,
    )
    r = await cliente.patch(
        f"{URL}/{segunda['id']}",
        json={
            "nome": "Treino de força",
            "horario_inicial": "06:00",
            "horario_final": "07:00",
            "alcance": "ESTA_E_PROXIMAS",
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    assert r.json()["nome"] == "Treino de força"
    assert r.json()["serie"]["periodicidade"] == "SEMANAL"
    # Anterior intacta; concluída posterior preservada.
    ant = await cliente.get(
        f"{URL}/{primeira['id']}", headers=usuario.cabecalhos
    )
    assert ant.json()["nome"] == "Treino na academia"
    assert ant.json()["horario_inicial"] == "17:00"
    conc = await cliente.get(
        f"{URL}/{terceira['id']}", headers=usuario.cabecalhos
    )
    assert conc.json()["nome"] == "Treino na academia"
    assert conc.json()["situacao"] == "CONCLUIDA"


async def test_edicao_esta_e_proximas_muda_data_e_periodicidade(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:

    await criar(
        cliente,
        usuario,
        nome="Corrida",
        data="2026-10-13",
        repeticao={
            "periodicidade": "DIARIA",
            "termino": "ATE_DATA",
            "data_final": "2026-10-20",
        },
    )
    terceira = (await listar(cliente, usuario, data="2026-10-15"))["itens"][0]
    r = await cliente.patch(
        f"{URL}/{terceira['id']}",
        json={
            "data": "2026-10-16",
            "repeticao": {
                "periodicidade": "SEMANAL",
                "termino": "ATE_DATA",
                "data_final": "2026-10-30",
            },
            "alcance": "ESTA_E_PROXIMAS",
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    assert r.json()["data"] == "2026-10-16"
    assert r.json()["serie"]["periodicidade"] == "SEMANAL"
    # Anteriores seguem diárias (13 e 14); a série semanal parte do dia 16.
    assert await nomes_do_dia(cliente, usuario, "2026-10-13") == ["Corrida"]
    assert await nomes_do_dia(cliente, usuario, "2026-10-14") == ["Corrida"]
    assert await nomes_do_dia(cliente, usuario, "2026-10-15") == []
    assert await nomes_do_dia(cliente, usuario, "2026-10-16") == ["Corrida"]
    assert await nomes_do_dia(cliente, usuario, "2026-10-17") == []
    assert await nomes_do_dia(cliente, usuario, "2026-10-23") == ["Corrida"]
    assert await nomes_do_dia(cliente, usuario, "2026-10-30") == ["Corrida"]
    assert await nomes_do_dia(cliente, usuario, "2026-11-06") == []


async def test_edicao_de_serie_com_data_final_invalida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_semanal(cliente, usuario)
    segunda = (await listar(cliente, usuario, data="2026-10-15"))["itens"][0]
    r = await cliente.patch(
        f"{URL}/{segunda['id']}",
        json={
            "repeticao": {
                "periodicidade": "SEMANAL",
                "termino": "ATE_DATA",
                "data_final": "2026-10-10",
            },
            "alcance": "ESTA_E_PROXIMAS",
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert r.json()["campos"][0]["campo"] == "repeticao.data_final"
    # Nada foi alterado.
    assert await nomes_do_dia(cliente, usuario, "2026-10-22") == [
        "Treino na academia"
    ]


async def test_pendencias_de_serie_antiga(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:

    await criar(
        cliente,
        usuario,
        nome="Diária antiga",
        data="2026-10-10",
        repeticao={"periodicidade": "DIARIA"},
    )
    r = await cliente.get(
        f"{URL}/pendencias-anteriores", headers=usuario.cabecalhos
    )
    # Dias 10, 11 e 12 de outubro, todos pendentes.
    assert r.json() == {"quantidade": 3, "data_mais_antiga": "2026-10-10"}
