"""Recuperação de senha em três etapas (arquitetura §8.3)."""

import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal import seguranca
from api_gestao_pessoal.email import (
    EnviadorEmail,
    FalhaEnvioEmail,
    mensagem_codigo,
)
from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import RecuperacaoSenha, Usuario
from api_gestao_pessoal.schemas.autenticacao import (
    MensagemResposta,
    RedefinirSenhaEntrada,
    SolicitacaoCodigoResposta,
    SolicitarCodigoEntrada,
    VerificarCodigoEntrada,
)
from api_gestao_pessoal.seguranca import HasherSenha
from api_gestao_pessoal.tempo import Relogio

VALIDADE_CODIGO = timedelta(minutes=10)
MAX_TENTATIVAS = 5
INTERVALO_REENVIO = timedelta(seconds=60)
MENSAGEM_REDEFINIDA = "Redefinição de senha concluída com sucesso"


@dataclass(frozen=True, slots=True)
class ResultadoVerificacao:
    """Resultado esperado da verificação (nunca lança, arquitetura §5.3)."""

    erro: CodigoErro | None
    token: str | None = None
    expira_em: datetime | None = None
    retry_after_s: int | None = None


@dataclass(frozen=True, slots=True)
class _Emissao:
    codigo: str
    agora: datetime


def _em_utc(instante: datetime) -> datetime:
    """Mesmo instante em UTC; um valor sem fuso é defeito (timestamptz)."""
    if instante.utcoffset() is None:
        msg = "instante sem fuso"
        raise RuntimeError(msg)
    return instante.astimezone(UTC)


def _segundos_ate_reenvio(rec: RecuperacaoSenha, agora: datetime) -> int:
    emitido_em = rec.expira_em - VALIDADE_CODIGO
    restante = emitido_em + INTERVALO_REENVIO - agora
    return max(1, math.ceil(restante.total_seconds()))


def _reenvio_permitido(rec: RecuperacaoSenha, agora: datetime) -> bool:
    return agora >= rec.expira_em - VALIDADE_CODIGO + INTERVALO_REENVIO


async def _travar_por_usuario(
    sessao: AsyncSession, usuario_id: uuid.UUID
) -> RecuperacaoSenha | None:
    return await sessao.scalar(
        select(RecuperacaoSenha)
        .where(RecuperacaoSenha.usuario_id == usuario_id)
        .with_for_update()
    )


async def _primeira_emissao(
    sessao: AsyncSession,
    usuario_id: uuid.UUID,
    relogio: Relogio,
    hasher: HasherSenha,
) -> _Emissao | None:
    """`INSERT … ON CONFLICT DO NOTHING`; `None` se outro confirmou antes."""
    agora = relogio.agora()
    codigo = seguranca.gerar_codigo()
    novo_id = await sessao.scalar(
        pg_insert(RecuperacaoSenha)
        .values(
            id=uuid.uuid7(),
            usuario_id=usuario_id,
            tentativas=0,
            codigo_hash=await hasher.gerar(codigo),
            expira_em=agora + VALIDADE_CODIGO,
        )
        .on_conflict_do_nothing(index_elements=["usuario_id"])
        .returning(RecuperacaoSenha.id)
    )
    return None if novo_id is None else _Emissao(codigo=codigo, agora=agora)


async def _reemitir(
    rec: RecuperacaoSenha, relogio: Relogio, hasher: HasherSenha
) -> _Emissao:
    """Reenvio: substitui o código e limpa verificação, token e uso."""
    agora = relogio.agora()
    if not _reenvio_permitido(rec, agora):
        raise ErroNegocio(
            CodigoErro.REENVIO_MUITO_FREQUENTE,
            cabecalhos={"Retry-After": str(_segundos_ate_reenvio(rec, agora))},
        )
    codigo = seguranca.gerar_codigo()
    rec.codigo_hash = await hasher.gerar(codigo)
    rec.expira_em = agora + VALIDADE_CODIGO
    rec.tentativas = 0
    rec.verificado_em = None
    rec.token_redefinicao_hash = None
    rec.utilizado_em = None
    return _Emissao(codigo=codigo, agora=agora)


async def _emitir(
    sessao: AsyncSession,
    usuario_id: uuid.UUID,
    relogio: Relogio,
    hasher: HasherSenha,
) -> _Emissao:
    rec = await _travar_por_usuario(sessao, usuario_id)
    if rec is None:
        emissao = await _primeira_emissao(sessao, usuario_id, relogio, hasher)
        if emissao is not None:
            return emissao
        rec = await _travar_por_usuario(sessao, usuario_id)
    if rec is None:
        msg = "recuperação inexistente após conflito"
        raise RuntimeError(msg)
    return await _reemitir(rec, relogio, hasher)


