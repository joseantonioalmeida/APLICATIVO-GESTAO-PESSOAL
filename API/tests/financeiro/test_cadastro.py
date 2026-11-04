from http import HTTPStatus

import httpx

from ..apoio.api import UsuarioTeste, chave_nova
from ..apoio.identidade import codigo_de_erro
from .util import (
    BASE,
    HOJE,
    categoria,
    despesa,
    movimentacoes,
    receita,
    resumo,
)


def campos(r: httpx.Response) -> dict[str, str]:
    return {c["campo"]: c["codigo"] for c in r.json()["campos"]}


async def enviar(cliente, usuario, caminho, corpo, chave=None):
    return await cliente.post(
        f"{BASE}/{caminho}",
        json=corpo,
        headers={
            **usuario.cabecalhos,
            "Idempotency-Key": chave or chave_nova(),
        },
    )


async def test_receita_valida_e_formato_do_valor(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    r = await receita(
        cliente,
        usuario,
        valor="100",
        nome="  Venda de notebook ",
        contraparte="  Cliente X ",
        forma="PIX",
    )
    assert r["tipo"] == "RECEITA"
    assert r["valor"] == "100.00"
    assert r["nome"] == "Venda de notebook"
    assert r["contraparte"] == "Cliente X"
    assert r["forma"] == "PIX"
    assert r["categoria"]["nome"] == "Salário"
    assert r["importancia"] is None
    assert r["descricao"] is None


async def test_despesa_valida(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    d = await despesa(
        cliente,
        usuario,
        valor="0.1",
        forma="CARTAO_DEBITO",
        descricao="Compras da semana",
    )
    assert d["tipo"] == "DESPESA"
    assert d["valor"] == "0.10"
    assert d["forma"] == "CARTAO_DEBITO"


async def test_validacoes_da_receita(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    cat = await categoria(cliente, usuario, "RECEITA", "Vendas")
    base = {
        "nome": "Salário",
        "valor": "10",
        "categoria_id": cat,
        "data_movimentacao": HOJE,
    }
    sem = await enviar(cliente, usuario, "receitas", {})
    assert sem.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    msgs = {c["campo"]: c["mensagem"] for c in sem.json()["campos"]}
    assert msgs["nome"] == "Informe o nome da receita"
    assert msgs["valor"] == "Informe um valor recebido maior que zero"
    assert msgs["categoria_id"] == "Selecione uma categoria"
    assert msgs["data_movimentacao"] == "Informe uma data válida"
    casos = {
        "valor_zero": ({"valor": "0"}, "valor", "VALOR_OBRIGATORIO"),
        "valor_negativo": ({"valor": "-5"}, "valor", "VALOR_OBRIGATORIO"),
        "valor_texto": ({"valor": "abc"}, "valor", "VALOR_OBRIGATORIO"),
        "valor_numero_json": ({"valor": 10.5}, "valor", "VALOR_OBRIGATORIO"),
        "tres_casas": ({"valor": "1.234"}, "valor", "CASAS_DECIMAIS"),
        "virgula": ({"valor": "1,50"}, "valor", "VALOR_OBRIGATORIO"),
        "acima_do_limite": (
            {"valor": "10000000000"},
            "valor",
            "VALOR_ACIMA_DO_LIMITE",
        ),
        "futura": (
            {"data_movimentacao": "2026-10-14"},
            "data_movimentacao",
            "DATA_FUTURA",
        ),
        "forma_de_despesa": (
            {"forma": "BOLETO"},
            "forma",
            "VALOR_NAO_PERMITIDO",
        ),
        "nome_so_espacos": ({"nome": "   "}, "nome", "NOME_OBRIGATORIO"),
    }
    for nome, (alteracao, campo, codigo) in casos.items():
        r = await enviar(cliente, usuario, "receitas", base | alteracao)
        assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, nome
        assert campos(r).get(campo) == codigo, (nome, r.text)
    futura = await enviar(
        cliente,
        usuario,
        "receitas",
        base | {"data_movimentacao": "2026-10-14"},
    )
    assert (
        futura.json()["campos"][0]["mensagem"]
        == "A data do recebimento não pode ser futura"
    )
    casas = await enviar(
        cliente, usuario, "receitas", base | {"valor": "1.234"}
    )
    assert (
        casas.json()["campos"][0]["mensagem"]
        == "Informe um valor com até duas casas decimais"
    )
    limite = await enviar(
        cliente, usuario, "receitas", base | {"valor": "9999999999.99"}
    )
    assert limite.status_code == HTTPStatus.CREATED


async def test_despesa_futura_orienta_a_usar_importancias(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    cat = await categoria(cliente, usuario, "DESPESA", "Contas")
    r = await enviar(
        cliente,
        usuario,
        "despesas",
        {
            "nome": "Internet",
            "valor": "99.90",
            "categoria_id": cat,
            "data_movimentacao": "2026-10-20",
        },
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert (
        r.json()["campos"][0]["mensagem"]
        == "A data do pagamento não pode ser futura. "
        "Cadastre o compromisso em Importâncias"
    )
    sem_nome = await enviar(
        cliente,
        usuario,
        "despesas",
        {"valor": "1", "categoria_id": cat, "data_movimentacao": HOJE},
    )
    assert (
        sem_nome.json()["campos"][0]["mensagem"] == "Informe o nome da despesa"
    )


async def test_categoria_deve_ser_do_mesmo_tipo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    despesa_cat = await categoria(cliente, usuario, "DESPESA", "Moradia")
    r = await enviar(
        cliente,
        usuario,
        "receitas",
        {
            "nome": "Salário",
            "valor": "1",
            "categoria_id": despesa_cat,
            "data_movimentacao": HOJE,
        },
    )
    assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert campos(r)["categoria_id"] == "CATEGORIA_INVALIDA"
    inexistente = await enviar(
        cliente,
        usuario,
        "despesas",
        {
            "nome": "Aluguel",
            "valor": "1",
            "categoria_id": "01900000-0000-7000-8000-000000000000",
            "data_movimentacao": HOJE,
        },
    )
    assert campos(inexistente)["categoria_id"] == "CATEGORIA_INVALIDA"


async def test_exige_autenticacao_e_chave(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    assert (
        await cliente.post(f"{BASE}/receitas", json={})
    ).status_code == HTTPStatus.UNAUTHORIZED
    r = await cliente.post(
        f"{BASE}/despesas", json={}, headers=usuario.cabecalhos
    )
    assert codigo_de_erro(r) == "IDEMPOTENCIA_CHAVE_AUSENTE"


async def test_idempotencia_nao_duplica_mas_permite_iguais_distintos(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    chave = chave_nova()
    a = await receita(cliente, usuario, chave=chave)
    b = await receita(cliente, usuario, chave=chave)
    assert a == b
    # Recebimentos distintos com nome, data e valor iguais são legítimos.
    await receita(cliente, usuario)
    r = await resumo(cliente, usuario)
    assert r["receitas"] == "4901.50"
    d1 = await despesa(cliente, usuario)
    d2 = await despesa(cliente, usuario)
    assert d1["id"] != d2["id"]


async def test_receita_e_despesa_com_mesma_chave_sao_acoes_distintas(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    chave = chave_nova()
    await receita(cliente, usuario, chave=chave)
    await despesa(cliente, usuario, chave=chave)
    assert len((await movimentacoes(cliente, usuario))["itens"]) == 2
