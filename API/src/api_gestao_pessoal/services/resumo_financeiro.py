"""Totais, comparações e resumo mensal (arquitetura §8.8)."""

import calendar
import uuid
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.models import CategoriaFinanceira
from api_gestao_pessoal.models import MovimentacaoFinanceira as Mov
from api_gestao_pessoal.models.enums import TipoMovimentacao
from api_gestao_pessoal.schemas.atividade import CategoriaRef
from api_gestao_pessoal.schemas.financeiro import (
    CategoriaDespesaTotal,
    Comparacao,
    ComparacoesResposta,
    DiaGrafico,
    Intervalo,
    MovimentacaoItem,
    ResumoFinanceiroResposta,
    Tendencia,
)
from api_gestao_pessoal.services.consulta_movimentacoes import (
    consulta_base,
    montar_item,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import (
    ContextoUsuario,
    mes_anterior,
    primeiro_dia_mes,
    ultimo_dia_do_mes,
)

ZERO = Decimal("0.00")
CEM = Decimal(100)
UMA_CASA = Decimal("0.1")
LIMITE_ULTIMAS = 5


async def totais_periodo(
    sessao: AsyncSession, usuario_id: uuid.UUID, inicio: date, fim: date
) -> tuple[Decimal, Decimal]:
    """`(receitas, despesas)` do período `[inicio, fim]`, sem exclusões."""
    linhas = (
        await sessao.execute(
            select(Mov.tipo, func.coalesce(func.sum(Mov.valor), 0))
            .where(
                Mov.usuario_id == usuario_id,
                Mov.excluida_em.is_(None),
                Mov.data_movimentacao.between(inicio, fim),
            )
            .group_by(Mov.tipo)
        )
    ).all()
    totais = {tipo: Decimal(total) for tipo, total in linhas}
    return (
        totais.get(TipoMovimentacao.RECEITA, ZERO),
        totais.get(TipoMovimentacao.DESPESA, ZERO),
    )


def intervalos_comparacao(
    mes: date, hoje: date
) -> tuple[Intervalo, Intervalo] | None:
    """Intervalos comparáveis (9.2.6); `None` para meses futuros."""
    mes = primeiro_dia_mes(mes)
    atual_mes = primeiro_dia_mes(hoje)
    if mes > atual_mes:
        return None
    anterior = mes_anterior(mes)
    if mes < atual_mes:
        return (
            Intervalo(inicio=mes, fim=ultimo_dia_do_mes(mes)),
            Intervalo(inicio=anterior, fim=ultimo_dia_do_mes(anterior)),
        )
    fim_anterior = anterior.replace(
        day=min(hoje.day, ultimo_dia_do_mes(anterior).day)
    )
    return (
        Intervalo(inicio=mes, fim=hoje),
        Intervalo(inicio=anterior, fim=fim_anterior),
    )


def comparar(
    atual: Decimal,
    anterior: Decimal,
    intervalos: tuple[Intervalo, Intervalo] | None,
) -> Comparacao:
    """Variação percentual com 1 casa (`ROUND_HALF_UP`), sem dividir por 0."""
    intervalo_atual = intervalos[0] if intervalos else None
    intervalo_anterior = intervalos[1] if intervalos else None
    base = {
        "intervalo_atual": intervalo_atual,
        "intervalo_anterior": intervalo_anterior,
        "total_atual": atual,
        "total_anterior": anterior,
    }
    if intervalos is None:
        return Comparacao(
            **base, variacao_percentual=None, tendencia=Tendencia.NAO_APLICAVEL
        )
    if anterior > 0:
        bruta = (atual - anterior) / anterior * CEM
        if bruta > 0:
            tendencia = Tendencia.AUMENTO
        elif bruta < 0:
            tendencia = Tendencia.REDUCAO
        else:
            tendencia = Tendencia.ESTABILIDADE
        variacao = bruta.quantize(UMA_CASA, ROUND_HALF_UP)
        return Comparacao(
            **base,
            variacao_percentual=format(variacao, "f"),
            tendencia=tendencia,
        )
    tendencia = Tendencia.SEM_BASE if atual > 0 else Tendencia.SEM_MOVIMENTACAO
    return Comparacao(**base, variacao_percentual=None, tendencia=tendencia)


async def comparacoes(
    sessao: AsyncSession, contexto: ContextoUsuario, mes: date
) -> ComparacoesResposta:
    intervalos = intervalos_comparacao(mes, contexto.hoje)
    if intervalos is None:
        return ComparacoesResposta(
            receitas=comparar(ZERO, ZERO, None),
            despesas=comparar(ZERO, ZERO, None),
        )
    atual, anterior = intervalos
    rec_a, des_a = await totais_periodo(
        sessao, contexto.usuario_id, atual.inicio, atual.fim
    )
    rec_b, des_b = await totais_periodo(
        sessao, contexto.usuario_id, anterior.inicio, anterior.fim
    )
    return ComparacoesResposta(
        receitas=comparar(rec_a, rec_b, intervalos),
        despesas=comparar(des_a, des_b, intervalos),
    )


async def _grafico_diario(
    sessao: AsyncSession, usuario_id: uuid.UUID, inicio: date, fim: date
) -> list[DiaGrafico]:
    linhas = (
        await sessao.execute(
            select(Mov.data_movimentacao, Mov.tipo, func.sum(Mov.valor))
            .where(
                Mov.usuario_id == usuario_id,
                Mov.excluida_em.is_(None),
                Mov.data_movimentacao.between(inicio, fim),
            )
            .group_by(Mov.data_movimentacao, Mov.tipo)
        )
    ).all()
    por_dia = {(dia, tipo): Decimal(total) for dia, tipo, total in linhas}
    dias_do_mes = calendar.monthrange(inicio.year, inicio.month)[1]
    grafico: list[DiaGrafico] = []
    for n in range(dias_do_mes):
        dia = inicio + timedelta(days=n)
        grafico.append(
            DiaGrafico(
                data=dia,
                receitas=por_dia.get((dia, TipoMovimentacao.RECEITA), ZERO),
                despesas=por_dia.get((dia, TipoMovimentacao.DESPESA), ZERO),
            )
        )
    return grafico


async def _categorias_de_despesa(
    sessao: AsyncSession, usuario_id: uuid.UUID, inicio: date, fim: date
) -> list[CategoriaDespesaTotal]:
    total = func.sum(Mov.valor)
    linhas = (
        await sessao.execute(
            select(CategoriaFinanceira.id, CategoriaFinanceira.nome, total)
            .join(
                CategoriaFinanceira, CategoriaFinanceira.id == Mov.categoria_id
            )
            .where(
                Mov.usuario_id == usuario_id,
                Mov.excluida_em.is_(None),
                Mov.tipo == TipoMovimentacao.DESPESA,
                Mov.data_movimentacao.between(inicio, fim),
            )
            .group_by(CategoriaFinanceira.id, CategoriaFinanceira.nome)
            .having(total > 0)
            .order_by(total.desc(), CategoriaFinanceira.nome)
        )
    ).all()
    return [
        CategoriaDespesaTotal(
            categoria=CategoriaRef(id=cid, nome=nome), total=Decimal(soma)
        )
        for cid, nome, soma in linhas
    ]


async def ultimas_movimentacoes(
    sessao: AsyncSession, usuario_id: uuid.UUID, inicio: date, fim: date
) -> list[MovimentacaoItem]:
    """Até cinco movimentações do período, da mais recente à mais antiga."""
    linhas = (
        await sessao.execute(
            consulta_base()
            .where(
                Mov.usuario_id == usuario_id,
                Mov.excluida_em.is_(None),
                Mov.data_movimentacao.between(inicio, fim),
            )
            .order_by(
                Mov.data_movimentacao.desc(),
                Mov.criado_em.desc(),
                Mov.id.desc(),
            )
            .limit(LIMITE_ULTIMAS)
        )
    ).all()
    return [montar_item(linha) for linha in linhas]


async def resumo(
    sessao: AsyncSession, contexto: ContextoUsuario, mes: date
) -> ResumoFinanceiroResposta:
    """Resumo do mês: totais, comparação, gráfico e categorias."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    inicio = primeiro_dia_mes(mes)
    fim = ultimo_dia_do_mes(mes)
    receitas, despesas = await totais_periodo(
        sessao, contexto.usuario_id, inicio, fim
    )
    return ResumoFinanceiroResposta(
        mes=f"{inicio.year:04d}-{inicio.month:02d}",
        periodo=Intervalo(inicio=inicio, fim=fim),
        receitas=receitas,
        despesas=despesas,
        saldo=receitas - despesas,
        comparacao=await comparacoes(sessao, contexto, inicio),
        grafico_diario=await _grafico_diario(
            sessao, contexto.usuario_id, inicio, fim
        ),
        categorias_despesa=await _categorias_de_despesa(
            sessao, contexto.usuario_id, inicio, fim
        ),
        ultimas_movimentacoes=await ultimas_movimentacoes(
            sessao, contexto.usuario_id, inicio, fim
        ),
    )
