"""Agendamento e ciclo de vida dos lembretes de importâncias (§8.6).

O envio de notificações é responsabilidade do processador (F9); aqui só se
mantém a configuração e a situação da versão corrente de cada lembrete.
"""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.models import Importancia, LembreteImportancia
from api_gestao_pessoal.models.enums import SituacaoLembrete
from api_gestao_pessoal.tempo import ContextoUsuario, instante_local


@dataclass(frozen=True, slots=True)
class ConfigLembrete:
    """Antecedência (0, 1, 3 ou 7 dias) e horário do lembrete."""

    antecedencia_dias: int
    horario: time


def calcular_agendamento(
    data_compromisso: date, config: ConfigLembrete, fuso: ZoneInfo
) -> datetime:
    """Instante UTC do lembrete (8.6.5)."""
    dia = data_compromisso - timedelta(days=config.antecedencia_dias)
    return instante_local(dia, config.horario, fuso)


async def obter(
    sessao: AsyncSession, importancia_id: uuid.UUID
) -> LembreteImportancia | None:
    """Lembrete (versão corrente) de uma importância."""
    return await sessao.scalar(
        select(LembreteImportancia).where(
            LembreteImportancia.importancia_id == importancia_id
        )
    )


def config_de(lembrete: LembreteImportancia | None) -> ConfigLembrete | None:
    """Configuração do lembrete, se houver e não estiver desativado."""
    if lembrete is None or lembrete.situacao == SituacaoLembrete.DESATIVADO:
        return None
    return ConfigLembrete(lembrete.antecedencia_dias, lembrete.horario)


async def reagendar(
    sessao: AsyncSession,
    importancia: Importancia,
    config: ConfigLembrete | None,
    contexto: ContextoUsuario,
    *,
    pendente: bool,
) -> None:
    """Aplica a configuração desejada à importância (§8.6.2).

    `config=None` desativa. Valores iguais não criam nova versão.
    """
    atual = await obter(sessao, importancia.id)
    if config is None:
        if atual is not None and atual.situacao != SituacaoLembrete.DESATIVADO:
            atual.situacao = SituacaoLembrete.DESATIVADO
            atual.enviado_em = None
        return
    novo = calcular_agendamento(
        importancia.data_compromisso, config, contexto.fuso
    )
    ativo = pendente and novo > contexto.agora
    situacao = (
        SituacaoLembrete.PENDENTE if ativo else SituacaoLembrete.CANCELADO
    )
    if atual is None:
        sessao.add(
            LembreteImportancia(
                usuario_id=importancia.usuario_id,
                importancia_id=importancia.id,
                antecedencia_dias=config.antecedencia_dias,
                horario=config.horario,
                agendado_para=novo,
                versao_agendamento=1,
                situacao=situacao,
            )
        )
        return
    igual = (
        atual.antecedencia_dias == config.antecedencia_dias
        and atual.horario == config.horario
        and atual.agendado_para == novo
        and atual.situacao != SituacaoLembrete.DESATIVADO
    )
    if igual:
        return
    atual.antecedencia_dias = config.antecedencia_dias
    atual.horario = config.horario
    atual.agendado_para = novo
    atual.versao_agendamento += 1
    atual.enviado_em = None
    atual.situacao = situacao


async def cancelar_pendente(
    sessao: AsyncSession, importancia_id: uuid.UUID
) -> None:
    """Concluir ou excluir: `PENDENTE` vira `CANCELADO` (mesma versão)."""
    await sessao.execute(
        update(LembreteImportancia)
        .where(
            LembreteImportancia.importancia_id == importancia_id,
            LembreteImportancia.situacao == SituacaoLembrete.PENDENTE,
        )
        .values(situacao=SituacaoLembrete.CANCELADO)
    )


async def ao_reabrir_importancia(
    sessao: AsyncSession, importancia_id: uuid.UUID, agora: datetime
) -> None:
    """Reabertura: `CANCELADO` com horário futuro volta a `PENDENTE`.

    `ENVIADO`, `DESATIVADO` e lembretes já vencidos não mudam.
    """
    await sessao.execute(
        update(LembreteImportancia)
        .where(
            LembreteImportancia.importancia_id == importancia_id,
            LembreteImportancia.situacao == SituacaoLembrete.CANCELADO,
            LembreteImportancia.agendado_para > agora,
        )
        .values(situacao=SituacaoLembrete.PENDENTE)
    )
