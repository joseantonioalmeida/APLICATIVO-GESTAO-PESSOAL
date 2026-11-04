"""CT-F11-02: orçamento de tempo com o volume de referência (§12).

Volume: 1 usuário com 5 anos de dados (10 séries diárias, 2.000
movimentações e 500 importâncias). Meta proposta: p95 < 300 ms por
endpoint (medido em processo, sem rede). Roda só com `-m performance` e
nunca junto do Pyright ou de outras suítes (medição limpa).
"""

import statistics
import time
from http import HTTPStatus

import httpx
import psycopg
import pytest

from ..apoio.api import UsuarioTeste
from ..apoio.banco import url_libpq

pytestmark = pytest.mark.performance

AMOSTRAS = 30
META_P95_S = 0.300
META_FRIO_S = 10.0
HOJE = "2026-10-13"
SERIES = 10
DIAS = 1826  # 5 anos até hoje


def popular(banco: str, usuario_id: str) -> None:
    """Insere o volume de referência diretamente (rápido e repetível)."""
    with psycopg.connect(url_libpq(banco)) as c:
        cat_atv = c.execute(
            "SELECT id FROM categoria_atividade WHERE nome = 'Estudo'"
        ).fetchone()
        assert cat_atv is not None
        for i in range(SERIES):
            serie = c.execute(
                "INSERT INTO serie_atividade (id, usuario_id, categoria_id, "
                "nome_padrao, periodicidade, data_referencia, "
                "horario_inicial_padrao, horario_final_padrao) VALUES "
                "(gen_random_uuid(), %s, %s, %s, 'DIARIA', "
                "%s::date - %s::int, %s, %s) RETURNING id",
                (
                    usuario_id,
                    cat_atv[0],
                    f"Rotina diaria {i}",
                    HOJE,
                    DIAS - 1,
                    f"{6 + i:02d}:00",
                    f"{6 + i:02d}:30",
                ),
            ).fetchone()
            assert serie is not None
            if i == SERIES - 1:
                continue  # a última fica sem materializar (partida a frio)
            c.execute(
                "INSERT INTO atividade (id, usuario_id, categoria_id, "
                "serie_id, numero_ocorrencia, nome, prioridade, "
                "data_atividade, horario_inicial, horario_final) "
                "SELECT gen_random_uuid(), %s, %s, %s, n, %s, 'BAIXA', "
                "%s::date - (%s::int - n), %s, %s "
                "FROM generate_series(1, %s) n",
                (
                    usuario_id,
                    cat_atv[0],
                    serie[0],
                    f"Rotina diaria {i}",
                    HOJE,
                    DIAS,
                    f"{6 + i:02d}:00",
                    f"{6 + i:02d}:30",
                    DIAS,
                ),
            )
        c.execute(
            "INSERT INTO movimentacao_financeira (id, usuario_id, "
            "categoria_id, tipo, nome, valor, data_movimentacao) "
            "SELECT gen_random_uuid(), %s, "
            "(SELECT id FROM categoria_financeira WHERE tipo = t.tipo "
            " ORDER BY nome LIMIT 1 OFFSET (n %% 5)), t.tipo, "
            "'Movimento ' || n, (n %% 500 + 1)::numeric / 10, "
            "%s::date - (n %% %s::int) "
            "FROM generate_series(1, 2000) n, "
            "LATERAL (SELECT CASE WHEN n %% 3 = 0 THEN 'RECEITA' "
            "ELSE 'DESPESA' END AS tipo) t",
            (usuario_id, HOJE, DIAS),
        )
        cat_imp = c.execute(
            "SELECT id FROM categoria_importancia WHERE nome = 'Contas'"
        ).fetchone()
        assert cat_imp is not None
        c.execute(
            "INSERT INTO importancia (id, usuario_id, categoria_id, nome, "
            "data_compromisso, possui_despesa, valor_previsto, "
            "concluida_manualmente_em) "
            "SELECT gen_random_uuid(), %s, %s, 'Compromisso ' || n, "
            "%s::date + ((n - 250) * 3), (n %% 2 = 0), "
            "CASE WHEN n %% 2 = 0 THEN 99.90 END, "
            "CASE WHEN n %% 2 = 1 AND n %% 5 = 0 THEN now() END "
            "FROM generate_series(1, 500) n",
            (usuario_id, cat_imp[0], HOJE),
        )
        c.execute("ANALYZE")


