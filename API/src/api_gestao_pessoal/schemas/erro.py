from typing import Any

from pydantic import BaseModel, Field


class CampoErro(BaseModel):
    campo: str
    codigo: str
    mensagem: str


class RespostaErro(BaseModel):
    codigo: str
    mensagem: str
    campos: list[CampoErro] = Field(default_factory=list)
    detalhes: dict[str, Any] | None = None
    id_requisicao: str | None = None
