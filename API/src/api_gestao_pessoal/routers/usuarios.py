"""Endpoint do usuário autenticado."""

from fastapi import APIRouter

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import ContextoDep
from api_gestao_pessoal.schemas.usuario import UsuarioResposta
from api_gestao_pessoal.services import identidade

router = APIRouter(prefix="/usuarios", tags=["usuários"])


@router.get("/me")
async def obter_usuario_atual(
    sessao: SessaoDep, contexto: ContextoDep
) -> UsuarioResposta:
    return await identidade.obter_usuario_atual(sessao, contexto)
