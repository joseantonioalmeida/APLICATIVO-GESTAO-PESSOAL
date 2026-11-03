from collections.abc import AsyncIterator
from datetime import timedelta
from http import HTTPStatus
from typing import override

import pytest
from fastapi import FastAPI
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from api_gestao_pessoal import seguranca
from api_gestao_pessoal.database import obter_sessao
from api_gestao_pessoal.email import FalhaEnvioEmail

from ..apoio.esquema import consultar
from ..apoio.identidade import (
    CODIGO_PADRAO,
    SENHA_PADRAO,
    URL_LOGIN,
    URL_REDEFINIR,
    SequenciaCodigos,
    codigo_de_erro,
    entrar,
    linha_recuperacao,
    obter_token_redefinicao,
    redefinir,
    registrar,
    solicitar,
    verificar,
)
from .conftest import Ambiente

NOVA_SENHA = "nova-senha-456"
CODIGO_ERRADO = "99999999"
MENSAGEM_CODIGO_INVALIDO = (
    "O código de verificação que você inseriu não é válido. "
    "Verifique o código e tente novamente."
)
CORPO_ESPERADO = (
    "Olá, Maria da Silva.\n"
    "Recebemos uma solicitação para redefinir a senha de sua conta "
    "MinhaVida.\n"
    "00012345\n"
    "Insira este código para concluir a redefinição.\n"
    "Obrigado por nos ajudar a manter sua conta segura.\n"
    "Equipe MinhaVida.\n"
)
DEZ_MINUTOS = timedelta(minutes=10)
UM_MINUTO = timedelta(seconds=60)


def forcar_codigos(
    monkeypatch: pytest.MonkeyPatch, *codigos: str
) -> SequenciaCodigos:
    sequencia = SequenciaCodigos(*codigos)
    monkeypatch.setattr(seguranca, "gerar_codigo", sequencia)
    return sequencia


def contar_recuperacoes(banco: str) -> int:
    return consultar(banco, "SELECT count(*) FROM recuperacao_senha")[0][0]


