"""Tabela `serie_importancia`: regra de repetição (tabela 7)."""

import uuid
from datetime import date, time
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin
from api_gestao_pessoal.models.enums import PeriodicidadeImportancia, tipo_enum


class SerieImportancia(CriadoAtualizadoMixin, Base):
    """Regra vigente e valores padrão das ocorrências de uma série."""

    __tablename__ = "serie_importancia"
    __table_args__ = (
        UniqueConstraint("id", "usuario_id"),
        CheckConstraint(
            "char_length(nome_padrao) BETWEEN 3 AND 100",
            name="nome_padrao_tamanho",
        ),
        CheckConstraint("numero_referencia >= 1", name="numero_referencia"),
        CheckConstraint(
            "numero_final IS NULL OR numero_final >= 0", name="numero_final"
        ),
        CheckConstraint(
            "data_final_repeticao IS NULL OR "
            "data_final_repeticao >= data_referencia",
            name="data_final",
        ),
        CheckConstraint(
            "(possui_despesa_padrao = false AND "
            "valor_previsto_padrao IS NULL) OR "
            "(possui_despesa_padrao = true AND "
            "valor_previsto_padrao IS NOT NULL AND "
            "valor_previsto_padrao > 0)",
            name="valor_previsto",
        ),
        CheckConstraint(
            "(lembrete_antecedencia_dias IS NULL) = "
            "(lembrete_horario IS NULL)",
            name="lembrete_par",
        ),
        CheckConstraint(
            "lembrete_antecedencia_dias IS NULL OR "
            "lembrete_antecedencia_dias IN (0, 1, 3, 7)",
            name="lembrete_antecedencia",
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
        ForeignKey("categoria_importancia.id", ondelete="RESTRICT"),
        nullable=False,
    )
    nome_padrao: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao_padrao: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    periodicidade: Mapped[PeriodicidadeImportancia] = mapped_column(
        tipo_enum(PeriodicidadeImportancia, "periodicidade", 10),
        nullable=False,
    )
    data_referencia: Mapped[date] = mapped_column(Date(), nullable=False)
    numero_referencia: Mapped[int] = mapped_column(
        Integer(), server_default=text("1"), nullable=False
    )
    horario_padrao: Mapped[time | None] = mapped_column(
        Time(timezone=False), nullable=True
    )
    data_final_repeticao: Mapped[date | None] = mapped_column(
        Date(), nullable=True
    )
    numero_final: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    possui_despesa_padrao: Mapped[bool] = mapped_column(
        Boolean(), server_default=text("false"), nullable=False
    )
    valor_previsto_padrao: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2, asdecimal=True), nullable=True
    )
    lembrete_antecedencia_dias: Mapped[int | None] = mapped_column(
        SmallInteger(), nullable=True
    )
    lembrete_horario: Mapped[time | None] = mapped_column(
        Time(timezone=False), nullable=True
    )
