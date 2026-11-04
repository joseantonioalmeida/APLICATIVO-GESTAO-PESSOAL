"""Catálogos de categorias ativas (arquitetura §9.2)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.models import (
    CategoriaAtividade,
    CategoriaFinanceira,
    CategoriaImportancia,
)
from api_gestao_pessoal.models.enums import TipoMovimentacao
from api_gestao_pessoal.schemas.categoria import (
    CategoriaFinanceiraResposta,
    CategoriaResposta,
)

NOME_OUTROS = "Outros"


async def listar_de_atividades(
    sessao: AsyncSession,
) -> list[CategoriaResposta]:
    consulta = (
        select(CategoriaAtividade)
        .where(CategoriaAtividade.ativa.is_(True))
        .order_by(
            CategoriaAtividade.nome == NOME_OUTROS, CategoriaAtividade.nome
        )
    )
    linhas = (await sessao.scalars(consulta)).all()
    return [CategoriaResposta(id=c.id, nome=c.nome) for c in linhas]


async def listar_de_importancias(
    sessao: AsyncSession,
) -> list[CategoriaResposta]:
    consulta = (
        select(CategoriaImportancia)
        .where(CategoriaImportancia.ativa.is_(True))
        .order_by(
            CategoriaImportancia.nome == NOME_OUTROS, CategoriaImportancia.nome
        )
    )
    linhas = (await sessao.scalars(consulta)).all()
    return [CategoriaResposta(id=c.id, nome=c.nome) for c in linhas]


async def listar_financeiras(
    sessao: AsyncSession, tipo: TipoMovimentacao
) -> list[CategoriaFinanceiraResposta]:
    consulta = (
        select(CategoriaFinanceira)
        .where(
            CategoriaFinanceira.ativa.is_(True),
            CategoriaFinanceira.tipo == tipo,
        )
        .order_by(
            CategoriaFinanceira.nome == NOME_OUTROS, CategoriaFinanceira.nome
        )
    )
    linhas = (await sessao.scalars(consulta)).all()
    return [
        CategoriaFinanceiraResposta(id=c.id, nome=c.nome, tipo=c.tipo)
        for c in linhas
    ]
