"""CT-F9: processador de lembretes (arquitetura §8.6.3)."""

import asyncio
from datetime import timedelta
from http import HTTPStatus

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api_gestao_pessoal.jobs.processar_lembretes import executar
from api_gestao_pessoal.services import processamento_lembretes
from api_gestao_pessoal.settings import Settings

from ..apoio.api import UsuarioTeste
from ..apoio.relogio import RelogioFixo
from ..importancias.util import criar, lembretes_no_banco, situacao
from .util import ciclo, consultar, notificacoes_no_banco

LEMBRETE_3_DIAS = {"antecedencia_dias": 3, "horario": "09:00"}


async def test_nada_antes_da_hora(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    # Compromisso em 20/10, lembrete em 17/10 09:00 (hoje é 13/10).
    await criar(cliente, usuario, lembrete=LEMBRETE_3_DIAS)
    resultado = await ciclo(fabrica, relogio)
    assert (resultado.enviados, resultado.cancelados) == (0, 0)
    assert notificacoes_no_banco(banco_migrado) == []


async def test_envia_na_hora_com_conteudo_congelado(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    imp = await criar(
        cliente,
        usuario,
        possui_despesa=True,
        valor_previsto="1234.50",
        horario="14:30",
        lembrete=LEMBRETE_3_DIAS,
    )
    relogio.avancar(timedelta(days=4))  # 17/10 09:00 em São Paulo
    resultado = await ciclo(fabrica, relogio)
    assert resultado.enviados == 1
    assert notificacoes_no_banco(banco_migrado) == [
        (
            "Lembrete: Pagamento da internet",
            "Pagamento da internet — em 3 dias (20/10/2026 às 14:30). "
            "Valor previsto: R$ 1.234,50.",
            1,
        )
    ]
    situacao_lembrete = lembretes_no_banco(banco_migrado, imp["id"])[0]
    assert situacao_lembrete[0] == "ENVIADO"
    assert situacao_lembrete[3] is not None


async def test_segundo_ciclo_nao_duplica(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    await criar(cliente, usuario, lembrete=LEMBRETE_3_DIAS)
    relogio.avancar(timedelta(days=4))
    await ciclo(fabrica, relogio)
    resultado = await ciclo(fabrica, relogio)
    assert resultado.enviados == 0
    assert len(notificacoes_no_banco(banco_migrado)) == 1


async def test_sem_data_de_despesa_mensagem_simples(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    await criar(
        cliente,
        usuario,
        data_compromisso="2026-10-14",
        lembrete={"antecedencia_dias": 1, "horario": "20:00"},
    )
    relogio.avancar(timedelta(hours=9))  # 13/10 18:00 -> ainda antes
    assert (await ciclo(fabrica, relogio)).enviados == 0
    relogio.avancar(timedelta(hours=3))  # 13/10 21:00 SP (>= 20:00)
    assert (await ciclo(fabrica, relogio)).enviados == 1
    assert notificacoes_no_banco(banco_migrado)[0][1] == (
        "Pagamento da internet — amanhã (14/10/2026)."
    )


async def test_concluida_cancela_sem_notificar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    imp = await criar(cliente, usuario, lembrete=LEMBRETE_3_DIAS)
    r = await situacao(cliente, usuario, imp["id"], "CONCLUIDA")
    assert r.status_code == HTTPStatus.OK
    relogio.avancar(timedelta(days=4))
    await ciclo(fabrica, relogio)
    assert notificacoes_no_banco(banco_migrado) == []
    assert lembretes_no_banco(banco_migrado, imp["id"])[0][0] == "CANCELADO"


async def test_compromisso_vencido_vira_cancelado_sem_notificar(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    """DEC-MV-20: processador parado; a data do compromisso já passou."""
    imp = await criar(cliente, usuario, lembrete=LEMBRETE_3_DIAS)
    relogio.avancar(timedelta(days=9))  # 22/10, compromisso era 20/10
    resultado = await ciclo(fabrica, relogio)
    assert (resultado.enviados, resultado.cancelados) == (0, 1)
    assert notificacoes_no_banco(banco_migrado) == []
    assert lembretes_no_banco(banco_migrado, imp["id"])[0][0] == "CANCELADO"


async def test_atraso_do_processador_ainda_notifica(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    """Lembrete vencido, mas compromisso ainda não passou: notifica."""
    await criar(cliente, usuario, lembrete=LEMBRETE_3_DIAS)
    relogio.avancar(timedelta(days=6))  # 19/10, lembrete era 17/10
    assert (await ciclo(fabrica, relogio)).enviados == 1
    assert "em 1 dia" not in notificacoes_no_banco(banco_migrado)[0][1]
    assert "amanhã" in notificacoes_no_banco(banco_migrado)[0][1]


async def test_reagendar_gera_nova_versao_e_nova_notificacao(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    imp = await criar(cliente, usuario, lembrete=LEMBRETE_3_DIAS)
    relogio.avancar(timedelta(days=4))
    await ciclo(fabrica, relogio)
    relogio.avancar(-timedelta(days=4))  # o token do usuário expiraria
    r = await cliente.patch(
        f"/api/v1/importancias/{imp['id']}",
        json={"data_compromisso": "2026-10-22"},
        headers=usuario.cabecalhos,
    )
    assert r.status_code == HTTPStatus.OK, r.text
    # Novo agendamento: 19/10 09:00. Ainda não é hora.
    relogio.avancar(timedelta(days=4))  # 17/10
    assert (await ciclo(fabrica, relogio)).enviados == 0
    relogio.avancar(timedelta(days=2))
    assert (await ciclo(fabrica, relogio)).enviados == 1
    versoes = [n[2] for n in notificacoes_no_banco(banco_migrado)]
    assert versoes == [1, 2]


async def test_serie_materializa_janela_antecipada(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    await criar(
        cliente,
        usuario,
        data_compromisso="2026-10-14",
        repeticao={"periodicidade": "DIARIA"},
        lembrete={"antecedencia_dias": 0, "horario": "09:00"},
    )
    antes = consultar(banco_migrado, "SELECT count(*) FROM importancia")[0][0]
    resultado = await ciclo(fabrica, relogio, janela_dias=8)
    depois = consultar(banco_migrado, "SELECT count(*) FROM importancia")[0][0]
    # Datas 14/10 a 21/10 (hoje + 8): 8 ocorrências; a 1ª já existia.
    assert depois == 8
    assert resultado.ocorrencias_materializadas == depois - antes
    lembretes = consultar(
        banco_migrado,
        "SELECT count(*) FROM lembrete_importancia WHERE situacao='PENDENTE'",
    )[0][0]
    assert lembretes == 8
    # Repetir o ciclo não cria nada.
    assert (await ciclo(fabrica, relogio)).ocorrencias_materializadas == 0


async def test_falha_isolada_por_item(  # noqa: PLR0913, PLR0917
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await criar(
        cliente, usuario, nome="Item com defeito", lembrete=LEMBRETE_3_DIAS
    )
    await criar(
        cliente, usuario, nome="Item correto", lembrete=LEMBRETE_3_DIAS
    )
    original = processamento_lembretes.montar_titulo

    def defeituoso(nome: str) -> str:
        if "defeito" in nome:
            msg = "falha injetada"
            raise RuntimeError(msg)
        return original(nome)

    monkeypatch.setattr(processamento_lembretes, "montar_titulo", defeituoso)
    relogio.avancar(timedelta(days=4))
    resultado = await ciclo(fabrica, relogio)
    assert (resultado.enviados, resultado.falhas) == (1, 1)
    assert [n[0] for n in notificacoes_no_banco(banco_migrado)] == [
        "Lembrete: Item correto"
    ]
    # O item com defeito continua PENDENTE (sem estado parcial).
    pendentes = consultar(
        banco_migrado,
        "SELECT count(*) FROM lembrete_importancia WHERE situacao='PENDENTE'",
    )[0][0]
    assert pendentes == 1


async def test_ciclos_concorrentes_geram_uma_notificacao(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    for i in range(5):
        await criar(
            cliente,
            usuario,
            nome=f"Conta numero {i}",
            lembrete=LEMBRETE_3_DIAS,
        )
    relogio.avancar(timedelta(days=4))
    resultados = await asyncio.gather(
        ciclo(fabrica, relogio),
        ciclo(fabrica, relogio),
        ciclo(fabrica, relogio),
    )
    assert sum(r.enviados for r in resultados) == 5
    assert len(notificacoes_no_banco(banco_migrado)) == 5


async def test_lote_limita_itens_por_ciclo(
    cliente: httpx.AsyncClient,
    usuario: UsuarioTeste,
    fabrica: async_sessionmaker[AsyncSession],
    relogio: RelogioFixo,
    banco_migrado: str,
) -> None:
    for i in range(3):
        await criar(
            cliente,
            usuario,
            nome=f"Conta numero {i}",
            lembrete=LEMBRETE_3_DIAS,
        )
    relogio.avancar(timedelta(days=4))
    assert (await ciclo(fabrica, relogio, lote=2)).enviados == 2
    assert (await ciclo(fabrica, relogio, lote=2)).enviados == 1


def test_formatacao_em_reais() -> None:
    from decimal import Decimal  # noqa: PLC0415

    f = processamento_lembretes.formatar_reais
    assert f(Decimal("1220.35")) == "R$ 1.220,35"
    assert f(Decimal("0.1")) == "R$ 0,10"
    assert f(Decimal("1234567.8")) == "R$ 1.234.567,80"


async def test_job_uma_vez_termina_sem_falhas(
    settings_teste: Settings, banco_migrado: str
) -> None:
    resultado = await executar(settings_teste, uma_vez=True)
    assert resultado.falhas == 0
