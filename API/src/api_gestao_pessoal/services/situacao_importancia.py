"""Expressões SQL de situação, pagamento e prazo (arquitetura §8.1).

A situação é derivada: nada é guardado em coluna. A movimentação vinculada
é unida por `m.importancia_id = importancia.id` (no máximo uma; uma
movimentação excluída nunca mantém vínculo).
"""

from typing import Any

from sqlalchemy import and_, case
from sqlalchemy.orm import aliased

from api_gestao_pessoal.models import Importancia, MovimentacaoFinanceira

Movimentacao = aliased(MovimentacaoFinanceira, name="pagamento")


def concluida(m: Any = Movimentacao) -> Any:  # noqa: ANN401
    """Concluída: paga (com despesa) ou concluída manualmente."""
    return case(
        (Importancia.possui_despesa, m.id.is_not(None)),
        else_=Importancia.concluida_manualmente_em.is_not(None),
    )


def paga(m: Any = Movimentacao) -> Any:  # noqa: ANN401
    """Paga: possui despesa e há movimentação vinculada."""
    return and_(Importancia.possui_despesa, m.id.is_not(None))


def momento_conclusao(m: Any = Movimentacao) -> Any:  # noqa: ANN401
    """Quando foi concluída (vínculo ou conclusão manual)."""
    return case(
        (Importancia.possui_despesa, m.importancia_vinculada_em),
        else_=Importancia.concluida_manualmente_em,
    )
