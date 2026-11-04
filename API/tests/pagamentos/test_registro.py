from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, chave_nova, criar_usuario
from ..apoio.identidade import codigo_de_erro
from ..importancias.util import criar, lembretes_no_banco, listar, situacao
from .util import (
    BASE,
    URL_IMP,
    criar_conta,
    obter_importancia,
    pagar,
    resumo,
)

LEMBRETE = {"antecedencia_dias": 1, "horario": "09:00"}


async def test_registrar_pagamento_11_6_3(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    """Previsto 99,90 e pago 105,00: só 105 conta; previsão preservada."""
    conta = await criar_conta(cliente, usuario, lembrete=LEMBRETE)
    r = await pagar(cliente, usuario, conta["id"], valor="105")
    mov = r.json()
    assert mov["tipo"] == "DESPESA"
    assert mov["valor"] == "105.00"
    assert mov["importancia"] == {
        "id": conta["id"],
        "nome": "Pagamento da internet",
        "disponivel": True,
        "data_compromisso": "2026-10-20",
        "valor_previsto": "99.90",
    }
    imp = await obter_importancia(cliente, usuario, conta["id"])
    assert imp["situacao"] == "CONCLUIDA"
    assert imp["pago"] is True
    assert imp["grupo"] == "CONCLUIDAS"
    assert imp["valor_previsto"] == "99.90"
    assert imp["pagamento"]["valor"] == "105.00"
    assert imp["pagamento"]["movimentacao_id"] == mov["id"]
    assert imp["pagamento"]["data_movimentacao"] == "2026-10-13"
    assert imp["prazo"] is None
    assert imp["momento_conclusao"].startswith("2026-10-13T12:00:00")
    assert lembretes_no_banco(banco_migrado, conta["id"])[0][0] == "CANCELADO"
    r = await resumo(cliente, usuario)
    assert r["despesas"] == "105.00"
    assert r["saldo"] == "-105.00"


async def test_cadastrar_importancia_nao_altera_saldo_4_3_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_conta(cliente, usuario)
    r = await resumo(cliente, usuario)
    assert (r["receitas"], r["despesas"], r["saldo"]) == (
        "0.00",
        "0.00",
        "0.00",
    )


async def test_pagamento_com_data_diferente_do_vencimento(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario, data_compromisso="2026-10-05")
    await pagar(cliente, usuario, conta["id"], data_movimentacao="2026-10-12")
    imp = await obter_importancia(cliente, usuario, conta["id"])
    assert imp["data_compromisso"] == "2026-10-05"
    assert imp["pagamento"]["data_movimentacao"] == "2026-10-12"
    assert (await listar(cliente, usuario, filtro="ATRASADOS"))["total"] == 0


async def test_segundo_pagamento_da_mesma_importancia_e_recusado(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    primeira = await pagar(cliente, usuario, conta["id"])
    r = await pagar(
        cliente, usuario, conta["id"], esperado=HTTPStatus.CONFLICT
    )
    assert codigo_de_erro(r) == "IMPORTANCIA_JA_PAGA"
    assert (
        r.json()["mensagem"]
        == "Esta importância já possui um pagamento registrado"
    )
    assert r.json()["detalhes"] == {"movimentacao_id": primeira.json()["id"]}
    assert (await resumo(cliente, usuario))["despesas"] == "105.00"


async def test_reenvio_com_a_mesma_chave_nao_duplica_11_6_4(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    chave = chave_nova()
    a = await pagar(cliente, usuario, conta["id"], chave=chave)
    b = await pagar(cliente, usuario, conta["id"], chave=chave)
    assert a.content == b.content
    assert b.headers["Idempotency-Replayed"] == "true"
    assert (await resumo(cliente, usuario))["despesas"] == "105.00"


async def test_importancia_invalida_para_pagamento(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    sem = await criar(cliente, usuario, nome="Aniversário da mãe")
    r = await pagar(cliente, usuario, sem["id"], esperado=HTTPStatus.CONFLICT)
    assert codigo_de_erro(r) == "IMPORTANCIA_SEM_DESPESA"
    inexistente = await pagar(
        cliente,
        usuario,
        "01900000-0000-7000-8000-000000000000",
        esperado=HTTPStatus.NOT_FOUND,
    )
    assert codigo_de_erro(inexistente) == "RECURSO_NAO_ENCONTRADO"
    conta = await criar_conta(cliente, usuario)
    await cliente.delete(
        f"{URL_IMP}/{conta['id']}", headers=usuario.cabecalhos
    )
    excluida = await pagar(
        cliente, usuario, conta["id"], esperado=HTTPStatus.NOT_FOUND
    )
    assert codigo_de_erro(excluida) == "RECURSO_NAO_ENCONTRADO"
    outro = await criar_usuario(cliente)
    minha = await criar_conta(cliente, usuario, nome="Conta minha")
    alheia = await pagar(
        cliente, outro, minha["id"], esperado=HTTPStatus.NOT_FOUND
    )
    assert codigo_de_erro(alheia) == "RECURSO_NAO_ENCONTRADO"


async def test_falha_de_validacao_nao_deixa_despesa_nem_pagamento_parcial(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    futura = await pagar(
        cliente,
        usuario,
        conta["id"],
        esperado=HTTPStatus.UNPROCESSABLE_ENTITY,
        data_movimentacao="2026-12-01",
    )
    assert futura.json()["campos"][0]["codigo"] == "DATA_FUTURA"
    imp = await obter_importancia(cliente, usuario, conta["id"])
    assert imp["situacao"] == "PENDENTE"
    assert imp["pagamento"] is None
    assert (await resumo(cliente, usuario))["despesas"] == "0.00"
    # Depois de corrigido, o pagamento funciona.
    await pagar(cliente, usuario, conta["id"])
    assert (await obter_importancia(cliente, usuario, conta["id"]))[
        "pago"
    ] is True


async def test_paga_nao_reabre_nem_perde_a_despesa(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    await pagar(cliente, usuario, conta["id"])
    reabrir = await situacao(cliente, usuario, conta["id"], "PENDENTE")
    assert reabrir.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(reabrir) == "REABERTURA_EXIGE_REMOVER_PAGAMENTO"
    concluir = await situacao(cliente, usuario, conta["id"], "CONCLUIDA")
    assert concluir.status_code == HTTPStatus.OK
    sem = await cliente.patch(
        f"{URL_IMP}/{conta['id']}",
        json={"possui_despesa": False},
        headers=usuario.cabecalhos,
    )
    assert sem.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(sem) == "IMPORTANCIA_PAGA_SEM_ALTERAR_DESPESA"
    # Editar o previsto é permitido e não altera o pago.
    ok = await cliente.patch(
        f"{URL_IMP}/{conta['id']}",
        json={"valor_previsto": "120"},
        headers=usuario.cabecalhos,
    )
    assert ok.status_code == HTTPStatus.OK
    assert ok.json()["valor_previsto"] == "120.00"
    assert ok.json()["pagamento"]["valor"] == "105.00"


async def test_excluir_a_despesa_reabre_a_importancia_11_6_7(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    conta = await criar_conta(cliente, usuario, lembrete=LEMBRETE)
    mov = (await pagar(cliente, usuario, conta["id"])).json()
    assert lembretes_no_banco(banco_migrado, conta["id"])[0][0] == "CANCELADO"
    r = await cliente.delete(
        f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    imp = await obter_importancia(cliente, usuario, conta["id"])
    assert imp["situacao"] == "PENDENTE"
    assert imp["pagamento"] is None
    assert imp["pago"] is False
    assert imp["valor_previsto"] == "99.90"
    # O lembrete ainda futuro volta a valer.
    assert lembretes_no_banco(banco_migrado, conta["id"])[0][0] == "PENDENTE"
    assert (await resumo(cliente, usuario))["despesas"] == "0.00"
    # E pode ser paga de novo, uma única vez.
    await pagar(cliente, usuario, conta["id"])
    assert (await resumo(cliente, usuario))["despesas"] == "105.00"


async def test_reaberta_com_vencimento_passado_fica_atrasada(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario, data_compromisso="2026-10-05")
    mov = (await pagar(cliente, usuario, conta["id"])).json()
    await cliente.delete(
        f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
    )
    imp = await obter_importancia(cliente, usuario, conta["id"])
    assert imp["atrasada"] is True
    assert imp["grupo"] == "ATRASADAS"
    assert imp["dias_ate_vencimento"] == -8


async def test_excluir_a_importancia_preserva_a_despesa_11_5_7(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    mov = (await pagar(cliente, usuario, conta["id"])).json()
    r = await cliente.delete(
        f"{URL_IMP}/{conta['id']}", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    detalhe = await cliente.get(
        f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
    )
    assert detalhe.status_code == HTTPStatus.OK
    assert detalhe.json()["importancia"] is None
    assert (await resumo(cliente, usuario))["despesas"] == "105.00"
    # A despesa volta a estar disponível para um novo vínculo.
    disponiveis = await cliente.get(
        f"{BASE}/despesas/disponiveis-vinculo", headers=usuario.cabecalhos
    )
    assert [d["id"] for d in disponiveis.json()["itens"]] == [mov["id"]]


async def test_editar_despesa_vinculada_reflete_na_importancia_11_6_5(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    mov = (await pagar(cliente, usuario, conta["id"])).json()
    r = await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"valor": "100"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK
    assert r.json()["importancia"]["id"] == conta["id"]
    assert (await resumo(cliente, usuario))["despesas"] == "100.00"
    imp = await obter_importancia(cliente, usuario, conta["id"])
    assert imp["pagamento"]["valor"] == "100.00"
    assert imp["valor_previsto"] == "99.90"
    # Mudar a data para outro mês transfere a contabilização.
    await cliente.patch(
        f"{BASE}/movimentacoes/{mov['id']}",
        json={"data_movimentacao": "2026-09-30"},
        headers=usuario.cabecalhos,
    )
    assert (await resumo(cliente, usuario, "2026-10"))["despesas"] == "0.00"
    assert (await resumo(cliente, usuario, "2026-09"))["despesas"] == "100.00"
    assert (await obter_importancia(cliente, usuario, conta["id"]))[
        "pago"
    ] is True


async def test_cada_ocorrencia_de_serie_tem_o_seu_pagamento(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    await criar_conta(
        cliente,
        usuario,
        nome="Aluguel",
        data_compromisso="2026-10-20",
        repeticao={"periodicidade": "MENSAL"},
    )
    todas = (await listar(cliente, usuario, filtro="ESTE_MES", mes="2026-10"))[
        "itens"
    ]
    out_id = todas[0]["id"]
    await pagar(cliente, usuario, out_id)
    nov = (await listar(cliente, usuario, filtro="ESTE_MES", mes="2026-11"))[
        "itens"
    ][0]
    assert nov["situacao"] == "PENDENTE"
    assert nov["pago"] is False
    assert (await obter_importancia(cliente, usuario, out_id))["pago"] is True
    await pagar(cliente, usuario, nov["id"], data_movimentacao="2026-10-13")
    assert (await resumo(cliente, usuario))["despesas"] == "210.00"
