"""Vínculo interno entre despesas e importâncias (arquitetura §8.7, F8).

"Pagamento" é só a informação registrada pelo usuário: a importância passa
a ter uma despesa vinculada. Nenhuma operação financeira é executada. O
valor previsto nunca entra nos totais; a despesa vinculada conta uma única
vez, pelas regras do financeiro.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import Importancia
from api_gestao_pessoal.models import MovimentacaoFinanceira as Mov
from api_gestao_pessoal.models.enums import TipoMovimentacao
from api_gestao_pessoal.schemas.comum import Pagina
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.schemas.financeiro import (
    DespesaCriacao,
    DespesaDisponivel,
    MovimentacaoDetalhe,
    MovimentacaoEdicao,
)
from api_gestao_pessoal.schemas.importancia import (
    ImportanciaDetalhe,
    PagamentoDisponivel,
)
from api_gestao_pessoal.services import financeiro, importancias, lembretes
from api_gestao_pessoal.services.autorizacao import obter_do_usuario_ou_404
from api_gestao_pessoal.services.consulta_movimentacoes import obter_detalhe
from api_gestao_pessoal.services.paginacao import (
    codificar_cursor,
    decodificar_cursor,
    escapar_busca,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import ContextoUsuario

ORDEM_PAGAMENTOS = "VENCIMENTO"
ORDEM_DESPESAS = "DATA_DESC"


def _erro_campo(campo: str, codigo: str, mensagem: str) -> ErroNegocio:
    return ErroNegocio(
        CodigoErro.VALIDACAO,
        campos=[CampoErro(campo=campo, codigo=codigo, mensagem=mensagem)],
    )


async def _importancia_elegivel(
    sessao: AsyncSession, contexto: ContextoUsuario, importancia_id: uuid.UUID
) -> Importancia:
    """Do usuário, não excluída, com despesa e sem pagamento (§8.7)."""
    imp = await obter_do_usuario_ou_404(
        sessao, Importancia, importancia_id, contexto.usuario_id
    )
    if not imp.possui_despesa:
        raise ErroNegocio(CodigoErro.IMPORTANCIA_SEM_DESPESA)
    vinculada = await sessao.scalar(
        select(Mov.id).where(Mov.importancia_id == imp.id)
    )
    if vinculada is not None:
        raise ErroNegocio(
            CodigoErro.IMPORTANCIA_JA_PAGA,
            detalhes={"movimentacao_id": str(vinculada)},
        )
    return imp


async def _vincular(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    mov: Mov,
    importancia: Importancia,
) -> None:
    mov.importancia_id = importancia.id
    mov.importancia_vinculada_em = contexto.agora
    await sessao.flush()
    await lembretes.cancelar_pendente(sessao, importancia.id)


async def registrar_pagamento(
    sessao: AsyncSession, contexto: ContextoUsuario, dados: DespesaCriacao
) -> MovimentacaoDetalhe:
    """Despesa nova já vinculada à importância (dentro de idempotência)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    if dados.importancia_id is None:
        msg = "registrar_pagamento exige importancia_id"
        raise ValueError(msg)
    imp = await _importancia_elegivel(sessao, contexto, dados.importancia_id)
    mov = await financeiro.inserir(
        sessao,
        contexto,
        TipoMovimentacao.DESPESA,
        dados,
        importancia_id=imp.id,
    )
    await lembretes.cancelar_pendente(sessao, imp.id)
    detalhe = await obter_detalhe(sessao, contexto.usuario_id, mov.id)
    if detalhe is None:
        raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
    return detalhe


