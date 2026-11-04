"""Consulta e conversão de movimentações (suporte de F6, F8 e F10)."""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.models import (
    CategoriaFinanceira,
    Importancia,
    MovimentacaoFinanceira,
)
from api_gestao_pessoal.schemas.atividade import CategoriaRef
from api_gestao_pessoal.schemas.financeiro import (
    ImportanciaVinculadaDetalhe,
    ImportanciaVinculadaItem,
    MovimentacaoDetalhe,
    MovimentacaoItem,
)

Mov = MovimentacaoFinanceira


def consulta_base() -> Any:  # noqa: ANN401
    """Movimentações com categoria e importância vinculada (se houver)."""
    return (
        select(
            Mov,
            CategoriaFinanceira.nome,
            Importancia.id,
            Importancia.nome,
            Importancia.excluida_em,
        )
        .join(CategoriaFinanceira, CategoriaFinanceira.id == Mov.categoria_id)
        .outerjoin(Importancia, Importancia.id == Mov.importancia_id)
    )


def montar_item(linha: Sequence[Any]) -> MovimentacaoItem:
    """Converte uma linha de `consulta_base` em item de lista."""
    mov, categoria_nome, imp_id, imp_nome, imp_excluida = linha
    importancia = (
        ImportanciaVinculadaItem(
            id=imp_id, nome=imp_nome, disponivel=imp_excluida is None
        )
        if imp_id is not None
        else None
    )
    return MovimentacaoItem(
        id=mov.id,
        tipo=mov.tipo,
        nome=mov.nome,
        valor=mov.valor,
        categoria=CategoriaRef(id=mov.categoria_id, nome=categoria_nome),
        data_movimentacao=mov.data_movimentacao,
        importancia=importancia,
    )


async def obter_detalhe(
    sessao: AsyncSession, usuario_id: uuid.UUID, movimentacao_id: uuid.UUID
) -> MovimentacaoDetalhe | None:
    """Detalhe de uma movimentação não excluída do usuário."""
    linha = (
        await sessao.execute(
            consulta_base().where(
                Mov.id == movimentacao_id,
                Mov.usuario_id == usuario_id,
                Mov.excluida_em.is_(None),
            )
        )
    ).first()
    if linha is None:
        return None
    mov = linha[0]
    importancia: ImportanciaVinculadaDetalhe | None = None
    if mov.importancia_id is not None:
        imp = await sessao.get(Importancia, mov.importancia_id)
        if imp is not None:
            importancia = ImportanciaVinculadaDetalhe(
                id=imp.id,
                nome=imp.nome,
                disponivel=imp.excluida_em is None,
                data_compromisso=imp.data_compromisso,
                valor_previsto=imp.valor_previsto,
            )
    item = montar_item(linha)
    return MovimentacaoDetalhe(
        id=item.id,
        tipo=item.tipo,
        nome=item.nome,
        valor=item.valor,
        categoria=item.categoria,
        data_movimentacao=item.data_movimentacao,
        importancia=importancia,
        descricao=mov.descricao,
        contraparte=mov.contraparte,
        forma=mov.forma_movimentacao,
        criado_em=mov.criado_em,
        atualizado_em=mov.atualizado_em,
    )
