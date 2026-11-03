"""Tabela `lembrete_importancia`: lembrete de uma importância (tabela 11)."""

import uuid
from datetime import datetime, time

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    SmallInteger,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin
from api_gestao_pessoal.models.enums import SituacaoLembrete, tipo_enum


class LembreteImportancia(CriadoAtualizadoMixin, Base):
    """Configuração e situação da versão corrente do lembrete."""

    __tablename__ = "lembrete_importancia"
    __table_args__ = (
        UniqueConstraint("importancia_id"),
        UniqueConstraint("id", "usuario_id"),
        CheckConstraint(
            "antecedencia_dias IN (0, 1, 3, 7)", name="antecedencia"
        ),
        CheckConstraint(
            "(situacao = 'ENVIADO' AND enviado_em IS NOT NULL) OR "
            "(situacao <> 'ENVIADO' AND enviado_em IS NULL)",
            name="enviado",
        ),
        ForeignKeyConstraint(
            ["importancia_id", "usuario_id"],
            ["importancia.id", "importancia.usuario_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_lembrete_situacao_agendado", "situacao", "agendado_para"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    importancia_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    antecedencia_dias: Mapped[int] = mapped_column(
        SmallInteger(), nullable=False
    )
    horario: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    agendado_para: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    versao_agendamento: Mapped[int] = mapped_column(
        Integer(), server_default=text("1"), nullable=False
    )
    situacao: Mapped[SituacaoLembrete] = mapped_column(
        tipo_enum(SituacaoLembrete, "situacao", 10),
        server_default=text("'PENDENTE'"),
        nullable=False,
    )
    enviado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
