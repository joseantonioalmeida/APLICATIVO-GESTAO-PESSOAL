from typing import Any, NamedTuple

import pytest
from pydantic import SecretStr, ValidationError

from ..conftest import SEGREDO_JWT_TESTE, SettingsTeste

URL = SecretStr("postgresql+psycopg://u:p@h/db")
SMTP_VALIDO: dict[str, Any] = {
    "EMAIL_MODO": "smtp",
    "SMTP_HOST": "smtp.exemplo.com",
    "SMTP_REMETENTE": "nao-responda@exemplo.com",
}
PRODUCAO_VALIDA: dict[str, Any] = SMTP_VALIDO | {
    "AMBIENTE": "producao",
    "ARGON2_TIME_COST": 3,
    "ARGON2_MEMORY_COST_KIB": 65536,
    "ARGON2_PARALLELISM": 4,
}


class Caso(NamedTuple):
    alteracoes: dict[str, Any]
    erro: str | None = None
    proibido_na_mensagem: str | None = None
    esperado: dict[str, Any] | None = None


def construir(alteracoes: dict[str, Any]) -> SettingsTeste:
    base: dict[str, Any] = {
        "DATABASE_URL": URL,
        "JWT_SEGREDO": SecretStr(SEGREDO_JWT_TESTE),
        "EMAIL_MODO": "memoria",
        "ARGON2_TIME_COST": 1,
        "ARGON2_MEMORY_COST_KIB": 8,
        "ARGON2_PARALLELISM": 1,
    }
    return SettingsTeste(**(base | alteracoes))


def segredo(valor: str) -> dict[str, Any]:
    return {"JWT_SEGREDO": SecretStr(valor)}


CASOS = [
    pytest.param(Caso(segredo("s" * 32)), id="segredo_32_bytes"),
    pytest.param(Caso(segredo("é" * 16)), id="segredo_multibyte_32_bytes"),
    pytest.param(
        Caso(segredo("s" * 31), "JWT_SEGREDO", "s" * 31), id="segredo_31_bytes"
    ),
    pytest.param(
        Caso(segredo("é" * 15 + "a"), "JWT_SEGREDO", "é" * 15),
        id="segredo_multibyte_31_bytes",
    ),
    pytest.param(
        Caso(segredo("TROQUE_ESTE_VALOR"), "JWT_SEGREDO", "TROQUE_ESTE_VALOR"),
        id="placeholder_do_env_exemplo",
    ),
    pytest.param(Caso({"JWT_VALIDADE_MINUTOS": 5}), id="validade_5"),
    pytest.param(Caso({"JWT_VALIDADE_MINUTOS": 1440}), id="validade_1440"),
    pytest.param(
        Caso({"JWT_VALIDADE_MINUTOS": 4}, "JWT_VALIDADE_MINUTOS"),
        id="validade_4",
    ),
    pytest.param(
        Caso({"JWT_VALIDADE_MINUTOS": 1441}, "JWT_VALIDADE_MINUTOS"),
        id="validade_1441",
    ),
    pytest.param(
        Caso({"ARGON2_TIME_COST": 0}, "ARGON2_TIME_COST"), id="time_cost_0"
    ),
    pytest.param(
        Caso({"ARGON2_TIME_COST": 11}, "ARGON2_TIME_COST"), id="time_cost_11"
    ),
    pytest.param(
        Caso({"ARGON2_MEMORY_COST_KIB": 7}, "ARGON2_MEMORY_COST_KIB"),
        id="memoria_7",
    ),
    pytest.param(
        Caso({"ARGON2_PARALLELISM": 17}, "ARGON2_PARALLELISM"),
        id="paralelismo_17",
    ),
    pytest.param(
        Caso({"ARGON2_MAX_CONCORRENTES": 0}, "ARGON2_MAX_CONCORRENTES"),
        id="concorrentes_0",
    ),
    pytest.param(
        Caso({"ARGON2_MAX_CONCORRENTES": 33}, "ARGON2_MAX_CONCORRENTES"),
        id="concorrentes_33",
    ),
    pytest.param(
        Caso(
            {"ARGON2_MEMORY_COST_KIB": 16, "ARGON2_PARALLELISM": 3},
            "ARGON2_MEMORY_COST_KIB deve ser pelo menos",
        ),
        id="memoria_menor_que_8_por_pista",
    ),
    pytest.param(
        Caso(
            {"EMAIL_MODO": "smtp", "SMTP_REMETENTE": "a@exemplo.com"},
            "SMTP_HOST",
        ),
        id="smtp_sem_host",
    ),
    pytest.param(
        Caso(
            {"EMAIL_MODO": "smtp", "SMTP_HOST": "smtp.exemplo.com"},
            "SMTP_REMETENTE",
        ),
        id="smtp_sem_remetente",
    ),
    pytest.param(
        Caso({"SMTP_REMETENTE": "nao-e-email"}, "SMTP_REMETENTE"),
        id="remetente_invalido",
    ),
    pytest.param(
        Caso(
            {"SMTP_REMETENTE": " Nao-Responda@Exemplo.COM "},
            esperado={"SMTP_REMETENTE": "nao-responda@exemplo.com"},
        ),
        id="remetente_canonico",
    ),
    pytest.param(
        Caso({"SMTP_USUARIO": "usuario"}, "SMTP_USUARIO e SMTP_SENHA"),
        id="usuario_sem_senha",
    ),
    pytest.param(
        Caso(
            {"SMTP_SENHA": SecretStr("senha-smtp")},
            "SMTP_USUARIO e SMTP_SENHA",
            "senha-smtp",
        ),
        id="senha_sem_usuario",
    ),
    pytest.param(
        Caso(
            {
                "SMTP_SEGURANCA": "nenhuma",
                "SMTP_USUARIO": "usuario",
                "SMTP_SENHA": SecretStr("senha-smtp"),
            },
            "credenciais SMTP",
            "senha-smtp",
        ),
        id="credenciais_sem_tls",
    ),
    pytest.param(Caso(PRODUCAO_VALIDA), id="producao_valida"),
    pytest.param(
        Caso({"AMBIENTE": "producao"}, "EMAIL_MODO=memoria"),
        id="producao_com_memoria",
    ),
    pytest.param(
        Caso(
            PRODUCAO_VALIDA | {"SMTP_SEGURANCA": "nenhuma"}, "SMTP_SEGURANCA"
        ),
        id="producao_sem_tls",
    ),
    pytest.param(
        Caso(PRODUCAO_VALIDA | {"ARGON2_TIME_COST": 2}, "ARGON2_TIME_COST"),
        id="producao_time_cost_2",
    ),
    pytest.param(
        Caso(
            PRODUCAO_VALIDA | {"ARGON2_MEMORY_COST_KIB": 65535},
            "ARGON2_MEMORY_COST_KIB",
        ),
        id="producao_memoria_65535",
    ),
]


@pytest.mark.parametrize("caso", CASOS)
def test_settings_da_f3(caso: Caso) -> None:
    if caso.erro is None:
        configuracao = construir(caso.alteracoes)
        for nome, valor in (caso.esperado or {}).items():
            assert getattr(configuracao, nome) == valor
        return
    with pytest.raises(ValidationError) as erro:
        construir(caso.alteracoes)
    assert caso.erro in str(erro.value)
    if caso.proibido_na_mensagem is not None:
        assert caso.proibido_na_mensagem not in str(erro.value)
