import asyncio
import uuid
from collections.abc import Callable
from datetime import timedelta
from http import HTTPStatus

import psycopg
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from api_gestao_pessoal.seguranca import hash_token

from ..apoio.identidade import (
    CODIGO_PADRAO,
    ESPERA_FOR_UPDATE,
    ESPERA_INSERT_RECUPERACAO,
    ESPERA_UPDATE_USUARIO,
    SENHA_PADRAO,
    URL_LOGIN,
    URL_USUARIO_ATUAL,
    aguardar_espera_por_trava,
    codigo_de_erro,
    disparar_em_ordem,
    disparar_simultaneas,
    entrar,
    linha_recuperacao,
    obter_token_redefinicao,
    redefinir,
    registrar,
    solicitar,
    verificar,
)
from .conftest import Ambiente
from .test_recuperacao import contar_recuperacoes, forcar_codigos

NOVA_SENHA = "nova-senha-456"
CODIGO_ERRADO = "99999999"
UM_MINUTO = timedelta(seconds=60)
Bloqueadoras = Callable[[], psycopg.Connection]


def travar_linha(
    abrir_bloqueadora: Bloqueadoras, usuario_id: str
) -> psycopg.Connection:
    """Bloqueadora: `FOR UPDATE` na linha de recuperação do usuário."""
    conexao = abrir_bloqueadora()
    conexao.execute(
        "SELECT id FROM recuperacao_senha WHERE usuario_id = %s FOR UPDATE",
        (uuid.UUID(usuario_id),),
    )
    return conexao


async def login_status(ambiente: Ambiente, email: str, senha: str) -> int:
    resposta = await ambiente.cliente.post(
        URL_LOGIN, json={"email": email, "senha": senha}
    )
    return resposta.status_code


