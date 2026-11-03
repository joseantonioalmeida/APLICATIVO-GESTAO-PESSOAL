"""Tabela `usuario`: conta do aplicativo (tabela 1)."""

import uuid
from datetime import date

from sqlalchemy import Date, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin


class Usuario(CriadoAtualizadoMixin, Base):
    """Conta de usuário; o e-mail chega normalizado pela aplicação."""

    __tablename__ = "usuario"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    nome_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(254), unique=True, nullable=False
    )
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date(), nullable=False)
    fuso_horario: Mapped[str] = mapped_column(String(64), nullable=False)
