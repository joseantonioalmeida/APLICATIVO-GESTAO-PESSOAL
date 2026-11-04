import logging
import traceback
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api_gestao_pessoal.schemas.erro import CampoErro, RespostaErro

logger = logging.getLogger(__name__)

CABECALHO_ID_REQUISICAO = "X-Request-ID"
ORIGENS_DE_CAMPO = frozenset({"body", "query", "path", "header", "cookie"})
SQLSTATES_CONFLITO = frozenset({"40001", "40P01", "55P03"})
SQLSTATE_TEMPO_ESGOTADO = "57014"


class CodigoErro(StrEnum):
    VALIDACAO = "VALIDACAO"
    CORPO_INVALIDO = "CORPO_INVALIDO"
    RECURSO_NAO_ENCONTRADO = "RECURSO_NAO_ENCONTRADO"
    METODO_NAO_PERMITIDO = "METODO_NAO_PERMITIDO"
    ERRO_HTTP = "ERRO_HTTP"
    CONFLITO_CONCORRENCIA = "CONFLITO_CONCORRENCIA"
    TEMPO_ESGOTADO = "TEMPO_ESGOTADO"
    SERVICO_INDISPONIVEL = "SERVICO_INDISPONIVEL"
    ERRO_INTERNO = "ERRO_INTERNO"
    NAO_AUTENTICADO = "NAO_AUTENTICADO"
    CREDENCIAIS_INVALIDAS = "CREDENCIAIS_INVALIDAS"
    EMAIL_JA_CADASTRADO = "EMAIL_JA_CADASTRADO"
    EMAIL_NAO_ENCONTRADO = "EMAIL_NAO_ENCONTRADO"
    REENVIO_MUITO_FREQUENTE = "REENVIO_MUITO_FREQUENTE"
    FALHA_ENVIO_EMAIL = "FALHA_ENVIO_EMAIL"
    CODIGO_INVALIDO = "CODIGO_INVALIDO"
    CODIGO_EXPIRADO = "CODIGO_EXPIRADO"
    TENTATIVAS_ESGOTADAS = "TENTATIVAS_ESGOTADAS"
    CODIGO_JA_VERIFICADO = "CODIGO_JA_VERIFICADO"
    TOKEN_REDEFINICAO_INVALIDO = "TOKEN_REDEFINICAO_INVALIDO"
    IDEMPOTENCIA_CHAVE_AUSENTE = "IDEMPOTENCIA_CHAVE_AUSENTE"
    IDEMPOTENCIA_CHAVE_INVALIDA = "IDEMPOTENCIA_CHAVE_INVALIDA"
    CHAVE_IDEMPOTENCIA_REUTILIZADA = "CHAVE_IDEMPOTENCIA_REUTILIZADA"
    CURSOR_INVALIDO = "CURSOR_INVALIDO"
    SOBREPOSICAO_HORARIO = "SOBREPOSICAO_HORARIO"
    ALCANCE_INVALIDO = "ALCANCE_INVALIDO"
    REPETICAO_EXIGE_ALCANCE_SERIE = "REPETICAO_EXIGE_ALCANCE_SERIE"


