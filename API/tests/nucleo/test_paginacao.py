import base64
import json

import pytest

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.services.paginacao import (
    codificar_cursor,
    decodificar_cursor,
)

FILTROS = {"data": "2026-10-13", "busca": None}


def test_cursor_ida_e_volta() -> None:
    cursor = codificar_cursor("HORARIO", FILTROS, ["08:00:00", "abc"])
    assert "=" not in cursor
    assert decodificar_cursor(cursor, "HORARIO", FILTROS) == [
        "08:00:00",
        "abc",
    ]


def test_cursor_de_outros_filtros_ou_ordenacao_e_recusado() -> None:
    cursor = codificar_cursor("HORARIO", FILTROS, [1])
    for ordenacao, filtros in (
        ("PRIORIDADE", FILTROS),
        ("HORARIO", {**FILTROS, "busca": "x"}),
    ):
        with pytest.raises(ErroNegocio) as info:
            decodificar_cursor(cursor, ordenacao, filtros)
        assert info.value.codigo == CodigoErro.CURSOR_INVALIDO


@pytest.mark.parametrize(
    "cursor",
    [
        "",
        "@@@",
        "x" * 2000,
        base64.urlsafe_b64encode(b"nao-json").decode(),
        base64.urlsafe_b64encode(json.dumps([1]).encode()).decode(),
        base64.urlsafe_b64encode(
            json.dumps({"v": 2, "o": "HORARIO", "f": "x", "k": []}).encode()
        ).decode(),
    ],
)
def test_cursor_malformado(cursor: str) -> None:
    with pytest.raises(ErroNegocio) as info:
        decodificar_cursor(cursor, "HORARIO", FILTROS)
    assert info.value.codigo == CodigoErro.CURSOR_INVALIDO
