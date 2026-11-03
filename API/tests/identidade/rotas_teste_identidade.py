"""Rotas exclusivas de testes de identidade (nunca incluídas no app real)."""

import uuid

from fastapi import APIRouter

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ContextoDep
from api_gestao_pessoal.models import Importancia
from api_gestao_pessoal.services.autorizacao import obter_do_usuario_ou_404

router = APIRouter(prefix="/teste")


@router.get("/contexto")
async def ver_contexto(contexto: ContextoDep) -> dict[str, str]:
    return {
        "usuario_id": str(contexto.usuario_id),
        "fuso": str(contexto.fuso),
        "agora": contexto.agora.isoformat(),
        "hoje": contexto.hoje.isoformat(),
    }


@router.get("/importancias/{importancia_id}")
async def ver_importancia(
    importancia_id: uuid.UUID, sessao: SessaoDep, contexto: ContextoDep
) -> dict[str, str]:
    recurso = await obter_do_usuario_ou_404(
        sessao, Importancia, importancia_id, contexto.usuario_id
    )
    return {"id": str(recurso.id)}
