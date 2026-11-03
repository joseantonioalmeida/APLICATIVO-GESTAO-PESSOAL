"""Tabela `movimentacao_financeira`: receitas e despesas (tabela 10)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin
from api_gestao_pessoal.models.enums import (
    FormaMovimentacao,
    TipoMovimentacao,
    tipo_enum,
)


class MovimentacaoFinanceira(CriadoAtualizadoMixin, Base):
    """Recebimento ou pagamento efetivado; o tipo define o sinal."""

    __tablename__ = "movimentacao_financeira"
    __table_args__ = (
        CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100", name="nome_tamanho"
        ),
        CheckConstraint("valor > 0", name="valor_positivo"),
        CheckConstraint(
            "(importancia_id IS NULL) = (importancia_vinculada_em IS NULL)",
            name="vinculo_par",
        ),
        CheckConstraint(
            "importancia_id IS NULL OR tipo = 'DESPESA'",
            name="vinculo_despesa",
        ),
        CheckConstraint(
            "excluida_em IS NULL OR importancia_id IS NULL",
            name="excluida_sem_vinculo",
        ),
        CheckConstraint(
            "forma_movimentacao IS NULL OR "
            "(tipo = 'RECEITA' AND forma_movimentacao IN "
            "('PIX','DINHEIRO','TRANSFERENCIA','DEPOSITO','OUTROS')) OR "
            "(tipo = 'DESPESA' AND forma_movimentacao IN "
            "('PIX','DINHEIRO','CARTAO_DEBITO','TRANSFERENCIA',"
            "'BOLETO','OUTROS'))",
            name="forma_tipo",
        ),
        ForeignKeyConstraint(
            ["categoria_id", "tipo"],
            ["categoria_financeira.id", "categoria_financeira.tipo"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["importancia_id", "usuario_id"],
            ["importancia.id", "importancia.usuario_id"],
            ondelete="RESTRICT",
        ),
        Index(
            "ix_movimentacao_usuario_data", "usuario_id", "data_movimentacao"
        ),
        Index(
            "ix_movimentacao_usuario_tipo_data",
            "usuario_id",
            "tipo",
            "data_movimentacao",
        ),
        Index(
            "ix_movimentacao_usuario_categoria_data",
            "usuario_id",
            "categoria_id",
            "data_movimentacao",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        tipo_enum(TipoMovimentacao, "tipo", 7), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valor: Mapped[Decimal] = mapped_column(
        Numeric(12, 2, asdecimal=True), nullable=False
    )
    data_movimentacao: Mapped[date] = mapped_column(Date(), nullable=False)
    contraparte: Mapped[str | None] = mapped_column(String(100), nullable=True)
    forma_movimentacao: Mapped[FormaMovimentacao | None] = mapped_column(
        tipo_enum(FormaMovimentacao, "forma_movimentacao", 20),
        nullable=True,
    )
    importancia_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), unique=True, nullable=True
    )
    importancia_vinculada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    excluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
