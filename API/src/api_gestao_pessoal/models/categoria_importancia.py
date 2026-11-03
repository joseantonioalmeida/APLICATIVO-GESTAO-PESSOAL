"""Tabela `categoria_importancia`: catálogo de categorias (tabela 6)."""

import uuid

from sqlalchemy import Boolean, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base


class CategoriaImportancia(Base):
    """Categoria de importância, compartilhada entre os usuários."""

    __tablename__ = "categoria_importancia"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ativa: Mapped[bool] = mapped_column(
        Boolean(), server_default=text("true"), nullable=False
    )
