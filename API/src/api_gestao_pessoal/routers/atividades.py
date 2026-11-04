"""Endpoints de atividades (F5)."""

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ChaveIdempotenciaDep, ContextoDep
from api_gestao_pessoal.schemas.atividade import (
    AtividadeCriacao,
    AtividadeDetalhe,
    AtividadeEdicao,
    ConsultaAtividadesResposta,
    FiltroPrioridade,
    FiltroSituacao,
    OrdenacaoAtividades,
    PendenciasAnterioresResposta,
    SituacaoEntrada,
)
from api_gestao_pessoal.schemas.comum import AlcanceSerie
from api_gestao_pessoal.services import atividades
from api_gestao_pessoal.services.idempotencia import (
    AcaoIdempotente,
    executar_idempotente,
)
from api_gestao_pessoal.services.paginacao import (
    LIMITE_MAXIMO,
    LIMITE_PADRAO,
)

router = APIRouter(prefix="/atividades", tags=["atividades"])

# Rotas estáticas antes das rotas com `{id}` (arquitetura §9).


@router.get("")
async def consultar_atividades(  # noqa: PLR0913
    *,
    sessao: SessaoDep,
    contexto: ContextoDep,
    data: Annotated[date | None, Query()] = None,
    categoria_id: Annotated[uuid.UUID | None, Query()] = None,
    situacao: Annotated[FiltroSituacao, Query()] = FiltroSituacao.TODAS,
    prioridade: Annotated[FiltroPrioridade, Query()] = FiltroPrioridade.TODAS,
    busca: Annotated[str, Query(max_length=100)] = "",
    ordenacao: Annotated[
        OrdenacaoAtividades, Query()
    ] = OrdenacaoAtividades.HORARIO,
    limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PADRAO,
    cursor: Annotated[str | None, Query()] = None,
) -> ConsultaAtividadesResposta:
    filtros = atividades.FiltrosConsulta(
        data=data or contexto.hoje,
        categoria_id=categoria_id,
        situacao=situacao,
        prioridade=prioridade,
        busca=busca,
        ordenacao=ordenacao,
        limite=limite,
        cursor=cursor,
    )
    resposta = await atividades.consultar(sessao, contexto, filtros)
    await sessao.commit()  # a consulta materializa ocorrências
    return resposta


@router.get("/pendencias-anteriores")
async def pendencias_anteriores(
    sessao: SessaoDep, contexto: ContextoDep
) -> PendenciasAnterioresResposta:
    resposta = await atividades.pendencias_anteriores(sessao, contexto)
    await sessao.commit()
    return resposta


@router.get("/{atividade_id}")
async def obter_atividade(
    atividade_id: uuid.UUID, sessao: SessaoDep, contexto: ContextoDep
) -> AtividadeDetalhe:
    return await atividades.obter(sessao, contexto, atividade_id)


@router.post("", status_code=201, response_model=AtividadeDetalhe)
async def cadastrar_atividade(
    dados: AtividadeCriacao,
    sessao: SessaoDep,
    contexto: ContextoDep,
    chave: ChaveIdempotenciaDep,
) -> JSONResponse:
    resposta = await executar_idempotente(
        sessao,
        contexto,
        acao=AcaoIdempotente.CADASTRAR_ATIVIDADE,
        chave=chave,
        conteudo=dados,
        status_sucesso=201,
        operacao=lambda: atividades.criar(sessao, contexto, dados),
    )
    await sessao.commit()
    return JSONResponse(
        status_code=resposta.status,
        content=resposta.corpo,
        headers=(
            {"Idempotency-Replayed": "true"} if resposta.reexecucao else None
        ),
    )


@router.patch("/{atividade_id}")
async def editar_atividade(
    atividade_id: uuid.UUID,
    dados: AtividadeEdicao,
    sessao: SessaoDep,
    contexto: ContextoDep,
) -> AtividadeDetalhe:
    resposta = await atividades.editar(sessao, contexto, atividade_id, dados)
    await sessao.commit()
    return resposta


@router.put("/{atividade_id}/situacao")
async def definir_situacao(
    atividade_id: uuid.UUID,
    dados: SituacaoEntrada,
    sessao: SessaoDep,
    contexto: ContextoDep,
) -> AtividadeDetalhe:
    resposta = await atividades.definir_situacao(
        sessao, contexto, atividade_id, dados.situacao
    )
    await sessao.commit()
    return resposta


@router.delete("/{atividade_id}", status_code=204)
async def excluir_atividade(
    atividade_id: uuid.UUID,
    sessao: SessaoDep,
    contexto: ContextoDep,
    alcance: Annotated[AlcanceSerie, Query()] = AlcanceSerie.SOMENTE_ESTA,
) -> Response:
    await atividades.excluir(sessao, contexto, atividade_id, alcance)
    await sessao.commit()
    return Response(status_code=204)
