from datetime import timedelta
from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste
from ..apoio.identidade import codigo_de_erro
from .util import (
    URL,
    campo_de_erro,
    categoria,
    criar,
    lembretes_no_banco,
    listar,
    obter,
    situacao,
)

LEMBRETE = {"antecedencia_dias": 1, "horario": "09:00"}


async def patch(cliente, usuario, id_, corpo) -> httpx.Response:
    return await cliente.patch(
        f"{URL}/{id_}", json=corpo, headers=usuario.cabecalhos
    )


async def test_concluir_e_reabrir_sem_despesa_7_4_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    i = await criar(
        cliente,
        usuario,
        nome="Aniversário da mãe",
        data_compromisso="2026-10-26",
        lembrete=LEMBRETE,
    )
    r = await situacao(cliente, usuario, i["id"], "CONCLUIDA")
    assert r.status_code == HTTPStatus.OK
    corpo = r.json()
    assert corpo["situacao"] == "CONCLUIDA"
    assert corpo["grupo"] == "CONCLUIDAS"
    assert corpo["pago"] is False
    assert corpo["prazo"] is None
    assert corpo["atrasada"] is False
    assert corpo["momento_conclusao"].startswith("2026-10-13T12:00:00")
    # Concluir cancela o lembrete pendente (mesma versão).
    assert [
        (s, v) for s, v, *_ in lembretes_no_banco(banco_migrado, i["id"])
    ] == [("CANCELADO", 1)]
    momento = corpo["momento_conclusao"]
    repetida = await situacao(cliente, usuario, i["id"], "CONCLUIDA")
    assert repetida.json()["momento_conclusao"] == momento
    # Reabrir reativa o lembrete ainda futuro.
    aberta = await situacao(cliente, usuario, i["id"], "PENDENTE")
    assert aberta.json()["situacao"] == "PENDENTE"
    assert aberta.json()["momento_conclusao"] is None
    assert [
        (s, v) for s, v, *_ in lembretes_no_banco(banco_migrado, i["id"])
    ] == [("PENDENTE", 1)]
    again = await situacao(cliente, usuario, i["id"], "PENDENTE")
    assert again.status_code == HTTPStatus.OK
    assert (await listar(cliente, usuario))["grupos"]["concluidas"] == 0


async def test_reabrir_nao_reativa_lembrete_vencido(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    banco_migrado: str,
    relogio,
) -> None:
    i = await criar(
        cliente,
        usuario,
        data_compromisso="2026-10-14",
        lembrete={"antecedencia_dias": 0, "horario": "08:00"},
    )
    await situacao(cliente, usuario, i["id"], "CONCLUIDA")
    relogio.avancar(
        timedelta(hours=23, minutes=30)
    )  # passou das 08:00 do dia 14
    await situacao(cliente, usuario, i["id"], "PENDENTE")
    assert lembretes_no_banco(banco_migrado, i["id"])[0][0] == "CANCELADO"


