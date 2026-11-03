"""Base declarativa, convenção de nomes e mixin de timestamps."""

from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

CONVENCAO_NOMES = {
    "pk": "pk_%(table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
}


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os modelos ORM."""

    metadata = MetaData(naming_convention=CONVENCAO_NOMES)
    # Valores gerados no servidor voltam por RETURNING no INSERT e no
    # UPDATE, sem I/O tardio na AsyncSession (DEC-MV-07).
    __mapper_args__ = {"eager_defaults": True}


class CriadoAtualizadoMixin:
    """`criado_em` e `atualizado_em` das 8 tabelas que têm as duas colunas.

    `criado_em`: padrão do banco (`DEFAULT now()`). `atualizado_em`: o
    mesmo padrão na inserção e `onupdate`, aplicado pelo SQLAlchemy nos
    UPDATEs que ele emite. Não há trigger no banco.
    """

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
