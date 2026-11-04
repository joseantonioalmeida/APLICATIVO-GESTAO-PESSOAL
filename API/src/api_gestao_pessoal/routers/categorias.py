"""Catálogos de categorias (F4)."""

from typing import Annotated

from fastapi import APIRouter, Query

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ContextoDep
from api_gestao_pessoal.models.enums import TipoMovimentacao
from api_gestao_pessoal.schemas.categoria import (
    CategoriaFinanceiraResposta,
    CategoriaResposta,
)
from api_gestao_pessoal.services import categorias

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("/atividades")
async def categorias_de_atividades(
    sessao: SessaoDep, _contexto: ContextoDep
) -> list[CategoriaResposta]:
    return await categorias.listar_de_atividades(sessao)


@router.get("/importancias")
async def categorias_de_importancias(
    sessao: SessaoDep, _contexto: ContextoDep
) -> list[CategoriaResposta]:
    return await categorias.listar_de_importancias(sessao)


@router.get("/financeiras")
async def categorias_financeiras(
    sessao: SessaoDep,
    _contexto: ContextoDep,
    tipo: Annotated[TipoMovimentacao, Query()],
) -> list[CategoriaFinanceiraResposta]:
    return await categorias.listar_financeiras(sessao, tipo)
