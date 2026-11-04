"""Schemas de atividades (arquitetura §9.3)."""

import enum
import uuid
from datetime import date, datetime, time
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from api_gestao_pessoal.models.enums import Prioridade
from api_gestao_pessoal.schemas.comum import (
    AlcanceSerie,
    DataCivil,
    Horario,
    Pagina,
    formatar_horario,
)

TAMANHO_MINIMO_NOME = 3
TAMANHO_MAXIMO_NOME = 100
TAMANHO_MAXIMO_DESCRICAO = 200
TAMANHO_MAXIMO_BUSCA = 100

MENSAGEM_NOME_OBRIGATORIO = "Informe o nome da atividade"
MENSAGEM_CATEGORIA_OBRIGATORIA = "Selecione uma categoria"
MENSAGEM_HORARIO_FINAL = (
    "O horário final deve ser posterior ao horário inicial"
)
MENSAGEM_DATA_FINAL_OBRIGATORIA = "Informe a data final da repetição"


class PeriodicidadeRepeticao(enum.StrEnum):
    """Repetição de atividades na API (`NAO_REPETIR` = sem série)."""

    NAO_REPETIR = "NAO_REPETIR"
    DIARIA = "DIARIA"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"


class TerminoRepeticao(enum.StrEnum):
    """Término de uma repetição."""

    SEM_DATA_FINAL = "SEM_DATA_FINAL"
    ATE_DATA = "ATE_DATA"


class SituacaoAtividade(enum.StrEnum):
    """Situação derivada de uma atividade."""

    PENDENTE = "PENDENTE"
    CONCLUIDA = "CONCLUIDA"


class FiltroSituacao(enum.StrEnum):
    """Filtro de situação da consulta."""

    TODAS = "TODAS"
    PENDENTE = "PENDENTE"
    CONCLUIDA = "CONCLUIDA"


class FiltroPrioridade(enum.StrEnum):
    """Filtro de prioridade da consulta."""

    TODAS = "TODAS"
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class OrdenacaoAtividades(enum.StrEnum):
    """Ordenações da consulta (padrão: `HORARIO`)."""

    HORARIO = "HORARIO"
    PRIORIDADE = "PRIORIDADE"
    RECENTES = "RECENTES"


HorarioSaida = Annotated[
    time, PlainSerializer(formatar_horario, return_type=str)
]


def _nome(valor: object) -> str:
    nome = valor.strip() if isinstance(valor, str) else ""
    if not nome:
        raise PydanticCustomError(
            "NOME_OBRIGATORIO", MENSAGEM_NOME_OBRIGATORIO
        )
    if len(nome) < TAMANHO_MINIMO_NOME:
        raise PydanticCustomError(
            "TAMANHO_MINIMO",
            "Informe pelo menos 3 caracteres.",
        )
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise PydanticCustomError(
            "TAMANHO_MAXIMO",
            "Informe no máximo 100 caracteres.",
        )
    return nome


def _categoria(valor: object) -> uuid.UUID:
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise PydanticCustomError(
            "CATEGORIA_OBRIGATORIA", MENSAGEM_CATEGORIA_OBRIGATORIA
        )
    if isinstance(valor, uuid.UUID):
        return valor
    try:
        return uuid.UUID(str(valor))
    except ValueError:
        raise PydanticCustomError(
            "FORMATO_INVALIDO", "Identificador inválido."
        ) from None


def _descricao(valor: object) -> str | None:
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise PydanticCustomError("FORMATO_INVALIDO", "Formato inválido.")
    texto = valor.strip()
    if len(texto) > TAMANHO_MAXIMO_DESCRICAO:
        raise PydanticCustomError(
            "TAMANHO_MAXIMO",
            "Informe no máximo 200 caracteres.",
        )
    return texto or None


NomeAtividade = Annotated[str, BeforeValidator(_nome)]
CategoriaId = Annotated[uuid.UUID, BeforeValidator(_categoria)]
Descricao = Annotated[str | None, BeforeValidator(_descricao)]


class RepeticaoEntrada(BaseModel):
    """Regra de repetição enviada no cadastro ou na edição."""

    model_config = ConfigDict(extra="ignore")

    periodicidade: PeriodicidadeRepeticao = PeriodicidadeRepeticao.NAO_REPETIR
    termino: TerminoRepeticao = TerminoRepeticao.SEM_DATA_FINAL
    data_final: DataCivil | None = None

    @model_validator(mode="after")
    def _exige_data_final(self) -> Self:
        if (
            self.termino == TerminoRepeticao.ATE_DATA
            and self.data_final is None
        ):
            raise PydanticCustomError(
                "DATA_FINAL_OBRIGATORIA", MENSAGEM_DATA_FINAL_OBRIGATORIA
            )
        return self


