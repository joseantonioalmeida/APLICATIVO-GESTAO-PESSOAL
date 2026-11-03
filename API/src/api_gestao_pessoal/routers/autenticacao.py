"""Endpoints de cadastro, login e recuperação de senha."""

from fastapi import APIRouter, Depends

from api_gestao_pessoal.database import SessaoDep
from api_gestao_pessoal.dependencias import (
    ConfiguracaoTokenDep,
    EnviadorEmailDep,
    HasherDep,
    RelogioDep,
    sem_cache,
)
from api_gestao_pessoal.erros import ErroNegocio
from api_gestao_pessoal.schemas.autenticacao import (
    LoginEntrada,
    MensagemResposta,
    RedefinirSenhaEntrada,
    RegistroEntrada,
    SolicitacaoCodigoResposta,
    SolicitarCodigoEntrada,
    TokenResposta,
    VerificacaoCodigoResposta,
    VerificarCodigoEntrada,
)
from api_gestao_pessoal.schemas.usuario import UsuarioResposta
from api_gestao_pessoal.services import identidade, recuperacao_senha

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/registro", status_code=201)
async def registrar(
    dados: RegistroEntrada,
    sessao: SessaoDep,
    relogio: RelogioDep,
    hasher: HasherDep,
) -> UsuarioResposta:
    resposta = await identidade.registrar(sessao, dados, relogio, hasher)
    await sessao.commit()
    return resposta


@router.post("/login", dependencies=[Depends(sem_cache)])
async def entrar(
    dados: LoginEntrada,
    sessao: SessaoDep,
    relogio: RelogioDep,
    hasher: HasherDep,
    configuracao: ConfiguracaoTokenDep,
) -> TokenResposta:
    return await identidade.entrar(
        sessao, dados, relogio, hasher, configuracao
    )


@router.post("/recuperacao/solicitar")
async def solicitar_codigo(
    dados: SolicitarCodigoEntrada,
    sessao: SessaoDep,
    relogio: RelogioDep,
    hasher: HasherDep,
    enviador: EnviadorEmailDep,
) -> SolicitacaoCodigoResposta:
    resposta = await recuperacao_senha.solicitar_codigo(
        sessao, dados, relogio, hasher, enviador
    )
    await sessao.commit()
    return resposta


@router.post("/recuperacao/verificar", dependencies=[Depends(sem_cache)])
async def verificar_codigo(
    dados: VerificarCodigoEntrada,
    sessao: SessaoDep,
    relogio: RelogioDep,
    hasher: HasherDep,
) -> VerificacaoCodigoResposta:
    resultado = await recuperacao_senha.verificar_codigo(
        sessao, dados, relogio, hasher
    )
    # A tentativa (ou o token) é confirmada antes de qualquer recusa.
    await sessao.commit()
    if resultado.erro is not None:
        cabecalhos = (
            None
            if resultado.retry_after_s is None
            else {"Retry-After": str(resultado.retry_after_s)}
        )
        raise ErroNegocio(resultado.erro, cabecalhos=cabecalhos)
    if resultado.token is None or resultado.expira_em is None:
        msg = "verificação bem-sucedida sem token"
        raise RuntimeError(msg)
    return VerificacaoCodigoResposta(
        token_redefinicao=resultado.token, expira_em=resultado.expira_em
    )


@router.post("/recuperacao/redefinir")
async def redefinir_senha(
    dados: RedefinirSenhaEntrada,
    sessao: SessaoDep,
    relogio: RelogioDep,
    hasher: HasherDep,
) -> MensagemResposta:
    resposta = await recuperacao_senha.redefinir_senha(
        sessao, dados, relogio, hasher
    )
    await sessao.commit()
    return resposta
