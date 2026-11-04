"""Schemas do painel inicial (arquitetura §9.7)."""

import enum
from datetime import date

from pydantic import BaseModel

from api_gestao_pessoal.schemas.atividade import (
    AtividadeItem,
    PendenciasAnterioresResposta,
)
from api_gestao_pessoal.schemas.comum import DinheiroSaida
from api_gestao_pessoal.schemas.financeiro import Comparacao, MovimentacaoItem
from api_gestao_pessoal.schemas.importancia import ImportanciaItem


class DiaSemana(enum.StrEnum):
    """Dia da semana de hoje, calculado a partir da data (4.1.3)."""

    SEGUNDA = "SEGUNDA"
    TERCA = "TERCA"
    QUARTA = "QUARTA"
    QUINTA = "QUINTA"
    SEXTA = "SEXTA"
    SABADO = "SABADO"
    DOMINGO = "DOMINGO"


class PainelAtividadesHoje(BaseModel):
    """Bloco “Atividades de hoje”."""

    hoje: date
    dia_semana: DiaSemana
    total: int
    concluidas: int
    previa: list[AtividadeItem]
    pendencias_anteriores: PendenciasAnterioresResposta


class TotaisMes(BaseModel):
    """Indicadores do mês atual."""

    receitas: DinheiroSaida
    despesas: DinheiroSaida
    saldo: DinheiroSaida
    comparacao_despesas: Comparacao


class TotaisDia(BaseModel):
    """Resumo financeiro de hoje."""

    receitas: DinheiroSaida
    despesas: DinheiroSaida
    saldo: DinheiroSaida


class PainelFinanceiro(BaseModel):
    """Blocos financeiros (mês, dia e movimentações recentes)."""

    hoje: date
    mes_referencia: str
    mes: TotaisMes
    dia: TotaisDia
    movimentacoes_recentes: list[MovimentacaoItem]


class PainelImportancias(BaseModel):
    """Bloco “Próximas importâncias” e aviso de atrasos."""

    hoje: date
    mes_referencia: str
    pendentes_mes: int
    proximas: list[ImportanciaItem]
    atrasadas_quantidade: int
