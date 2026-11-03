import unicodedata
import uuid
from collections.abc import Callable
from datetime import timedelta
from http import HTTPStatus
from typing import Any, NamedTuple

import psycopg
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from ..apoio.esquema import consultar
from ..apoio.identidade import (
    ESPERA_INSERT_USUARIO,
    SENHA_PADRAO,
    URL_REGISTRO,
    codigo_de_erro,
    disparar_simultaneas,
    registrar,
)
from .conftest import Ambiente

AUSENTE = object()
CAMPOS_RESPOSTA = {
    "id",
    "nome_completo",
    "email",
    "data_nascimento",
    "fuso_horario",
}
MENSAGEM_SENHA_FRACA = (
    "A senha informada não atende os requisitos necessários de 8 caracteres"
)
MENSAGEM_SENHAS_DIFERENTES = "As senhas devem ser idênticas"
AVANCO_ATE_02H30Z = timedelta(hours=14, minutes=30)


class Caso(NamedTuple):
    alteracoes: dict[str, Any]
    campo: str | None
    codigo: str | None
    avanco: timedelta = timedelta(0)


def montar_corpo(alteracoes: dict[str, Any]) -> dict[str, Any]:
    corpo: dict[str, Any] = {
        "nome_completo": "Pessoa Teste",
        "email": "pessoa@exemplo.com",
        "senha": SENHA_PADRAO,
        "confirmar_senha": SENHA_PADRAO,
        "data_nascimento": "1990-01-01",
        "fuso_horario": "America/Sao_Paulo",
    }
    for chave, valor in alteracoes.items():
        if valor is AUSENTE:
            corpo.pop(chave)
        else:
            corpo[chave] = valor
    return corpo


def contar_usuarios(banco: str) -> int:
    return consultar(banco, "SELECT count(*) FROM usuario")[0][0]


async def test_registro_valido(ambiente: Ambiente) -> None:
    resposta = await ambiente.cliente.post(
        URL_REGISTRO,
        json=montar_corpo({"email": "  Fulano.Silva@Exemplo.COM  "}),
    )
    assert resposta.status_code == HTTPStatus.CREATED
    corpo = resposta.json()
    assert set(corpo) == CAMPOS_RESPOSTA
    assert corpo["email"] == "fulano.silva@exemplo.com"
    assert corpo["data_nascimento"] == "1990-01-01"
    assert uuid.UUID(corpo["id"]).version == 7
    (hash_gravado,) = consultar(
        ambiente.banco, "SELECT senha_hash FROM usuario"
    )[0]
    assert hash_gravado.startswith("$argon2id$")
    assert hash_gravado != SENHA_PADRAO
    assert hash_gravado not in resposta.text


CASOS_INVALIDOS = [
    pytest.param(
        Caso(
            {"senha": "curta1!", "confirmar_senha": "curta1!"},
            "senha",
            "SENHA_FRACA",
        ),
        id="senha_curta",
    ),
    pytest.param(
        Caso({"senha": "", "confirmar_senha": ""}, "senha", "SENHA_FRACA"),
        id="senha_vazia",
    ),
    pytest.param(
        Caso({"senha": AUSENTE}, "senha", "SENHA_FRACA"), id="senha_ausente"
    ),
    pytest.param(
        Caso(
            {"senha": "a" * 129, "confirmar_senha": "a" * 129},
            "senha",
            "TAMANHO_MAXIMO",
        ),
        id="senha_129_caracteres",
    ),
    pytest.param(
        Caso(
            {"confirmar_senha": "outra-senha-123"},
            "confirmar_senha",
            "SENHAS_DIFERENTES",
        ),
        id="confirmacao_diferente",
    ),
    pytest.param(
        Caso({"email": "sem-arroba"}, "email", "EMAIL_INVALIDO"),
        id="email_sem_arroba",
    ),
    pytest.param(
        Caso({"email": "josé@exemplo.com"}, "email", "EMAIL_INVALIDO"),
        id="email_parte_local_nao_ascii",
    ),
    pytest.param(
        Caso({"email": "fulano@localhost"}, "email", "EMAIL_INVALIDO"),
        id="email_localhost",
    ),
    pytest.param(
        Caso({"fuso_horario": "localtime"}, "fuso_horario", "FUSO_INVALIDO"),
        id="fuso_localtime",
    ),
    pytest.param(
        Caso(
            {"fuso_horario": "../etc/passwd"}, "fuso_horario", "FUSO_INVALIDO"
        ),
        id="fuso_caminho_relativo",
    ),
    pytest.param(
        Caso(
            {"fuso_horario": "Mundo/Inexistente"},
            "fuso_horario",
            "FUSO_INVALIDO",
        ),
        id="fuso_inexistente",
    ),
    pytest.param(
        Caso(
            {"nome_completo": "   "},
            "nome_completo",
            "NOME_COMPLETO_OBRIGATORIO",
        ),
        id="nome_vazio",
    ),
    pytest.param(
        Caso(
            {"nome_completo": "Pessoa\r\nTeste"},
            "nome_completo",
            "NOME_COMPLETO_INVALIDO",
        ),
        id="nome_com_controle",
    ),
    pytest.param(
        Caso(
            {"data_nascimento": "1990-1-1"}, "data_nascimento", "DATA_INVALIDA"
        ),
        id="data_sem_zeros",
    ),
    pytest.param(
        Caso(
            {"data_nascimento": "19900101"}, "data_nascimento", "DATA_INVALIDA"
        ),
        id="data_compacta",
    ),
    pytest.param(
        Caso(
            {"data_nascimento": "1990-01-01T00:00:00"},
            "data_nascimento",
            "DATA_INVALIDA",
        ),
        id="data_com_hora",
    ),
    pytest.param(
        Caso({"data_nascimento": 0}, "data_nascimento", "DATA_INVALIDA"),
        id="data_numerica",
    ),
    pytest.param(
        Caso(
            {"data_nascimento": "2001-02-29"},
            "data_nascimento",
            "DATA_INVALIDA",
        ),
        id="data_inexistente",
    ),
    pytest.param(
        Caso(
            {"data_nascimento": "١٩٩٠-٠١-٠١"},
            "data_nascimento",
            "DATA_INVALIDA",
        ),
        id="data_digitos_nao_ascii",
    ),
    pytest.param(
        Caso(
            {"data_nascimento": "2026-10-14"},
            "data_nascimento",
            "DATA_NASCIMENTO_FUTURA",
            AVANCO_ATE_02H30Z,
        ),
        id="nascimento_futuro_no_fuso",
    ),
    pytest.param(
        Caso({"data_nascimento": "2026-10-13"}, None, None, AVANCO_ATE_02H30Z),
        id="nascimento_hoje_no_fuso",
    ),
]