async def solicitar_codigo(
    sessao: AsyncSession,
    dados: SolicitarCodigoEntrada,
    relogio: Relogio,
    hasher: HasherSenha,
    enviador: EnviadorEmail,
) -> SolicitacaoCodigoResposta:
    """Emite (ou reemite) o código e o envia antes do commit."""
    usuario = await sessao.scalar(
        select(Usuario).where(Usuario.email == dados.email)
    )
    if usuario is None:
        raise ErroNegocio(CodigoErro.EMAIL_NAO_ENCONTRADO)
    emissao = await _emitir(sessao, usuario.id, relogio, hasher)
    await sessao.flush()
    try:
        await enviador.enviar(
            mensagem_codigo(
                usuario.nome_completo, usuario.email, emissao.codigo
            )
        )
    except FalhaEnvioEmail:
        raise ErroNegocio(CodigoErro.FALHA_ENVIO_EMAIL) from None
    return SolicitacaoCodigoResposta(
        expira_em=emissao.agora + VALIDADE_CODIGO,
        reenvio_permitido_em=emissao.agora + INTERVALO_REENVIO,
    )


def _motivo_recusa(
    rec: RecuperacaoSenha, agora: datetime
) -> CodigoErro | None:
    if rec.verificado_em is not None or rec.utilizado_em is not None:
        return CodigoErro.CODIGO_JA_VERIFICADO
    if agora >= rec.expira_em:
        return CodigoErro.CODIGO_EXPIRADO
    if rec.tentativas >= MAX_TENTATIVAS:
        return CodigoErro.TENTATIVAS_ESGOTADAS
    return None


async def verificar_codigo(
    sessao: AsyncSession,
    dados: VerificarCodigoEntrada,
    relogio: Relogio,
    hasher: HasherSenha,
) -> ResultadoVerificacao:
    """Verifica o código; o router confirma a transação antes do erro."""
    rec = await sessao.scalar(
        select(RecuperacaoSenha)
        .join(Usuario, Usuario.id == RecuperacaoSenha.usuario_id)
        .where(Usuario.email == dados.email)
        .with_for_update(of=RecuperacaoSenha)
    )
    if rec is None:
        return ResultadoVerificacao(erro=CodigoErro.CODIGO_INVALIDO)
    agora = relogio.agora()
    motivo = _motivo_recusa(rec, agora)
    if motivo is CodigoErro.TENTATIVAS_ESGOTADAS:
        return ResultadoVerificacao(
            erro=motivo, retry_after_s=_segundos_ate_reenvio(rec, agora)
        )
    if motivo is not None:
        return ResultadoVerificacao(erro=motivo)
    if not await hasher.verificar(rec.codigo_hash, dados.codigo):
        rec.tentativas += 1
        await sessao.flush()
        return ResultadoVerificacao(erro=CodigoErro.CODIGO_INVALIDO)
    token = seguranca.gerar_token_redefinicao()
    rec.verificado_em = agora
    rec.token_redefinicao_hash = seguranca.hash_token(token)
    await sessao.flush()
    return ResultadoVerificacao(
        erro=None, token=token, expira_em=_em_utc(rec.expira_em)
    )


async def redefinir_senha(
    sessao: AsyncSession,
    dados: RedefinirSenhaEntrada,
    relogio: Relogio,
    hasher: HasherSenha,
) -> MensagemResposta:
    """Troca a senha com o token de uso único."""
    rec = await sessao.scalar(
        select(RecuperacaoSenha)
        .where(
            RecuperacaoSenha.token_redefinicao_hash
            == seguranca.hash_token(dados.token_redefinicao)
        )
        .with_for_update()
    )
    agora = relogio.agora()
    if (
        rec is None
        or rec.verificado_em is None
        or rec.utilizado_em is not None
        or agora >= rec.expira_em
    ):
        raise ErroNegocio(CodigoErro.TOKEN_REDEFINICAO_INVALIDO)
    usuario = await sessao.get(Usuario, rec.usuario_id)
    if usuario is None:
        msg = "usuário da recuperação inexistente"
        raise RuntimeError(msg)
    usuario.senha_hash = await hasher.gerar(dados.nova_senha)
    rec.utilizado_em = agora
    await sessao.flush()
    return MensagemResposta(mensagem=MENSAGEM_REDEFINIDA)
