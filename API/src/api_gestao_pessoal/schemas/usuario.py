"""Schema de resposta do usuário."""

import uuid
from datetime import date

from pydantic import BaseModel


class UsuarioResposta(BaseModel):
    """Dados do próprio usuário (nunca inclui hashes)."""

    id: uuid.UUID
    nome_completo: str
    email: str
    data_nascimento: date
    fuso_horario: str