async def test_com_despesa_exige_pagamento_7_3_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    i = await criar(
        cliente, usuario, possui_despesa=True, valor_previsto="99.90"
    )
    r = await situacao(cliente, usuario, i["id"], "CONCLUIDA")
    assert r.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(r) == "CONCLUSAO_EXIGE_PAGAMENTO"
    pendente = await situacao(cliente, usuario, i["id"], "PENDENTE")
    assert pendente.status_code == HTTPStatus.OK
    assert (await obter(cliente, usuario, i["id"]))["situacao"] == "PENDENTE"
    invalida = await situacao(cliente, usuario, i["id"], "TALVEZ")
    assert invalida.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_edicao_parcial_preserva_a_identidade(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    i = await criar(
        cliente,
        usuario,
        nome="Pagamento da internet",
        descricao="Vivo",
        horario="08:00",
        possui_despesa=True,
        valor_previsto="99.90",
    )
    r = await patch(
        cliente,
        usuario,
        i["id"],
        {
            "nome": "Internet fibra",
            "valor_previsto": "109.90",
            "horario": None,
            "descricao": None,
        },
    )
    assert r.status_code == HTTPStatus.OK, r.text
    c = r.json()
    assert c["id"] == i["id"]
    assert c["nome"] == "Internet fibra"
    assert c["valor_previsto"] == "109.90"
    assert c["horario"] is None
    assert c["descricao"] is None
    assert c["possui_despesa"] is True
    cat = await categoria(cliente, usuario, "Compras")
    r2 = await patch(
        cliente,
        usuario,
        i["id"],
        {"categoria_id": cat, "data_compromisso": "2026-10-30"},
    )
    assert r2.json()["categoria"]["nome"] == "Compras"
    assert r2.json()["data_compromisso"] == "2026-10-30"
    assert (await listar(cliente, usuario))["total"] == 1


async def test_alterar_possui_despesa(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    com = await criar(
        cliente, usuario, possui_despesa=True, valor_previsto="50"
    )
    r = await patch(cliente, usuario, com["id"], {"possui_despesa": False})
    assert r.status_code == HTTPStatus.OK
    assert r.json()["possui_despesa"] is False
    assert r.json()["valor_previsto"] is None
    sem_valor = await patch(
        cliente, usuario, com["id"], {"possui_despesa": True}
    )
    assert sem_valor.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert (
        campo_de_erro(sem_valor.json())["valor_previsto"]
        == "VALOR_PREVISTO_OBRIGATORIO"
    )
    de_novo = await patch(
        cliente,
        usuario,
        com["id"],
        {"possui_despesa": True, "valor_previsto": "75.5"},
    )
    assert de_novo.json()["valor_previsto"] == "75.50"
    proibido = await patch(
        cliente,
        usuario,
        com["id"],
        {"possui_despesa": False, "valor_previsto": "5"},
    )
    assert (
        campo_de_erro(proibido.json())["valor_previsto"]
        == "VALOR_PREVISTO_NAO_PERMITIDO"
    )
    feita = await criar(cliente, usuario, nome="Sem despesa feita")
    await situacao(cliente, usuario, feita["id"], "CONCLUIDA")
    bloqueada = await patch(
        cliente,
        usuario,
        feita["id"],
        {"possui_despesa": True, "valor_previsto": "10"},
    )
    assert bloqueada.status_code == HTTPStatus.CONFLICT
    assert (
        codigo_de_erro(bloqueada)
        == "IMPORTANCIA_CONCLUIDA_SEM_ALTERAR_DESPESA"
    )


async def test_validacoes_na_edicao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    i = await criar(cliente, usuario)
    for corpo in (
        {"nome": None},
        {"nome": "ab"},
        {"data_compromisso": None},
        {"data_compromisso": "x"},
        {"categoria_id": None},
        {"possui_despesa": None},
        {"alcance": None},
        {"valor_previsto": "1.999"},
    ):
        r = await patch(cliente, usuario, i["id"], corpo)
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, corpo
    ruim = await patch(
        cliente,
        usuario,
        i["id"],
        {"categoria_id": "01900000-0000-7000-8000-000000000000"},
    )
    assert campo_de_erro(ruim.json())["categoria_id"] == "CATEGORIA_INVALIDA"


async def test_lembrete_nova_versao_ao_mudar_a_data_ou_a_configuracao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    i = await criar(
        cliente, usuario, data_compromisso="2026-10-25", lembrete=LEMBRETE
    )
    id_ = i["id"]
    assert [(s, v) for s, v, *_ in lembretes_no_banco(banco_migrado, id_)] == [
        ("PENDENTE", 1)
    ]
    # Mesmos valores: sem nova versão.
    await patch(
        cliente,
        usuario,
        id_,
        {"lembrete": LEMBRETE, "nome": "Conta renomeada"},
    )
    assert [v for _, v, *_ in lembretes_no_banco(banco_migrado, id_)] == [1]
    # Muda a data: o lembrete acompanha (versão 2).
    r = await patch(cliente, usuario, id_, {"data_compromisso": "2026-10-28"})
    assert r.json()["lembrete"]["agendado_para"].startswith(
        "2026-10-27T12:00:00"
    )
    assert [(s, v) for s, v, *_ in lembretes_no_banco(banco_migrado, id_)] == [
        ("PENDENTE", 2)
    ]
    # Muda a antecedência: versão 3.
    r = await patch(
        cliente,
        usuario,
        id_,
        {"lembrete": {"antecedencia_dias": 7, "horario": "10:00"}},
    )
    assert r.json()["lembrete"]["antecedencia_dias"] == 7
    assert r.json()["lembrete"]["agendado_para"].startswith(
        "2026-10-21T13:00:00"
    )
    assert [v for _, v, *_ in lembretes_no_banco(banco_migrado, id_)] == [3]
    # Lembrete no passado é recusado na edição.
    ruim = await patch(
        cliente,
        usuario,
        id_,
        {
            "lembrete": {"antecedencia_dias": 7, "horario": "09:00"},
            "data_compromisso": "2026-10-14",
        },
    )
    assert campo_de_erro(ruim.json())["lembrete"] == "LEMBRETE_NO_PASSADO"


async def test_desativar_lembrete_e_reabertura_nao_reativa(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    i = await criar(
        cliente, usuario, data_compromisso="2026-10-25", lembrete=LEMBRETE
    )
    r = await patch(cliente, usuario, i["id"], {"lembrete": None})
    assert r.json()["lembrete"]["situacao"] == "DESATIVADO"
    assert lembretes_no_banco(banco_migrado, i["id"])[0][0] == "DESATIVADO"
    await situacao(cliente, usuario, i["id"], "CONCLUIDA")
    await situacao(cliente, usuario, i["id"], "PENDENTE")
    assert lembretes_no_banco(banco_migrado, i["id"])[0][0] == "DESATIVADO"
    # Mudar a data de um lembrete desativado não o reativa.
    await patch(cliente, usuario, i["id"], {"data_compromisso": "2026-10-29"})
    assert lembretes_no_banco(banco_migrado, i["id"])[0][0] == "DESATIVADO"
    # Reativar: nova versão pendente.
    r = await patch(cliente, usuario, i["id"], {"lembrete": LEMBRETE})
    assert r.json()["lembrete"]["situacao"] == "PENDENTE"
    assert lembretes_no_banco(banco_migrado, i["id"])[0][:2] == ("PENDENTE", 2)


async def test_ativar_lembrete_em_importancia_sem_lembrete(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    i = await criar(cliente, usuario, data_compromisso="2026-10-25")
    r = await patch(cliente, usuario, i["id"], {"lembrete": LEMBRETE})
    assert r.json()["lembrete"]["situacao"] == "PENDENTE"
    assert lembretes_no_banco(banco_migrado, i["id"])[0][:2] == ("PENDENTE", 1)


async def test_exclusao_simples_cancela_lembrete_e_e_idempotente(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    i = await criar(
        cliente, usuario, data_compromisso="2026-10-25", lembrete=LEMBRETE
    )
    r = await cliente.delete(f"{URL}/{i['id']}", headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.NO_CONTENT
    again = await cliente.delete(
        f"{URL}/{i['id']}", headers=usuario.cabecalhos
    )
    assert again.status_code == HTTPStatus.NO_CONTENT
    assert lembretes_no_banco(banco_migrado, i["id"])[0][0] == "CANCELADO"
    assert (await listar(cliente, usuario))["total"] == 0
    assert (
        await cliente.get(f"{URL}/{i['id']}", headers=usuario.cabecalhos)
    ).status_code == HTTPStatus.NOT_FOUND
    assert (
        await patch(cliente, usuario, i["id"], {"nome": "Volta"})
    ).status_code == HTTPStatus.NOT_FOUND
    assert (
        await cliente.delete(
            f"{URL}/01900000-0000-7000-8000-000000000000",
            headers=usuario.cabecalhos,
        )
    ).status_code == HTTPStatus.NOT_FOUND


async def test_alcance_invalido_em_avulsa_e_concluida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    i = await criar(cliente, usuario)
    r = await cliente.delete(
        f"{URL}/{i['id']}",
        params={"alcance": "ESTA_E_PROXIMAS"},
        headers=usuario.cabecalhos,
    )
    assert codigo_de_erro(r) == "ALCANCE_INVALIDO"
    p = await patch(
        cliente,
        usuario,
        i["id"],
        {"nome": "Outro nome", "alcance": "ESTA_E_PROXIMAS"},
    )
    assert codigo_de_erro(p) == "ALCANCE_INVALIDO"
    await situacao(cliente, usuario, i["id"], "CONCLUIDA")
    rep = await patch(
        cliente, usuario, i["id"], {"repeticao": {"periodicidade": "MENSAL"}}
    )
    assert codigo_de_erro(rep) == "REPETICAO_EXIGE_ALCANCE_SERIE"
