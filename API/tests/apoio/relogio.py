"""Relógio fixo e avançável para os testes (arquitetura §7)."""

from datetime import UTC, datetime, timedelta
from typing import override

from api_gestao_pessoal.tempo import Relogio


class RelogioFixo(Relogio):
    """Devolve sempre o mesmo instante até `avancar` ser chamado."""

    def __init__(self, instante: datetime) -> None:
        if instante.tzinfo is not UTC:
            msg = "RelogioFixo exige instante em UTC"
            raise ValueError(msg)
        self._instante = instante

    @override
    def agora(self) -> datetime:
        return self._instante

    def avancar(self, intervalo: timedelta) -> None:
        self._instante += intervalo
