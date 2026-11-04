"""Schemas do financeiro (arquitetura §9.4)."""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field
from pydantic_core import PydanticCustomError

from api_gestao_pessoal.models.enums import FormaMovimentacao, TipoMovimentacao
from api_gestao_pessoal.schemas.atividade import (
    CategoriaId,
    CategoriaRef,
    Descricao,
)
from api_gestao_pessoal.schemas.comum import (
    DataCivil,
    DinheiroSaida,
    Pagina,
    conversor_valor,
)

TAMANHO_MAXIMO_CONTRAPARTE = 100


class FiltroTipo(enum.StrEnum):
    """Filtro de tipo da consulta de movimentações."""

    TODAS = "TODAS"
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"


class FormaReceita(enum.StrEnum):
    """Formas de recebimento (10.2.3)."""

    PIX = "PIX"
    DINHEIRO = "DINHEIRO"
    TRANSFERENCIA = "TRANSFERENCIA"
    DEPOSITO = "DEPOSITO"
    OUTROS = "OUTROS"


class FormaDespesa(enum.StrEnum):
    """Formas de pagamento (11.2.3)."""

    PIX = "PIX"
    DINHEIRO = "DINHEIRO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    BOLETO = "BOLETO"
    OUTROS = "OUTROS"


class Tendencia(enum.StrEnum):
    """Resultado da comparação entre períodos (9.2.7 e 9.2.8)."""

    AUMENTO = "AUMENTO"
    REDUCAO = "REDUCAO"
    ESTABILIDADE = "ESTABILIDADE"
    SEM_BASE = "SEM_BASE"
    SEM_MOVIMENTACAO = "SEM_MOVIMENTACAO"
    NAO_APLICAVEL = "NAO_APLICAVEL"


def _nome_receita(valor: object) -> str:
    nome = valor.strip() if isinstance(valor, str) else ""
    if not nome:
        raise PydanticCustomError(
            "NOME_OBRIGATORIO", "Informe o nome da receita"
        )
    return _tamanho_do_nome(nome)


def _nome_despesa(valor: object) -> str:
    nome = valor.strip() if isinstance(valor, str) else ""
    if not nome:
        raise PydanticCustomError(
            "NOME_OBRIGATORIO", "Informe o nome da despesa"
        )
    return _tamanho_do_nome(nome)


def _tamanho_do_nome(nome: str) -> str:
    if len(nome) < 3:  # noqa: PLR2004
        raise PydanticCustomError(
            "TAMANHO_MINIMO", "Informe pelo menos 3 caracteres."
        )
    if len(nome) > 100:  # noqa: PLR2004
        raise PydanticCustomError(
            "TAMANHO_MAXIMO", "Informe no máximo 100 caracteres."
        )
    return nome


def _contraparte(valor: object) -> str | None:
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise PydanticCustomError("FORMATO_INVALIDO", "Formato inválido.")
    texto = valor.strip()
    if len(texto) > TAMANHO_MAXIMO_CONTRAPARTE:
        raise PydanticCustomError(
            "TAMANHO_MAXIMO", "Informe no máximo 100 caracteres."
        )
    return texto or None


def _nao_nulo(valor: object) -> object:
    if valor is None:
        raise PydanticCustomError("OBRIGATORIO", "Campo obrigatório.")
    return valor


Contraparte = Annotated[str | None, BeforeValidator(_contraparte)]
ValorRecebido = Annotated[
    Decimal,
    BeforeValidator(
        conversor_valor(
            "VALOR_OBRIGATORIO", "Informe um valor recebido maior que zero"
        )
    ),
]
ValorPago = Annotated[
    Decimal,
    BeforeValidator(
        conversor_valor(
            "VALOR_OBRIGATORIO", "Informe um valor pago maior que zero"
        )
    ),
]
ValorGenerico = Annotated[
    Decimal,
    BeforeValidator(
        conversor_valor("VALOR_OBRIGATORIO", "Informe um valor maior que zero")
    ),
]


class ReceitaCriacao(BaseModel):
    """Corpo do cadastro de receita (tela 10)."""

    nome: Annotated[str, BeforeValidator(_nome_receita)] = Field(
        default=None, validate_default=True
    )
    valor: ValorRecebido = Field(default=None, validate_default=True)
    categoria_id: CategoriaId = Field(default=None, validate_default=True)
    data_movimentacao: DataCivil = Field(default=None, validate_default=True)
    descricao: Descricao = None
    contraparte: Contraparte = None
    forma: FormaReceita | None = None


