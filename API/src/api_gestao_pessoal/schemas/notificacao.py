"""Schemas de notificações (arquitetura §9.6)."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ImportanciaDaNotificacao(BaseModel):
    """Importância de origem; `disponivel` é falso se foi excluída."""

    id: uuid.UUID
    disponivel: bool


class NotificacaoItem(BaseModel):
    """Notificação interna (sino da tela inicial)."""

    id: uuid.UUID
    titulo: str
    mensagem: str
    criada_em: datetime
    lida: bool
    importancia: ImportanciaDaNotificacao


class NaoLidasResposta(BaseModel):
    """Quantidade de notificações não lidas."""

    quantidade: int