CATALOGO_ERROS: dict[CodigoErro, tuple[HTTPStatus, str]] = {
    CodigoErro.VALIDACAO: (
        HTTPStatus.UNPROCESSABLE_CONTENT,
        "Dados inválidos.",
    ),
    CodigoErro.CORPO_INVALIDO: (
        HTTPStatus.UNPROCESSABLE_CONTENT,
        "Corpo da requisição inválido.",
    ),
    CodigoErro.RECURSO_NAO_ENCONTRADO: (
        HTTPStatus.NOT_FOUND,
        "Recurso não encontrado.",
    ),
    CodigoErro.METODO_NAO_PERMITIDO: (
        HTTPStatus.METHOD_NOT_ALLOWED,
        "Método não permitido.",
    ),
    CodigoErro.ERRO_HTTP: (
        HTTPStatus.BAD_REQUEST,
        "Não foi possível processar a requisição.",
    ),
    CodigoErro.CONFLITO_CONCORRENCIA: (
        HTTPStatus.SERVICE_UNAVAILABLE,
        "Não foi possível concluir a operação agora. Tente novamente.",
    ),
    CodigoErro.TEMPO_ESGOTADO: (
        HTTPStatus.SERVICE_UNAVAILABLE,
        "A operação demorou mais que o esperado. Tente novamente.",
    ),
    CodigoErro.SERVICO_INDISPONIVEL: (
        HTTPStatus.SERVICE_UNAVAILABLE,
        "Serviço indisponível.",
    ),
    CodigoErro.ERRO_INTERNO: (
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "Ocorreu um erro inesperado. Tente novamente.",
    ),
    CodigoErro.NAO_AUTENTICADO: (
        HTTPStatus.UNAUTHORIZED,
        "Sessão inválida ou expirada. Entre novamente.",
    ),
    CodigoErro.CREDENCIAIS_INVALIDAS: (
        HTTPStatus.UNAUTHORIZED,
        "E-mail ou senha inválidos.",
    ),
    CodigoErro.EMAIL_JA_CADASTRADO: (
        HTTPStatus.CONFLICT,
        "Este e-mail já está cadastrado.",
    ),
    CodigoErro.EMAIL_NAO_ENCONTRADO: (
        HTTPStatus.NOT_FOUND,
        "Não foi possível encontrar seu email.",
    ),
    CodigoErro.REENVIO_MUITO_FREQUENTE: (
        HTTPStatus.TOO_MANY_REQUESTS,
        "Aguarde alguns instantes para solicitar um novo código.",
    ),
    CodigoErro.FALHA_ENVIO_EMAIL: (
        HTTPStatus.SERVICE_UNAVAILABLE,
        "Não foi possível enviar o código. Tente novamente.",
    ),
    CodigoErro.CODIGO_INVALIDO: (
        HTTPStatus.BAD_REQUEST,
        (
            "O código de verificação que você inseriu não é válido. "
            "Verifique o código e tente novamente."
        ),
    ),
    CodigoErro.CODIGO_EXPIRADO: (
        HTTPStatus.BAD_REQUEST,
        "O código expirou. Solicite um novo código.",
    ),
    CodigoErro.TENTATIVAS_ESGOTADAS: (
        HTTPStatus.TOO_MANY_REQUESTS,
        "Limite de tentativas atingido. Solicite um novo código.",
    ),
    CodigoErro.CODIGO_JA_VERIFICADO: (
        HTTPStatus.CONFLICT,
        "Este código já foi utilizado. Solicite um novo código.",
    ),
    CodigoErro.TOKEN_REDEFINICAO_INVALIDO: (
        HTTPStatus.BAD_REQUEST,
        (
            "A solicitação de redefinição expirou ou é inválida. "
            "Solicite um novo código."
        ),
    ),
    CodigoErro.IDEMPOTENCIA_CHAVE_AUSENTE: (
        HTTPStatus.BAD_REQUEST,
        "Cabeçalho Idempotency-Key obrigatório.",
    ),
    CodigoErro.IDEMPOTENCIA_CHAVE_INVALIDA: (
        HTTPStatus.BAD_REQUEST,
        "Cabeçalho Idempotency-Key inválido.",
    ),
    CodigoErro.CHAVE_IDEMPOTENCIA_REUTILIZADA: (
        HTTPStatus.UNPROCESSABLE_CONTENT,
        "Esta chave de idempotência já foi usada com outro conteúdo.",
    ),
    CodigoErro.CURSOR_INVALIDO: (
        HTTPStatus.UNPROCESSABLE_CONTENT,
        "Cursor de paginação inválido.",
    ),
    CodigoErro.SOBREPOSICAO_HORARIO: (
        HTTPStatus.CONFLICT,
        "Este horário se sobrepõe a outra atividade.",
    ),
    CodigoErro.ALCANCE_INVALIDO: (
        HTTPStatus.UNPROCESSABLE_CONTENT,
        "Ocorrências concluídas só podem ser alteradas individualmente.",
    ),
    CodigoErro.REPETICAO_EXIGE_ALCANCE_SERIE: (
        HTTPStatus.UNPROCESSABLE_CONTENT,
        "Para alterar a repetição, escolha “Esta e as próximas pendentes”.",
    ),
}