@pytest.mark.parametrize("caso", CASOS_INVALIDOS)
async def test_validacoes_do_registro(ambiente: Ambiente, caso: Caso) -> None:
    ambiente.relogio.avancar(caso.avanco)
    resposta = await ambiente.cliente.post(
        URL_REGISTRO, json=montar_corpo(caso.alteracoes)
    )
    if caso.codigo is None:
        assert resposta.status_code == HTTPStatus.CREATED
        assert contar_usuarios(ambiente.banco) == 1
        return
    assert resposta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert codigo_de_erro(resposta) == "VALIDACAO"
    campos = resposta.json()["campos"]
    achados = [c for c in campos if c["campo"] == caso.campo]
    assert [c["codigo"] for c in achados] == [caso.codigo]
    if caso.codigo == "SENHA_FRACA":
        assert achados[0]["mensagem"] == MENSAGEM_SENHA_FRACA
    if caso.codigo == "SENHAS_DIFERENTES":
        assert achados[0]["mensagem"] == MENSAGEM_SENHAS_DIFERENTES
    for valor in caso.alteracoes.values():
        if isinstance(valor, str) and len(valor) >= len("curta1!"):
            assert valor not in resposta.text
    assert contar_usuarios(ambiente.banco) == 0


def decompor(texto: str) -> str:
    return unicodedata.normalize("NFD", texto)


@pytest.mark.parametrize(
    ("primeiro", "segundo"),
    [
        pytest.param(
            "fulano@exemplo.com", " FULANO@Exemplo.COM ", id="ascii_maiusculas"
        ),
        pytest.param(
            "fulano@exâmple.com", "FULANO@EXÂMPLE.COM", id="idn_maiusculas"
        ),
        pytest.param(
            "fulano@exâmple.com", decompor("fulano@exâmple.com"), id="idn_nfd"
        ),
        pytest.param(
            "fulano@exâmple.com",
            "fulano@xn--exmple-xta.com",
            id="idn_punycode",
        ),
    ],
)
async def test_email_duplicado(
    ambiente: Ambiente, primeiro: str, segundo: str
) -> None:
    await registrar(ambiente.cliente, email=primeiro)
    resposta = await ambiente.cliente.post(
        URL_REGISTRO, json=montar_corpo({"email": segundo})
    )
    assert resposta.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(resposta) == "EMAIL_JA_CADASTRADO"
    assert contar_usuarios(ambiente.banco) == 1


@pytest.mark.concorrencia
async def test_registros_simultaneos(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Callable[[], psycopg.Connection],
) -> None:
    bloqueadora = abrir_bloqueadora()
    bloqueadora.execute(
        "INSERT INTO usuario (id, nome_completo, email, senha_hash, "
        "data_nascimento, fuso_horario) VALUES (%s, 'Bloqueio', %s, 'x', "
        "'1990-01-01', 'UTC')",
        (uuid.uuid7(), "concorrente@exemplo.com"),
    )
    corpo = montar_corpo({"email": "concorrente@exemplo.com"})
    respostas = await disparar_simultaneas(
        bloqueadora,
        monitor,
        [ambiente.cliente.post(URL_REGISTRO, json=corpo) for _ in range(2)],
        ESPERA_INSERT_USUARIO,
        2,
    )
    assert sorted(r.status_code for r in respostas) == [
        HTTPStatus.CREATED,
        HTTPStatus.CONFLICT,
    ]
    perdedora = next(
        r for r in respostas if r.status_code == HTTPStatus.CONFLICT
    )
    assert codigo_de_erro(perdedora) == "EMAIL_JA_CADASTRADO"
    assert contar_usuarios(ambiente.banco) == 1
