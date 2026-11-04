import random
from datetime import date, timedelta

import pytest

from api_gestao_pessoal.services.recorrencia import (
    RegraSerie,
    data_da_posicao,
    maior_posicao_ate,
    posicao_valida,
    posicoes_no_intervalo,
    primeira_posicao_em_ou_apos,
    ultima_posicao,
)


def regra(
    periodicidade: str,
    referencia: date,
    *,
    r: int = 1,
    final: date | None = None,
    numero_final: int | None = None,
) -> RegraSerie:
    return RegraSerie(periodicidade, referencia, r, final, numero_final)


def datas(r: RegraSerie, ate: int) -> list[date | None]:
    return [data_da_posicao(r, n) for n in range(1, ate + 1)]


def test_mensal_preserva_o_dia_original() -> None:
    r = regra("MENSAL", date(2027, 1, 31))
    assert datas(r, 3) == [
        date(2027, 1, 31),
        date(2027, 2, 28),
        date(2027, 3, 31),
    ]
    bissexto = regra("MENSAL", date(2028, 1, 31))
    assert data_da_posicao(bissexto, 2) == date(2028, 2, 29)


def test_anual_em_29_de_fevereiro() -> None:
    r = regra("ANUAL", date(2028, 2, 29))
    assert data_da_posicao(r, 2) == date(2029, 2, 28)
    assert data_da_posicao(r, 5) == date(2032, 2, 29)


def test_semanal_com_data_final_inclusiva() -> None:
    r = regra("SEMANAL", date(2026, 10, 8), final=date(2026, 10, 22))
    posicoes = posicoes_no_intervalo(r, date(2026, 10, 1), date(2026, 12, 31))
    assert [data_da_posicao(r, n) for n in posicoes] == [
        date(2026, 10, 8),
        date(2026, 10, 15),
        date(2026, 10, 22),
    ]
    assert ultima_posicao(r) == 3


def test_numero_final_zero_nao_gera_nada() -> None:
    r = regra("DIARIA", date(2026, 10, 13), numero_final=0)
    assert ultima_posicao(r) == 0
    assert (
        len(posicoes_no_intervalo(r, date(2026, 10, 13), date(2027, 1, 1)))
        == 0
    )
    assert not posicao_valida(r, 1)


def test_nenhuma_so_a_posicao_de_referencia() -> None:
    r = regra("NENHUMA", date(2026, 10, 13), r=4)
    assert data_da_posicao(r, 4) == date(2026, 10, 13)
    assert data_da_posicao(r, 5) is None
    assert data_da_posicao(r, 3) is None
    assert ultima_posicao(r) == 4
    assert list(
        posicoes_no_intervalo(r, date(2026, 10, 13), date(2026, 10, 13))
    ) == [4]
    assert (
        list(posicoes_no_intervalo(r, date(2026, 10, 14), date(2026, 12, 1)))
        == []
    )


def test_data_final_anterior_a_referencia() -> None:
    r = regra("DIARIA", date(2026, 10, 13), final=date(2026, 10, 1))
    assert ultima_posicao(r) == 0


@pytest.mark.parametrize(
    "periodicidade", ["DIARIA", "SEMANAL", "MENSAL", "ANUAL"]
)
def test_busca_aritmetica_confere_com_forca_bruta(periodicidade: str) -> None:
    rng = random.Random(7)
    for _ in range(60):
        ref = date(2024, 1, 1) + timedelta(days=rng.randrange(0, 1500))
        r = regra(periodicidade, ref, r=rng.randrange(1, 6))
        alvo = ref + timedelta(days=rng.randrange(-400, 1500))
        bruta = next(
            n
            for n in range(r.numero_referencia, r.numero_referencia + 2000)
            if (d := data_da_posicao(r, n)) is not None and d >= alvo
        )
        assert primeira_posicao_em_ou_apos(r, alvo) == bruta
        assert maior_posicao_ate(r, alvo) == (
            max(
                (
                    n
                    for n in range(r.numero_referencia, bruta + 2)
                    if (d := data_da_posicao(r, n)) is not None and d <= alvo
                ),
                default=r.numero_referencia - 1,
            )
        )