class ErroNegocio(Exception):
    """Erro previsto, convertido em resposta JSON padronizada.

    O status HTTP vem sempre do catálogo.
    """

    def __init__(
        self,
        codigo: CodigoErro,
        mensagem: str | None = None,
        *,
        campos: Sequence[CampoErro] | None = None,
        detalhes: Mapping[str, Any] | None = None,
        cabecalhos: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(codigo.value)
        self.codigo = codigo
        self.mensagem = mensagem or CATALOGO_ERROS[codigo][1]
        self.campos = tuple(campos or ())
        self.detalhes = detalhes
        self.cabecalhos = cabecalhos

    @property
    def status(self) -> int:
        return int(CATALOGO_ERROS[self.codigo][0])


@dataclass(frozen=True, slots=True)
class DadosErro:
    status: int
    codigo: str
    mensagem: str
    campos: tuple[CampoErro, ...] = ()
    detalhes: Mapping[str, Any] | None = None
    cabecalhos: Mapping[str, str] | None = None


def dados_do_catalogo(
    codigo: CodigoErro,
    *,
    cabecalhos: Mapping[str, str] | None = None,
) -> DadosErro:
    status, mensagem = CATALOGO_ERROS[codigo]
    return DadosErro(
        status=int(status),
        codigo=codigo.value,
        mensagem=mensagem,
        cabecalhos=cabecalhos,
    )


def responder_erro(request: Request, dados: DadosErro) -> JSONResponse:
    id_requisicao = getattr(request.state, "id_requisicao", None)
    corpo = RespostaErro(
        codigo=dados.codigo,
        mensagem=dados.mensagem,
        campos=list(dados.campos),
        detalhes=dict(dados.detalhes) if dados.detalhes is not None else None,
        id_requisicao=id_requisicao,
    )
    cabecalhos = dict(dados.cabecalhos or {})
    if id_requisicao is not None:
        cabecalhos[CABECALHO_ID_REQUISICAO] = id_requisicao
    return JSONResponse(
        status_code=dados.status,
        content=corpo.model_dump(mode="json"),
        headers=cabecalhos,
    )


def _caminho_do_campo(loc: Sequence[Any]) -> str:
    partes = [str(p) for p in loc]
    if partes and partes[0] in ORIGENS_DE_CAMPO:
        partes = partes[1:]
    return ".".join(partes) or "corpo"


def _campo_erro(erro: Mapping[str, Any]) -> CampoErro:
    tipo = str(erro.get("type", ""))
    contexto = erro.get("ctx") or {}
    campo = _caminho_do_campo(erro.get("loc", ()))
    if tipo.isupper():
        codigo, mensagem = tipo, str(erro.get("msg", ""))
    elif tipo == "missing":
        codigo, mensagem = "OBRIGATORIO", "Campo obrigatório."
    elif tipo == "string_too_short":
        codigo = "TAMANHO_MINIMO"
        mensagem = (
            f"Informe pelo menos {contexto.get('min_length')} caracteres."
        )
    elif tipo == "string_too_long":
        codigo = "TAMANHO_MAXIMO"
        mensagem = (
            f"Informe no máximo {contexto.get('max_length')} caracteres."
        )
    elif tipo.startswith("date_"):
        codigo, mensagem = "DATA_INVALIDA", "Informe uma data válida"
    elif tipo.startswith("time_"):
        codigo, mensagem = "HORARIO_INVALIDO", "Informe um horário válido"
    elif tipo.startswith("uuid_"):
        codigo, mensagem = "FORMATO_INVALIDO", "Identificador inválido."
    elif tipo in {"enum", "literal_error"}:
        codigo, mensagem = "VALOR_NAO_PERMITIDO", "Valor não permitido."
    else:
        codigo, mensagem = "FORMATO_INVALIDO", "Formato inválido."
    return CampoErro(campo=campo, codigo=codigo, mensagem=mensagem)


def converter_erros_validacao(
    erros: Sequence[Mapping[str, Any]],
) -> tuple[CampoErro, ...]:
    """Converte erros do Pydantic sem ecoar `input` nem `ctx` bruto."""
    return tuple(_campo_erro(e) for e in erros)


def _id_requisicao(request: Request) -> str | None:
    return getattr(request.state, "id_requisicao", None)


def _descrever_erro_banco(exc: DBAPIError) -> str:
    """Resume o erro de banco somente com identificadores.

    A mensagem do driver e o `DETAIL` do PostgreSQL podem conter valores
    de colunas (arquitetura §3.4); por isso não entram no log.
    """
    orig = getattr(exc, "orig", None)
    diag = getattr(orig, "diag", None)
    campos = {
        "sqlstate": getattr(orig, "sqlstate", None),
        "classe": type(orig if orig is not None else exc).__name__,
        "esquema": getattr(diag, "schema_name", None),
        "tabela": getattr(diag, "table_name", None),
        "coluna": getattr(diag, "column_name", None),
        "restricao": getattr(diag, "constraint_name", None),
    }
    return " ".join(f"{nome}={valor or '-'}" for nome, valor in campos.items())


def _dados_de_banco(exc: DBAPIError) -> DadosErro:
    sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)
    if sqlstate in SQLSTATES_CONFLITO:
        return dados_do_catalogo(
            CodigoErro.CONFLITO_CONCORRENCIA,
            cabecalhos={"Retry-After": "1"},
        )
    if sqlstate == SQLSTATE_TEMPO_ESGOTADO:
        return dados_do_catalogo(CodigoErro.TEMPO_ESGOTADO)
    return dados_do_catalogo(CodigoErro.ERRO_INTERNO)


