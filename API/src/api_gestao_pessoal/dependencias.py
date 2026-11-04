"""Dependências HTTP: relógio, recursos da aplicação e contexto (§8.10)."""

import re
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Header, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.email import EnviadorEmail
from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.seguranca import (
    TAMANHO_MAXIMO_TOKEN,
    ConfiguracaoToken,
    HasherSenha,
)
from api_gestao_pessoal.services import identidade
from api_gestao_pessoal.settings import Settings
from api_gestao_pessoal.tempo import ContextoUsuario, Relogio, RelogioSistema

_RELOGIO_SISTEMA = RelogioSistema()
_ESQUEMA_BEARER = HTTPBearer(auto_error=False)


def obter_relogio() -> Relogio:
    """Relógio da aplicação (os testes o substituem por `RelogioFixo`)."""
    return _RELOGIO_SISTEMA


RelogioDep = Annotated[Relogio, Depends(obter_relogio)]


def obter_settings_app(request: Request) -> Settings:
    """Settings em uso pela aplicação."""
    return request.app.state.settings


SettingsDep = Annotated[Settings, Depends(obter_settings_app)]


def obter_hasher(request: Request) -> HasherSenha:
    """Hasher criado no `lifespan`."""
    return request.app.state.hasher


HasherDep = Annotated[HasherSenha, Depends(obter_hasher)]


def obter_enviador_email(request: Request) -> EnviadorEmail:
    """Enviador de e-mail criado no `lifespan`."""
    return request.app.state.enviador_email


EnviadorEmailDep = Annotated[EnviadorEmail, Depends(obter_enviador_email)]


def obter_configuracao_token(settings: SettingsDep) -> ConfiguracaoToken:
    """Segredo e validade dos tokens, a partir das Settings."""
    return ConfiguracaoToken(
        segredo=settings.JWT_SEGREDO,
        validade=timedelta(minutes=settings.JWT_VALIDADE_MINUTOS),
    )


ConfiguracaoTokenDep = Annotated[
    ConfiguracaoToken, Depends(obter_configuracao_token)
]


def sem_cache(response: Response) -> None:
    """`Cache-Control: no-store` na resposta de sucesso."""
    response.headers["Cache-Control"] = "no-store"


async def obter_contexto(
    sessao: SessaoDep,
    relogio: RelogioDep,
    configuracao: ConfiguracaoTokenDep,
    credenciais: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_ESQUEMA_BEARER)
    ],
) -> ContextoUsuario:
    """Contexto do usuário autenticado; o instante é capturado primeiro."""
    agora = relogio.agora()
    if (
        credenciais is None
        or len(credenciais.credentials) > TAMANHO_MAXIMO_TOKEN
    ):
        raise ErroNegocio(
            CodigoErro.NAO_AUTENTICADO,
            cabecalhos=identidade.CABECALHO_BEARER,
        )
    return await identidade.montar_contexto(
        sessao, credenciais.credentials, agora, configuracao
    )


ContextoDep = Annotated[ContextoUsuario, Depends(obter_contexto)]


PADRAO_CHAVE_IDEMPOTENCIA = re.compile(r"[A-Za-z0-9_-]{16,64}")


def obter_chave_idempotencia(
    chave: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> str:
    """`Idempotency-Key` obrigatória e no formato do contrato (§4.3)."""
    if chave is None:
        raise ErroNegocio(CodigoErro.IDEMPOTENCIA_CHAVE_AUSENTE)
    if not PADRAO_CHAVE_IDEMPOTENCIA.fullmatch(chave):
        raise ErroNegocio(CodigoErro.IDEMPOTENCIA_CHAVE_INVALIDA)
    return chave


ChaveIdempotenciaDep = Annotated[str, Depends(obter_chave_idempotencia)]
