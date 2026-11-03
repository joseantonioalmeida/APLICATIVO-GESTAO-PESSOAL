import uuid
from datetime import date

from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.models import Usuario

from ..apoio.esquema import SQLSTATE_NOT_NULL, esperar_violacao, inserir


async def test_orm_gera_uuid_v7(sessao_orm: AsyncSession) -> None:
    usuario = Usuario(
        nome_completo="Pessoa Teste",
        email=f"{uuid.uuid7().hex}@exemplo.com",
        senha_hash="hash-ficticio",
        data_nascimento=date(1990, 1, 1),
        fuso_horario="America/Sao_Paulo",
    )
    sessao_orm.add(usuario)
    await sessao_orm.flush()
    assert isinstance(usuario.id, uuid.UUID)
    assert usuario.id.version == 7
    assert usuario.criado_em is not None
    assert "criado_em" not in inspect(usuario).expired_attributes


def test_sql_textual_sem_id_rejeitado(conexao: Connection) -> None:
    esperar_violacao(
        conexao,
        SQLSTATE_NOT_NULL,
        lambda: inserir(
            conexao,
            "usuario",
            {
                "nome_completo": "Pessoa Teste",
                "email": f"{uuid.uuid7().hex}@exemplo.com",
                "senha_hash": "hash-ficticio",
                "data_nascimento": date(1990, 1, 1),
                "fuso_horario": "America/Sao_Paulo",
            },
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_NOT_NULL,
        lambda: inserir(conexao, "categoria_atividade", {"nome": "Teste"}),
    )
