"""Enumerações persistidas como texto validado (DEC-MV-07)."""

import enum

from sqlalchemy import Enum


class Prioridade(enum.StrEnum):
    """Prioridade de atividade."""

    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class PeriodicidadeAtividade(enum.StrEnum):
    """Repetição de atividades."""

    NENHUMA = "NENHUMA"
    DIARIA = "DIARIA"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"


class PeriodicidadeImportancia(enum.StrEnum):
    """Repetição de importâncias (admite ANUAL)."""

    NENHUMA = "NENHUMA"
    DIARIA = "DIARIA"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"
    ANUAL = "ANUAL"


class TipoMovimentacao(enum.StrEnum):
    """Tipo de lançamento financeiro e de categoria financeira."""

    RECEITA = "RECEITA"
    DESPESA = "DESPESA"


class FormaMovimentacao(enum.StrEnum):
    """Forma descritiva de recebimento ou pagamento."""

    PIX = "PIX"
    DINHEIRO = "DINHEIRO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    DEPOSITO = "DEPOSITO"
    BOLETO = "BOLETO"
    OUTROS = "OUTROS"


class SituacaoLembrete(enum.StrEnum):
    """Situação da versão corrente de um lembrete."""

    PENDENTE = "PENDENTE"
    ENVIADO = "ENVIADO"
    CANCELADO = "CANCELADO"


class SituacaoRequisicao(enum.StrEnum):
    """Situação de uma requisição idempotente."""

    EM_PROCESSAMENTO = "EM_PROCESSAMENTO"
    CONCLUIDA = "CONCLUIDA"


def _valores(classe: type[enum.Enum]) -> list[str]:
    """Valores persistidos: iguais aos nomes dos membros."""
    return [str(membro.value) for membro in classe]


def tipo_enum(classe: type[enum.StrEnum], nome: str, comprimento: int) -> Enum:
    """Tipo textual com CHECK `ck_<tabela>_<nome>`; `nome` é a coluna."""
    return Enum(
        classe,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        length=comprimento,
        values_callable=_valores,
        name=nome,
    )
