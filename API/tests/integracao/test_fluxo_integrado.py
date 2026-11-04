"""CT-F11-01: fluxo dirigido de ponta a ponta com painel coerente."""

from datetime import timedelta
from http import HTTPStatus
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..apoio.api import UsuarioTeste
from ..apoio.relogio import RelogioFixo
from ..atividades.util import URL as URL_ATIVIDADES
from ..atividades.util import criar as criar_atividade
from ..financeiro.util import BASE, despesa, receita
from ..importancias.util import criar as criar_importancia
from ..lembretes.util import ciclo
from ..pagamentos.util import pagar

PAINEL = "/api/v1/painel"
NOTIFICACOES = "/api/v1/notificacoes"


async def ler(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    caminho: str,
    **params: Any,
) -> dict[str, Any]:
    r = await cliente.get(caminho, params=params, headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()


async def test_fluxo_completo_com_painel_coerente(  # noqa: PLR0915
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
) -> None:
    # 1. Atividade semanal iniciada na terça anterior: hoje (13/10) é a 2ª.
    await criar_atividade(
        cliente,
        usuario,
        data="2026-10-06",
        repeticao={"periodicidade": "SEMANAL", "termino": "SEM_DATA_FINAL"},
    )
    painel_atv = await ler(cliente, usuario, f"{PAINEL}/atividades-hoje")
    tela_atv = await ler(cliente, usuario, URL_ATIVIDADES)
    assert painel_atv["total"] == tela_atv["indicadores"]["total"] == 1
    assert painel_atv["pendencias_anteriores"]["quantidade"] == 1

    # 2. Receita e despesa do mês: saldo do painel = Financeiro (4.3.1).
    await receita(
        cliente, usuario, valor="2450.75", data_movimentacao="2026-10-05"
    )
    await despesa(
        cliente, usuario, valor="1230.40", data_movimentacao="2026-10-06"
    )
    fin = await ler(cliente, usuario, f"{PAINEL}/financeiro")
    resumo = await ler(cliente, usuario, f"{BASE}/resumo", mes="2026-10")
    assert fin["mes"]["saldo"] == resumo["saldo"] == "1220.35"

    # 3. Importância de R$ 99,90 com lembrete: não altera o saldo (4.3.4).
    conta = await criar_importancia(
        cliente,
        usuario,
        nome="Conta de internet",
        data_compromisso="2026-10-14",
        possui_despesa=True,
        valor_previsto="99.90",
        lembrete={"antecedencia_dias": 1, "horario": "20:00"},
    )
    fin = await ler(cliente, usuario, f"{PAINEL}/financeiro")
    assert fin["mes"]["saldo"] == "1220.35"
    imp = await ler(cliente, usuario, f"{PAINEL}/importancias")
    assert [i["id"] for i in imp["proximas"]] == [conta["id"]]
    assert imp["pendentes_mes"] == 1

    # 4. O processador gera a notificação no horário do lembrete (8.6.5).
    relogio.avancar(timedelta(hours=12))  # 13/10 21:00 em São Paulo
    resultado = await ciclo(fabrica, relogio)
    assert resultado.enviados == 1
    nao_lidas = await ler(cliente, usuario, f"{NOTIFICACOES}/nao-lidas")
    assert nao_lidas == {"quantidade": 1}
    (nota,) = (await ler(cliente, usuario, NOTIFICACOES))["itens"]
    assert nota["importancia"] == {"id": conta["id"], "disponivel": True}
    r = await cliente.post(
        f"{NOTIFICACOES}/{nota['id']}/leitura", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.OK
    assert await ler(cliente, usuario, f"{NOTIFICACOES}/nao-lidas") == {
        "quantidade": 0
    }
    # Ler a notificação não conclui nem paga o compromisso.
    imp = await ler(cliente, usuario, f"{PAINEL}/importancias")
    assert imp["pendentes_mes"] == 1

    # 5. Pagamento de R$ 105,00: só o valor pago entra nas despesas.
    r = await pagar(cliente, usuario, conta["id"], valor="105.00")
    assert r.status_code == HTTPStatus.CREATED
    movimentacao_id = r.json()["id"]
    fin = await ler(cliente, usuario, f"{PAINEL}/financeiro")
    assert fin["mes"]["despesas"] == "1335.40"
    assert fin["mes"]["saldo"] == "1115.35"
    assert fin["dia"]["despesas"] == "105.00"
    resumo = await ler(cliente, usuario, f"{BASE}/resumo", mes="2026-10")
    assert resumo["saldo"] == fin["mes"]["saldo"]
    imp = await ler(cliente, usuario, f"{PAINEL}/importancias")
    assert (imp["pendentes_mes"], imp["proximas"]) == (0, [])
    detalhe = await ler(
        cliente, usuario, f"/api/v1/importancias/{conta['id']}"
    )
    assert detalhe["situacao"] == "CONCLUIDA"
    assert detalhe["valor_previsto"] == "99.90"
    assert detalhe["pagamento"]["valor"] == "105.00"

    # 6. Excluir a despesa reabre a importância e devolve os totais.
    r = await cliente.delete(
        f"{BASE}/movimentacoes/{movimentacao_id}", headers=usuario.cabecalhos
    )
    assert r.status_code == HTTPStatus.NO_CONTENT
    fin = await ler(cliente, usuario, f"{PAINEL}/financeiro")
    assert fin["mes"]["saldo"] == "1220.35"
    imp = await ler(cliente, usuario, f"{PAINEL}/importancias")
    assert [i["id"] for i in imp["proximas"]] == [conta["id"]]
    assert imp["pendentes_mes"] == 1
