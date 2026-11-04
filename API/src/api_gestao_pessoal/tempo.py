"""Relógio da aplicação, contexto da requisição e utilidades de fuso (D-13)."""

import calendar
import functools
import uuid
import zoneinfo
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Protocol, override

FUSOS_EXCLUIDOS = frozenset({"localtime", "posixrules", "Factory"})
PREFIXOS_EXCLUIDOS = ("posix/", "right/")
TAMANHO_MAXIMO_FUSO = 64


class Relogio(Protocol):
    """Fonte única do instante atual da aplicação."""

    def agora(self) -> datetime:
        """Instante atual, sempre com fuso UTC."""
        ...


class RelogioSistema(Relogio):
    """Relógio real da aplicação, em UTC."""

    @override
    def agora(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ContextoUsuario:
    """Usuário autenticado e instante da requisição, capturados uma vez."""

    usuario_id: uuid.UUID
    fuso: zoneinfo.ZoneInfo
    agora: datetime
    hoje: date


@functools.cache
def _fusos_disponiveis() -> frozenset[str]:
    return frozenset(zoneinfo.available_timezones())


def fuso_valido(chave: str) -> bool:
    """Chave IANA aceita no cadastro (arquitetura §7)."""
    return (
        0 < len(chave) <= TAMANHO_MAXIMO_FUSO
        and chave not in FUSOS_EXCLUIDOS
        and not chave.startswith(PREFIXOS_EXCLUIDOS)
        and chave in _fusos_disponiveis()
    )


def hoje_no_fuso(instante: datetime, fuso: zoneinfo.ZoneInfo) -> date:
    """Data civil do instante no fuso informado."""
    return instante.astimezone(fuso).date()


def instante_local(
    data: date, horario: time, fuso: zoneinfo.ZoneInfo
) -> datetime:
    """Instante UTC de `data` + `horario` no fuso informado (fold=0)."""
    return datetime.combine(data, horario, tzinfo=fuso).astimezone(UTC)


def primeiro_dia_mes(d: date) -> date:
    """Primeiro dia do mês de `d`."""
    return d.replace(day=1)


def ultimo_dia_do_mes(d: date) -> date:
    """Último dia do mês de `d`."""
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def mes_anterior(d: date) -> date:
    """Primeiro dia do mês anterior ao de `d`."""
    return primeiro_dia_mes(primeiro_dia_mes(d) - timedelta(days=1))
