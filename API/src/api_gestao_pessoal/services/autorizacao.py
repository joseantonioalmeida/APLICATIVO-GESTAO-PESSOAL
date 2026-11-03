"""Acesso a recursos do próprio usuário (arquitetura §4.2)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import Base


async def obter_do_usuario_ou_404[M: Base](
    sessao: AsyncSession,
    modelo: type[M],
    id_recurso: uuid.UUID,
    usuario_id: uuid.UUID,
    *,
    incluir_excluidos: bool = False,
) -> M:
    """Recurso do usuário; o de outro usuário é igual ao inexistente."""
    colunas = modelo.__table__.c
    if "usuario_id" not in colunas:
        msg = "o modelo não tem a coluna usuario_id"
        raise TypeError(msg)
    consulta = select(modelo).where(
        colunas["id"] == id_recurso, colunas["usuario_id"] == usuario_id
    )
    if "excluida_em" in colunas and not incluir_excluidos:
        consulta = consulta.where(colunas["excluida_em"].is_(None))
    recurso = await sessao.scalar(consulta)
    if recurso is None:
        raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
    return recurso
