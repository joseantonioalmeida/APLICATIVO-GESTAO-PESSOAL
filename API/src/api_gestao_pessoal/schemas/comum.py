"""Tipos e envelopes compartilhados pelos schemas (arquitetura §4.1)."""

import enum
import re
from collections.abc import Callable
from datetime import date, datetime, time
from decimal import Decimal
from typing import Annotated, LiteralString

from pydantic import BaseModel, BeforeValidator, PlainSerializer
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


PADRAO_VALOR = re.compile(r"[0-9]+(\.[0-9]+)?")
MENSAGEM_CASAS = "Informe um valor com até duas casas decimais"
MENSAGEM_LIMITE = "O valor máximo por lançamento é R$ 9.999.999.999,99"
DIGITOS_INTEIROS_MAXIMOS = 10
CASAS_DECIMAIS_MAXIMAS = 2


def conversor_valor(
    codigo: LiteralString, mensagem: LiteralString
) -> Callable[[object], Decimal]:
    """Fábrica de validadores de dinheiro (string decimal, D-16).

    `codigo`/`mensagem` descrevem o erro de valor ausente, zero, negativo
    ou fora do formato (ex.: `VALOR_OBRIGATORIO`). Número JSON é rejeitado.
    """

    def converter(valor: object) -> Decimal:
        if isinstance(valor, Decimal):
            texto = format(valor, "f")
        elif isinstance(valor, str):
            texto = valor.strip()
        else:
            raise PydanticCustomError(codigo, mensagem)
        if not PADRAO_VALOR.fullmatch(texto):
            raise PydanticCustomError(codigo, mensagem)
        inteiro, _, decimais = texto.partition(".")
        if len(decimais.rstrip("0")) > CASAS_DECIMAIS_MAXIMAS:
            raise PydanticCustomError("CASAS_DECIMAIS", MENSAGEM_CASAS)
        if len(inteiro.lstrip("0")) > DIGITOS_INTEIROS_MAXIMOS:
            raise PydanticCustomError("VALOR_ACIMA_DO_LIMITE", MENSAGEM_LIMITE)
        resultado = Decimal(texto).quantize(Decimal("0.01"))
        if resultado <= 0:
            raise PydanticCustomError(codigo, mensagem)
        return resultado

    return converter


def formatar_dinheiro(valor: Decimal) -> str:
    """Sempre com duas casas: `Decimal("1220.3")` -> `"1220.30"`."""
    return format(valor.quantize(Decimal("0.01")), "f")


DinheiroSaida = Annotated[
    Decimal, PlainSerializer(formatar_dinheiro, return_type=str)
]
