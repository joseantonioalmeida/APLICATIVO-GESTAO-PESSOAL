"""Registro, login e contexto do usuário autenticado (arquitetura §8.2)."""

import hmac
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg.errors
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import Usuario
from api_gestao_pessoal.schemas.autenticacao import (
    LoginEntrada,
    RegistroEntrada,
    TokenResposta,
    canonicalizar_email,
)
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.schemas.usuario import UsuarioResposta
from api_gestao_pessoal.seguranca import (
    ConfiguracaoToken,
    HasherSenha,
    TokenInvalido,
    carimbo,
    decodificar_token,
    emitir_token,
)
from api_gestao_pessoal.tempo import (
    ContextoUsuario,
    Relogio,
    hoje_no_fuso,
)

CABECALHO_BEARER = {"WWW-Authenticate": "Bearer"}
MENSAGEM_NASCIMENTO_FUTURO = "A data de nascimento não pode ser futura"
RESTRICAO_EMAIL_UNICO = "uq_usuario_email"


def _resposta(usuario: Usuario) -> UsuarioResposta:
    return UsuarioResposta(
        id=usuario.id,
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        data_nascimento=usuario.data_nascimento,
        fuso_horario=usuario.fuso_horario,
    )


def _violou_email_unico(erro: IntegrityError) -> bool:
    origem = erro.orig
    return (
        isinstance(origem, psycopg.errors.UniqueViolation)
        and origem.diag.constraint_name == RESTRICAO_EMAIL_UNICO
    )


async def registrar(
    sessao: AsyncSession,
    dados: RegistroEntrada,
    relogio: Relogio,
    hasher: HasherSenha,
) -> UsuarioResposta:
    """Cria a conta; a unicidade do e-mail é garantida pelo banco."""
    agora = relogio.agora()
    hoje = hoje_no_fuso(agora, ZoneInfo(dados.fuso_horario))
    if dados.data_nascimento > hoje:
        raise ErroNegocio(
            CodigoErro.VALIDACAO,
            campos=[
                CampoErro(
                    campo="data_nascimento",
                    codigo="DATA_NASCIMENTO_FUTURA",
                    mensagem=MENSAGEM_NASCIMENTO_FUTURO,
                )
            ],
        )
    existente = await sessao.scalar(
        select(Usuario.id).where(Usuario.email == dados.email)
    )
    if existente is not None:
        raise ErroNegocio(CodigoErro.EMAIL_JA_CADASTRADO)
    usuario = Usuario(
        nome_completo=dados.nome_completo,
        email=dados.email,
        data_nascimento=dados.data_nascimento,
        fuso_horario=dados.fuso_horario,
        senha_hash=await hasher.gerar(dados.senha),
    )
    sessao.add(usuario)
    try:
        await sessao.flush()
    except IntegrityError as erro:
        if _violou_email_unico(erro):
            raise ErroNegocio(CodigoErro.EMAIL_JA_CADASTRADO) from None
        raise
    return _resposta(usuario)


async def entrar(
    sessao: AsyncSession,
    dados: LoginEntrada,
    relogio: Relogio,
    hasher: HasherSenha,
    configuracao: ConfiguracaoToken,
) -> TokenResposta:
    """Login; e-mail inexistente ou malformado segue o mesmo caminho."""
    email = canonicalizar_email(dados.email)
    usuario = (
        None
        if email is None
        else await sessao.scalar(select(Usuario).where(Usuario.email == email))
    )
    if usuario is None:
        await hasher.verificar_ficticio(dados.senha)
        raise ErroNegocio(CodigoErro.CREDENCIAIS_INVALIDAS)
    if not await hasher.verificar(usuario.senha_hash, dados.senha):
        raise ErroNegocio(CodigoErro.CREDENCIAIS_INVALIDAS)
    emitido = emitir_token(
        usuario.id, usuario.senha_hash, relogio.agora(), configuracao
    )
    return TokenResposta(
        access_token=emitido.token,
        token_type="bearer",
        expira_em=emitido.expira_em,
    )


async def montar_contexto(
    sessao: AsyncSession,
    token: str,
    agora: datetime,
    configuracao: ConfiguracaoToken,
) -> ContextoUsuario:
    """Valida o token e o carimbo da credencial; monta o contexto."""
    try:
        claims = decodificar_token(token, agora, configuracao)
    except TokenInvalido:
        raise ErroNegocio(
            CodigoErro.NAO_AUTENTICADO, cabecalhos=CABECALHO_BEARER
        ) from None
    usuario = await sessao.get(Usuario, claims.usuario_id)
    if usuario is None or not hmac.compare_digest(
        claims.sv, carimbo(usuario.senha_hash)
    ):
        raise ErroNegocio(
            CodigoErro.NAO_AUTENTICADO, cabecalhos=CABECALHO_BEARER
        )
    fuso = ZoneInfo(usuario.fuso_horario)
    return ContextoUsuario(
        usuario_id=usuario.id,
        fuso=fuso,
        agora=agora,
        hoje=hoje_no_fuso(agora, fuso),
    )


async def obter_usuario_atual(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> UsuarioResposta:
    """Dados do usuário autenticado (mesmo objeto do mapa de identidade)."""
    usuario = await sessao.get(Usuario, contexto.usuario_id)
    if usuario is None:
        msg = "usuário autenticado inexistente"
        raise RuntimeError(msg)
    return _resposta(usuario)