async def medir(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, caminho: str
) -> float:
    """p95 (segundos) de `AMOSTRAS` chamadas, após uma de aquecimento."""
    r = await cliente.get(caminho, headers=usuario.cabecalhos)
    assert r.status_code == HTTPStatus.OK, r.text
    tempos: list[float] = []
    for _ in range(AMOSTRAS):
        inicio = time.perf_counter()
        r = await cliente.get(caminho, headers=usuario.cabecalhos)
        tempos.append(time.perf_counter() - inicio)
        assert r.status_code == HTTPStatus.OK
    tempos.sort()
    p95 = tempos[int(AMOSTRAS * 0.95) - 1]
    print(  # noqa: T201
        f"{caminho:<60} mediana={statistics.median(tempos) * 1000:6.1f} ms"
        f"  p95={p95 * 1000:6.1f} ms"
    )
    return p95


ENDPOINTS = [
    f"/api/v1/atividades?data={HOJE}",
    f"/api/v1/atividades?data={HOJE}&ordenacao=PRIORIDADE&limite=50",
    "/api/v1/atividades/pendencias-anteriores",
    "/api/v1/financeiro/resumo?mes=2026-10",
    "/api/v1/financeiro/resumo?mes=2024-03",
    "/api/v1/financeiro/movimentacoes?mes=2026-10&limite=50",
    "/api/v1/financeiro/movimentacoes?mes=2026-10&tipo=DESPESA&busca=mov",
    "/api/v1/importancias",
    "/api/v1/importancias?filtro=ATRASADOS",
    "/api/v1/importancias?filtro=CONCLUIDOS",
    "/api/v1/importancias?filtro=ESTE_MES",
    "/api/v1/importancias/disponiveis-pagamento",
    "/api/v1/financeiro/despesas/disponiveis-vinculo",
    "/api/v1/painel/atividades-hoje",
    "/api/v1/painel/financeiro",
    "/api/v1/painel/importancias",
    "/api/v1/notificacoes",
]


async def test_orcamento_de_tempo_com_volume_de_referencia(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    popular(banco_migrado, str(usuario.id))

    # Partida a frio: materializa 1.826 ocorrências da série pendente.
    inicio = time.perf_counter()
    r = await cliente.get(
        "/api/v1/atividades/pendencias-anteriores", headers=usuario.cabecalhos
    )
    frio = time.perf_counter() - inicio
    print(f"partida a frio (materialização de 1 série): {frio * 1000:.0f} ms")  # noqa: T201
    assert r.status_code == HTTPStatus.OK
    assert r.json()["quantidade"] == SERIES * (DIAS - 1)
    assert frio < META_FRIO_S

    resultados = {c: await medir(cliente, usuario, c) for c in ENDPOINTS}
    acima = {c: p for c, p in resultados.items() if p >= META_P95_S}
    assert not acima, f"p95 acima de {META_P95_S * 1000:.0f} ms: {acima}"


async def test_consultas_de_indicadores_usam_indices(
    cliente: httpx.AsyncClient, usuario: UsuarioTeste, banco_migrado: str
) -> None:
    popular(banco_migrado, str(usuario.id))
    consultas = {
        "totais do mês": (
            "SELECT tipo, COALESCE(SUM(valor), 0) FROM "
            "movimentacao_financeira WHERE usuario_id = %s AND "
            "excluida_em IS NULL AND data_movimentacao BETWEEN "
            "'2026-10-01' AND '2026-10-31' GROUP BY tipo"
        ),
        "atividades do dia": (
            "SELECT count(*) FROM atividade WHERE usuario_id = %s "
            "AND excluida_em IS NULL AND data_atividade = '2026-10-13'"
        ),
        "pendências anteriores": (
            "SELECT count(*), min(data_atividade) FROM atividade WHERE "
            "usuario_id = %s AND excluida_em IS NULL AND "
            "concluida_em IS NULL AND data_atividade < '2026-10-13'"
        ),
        "importâncias do período": (
            "SELECT count(*) FROM importancia WHERE usuario_id = %s AND "
            "excluida_em IS NULL AND data_compromisso BETWEEN "
            "'2026-10-01' AND '2026-10-31'"
        ),
    }
    with psycopg.connect(url_libpq(banco_migrado)) as c:
        for nome, sql in consultas.items():
            linhas = c.execute(
                "EXPLAIN (ANALYZE, BUFFERS) " + sql,  # pyright: ignore[reportArgumentType]
                (str(usuario.id),),
            ).fetchall()
            plano = "\n".join(linha[0] for linha in linhas)
            print(f"--- {nome}\n{plano}")  # noqa: T201
            tempo = float(plano.rsplit("Execution Time: ", 1)[1].split()[0])
            assert tempo < 50, f"{nome}: {tempo} ms"
