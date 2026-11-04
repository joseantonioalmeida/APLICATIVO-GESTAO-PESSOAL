"""Receitas e despesas: cadastro, consulta, edição e exclusão (§8.8)."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import CategoriaFinanceira
from api_gestao_pessoal.models import MovimentacaoFinanceira as Mov
from api_gestao_pessoal.models.enums import FormaMovimentacao, TipoMovimentacao
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.schemas.financeiro import (
    ConsultaMovimentacoesResposta,
    DespesaCriacao,
    FiltroTipo,
    MovimentacaoDetalhe,
    MovimentacaoEdicao,
    ReceitaCriacao,
)
from api_gestao_pessoal.services.autorizacao import obter_do_usuario_ou_404
from api_gestao_pessoal.services.consulta_movimentacoes import (
    consulta_base,
    montar_item,
    obter_detalhe,
)
from api_gestao_pessoal.services.paginacao import (
    codificar_cursor,
    decodificar_cursor,
    escapar_busca,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import (
    ContextoUsuario,
    primeiro_dia_mes,
    ultimo_dia_do_mes,
)

MENSAGEM_CATEGORIA_INVALIDA = "Selecione uma categoria válida"
MENSAGEM_FORMA = "Forma não disponível para este tipo de lançamento"
MENSAGEM_DATA_FUTURA = {
    TipoMovimentacao.RECEITA: "A data do recebimento não pode ser futura",
    TipoMovimentacao.DESPESA: (
        "A data do pagamento não pode ser futura. "
        "Cadastre o compromisso em Importâncias"
    ),
}
FORMAS_DA_RECEITA = frozenset({
    FormaMovimentacao.PIX,
    FormaMovimentacao.DINHEIRO,
    FormaMovimentacao.TRANSFERENCIA,
    FormaMovimentacao.DEPOSITO,
    FormaMovimentacao.OUTROS,
})
FORMAS_DA_DESPESA = frozenset({
    FormaMovimentacao.PIX,
    FormaMovimentacao.DINHEIRO,
    FormaMovimentacao.CARTAO_DEBITO,
    FormaMovimentacao.TRANSFERENCIA,
    FormaMovimentacao.BOLETO,
    FormaMovimentacao.OUTROS,
})


def _erro_campo(campo: str, codigo: str, mensagem: str) -> ErroNegocio:
    return ErroNegocio(
        CodigoErro.VALIDACAO,
        campos=[CampoErro(campo=campo, codigo=codigo, mensagem=mensagem)],
    )


async def validar_categoria(
    sessao: AsyncSession,
    categoria_id: uuid.UUID,
    tipo: TipoMovimentacao,
    *,
    atual: uuid.UUID | None = None,
) -> None:
    """Categoria ativa e do mesmo tipo; a atual pode ser mantida."""
    consulta = select(CategoriaFinanceira.id).where(
        CategoriaFinanceira.id == categoria_id,
        CategoriaFinanceira.tipo == tipo,
    )
    if categoria_id != atual:
        consulta = consulta.where(CategoriaFinanceira.ativa.is_(True))
    if await sessao.scalar(consulta) is None:
        raise _erro_campo(
            "categoria_id", "CATEGORIA_INVALIDA", MENSAGEM_CATEGORIA_INVALIDA
        )


def validar_data(data: date, hoje: date, tipo: TipoMovimentacao) -> None:
    """Data do recebimento/pagamento não pode ser futura."""
    if data > hoje:
        raise _erro_campo(
            "data_movimentacao", "DATA_FUTURA", MENSAGEM_DATA_FUTURA[tipo]
        )


def validar_forma(
    forma: FormaMovimentacao | None, tipo: TipoMovimentacao
) -> None:
    """Forma compatível com o tipo."""
    if forma is None:
        return
    permitidas = (
        FORMAS_DA_RECEITA
        if tipo == TipoMovimentacao.RECEITA
        else FORMAS_DA_DESPESA
    )
    if forma not in permitidas:
        raise _erro_campo("forma", "FORMA_INCOMPATIVEL", MENSAGEM_FORMA)


async def inserir(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    tipo: TipoMovimentacao,
    dados: ReceitaCriacao | DespesaCriacao,
    *,
    importancia_id: uuid.UUID | None = None,
) -> Mov:
    """Valida e insere (flush) a movimentação; o vínculo vem da F8."""
    await validar_categoria(sessao, dados.categoria_id, tipo)
    validar_data(dados.data_movimentacao, contexto.hoje, tipo)
    forma = FormaMovimentacao(dados.forma.value) if dados.forma else None
    validar_forma(forma, tipo)
    mov = Mov(
        usuario_id=contexto.usuario_id,
        categoria_id=dados.categoria_id,
        tipo=tipo,
        nome=dados.nome,
        descricao=dados.descricao,
        valor=dados.valor,
        data_movimentacao=dados.data_movimentacao,
        contraparte=dados.contraparte,
        forma_movimentacao=forma,
        importancia_id=importancia_id,
        importancia_vinculada_em=(
            contexto.agora if importancia_id is not None else None
        ),
    )
    sessao.add(mov)
    await sessao.flush()
    return mov


async def _detalhe(
    sessao: AsyncSession, contexto: ContextoUsuario, mov_id: uuid.UUID
) -> MovimentacaoDetalhe:
    detalhe = await obter_detalhe(sessao, contexto.usuario_id, mov_id)
    if detalhe is None:
        raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
    return detalhe


async def criar_receita(
    sessao: AsyncSession, contexto: ContextoUsuario, dados: ReceitaCriacao
) -> MovimentacaoDetalhe:
    """Cadastra uma receita (dentro de `executar_idempotente`)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    mov = await inserir(sessao, contexto, TipoMovimentacao.RECEITA, dados)
    return await _detalhe(sessao, contexto, mov.id)


