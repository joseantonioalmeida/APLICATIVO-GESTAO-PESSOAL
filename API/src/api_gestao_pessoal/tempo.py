"""Relógio da aplicação, contexto da requisição e utilidades de fuso (D-13)."""

import functools
import uuid
import zoneinfo
from dataclasses import dataclass
from datetime import UTC, date, datetime
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