async def vincular_despesa_existente(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    importancia_id: uuid.UUID,
    movimentacao_id: uuid.UUID,
) -> ImportanciaDetalhe:
    """`PUT /importancias/{id}/pagamento`: só muda o vínculo e a situação."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    imp = await obter_do_usuario_ou_404(
        sessao, Importancia, importancia_id, contexto.usuario_id
    )
    mov = await obter_do_usuario_ou_404(
        sessao, Mov, movimentacao_id, contexto.usuario_id
    )
    if mov.tipo != TipoMovimentacao.DESPESA:
        raise _erro_campo(
            "movimentacao_id",
            "MOVIMENTACAO_NAO_E_DESPESA",
            "Selecione uma despesa",
        )
    if mov.importancia_id == imp.id:
        return await importancias.detalhe(sessao, contexto, imp.id)
    if mov.importancia_id is not None:
        raise ErroNegocio(CodigoErro.DESPESA_JA_VINCULADA)
    elegivel = await _importancia_elegivel(sessao, contexto, imp.id)
    await _vincular(sessao, contexto, mov, elegivel)
    return await importancias.detalhe(sessao, contexto, imp.id)


async def alterar_vinculo_despesa(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    movimentacao_id: uuid.UUID,
    dados: MovimentacaoEdicao,
) -> MovimentacaoDetalhe:
    """`PATCH` com `importancia_id`: trocar, remover ou criar o vínculo.

    Os demais campos do mesmo PATCH seguem as regras do financeiro. Tudo
    ocorre numa única transação (§8.7, atomicidade).
    """
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    mov = await obter_do_usuario_ou_404(
        sessao, Mov, movimentacao_id, contexto.usuario_id
    )
    if mov.tipo != TipoMovimentacao.DESPESA:
        raise _erro_campo(
            "importancia_id",
            "SOMENTE_DESPESA",
            "Somente despesas podem ser vinculadas a importâncias",
        )
    await financeiro.aplicar_edicao(sessao, contexto, mov, dados)
    novo = dados.importancia_id
    atual = mov.importancia_id
    if novo != atual:
        if atual is not None and not dados.confirmar_alteracao_vinculo:
            raise ErroNegocio(CodigoErro.CONFIRMACAO_VINCULO_NECESSARIA)
        if atual is not None:
            mov.importancia_id = None
            mov.importancia_vinculada_em = None
            await sessao.flush()
            await lembretes.ao_reabrir_importancia(
                sessao, atual, contexto.agora
            )
        if novo is not None:
            imp = await _importancia_elegivel(sessao, contexto, novo)
            await _vincular(sessao, contexto, mov, imp)
    detalhe = await obter_detalhe(sessao, contexto.usuario_id, mov.id)
    if detalhe is None:
        raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
    return detalhe


# ------------------------------------------------------------------ consultas


async def importancias_disponiveis(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    *,
    busca: str,
    limite: int,
    cursor: str | None,
) -> Pagina[PagamentoDisponivel]:
    """Importâncias elegíveis, por vencimento (11.2.4)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    filtros = {"busca": busca.strip().lower()}
    chaves = (
        decodificar_cursor(cursor, ORDEM_PAGAMENTOS, filtros)
        if cursor is not None
        else None
    )
    consulta = (
        select(Importancia)
        .outerjoin(Mov, Mov.importancia_id == Importancia.id)
        .where(
            Importancia.usuario_id == contexto.usuario_id,
            Importancia.excluida_em.is_(None),
            Importancia.possui_despesa.is_(True),
            Mov.id.is_(None),
        )
    )
    termo = busca.strip()
    if termo:
        consulta = consulta.where(
            Importancia.nome.ilike(f"%{escapar_busca(termo)}%", escape="\\")
        )
    if chaves is not None:
        try:
            consulta = consulta.where(
                tuple_(Importancia.data_compromisso, Importancia.id)
                > tuple_(date.fromisoformat(chaves[0]), uuid.UUID(chaves[1]))
            )
        except (ValueError, TypeError, IndexError) as exc:
            raise ErroNegocio(CodigoErro.CURSOR_INVALIDO) from exc
    linhas = (
        await sessao.scalars(
            consulta.order_by(
                Importancia.data_compromisso, Importancia.id
            ).limit(limite + 1)
        )
    ).all()
    pagina = linhas[:limite]
    proximo = (
        codificar_cursor(
            ORDEM_PAGAMENTOS,
            filtros,
            [pagina[-1].data_compromisso.isoformat(), str(pagina[-1].id)],
        )
        if len(linhas) > limite
        else None
    )
    return Pagina[PagamentoDisponivel](
        itens=[
            PagamentoDisponivel(
                id=i.id,
                nome=i.nome,
                data_compromisso=i.data_compromisso,
                valor_previsto=i.valor_previsto or Decimal(0),
            )
            for i in pagina
        ],
        proximo_cursor=proximo,
    )


async def despesas_disponiveis(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    *,
    busca: str,
    limite: int,
    cursor: str | None,
) -> Pagina[DespesaDisponivel]:
    """Despesas sem vínculo, da mais recente (11.5.5)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    filtros = {"busca": busca.strip().lower()}
    chaves: list[Any] | None = (
        decodificar_cursor(cursor, ORDEM_DESPESAS, filtros)
        if cursor is not None
        else None
    )
    consulta = select(Mov).where(
        Mov.usuario_id == contexto.usuario_id,
        Mov.excluida_em.is_(None),
        Mov.tipo == TipoMovimentacao.DESPESA,
        Mov.importancia_id.is_(None),
    )
    termo = busca.strip()
    if termo:
        consulta = consulta.where(
            Mov.nome.ilike(f"%{escapar_busca(termo)}%", escape="\\")
        )
    if chaves is not None:
        try:
            consulta = consulta.where(
                tuple_(Mov.data_movimentacao, Mov.criado_em, Mov.id)
                < tuple_(
                    date.fromisoformat(chaves[0]),
                    datetime.fromisoformat(chaves[1]),
                    uuid.UUID(chaves[2]),
                )
            )
        except (ValueError, TypeError, IndexError) as exc:
            raise ErroNegocio(CodigoErro.CURSOR_INVALIDO) from exc
    linhas = (
        await sessao.scalars(
            consulta.order_by(
                Mov.data_movimentacao.desc(),
                Mov.criado_em.desc(),
                Mov.id.desc(),
            ).limit(limite + 1)
        )
    ).all()
    pagina = linhas[:limite]
    proximo = (
        codificar_cursor(
            ORDEM_DESPESAS,
            filtros,
            [
                pagina[-1].data_movimentacao.isoformat(),
                pagina[-1].criado_em.isoformat(),
                str(pagina[-1].id),
            ],
        )
        if len(linhas) > limite
        else None
    )
    return Pagina[DespesaDisponivel](
        itens=[
            DespesaDisponivel(
                id=m.id,
                nome=m.nome,
                data_movimentacao=m.data_movimentacao,
                valor=m.valor,
            )
            for m in pagina
        ],
        proximo_cursor=proximo,
    )
