"""Tabela `recuperacao_senha`: recuperação corrente do usuário (tabela 2)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin


class RecuperacaoSenha(CriadoAtualizadoMixin, Base):
    """Código protegido e token de redefinição; uma linha por usuário."""

    __tablename__ = "recuperacao_senha"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    codigo_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expira_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    tentativas: Mapped[int] = mapped_column(
        Integer(), server_default=text("0"), nullable=False
    )
    verificado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    token_redefinicao_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True
    )
    utilizado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
