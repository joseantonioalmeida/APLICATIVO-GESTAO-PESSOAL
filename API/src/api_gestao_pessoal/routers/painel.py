"""Endpoints do painel inicial (F10): um por bloco (4.2.8)."""

from fastapi import APIRouter

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ContextoDep
from api_gestao_pessoal.schemas.painel import (
    PainelAtividadesHoje,
    PainelFinanceiro,
    PainelImportancias,
)
from api_gestao_pessoal.services import painel

router = APIRouter(prefix="/painel", tags=["painel"])


@router.get("/atividades-hoje")
async def atividades_hoje(
    sessao: SessaoDep, contexto: ContextoDep
) -> PainelAtividadesHoje:
    resposta = await painel.atividades_de_hoje(sessao, contexto)
    await sessao.commit()  # a consulta materializa ocorrências
    return resposta


@router.get("/financeiro")
async def financeiro(
    sessao: SessaoDep, contexto: ContextoDep
) -> PainelFinanceiro:
    return await painel.financeiro(sessao, contexto)


@router.get("/importancias")
async def importancias(
    sessao: SessaoDep, contexto: ContextoDep
) -> PainelImportancias:
    resposta = await painel.importancias_do_painel(sessao, contexto)
    await sessao.commit()  # a consulta materializa ocorrências
    return resposta
