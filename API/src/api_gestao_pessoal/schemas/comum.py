"""Tipos e envelopes compartilhados pelos schemas (arquitetura §4.1)."""

import enum
import re
from datetime import date, datetime, time
from typing import Annotated

from pydantic import BaseModel, BeforeValidator
from pydantic_core import PydanticCustomError

PADRAO_HORARIO = re.compile(r"([01][0-9]|2[0-3]):[0-5][0-9]")
MENSAGEM_HORARIO = "Informe um horário válido"


def converter_horario(valor: object) -> time:
    """`HH:MM` (sem segundos) para `time`; entrada de `time` é aceita."""
    if isinstance(valor, time):
        return valor.replace(second=0, microsecond=0)
    if isinstance(valor, str) and PADRAO_HORARIO.fullmatch(valor):
        return time(int(valor[:2]), int(valor[3:]))
    raise PydanticCustomError("HORARIO_INVALIDO", MENSAGEM_HORARIO)


Horario = Annotated[time, BeforeValidator(converter_horario)]


def formatar_horario(valor: time) -> str:
    """`time` para `HH:MM`."""
    return valor.strftime("%H:%M")


class Pagina[T](BaseModel):
    """Página de itens com cursor opaco para a próxima."""

    itens: list[T]
    proximo_cursor: str | None = None


PADRAO_DATA_CIVIL = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
MENSAGEM_DATA = "Informe uma data válida"
DATA_MINIMA = date(2000, 1, 1)
DATA_MAXIMA = date(2100, 12, 31)


def converter_data(valor: object) -> date:
    """`AAAA-MM-DD` existente, entre 2000 e 2100 (`DATA_INVALIDA`)."""
    erro = PydanticCustomError("DATA_INVALIDA", MENSAGEM_DATA)
    if isinstance(valor, date) and not isinstance(valor, datetime):
        resultado = valor
    elif isinstance(valor, str) and PADRAO_DATA_CIVIL.fullmatch(valor):
        try:
            resultado = date.fromisoformat(valor)
        except ValueError:
            raise erro from None
    else:
        raise erro
    if not DATA_MINIMA <= resultado <= DATA_MAXIMA:
        raise erro
    return resultado


DataCivil = Annotated[date, BeforeValidator(converter_data)]


class AlcanceSerie(enum.StrEnum):
    """Alcance de uma edição ou exclusão em série."""

    SOMENTE_ESTA = "SOMENTE_ESTA"
    ESTA_E_PROXIMAS = "ESTA_E_PROXIMAS"
