"""Tabela `categoria_atividade`: catálogo de categorias (tabela 3)."""

import uuid

from sqlalchemy import Boolean, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base


class CategoriaAtividade(Base):
    """Categoria de atividade, compartilhada entre os usuários."""

    __tablename__ = "categoria_atividade"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ativa: Mapped[bool] = mapped_column(
        Boolean(), server_default=text("true"), nullable=False
    )
