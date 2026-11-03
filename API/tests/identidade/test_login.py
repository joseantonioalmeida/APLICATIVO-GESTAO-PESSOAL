import unicodedata
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Any

import jwt
import pytest

from api_gestao_pessoal.seguranca import HasherSenha

from ..apoio.esquema import consultar
from ..apoio.identidade import (
    SENHA_PADRAO,
    URL_LOGIN,
    URL_USUARIO_ATUAL,
    codigo_de_erro,
    entrar,
    registrar,
)
from ..conftest import SEGREDO_JWT_TESTE
from .conftest import Ambiente

CLAIMS_ESPERADAS = {"sub", "iat", "exp", "typ", "sv"}
VALIDADE_S = 86400
OUTRA_CHAVE = "outra-chave-sintetica-0123456789abcdef"


def sem_verificar(token: str) -> dict[str, Any]:
    return jwt.decode(token, options={"verify_signature": False})


async def test_login_valido(ambiente: Ambiente) -> None:
    cliente = ambiente.cliente
    await registrar(cliente, email="Maria@Exemplo.com")
    await registrar(cliente, email="Fulano@exâmple.com")
    resposta = await cliente.post(
        URL_LOGIN, json={"email": "maria@exemplo.com", "senha": SENHA_PADRAO}
    )
    assert resposta.status_code == HTTPStatus.OK
    assert resposta.headers["cache-control"] == "no-store"
    corpo = resposta.json()
    assert set(corpo) == {"access_token", "token_type", "expira_em"}
    assert corpo["token_type"] == "bearer"
    claims = sem_verificar(corpo["access_token"])
    assert set(claims) == CLAIMS_ESPERADAS
    assert claims["exp"] - claims["iat"] == VALIDADE_S
    assert claims["typ"] == "access"
    assert corpo["expira_em"].endswith("Z")
    assert datetime.fromisoformat(
        corpo["expira_em"]
    ) == datetime.fromtimestamp(claims["exp"], UTC)
    variantes = [
        "MARIA@EXEMPLO.COM",
        " Fulano@EXÂMPLE.com ",
        "fulano@xn--exmple-xta.com",
        unicodedata.normalize("NFD", "fulano@exâmple.com"),
    ]
    for email in variantes:
        outra = await cliente.post(
            URL_LOGIN, json={"email": email, "senha": SENHA_PADRAO}
        )
        assert outra.status_code == HTTPStatus.OK, email


