"""Schemas de importâncias (arquitetura §9.5)."""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    model_validator,
)
from pydantic_core import PydanticCustomError

from api_gestao_pessoal.models.enums import SituacaoLembrete
from api_gestao_pessoal.schemas.atividade import (
    CategoriaId,
    CategoriaRef,
    Descricao,
    HorarioSaida,
    TerminoRepeticao,
)
from api_gestao_pessoal.schemas.comum import (
    AlcanceSerie,
    DataCivil,
    DinheiroSaida,
    Horario,
    Pagina,
    conversor_valor,
)

MENSAGEM_NOME = "Informe o nome da importância"
MENSAGEM_DATA_FINAL_OBRIGATORIA = "Informe a data final da repetição"


class PeriodicidadeImportanciaApi(enum.StrEnum):
    """Repetição de importâncias (admite ANUAL)."""

    NAO_REPETIR = "NAO_REPETIR"
    DIARIA = "DIARIA"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"
    ANUAL = "ANUAL"


class FiltroImportancia(enum.StrEnum):
    """Filtros da lista de importâncias (7.1.2)."""

    TODOS = "TODOS"
    VENCENDO_HOJE = "VENCENDO_HOJE"
    ESTE_MES = "ESTE_MES"
    PROXIMOS = "PROXIMOS"
    CONCLUIDOS = "CONCLUIDOS"
    ATRASADOS = "ATRASADOS"


class GrupoImportancia(enum.StrEnum):
    """Grupos da lista (7.1.5)."""

    ATRASADAS = "ATRASADAS"
    HOJE = "HOJE"
    PROXIMAS = "PROXIMAS"
    CONCLUIDAS = "CONCLUIDAS"


class SituacaoImportancia(enum.StrEnum):
    """Situação derivada de uma importância."""

    PENDENTE = "PENDENTE"
    CONCLUIDA = "CONCLUIDA"


class Prazo(enum.StrEnum):
    """Prazo de uma importância pendente (7.1.4)."""

    HOJE = "HOJE"
    AMANHA = "AMANHA"
    EM_DIAS = "EM_DIAS"
    ATRASADA = "ATRASADA"


def _nome(valor: object) -> str:
    nome = valor.strip() if isinstance(valor, str) else ""
    if not nome:
        raise PydanticCustomError("NOME_OBRIGATORIO", MENSAGEM_NOME)
    if len(nome) < 3:  # noqa: PLR2004
        raise PydanticCustomError(
            "TAMANHO_MINIMO", "Informe pelo menos 3 caracteres."
        )
    if len(nome) > 100:  # noqa: PLR2004
        raise PydanticCustomError(
            "TAMANHO_MAXIMO", "Informe no máximo 100 caracteres."
        )
    return nome


def _nao_nulo(valor: object) -> object:
    if valor is None:
        raise PydanticCustomError("OBRIGATORIO", "Campo obrigatório.")
    return valor


def _valor_previsto(valor: object) -> Decimal | None:
    if valor is None:
        return None
    return conversor_valor(
        "VALOR_PREVISTO_OBRIGATORIO",
        "Informe um valor previsto maior que zero",
    )(valor)


NomeImportancia = Annotated[str, BeforeValidator(_nome)]
ValorPrevisto = Annotated[Decimal | None, BeforeValidator(_valor_previsto)]


class LembreteEntrada(BaseModel):
    """Lembrete no app: antecedência e horário (obrigatório, 8.3.4)."""

    antecedencia_dias: Literal[0, 1, 3, 7]
    horario: Horario


class RepeticaoImportanciaEntrada(BaseModel):
    """Regra de repetição de importâncias."""

    periodicidade: PeriodicidadeImportanciaApi = (
        PeriodicidadeImportanciaApi.NAO_REPETIR
    )
    momento_conclusao: datetime | None = None
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


class ImportanciaCriacao(BaseModel):
    """Corpo do cadastro de importância (tela 8)."""

    nome: NomeImportancia = Field(default=None, validate_default=True)
    categoria_id: CategoriaId = Field(default=None, validate_default=True)
    data_compromisso: DataCivil = Field(default=None, validate_default=True)
    horario: Horario | None = None
    descricao: Descricao = None
    possui_despesa: bool = False
    valor_previsto: ValorPrevisto = None
    repeticao: RepeticaoImportanciaEntrada = Field(
        default_factory=RepeticaoImportanciaEntrada
    )
    lembrete: LembreteEntrada | None = None


