import uuid
from datetime import datetime, timedelta
from http import HTTPStatus

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from ..apoio.esquema import inserir_importancia
from ..apoio.identidade import (
    SENHA_PADRAO,
    URL_USUARIO_ATUAL,
    codigo_de_erro,
    entrar,
    registrar,
)
from .conftest import Ambiente


def cabecalho(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_usuario_atual(ambiente: Ambiente) -> None:
    usuario = await registrar(
        ambiente.cliente,
        nome_completo="Maria da Silva",
        email="Maria@Exemplo.com",
        data_nascimento="1985-03-20",
    )
    token = await entrar(ambiente.cliente, usuario["email"], SENHA_PADRAO)
    resposta = await ambiente.cliente.get(
        URL_USUARIO_ATUAL, headers=cabecalho(token)
    )
    assert resposta.status_code == HTTPStatus.OK
    assert set(resposta.json()) == {
        "id",
        "nome_completo",
        "email",
        "data_nascimento",
        "fuso_horario",
    }
    assert resposta.json() == usuario
    assert usuario["email"] == "maria@exemplo.com"


async def test_hoje_no_fuso(ambiente: Ambiente) -> None:
    usuario = await registrar(ambiente.cliente)
    token = await entrar(ambiente.cliente, usuario["email"], SENHA_PADRAO)
    ambiente.relogio.avancar(timedelta(hours=14, minutes=30))
    resposta = await ambiente.cliente.get(
        "/teste/contexto", headers=cabecalho(token)
    )
    assert resposta.status_code == HTTPStatus.OK
    corpo = resposta.json()
    assert corpo["hoje"] == "2026-10-13"
    assert corpo["fuso"] == "America/Sao_Paulo"
    assert corpo["usuario_id"] == usuario["id"]
    assert datetime.fromisoformat(corpo["agora"]) == ambiente.relogio.agora()


async def test_obter_do_usuario_ou_404(ambiente: Ambiente) -> None:
    dono = await registrar(ambiente.cliente)
    outro = await registrar(ambiente.cliente)
    token_outro = await entrar(ambiente.cliente, outro["email"], SENHA_PADRAO)
    token_dono = await entrar(ambiente.cliente, dono["email"], SENHA_PADRAO)
    engine = create_engine(ambiente.banco, poolclass=NullPool)
    try:
        with engine.begin() as conexao:
            importancia = inserir_importancia(conexao, uuid.UUID(dono["id"]))
    finally:
        engine.dispose()
    url = f"/teste/importancias/{importancia}"
    alheia = await ambiente.cliente.get(url, headers=cabecalho(token_outro))
    assert alheia.status_code == HTTPStatus.NOT_FOUND
    assert codigo_de_erro(alheia) == "RECURSO_NAO_ENCONTRADO"
    inexistente = await ambiente.cliente.get(
        f"/teste/importancias/{uuid.uuid7()}", headers=cabecalho(token_outro)
    )
    assert inexistente.json() | {"id_requisicao": ""} == alheia.json() | {
        "id_requisicao": ""
    }
    malformado = await ambiente.cliente.get(
        "/teste/importancias/nao-e-uuid", headers=cabecalho(token_dono)
    )
    assert malformado.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    propria = await ambiente.cliente.get(url, headers=cabecalho(token_dono))
    assert propria.status_code == HTTPStatus.OK
    assert propria.json() == {"id": str(importancia)}
