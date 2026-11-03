import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Connection, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session

from api_gestao_pessoal.models import RequisicaoIdempotente, Usuario

from ..apoio.esquema import (
    SQLSTATE_NUMERICO_EXCEDIDO,
    esperar_violacao,
    inserir_importancia,
    inserir_lembrete,
    inserir_movimentacao,
    inserir_notificacao,
    inserir_requisicao,
    inserir_usuario,
)


def _novo_usuario() -> Usuario:
    return Usuario(
        nome_completo="Pessoa Teste",
        email=f"{uuid.uuid7().hex}@exemplo.com",
        senha_hash="hash-ficticio",
        data_nascimento=date(1990, 1, 1),
        fuso_horario="America/Sao_Paulo",
    )


def test_decimal_ida_e_volta(conexao: Connection) -> None:
    usuario = inserir_usuario(conexao)
    for valor in (Decimal("0.01"), Decimal("9999999999.99")):
        movimentacao = inserir_movimentacao(conexao, usuario, valor=valor)
        lido = conexao.execute(
            text("SELECT valor FROM movimentacao_financeira WHERE id = :id"),
            {"id": movimentacao},
        ).scalar_one()
        assert isinstance(lido, Decimal)
        assert lido == valor
        assert str(lido) == str(valor)
    esperar_violacao(
        conexao,
        SQLSTATE_NUMERICO_EXCEDIDO,
        lambda: inserir_movimentacao(
            conexao, usuario, valor=Decimal("10000000000.00")
        ),
    )


async def test_json_none_vira_null_sql(sessao_orm: AsyncSession) -> None:
    usuario = _novo_usuario()
    sessao_orm.add(usuario)
    await sessao_orm.flush()
    sem_resposta = RequisicaoIdempotente(
        usuario_id=usuario.id,
        chave=uuid.uuid7().hex,
        acao="CADASTRAR_DESPESA",
        conteudo_hash="0" * 64,
        resposta=None,
    )
    com_resposta = RequisicaoIdempotente(
        usuario_id=usuario.id,
        chave=uuid.uuid7().hex,
        acao="CADASTRAR_DESPESA",
        conteudo_hash="0" * 64,
        resposta={"id": "abc"},
    )
    sessao_orm.add_all([sem_resposta, com_resposta])
    await sessao_orm.flush()
    e_nulo = await sessao_orm.execute(
        text(
            "SELECT resposta IS NULL FROM requisicao_idempotente "
            "WHERE id = :id"
        ),
        {"id": sem_resposta.id},
    )
    assert e_nulo.scalar_one() is True
    texto = await sessao_orm.execute(
        text(
            "SELECT resposta::text FROM requisicao_idempotente WHERE id = :id"
        ),
        {"id": com_resposta.id},
    )
    assert texto.scalar_one() == '{"id": "abc"}'


def _inserir_dependentes(sessao: Session, usuario_id: uuid.UUID) -> None:
    conexao = sessao.connection()
    importancia = inserir_importancia(conexao, usuario_id)
    lembrete = inserir_lembrete(conexao, usuario_id, importancia)
    inserir_notificacao(conexao, usuario_id, lembrete)
    inserir_requisicao(conexao, usuario_id)


async def test_timestamps(
    fabrica_sessoes: async_sessionmaker[AsyncSession],
) -> None:
    controlados = {"criado_em", "atualizado_em"}

    # Transação 1: o INSERT do ORM recebe os padrões do banco por RETURNING.
    async with fabrica_sessoes() as sessao:
        t1 = (await sessao.execute(text("SELECT now()"))).scalar_one()
        usuario = _novo_usuario()
        sessao.add(usuario)
        await sessao.flush()
        assert usuario.criado_em == t1
        assert usuario.atualizado_em == t1
        assert not controlados & inspect(usuario).expired_attributes
        usuario_id = usuario.id
        await sessao.commit()

    # Transação 2: o UPDATE do ORM acrescenta atualizado_em = now().
    async with fabrica_sessoes() as sessao:
        t2 = (await sessao.execute(text("SELECT now()"))).scalar_one()
        carregado = await sessao.get(Usuario, usuario_id)
        assert carregado is not None
        carregado.nome_completo = "Pessoa Alterada"
        await sessao.flush()
        assert not controlados & inspect(carregado).expired_attributes
        assert carregado.atualizado_em == t2
        assert carregado.criado_em == t1
        assert t2 > t1
        await sessao.commit()

    # Transação 3: UPDATE em SQL textual não passa pelo onupdate.
    async with fabrica_sessoes() as sessao:
        await sessao.execute(
            text(
                "UPDATE usuario SET nome_completo = 'Pessoa Textual' "
                "WHERE id = :id"
            ),
            {"id": usuario_id},
        )
        await sessao.commit()

    # Transação 4: o nome mudou e atualizado_em continua o da transação 2.
    async with fabrica_sessoes() as sessao:
        linha = (
            await sessao.execute(
                text(
                    "SELECT nome_completo, atualizado_em FROM usuario "
                    "WHERE id = :id"
                ),
                {"id": usuario_id},
            )
        ).one()
        assert linha[0] == "Pessoa Textual"
        assert linha[1] == t2

    # Transação 5: criada_em e criado_em das tabelas sem mixin.
    async with fabrica_sessoes() as sessao:
        t5 = (await sessao.execute(text("SELECT now()"))).scalar_one()
        await sessao.run_sync(_inserir_dependentes, usuario_id)
        linha = (
            await sessao.execute(
                text(
                    "SELECT n.criada_em, r.criado_em "
                    "FROM notificacao n, requisicao_idempotente r "
                    "WHERE n.usuario_id = :id AND r.usuario_id = :id"
                ),
                {"id": usuario_id},
            )
        ).one()
        assert linha[0] == t5
        assert linha[1] == t5
