"""Cursores keyset opacos (arquitetura §4.1)."""

import base64
import binascii
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio

VERSAO_CURSOR = 1
LIMITE_PADRAO = 20
LIMITE_MAXIMO = 50
TAMANHO_MAXIMO_CURSOR = 1024


def hash_dos_filtros(filtros: Mapping[str, Any]) -> str:
    """Oito hex do SHA-256 dos filtros normalizados."""
    canonico = json.dumps(
        dict(filtros),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(canonico.encode()).hexdigest()[:8]


def codificar_cursor(
    ordenacao: str, filtros: Mapping[str, Any], chaves: Sequence[Any]
) -> str:
    """Cursor opaco: base64url de `{"v","o","f","k"}`."""
    corpo = {
        "v": VERSAO_CURSOR,
        "o": ordenacao,
        "f": hash_dos_filtros(filtros),
        "k": list(chaves),
    }
    bruto = json.dumps(corpo, separators=(",", ":"), ensure_ascii=False)
    return base64.urlsafe_b64encode(bruto.encode()).decode().rstrip("=")


def decodificar_cursor(
    cursor: str, ordenacao: str, filtros: Mapping[str, Any]
) -> list[Any]:
    """Chaves do cursor; qualquer divergência vira `CURSOR_INVALIDO`."""
    erro = ErroNegocio(CodigoErro.CURSOR_INVALIDO)
    if not cursor or len(cursor) > TAMANHO_MAXIMO_CURSOR:
        raise erro
    try:
        preenchido = cursor + "=" * (-len(cursor) % 4)
        corpo = json.loads(base64.urlsafe_b64decode(preenchido.encode()))
    except (binascii.Error, ValueError, UnicodeError) as exc:
        raise erro from exc
    if (
        not isinstance(corpo, dict)
        or corpo.get("v") != VERSAO_CURSOR
        or corpo.get("o") != ordenacao
        or corpo.get("f") != hash_dos_filtros(filtros)
        or not isinstance(corpo.get("k"), list)
    ):
        raise erro
    return corpo["k"]


def escapar_busca(texto: str) -> str:
    """Escapa `\\`, `%` e `_` para `ILIKE ... ESCAPE '\\'`."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
