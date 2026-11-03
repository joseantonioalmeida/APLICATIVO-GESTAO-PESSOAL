from typing import Literal

from pydantic import BaseModel


class SituacaoSaude(BaseModel):
    situacao: Literal["ativo", "pronto"]
