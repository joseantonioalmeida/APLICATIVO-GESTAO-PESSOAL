"""Trava transacional por usuário (arquitetura §6.1, DEC-MV-14).

Serializa as escritas de um mesmo usuário com `pg_advisory_xact_lock`.
A trava é liberada pelo próprio PostgreSQL no commit ou no rollback; o
registro em `sessao.info` é limpo pelos listeners abaixo.
"""

import enum
import uuid

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, SessionTransaction

CHAVE_INFO = "trava_usuario"


class ModoTrava(enum.StrEnum):
    """Modo da trava do usuário."""

    EXCLUSIVA = "EXCLUSIVA"
    COMPARTILHADA = "COMPARTILHADA"


_FUNCOES = {
    ModoTrava.EXCLUSIVA: "pg_advisory_xact_lock",
    ModoTrava.COMPARTILHADA: "pg_advisory_xact_lock_shared",
}


def _limpar_ao_fim_da_transacao(
    sessao: Session, transacao: SessionTransaction
) -> None:
    # Só o fim da transação externa (commit, rollback ou close) libera a
    # trava; o rollback de um SAVEPOINT não a libera (§5.2, regra 3).
    if transacao.parent is None:
        sessao.info.pop(CHAVE_INFO, None)


event.listen(Session, "after_transaction_end", _limpar_ao_fim_da_transacao)


async def travar_usuario(
    sessao: AsyncSession, usuario_id: uuid.UUID, modo: ModoTrava
) -> None:
    """Adquire a trava do usuário (reentrante; nunca promove o modo)."""
    atual = sessao.info.get(CHAVE_INFO)
    if atual is not None:
        if atual[0] != usuario_id:
            msg = "trava de outro usuário já adquirida nesta sessão"
            raise RuntimeError(msg)
        if atual[1] == ModoTrava.COMPARTILHADA and modo == ModoTrava.EXCLUSIVA:
            msg = "promoção de trava compartilhada para exclusiva é proibida"
            raise RuntimeError(msg)
        return
    funcao = _FUNCOES[modo]
    await sessao.execute(
        text(f"SELECT {funcao}(hashtextextended(:chave, 0))"),
        {"chave": f"minhavida:usuario:{usuario_id}"},
    )
    sessao.info[CHAVE_INFO] = (usuario_id, modo)
