"""Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).

Revision ID: 0001
Revises:
Create Date: 2026-10-13 14:21:22.519321

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import Insert, insert

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CATEGORIAS_ATIVIDADE = (
    "Trabalho",
    "Estudo",
    "Saúde",
    "Pessoal",
    "Lazer",
    "Outros",
)
CATEGORIAS_IMPORTANCIA = (
    "Contas",
    "Compras",
    "Veículo",
    "Lazer",
    "Saúde",
    "Educação",
    "Pessoal",
    "Outros",
)
CATEGORIAS_RECEITA = (
    "Salário",
    "Trabalho autônomo",
    "Vendas",
    "Rendimentos",
    "Reembolsos",
    "Outros",
)
CATEGORIAS_DESPESA = (
    "Alimentação",
    "Transporte",
    "Moradia",
    "Contas",
    "Compras",
    "Saúde",
    "Educação",
    "Lazer",
    "Veículo",
    "Outros",
)


def instrucoes_categorias() -> list[Insert]:
    """INSERTs idempotentes das 30 categorias, com UUIDv7 gerado agora."""
    categoria_atividade = sa.table(
        "categoria_atividade",
        sa.column("id", sa.Uuid()),
        sa.column("nome", sa.String()),
    )
    categoria_importancia = sa.table(
        "categoria_importancia",
        sa.column("id", sa.Uuid()),
        sa.column("nome", sa.String()),
    )
    categoria_financeira = sa.table(
        "categoria_financeira",
        sa.column("id", sa.Uuid()),
        sa.column("tipo", sa.String()),
        sa.column("nome", sa.String()),
    )
    financeiras = [
        {"id": uuid.uuid7(), "tipo": "RECEITA", "nome": nome}
        for nome in CATEGORIAS_RECEITA
    ] + [
        {"id": uuid.uuid7(), "tipo": "DESPESA", "nome": nome}
        for nome in CATEGORIAS_DESPESA
    ]
    return [
        insert(categoria_atividade)
        .values([
            {"id": uuid.uuid7(), "nome": nome} for nome in CATEGORIAS_ATIVIDADE
        ])
        .on_conflict_do_nothing(index_elements=["nome"]),
        insert(categoria_importancia)
        .values([
            {"id": uuid.uuid7(), "nome": nome}
            for nome in CATEGORIAS_IMPORTANCIA
        ])
        .on_conflict_do_nothing(index_elements=["nome"]),
        insert(categoria_financeira)
        .values(financeiras)
        .on_conflict_do_nothing(index_elements=["tipo", "nome"]),
    ]


def upgrade() -> None:
    """Aplica a migração."""
    op.create_table(
        "categoria_atividade",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=50), nullable=False),
        sa.Column(
            "ativa",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categoria_atividade")),
        sa.UniqueConstraint("nome", name=op.f("uq_categoria_atividade_nome")),
    )
    op.create_table(
        "categoria_financeira",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=50), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "RECEITA",
                "DESPESA",
                name="tipo",
                native_enum=False,
                create_constraint=True,
                length=7,
            ),
            nullable=False,
        ),
        sa.Column(
            "ativa",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categoria_financeira")),
        sa.UniqueConstraint(
            "id", "tipo", name=op.f("uq_categoria_financeira_id_tipo")
        ),
        sa.UniqueConstraint(
            "tipo", "nome", name=op.f("uq_categoria_financeira_tipo_nome")
        ),
    )
    op.create_table(
        "categoria_importancia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=50), nullable=False),
        sa.Column(
            "ativa",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categoria_importancia")),
        sa.UniqueConstraint(
            "nome", name=op.f("uq_categoria_importancia_nome")
        ),
    )
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome_completo", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("data_nascimento", sa.Date(), nullable=False),
        sa.Column("fuso_horario", sa.String(length=64), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuario")),
        sa.UniqueConstraint("email", name=op.f("uq_usuario_email")),
    )
    op.create_table(
        "recuperacao_senha",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("codigo_hash", sa.String(length=255), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "tentativas",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("verificado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "token_redefinicao_hash", sa.String(length=64), nullable=True
        ),
        sa.Column("utilizado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_recuperacao_senha_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recuperacao_senha")),
        sa.UniqueConstraint(
            "token_redefinicao_hash",
            name=op.f("uq_recuperacao_senha_token_redefinicao_hash"),
        ),
        sa.UniqueConstraint(
            "usuario_id", name=op.f("uq_recuperacao_senha_usuario_id")
        ),
    )
    op.create_table(
        "requisicao_idempotente",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("chave", sa.String(length=64), nullable=False),
        sa.Column("acao", sa.String(length=50), nullable=False),
        sa.Column("conteudo_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "situacao",
            sa.Enum(
                "EM_PROCESSAMENTO",
                "CONCLUIDA",
                name="situacao",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            server_default=sa.text("'EM_PROCESSAMENTO'"),
            nullable=False,
        ),
        sa.Column("codigo_resposta", sa.SmallInteger(), nullable=True),
        sa.Column("resposta", sa.JSON(none_as_null=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("concluida_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_requisicao_idempotente_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_requisicao_idempotente")),
        sa.UniqueConstraint(
            "usuario_id",
            "acao",
            "chave",
            name=op.f("uq_requisicao_idempotente_usuario_id_acao_chave"),
        ),
    )
    op.create_table(
        "serie_atividade",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_id", sa.Uuid(), nullable=False),
        sa.Column("nome_padrao", sa.String(length=100), nullable=False),
        sa.Column("descricao_padrao", sa.String(length=200), nullable=True),
        sa.Column(
            "prioridade_padrao",
            sa.Enum(
                "BAIXA",
                "MEDIA",
                "ALTA",
                name="prioridade_padrao",
                native_enum=False,
                create_constraint=True,
                length=5,
            ),
            server_default=sa.text("'BAIXA'"),
            nullable=False,
        ),
        sa.Column(
            "periodicidade",
            sa.Enum(
                "NENHUMA",
                "DIARIA",
                "SEMANAL",
                "MENSAL",
                name="periodicidade",
                native_enum=False,
                create_constraint=True,
                length=10,
            ),
            nullable=False,
        ),
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column(
            "numero_referencia",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column("horario_inicial_padrao", sa.Time(), nullable=False),
        sa.Column("horario_final_padrao", sa.Time(), nullable=False),
        sa.Column("data_final_repeticao", sa.Date(), nullable=True),
        sa.Column("numero_final", sa.Integer(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(nome_padrao) BETWEEN 3 AND 100",
            name=op.f("ck_serie_atividade_nome_padrao_tamanho"),
        ),
        sa.CheckConstraint(
            "data_final_repeticao IS NULL OR "
            "data_final_repeticao >= data_referencia",
            name=op.f("ck_serie_atividade_data_final"),
        ),
        sa.CheckConstraint(
            "horario_final_padrao > horario_inicial_padrao",
            name=op.f("ck_serie_atividade_horarios"),
        ),
        sa.CheckConstraint(
            "numero_final IS NULL OR numero_final >= 0",
            name=op.f("ck_serie_atividade_numero_final"),
        ),
        sa.CheckConstraint(
            "numero_referencia >= 1",
            name=op.f("ck_serie_atividade_numero_referencia"),
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categoria_atividade.id"],
            name=op.f("fk_serie_atividade_categoria_id_categoria_atividade"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_serie_atividade_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_serie_atividade")),
        sa.UniqueConstraint(
            "id", "usuario_id", name=op.f("uq_serie_atividade_id_usuario_id")
        ),
    )
    op.create_table(
        "serie_importancia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_id", sa.Uuid(), nullable=False),
        sa.Column("nome_padrao", sa.String(length=100), nullable=False),
        sa.Column("descricao_padrao", sa.String(length=200), nullable=True),
        sa.Column(
            "periodicidade",
            sa.Enum(
                "NENHUMA",
                "DIARIA",
                "SEMANAL",
                "MENSAL",
                "ANUAL",
                name="periodicidade",
                native_enum=False,
                create_constraint=True,
                length=10,
            ),
            nullable=False,
        ),
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column(
            "numero_referencia",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column("horario_padrao", sa.Time(), nullable=True),
        sa.Column("data_final_repeticao", sa.Date(), nullable=True),
        sa.Column("numero_final", sa.Integer(), nullable=True),
        sa.Column(
            "possui_despesa_padrao",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "valor_previsto_padrao",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
        sa.Column(
            "lembrete_antecedencia_dias", sa.SmallInteger(), nullable=True
        ),
        sa.Column("lembrete_horario", sa.Time(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(lembrete_antecedencia_dias IS NULL) = "
            "(lembrete_horario IS NULL)",
            name=op.f("ck_serie_importancia_lembrete_par"),
        ),
        sa.CheckConstraint(
            "(possui_despesa_padrao = false AND "
            "valor_previsto_padrao IS NULL) OR "
            "(possui_despesa_padrao = true AND "
            "valor_previsto_padrao IS NOT NULL AND "
            "valor_previsto_padrao > 0)",
            name=op.f("ck_serie_importancia_valor_previsto"),
        ),
        sa.CheckConstraint(
            "char_length(nome_padrao) BETWEEN 3 AND 100",
            name=op.f("ck_serie_importancia_nome_padrao_tamanho"),
        ),
        sa.CheckConstraint(
            "data_final_repeticao IS NULL OR "
            "data_final_repeticao >= data_referencia",
            name=op.f("ck_serie_importancia_data_final"),
        ),
        sa.CheckConstraint(
            "lembrete_antecedencia_dias IS NULL OR "
            "lembrete_antecedencia_dias IN (0, 1, 3, 7)",
            name=op.f("ck_serie_importancia_lembrete_antecedencia"),
        ),
        sa.CheckConstraint(
            "numero_final IS NULL OR numero_final >= 0",
            name=op.f("ck_serie_importancia_numero_final"),
        ),
        sa.CheckConstraint(
            "numero_referencia >= 1",
            name=op.f("ck_serie_importancia_numero_referencia"),
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categoria_importancia.id"],
            name=op.f(
                "fk_serie_importancia_categoria_id_categoria_importancia"
            ),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_serie_importancia_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_serie_importancia")),
        sa.UniqueConstraint(
            "id",
            "usuario_id",
            name=op.f("uq_serie_importancia_id_usuario_id"),
        ),
    )
    op.create_table(
        "atividade",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_id", sa.Uuid(), nullable=False),
        sa.Column("serie_id", sa.Uuid(), nullable=True),
        sa.Column("numero_ocorrencia", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.String(length=200), nullable=True),
        sa.Column(
            "prioridade",
            sa.Enum(
                "BAIXA",
                "MEDIA",
                "ALTA",
                name="prioridade",
                native_enum=False,
                create_constraint=True,
                length=5,
            ),
            server_default=sa.text("'BAIXA'"),
            nullable=False,
        ),
        sa.Column("data_atividade", sa.Date(), nullable=False),
        sa.Column("horario_inicial", sa.Time(), nullable=False),
        sa.Column("horario_final", sa.Time(), nullable=False),
        sa.Column("concluida_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("excluida_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(serie_id IS NULL AND numero_ocorrencia IS NULL) OR "
            "(serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL "
            "AND numero_ocorrencia >= 1)",
            name=op.f("ck_atividade_serie_numero"),
        ),
        sa.CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100",
            name=op.f("ck_atividade_nome_tamanho"),
        ),
        sa.CheckConstraint(
            "horario_final > horario_inicial",
            name=op.f("ck_atividade_horarios"),
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categoria_atividade.id"],
            name=op.f("fk_atividade_categoria_id_categoria_atividade"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["serie_id", "usuario_id"],
            ["serie_atividade.id", "serie_atividade.usuario_id"],
            name=op.f("fk_atividade_serie_id_serie_atividade"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_atividade_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_atividade")),
        sa.UniqueConstraint(
            "serie_id",
            "numero_ocorrencia",
            name=op.f("uq_atividade_serie_id_numero_ocorrencia"),
        ),
    )
    op.create_index(
        op.f("ix_atividade_usuario_concluida_data"),
        "atividade",
        ["usuario_id", "concluida_em", "data_atividade"],
        unique=False,
    )
    op.create_index(
        op.f("ix_atividade_usuario_data"),
        "atividade",
        ["usuario_id", "data_atividade"],
        unique=False,
    )
    op.create_table(
        "importancia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_id", sa.Uuid(), nullable=False),
        sa.Column("serie_id", sa.Uuid(), nullable=True),
        sa.Column("numero_ocorrencia", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.String(length=200), nullable=True),
        sa.Column("data_compromisso", sa.Date(), nullable=False),
        sa.Column("horario", sa.Time(), nullable=True),
        sa.Column(
            "possui_despesa",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "valor_previsto", sa.Numeric(precision=12, scale=2), nullable=True
        ),
        sa.Column(
            "concluida_manualmente_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("excluida_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(possui_despesa = false AND valor_previsto IS NULL) OR "
            "(possui_despesa = true AND valor_previsto IS NOT NULL "
            "AND valor_previsto > 0)",
            name=op.f("ck_importancia_valor_previsto"),
        ),
        sa.CheckConstraint(
            "(serie_id IS NULL AND numero_ocorrencia IS NULL) OR "
            "(serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL "
            "AND numero_ocorrencia >= 1)",
            name=op.f("ck_importancia_serie_numero"),
        ),
        sa.CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100",
            name=op.f("ck_importancia_nome_tamanho"),
        ),
        sa.CheckConstraint(
            "possui_despesa = false OR concluida_manualmente_em IS NULL",
            name=op.f("ck_importancia_conclusao_manual"),
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categoria_importancia.id"],
            name=op.f("fk_importancia_categoria_id_categoria_importancia"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["serie_id", "usuario_id"],
            ["serie_importancia.id", "serie_importancia.usuario_id"],
            name=op.f("fk_importancia_serie_id_serie_importancia"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_importancia_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_importancia")),
        sa.UniqueConstraint(
            "id", "usuario_id", name=op.f("uq_importancia_id_usuario_id")
        ),
        sa.UniqueConstraint(
            "serie_id",
            "numero_ocorrencia",
            name=op.f("uq_importancia_serie_id_numero_ocorrencia"),
        ),
    )
    op.create_index(
        op.f("ix_importancia_usuario_data"),
        "importancia",
        ["usuario_id", "data_compromisso"],
        unique=False,
    )
    op.create_table(
        "lembrete_importancia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("importancia_id", sa.Uuid(), nullable=False),
        sa.Column("antecedencia_dias", sa.SmallInteger(), nullable=False),
        sa.Column("horario", sa.Time(), nullable=False),
        sa.Column("agendado_para", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "versao_agendamento",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "situacao",
            sa.Enum(
                "PENDENTE",
                "ENVIADO",
                "CANCELADO",
                name="situacao",
                native_enum=False,
                create_constraint=True,
                length=10,
            ),
            server_default=sa.text("'PENDENTE'"),
            nullable=False,
        ),
        sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(situacao = 'ENVIADO' AND enviado_em IS NOT NULL) OR "
            "(situacao <> 'ENVIADO' AND enviado_em IS NULL)",
            name=op.f("ck_lembrete_importancia_enviado"),
        ),
        sa.CheckConstraint(
            "antecedencia_dias IN (0, 1, 3, 7)",
            name=op.f("ck_lembrete_importancia_antecedencia"),
        ),
        sa.ForeignKeyConstraint(
            ["importancia_id", "usuario_id"],
            ["importancia.id", "importancia.usuario_id"],
            name=op.f("fk_lembrete_importancia_importancia_id_importancia"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_lembrete_importancia_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lembrete_importancia")),
        sa.UniqueConstraint(
            "id",
            "usuario_id",
            name=op.f("uq_lembrete_importancia_id_usuario_id"),
        ),
        sa.UniqueConstraint(
            "importancia_id",
            name=op.f("uq_lembrete_importancia_importancia_id"),
        ),
    )
    op.create_index(
        op.f("ix_lembrete_situacao_agendado"),
        "lembrete_importancia",
        ["situacao", "agendado_para"],
        unique=False,
    )
    op.create_table(
        "movimentacao_financeira",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_id", sa.Uuid(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "RECEITA",
                "DESPESA",
                name="tipo",
                native_enum=False,
                create_constraint=True,
                length=7,
            ),
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.String(length=200), nullable=True),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("data_movimentacao", sa.Date(), nullable=False),
        sa.Column("contraparte", sa.String(length=100), nullable=True),
        sa.Column(
            "forma_movimentacao",
            sa.Enum(
                "PIX",
                "DINHEIRO",
                "CARTAO_DEBITO",
                "TRANSFERENCIA",
                "DEPOSITO",
                "BOLETO",
                "OUTROS",
                name="forma_movimentacao",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=True,
        ),
        sa.Column("importancia_id", sa.Uuid(), nullable=True),
        sa.Column(
            "importancia_vinculada_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("excluida_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "forma_movimentacao IS NULL OR "
            "(tipo = 'RECEITA' AND forma_movimentacao IN "
            "('PIX','DINHEIRO','TRANSFERENCIA','DEPOSITO','OUTROS')) OR "
            "(tipo = 'DESPESA' AND forma_movimentacao IN "
            "('PIX','DINHEIRO','CARTAO_DEBITO','TRANSFERENCIA',"
            "'BOLETO','OUTROS'))",
            name=op.f("ck_movimentacao_financeira_forma_tipo"),
        ),
        sa.CheckConstraint(
            "importancia_id IS NULL OR tipo = 'DESPESA'",
            name=op.f("ck_movimentacao_financeira_vinculo_despesa"),
        ),
        sa.CheckConstraint(
            "(importancia_id IS NULL) = (importancia_vinculada_em IS NULL)",
            name=op.f("ck_movimentacao_financeira_vinculo_par"),
        ),
        sa.CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100",
            name=op.f("ck_movimentacao_financeira_nome_tamanho"),
        ),
        sa.CheckConstraint(
            "excluida_em IS NULL OR importancia_id IS NULL",
            name=op.f("ck_movimentacao_financeira_excluida_sem_vinculo"),
        ),
        sa.CheckConstraint(
            "valor > 0", name=op.f("ck_movimentacao_financeira_valor_positivo")
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id", "tipo"],
            ["categoria_financeira.id", "categoria_financeira.tipo"],
            name=op.f(
                "fk_movimentacao_financeira_categoria_id_categoria_financeira"
            ),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["importancia_id", "usuario_id"],
            ["importancia.id", "importancia.usuario_id"],
            name=op.f("fk_movimentacao_financeira_importancia_id_importancia"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_movimentacao_financeira_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_movimentacao_financeira")),
        sa.UniqueConstraint(
            "importancia_id",
            name=op.f("uq_movimentacao_financeira_importancia_id"),
        ),
    )
    op.create_index(
        op.f("ix_movimentacao_usuario_categoria_data"),
        "movimentacao_financeira",
        ["usuario_id", "categoria_id", "data_movimentacao"],
        unique=False,
    )
    op.create_index(
        op.f("ix_movimentacao_usuario_data"),
        "movimentacao_financeira",
        ["usuario_id", "data_movimentacao"],
        unique=False,
    )
    op.create_index(
        op.f("ix_movimentacao_usuario_tipo_data"),
        "movimentacao_financeira",
        ["usuario_id", "tipo", "data_movimentacao"],
        unique=False,
    )
    op.create_table(
        "notificacao",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("lembrete_id", sa.Uuid(), nullable=False),
        sa.Column("versao_agendamento", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=120), nullable=False),
        sa.Column("mensagem", sa.String(length=500), nullable=False),
        sa.Column(
            "criada_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("lida_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["lembrete_id", "usuario_id"],
            ["lembrete_importancia.id", "lembrete_importancia.usuario_id"],
            name=op.f("fk_notificacao_lembrete_id_lembrete_importancia"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name=op.f("fk_notificacao_usuario_id_usuario"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notificacao")),
        sa.UniqueConstraint(
            "lembrete_id",
            "versao_agendamento",
            name=op.f("uq_notificacao_lembrete_id_versao_agendamento"),
        ),
    )
    op.create_index(
        op.f("ix_notificacao_usuario_lida_criada"),
        "notificacao",
        ["usuario_id", "lida_em", "criada_em"],
        unique=False,
    )
    for instrucao in instrucoes_categorias():
        op.execute(instrucao)


def downgrade() -> None:
    """Reverte a migração."""
    op.drop_index(
        op.f("ix_notificacao_usuario_lida_criada"), table_name="notificacao"
    )
    op.drop_table("notificacao")
    op.drop_index(
        op.f("ix_movimentacao_usuario_tipo_data"),
        table_name="movimentacao_financeira",
    )
    op.drop_index(
        op.f("ix_movimentacao_usuario_data"),
        table_name="movimentacao_financeira",
    )
    op.drop_index(
        op.f("ix_movimentacao_usuario_categoria_data"),
        table_name="movimentacao_financeira",
    )
    op.drop_table("movimentacao_financeira")
    op.drop_index(
        op.f("ix_lembrete_situacao_agendado"),
        table_name="lembrete_importancia",
    )
    op.drop_table("lembrete_importancia")
    op.drop_index(
        op.f("ix_importancia_usuario_data"), table_name="importancia"
    )
    op.drop_table("importancia")
    op.drop_index(op.f("ix_atividade_usuario_data"), table_name="atividade")
    op.drop_index(
        op.f("ix_atividade_usuario_concluida_data"), table_name="atividade"
    )
    op.drop_table("atividade")
    op.drop_table("serie_importancia")
    op.drop_table("serie_atividade")
    op.drop_table("requisicao_idempotente")
    op.drop_table("recuperacao_senha")
    op.drop_table("usuario")
    op.drop_table("categoria_importancia")
    op.drop_table("categoria_financeira")
    op.drop_table("categoria_atividade")