@pytest.mark.concorrencia
async def test_verificacoes_corretas_simultaneas(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    await solicitar(cliente, email)
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    respostas = await disparar_simultaneas(
        bloqueadora,
        monitor,
        [verificar(cliente, email, CODIGO_PADRAO) for _ in range(2)],
        ESPERA_FOR_UPDATE,
        2,
    )
    assert sorted(r.status_code for r in respostas) == [
        HTTPStatus.OK,
        HTTPStatus.CONFLICT,
    ]
    vencedora = next(r for r in respostas if r.status_code == HTTPStatus.OK)
    perdedora = next(r for r in respostas if r.status_code != HTTPStatus.OK)
    assert codigo_de_erro(perdedora) == "CODIGO_JA_VERIFICADO"
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.token_redefinicao_hash == hash_token(
        vencedora.json()["token_redefinicao"]
    )


@pytest.mark.concorrencia
async def test_cinco_invalidas_simultaneas(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    await solicitar(cliente, email)
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    invalidos = [str(digito) * 8 for digito in range(1, 6)]
    respostas = await disparar_simultaneas(
        bloqueadora,
        monitor,
        [verificar(cliente, email, codigo) for codigo in invalidos],
        ESPERA_FOR_UPDATE,
        5,
    )
    assert [r.status_code for r in respostas] == [HTTPStatus.BAD_REQUEST] * 5
    assert {codigo_de_erro(r) for r in respostas} == {"CODIGO_INVALIDO"}
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.tentativas == 5
    sexta = await verificar(cliente, email, CODIGO_PADRAO)
    assert sexta.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert codigo_de_erro(sexta) == "TENTATIVAS_ESGOTADAS"
    assert "retry-after" in sexta.headers


@pytest.mark.concorrencia
async def test_redefinicoes_simultaneas(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    token = await obter_token_redefinicao(cliente, usuario["email"])
    senhas = ["senha-nova-aaa-1", "senha-nova-bbb-2"]
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    respostas = await disparar_simultaneas(
        bloqueadora,
        monitor,
        [redefinir(cliente, token, senha) for senha in senhas],
        ESPERA_FOR_UPDATE,
        2,
    )
    assert sorted(r.status_code for r in respostas) == [
        HTTPStatus.OK,
        HTTPStatus.BAD_REQUEST,
    ]
    perdedora = next(r for r in respostas if r.status_code != HTTPStatus.OK)
    assert codigo_de_erro(perdedora) == "TOKEN_REDEFINICAO_INVALIDO"
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.utilizado_em == ambiente.relogio.agora()
    entradas = [
        await login_status(ambiente, usuario["email"], s) for s in senhas
    ]
    assert sorted(entradas) == [HTTPStatus.OK, HTTPStatus.UNAUTHORIZED]


@pytest.mark.concorrencia
@pytest.mark.parametrize(
    "verificar_primeiro",
    [
        pytest.param(True, id="verificar_antes"),
        pytest.param(False, id="reenviar_antes"),
    ],
)
async def test_reenvio_e_verificacao(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
    verificar_primeiro: bool,
) -> None:
    forcar_codigos(monkeypatch, "00012345", "87654321")
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    assert (await solicitar(cliente, email)).status_code == HTTPStatus.OK
    ambiente.relogio.avancar(UM_MINUTO)
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    verificacao = verificar(cliente, email, "00012345")
    reenvio = solicitar(cliente, email)
    ordem = (
        [verificacao, reenvio]
        if verificar_primeiro
        else [reenvio, verificacao]
    )
    respostas = await disparar_em_ordem(
        bloqueadora, monitor, ordem, ESPERA_FOR_UPDATE
    )
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    if verificar_primeiro:
        assert [r.status_code for r in respostas] == [HTTPStatus.OK] * 2
        assert linha.token_redefinicao_hash is None
        assert linha.verificado_em is None
        assert linha.tentativas == 0
    else:
        assert respostas[0].status_code == HTTPStatus.OK
        assert respostas[1].status_code == HTTPStatus.BAD_REQUEST
        assert codigo_de_erro(respostas[1]) == "CODIGO_INVALIDO"
        assert linha.tentativas == 1


@pytest.mark.concorrencia
async def test_primeiras_solicitacoes_simultaneas(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    bloqueadora = abrir_bloqueadora()
    bloqueadora.execute(
        "INSERT INTO recuperacao_senha (id, usuario_id, codigo_hash, "
        "expira_em) VALUES (%s, %s, 'x', now())",
        (uuid.uuid7(), uuid.UUID(usuario["id"])),
    )
    respostas = await disparar_simultaneas(
        bloqueadora,
        monitor,
        [solicitar(cliente, usuario["email"]) for _ in range(2)],
        ESPERA_INSERT_RECUPERACAO,
        2,
    )
    assert sorted(r.status_code for r in respostas) == [
        HTTPStatus.OK,
        HTTPStatus.TOO_MANY_REQUESTS,
    ]
    assert contar_recuperacoes(ambiente.banco) == 1
    assert len(ambiente.enviador.enviadas) == 1


@pytest.mark.concorrencia
@pytest.mark.parametrize(
    "redefinir_primeiro",
    [
        pytest.param(True, id="redefinir_antes"),
        pytest.param(False, id="reenviar_antes"),
    ],
)
async def test_reenvio_e_redefinicao(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
    redefinir_primeiro: bool,
) -> None:
    forcar_codigos(monkeypatch, "00012345", "87654321")
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    token = await obter_token_redefinicao(cliente, email)
    ambiente.relogio.avancar(UM_MINUTO)
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    troca = redefinir(cliente, token, NOVA_SENHA)
    reenvio = solicitar(cliente, email)
    ordem = [troca, reenvio] if redefinir_primeiro else [reenvio, troca]
    respostas = await disparar_em_ordem(
        bloqueadora, monitor, ordem, ESPERA_FOR_UPDATE
    )
    if redefinir_primeiro:
        assert [r.status_code for r in respostas] == [HTTPStatus.OK] * 2
        assert await login_status(ambiente, email, NOVA_SENHA) == HTTPStatus.OK
        return
    assert respostas[0].status_code == HTTPStatus.OK
    assert respostas[1].status_code == HTTPStatus.BAD_REQUEST
    assert codigo_de_erro(respostas[1]) == "TOKEN_REDEFINICAO_INVALIDO"
    assert await login_status(ambiente, email, SENHA_PADRAO) == HTTPStatus.OK
    assert await login_status(ambiente, email, NOVA_SENHA) == (
        HTTPStatus.UNAUTHORIZED
    )


@pytest.mark.concorrencia
async def test_reenvios_simultaneos(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sequencia = forcar_codigos(monkeypatch, "00012345", "11111111")
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    assert (await solicitar(cliente, email)).status_code == HTTPStatus.OK
    ambiente.relogio.avancar(UM_MINUTO)
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    respostas = await disparar_simultaneas(
        bloqueadora,
        monitor,
        [solicitar(cliente, email) for _ in range(2)],
        ESPERA_FOR_UPDATE,
        2,
    )
    assert sorted(r.status_code for r in respostas) == [
        HTTPStatus.OK,
        HTTPStatus.TOO_MANY_REQUESTS,
    ]
    perdedora = next(r for r in respostas if r.status_code != HTTPStatus.OK)
    assert codigo_de_erro(perdedora) == "REENVIO_MUITO_FREQUENTE"
    assert perdedora.headers["retry-after"] == "60"
    assert sequencia.chamadas == 2
    assert len(ambiente.enviador.enviadas) == 2
    assert "11111111" in ambiente.enviador.enviadas[1].corpo
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.tentativas == 0
    assert linha.verificado_em is None
    assert linha.token_redefinicao_hash is None
    assert linha.utilizado_em is None
    assert linha.expira_em == ambiente.relogio.agora() + timedelta(minutes=10)
    antigo = await verificar(cliente, email, "00012345")
    assert codigo_de_erro(antigo) == "CODIGO_INVALIDO"
    novo = await verificar(cliente, email, "11111111")
    assert novo.status_code == HTTPStatus.OK


@pytest.mark.concorrencia
@pytest.mark.parametrize(
    "invalida_primeiro",
    [
        pytest.param(True, id="invalida_antes"),
        pytest.param(False, id="correta_antes"),
    ],
)
async def test_verificacao_correta_e_limite(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
    invalida_primeiro: bool,
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    await solicitar(cliente, email)
    for _ in range(4):
        sequencial = await verificar(cliente, email, CODIGO_ERRADO)
        assert sequencial.status_code == HTTPStatus.BAD_REQUEST
    antes = linha_recuperacao(ambiente.banco, usuario["id"])
    assert antes is not None
    assert antes.tentativas == 4
    bloqueadora = travar_linha(abrir_bloqueadora, usuario["id"])
    invalida = verificar(cliente, email, CODIGO_ERRADO)
    correta = verificar(cliente, email, CODIGO_PADRAO)
    ordem = [invalida, correta] if invalida_primeiro else [correta, invalida]
    respostas = await disparar_em_ordem(
        bloqueadora, monitor, ordem, ESPERA_FOR_UPDATE
    )
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    if invalida_primeiro:
        assert respostas[0].status_code == HTTPStatus.BAD_REQUEST
        assert codigo_de_erro(respostas[0]) == "CODIGO_INVALIDO"
        assert respostas[1].status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert codigo_de_erro(respostas[1]) == "TENTATIVAS_ESGOTADAS"
        assert respostas[1].headers["retry-after"] == "60"
        assert linha.tentativas == 5
        assert linha.verificado_em is None
        assert linha.token_redefinicao_hash is None
        return
    assert respostas[0].status_code == HTTPStatus.OK
    assert respostas[1].status_code == HTTPStatus.CONFLICT
    assert codigo_de_erro(respostas[1]) == "CODIGO_JA_VERIFICADO"
    assert linha.tentativas == 4
    assert linha.verificado_em is not None
    assert linha.token_redefinicao_hash == hash_token(
        respostas[0].json()["token_redefinicao"]
    )


@pytest.mark.concorrencia
async def test_login_durante_redefinicao(
    ambiente: Ambiente,
    monitor: AsyncEngine,
    abrir_bloqueadora: Bloqueadoras,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forcar_codigos(monkeypatch, CODIGO_PADRAO)
    cliente = ambiente.cliente
    usuario = await registrar(cliente)
    email = usuario["email"]
    token_t1 = await entrar(cliente, email, SENHA_PADRAO)
    token_r = await obter_token_redefinicao(cliente, email)
    bloqueadora = abrir_bloqueadora()
    bloqueadora.execute(
        "SELECT id FROM usuario WHERE id = %s FOR UPDATE",
        (uuid.UUID(usuario["id"]),),
    )
    tarefa = asyncio.create_task(redefinir(cliente, token_r, NOVA_SENHA))
    try:
        await aguardar_espera_por_trava(monitor, 1, ESPERA_UPDATE_USUARIO)
        token_t2 = await entrar(cliente, email, SENHA_PADRAO)
        com_t1 = await cliente.get(
            URL_USUARIO_ATUAL, headers={"Authorization": f"Bearer {token_t1}"}
        )
        assert com_t1.status_code == HTTPStatus.OK
        assert not tarefa.done()
    finally:
        bloqueadora.rollback()
    redefinicao = await tarefa
    assert redefinicao.status_code == HTTPStatus.OK
    assert redefinicao.json()["mensagem"] == (
        "Redefinição de senha concluída com sucesso"
    )
    for token in (token_t1, token_t2):
        recusado = await cliente.get(
            URL_USUARIO_ATUAL, headers={"Authorization": f"Bearer {token}"}
        )
        assert recusado.status_code == HTTPStatus.UNAUTHORIZED
        assert codigo_de_erro(recusado) == "NAO_AUTENTICADO"
    antiga = await cliente.post(
        URL_LOGIN, json={"email": email, "senha": SENHA_PADRAO}
    )
    assert antiga.status_code == HTTPStatus.UNAUTHORIZED
    assert codigo_de_erro(antiga) == "CREDENCIAIS_INVALIDAS"
    assert await login_status(ambiente, email, NOVA_SENHA) == HTTPStatus.OK
    linha = linha_recuperacao(ambiente.banco, usuario["id"])
    assert linha is not None
    assert linha.utilizado_em is not None
