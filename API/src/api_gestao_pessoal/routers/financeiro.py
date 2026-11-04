"""Endpoints do financeiro (F6; vínculo com importâncias na F8)."""

import re
import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ChaveIdempotenciaDep, ContextoDep
from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.schemas.comum import Pagina
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.schemas.financeiro import (
    ConsultaMovimentacoesResposta,
    DespesaCriacao,
    DespesaDisponivel,
    FiltroTipo,
    MovimentacaoDetalhe,
    MovimentacaoEdicao,
    ReceitaCriacao,
    ResumoFinanceiroResposta,
)
from api_gestao_pessoal.services import (
    financeiro,
    pagamentos,
    resumo_financeiro,
)
from api_gestao_pessoal.services.idempotencia import (
    AcaoIdempotente,
    RespostaIdempotente,
    executar_idempotente,
)
from api_gestao_pessoal.services.paginacao import (
    LIMITE_MAXIMO,
    LIMITE_PADRAO,
)

router = APIRouter(prefix="/financeiro", tags=["financeiro"])

PADRAO_MES = r"^[0-9]{4}-(0[1-9]|1[0-2])$"
ANO_MINIMO, ANO_MAXIMO = 2000, 2100
MesQuery = Annotated[str | None, Query(pattern=PADRAO_MES)]


def interpretar_mes(texto: str | None, hoje: date) -> date:
    """`AAAA-MM` -> primeiro dia do mês (padrão: mês de hoje)."""
    if texto is None:
        return hoje.replace(day=1)
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


def _resposta_idempotente(resposta: RespostaIdempotente) -> JSONResponse:
    return JSONResponse(
        status_code=resposta.status,
        content=resposta.corpo,
        headers=(
            {"Idempotency-Replayed": "true"} if resposta.reexecucao else None
        ),
    )


@router.post("/receitas", status_code=201, response_model=MovimentacaoDetalhe)
async def cadastrar_receita(
    dados: ReceitaCriacao,
    sessao: SessaoDep,
    contexto: ContextoDep,
    chave: ChaveIdempotenciaDep,
) -> JSONResponse:
    resposta = await executar_idempotente(
        sessao,
        contexto,
        acao=AcaoIdempotente.CADASTRAR_RECEITA,
        chave=chave,
        conteudo=dados,
        status_sucesso=201,
        operacao=lambda: financeiro.criar_receita(sessao, contexto, dados),
    )
    await sessao.commit()
    return _resposta_idempotente(resposta)


@router.post("/despesas", status_code=201, response_model=MovimentacaoDetalhe)
async def cadastrar_despesa(
    dados: DespesaCriacao,
    sessao: SessaoDep,
    contexto: ContextoDep,
    chave: ChaveIdempotenciaDep,
) -> JSONResponse:
    resposta = await executar_idempotente(
        sessao,
        contexto,
        acao=AcaoIdempotente.CADASTRAR_DESPESA,
        chave=chave,
        conteudo=dados,
        status_sucesso=201,
        operacao=lambda: (
            pagamentos.registrar_pagamento(sessao, contexto, dados)
            if dados.importancia_id is not None
            else financeiro.criar_despesa(sessao, contexto, dados)
        ),
    )
    await sessao.commit()
    return _resposta_idempotente(resposta)


@router.get("/movimentacoes")
async def consultar_movimentacoes(  # noqa: PLR0913
    *,
    sessao: SessaoDep,
    contexto: ContextoDep,
    mes: MesQuery = None,
    tipo: Annotated[FiltroTipo, Query()] = FiltroTipo.TODAS,
    categoria_id: Annotated[uuid.UUID | None, Query()] = None,
    busca: Annotated[str, Query(max_length=100)] = "",
    limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PADRAO,
    cursor: Annotated[str | None, Query()] = None,
) -> ConsultaMovimentacoesResposta:
    return await financeiro.consultar(
        sessao,
        contexto,
        mes=interpretar_mes(mes, contexto.hoje),
        tipo=tipo,
        categoria_id=categoria_id,
        busca=busca,
        limite=limite,
        cursor=cursor,
    )


@router.get("/despesas/disponiveis-vinculo")
async def despesas_disponiveis_para_vinculo(
    sessao: SessaoDep,
    contexto: ContextoDep,
    busca: Annotated[str, Query(max_length=100)] = "",
    limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PADRAO,
    cursor: Annotated[str | None, Query()] = None,
) -> Pagina[DespesaDisponivel]:
    return await pagamentos.despesas_disponiveis(
        sessao, contexto, busca=busca, limite=limite, cursor=cursor
    )


@router.get("/resumo")
async def resumo(
    sessao: SessaoDep, contexto: ContextoDep, mes: MesQuery = None
) -> ResumoFinanceiroResposta:
    return await resumo_financeiro.resumo(
        sessao, contexto, interpretar_mes(mes, contexto.hoje)
    )


@router.get("/movimentacoes/{movimentacao_id}")
async def obter_movimentacao(
    movimentacao_id: uuid.UUID, sessao: SessaoDep, contexto: ContextoDep
) -> MovimentacaoDetalhe:
    return await financeiro.obter(sessao, contexto, movimentacao_id)


@router.patch("/movimentacoes/{movimentacao_id}")
async def editar_movimentacao(
    movimentacao_id: uuid.UUID,
    dados: MovimentacaoEdicao,
    sessao: SessaoDep,
    contexto: ContextoDep,
) -> MovimentacaoDetalhe:
    if "importancia_id" in dados.model_fields_set:
        resposta = await pagamentos.alterar_vinculo_despesa(
            sessao, contexto, movimentacao_id, dados
        )
    else:
        resposta = await financeiro.editar(
            sessao, contexto, movimentacao_id, dados
        )
    await sessao.commit()
    return resposta


@router.delete("/movimentacoes/{movimentacao_id}", status_code=204)
async def excluir_movimentacao(
    movimentacao_id: uuid.UUID, sessao: SessaoDep, contexto: ContextoDep
) -> Response:
    await financeiro.excluir(sessao, contexto, movimentacao_id)
    await sessao.commit()
    return Response(status_code=204)
