from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, chave_nova
from ..apoio.identidade import codigo_de_erro
from .util import (
    URL,
    campo_de_erro,
    categoria,
    criar,
    lembretes_no_banco,
    listar,
)


async def post(cliente, usuario, corpo, chave=None):
    return await cliente.post(
        URL,
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )


async def test_cadastro_simples_8_6_3(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    """Conta de R$ 99,90: pendente, com valor previsto."""
    i = await criar(
        cliente,
        usuario,
        nome="  Pagamento da internet ",
        descricao="Vivo Fibra",
        data_compromisso="2026-10-13",
        horario="08:00",
        possui_despesa=True,
        valor_previsto="99.90",
    )
    assert i["nome"] == "Pagamento da internet"
    assert i["situacao"] == "PENDENTE"
    assert i["valor_previsto"] == "99.90"
    assert i["pagamento"] is None
    assert i["pago"] is False
    assert i["horario"] == "08:00"
    assert i["prazo"] == "HOJE"
    assert i["dias_ate_vencimento"] == 0
    assert i["grupo"] == "HOJE"
    assert i["recorrente"] is False
    assert i["lembrete"] is None
    assert i["categoria"]["nome"] == "Contas"
    assert i["categoria_financeira_sugerida"]["nome"] == "Contas"
    assert i["momento_conclusao"] is None


async def test_sem_despesa_e_sugestao_nula_sem_correspondencia(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    cat = await categoria(cliente, usuario, "Pessoal")
    i = await criar(
        cliente, usuario, nome="Aniversário da mãe", categoria_id=cat
    )
    assert i["possui_despesa"] is False
    assert i["valor_previsto"] is None
    assert i["horario"] is None
    assert i["categoria_financeira_sugerida"] is None


async def test_validacoes(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    sem = await post(cliente, usuario, {})
    assert sem.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    msgs = {c["campo"]: c["mensagem"] for c in sem.json()["campos"]}
    assert msgs["nome"] == "Informe o nome da importância"
    assert msgs["categoria_id"] == "Selecione uma categoria"
    assert msgs["data_compromisso"] == "Informe uma data válida"
    cat = await categoria(cliente, usuario)
    base = {
        "nome": "Conta de luz",
        "categoria_id": cat,
        "data_compromisso": "2026-10-20",
    }
    casos = {
        "valor_obrigatorio": (
            {"possui_despesa": True},
            "valor_previsto",
            "VALOR_PREVISTO_OBRIGATORIO",
        ),
        "valor_zero": (
            {"possui_despesa": True, "valor_previsto": "0"},
            "valor_previsto",
            "VALOR_PREVISTO_OBRIGATORIO",
        ),
        "valor_negativo": (
            {"possui_despesa": True, "valor_previsto": "-1"},
            "valor_previsto",
            "VALOR_PREVISTO_OBRIGATORIO",
        ),
        "tres_casas": (
            {"possui_despesa": True, "valor_previsto": "1.999"},
            "valor_previsto",
            "CASAS_DECIMAIS",
        ),
        "valor_sem_despesa": (
            {"valor_previsto": "10"},
            "valor_previsto",
            "VALOR_PREVISTO_NAO_PERMITIDO",
        ),
        "nome_curto": ({"nome": "ab"}, "nome", "TAMANHO_MINIMO"),
        "data_ruim": (
            {"data_compromisso": "2026-02-30"},
            "data_compromisso",
            "DATA_INVALIDA",
        ),
        "antecedencia": (
            {"lembrete": {"antecedencia_dias": 2, "horario": "09:00"}},
            "lembrete.antecedencia_dias",
            "VALOR_NAO_PERMITIDO",
        ),
        "lembrete_sem_horario": (
            {"lembrete": {"antecedencia_dias": 1}},
            "lembrete.horario",
            "OBRIGATORIO",
        ),
        "ate_data_sem_data": (
            {"repeticao": {"periodicidade": "MENSAL", "termino": "ATE_DATA"}},
            "repeticao",
            "DATA_FINAL_OBRIGATORIA",
        ),
        "data_final_anterior": (
            {
                "repeticao": {
                    "periodicidade": "MENSAL",
                    "termino": "ATE_DATA",
                    "data_final": "2026-10-01",
                }
            },
            "repeticao.data_final",
            "DATA_FINAL_REPETICAO_INVALIDA",
        ),
        "descricao_longa": (
            {"descricao": "x" * 201},
            "descricao",
            "TAMANHO_MAXIMO",
        ),
    }
    for nome, (alteracao, campo, codigo) in casos.items():
        r = await post(cliente, usuario, base | alteracao)
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, nome
        assert campo_de_erro(r.json()).get(campo) == codigo, (nome, r.text)
    msg = await post(cliente, usuario, base | {"possui_despesa": True})
    assert (
        msg.json()["campos"][0]["mensagem"]
        == "Informe um valor previsto maior que zero"
    )
    assert (await listar(cliente, usuario))["total"] == 0


async def test_data_passada_aparece_como_atrasada(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    i = await criar(
        cliente,
        usuario,
        data_compromisso="2026-10-09",
        possui_despesa=True,
        valor_previsto="480",
    )
    assert i["atrasada"] is True
    assert i["prazo"] == "ATRASADA"
    assert i["dias_ate_vencimento"] == -4
    assert i["grupo"] == "ATRASADAS"


async def test_lembrete_8_6_5_e_passado(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    # 25/10, 3 dias antes às 09:00 em São Paulo = 22/10 12:00Z.
    i = await criar(
        cliente,
        usuario,
        data_compromisso="2026-10-25",
        lembrete={"antecedencia_dias": 3, "horario": "09:00"},
    )
    assert i["lembrete"]["situacao"] == "PENDENTE"
    assert i["lembrete"]["agendado_para"].startswith("2026-10-22T12:00:00")
    assert i["lembrete"]["horario"] == "09:00"
    linhas = lembretes_no_banco(banco_migrado, i["id"])
    assert [(s, v) for s, v, *_ in linhas] == [("PENDENTE", 1)]
    # Lembrete que cairia no passado: orienta ajustar ou desativar.
    cat = await categoria(cliente, usuario)
    r = await post(
        cliente,
        usuario,
        {
            "nome": "Em cima da hora",
            "categoria_id": cat,
            "data_compromisso": "2026-10-13",
            "lembrete": {"antecedencia_dias": 0, "horario": "08:00"},
        },
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert campo_de_erro(r.json())["lembrete"] == "LEMBRETE_NO_PASSADO"
    ok = await post(
        cliente,
        usuario,
        {
            "nome": "Ainda dá tempo",
            "categoria_id": cat,
            "data_compromisso": "2026-10-13",
            "lembrete": {"antecedencia_dias": 0, "horario": "10:00"},
        },
    )
    assert ok.status_code == HTTPStatus.CREATED
    # Compromisso atrasado sem lembrete pode ser salvo.
    atrasado = await post(
        cliente,
        usuario,
        {
            "nome": "Já atrasado",
            "categoria_id": cat,
            "data_compromisso": "2026-10-01",
        },
    )
    assert atrasado.status_code == HTTPStatus.CREATED


async def test_idempotencia_e_autenticacao(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    chave = chave_nova()
    a = await criar(cliente, usuario, chave=chave)
    b = await criar(cliente, usuario, chave=chave)
    assert a == b
    assert (await listar(cliente, usuario))["total"] == 1
    assert (
        await cliente.post(URL, json={})
    ).status_code == HTTPStatus.UNAUTHORIZED
    r = await cliente.post(URL, json={}, headers=usuario.cabecalhos)
    assert codigo_de_erro(r) == "IDEMPOTENCIA_CHAVE_AUSENTE"


async def test_categoria_invalida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await post(
        cliente,
        usuario,
        {
            "nome": "Conta",
            "categoria_id": "01900000-0000-7000-8000-000000000000",
            "data_compromisso": "2026-10-20",
        },
    )
    assert campo_de_erro(r.json())["categoria_id"] == "CATEGORIA_INVALIDA"