class AtividadeCriacao(BaseModel):
    """Corpo do cadastro de atividade (tela 6)."""

    nome: NomeAtividade = Field(default=None, validate_default=True)
    categoria_id: CategoriaId = Field(default=None, validate_default=True)
    prioridade: Prioridade = Prioridade.BAIXA
    data: DataCivil = Field(default=None, validate_default=True)
    horario_inicial: Horario = Field(default=None, validate_default=True)
    horario_final: Horario = Field(default=None, validate_default=True)
    descricao: Descricao = None
    repeticao: RepeticaoEntrada = Field(default_factory=RepeticaoEntrada)
    confirmar_sobreposicao: bool = False

    @field_validator("horario_final", mode="after")
    @classmethod
    def _final_posterior(cls, valor: time, info: ValidationInfo) -> time:
        inicial = info.data.get("horario_inicial")
        if inicial is not None and valor <= inicial:
            raise PydanticCustomError(
                "HORARIO_FINAL_INVALIDO", MENSAGEM_HORARIO_FINAL
            )
        return valor


def _nao_nulo(valor: object) -> object:
    if valor is None:
        raise PydanticCustomError("OBRIGATORIO", "Campo obrigatório.")
    return valor


class AtividadeEdicao(BaseModel):
    """Corpo do PATCH: campo ausente = sem alteração."""

    nome: Annotated[NomeAtividade | None, BeforeValidator(_nao_nulo)] = None
    categoria_id: Annotated[CategoriaId | None, BeforeValidator(_nao_nulo)] = (
        None
    )
    prioridade: Annotated[Prioridade | None, BeforeValidator(_nao_nulo)] = None
    data: Annotated[DataCivil | None, BeforeValidator(_nao_nulo)] = None
    horario_inicial: Annotated[Horario | None, BeforeValidator(_nao_nulo)] = (
        None
    )
    horario_final: Annotated[Horario | None, BeforeValidator(_nao_nulo)] = None
    descricao: Descricao = None
    repeticao: Annotated[
        RepeticaoEntrada | None, BeforeValidator(_nao_nulo)
    ] = None
    alcance: Annotated[AlcanceSerie, BeforeValidator(_nao_nulo)] = (
        AlcanceSerie.SOMENTE_ESTA
    )
    confirmar_sobreposicao: Annotated[bool, BeforeValidator(_nao_nulo)] = False

    @field_validator("horario_final", mode="after")
    @classmethod
    def _final_posterior(
        cls, valor: time | None, info: ValidationInfo
    ) -> time | None:
        inicial = info.data.get("horario_inicial")
        if valor is not None and inicial is not None and valor <= inicial:
            raise PydanticCustomError(
                "HORARIO_FINAL_INVALIDO", MENSAGEM_HORARIO_FINAL
            )
        return valor


class SituacaoEntrada(BaseModel):
    """Corpo do `PUT …/situacao` (estado alvo)."""

    situacao: SituacaoAtividade


class CategoriaRef(BaseModel):
    """Categoria exibida nos itens (inclusive se inativa)."""

    id: uuid.UUID
    nome: str


class AtividadeItem(BaseModel):
    """Item da lista de atividades."""

    id: uuid.UUID
    nome: str
    categoria: CategoriaRef
    descricao_previa: str | None
    data: date
    horario_inicial: HorarioSaida
    horario_final: HorarioSaida
    duracao_minutos: int
    prioridade: Prioridade
    situacao: SituacaoAtividade
    concluida_em: datetime | None
    recorrente: bool
    periodicidade: PeriodicidadeRepeticao = PeriodicidadeRepeticao.NAO_REPETIR


class SerieResposta(BaseModel):
    """Regra da série a que a ocorrência pertence."""

    id: uuid.UUID
    periodicidade: PeriodicidadeRepeticao
    termino: TerminoRepeticao
    data_final: date | None
    numero_final: int | None


class AtividadeDetalhe(AtividadeItem):
    """Detalhes completos de uma atividade."""

    descricao: str | None
    serie: SerieResposta | None
    numero_ocorrencia: int | None
    criado_em: datetime
    atualizado_em: datetime


class Indicadores(BaseModel):
    """Indicadores da consulta (mesmo universo dos filtros)."""

    total: int
    concluidas: int
    pendentes: int
    tempo_total_minutos: int


class ConsultaAtividadesResposta(Pagina[AtividadeItem]):
    """Consulta do dia com indicadores e paginação."""

    data: date
    eh_hoje: bool
    filtros_ativos: bool
    total_data: int
    indicadores: Indicadores


class PendenciasAnterioresResposta(BaseModel):
    """Aviso de pendências de dias anteriores (5.1.9)."""

    quantidade: int
    data_mais_antiga: date | None


class ConflitoHorario(BaseModel):
    """Atividade que se sobrepõe ao horário informado."""

    id: uuid.UUID
    nome: str
    horario_inicial: HorarioSaida
    horario_final: HorarioSaida
