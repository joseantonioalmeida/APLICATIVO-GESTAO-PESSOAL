"""Recorrência: cálculo puro e materialização genérica (arquitetura §8.5).

As funções de cálculo não acessam o banco. A materialização insere as
ocorrências faltantes de uma série, sempre sob a trava EXCLUSIVA do
usuário (I-REC-4) e com `ON CONFLICT DO NOTHING` (I-REC-2).
"""

import calendar
import uuid
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

NENHUMA = "NENHUMA"
DIARIA = "DIARIA"
SEMANAL = "SEMANAL"
MENSAL = "MENSAL"
ANUAL = "ANUAL"
TAMANHO_BLOCO = 500


@dataclass(frozen=True, slots=True)
class RegraSerie:
    """Regra vigente de uma série (valores já persistidos ou propostos)."""

    periodicidade: str
    data_referencia: date
    numero_referencia: int
    data_final_repeticao: date | None = None
    numero_final: int | None = None


def bissexto(ano: int) -> bool:
    """Ano bissexto no calendário gregoriano."""
    return calendar.isleap(ano)


def ultimo_dia_mes(ano: int, mes: int) -> int:
    """Último dia do mês."""
    return calendar.monthrange(ano, mes)[1]


def somar_meses(ano: int, mes: int, k: int) -> tuple[int, int]:
    """Ano e mês resultantes de somar `k` meses."""
    indice = ano * 12 + (mes - 1) + k
    return indice // 12, indice % 12 + 1


def _data_deslocada(regra: RegraSerie, k: int) -> date | None:
    """Data da posição `r + k`, com `k >= 0`."""
    ref = regra.data_referencia
    match regra.periodicidade:
        case "NENHUMA":
            return ref if k == 0 else None
        case "DIARIA":
            return ref + timedelta(days=k)
        case "SEMANAL":
            return ref + timedelta(days=7 * k)
        case "MENSAL":
            ano, mes = somar_meses(ref.year, ref.month, k)
            return date(ano, mes, min(ref.day, ultimo_dia_mes(ano, mes)))
        case "ANUAL":
            ano = ref.year + k
            if (ref.month, ref.day) == (2, 29) and not bissexto(ano):
                return date(ano, 2, 28)
            return date(ano, ref.month, ref.day)
    msg = f"periodicidade desconhecida: {regra.periodicidade}"
    raise ValueError(msg)


def data_da_posicao(regra: RegraSerie, n: int) -> date | None:
    """Data da posição `n` (definida só para `n >= numero_referencia`)."""
    k = n - regra.numero_referencia
    if k < 0:
        return None
    return _data_deslocada(regra, k)


def primeira_posicao_em_ou_apos(regra: RegraSerie, d: date) -> int:
    """Menor `n >= r` com `data_da_posicao(n) >= d`."""
    r = regra.numero_referencia
    ref = regra.data_referencia
    if regra.periodicidade == NENHUMA:
        return r if ref >= d else r + 1
    if d <= ref:
        return r
    dias = (d - ref).days
    match regra.periodicidade:
        case "DIARIA":
            k = dias
        case "SEMANAL":
            k = -(-dias // 7)
        case "MENSAL":
            k = (d.year - ref.year) * 12 + d.month - ref.month
        case _:
            k = d.year - ref.year
    k = max(k, 0)
    while (alvo := _data_deslocada(regra, k)) is not None and alvo < d:
        k += 1
    while k > 0:
        anterior = _data_deslocada(regra, k - 1)
        if anterior is None or anterior < d:
            break
        k -= 1
    return r + k


def maior_posicao_ate(regra: RegraSerie, d: date) -> int:
    """Maior `n >= r - 1` com `data_da_posicao(n) <= d`."""
    return primeira_posicao_em_ou_apos(regra, d + timedelta(days=1)) - 1


def ultima_posicao(regra: RegraSerie) -> int | None:
    """Última posição gerável (`None` = sem limite)."""
    limites: list[int] = []
    if regra.numero_final is not None:
        limites.append(regra.numero_final)
    if regra.periodicidade == NENHUMA:
        limites.append(regra.numero_referencia)
    if regra.data_final_repeticao is not None:
        limites.append(maior_posicao_ate(regra, regra.data_final_repeticao))
    return min(limites) if limites else None


def posicoes_no_intervalo(regra: RegraSerie, inicio: date, fim: date) -> range:
    """Posições com data em `[inicio, fim]`, respeitando os limites."""
    primeira = primeira_posicao_em_ou_apos(regra, inicio)
    ultima_no_fim = maior_posicao_ate(regra, fim)
    limite = ultima_posicao(regra)
    if limite is not None:
        ultima_no_fim = min(ultima_no_fim, limite)
    return range(primeira, ultima_no_fim + 1)


def posicao_valida(regra: RegraSerie, n: int) -> bool:
    """A posição existe segundo a regra (referência e limites)."""
    if n < regra.numero_referencia:
        return False
    limite = ultima_posicao(regra)
    return limite is None or n <= limite


def _em_blocos(
    numeros: Sequence[int], tamanho: int
) -> Iterator[Sequence[int]]:
    for i in range(0, len(numeros), tamanho):
        yield numeros[i : i + tamanho]


async def materializar_posicoes(
    sessao: AsyncSession,
    modelo: Any,
    serie_id: uuid.UUID,
    posicoes: range,
    valores_da_posicao: Callable[[int], dict[str, Any]],
) -> list[tuple[uuid.UUID, int]]:
    """Insere as posições faltantes; devolve `(id, numero)` das novas.

    Posições já existentes (inclusive excluídas, que são lápides) nunca
    são recriadas. `modelo` precisa ter `serie_id` e `numero_ocorrencia`.
    """
    if len(posicoes) == 0:
        return []
    primeira, ultima = posicoes.start, posicoes.stop - 1
    ocupadas = set(
        (
            await sessao.scalars(
                select(modelo.numero_ocorrencia).where(
                    modelo.serie_id == serie_id,
                    modelo.numero_ocorrencia.between(primeira, ultima),
                )
            )
        ).all()
    )
    if len(ocupadas) == len(posicoes):
        return []
    faltantes = [n for n in posicoes if n not in ocupadas]
    inseridas: list[tuple[uuid.UUID, int]] = []
    for bloco in _em_blocos(faltantes, TAMANHO_BLOCO):
        linhas = [
            {**valores_da_posicao(n), "numero_ocorrencia": n} for n in bloco
        ]
        resultado = await sessao.execute(
            pg_insert(modelo)
            .values(linhas)
            .on_conflict_do_nothing(
                index_elements=["serie_id", "numero_ocorrencia"]
            )
            .returning(modelo.id, modelo.numero_ocorrencia)
        )
        linhas_novas: list[Any] = list(resultado.all())
        inseridas += [(r[0], r[1]) for r in linhas_novas]
    return inseridas


async def contar_ocorrencias(
    sessao: AsyncSession, modelo: Any, serie_id: uuid.UUID
) -> int:
    """Quantidade de linhas (inclusive lápides) de uma série."""
    return int(
        await sessao.scalar(
            select(func.count()).where(modelo.serie_id == serie_id)
        )
        or 0
    )
