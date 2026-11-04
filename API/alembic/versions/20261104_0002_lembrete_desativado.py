"""Lembrete: acrescenta a situação DESATIVADO (F7, DEC-MV-19).

Distingue o lembrete desligado pelo usuário (DESATIVADO) do cancelado por
conclusão ou exclusão (CANCELADO), para que a reabertura não reative um
lembrete que o usuário desligou. Migração aditiva e reversível.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-04 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABELA = "lembrete_importancia"
RESTRICAO = "ck_lembrete_importancia_situacao"


def upgrade() -> None:
    op.drop_constraint(op.f(RESTRICAO), TABELA, type_="check")
    op.create_check_constraint(
        op.f(RESTRICAO),
        TABELA,
        "situacao IN ('PENDENTE', 'ENVIADO', 'CANCELADO', 'DESATIVADO')",
    )


def downgrade() -> None:
    # Sem o valor novo, o lembrete desativado passa a cancelado.
    op.execute(
        "UPDATE lembrete_importancia SET situacao = 'CANCELADO' "
        "WHERE situacao = 'DESATIVADO'"
    )
    op.drop_constraint(op.f(RESTRICAO), TABELA, type_="check")
    op.create_check_constraint(
        op.f(RESTRICAO),
        TABELA,
        "situacao IN ('PENDENTE', 'ENVIADO', 'CANCELADO')",
    )
