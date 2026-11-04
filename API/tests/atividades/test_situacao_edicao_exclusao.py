from datetime import timedelta
from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste
from ..apoio.identidade import codigo_de_erro
from ..apoio.relogio import RelogioFixo
from .util import URL, campo_de_erro, criar, listar


async def situacao(cliente, usuario, id_, valor) -> httpx.Response:
    return await cliente.put(
        f"{URL}/{id_}/situacao",
        json={"situacao": valor},
        headers=usuario.cabecalhos,
    )


async def test_concluir_e_reabrir_sao_estados_alvo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, relogio: RelogioFixo
) -> None:
    a = await criar(cliente, usuario)
    r1 = await situacao(cliente, usuario, a["id"], "CONCLUIDA")
    assert r1.status_code == HTTPStatus.OK
    assert r1.json()["situacao"] == "CONCLUIDA"
    momento = r1.json()["concluida_em"]
    assert momento.startswith("2026-10-13T12:00:00")
    relogio.avancar(timedelta(hours=1))
    # Repetir não reabre nem altera o momento da conclusão (5.3.5).
    r2 = await situacao(cliente, usuario, a["id"], "CONCLUIDA")
    assert r2.json()["situacao"] == "CONCLUIDA"
    assert r2.json()["concluida_em"] == momento
    r3 = await situacao(cliente, usuario, a["id"], "PENDENTE")
    assert r3.json()["situacao"] == "PENDENTE"
    assert r3.json()["concluida_em"] is None
    r4 = await situacao(cliente, usuario, a["id"], "PENDENTE")
    assert r4.json()["situacao"] == "PENDENTE"
    invalida = await situacao(cliente, usuario, a["id"], "TALVEZ")
    assert invalida.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_conclusao_antecipada_mantem_a_data_planejada(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    futura = await criar(cliente, usuario, data="2026-11-30")
    r = await situacao(cliente, usuario, futura["id"], "CONCLUIDA")
    assert r.json()["data"] == "2026-11-30"
    assert r.json()["concluida_em"] is not None


async def test_edicao_parcial(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar(
        cliente,
        usuario,
        descricao="Antiga",
        horario_inicial="08:00",
        horario_final="09:00",
    )
    r = await cliente.patch(
        f"{URL}/{a['id']}",
        json={"horario_final": "09:30", "prioridade": "ALTA"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK
    corpo = r.json()
    assert corpo["id"] == a["id"]
    assert corpo["horario_final"] == "09:30"
    assert corpo["duracao_minutos"] == 90
    assert corpo["nome"] == a["nome"]
    assert corpo["descricao"] == "Antiga"
    assert corpo["prioridade"] == "ALTA"
    assert corpo["situacao"] == "PENDENTE"
    sem_descricao = await cliente.patch(
        f"{URL}/{a['id']}",
        json={"descricao": None},
        headers=usuario.cabecalhos,
    )
    assert sem_descricao.json()["descricao"] is None
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 1


async def test_edicao_nao_altera_situacao_e_muda_de_data(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar(cliente, usuario)
    await situacao(cliente, usuario, a["id"], "CONCLUIDA")
    r = await cliente.patch(
        f"{URL}/{a['id']}",
        json={"nome": "Novo nome", "data": "2026-10-15"},
        headers=usuario.cabecalhos,
    )
    assert r.json()["situacao"] == "CONCLUIDA"
    assert r.json()["data"] == "2026-10-15"
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 0
    assert (await listar(cliente, usuario, data="2026-10-15"))["itens"][0][
        "nome"
    ] == "Novo nome"


async def test_edicao_valida_horarios_e_nulos(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar(
        cliente, usuario, horario_inicial="08:00", horario_final="09:00"
    )
    so_final = await cliente.patch(
        f"{URL}/{a['id']}",
        json={"horario_final": "07:00"},
        headers=usuario.cabecalhos,
    )
    assert so_final.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert (
        campo_de_erro(so_final.json())["horario_final"]
        == "HORARIO_FINAL_INVALIDO"
    )
    ambos = await cliente.patch(
        f"{URL}/{a['id']}",
        json={"horario_inicial": "10:00", "horario_final": "09:00"},
        headers=usuario.cabecalhos,
    )
    assert ambos.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    for campo in (
        "nome",
        "data",
        "categoria_id",
        "horario_inicial",
        "prioridade",
    ):
        nulo = await cliente.patch(
            f"{URL}/{a['id']}", json={campo: None}, headers=usuario.cabecalhos
        )
        assert nulo.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, campo
    categoria_ruim = await cliente.patch(
        f"{URL}/{a['id']}",
        json={"categoria_id": "01900000-0000-7000-8000-000000000000"},
        headers=usuario.cabecalhos,
    )
    assert (
        campo_de_erro(categoria_ruim.json())["categoria_id"]
        == "CATEGORIA_INVALIDA"
    )


async def test_edicao_com_sobreposicao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar(
        cliente,
        usuario,
        nome="Primeira",
        horario_inicial="08:00",
        horario_final="10:00",
    )
    b = await criar(
        cliente,
        usuario,
        nome="Segunda",
        horario_inicial="10:00",
        horario_final="11:00",
    )
    conflito = await cliente.patch(
        f"{URL}/{b['id']}",
        json={"horario_inicial": "09:00"},
        headers=usuario.cabecalhos,
    )
    assert conflito.status_code == HTTPStatus.CONFLICT
    ok = await cliente.patch(
        f"{URL}/{b['id']}",
        json={"horario_inicial": "09:00", "confirmar_sobreposicao": True},
        headers=usuario.cabecalhos,
    )
    assert ok.status_code == HTTPStatus.OK
    # Editar sem mexer no horário não conflita consigo mesma.
    sozinha = await cliente.patch(
        f"{URL}/{b['id']}",
        json={"nome": "Segunda editada"},
        headers=usuario.cabecalhos,
    )
    assert sozinha.status_code == HTTPStatus.OK


async def test_exclusao_simples_e_idempotente(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar(cliente, usuario)
    r = await cliente.delete(f"{URL}/{a['id']}", headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.NO_CONTENT
    assert r.content == b""
    outra = await cliente.delete(
        f"{URL}/{a['id']}", headers=usuario.cabecalhos
    )
    assert outra.status_code == HTTPStatus.NO_CONTENT
    assert (await listar(cliente, usuario))["indicadores"]["total"] == 0
    detalhe = await cliente.get(f"{URL}/{a['id']}", headers=usuario.cabecalhos)
    assert detalhe.status_code == HTTPStatus.NOT_FOUND
    edicao = await cliente.patch(
        f"{URL}/{a['id']}", json={"nome": "Volta"}, headers=usuario.cabecalhos
    )
    assert edicao.status_code == HTTPStatus.NOT_FOUND


async def test_alcance_de_serie_em_avulsa_ou_concluida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    avulsa = await criar(cliente, usuario)
    r = await cliente.delete(
        f"{URL}/{avulsa['id']}",
        params={"alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert codigo_de_erro(r) == "ALCANCE_INVALIDO"
    p = await cliente.patch(
        f"{URL}/{avulsa['id']}",
        json={"nome": "Outro", "alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(p) == "ALCANCE_INVALIDO"
    invalido = await cliente.delete(
        f"{URL}/{avulsa['id']}",
        params={"alcance": "TUDO"},
        headers=usuario.cabecalhos,
    )
    assert invalido.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_avulsa_vira_serie_ao_editar(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar(cliente, usuario, data="2026-10-14")
    r = await cliente.patch(
        f"{URL}/{a['id']}",
        json={
            "repeticao": {
                "periodicidade": "DIARIA",
                "termino": "ATE_DATA",
                "data_final": "2026-10-16",
            }
        },
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    corpo = r.json()
    assert corpo["recorrente"] is True
    assert corpo["numero_ocorrencia"] == 1
    assert corpo["serie"]["periodicidade"] == "DIARIA"
    assert corpo["serie"]["data_final"] == "2026-10-16"
    assert (await listar(cliente, usuario, data="2026-10-15"))["indicadores"][
        "total"
    ] == 1
    assert (await listar(cliente, usuario, data="2026-10-16"))["indicadores"][
        "total"
    ] == 1
    assert (await listar(cliente, usuario, data="2026-10-17"))["indicadores"][
        "total"
    ] == 0