def registrar_tratadores_erro(app: FastAPI) -> None:
    @app.exception_handler(ErroNegocio)
    async def tratar_erro_negocio(
        request: Request, exc: ErroNegocio
    ) -> JSONResponse:
        return responder_erro(
            request,
            DadosErro(
                status=exc.status,
                codigo=exc.codigo.value,
                mensagem=exc.mensagem,
                campos=exc.campos,
                detalhes=exc.detalhes,
                cabecalhos=exc.cabecalhos,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        erros = exc.errors()
        if any(e.get("type") == "json_invalid" for e in erros):
            return responder_erro(
                request, dados_do_catalogo(CodigoErro.CORPO_INVALIDO)
            )
        dados = dados_do_catalogo(CodigoErro.VALIDACAO)
        return responder_erro(
            request,
            DadosErro(
                status=dados.status,
                codigo=dados.codigo,
                mensagem=dados.mensagem,
                campos=converter_erros_validacao(erros),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def tratar_http(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if exc.status_code == HTTPStatus.NOT_FOUND:
            dados = dados_do_catalogo(CodigoErro.RECURSO_NAO_ENCONTRADO)
        elif exc.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            dados = dados_do_catalogo(
                CodigoErro.METODO_NAO_PERMITIDO,
                cabecalhos=exc.headers,
            )
        else:
            base = dados_do_catalogo(
                CodigoErro.ERRO_HTTP, cabecalhos=exc.headers
            )
            dados = DadosErro(
                status=exc.status_code,
                codigo=base.codigo,
                mensagem=base.mensagem,
                cabecalhos=base.cabecalhos,
            )
        return responder_erro(request, dados)

    @app.exception_handler(DBAPIError)
    async def tratar_banco(request: Request, exc: DBAPIError) -> JSONResponse:
        dados = _dados_de_banco(exc)
        extra = {"id_requisicao": _id_requisicao(request) or "-"}
        if dados.status == HTTPStatus.INTERNAL_SERVER_ERROR:
            # Sem exc_info: o traceback encadeado traria o DETAIL do driver.
            logger.error(
                "erro de banco de dados: %s\n%s",
                _descrever_erro_banco(exc),
                "".join(traceback.format_tb(exc.__traceback__)).rstrip(),
                extra=extra,
            )
        else:
            logger.warning(
                "erro de banco de dados: %s", dados.codigo, extra=extra
            )
        return responder_erro(request, dados)

    @app.exception_handler(Exception)
    async def tratar_inesperado(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "erro inesperado",
            extra={"id_requisicao": _id_requisicao(request) or "-"},
        )
        return responder_erro(
            request, dados_do_catalogo(CodigoErro.ERRO_INTERNO)
        )
