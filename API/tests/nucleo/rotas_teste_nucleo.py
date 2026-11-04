"""Rota exclusiva de testes do mecanismo de idempotência (F4)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ChaveIdempotenciaDep, ContextoDep
from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.services.idempotencia import (
    AcaoIdempotente,
    executar_idempotente,
)

router = APIRouter(prefix="/teste-nucleo")


class CorpoRegistro(BaseModel):
    valor: str


class RespostaRegistro(BaseModel):
    id: uuid.UUID
    valor: str


@router.post("/registros", status_code=201)
async def criar_registro(
    corpo: CorpoRegistro,
    sessao: SessaoDep,
    contexto: ContextoDep,
    chave: ChaveIdempotenciaDep,
    falhar: Annotated[bool, Query()] = False,  # noqa: FBT002
) -> JSONResponse:
    async def operacao() -> RespostaRegistro:
        novo = uuid.uuid7()
        await sessao.execute(
            text(
                "INSERT INTO teste_nucleo_registro (id, usuario_id, valor) "
                "VALUES (:id, :usuario_id, :valor)"
            ),
            {
                "id": novo,
                "usuario_id": contexto.usuario_id,
                "valor": corpo.valor,
            },
        )
        if falhar:
            raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
        return RespostaRegistro(id=novo, valor=corpo.valor)

    resposta = await executar_idempotente(
        sessao,
        contexto,
        acao=AcaoIdempotente.CADASTRAR_ATIVIDADE,
        chave=chave,
        conteudo=corpo,
        status_sucesso=201,
        operacao=operacao,
    )
    await sessao.commit()
    return JSONResponse(
        status_code=resposta.status,
        content=resposta.corpo,
        headers={"Idempotency-Replayed": "true"}
        if resposta.reexecucao
        else None,
    )