class ImportanciaEdicao(BaseModel):
    """Corpo do PATCH: campo ausente = sem alteração."""

    nome: Annotated[NomeImportancia | None, BeforeValidator(_nao_nulo)] = None
    categoria_id: Annotated[CategoriaId | None, BeforeValidator(_nao_nulo)] = (
        None
    )
    data_compromisso: Annotated[
        DataCivil | None, BeforeValidator(_nao_nulo)
    ] = None
    horario: Horario | None = None
    descricao: Descricao = None
    possui_despesa: Annotated[bool | None, BeforeValidator(_nao_nulo)] = None
    valor_previsto: ValorPrevisto = None
    repeticao: Annotated[
        RepeticaoImportanciaEntrada | None, BeforeValidator(_nao_nulo)
    ] = None
    lembrete: LembreteEntrada | None = None
    alcance: Annotated[AlcanceSerie, BeforeValidator(_nao_nulo)] = (
        AlcanceSerie.SOMENTE_ESTA
    )


class SituacaoImportanciaEntrada(BaseModel):
    """Corpo do `PUT …/situacao` (estado alvo)."""

    situacao: SituacaoImportancia


class PagamentoVinculado(BaseModel):
    """Despesa que quitou a importância."""

    movimentacao_id: uuid.UUID
    valor: DinheiroSaida
    data_movimentacao: date


class ImportanciaItem(BaseModel):
    """Item da lista de importâncias."""

    id: uuid.UUID
    nome: str
    descricao: str | None
    categoria: CategoriaRef
    data_compromisso: date
    horario: HorarioSaida | None
    possui_despesa: bool
    valor_previsto: DinheiroSaida | None
    pagamento: PagamentoVinculado | None
    situacao: SituacaoImportancia
    pago: bool
    atrasada: bool
    dias_ate_vencimento: int | None
    prazo: Prazo | None
    recorrente: bool
    serie_id: uuid.UUID | None = None
    grupo: GrupoImportancia
    periodicidade: PeriodicidadeImportanciaApi = (
        PeriodicidadeImportanciaApi.NAO_REPETIR
    )
    momento_conclusao: datetime | None = None


class LembreteResposta(BaseModel):
    """Lembrete da importância e sua situação."""

    antecedencia_dias: int
    horario: HorarioSaida
    situacao: SituacaoLembrete
    agendado_para: datetime


class SerieImportanciaResposta(BaseModel):
    """Regra da série a que a ocorrência pertence."""

    id: uuid.UUID
    periodicidade: PeriodicidadeImportanciaApi
    termino: TerminoRepeticao
    data_final: date | None
    numero_final: int | None


class CategoriaFinanceiraSugerida(BaseModel):
    """Categoria de despesa sugerida para registrar o pagamento."""

    id: uuid.UUID
    nome: str


class ImportanciaDetalhe(ImportanciaItem):
    """Detalhes completos de uma importância."""

    lembrete: LembreteResposta | None
    serie: SerieImportanciaResposta | None
    numero_ocorrencia: int | None
    categoria_financeira_sugerida: CategoriaFinanceiraSugerida | None
    criado_em: datetime
    atualizado_em: datetime


class Grupos(BaseModel):
    """Quantidade de importâncias por grupo (consulta completa)."""

    atrasadas: int
    hoje: int
    proximas: int
    concluidas: int


class ConsultaImportanciasResposta(Pagina[ImportanciaItem]):
    """Lista de importâncias com grupos e paginação."""

    filtro: FiltroImportancia
    mes: str | None
    rotulo_periodo: str | None
    horizonte_proximas: date | None
    possui_importancias: bool
    grupos: Grupos
    total: int


class PagamentoDisponivel(BaseModel):
    """Importância elegível para receber um pagamento (11.2.4)."""

    id: uuid.UUID
    nome: str
    data_compromisso: date
    valor_previsto: DinheiroSaida


class VincularPagamentoEntrada(BaseModel):
    """Corpo do `PUT …/pagamento`."""

    movimentacao_id: uuid.UUID
