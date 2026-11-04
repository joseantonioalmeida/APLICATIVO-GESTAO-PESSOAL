"""Processador de lembretes: materialização antecipada e notificações.

Dono das próprias transações (uma por série e uma por lembrete), ao
contrário dos demais services. Ver arquitetura §8.6.3 e DEC-MV-20.
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api_gestao_pessoal.models import (
    Importancia,
    LembreteImportancia,
    Notificacao,
    SerieImportancia,
    Usuario,
)
from api_gestao_pessoal.models.enums import SituacaoLembrete
from api_gestao_pessoal.services import importancias
from api_gestao_pessoal.services.situacao_importancia import (
    Movimentacao,
    concluida,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import ContextoUsuario, hoje_no_fuso

logger = logging.getLogger("api_gestao_pessoal.lembretes")


@dataclass(slots=True)
class ResultadoCiclo:
    """Contadores de um ciclo do processador."""

    ocorrencias_materializadas: int = 0
    enviados: int = 0
    cancelados: int = 0
    falhas: int = 0
    falhos: set[uuid.UUID] = field(default_factory=set)


def formatar_reais(valor: Decimal) -> str:
    """`Decimal("1234.5")` -> `"R$ 1.234,50"`."""
    texto = f"{valor.quantize(Decimal('0.01')):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def descrever_prazo(dias: int) -> str:
    """`hoje`, `amanhã` ou `em X dias`."""
    if dias <= 0:
        return "hoje"
    if dias == 1:
        return "amanhã"
    return f"em {dias} dias"


def montar_titulo(nome: str) -> str:
    """Título congelado no envio (§8.6.4)."""
    return f"Lembrete: {nome}"


def montar_mensagem(importancia: Importancia, hoje: date) -> str:
    """Mensagem congelada no envio (§8.6.4)."""
    quando = importancia.data_compromisso.strftime("%d/%m/%Y")
    if importancia.horario is not None:
        quando += f" às {importancia.horario.strftime('%H:%M')}"
    prazo = descrever_prazo((importancia.data_compromisso - hoje).days)
    texto = f"{importancia.nome} — {prazo} ({quando})."
    if importancia.possui_despesa and importancia.valor_previsto is not None:
        texto += (
            f" Valor previsto: {formatar_reais(importancia.valor_previsto)}."
        )
    return texto


async def _materializar_antecipado(
    fabrica: async_sessionmaker[AsyncSession],
    agora: datetime,
    janela_dias: int,
    resultado: ResultadoCiclo,
) -> None:
    """Etapa 1: uma transação por série com lembrete."""
    async with fabrica() as sessao:
        alvos = (
            await sessao.execute(
                select(
                    SerieImportancia.id,
                    SerieImportancia.usuario_id,
                    Usuario.fuso_horario,
                )
                .join(Usuario, Usuario.id == SerieImportancia.usuario_id)
                .where(
                    SerieImportancia.lembrete_antecedencia_dias.is_not(None)
                )
                .order_by(SerieImportancia.id)
            )
        ).all()
    for serie_id, usuario_id, nome_fuso in alvos:
        try:
            resultado.ocorrencias_materializadas += await _materializar_serie(
                fabrica, agora, janela_dias, (serie_id, usuario_id, nome_fuso)
            )
        except Exception:
            resultado.falhas += 1
            logger.exception("falha ao materializar a série %s", serie_id)


async def _materializar_serie(
    fabrica: async_sessionmaker[AsyncSession],
    agora: datetime,
    janela_dias: int,
    alvo: tuple[uuid.UUID, uuid.UUID, str],
) -> int:
    serie_id, usuario_id, nome_fuso = alvo
    fuso = ZoneInfo(nome_fuso)
    hoje = hoje_no_fuso(agora, fuso)
    contexto = ContextoUsuario(usuario_id, fuso, agora, hoje)
    async with fabrica() as sessao:
        await travar_usuario(sessao, usuario_id, ModoTrava.EXCLUSIVA)
        criadas = await importancias.materializar_janela_da_serie(
            sessao,
            contexto,
            serie_id,
            hoje,
            hoje + timedelta(days=janela_dias),
        )
        await sessao.commit()
    return criadas


async def _atualizar_condicional(  # noqa: PLR0913
    sessao: AsyncSession,
    lembrete: LembreteImportancia,
    *,
    para: SituacaoLembrete,
    agora: datetime,
) -> int:
    valores: dict[str, object] = {"situacao": para}
    if para == SituacaoLembrete.ENVIADO:
        valores["enviado_em"] = agora
    resultado = await sessao.execute(
        update(LembreteImportancia)
        .where(
            LembreteImportancia.id == lembrete.id,
            LembreteImportancia.situacao == SituacaoLembrete.PENDENTE,
            LembreteImportancia.versao_agendamento
            == lembrete.versao_agendamento,
        )
        .values(**valores)
    )
    return int(resultado.rowcount or 0)  # pyright: ignore[reportAttributeAccessIssue]


async def _processar(
    sessao: AsyncSession, lembrete: LembreteImportancia, agora: datetime
) -> SituacaoLembrete:
    """Processa um lembrete já travado; devolve o estado final."""
    linha = (
        await sessao.execute(
            select(Importancia, Usuario.fuso_horario, concluida())
            .join(Usuario, Usuario.id == Importancia.usuario_id)
            .outerjoin(
                Movimentacao, Movimentacao.importancia_id == Importancia.id
            )
            .where(Importancia.id == lembrete.importancia_id)
        )
    ).one()
    importancia, nome_fuso, esta_concluida = linha
    hoje = hoje_no_fuso(agora, ZoneInfo(nome_fuso))
    if (
        importancia.excluida_em is not None
        or esta_concluida
        or importancia.data_compromisso < hoje
    ):
        await _atualizar_condicional(
            sessao, lembrete, para=SituacaoLembrete.CANCELADO, agora=agora
        )
        return SituacaoLembrete.CANCELADO
    await sessao.execute(
        pg_insert(Notificacao)
        .values(
            id=uuid.uuid7(),
            usuario_id=lembrete.usuario_id,
            lembrete_id=lembrete.id,
            versao_agendamento=lembrete.versao_agendamento,
            titulo=montar_titulo(importancia.nome),
            mensagem=montar_mensagem(importancia, hoje),
        )
        .on_conflict_do_nothing(
            index_elements=["lembrete_id", "versao_agendamento"]
        )
    )
    linhas = await _atualizar_condicional(
        sessao, lembrete, para=SituacaoLembrete.ENVIADO, agora=agora
    )
    if linhas != 1:
        msg = "lembrete alterado durante o processamento"
        raise RuntimeError(msg)
    return SituacaoLembrete.ENVIADO


async def _processar_lembretes_vencidos(
    fabrica: async_sessionmaker[AsyncSession],
    agora: datetime,
    lote: int,
    resultado: ResultadoCiclo,
) -> None:
    """Etapa 2: uma transação por lembrete, com `SKIP LOCKED`."""
    for _ in range(lote):
        async with fabrica() as sessao:
            consulta = (
                select(LembreteImportancia)
                .where(
                    LembreteImportancia.situacao == SituacaoLembrete.PENDENTE,
                    LembreteImportancia.agendado_para <= agora,
                )
                .order_by(
                    LembreteImportancia.agendado_para, LembreteImportancia.id
                )
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if resultado.falhos:
                consulta = consulta.where(
                    LembreteImportancia.id.not_in(resultado.falhos)
                )
            lembrete = await sessao.scalar(consulta)
            if lembrete is None:
                return
            lembrete_id = lembrete.id
            try:
                final = await _processar(sessao, lembrete, agora)
                await sessao.commit()
            except Exception:
                await sessao.rollback()
                resultado.falhos.add(lembrete_id)
                resultado.falhas += 1
                logger.exception(
                    "falha ao processar o lembrete %s", lembrete_id
                )
                continue
            if final == SituacaoLembrete.ENVIADO:
                resultado.enviados += 1
            else:
                resultado.cancelados += 1


async def executar_ciclo(
    fabrica: async_sessionmaker[AsyncSession],
    relogio: Callable[[], datetime],
    *,
    lote: int,
    janela_dias: int,
) -> ResultadoCiclo:
    """Um ciclo completo: materialização antecipada e envio."""
    agora = relogio()
    resultado = ResultadoCiclo()
    await _materializar_antecipado(fabrica, agora, janela_dias, resultado)
    await _processar_lembretes_vencidos(fabrica, agora, lote, resultado)
    return resultado
