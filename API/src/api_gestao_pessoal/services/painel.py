"""Painel inicial (§8.10): só compõe funções dos demais services.

Nenhuma regra de negócio própria: cada bloco chama as mesmas funções das
telas de Atividades, Financeiro e Importâncias, o que garante os mesmos
números nas duas telas (4.2.2).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.schemas.painel import (
    DiaSemana,
    PainelAtividadesHoje,
    PainelFinanceiro,
    PainelImportancias,
    TotaisDia,
    TotaisMes,
)
from api_gestao_pessoal.services import (
    atividades,
    importancias,
    resumo_financeiro,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import (
    ContextoUsuario,
    primeiro_dia_mes,
    ultimo_dia_do_mes,
)

DIAS_DA_SEMANA = (
    DiaSemana.SEGUNDA,
    DiaSemana.TERCA,
    DiaSemana.QUARTA,
    DiaSemana.QUINTA,
    DiaSemana.SEXTA,
    DiaSemana.SABADO,
    DiaSemana.DOMINGO,
)


def _mes_texto(contexto: ContextoUsuario) -> str:
    return f"{contexto.hoje.year:04d}-{contexto.hoje.month:02d}"


async def atividades_de_hoje(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> PainelAtividadesHoje:
    """Prévia, totais do dia e pendências anteriores (4.1.4)."""
    total, concluidas, previa = await atividades.resumo_do_dia(
        sessao, contexto
    )
    pendencias = await atividades.pendencias_anteriores(sessao, contexto)
    return PainelAtividadesHoje(
        hoje=contexto.hoje,
        dia_semana=DIAS_DA_SEMANA[contexto.hoje.weekday()],
        total=total,
        concluidas=concluidas,
        previa=previa,
        pendencias_anteriores=pendencias,
    )


async def financeiro(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> PainelFinanceiro:
    """Indicadores do mês, resumo do dia e movimentações (4.1.2, 4.1.5)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    inicio = primeiro_dia_mes(contexto.hoje)
    fim = ultimo_dia_do_mes(contexto.hoje)
    rec_mes, des_mes = await resumo_financeiro.totais_periodo(
        sessao, contexto.usuario_id, inicio, fim
    )
    rec_dia, des_dia = await resumo_financeiro.totais_periodo(
        sessao, contexto.usuario_id, contexto.hoje, contexto.hoje
    )
    comparacoes = await resumo_financeiro.comparacoes(sessao, contexto, inicio)
    recentes = await resumo_financeiro.ultimas_movimentacoes(
        sessao, contexto.usuario_id, inicio, fim
    )
    return PainelFinanceiro(
        hoje=contexto.hoje,
        mes_referencia=_mes_texto(contexto),
        mes=TotaisMes(
            receitas=rec_mes,
            despesas=des_mes,
            saldo=rec_mes - des_mes,
            comparacao_despesas=comparacoes.despesas,
        ),
        dia=TotaisDia(
            receitas=rec_dia, despesas=des_dia, saldo=rec_dia - des_dia
        ),
        movimentacoes_recentes=recentes,
    )


async def importancias_do_painel(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> PainelImportancias:
    """Pendentes do mês, três próximas e atrasadas (4.1.2, 4.1.8)."""
    resumo = await importancias.resumo_painel(sessao, contexto)
    return PainelImportancias(
        hoje=contexto.hoje,
        mes_referencia=_mes_texto(contexto),
        pendentes_mes=resumo.pendentes_mes,
        proximas=resumo.proximas,
        atrasadas_quantidade=resumo.atrasadas_quantidade,
    )
