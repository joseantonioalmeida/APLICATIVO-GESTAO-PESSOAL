"""Tabela `requisicao_idempotente`: proteção contra reenvio (tabela 13)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base
from api_gestao_pessoal.models.enums import SituacaoRequisicao, tipo_enum


class RequisicaoIdempotente(Base):
    """Operação identificada por `(usuario_id, acao, chave)`."""

    __tablename__ = "requisicao_idempotente"
    __table_args__ = (UniqueConstraint("usuario_id", "acao", "chave"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    chave: Mapped[str] = mapped_column(String(64), nullable=False)
    acao: Mapped[str] = mapped_column(String(50), nullable=False)
    conteudo_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    situacao: Mapped[SituacaoRequisicao] = mapped_column(
        tipo_enum(SituacaoRequisicao, "situacao", 20),
        server_default=text("'EM_PROCESSAMENTO'"),
        nullable=False,
    )
    codigo_resposta: Mapped[int | None] = mapped_column(
        SmallInteger(), nullable=True
    )
    resposta: Mapped[dict[str, Any] | None] = mapped_column(
        JSON(none_as_null=True), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    concluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