async def test_solicitar_codigo(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    usuario = await registrar(ambiente.cliente, nome_completo="Maria da Silva")
    resposta = await solicitar(ambiente.cliente, usuario["email"])
    assert resposta.status_code == HTTPStatus.OK
    assert resposta.json() == {
        "expira_em": "2026-10-13T12:10:00Z",
        "reenvio_permitido_em": "2026-10-13T12:01:00Z",
    }
    (mensagem,) = ambiente.enviador.enviadas
    assert mensagem.assunto == "Maria da Silva, aqui está seu código"
    assert mensagem.corpo == CORPO_ESPERADO
    assert mensagem.destinatario == usuario["email"]
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.codigo_hash.startswith("$argon2id$")
    assert CODIGO_PADRAO not in linha.codigo_hash
    assert linha.expira_em == ambiente.relogio.agora() + DEZ_MINUTOS
    assert linha.tentativas == 0


async def test_email_nao_encontrado(ambiente: Ambiente) -> None:
    resposta = await solicitar(ambiente.cliente, "ninguem@exemplo.com")
    assert resposta.status_code == HTTPStatus.NOT_FOUND
    assert codigo_de_erro(resposta) == "EMAIL_NAO_ENCONTRADO"
    assert (
        resposta.json()["mensagem"] == "Não foi possível encontrar seu email."
    )
    assert not ambiente.enviador.enviadas
    assert contar_recuperacoes(ambiente.banco) == 0


async def test_reenvio(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, "00012345", "87654321")
    cliente, relogio = ambiente.cliente, ambiente.relogio
    usuario = await registrar(cliente)
    email, uid = usuario["email"], usuario["id"]
    assert (await solicitar(cliente, email)).status_code == HTTPStatus.OK
    for _ in range(2):
        invalida = await verificar(cliente, email, CODIGO_ERRADO)
        assert codigo_de_erro(invalida) == "CODIGO_INVALIDO"
    anterior = linha_recuperacao(ambiente.banco, uid)
    assert anterior is not None
    assert anterior.tentativas == 2

    relogio.avancar(timedelta(seconds=59))
    cedo = await solicitar(cliente, email)
    assert cedo.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert codigo_de_erro(cedo) == "REENVIO_MUITO_FREQUENTE"
    assert cedo.headers["retry-after"] == "1"
    assert linha_recuperacao(ambiente.banco, uid) == anterior

    relogio.avancar(timedelta(seconds=1))
    assert (await solicitar(cliente, email)).status_code == HTTPStatus.OK
    nova = linha_recuperacao(ambiente.banco, uid)
    assert nova is not None
    assert nova.tentativas == 0
    assert nova.verificado_em is None
    assert nova.token_redefinicao_hash is None
    assert nova.utilizado_em is None
    assert nova.codigo_hash != anterior.codigo_hash
    assert nova.expira_em == relogio.agora() + DEZ_MINUTOS
    assert len(ambiente.enviador.enviadas) == 2
    assert "87654321" in ambiente.enviador.enviadas[1].corpo

    antigo = await verificar(cliente, email, "00012345")
    assert codigo_de_erro(antigo) == "CODIGO_INVALIDO"
    depois = linha_recuperacao(ambiente.banco, uid)
    assert depois is not None
    assert depois.tentativas == 1
    novo = await verificar(cliente, email, "87654321")
    assert novo.status_code == HTTPStatus.OK


async def test_reenvio_anula_token(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, "00012345", "87654321")
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    token = await obter_token_redefinicao(cliente, usuario["email"])
    ambiente.relogio.avancar(UM_MINUTO)
    assert (await solicitar(cliente, usuario["email"])).status_code == (
        HTTPStatus.OK
    )
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.verificado_em is None
    assert linha.token_redefinicao_hash is None
    assert linha.utilizado_em is None
    assert linha.tentativas == 0
    anulado = await redefinir(cliente, token, NOVA_SENHA)
    assert anulado.status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(anulado) == "TOKEN_REDEFINICAO_INVALIDO"


async def fluxo_correto_e_incorreto(ambiente: Ambiente) -> None:
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    await solicitar(cliente, email)
    errada = await verificar(cliente, email, CODIGO_ERRADO)
    assert errada.status_code == HTTPStatus.BAD_REQUEST
    assert errada.json()["mensagem"] == MENSAGEM_CODIGO_INVALIDO
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.tentativas == 1
    certa = await verificar(cliente, email, CODIGO_PADRAO)
    assert certa.status_code == HTTPStatus.OK
    assert set(certa.json()) == {"token_redefinicao", "expira_em"}
    assert certa.headers["cache-control"] == "no-store"


async def fluxo_cinco_invalidas(ambiente: Ambiente) -> None:
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    await solicitar(cliente, email)
    for _ in range(5):
        invalida = await verificar(cliente, email, CODIGO_ERRADO)
        assert invalida.status_code == HTTPStatus.BAD_REQUEST
        assert codigo_de_erro(invalida) == "CODIGO_INVALIDO"
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.tentativas == 5
    sexta = await verificar(cliente, email, CODIGO_PADRAO)
    assert sexta.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert codigo_de_erro(sexta) == "TENTATIVAS_ESGOTADAS"
    assert sexta.headers["retry-after"] == "60"


async def fluxo_formato_do_codigo(ambiente: Ambiente) -> None:
    for codigo in ("١٢٣٤٥٦٧٨", "1234567", "abcdefgh", "123456789"):
        resposta = await verificar(ambiente.cliente, "x@exemplo.com", codigo)
        assert resposta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
        (campo,) = resposta.json()["campos"]
        assert (campo["campo"], campo["codigo"]) == (
            "codigo",
            "CODIGO_FORMATO",
        )
    ausente = await ambiente.cliente.post(
        "/api/v1/auth/recuperacao/verificar", json={"email": "x@exemplo.com"}
    )
    assert ausente.json()["campos"][0]["codigo"] == "CODIGO_FORMATO"


async def fluxo_expirado(ambiente: Ambiente) -> None:
    usuario = await registrar(ambiente.cliente)
    await solicitar(ambiente.cliente, usuario["email"])
    ambiente.relogio.avancar(DEZ_MINUTOS)
    resposta = await verificar(
        ambiente.cliente, usuario["email"], CODIGO_PADRAO
    )
    assert resposta.status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(resposta) == "CODIGO_EXPIRADO"


async def test_verificacao(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    await fluxo_correto_e_incorreto(ambiente)
    await fluxo_cinco_invalidas(ambiente)
    await fluxo_formato_do_codigo(ambiente)
    await fluxo_expirado(ambiente)


async def test_verificar_de_novo(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    usuario = await registrar(ambiente.cliente)
    email = usuario["email"]
    await obter_token_redefinicao(ambiente.cliente, email)
    antes = linha_recuperacao(ambiente.banco, usuario["id"])
    repetida = await verificar(ambiente.cliente, email, CODIGO_PADRAO)
    assert repetida.status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(repetida) == "CODIGO_JA_VERIFICADO"
    assert "token_redefinicao" not in repetida.text
    depois = linha_recuperacao(ambiente.banco, usuario["id"])
    assert antes is not None
    assert depois is not None
    assert depois.token_redefinicao_hash == antes.token_redefinicao_hash


async def test_redefinir(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    jwt_anterior = await entrar(cliente, email, SENHA_PADRAO)
    token = await obter_token_redefinicao(cliente, email)
    resposta = await redefinir(cliente, token, NOVA_SENHA)
    assert resposta.status_code == HTTPStatus.OK
    assert resposta.json() == {
        "mensagem": "Redefinição de senha concluída com sucesso"
    }
    nova = await cliente.post(
        URL_LOGIN, json={"email": email, "senha": NOVA_SENHA}
    )
    antiga = await cliente.post(
        URL_LOGIN, json={"email": email, "senha": SENHA_PADRAO}
    )
    assert nova.status_code == HTTPStatus.OK
    assert antiga.status_code == HTTPStatus.UNAUTHORIZED
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.utilizado_em == ambiente.relogio.agora()
    anterior = await cliente.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": f"Bearer {jwt_anterior}"},
    )
    assert anterior.status_code == HTTPStatus.UNAUTHORIZED


async def test_redefinir_invalido(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usado = await registrar(cliente)
    expirado = await registrar(cliente)
    token_usado = await obter_token_redefinicao(cliente, usado["email"])
    token_expirado = await obter_token_redefinicao(cliente, expirado["email"])

    diferentes = await cliente.post(
        URL_REDEFINIR,
        json={
            "token_redefinicao": token_usado,
            "nova_senha": NOVA_SENHA,
            "confirmar_senha": "outra-senha-789",
        },
    )
    assert diferentes.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert diferentes.json()["campos"][0]["codigo"] == "SENHAS_DIFERENTES"
    curta = await redefinir(cliente, token_usado, "curta1!")
    assert curta.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert curta.json()["campos"][0]["codigo"] == "SENHA_FRACA"

    inexistente = await redefinir(cliente, "x" * 43, NOVA_SENHA)
    assert inexistente.status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(inexistente) == "TOKEN_REDEFINICAO_INVALIDO"
    assert (
        await redefinir(cliente, token_usado, NOVA_SENHA)
    ).status_code == 200
    de_novo = await redefinir(cliente, token_usado, NOVA_SENHA)
    assert de_novo.status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(de_novo) == "TOKEN_REDEFINICAO_INVALIDO"

    ambiente.relogio.avancar(DEZ_MINUTOS)
    vencido = await redefinir(cliente, token_expirado, NOVA_SENHA)
    assert vencido.status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(vencido) == "TOKEN_REDEFINICAO_INVALIDO"


async def test_falha_de_envio(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, "00012345", "87654321", "11111111")
    cliente, enviador = ambiente.cliente, ambiente.enviador
    usuario = await registrar(cliente)
    email, uid = usuario["email"], usuario["id"]

    enviador.falha_programada = FalhaEnvioEmail("SMTPException")
    primeira = await solicitar(cliente, email)
    assert primeira.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert codigo_de_erro(primeira) == "FALHA_ENVIO_EMAIL"
    assert linha_recuperacao(ambiente.banco, uid) is None
    assert (await solicitar(cliente, email)).status_code == HTTPStatus.OK

    emitida = linha_recuperacao(ambiente.banco, uid)
    ambiente.relogio.avancar(UM_MINUTO)
    enviador.falha_programada = FalhaEnvioEmail("SMTPException")
    reenvio = await solicitar(cliente, email)
    assert reenvio.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert linha_recuperacao(ambiente.banco, uid) == emitida
    assert (await solicitar(cliente, email)).status_code == HTTPStatus.OK


async def test_limites_da_recuperacao(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente, relogio = ambiente.cliente, ambiente.relogio
    valido, vencido, reenvio = [await registrar(cliente) for _ in range(3)]
    for usuario in (valido, vencido, reenvio):
        await solicitar(cliente, usuario["email"])

    relogio.avancar(timedelta(seconds=59))
    cedo = await solicitar(cliente, reenvio["email"])
    assert cedo.status_code == HTTPStatus.TOO_MANY_REQUESTS
    relogio.avancar(timedelta(seconds=1))
    assert (await solicitar(cliente, reenvio["email"])).status_code == 200

    relogio.avancar(timedelta(seconds=539))
    no_limite = await verificar(cliente, valido["email"], CODIGO_PADRAO)
    assert no_limite.status_code == HTTPStatus.OK
    relogio.avancar(timedelta(seconds=1))
    expirado = await verificar(cliente, vencido["email"], CODIGO_PADRAO)
    assert codigo_de_erro(expirado) == "CODIGO_EXPIRADO"


class SessaoQueFalhaNoCommit(AsyncSession):
    """Sessão de teste cujo `commit` falha como um erro de banco."""

    @override
    async def commit(self) -> None:
        raise DBAPIError("COMMIT", None, Exception("falha sintética"))


def instalar_sessoes(
    app: FastAPI,
    engine: AsyncEngine,
    classe: type[AsyncSession] = AsyncSession,
) -> None:
    fabrica = async_sessionmaker(
        engine, class_=classe, expire_on_commit=False, autoflush=False
    )

    async def obter() -> AsyncIterator[AsyncSession]:
        async with fabrica() as sessao:
            yield sessao

    app.dependency_overrides[obter_sessao] = obter


async def test_commit_falha_depois_do_envio(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    usuario = await registrar(ambiente.cliente)
    engine = create_async_engine(ambiente.banco, poolclass=NullPool)
    try:
        instalar_sessoes(ambiente.app, engine, SessaoQueFalhaNoCommit)
        falha = await solicitar(ambiente.cliente, usuario["email"])
        assert falha.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR
        assert len(ambiente.enviador.enviadas) == 1
        assert linha_recuperacao(ambiente.banco, usuario["id"]) is None
        del ambiente.app.dependency_overrides[obter_sessao]
        nova = await solicitar(ambiente.cliente, usuario["email"])
        assert nova.status_code == HTTPStatus.OK
        assert len(ambiente.enviador.enviadas) == 2
    finally:
        await engine.dispose()


async def test_expira_em_utc_com_sessao_em_outro_fuso(
    ambiente: Ambiente, monkeypatch: pytest.MonkeyPatch
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    usuario = await registrar(ambiente.cliente)
    solicitacao = await solicitar(ambiente.cliente, usuario["email"])
    assert solicitacao.json()["expira_em"] == "2026-10-13T12:10:00Z"
    engine = create_async_engine(
        ambiente.banco,
        poolclass=NullPool,
        connect_args={"options": "-c TimeZone=America/Sao_Paulo"},
    )
    try:
        instalar_sessoes(ambiente.app, engine)
        resposta = await verificar(
            ambiente.cliente, usuario["email"], CODIGO_PADRAO
        )
        assert resposta.status_code == HTTPStatus.OK
        assert resposta.json()["expira_em"] == "2026-10-13T12:10:00Z"
    finally:
        await engine.dispose()
