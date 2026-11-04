"""Schemas dos catálogos de categorias (arquitetura §9.2)."""

import uuid

from pydantic import BaseModel

from api_gestao_pessoal.models.enums import TipoMovimentacao


class CategoriaResposta(BaseModel):
    """Categoria de atividade ou de importância."""

    id: uuid.UUID
    nome: str


class CategoriaFinanceiraResposta(BaseModel):
    """Categoria de receita ou de despesa."""

    id: uuid.UUID
    nome: str
    tipo: TipoMovimentacao
