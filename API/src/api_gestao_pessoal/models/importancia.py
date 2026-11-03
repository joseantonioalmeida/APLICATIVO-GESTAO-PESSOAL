"""Tabela `importancia`: ocorrência concreta de um compromisso (tabela 8)."""

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin


class Importancia(CriadoAtualizadoMixin, Base):
    """Ocorrência de importância; avulsa quando `serie_id` é nulo."""

    __tablename__ = "importancia"
    __table_args__ = (
        UniqueConstraint("id", "usuario_id"),
        UniqueConstraint("serie_id", "numero_ocorrencia"),
        CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100", name="nome_tamanho"
        ),
        CheckConstraint(
            "(serie_id IS NULL AND numero_ocorrencia IS NULL) OR "
            "(serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL "
            "AND numero_ocorrencia >= 1)",
            name="serie_numero",
        ),
        CheckConstraint(
            "(possui_despesa = false AND valor_previsto IS NULL) OR "
            "(possui_despesa = true AND valor_previsto IS NOT NULL "
            "AND valor_previsto > 0)",
            name="valor_previsto",
        ),
        CheckConstraint(
            "possui_despesa = false OR concluida_manualmente_em IS NULL",
            name="conclusao_manual",
        ),
        ForeignKeyConstraint(
            ["serie_id", "usuario_id"],
            ["serie_importancia.id", "serie_importancia.usuario_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_importancia_usuario_data", "usuario_id", "data_compromisso"),
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
        Uuid(as_uuid=True),
        ForeignKey("categoria_importancia.id", ondelete="RESTRICT"),
        nullable=False,
    )
    serie_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    numero_ocorrencia: Mapped[int | None] = mapped_column(
        Integer(), nullable=True
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)
    data_compromisso: Mapped[date] = mapped_column(Date(), nullable=False)
    horario: Mapped[time | None] = mapped_column(
        Time(timezone=False), nullable=True
    )
    possui_despesa: Mapped[bool] = mapped_column(
        Boolean(), server_default=text("false"), nullable=False
    )
    valor_previsto: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2, asdecimal=True), nullable=True
    )
    concluida_manualmente_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    excluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