async def test_credenciais_invalidas_indistinguiveis(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    chamadas: list[str] = []
    original = HasherSenha.verificar_ficticio

    async def espiao(self: HasherSenha, segredo: str) -> None:
        chamadas.append("ficticio")
        await original(self, segredo)

    monkeypatch.setattr(HasherSenha, "verificar_ficticio", espiao)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    tentativas = [
        {"email": "naoexiste@exemplo.com", "senha": "qualquer-senha-1"},
        {"email": "sem-arroba", "senha": "qualquer-senha-1"},
        {"email": usuario["email"], "senha": "senha-errada-123"},
    ]
    corpos = []
    for corpo_envio in tentativas:
        resposta = await cliente.post(URL_LOGIN, json=corpo_envio)
        assert resposta.status_code == HTTPStatus.UNAUTHORIZED
        corpo = resposta.json()
        assert corpo.pop("id_requisicao")
        corpos.append(corpo)
        assert len(chamadas) == min(len(corpos), 2)
    assert corpos[0] == corpos[1] == corpos[2]
    assert corpos[0]["codigo"] == "CREDENCIAIS_INVALIDAS"


def _claims_alteradas(**mudancas: Any) -> Callable[[dict[str, Any], str], str]:
    def construir(claims: dict[str, Any], _valido: str) -> str:
        return "Bearer " + jwt.encode(
            claims | mudancas, SEGREDO_JWT_TESTE, algorithm="HS256"
        )

    return construir


def _com_claims(
    alterar: Callable[[dict[str, Any]], dict[str, Any]],
) -> Callable[[dict[str, Any], str], str]:
    def construir(claims: dict[str, Any], _valido: str) -> str:
        return "Bearer " + jwt.encode(
            alterar(claims), SEGREDO_JWT_TESTE, algorithm="HS256"
        )

    return construir


CASOS_TOKEN = [
    pytest.param(lambda c, v: None, id="ausente"),
    pytest.param(lambda c, v: f"Basic {v}", id="esquema_basic"),
    pytest.param(lambda c, v: "Bearer abc.def", id="malformado"),
    pytest.param(lambda c, v: "Bearer " + "a" * 4097, id="mais_de_4096"),
    pytest.param(
        lambda c, v: "Bearer " + jwt.encode(c, OUTRA_CHAVE, algorithm="HS256"),
        id="assinatura_errada",
    ),
    pytest.param(
        lambda c, v: "Bearer " + jwt.encode(c, None, algorithm="none"),
        id="alg_none",
    ),
    pytest.param(_claims_alteradas(typ="refresh"), id="typ_errado"),
    pytest.param(
        _claims_alteradas(sub=str(uuid.uuid7())), id="sub_inexistente"
    ),
    pytest.param(
        _com_claims(lambda c: c | {"sub": c["sub"].replace("-", "")}),
        id="sub_nao_canonico",
    ),
    pytest.param(_claims_alteradas(extra=1), id="claim_extra"),
    pytest.param(_claims_alteradas(iat=True), id="iat_booleano"),
    pytest.param(
        _com_claims(
            lambda c: c | {"iat": c["iat"] + 3600, "exp": c["exp"] + 3600}
        ),
        id="iat_no_futuro",
    ),
    pytest.param(
        _com_claims(
            lambda c: c | {"iat": c["iat"] - 90000, "exp": c["iat"] - 3600}
        ),
        id="expirado",
    ),
]


@pytest.mark.parametrize("construir", CASOS_TOKEN)
async def test_tokens_recusados(
    ambiente: Ambiente, construir: Callable[[dict[str, Any], str], str | None]
) -> None:
    usuario = await registrar(ambiente.cliente)
    valido = await entrar(ambiente.cliente, usuario["email"], SENHA_PADRAO)
    autorizacao = construir(sem_verificar(valido), valido)
    cabecalhos = {} if autorizacao is None else {"Authorization": autorizacao}
    resposta = await ambiente.cliente.get(
        URL_USUARIO_ATUAL, headers=cabecalhos
    )
    assert resposta.status_code == HTTPStatus.UNAUTHORIZED
    assert codigo_de_erro(resposta) == "NAO_AUTENTICADO"
    assert resposta.headers["www-authenticate"] == "Bearer"


async def test_limites_do_token(ambiente: Ambiente) -> None:
    usuario = await registrar(ambiente.cliente)
    token = await entrar(ambiente.cliente, usuario["email"], SENHA_PADRAO)
    cabecalhos = {"Authorization": f"Bearer {token}"}

    async def status() -> int:
        resposta = await ambiente.cliente.get(
            URL_USUARIO_ATUAL, headers=cabecalhos
        )
        return resposta.status_code

    ambiente.relogio.avancar(timedelta(seconds=-1))
    assert await status() == HTTPStatus.UNAUTHORIZED
    ambiente.relogio.avancar(timedelta(seconds=1))
    assert await status() == HTTPStatus.OK
    ambiente.relogio.avancar(timedelta(seconds=VALIDADE_S - 1))
    assert await status() == HTTPStatus.OK
    ambiente.relogio.avancar(timedelta(seconds=1))
    assert await status() == HTTPStatus.UNAUTHORIZED


async def test_login_nao_regrava_hash(ambiente: Ambiente) -> None:
    usuario = await registrar(ambiente.cliente)
    antes = consultar(ambiente.banco, "SELECT senha_hash FROM usuario")
    await entrar(ambiente.cliente, usuario["email"], SENHA_PADRAO)
    await entrar(ambiente.cliente, usuario["email"], SENHA_PADRAO)
    assert consultar(ambiente.banco, "SELECT senha_hash FROM usuario") == antes
