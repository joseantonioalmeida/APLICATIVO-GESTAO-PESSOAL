import asyncio
from http import HTTPStatus

import httpx
import pytest

from ..apoio.api import UsuarioTeste, chave_nova
from ..financeiro.util import categoria as categoria_financeira
from .util import (
    BASE,
    URL_IMP,
    criar_conta,
    despesa_avulsa,
    obter_importancia,
    resumo,
)

pytestmark = pytest.mark.concorrencia


async def test_dois_pagamentos_simultaneos_geram_uma_despesa(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    cat = await categoria_financeira(cliente, usuario, "DESPESA", "Contas")

    def pedido():
        return cliente.post(
            f"{BASE}/despesas",
            json={
                "nome": "Pagamento da internet",
                "valor": "99.90",
                "categoria_id": cat,
                "data_movimentacao": "2026-10-13",
                "importancia_id": conta["id"],
            },
            headers={**usuario.cabecalhos, "Idempotency-Key": chave_nova()},
        )

    respostas = await asyncio.gather(*[pedido() for _ in range(4)])
    codigos = sorted(r.status_code for r in respostas)
    assert codigos == [HTTPStatus.CREATED] + [HTTPStatus.CONFLICT] * 3
    recusadas = [r for r in respostas if r.status_code == HTTPStatus.CONFLICT]
    assert {r.json()["codigo"] for r in recusadas} == {"IMPORTANCIA_JA_PAGA"}
    assert (await resumo(cliente, usuario))["despesas"] == "99.90"
    assert (await obter_importancia(cliente, usuario, conta["id"]))[
        "pago"
    ] is True


async def test_mesma_despesa_para_dois_compromissos_quita_so_um(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    a = await criar_conta(cliente, usuario, nome="Conta A")
    b = await criar_conta(cliente, usuario, nome="Conta B")
    mov = await despesa_avulsa(cliente, usuario)
    ra, rb = await asyncio.gather(*[
        cliente.put(
            f"{URL_IMP}/{c['id']}/pagamento",
            json={"movimentacao_id": mov["id"]},
            headers=usuario.cabecalhos,
        )
        for c in (a, b)
    ])
    assert sorted([ra.status_code, rb.status_code]) == [
        HTTPStatus.OK,
        HTTPStatus.CONFLICT,
    ]
    perdedora = ra if ra.status_code == HTTPStatus.CONFLICT else rb
    assert perdedora.json()["codigo"] == "DESPESA_JA_VINCULADA"
    pagas = [
        (await obter_importancia(cliente, usuario, c["id"]))["pago"]
        for c in (a, b)
    ]
    assert sorted(pagas) == [False, True]


async def test_exclusao_da_despesa_e_novo_pagamento_em_paralelo(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste
) -> None:
    conta = await criar_conta(cliente, usuario)
    mov = await despesa_avulsa(cliente, usuario)
    await cliente.put(
        f"{URL_IMP}/{conta['id']}/pagamento",
        json={"movimentacao_id": mov["id"]},
        headers=usuario.cabecalhos,
    )
    excluir, ler = await asyncio.gather(
        cliente.delete(
            f"{BASE}/movimentacoes/{mov['id']}", headers=usuario.cabecalhos
        ),
        cliente.get(f"{URL_IMP}/{conta['id']}", headers=usuario.cabecalhos),
    )
    assert excluir.status_code == HTTPStatus.NO_CONTENT
    # A leitura vê o estado inteiro de antes ou de depois, nunca um meio-termo.
    corpo = ler.json()
    assert (corpo["pago"], corpo["pagamento"] is not None) in {
        (True, True),
        (False, False),
    }