class DespesaCriacao(BaseModel):
    """Corpo do cadastro de despesa (tela 11)."""

    nome: Annotated[str, BeforeValidator(_nome_despesa)] = Field(
        default=None, validate_default=True
    )
    valor: ValorPago = Field(default=None, validate_default=True)
    categoria_id: CategoriaId = Field(default=None, validate_default=True)
    data_movimentacao: DataCivil = Field(default=None, validate_default=True)
    descricao: Descricao = None
    contraparte: Contraparte = None
    forma: FormaDespesa | None = None
    importancia_id: uuid.UUID | None = None


def _nome_generico(valor: object) -> str:
    nome = valor.strip() if isinstance(valor, str) else ""
    if not nome:
        raise PydanticCustomError("NOME_OBRIGATORIO", "Informe o nome")
    return _tamanho_do_nome(nome)


class MovimentacaoEdicao(BaseModel):
    """Corpo do PATCH: campo ausente = sem alteração; `tipo` é imutável."""

    nome: Annotated[
        str | None,
        BeforeValidator(_nao_nulo),
        BeforeValidator(_nome_generico),
    ] = None
    valor: Annotated[ValorGenerico | None, BeforeValidator(_nao_nulo)] = None
    categoria_id: Annotated[CategoriaId | None, BeforeValidator(_nao_nulo)] = (
        None
    )
    data_movimentacao: Annotated[
        DataCivil | None, BeforeValidator(_nao_nulo)
    ] = None
    descricao: Descricao = None
    contraparte: Contraparte = None
    forma: FormaMovimentacao | None = None
    importancia_id: uuid.UUID | None = None
    confirmar_alteracao_vinculo: Annotated[
        bool, BeforeValidator(_nao_nulo)
    ] = False


class ImportanciaVinculadaItem(BaseModel):
    """Importância quitada pela despesa (nas listas)."""

    id: uuid.UUID
    nome: str
    disponivel: bool


class ImportanciaVinculadaDetalhe(ImportanciaVinculadaItem):
    """Importância quitada pela despesa (no detalhe)."""

    data_compromisso: date
    valor_previsto: DinheiroSaida | None


class MovimentacaoBase(BaseModel):
    """Campos comuns de item e detalhe de movimentação."""

    id: uuid.UUID
    tipo: TipoMovimentacao
    nome: str
    valor: DinheiroSaida
    categoria: CategoriaRef
    data_movimentacao: date


class MovimentacaoItem(MovimentacaoBase):
    """Item de lista de movimentações."""

    importancia: ImportanciaVinculadaItem | None


class MovimentacaoDetalhe(MovimentacaoBase):
    """Detalhes de uma movimentação."""

    importancia: ImportanciaVinculadaDetalhe | None
    descricao: str | None
    contraparte: str | None
    forma: FormaMovimentacao | None
    criado_em: datetime
    atualizado_em: datetime


class ConsultaMovimentacoesResposta(Pagina[MovimentacaoItem]):
    """Consulta de movimentações do mês."""

    mes: str
    filtros_ativos: bool
    possui_movimentacoes_mes: bool


class Intervalo(BaseModel):
    """Intervalo de datas (inclusivo)."""

    inicio: date
    fim: date


class Comparacao(BaseModel):
    """Comparação de um total com o período anterior (9.2.6 a 9.2.8)."""

    intervalo_atual: Intervalo | None
    intervalo_anterior: Intervalo | None
    total_atual: DinheiroSaida
    total_anterior: DinheiroSaida
    variacao_percentual: str | None
    tendencia: Tendencia


class ComparacoesResposta(BaseModel):
    """Comparações de receitas e despesas."""

    receitas: Comparacao
    despesas: Comparacao


class DiaGrafico(BaseModel):
    """Totais de um dia do mês (zeros incluídos)."""

    data: date
    receitas: DinheiroSaida
    despesas: DinheiroSaida


class CategoriaDespesaTotal(BaseModel):
    """Total de despesas de uma categoria no mês."""

    categoria: CategoriaRef
    total: DinheiroSaida


class ResumoFinanceiroResposta(BaseModel):
    """Resumo mensal: totais, comparação, gráfico e categorias."""

    mes: str
    periodo: Intervalo
    receitas: DinheiroSaida
    despesas: DinheiroSaida
    saldo: DinheiroSaida
    comparacao: ComparacoesResposta
    grafico_diario: list[DiaGrafico]
    categorias_despesa: list[CategoriaDespesaTotal]
    ultimas_movimentacoes: list[MovimentacaoItem]


class DespesaDisponivel(BaseModel):
    """Despesa sem vínculo, elegível para quitar uma importância."""

    id: uuid.UUID
    nome: str
    data_movimentacao: date
    valor: DinheiroSaida
