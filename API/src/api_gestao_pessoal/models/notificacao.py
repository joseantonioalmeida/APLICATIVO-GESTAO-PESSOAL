"""Tabela `notificacao`: notificação interna de um lembrete (tabela 12)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base


class Notificacao(Base):
    """Conteúdo de um envio, preservado por versão do agendamento."""

    __tablename__ = "notificacao"
    __table_args__ = (
        UniqueConstraint("lembrete_id", "versao_agendamento"),
        ForeignKeyConstraint(
            ["lembrete_id", "usuario_id"],
            ["lembrete_importancia.id", "lembrete_importancia.usuario_id"],
            ondelete="RESTRICT",
        ),
        Index(
            "ix_notificacao_usuario_lida_criada",
            "usuario_id",
            "lida_em",
            "criada_em",
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
    lembrete_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    versao_agendamento: Mapped[int] = mapped_column(Integer(), nullable=False)
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    mensagem: Mapped[str] = mapped_column(String(500), nullable=False)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    lida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