async def criar_despesa(
    sessao: AsyncSession, contexto: ContextoUsuario, dados: DespesaCriacao
) -> MovimentacaoDetalhe:
    """Cadastra uma despesa sem vínculo (com vínculo: `pagamentos`)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    mov = await inserir(sessao, contexto, TipoMovimentacao.DESPESA, dados)
    return await _detalhe(sessao, contexto, mov.id)


async def obter(
    sessao: AsyncSession, contexto: ContextoUsuario, mov_id: uuid.UUID
) -> MovimentacaoDetalhe:
    """Detalhes de uma movimentação do usuário."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    return await _detalhe(sessao, contexto, mov_id)


async def aplicar_edicao(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    mov: Mov,
    dados: MovimentacaoEdicao,
) -> None:
    """Aplica os campos enviados (exceto vínculo) e valida as regras."""
    campos = dados.model_fields_set
    if "categoria_id" in campos and dados.categoria_id is not None:
        await validar_categoria(
            sessao, dados.categoria_id, mov.tipo, atual=mov.categoria_id
        )
        mov.categoria_id = dados.categoria_id
    if "data_movimentacao" in campos and dados.data_movimentacao is not None:
        validar_data(dados.data_movimentacao, contexto.hoje, mov.tipo)
        mov.data_movimentacao = dados.data_movimentacao
    if "forma" in campos:
        validar_forma(dados.forma, mov.tipo)
        mov.forma_movimentacao = dados.forma
    if "nome" in campos and dados.nome is not None:
        mov.nome = dados.nome
    if "valor" in campos and dados.valor is not None:
        mov.valor = dados.valor
    if "descricao" in campos:
        mov.descricao = dados.descricao
    if "contraparte" in campos:
        mov.contraparte = dados.contraparte
    await sessao.flush()


async def editar(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    mov_id: uuid.UUID,
    dados: MovimentacaoEdicao,
) -> MovimentacaoDetalhe:
    """Atualiza o mesmo lançamento (a identidade e o tipo se mantêm)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    mov = await obter_do_usuario_ou_404(
        sessao, Mov, mov_id, contexto.usuario_id
    )
    await aplicar_edicao(sessao, contexto, mov, dados)
    return await _detalhe(sessao, contexto, mov.id)


async def excluir(
    sessao: AsyncSession, contexto: ContextoUsuario, mov_id: uuid.UUID
) -> None:
    """Exclusão lógica; idempotente (§8.7: vínculo é desfeito)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    mov = await obter_do_usuario_ou_404(
        sessao, Mov, mov_id, contexto.usuario_id, incluir_excluidos=True
    )
    if mov.excluida_em is not None:
        return
    mov.excluida_em = contexto.agora
    mov.importancia_id = None
    mov.importancia_vinculada_em = None
    await sessao.flush()


# ---------------------------------------------------------------- consulta


def _chaves(mov: Mov) -> list[Any]:
    return [
        mov.data_movimentacao.isoformat(),
        mov.criado_em.isoformat(),
        str(mov.id),
    ]


async def consultar(  # noqa: PLR0913
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    *,
    mes: date,
    tipo: FiltroTipo,
    categoria_id: uuid.UUID | None,
    busca: str,
    limite: int,
    cursor: str | None,
) -> ConsultaMovimentacoesResposta:
    """Movimentações do mês com filtros e paginação keyset (§8.9)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    inicio, fim = primeiro_dia_mes(mes), ultimo_dia_do_mes(mes)
    if categoria_id is not None:
        categoria = await sessao.get(CategoriaFinanceira, categoria_id)
        if categoria is None or (
            tipo != FiltroTipo.TODAS and categoria.tipo.value != tipo.value
        ):
            raise _erro_campo(
                "categoria_id",
                "CATEGORIA_INVALIDA",
                MENSAGEM_CATEGORIA_INVALIDA,
            )
    filtros = {
        "mes": inicio.isoformat(),
        "tipo": tipo.value,
        "categoria_id": str(categoria_id) if categoria_id else None,
        "busca": busca.strip().lower(),
    }
    chaves = (
        decodificar_cursor(cursor, "DATA_DESC", filtros)
        if cursor is not None
        else None
    )
    condicoes: list[Any] = [
        Mov.usuario_id == contexto.usuario_id,
        Mov.excluida_em.is_(None),
        Mov.data_movimentacao.between(inicio, fim),
    ]
    possui = bool(
        await sessao.scalar(select(func.count()).where(*condicoes).limit(1))
    )
    if tipo != FiltroTipo.TODAS:
        condicoes.append(Mov.tipo == TipoMovimentacao(tipo.value))
    if categoria_id is not None:
        condicoes.append(Mov.categoria_id == categoria_id)
    termo = busca.strip()
    if termo:
        condicoes.append(
            Mov.nome.ilike(f"%{escapar_busca(termo)}%", escape="\\")
        )
    consulta = consulta_base().where(*condicoes)
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
        await sessao.execute(
            consulta.order_by(
                Mov.data_movimentacao.desc(),
                Mov.criado_em.desc(),
                Mov.id.desc(),
            ).limit(limite + 1)
        )
    ).all()
    pagina = linhas[:limite]
    proximo = (
        codificar_cursor("DATA_DESC", filtros, _chaves(pagina[-1][0]))
        if len(linhas) > limite
        else None
    )
    return ConsultaMovimentacoesResposta(
        itens=[montar_item(linha) for linha in pagina],
        proximo_cursor=proximo,
        mes=f"{inicio.year:04d}-{inicio.month:02d}",
        filtros_ativos=(
            tipo != FiltroTipo.TODAS or categoria_id is not None or bool(termo)
        ),
        possui_movimentacoes_mes=possui,
    )
