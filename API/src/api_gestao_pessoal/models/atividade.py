"""Tabela `atividade`: ocorrência concreta de uma atividade (tabela 5)."""

import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin
from api_gestao_pessoal.models.enums import Prioridade, tipo_enum


class Atividade(CriadoAtualizadoMixin, Base):
    """Ocorrência de atividade; avulsa quando `serie_id` é nulo."""

    __tablename__ = "atividade"
    __table_args__ = (
        UniqueConstraint("serie_id", "numero_ocorrencia"),
        CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100", name="nome_tamanho"
        ),
        CheckConstraint("horario_final > horario_inicial", name="horarios"),
        CheckConstraint(
            "(serie_id IS NULL AND numero_ocorrencia IS NULL) OR "
            "(serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL "
            "AND numero_ocorrencia >= 1)",
            name="serie_numero",
        ),
        ForeignKeyConstraint(
            ["serie_id", "usuario_id"],
            ["serie_atividade.id", "serie_atividade.usuario_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_atividade_usuario_data", "usuario_id", "data_atividade"),
        Index(
            "ix_atividade_usuario_concluida_data",
            "usuario_id",
            "concluida_em",
            "data_atividade",
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
        Uuid(as_uuid=True),
        ForeignKey("categoria_atividade.id", ondelete="RESTRICT"),
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
    prioridade: Mapped[Prioridade] = mapped_column(
        tipo_enum(Prioridade, "prioridade", 5),
        server_default=text("'BAIXA'"),
        nullable=False,
    )
    data_atividade: Mapped[date] = mapped_column(Date(), nullable=False)
    horario_inicial: Mapped[time] = mapped_column(
        Time(timezone=False), nullable=False
    )
    horario_final: Mapped[time] = mapped_column(
        Time(timezone=False), nullable=False
    )
    concluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    excluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
