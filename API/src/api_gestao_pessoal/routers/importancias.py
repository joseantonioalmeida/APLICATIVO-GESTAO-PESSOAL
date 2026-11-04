"""Endpoints de importâncias (F7; pagamentos na F8)."""

import re
import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ChaveIdempotenciaDep, ContextoDep
from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.schemas.comum import AlcanceSerie
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.schemas.importancia import (
    ConsultaImportanciasResposta,
    FiltroImportancia,
    ImportanciaCriacao,
    ImportanciaDetalhe,
    ImportanciaEdicao,
    SituacaoImportanciaEntrada,
)
from api_gestao_pessoal.services import importancias
from api_gestao_pessoal.services.idempotencia import (
    AcaoIdempotente,
    executar_idempotente,
)
from api_gestao_pessoal.services.paginacao import (
    LIMITE_MAXIMO,
    LIMITE_PADRAO,
)

router = APIRouter(prefix="/importancias", tags=["importâncias"])

PADRAO_MES = r"^[0-9]{4}-(0[1-9]|1[0-2])$"
ANO_MINIMO, ANO_MAXIMO = 2000, 2100


def _interpretar_mes(texto: str | None) -> date | None:
    if texto is None:
        return None
    if not re.fullmatch(PADRAO_MES, texto) or not (
        ANO_MINIMO <= int(texto[:4]) <= ANO_MAXIMO
    ):
        raise ErroNegocio(
            CodigoErro.VALIDACAO,
            campos=[
                CampoErro(
                    campo="mes",
                    codigo="MES_INVALIDO",
                    mensagem="Informe um mês válido (AAAA-MM)",
                )
            ],
        )
    return date(int(texto[:4]), int(texto[5:]), 1)


# Rotas estáticas antes das rotas com `{id}` (arquitetura §9).


@router.get("")
async def consultar_importancias(  # noqa: PLR0913
    *,
    sessao: SessaoDep,
    contexto: ContextoDep,
    filtro: Annotated[FiltroImportancia, Query()] = FiltroImportancia.TODOS,
    mes: Annotated[str | None, Query(pattern=PADRAO_MES)] = None,
    busca: Annotated[str, Query(max_length=100)] = "",
    limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PADRAO,
    cursor: Annotated[str | None, Query()] = None,
) -> ConsultaImportanciasResposta:
    resposta = await importancias.consultar(
        sessao,
        contexto,
        importancias.FiltrosConsulta(
            filtro=filtro,
            mes=_interpretar_mes(mes),
            busca=busca,
            limite=limite,
            cursor=cursor,
        ),
    )
    await sessao.commit()  # a consulta materializa ocorrências
    return resposta


@router.get("/{importancia_id}")
async def obter_importancia(
    importancia_id: uuid.UUID, sessao: SessaoDep, contexto: ContextoDep
) -> ImportanciaDetalhe:
    return await importancias.obter(sessao, contexto, importancia_id)


@router.post("", status_code=201, response_model=ImportanciaDetalhe)
async def cadastrar_importancia(
    dados: ImportanciaCriacao,
    sessao: SessaoDep,
    contexto: ContextoDep,
    chave: ChaveIdempotenciaDep,
) -> JSONResponse:
    resposta = await executar_idempotente(
        sessao,
        contexto,
        acao=AcaoIdempotente.CADASTRAR_IMPORTANCIA,
        chave=chave,
        conteudo=dados,
        status_sucesso=201,
        operacao=lambda: importancias.criar(sessao, contexto, dados),
    )
    await sessao.commit()
    return JSONResponse(
        status_code=resposta.status,
        content=resposta.corpo,
        headers=(
            {"Idempotency-Replayed": "true"} if resposta.reexecucao else None
        ),
    )


@router.patch("/{importancia_id}")
async def editar_importancia(
    importancia_id: uuid.UUID,
    dados: ImportanciaEdicao,
    sessao: SessaoDep,
    contexto: ContextoDep,
) -> ImportanciaDetalhe:
    resposta = await importancias.editar(
        sessao, contexto, importancia_id, dados
    )
    await sessao.commit()
    return resposta


@router.put("/{importancia_id}/situacao")
async def definir_situacao(
    importancia_id: uuid.UUID,
    dados: SituacaoImportanciaEntrada,
    sessao: SessaoDep,
    contexto: ContextoDep,
) -> ImportanciaDetalhe:
    resposta = await importancias.definir_situacao(
        sessao, contexto, importancia_id, dados.situacao
    )
    await sessao.commit()
    return resposta


@router.delete("/{importancia_id}", status_code=204)
async def excluir_importancia(
    importancia_id: uuid.UUID,
    sessao: SessaoDep,
    contexto: ContextoDep,
    alcance: Annotated[AlcanceSerie, Query()] = AlcanceSerie.SOMENTE_ESTA,
) -> Response:
    await importancias.excluir(sessao, contexto, importancia_id, alcance)
    await sessao.commit()
    return Response(status_code=204)
