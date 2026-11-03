"""Tabela `categoria_financeira`: catálogo por tipo (tabela 9)."""

import uuid

from sqlalchemy import Boolean, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base
from api_gestao_pessoal.models.enums import TipoMovimentacao, tipo_enum


class CategoriaFinanceira(Base):
    """Categoria de receita ou despesa; `Outros` existe nos dois tipos."""

    __tablename__ = "categoria_financeira"
    __table_args__ = (
        UniqueConstraint("tipo", "nome"),
        UniqueConstraint("id", "tipo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        tipo_enum(TipoMovimentacao, "tipo", 7), nullable=False
    )
    ativa: Mapped[bool] = mapped_column(
        Boolean(), server_default=text("true"), nullable=False
    )
