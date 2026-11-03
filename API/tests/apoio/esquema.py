"""Apoio dos testes de esquema: SQLSTATE, violações e linhas válidas."""

import uuid
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Any, LiteralString

import psycopg
import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError

from .banco import url_libpq

SQLSTATE_NOT_NULL = "23502"
SQLSTATE_FK = "23503"
SQLSTATE_UNICO = "23505"
SQLSTATE_CHECK = "23514"
SQLSTATE_TEXTO_LONGO = "22001"
SQLSTATE_NUMERICO_EXCEDIDO = "22003"

MOMENTO = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)


def esperar_violacao(
    conexao: Connection, sqlstate: str, acao: Callable[[], object]
) -> None:
    """Exige que `acao` viole o SQLSTATE; o SAVEPOINT preserva a transação."""

    def tentar() -> None:
        with conexao.begin_nested():
            acao()

    with pytest.raises(DBAPIError) as info:
        tentar()
    assert getattr(info.value.orig, "sqlstate", None) == sqlstate


def inserir(
    conexao: Connection, tabela: str, valores: Mapping[str, object]
) -> None:
    """INSERT textual com parâmetros vinculados."""
    colunas = list(valores)
    nomes = ", ".join(colunas)
    marcas = ", ".join(f":{coluna}" for coluna in colunas)
    conexao.execute(
        text(f"INSERT INTO {tabela} ({nomes}) VALUES ({marcas})"),
        dict(valores),
    )


def consultar(url: str, instrucao: LiteralString) -> list[tuple[Any, ...]]:
    """Consulta por conexão independente da transação do teste."""
    with psycopg.connect(url_libpq(url)) as conexao:
        return [tuple(linha) for linha in conexao.execute(instrucao)]


def id_categoria(
    conexao: Connection, tabela: str, nome: str, tipo: str | None = None
) -> uuid.UUID:
    """`id` de uma categoria do catálogo, pela chave natural."""
    if tipo is None:
        instrucao = text(f"SELECT id FROM {tabela} WHERE nome = :nome")
        return conexao.execute(instrucao, {"nome": nome}).scalar_one()
    instrucao = text(
        f"SELECT id FROM {tabela} WHERE nome = :nome AND tipo = :tipo"
    )
    return conexao.execute(
        instrucao, {"nome": nome, "tipo": tipo}
    ).scalar_one()


def _inserir_com_id(
    conexao: Connection, tabela: str, valores: Mapping[str, object]
) -> uuid.UUID:
    if "id" in valores:
        msg = "o id é gerado pela fábrica"
        raise ValueError(msg)
    identificador = uuid.uuid7()
    inserir(conexao, tabela, {"id": identificador, **valores})
    return identificador


def inserir_usuario(conexao: Connection, **campos: Any) -> uuid.UUID:
    valores: dict[str, Any] = {
        "nome_completo": "Pessoa Teste",
        "email": f"{uuid.uuid7().hex}@exemplo.com",
        "senha_hash": "hash-ficticio",
        "data_nascimento": date(1990, 1, 1),
        "fuso_horario": "America/Sao_Paulo",
    } | campos
    return _inserir_com_id(conexao, "usuario", valores)


def inserir_serie_atividade(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "nome_padrao": "Estudar",
        "periodicidade": "SEMANAL",
        "data_referencia": date(2026, 10, 8),
        "horario_inicial_padrao": time(8, 0),
        "horario_final_padrao": time(10, 0),
    } | campos
    if "categoria_id" not in valores:
        valores["categoria_id"] = id_categoria(
            conexao, "categoria_atividade", "Estudo"
        )
    return _inserir_com_id(conexao, "serie_atividade", valores)


def inserir_atividade(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "nome": "Estudar para a prova",
        "data_atividade": date(2026, 10, 8),
        "horario_inicial": time(8, 0),
        "horario_final": time(10, 0),
    } | campos
    if "categoria_id" not in valores:
        valores["categoria_id"] = id_categoria(
            conexao, "categoria_atividade", "Estudo"
        )
    return _inserir_com_id(conexao, "atividade", valores)


def inserir_serie_importancia(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "nome_padrao": "Pagamento da internet",
        "periodicidade": "MENSAL",
        "data_referencia": date(2026, 10, 15),
    } | campos
    if "categoria_id" not in valores:
        valores["categoria_id"] = id_categoria(
            conexao, "categoria_importancia", "Contas"
        )
    return _inserir_com_id(conexao, "serie_importancia", valores)


def inserir_importancia(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "nome": "Pagamento da internet",
        "data_compromisso": date(2026, 10, 15),
    } | campos
    if "categoria_id" not in valores:
        valores["categoria_id"] = id_categoria(
            conexao, "categoria_importancia", "Contas"
        )
    return _inserir_com_id(conexao, "importancia", valores)


def inserir_movimentacao(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "tipo": "DESPESA",
        "nome": "Pagamento da internet",
        "valor": Decimal("105.00"),
        "data_movimentacao": date(2026, 10, 15),
    } | campos
    if "categoria_id" not in valores:
        if valores["tipo"] == "RECEITA":
            valores["categoria_id"] = id_categoria(
                conexao, "categoria_financeira", "Salário", "RECEITA"
            )
        else:
            valores["categoria_id"] = id_categoria(
                conexao, "categoria_financeira", "Contas", "DESPESA"
            )
    return _inserir_com_id(conexao, "movimentacao_financeira", valores)


def inserir_lembrete(
    conexao: Connection,
    usuario_id: uuid.UUID,
    importancia_id: uuid.UUID,
    **campos: Any,
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "importancia_id": importancia_id,
        "antecedencia_dias": 3,
        "horario": time(9, 0),
        "agendado_para": datetime(2026, 10, 12, 12, 0, tzinfo=UTC),
    } | campos
    return _inserir_com_id(conexao, "lembrete_importancia", valores)


def inserir_notificacao(
    conexao: Connection,
    usuario_id: uuid.UUID,
    lembrete_id: uuid.UUID,
    **campos: Any,
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "lembrete_id": lembrete_id,
        "versao_agendamento": 1,
        "titulo": "Lembrete",
        "mensagem": "Pagamento da internet",
    } | campos
    return _inserir_com_id(conexao, "notificacao", valores)


def inserir_recuperacao(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "codigo_hash": "hash-ficticio",
        "expira_em": datetime(2026, 10, 13, 12, 10, tzinfo=UTC),
    } | campos
    return _inserir_com_id(conexao, "recuperacao_senha", valores)


def inserir_requisicao(
    conexao: Connection, usuario_id: uuid.UUID, **campos: Any
) -> uuid.UUID:
    valores: dict[str, Any] = {
        "usuario_id": usuario_id,
        "chave": uuid.uuid7().hex,
        "acao": "CADASTRAR_DESPESA",
        "conteudo_hash": "0" * 64,
    } | campos
    return _inserir_com_id(conexao, "requisicao_idempotente", valores)
