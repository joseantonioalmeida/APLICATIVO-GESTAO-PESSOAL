"""Rotas exclusivas de testes de transação (nunca incluídas no app real)."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import text

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.erros import CampoErro, CodigoErro, ErroNegocio
from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.settings import Settings

CHAVE_TRAVA = 4242
# Valores sintéticos que nunca podem aparecer em logs ou respostas.
SENTINELA_UNICO = "sentinela-unico-7f3a"
SENTINELA_LINHA = "sentinela-linha-9c2e"

router = APIRouter(prefix="/teste")


def criar_app_teste(settings: Settings) -> FastAPI:
    """App real com o router de teste incluído (somente nos testes)."""
    app = criar_app(settings)
    app.include_router(router)
    return app


INSERIR_REGISTRO = text(
    "INSERT INTO teste_infra.registro (id, valor, unico) "
    "VALUES (:id, :valor, :unico)"
)


class NovoRegistro(BaseModel):
    valor: str


class CorpoValidacao(BaseModel):
    nome: str = Field(min_length=3)
    senha: str
    quantidade: int


async def consultar_antes(sessao: SessaoDep) -> int:
    """Dependência que inicia a transação (autobegin) antes do endpoint."""
    await sessao.execute(text("SELECT 1"))
    return id(sessao)


@router.post("/registros", status_code=201)
async def criar_registro(
    corpo: NovoRegistro, sessao: SessaoDep
) -> dict[str, str]:
    novo_id = uuid.uuid7()
    await sessao.execute(
        INSERIR_REGISTRO, {"id": novo_id, "valor": corpo.valor, "unico": None}
    )
    await sessao.commit()
    return {"id": str(novo_id)}


@router.post("/registros/erro-apos-escrita")
async def erro_apos_escrita(sessao: SessaoDep) -> None:
    await sessao.execute(
        INSERIR_REGISTRO,
        {"id": uuid.uuid7(), "valor": "descartado", "unico": None},
    )
    raise ErroNegocio(CodigoErro.VALIDACAO, "erro de teste")


@router.post("/registros/com-dependencia", status_code=201)
async def com_dependencia(
    sessao: SessaoDep,
    id_sessao_dependencia: Annotated[int, Depends(consultar_antes)],
) -> dict[str, Any]:
    novo_id = uuid.uuid7()
    await sessao.execute(
        INSERIR_REGISTRO,
        {"id": novo_id, "valor": "com-dependencia", "unico": None},
    )
    await sessao.commit()
    return {
        "id": str(novo_id),
        "mesma_sessao": id_sessao_dependencia == id(sessao),
    }


@router.post("/registros/falha-no-commit")
async def falha_no_commit(sessao: SessaoDep) -> None:
    for _ in range(2):
        await sessao.execute(
            INSERIR_REGISTRO,
            {
                "id": uuid.uuid7(),
                "valor": "duplicado",
                "unico": SENTINELA_UNICO,
            },
        )
    await sessao.commit()


@router.post("/registros/violacao-nao-nulo")
async def violacao_nao_nulo(sessao: SessaoDep) -> None:
    await sessao.execute(
        INSERIR_REGISTRO,
        {"id": uuid.uuid7(), "valor": None, "unico": SENTINELA_LINHA},
    )
    await sessao.commit()


@router.post("/trava")
async def trava(sessao: SessaoDep) -> dict[str, bool]:
    await sessao.execute(
        text("SELECT pg_advisory_xact_lock(:chave)"), {"chave": CHAVE_TRAVA}
    )
    await sessao.commit()
    return {"ok": True}


@router.get("/erro-negocio")
async def erro_negocio() -> None:
    raise ErroNegocio(
        CodigoErro.VALIDACAO,
        "Mensagem de teste",
        campos=[
            CampoErro(
                campo="nome",
                codigo="NOME_OBRIGATORIO",
                mensagem="Informe o nome",
            )
        ],
        detalhes={"chave": "valor"},
        cabecalhos={"X-Teste": "1"},
    )


@router.post("/validacao")
async def validacao(corpo: CorpoValidacao) -> dict[str, bool]:
    del corpo
    return {"ok": True}


@router.get("/excecao")
async def excecao() -> None:
    msg = "falha interna de teste"
    raise RuntimeError(msg)
