"""Tabela `serie_atividade`: regra de repetição de atividades (tabela 4)."""

import uuid
from datetime import date, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin
from api_gestao_pessoal.models.enums import (
    PeriodicidadeAtividade,
    Prioridade,
    tipo_enum,
)


class SerieAtividade(CriadoAtualizadoMixin, Base):
    """Regra vigente e valores padrão das ocorrências de uma série."""

    __tablename__ = "serie_atividade"
    __table_args__ = (
        UniqueConstraint("id", "usuario_id"),
        CheckConstraint(
            "char_length(nome_padrao) BETWEEN 3 AND 100",
            name="nome_padrao_tamanho",
        ),
        CheckConstraint(
            "horario_final_padrao > horario_inicial_padrao", name="horarios"
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
    nome_padrao: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao_padrao: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    prioridade_padrao: Mapped[Prioridade] = mapped_column(
        tipo_enum(Prioridade, "prioridade_padrao", 5),
        server_default=text("'BAIXA'"),
        nullable=False,
    )
    periodicidade: Mapped[PeriodicidadeAtividade] = mapped_column(
        tipo_enum(PeriodicidadeAtividade, "periodicidade", 10),
        nullable=False,
    )
    data_referencia: Mapped[date] = mapped_column(Date(), nullable=False)
    numero_referencia: Mapped[int] = mapped_column(
        Integer(), server_default=text("1"), nullable=False
    )
    horario_inicial_padrao: Mapped[time] = mapped_column(
        Time(timezone=False), nullable=False
    )
    horario_final_padrao: Mapped[time] = mapped_column(
        Time(timezone=False), nullable=False
    )
    data_final_repeticao: Mapped[date | None] = mapped_column(
        Date(), nullable=True
    )
    numero_final: Mapped[int | None] = mapped_column(Integer(), nullable=True)
