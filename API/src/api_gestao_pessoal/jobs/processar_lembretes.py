"""Ponto de entrada do processador de lembretes (F9).

Uso: `uv run python -m api_gestao_pessoal.jobs.processar_lembretes
[--uma-vez]`. Em modo contínuo executa um ciclo a cada
`LEMBRETES_INTERVALO_S`; `SIGTERM`/`SIGINT` terminam o ciclo corrente e
encerram o processo.
"""

import argparse
import asyncio
import contextlib
import logging
import signal
import sys
from collections.abc import Sequence
from datetime import UTC, datetime

from api_gestao_pessoal.database import criar_engine, criar_fabrica_sessoes
from api_gestao_pessoal.rastreamento import configurar_logging
from api_gestao_pessoal.services.processamento_lembretes import (
    ResultadoCiclo,
    executar_ciclo,
)
from api_gestao_pessoal.settings import Settings, obter_settings

logger = logging.getLogger("api_gestao_pessoal.lembretes")


def _agora() -> datetime:
    return datetime.now(UTC)


async def executar(settings: Settings, *, uma_vez: bool) -> ResultadoCiclo:
    """Executa um ciclo (`uma_vez`) ou ciclos até receber o sinal de parada."""
    engine = criar_engine(settings)
    fabrica = criar_fabrica_sessoes(engine)
    parar = asyncio.Event()
    lacos = asyncio.get_running_loop()
    for sinal in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            lacos.add_signal_handler(sinal, parar.set)
    resultado = ResultadoCiclo()
    try:
        while True:
            resultado = await executar_ciclo(
                fabrica,
                _agora,
                lote=settings.LEMBRETES_LOTE,
                janela_dias=settings.LEMBRETES_JANELA_DIAS,
            )
            logger.info(
                "ciclo: %d enviados, %d cancelados, %d ocorrências, %d falhas",
                resultado.enviados,
                resultado.cancelados,
                resultado.ocorrencias_materializadas,
                resultado.falhas,
            )
            if uma_vez or parar.is_set():
                break
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(
                    parar.wait(), timeout=settings.LEMBRETES_INTERVALO_S
                )
            if parar.is_set():
                break
    finally:
        await engine.dispose()
    return resultado


def main(argv: Sequence[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(prog="processar_lembretes")
    analisador.add_argument(
        "--uma-vez", action="store_true", help="executa um ciclo e encerra"
    )
    argumentos = analisador.parse_args(argv)
    settings = obter_settings()
    configurar_logging(settings.LOG_NIVEL)
    resultado = asyncio.run(executar(settings, uma_vez=argumentos.uma_vez))
    return 1 if resultado.falhas and argumentos.uma_vez else 0


if __name__ == "__main__":
    sys.exit(main())
