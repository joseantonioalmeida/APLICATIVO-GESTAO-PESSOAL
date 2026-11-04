"""Atividades: cadastro, consulta, edição e exclusão (arquitetura §8.5, §8.9).

Cada linha de `atividade` é uma ocorrência concreta. Séries guardam só a
regra e os padrões; as ocorrências são materializadas sob demanda, sempre
com a trava EXCLUSIVA do usuário.
"""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import (
    Integer,
    and_,
    case,
    extract,
    func,
    or_,
    select,
    tuple_,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import (
    Atividade,
    CategoriaAtividade,
    SerieAtividade,
)
from api_gestao_pessoal.models.enums import PeriodicidadeAtividade, Prioridade
from api_gestao_pessoal.schemas.atividade import (
    AtividadeCriacao,
    AtividadeDetalhe,
    AtividadeEdicao,
    AtividadeItem,
    CategoriaRef,
    ConflitoHorario,
    ConsultaAtividadesResposta,
    FiltroPrioridade,
    FiltroSituacao,
    Indicadores,
    OrdenacaoAtividades,
    PendenciasAnterioresResposta,
    PeriodicidadeRepeticao,
    RepeticaoEntrada,
    SerieResposta,
    SituacaoAtividade,
    TerminoRepeticao,
)
from api_gestao_pessoal.schemas.comum import AlcanceSerie
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.services.autorizacao import obter_do_usuario_ou_404
from api_gestao_pessoal.services.paginacao import (
    codificar_cursor,
    decodificar_cursor,
)
from api_gestao_pessoal.services.recorrencia import (
    RegraSerie,
    data_da_posicao,
    materializar_posicoes,
    posicao_valida,
    posicoes_no_intervalo,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import ContextoUsuario

TAMANHO_PREVIA = 30
ELIPSE = "…"
MENSAGEM_CATEGORIA_INVALIDA = "Selecione uma categoria válida"
MENSAGEM_HORARIO_FINAL = (
    "O horário final deve ser posterior ao horário inicial"
)
MENSAGEM_DATA_FINAL = (
    "A data final da repetição não pode ser anterior à primeira ocorrência"
)


@dataclass(frozen=True, slots=True)
class FiltrosConsulta:
    """Parâmetros de `GET /atividades` já validados."""

    data: date
    categoria_id: uuid.UUID | None
    situacao: FiltroSituacao
    prioridade: FiltroPrioridade
    busca: str
    ordenacao: OrdenacaoAtividades
    limite: int
    cursor: str | None


# --------------------------------------------------------------------------
# Conversões e utilidades puras
# --------------------------------------------------------------------------


def previa_da_descricao(descricao: str | None) -> str | None:
    """30 primeiros caracteres e reticências, se houver continuação."""
    if descricao is None:
        return None
    if len(descricao) <= TAMANHO_PREVIA:
        return descricao
    return descricao[:TAMANHO_PREVIA] + ELIPSE


def duracao_em_minutos(inicial: time, final: time) -> int:
    """Diferença em minutos (os horários não têm segundos)."""
    base = date(2000, 1, 1)
    return int(
        (
            datetime.combine(base, final) - datetime.combine(base, inicial)
        ).total_seconds()
        // 60
    )


def escapar_busca(texto: str) -> str:
    """Escapa `\\`, `%` e `_` para uso em `ILIKE ... ESCAPE '\\'`."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _periodicidade_modelo(
    valor: PeriodicidadeRepeticao,
) -> PeriodicidadeAtividade:
    if valor == PeriodicidadeRepeticao.NAO_REPETIR:
        return PeriodicidadeAtividade.NENHUMA
    return PeriodicidadeAtividade(valor.value)


def _periodicidade_api(
    valor: PeriodicidadeAtividade,
) -> PeriodicidadeRepeticao:
    if valor == PeriodicidadeAtividade.NENHUMA:
        return PeriodicidadeRepeticao.NAO_REPETIR
    return PeriodicidadeRepeticao(valor.value)


def _regra(serie: SerieAtividade) -> RegraSerie:
    return RegraSerie(
        periodicidade=serie.periodicidade.value,
        data_referencia=serie.data_referencia,
        numero_referencia=serie.numero_referencia,
        data_final_repeticao=serie.data_final_repeticao,
        numero_final=serie.numero_final,
    )


def _erro_campo(campo: str, codigo: str, mensagem: str) -> ErroNegocio:
    return ErroNegocio(
        CodigoErro.VALIDACAO,
        campos=[CampoErro(campo=campo, codigo=codigo, mensagem=mensagem)],
    )


def _validar_horarios(inicial: time, final: time) -> None:
    if final <= inicial:
        raise _erro_campo(
            "horario_final", "HORARIO_FINAL_INVALIDO", MENSAGEM_HORARIO_FINAL
        )


def _data_final_da_repeticao(
    repeticao: RepeticaoEntrada, primeira: date
) -> date | None:
    """Data final efetiva; valida que não antecede a primeira ocorrência."""
    if (
        repeticao.periodicidade == PeriodicidadeRepeticao.NAO_REPETIR
        or repeticao.termino == TerminoRepeticao.SEM_DATA_FINAL
    ):
        return None
    final = repeticao.data_final
    if final is None or final < primeira:
        raise _erro_campo(
            "repeticao.data_final",
            "DATA_FINAL_REPETICAO_INVALIDA",
            MENSAGEM_DATA_FINAL,
        )
    return final


# --------------------------------------------------------------------------
# Acesso a dados
# --------------------------------------------------------------------------


async def _categoria_ativa(
    sessao: AsyncSession, categoria_id: uuid.UUID
) -> None:
    existe = await sessao.scalar(
        select(CategoriaAtividade.id).where(
            CategoriaAtividade.id == categoria_id,
            CategoriaAtividade.ativa.is_(True),
        )
    )
    if existe is None:
        raise _erro_campo(
            "categoria_id", "CATEGORIA_INVALIDA", MENSAGEM_CATEGORIA_INVALIDA
        )


def _valores_da_ocorrencia(serie: SerieAtividade):  # noqa: ANN202
    regra = _regra(serie)

    def valores(n: int) -> dict[str, Any]:
        return {
            "id": uuid.uuid7(),
            "usuario_id": serie.usuario_id,
            "categoria_id": serie.categoria_id,
            "serie_id": serie.id,
            "nome": serie.nome_padrao,
            "descricao": serie.descricao_padrao,
            "prioridade": serie.prioridade_padrao,
            "data_atividade": data_da_posicao(regra, n),
            "horario_inicial": serie.horario_inicial_padrao,
            "horario_final": serie.horario_final_padrao,
        }

    return valores


async def _materializar_intervalo(
    sessao: AsyncSession,
    series: list[SerieAtividade],
    inicio: date,
    fim: date,
) -> None:
    for serie in series:
        posicoes = posicoes_no_intervalo(_regra(serie), inicio, fim)
        await materializar_posicoes(
            sessao,
            Atividade,
            serie.id,
            posicoes,
            _valores_da_ocorrencia(serie),
        )


async def materializar_dia(
    sessao: AsyncSession, usuario_id: uuid.UUID, dia: date
) -> None:
    """Materializa a ocorrência de `dia` de todas as séries do usuário."""
    series = (
        await sessao.scalars(
            select(SerieAtividade).where(
                SerieAtividade.usuario_id == usuario_id,
                SerieAtividade.data_referencia <= dia,
                or_(
                    SerieAtividade.data_final_repeticao.is_(None),
                    SerieAtividade.data_final_repeticao >= dia,
                ),
            )
        )
    ).all()
    await _materializar_intervalo(sessao, list(series), dia, dia)


async def materializar_passado(
    sessao: AsyncSession, usuario_id: uuid.UUID, hoje: date
) -> None:
    """Materializa tudo o que é anterior a `hoje` (pendências, 5.1.9)."""
    series = (
        await sessao.scalars(
            select(SerieAtividade).where(
                SerieAtividade.usuario_id == usuario_id,
                SerieAtividade.data_referencia < hoje,
            )
        )
    ).all()
    for serie in series:
        await _materializar_intervalo(
            sessao,
            [serie],
            serie.data_referencia,
            hoje - timedelta(days=1),
        )


async def _verificar_sobreposicao(  # noqa: PLR0913
    sessao: AsyncSession,
    usuario_id: uuid.UUID,
    data: date,
    inicial: time,
    final: time,
    *,
    ignorar_id: uuid.UUID | None,
    confirmar: bool,
) -> None:
    """409 com os conflitos, salvo se o cliente já confirmou (6.4.4)."""
    if confirmar:
        return
    consulta = (
        select(Atividade)
        .where(
            Atividade.usuario_id == usuario_id,
            Atividade.excluida_em.is_(None),
            Atividade.data_atividade == data,
            Atividade.horario_inicial < final,
            Atividade.horario_final > inicial,
        )
        .order_by(Atividade.horario_inicial, Atividade.id)
    )
    if ignorar_id is not None:
        consulta = consulta.where(Atividade.id != ignorar_id)
    conflitos = (await sessao.scalars(consulta)).all()
    if conflitos:
        raise ErroNegocio(
            CodigoErro.SOBREPOSICAO_HORARIO,
            detalhes={
                "conflitos": [
                    ConflitoHorario(
                        id=c.id,
                        nome=c.nome,
                        horario_inicial=c.horario_inicial,
                        horario_final=c.horario_final,
                    ).model_dump(mode="json")
                    for c in conflitos
                ]
            },
        )


def _item(atividade: Atividade, categoria_nome: str) -> AtividadeItem:
    return AtividadeItem(
        id=atividade.id,
        nome=atividade.nome,
        categoria=CategoriaRef(id=atividade.categoria_id, nome=categoria_nome),
        descricao_previa=previa_da_descricao(atividade.descricao),
        data=atividade.data_atividade,
        horario_inicial=atividade.horario_inicial,
        horario_final=atividade.horario_final,
        duracao_minutos=duracao_em_minutos(
            atividade.horario_inicial, atividade.horario_final
        ),
        prioridade=atividade.prioridade,
        situacao=(
            SituacaoAtividade.CONCLUIDA
            if atividade.concluida_em is not None
            else SituacaoAtividade.PENDENTE
        ),
        concluida_em=atividade.concluida_em,
        recorrente=atividade.serie_id is not None,
        serie_id=atividade.serie_id,
    )


async def _com_periodicidade(
    sessao: AsyncSession, itens: list[AtividadeItem]
) -> list[AtividadeItem]:
    """Preenche a repetição dos itens recorrentes (uma consulta só)."""
    ids = [i.id for i in itens if i.recorrente]
    if not ids:
        return itens
    linhas = (
        await sessao.execute(
            select(Atividade.id, SerieAtividade.periodicidade)
            .join(SerieAtividade, SerieAtividade.id == Atividade.serie_id)
            .where(Atividade.id.in_(ids))
        )
    ).all()
    por_id = {i: _periodicidade_api(p) for i, p in linhas}
    for item in itens:
        item.periodicidade = por_id.get(item.id, item.periodicidade)
    return itens


async def _detalhe(
    sessao: AsyncSession, atividade: Atividade
) -> AtividadeDetalhe:
    categoria_nome = await sessao.scalar(
        select(CategoriaAtividade.nome).where(
            CategoriaAtividade.id == atividade.categoria_id
        )
    )
    serie: SerieResposta | None = None
    if atividade.serie_id is not None:
        s = await sessao.get(SerieAtividade, atividade.serie_id)
        if s is not None:
            serie = SerieResposta(
                id=s.id,
                periodicidade=_periodicidade_api(s.periodicidade),
                termino=(
                    TerminoRepeticao.ATE_DATA
                    if s.data_final_repeticao is not None
                    else TerminoRepeticao.SEM_DATA_FINAL
                ),
                data_final=s.data_final_repeticao,
                numero_final=s.numero_final,
            )
    base = _item(atividade, categoria_nome or "")
    if serie is not None:
        base.periodicidade = serie.periodicidade
    return AtividadeDetalhe(
        **base.model_dump(),
        descricao=atividade.descricao,
        serie=serie,
        numero_ocorrencia=atividade.numero_ocorrencia,
        criado_em=atividade.criado_em,
        atualizado_em=atividade.atualizado_em,
    )


# --------------------------------------------------------------------------
# Cadastro
# --------------------------------------------------------------------------


async def criar(
    sessao: AsyncSession, contexto: ContextoUsuario, dados: AtividadeCriacao
) -> AtividadeDetalhe:
    """Cadastra uma atividade avulsa ou a primeira ocorrência de uma série.

    Chamado dentro de `executar_idempotente` (trava já adquirida).
    """
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    await _categoria_ativa(sessao, dados.categoria_id)
    data_final = _data_final_da_repeticao(dados.repeticao, dados.data)
    await materializar_dia(sessao, contexto.usuario_id, dados.data)
    await _verificar_sobreposicao(
        sessao,
        contexto.usuario_id,
        dados.data,
        dados.horario_inicial,
        dados.horario_final,
        ignorar_id=None,
        confirmar=dados.confirmar_sobreposicao,
    )
    if dados.repeticao.periodicidade == PeriodicidadeRepeticao.NAO_REPETIR:
        atividade = Atividade(
            usuario_id=contexto.usuario_id,
            categoria_id=dados.categoria_id,
            nome=dados.nome,
            descricao=dados.descricao,
            prioridade=dados.prioridade,
            data_atividade=dados.data,
            horario_inicial=dados.horario_inicial,
            horario_final=dados.horario_final,
        )
        sessao.add(atividade)
        await sessao.flush()
        return await _detalhe(sessao, atividade)
    serie = SerieAtividade(
        usuario_id=contexto.usuario_id,
        categoria_id=dados.categoria_id,
        nome_padrao=dados.nome,
        descricao_padrao=dados.descricao,
        prioridade_padrao=dados.prioridade,
        periodicidade=_periodicidade_modelo(dados.repeticao.periodicidade),
        data_referencia=dados.data,
        numero_referencia=1,
        horario_inicial_padrao=dados.horario_inicial,
        horario_final_padrao=dados.horario_final,
        data_final_repeticao=data_final,
    )
    sessao.add(serie)
    await sessao.flush()
    novas = await materializar_posicoes(
        sessao, Atividade, serie.id, range(1, 2), _valores_da_ocorrencia(serie)
    )
    atividade = await sessao.get_one(Atividade, novas[0][0])
    return await _detalhe(sessao, atividade)


# --------------------------------------------------------------------------
# Consultas
# --------------------------------------------------------------------------


def _condicoes(usuario_id: uuid.UUID, f: FiltrosConsulta) -> list[Any]:
    condicoes: list[Any] = [
        Atividade.usuario_id == usuario_id,
        Atividade.excluida_em.is_(None),
        Atividade.data_atividade == f.data,
    ]
    if f.categoria_id is not None:
        condicoes.append(Atividade.categoria_id == f.categoria_id)
    if f.situacao == FiltroSituacao.PENDENTE:
        condicoes.append(Atividade.concluida_em.is_(None))
    elif f.situacao == FiltroSituacao.CONCLUIDA:
        condicoes.append(Atividade.concluida_em.is_not(None))
    if f.prioridade != FiltroPrioridade.TODAS:
        condicoes.append(
            Atividade.prioridade == Prioridade(f.prioridade.value)
        )
    busca = f.busca.strip()
    if busca:
        condicoes.append(
            Atividade.nome.ilike(f"%{escapar_busca(busca)}%", escape="\\")
        )
    return condicoes


def _filtros_do_cursor(f: FiltrosConsulta) -> dict[str, Any]:
    return {
        "data": f.data.isoformat(),
        "categoria_id": str(f.categoria_id) if f.categoria_id else None,
        "situacao": f.situacao.value,
        "prioridade": f.prioridade.value,
        "busca": f.busca.strip().lower(),
    }


def _chaves_da_linha(
    ordenacao: OrdenacaoAtividades,
    atividade: Atividade,
    rank: int,
    criado_ord: datetime,
) -> list[Any]:
    match ordenacao:
        case OrdenacaoAtividades.HORARIO:
            return [atividade.horario_inicial.isoformat(), str(atividade.id)]
        case OrdenacaoAtividades.PRIORIDADE:
            return [
                rank,
                atividade.horario_inicial.isoformat(),
                str(atividade.id),
            ]
        case OrdenacaoAtividades.RECENTES:
            return [criado_ord.isoformat(), str(atividade.id)]


async def consultar(
    sessao: AsyncSession, contexto: ContextoUsuario, f: FiltrosConsulta
) -> ConsultaAtividadesResposta:
    """Atividades do dia com indicadores e paginação keyset (§8.9)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    chaves: list[Any] | None = None
    if f.cursor is not None:
        chaves = decodificar_cursor(
            f.cursor, f.ordenacao.value, _filtros_do_cursor(f)
        )
    await materializar_dia(sessao, contexto.usuario_id, f.data)

    condicoes = _condicoes(contexto.usuario_id, f)
    minutos = (
        extract("epoch", Atividade.horario_final - Atividade.horario_inicial)
        / 60
    ).cast(Integer)
    totais = (
        await sessao.execute(
            select(
                func.count(),
                func.count().filter(Atividade.concluida_em.is_not(None)),
                func.coalesce(func.sum(minutos), 0),
            ).where(*condicoes)
        )
    ).one()
    total, concluidas, tempo = int(totais[0]), int(totais[1]), int(totais[2])
    total_data = int(
        await sessao.scalar(
            select(func.count()).where(
                Atividade.usuario_id == contexto.usuario_id,
                Atividade.excluida_em.is_(None),
                Atividade.data_atividade == f.data,
            )
        )
        or 0
    )

    rank = case(
        (Atividade.prioridade == Prioridade.ALTA, 3),
        (Atividade.prioridade == Prioridade.MEDIA, 2),
        else_=1,
    )
    criado_ord = func.coalesce(SerieAtividade.criado_em, Atividade.criado_em)
    consulta = (
        select(
            Atividade,
            CategoriaAtividade.nome,
            rank.label("rank"),
            criado_ord.label("criado_ord"),
        )
        .join(
            CategoriaAtividade, CategoriaAtividade.id == Atividade.categoria_id
        )
        .outerjoin(SerieAtividade, SerieAtividade.id == Atividade.serie_id)
        .where(*condicoes)
    )
    try:
        consulta = _ordenar_e_paginar(consulta, f, rank, criado_ord, chaves)
    except (ValueError, TypeError, IndexError) as exc:
        raise ErroNegocio(CodigoErro.CURSOR_INVALIDO) from exc
    linhas: list[Any] = list(
        (await sessao.execute(consulta.limit(f.limite + 1))).all()
    )

    pagina = linhas[: f.limite]
    proximo: str | None = None
    if len(linhas) > f.limite:
        ultima = pagina[-1]
        proximo = codificar_cursor(
            f.ordenacao.value,
            _filtros_do_cursor(f),
            _chaves_da_linha(f.ordenacao, ultima[0], ultima[2], ultima[3]),
        )
    return ConsultaAtividadesResposta(
        itens=await _com_periodicidade(
            sessao, [_item(linha[0], linha[1]) for linha in pagina]
        ),
        proximo_cursor=proximo,
        data=f.data,
        eh_hoje=f.data == contexto.hoje,
        filtros_ativos=_filtros_ativos(f),
        total_data=total_data,
        indicadores=Indicadores(
            total=total,
            concluidas=concluidas,
            pendentes=total - concluidas,
            tempo_total_minutos=tempo,
        ),
    )


def _filtros_ativos(f: FiltrosConsulta) -> bool:
    return (
        f.categoria_id is not None
        or f.situacao != FiltroSituacao.TODAS
        or f.prioridade != FiltroPrioridade.TODAS
        or bool(f.busca.strip())
    )


def _ordenar_e_paginar(
    consulta: Any,
    f: FiltrosConsulta,
    rank: Any,
    criado_ord: Any,
    chaves: list[Any] | None,
) -> Any:
    match f.ordenacao:
        case OrdenacaoAtividades.HORARIO:
            if chaves is not None:
                consulta = consulta.where(
                    tuple_(Atividade.horario_inicial, Atividade.id)
                    > tuple_(
                        time.fromisoformat(chaves[0]), uuid.UUID(chaves[1])
                    )
                )
            return consulta.order_by(Atividade.horario_inicial, Atividade.id)
        case OrdenacaoAtividades.PRIORIDADE:
            if chaves is not None:
                r = int(chaves[0])
                h = time.fromisoformat(chaves[1])
                i = uuid.UUID(chaves[2])
                consulta = consulta.where(
                    or_(
                        rank < r,
                        and_(
                            rank == r,
                            tuple_(Atividade.horario_inicial, Atividade.id)
                            > tuple_(h, i),
                        ),
                    )
                )
            return consulta.order_by(
                rank.desc(), Atividade.horario_inicial, Atividade.id
            )
        case OrdenacaoAtividades.RECENTES:
            if chaves is not None:
                consulta = consulta.where(
                    tuple_(criado_ord, Atividade.id)
                    < tuple_(
                        datetime.fromisoformat(chaves[0]),
                        uuid.UUID(chaves[1]),
                    )
                )
            return consulta.order_by(criado_ord.desc(), Atividade.id.desc())


async def pendencias_anteriores(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> PendenciasAnterioresResposta:
    """Pendentes anteriores a hoje, sem os filtros da consulta (5.1.9)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    await materializar_passado(sessao, contexto.usuario_id, contexto.hoje)
    linha = (
        await sessao.execute(
            select(func.count(), func.min(Atividade.data_atividade)).where(
                Atividade.usuario_id == contexto.usuario_id,
                Atividade.excluida_em.is_(None),
                Atividade.concluida_em.is_(None),
                Atividade.data_atividade < contexto.hoje,
            )
        )
    ).one()
    return PendenciasAnterioresResposta(
        quantidade=int(linha[0]), data_mais_antiga=linha[1]
    )


LIMITE_PREVIA_PAINEL = 3


async def resumo_do_dia(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> tuple[int, int, list[AtividadeItem]]:
    """`(total, concluidas, previa)` de hoje, sem filtros (4.1.4).

    Os totais cobrem todas as atividades do dia; a prévia traz até três,
    pendentes antes das concluídas, por horário inicial e `id`.
    """
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    await materializar_dia(sessao, contexto.usuario_id, contexto.hoje)
    do_dia = (
        Atividade.usuario_id == contexto.usuario_id,
        Atividade.excluida_em.is_(None),
        Atividade.data_atividade == contexto.hoje,
    )
    total, concluidas = (
        await sessao.execute(
            select(
                func.count(),
                func.count().filter(Atividade.concluida_em.is_not(None)),
            ).where(*do_dia)
        )
    ).one()
    linhas = (
        await sessao.execute(
            select(Atividade, CategoriaAtividade.nome)
            .join(
                CategoriaAtividade,
                CategoriaAtividade.id == Atividade.categoria_id,
            )
            .where(*do_dia)
            .order_by(
                Atividade.concluida_em.is_not(None),
                Atividade.horario_inicial,
                Atividade.id,
            )
            .limit(LIMITE_PREVIA_PAINEL)
        )
    ).all()
    return (
        int(total),
        int(concluidas),
        await _com_periodicidade(
            sessao, [_item(atividade, nome) for atividade, nome in linhas]
        ),
    )


async def obter(
    sessao: AsyncSession, contexto: ContextoUsuario, atividade_id: uuid.UUID
) -> AtividadeDetalhe:
    """Detalhes de uma atividade do usuário (404 se não for dele)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    atividade = await obter_do_usuario_ou_404(
        sessao, Atividade, atividade_id, contexto.usuario_id
    )
    return await _detalhe(sessao, atividade)


# --------------------------------------------------------------------------
# Situação
# --------------------------------------------------------------------------


async def definir_situacao(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    atividade_id: uuid.UUID,
    situacao: SituacaoAtividade,
) -> AtividadeDetalhe:
    """Define o estado alvo (não alterna): repetir é um no-op (5.3.5)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    atividade = await obter_do_usuario_ou_404(
        sessao, Atividade, atividade_id, contexto.usuario_id
    )
    if situacao == SituacaoAtividade.CONCLUIDA:
        if atividade.concluida_em is None:
            atividade.concluida_em = contexto.agora
    else:
        atividade.concluida_em = None
    await sessao.flush()
    return await _detalhe(sessao, atividade)


# --------------------------------------------------------------------------
# Edição
# --------------------------------------------------------------------------

_CAMPOS_DA_OCORRENCIA = (
    "nome",
    "categoria_id",
    "prioridade",
    "descricao",
    "horario_inicial",
    "horario_final",
)
_CAMPOS_DE_AGENDA = frozenset({"data", "horario_inicial", "horario_final"})
_PADROES_DA_SERIE = {
    "nome": "nome_padrao",
    "categoria_id": "categoria_id",
    "prioridade": "prioridade_padrao",
    "descricao": "descricao_padrao",
    "horario_inicial": "horario_inicial_padrao",
    "horario_final": "horario_final_padrao",
}


def _enviado(dados: AtividadeEdicao, campo: str, atual: Any) -> Any:
    return getattr(dados, campo) if campo in dados.model_fields_set else atual


def _validar_alcance(atividade: Atividade, dados: AtividadeEdicao) -> bool:
    """Valida alcance e repetição (§8.5.7, passos 2-4).

    Devolve `True` quando a edição deve atingir a série.
    """
    pede_proximas = dados.alcance == AlcanceSerie.ESTA_E_PROXIMAS
    mexe_repeticao = dados.repeticao is not None
    serie = atividade.serie_id is not None
    if atividade.concluida_em is not None:
        if pede_proximas:
            raise ErroNegocio(CodigoErro.ALCANCE_INVALIDO)
        if mexe_repeticao:
            raise ErroNegocio(CodigoErro.REPETICAO_EXIGE_ALCANCE_SERIE)
        return False
    if not serie:
        if pede_proximas:
            raise ErroNegocio(CodigoErro.ALCANCE_INVALIDO)
        return False
    if mexe_repeticao and not pede_proximas:
        raise ErroNegocio(CodigoErro.REPETICAO_EXIGE_ALCANCE_SERIE)
    return pede_proximas


async def editar(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    atividade_id: uuid.UUID,
    dados: AtividadeEdicao,
) -> AtividadeDetalhe:
    """Edita uma ocorrência ou ela e as próximas pendentes (§8.5.7)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    atividade = await obter_do_usuario_ou_404(
        sessao, Atividade, atividade_id, contexto.usuario_id
    )
    campos = dados.model_fields_set
    escopo_serie = _validar_alcance(atividade, dados)

    if "categoria_id" in campos and dados.categoria_id is not None:
        await _categoria_ativa(sessao, dados.categoria_id)
    inicial: time = _enviado(
        dados, "horario_inicial", atividade.horario_inicial
    )
    final: time = _enviado(dados, "horario_final", atividade.horario_final)
    _validar_horarios(inicial, final)

    if escopo_serie:
        data_da_linha = await _editar_serie(sessao, contexto, atividade, dados)
    else:
        data_da_linha = _enviado(dados, "data", atividade.data_atividade)
        if campos & _CAMPOS_DE_AGENDA:
            await _verificar_sobreposicao(
                sessao,
                contexto.usuario_id,
                data_da_linha,
                inicial,
                final,
                ignorar_id=atividade.id,
                confirmar=dados.confirmar_sobreposicao,
            )
        for campo in _CAMPOS_DA_OCORRENCIA:
            if campo in campos:
                setattr(atividade, campo, getattr(dados, campo))
        atividade.data_atividade = data_da_linha
        if (
            atividade.serie_id is None
            and dados.repeticao is not None
            and dados.repeticao.periodicidade
            != PeriodicidadeRepeticao.NAO_REPETIR
        ):
            await _converter_em_serie(sessao, atividade, dados.repeticao)
    await sessao.flush()
    return await _detalhe(sessao, atividade)


async def _converter_em_serie(
    sessao: AsyncSession, atividade: Atividade, repeticao: RepeticaoEntrada
) -> None:
    """Avulsa vira a posição 1 de uma nova série (§8.5.7, passo 3)."""
    data_final = _data_final_da_repeticao(repeticao, atividade.data_atividade)
    serie = SerieAtividade(
        usuario_id=atividade.usuario_id,
        categoria_id=atividade.categoria_id,
        nome_padrao=atividade.nome,
        descricao_padrao=atividade.descricao,
        prioridade_padrao=atividade.prioridade,
        periodicidade=_periodicidade_modelo(repeticao.periodicidade),
        data_referencia=atividade.data_atividade,
        numero_referencia=1,
        horario_inicial_padrao=atividade.horario_inicial,
        horario_final_padrao=atividade.horario_final,
        data_final_repeticao=data_final,
    )
    sessao.add(serie)
    await sessao.flush()
    atividade.serie_id = serie.id
    atividade.numero_ocorrencia = 1


def _regra_proposta(
    atividade: Atividade,
    regra: RegraSerie,
    dados: AtividadeEdicao,
    k: int,
) -> RegraSerie:
    """Nova regra da série a partir da posição `k` (§8.5.7, passo 5.2-5.4)."""
    if (
        "data" in dados.model_fields_set
        and dados.data is not None
        and dados.data != atividade.data_atividade
    ):
        referencia = dados.data
    elif k >= regra.numero_referencia:
        referencia = data_da_posicao(regra, k) or atividade.data_atividade
    else:
        referencia = atividade.data_atividade
    periodicidade = regra.periodicidade
    data_final = regra.data_final_repeticao
    numero_final = regra.numero_final
    if dados.repeticao is not None:
        periodicidade = _periodicidade_modelo(
            dados.repeticao.periodicidade
        ).value
        if dados.repeticao.termino == TerminoRepeticao.SEM_DATA_FINAL:
            data_final = None
            numero_final = None
        else:
            data_final = dados.repeticao.data_final
    if data_final is not None and data_final < referencia:
        raise _erro_campo(
            "repeticao.data_final",
            "DATA_FINAL_REPETICAO_INVALIDA",
            MENSAGEM_DATA_FINAL,
        )
    return RegraSerie(periodicidade, referencia, k, data_final, numero_final)


async def _editar_serie(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    atividade: Atividade,
    dados: AtividadeEdicao,
) -> date:
    """`ESTA_E_PROXIMAS` sobre uma ocorrência pendente de série.

    Devolve a data resultante da ocorrência selecionada.
    """
    if atividade.serie_id is None or atividade.numero_ocorrencia is None:
        msg = "ocorrência sem série"
        raise RuntimeError(msg)
    serie = await sessao.get_one(SerieAtividade, atividade.serie_id)
    k = atividade.numero_ocorrencia
    regra = _regra(serie)
    campos = dados.model_fields_set
    inicial: time = _enviado(
        dados, "horario_inicial", atividade.horario_inicial
    )
    final: time = _enviado(dados, "horario_final", atividade.horario_final)

    # Preserva I-REC-1: as posições anteriores seguem a regra atual.
    if k > regra.numero_referencia:
        await materializar_posicoes(
            sessao,
            Atividade,
            serie.id,
            range(regra.numero_referencia, k),
            _valores_da_ocorrencia(serie),
        )

    nova_regra = _regra_proposta(atividade, regra, dados, k)
    nova_referencia = nova_regra.data_referencia
    periodicidade = PeriodicidadeAtividade(nova_regra.periodicidade)
    data_final = nova_regra.data_final_repeticao
    numero_final = nova_regra.numero_final

    data_da_linha = data_da_posicao(nova_regra, k) or nova_referencia
    if campos & _CAMPOS_DE_AGENDA:
        await _verificar_sobreposicao(
            sessao,
            contexto.usuario_id,
            data_da_linha,
            inicial,
            final,
            ignorar_id=atividade.id,
            confirmar=dados.confirmar_sobreposicao,
        )

    serie.periodicidade = periodicidade
    serie.data_referencia = nova_referencia
    serie.numero_referencia = k
    serie.data_final_repeticao = data_final
    serie.numero_final = numero_final
    for campo, padrao in _PADROES_DA_SERIE.items():
        if campo in campos:
            setattr(serie, padrao, getattr(dados, campo))

    linhas = (
        await sessao.scalars(
            select(Atividade)
            .where(
                Atividade.serie_id == serie.id,
                Atividade.numero_ocorrencia >= k,
                Atividade.excluida_em.is_(None),
                Atividade.concluida_em.is_(None),
            )
            .order_by(Atividade.numero_ocorrencia)
        )
    ).all()
    for linha in linhas:
        n = linha.numero_ocorrencia
        if n is not None and posicao_valida(nova_regra, n):
            for campo in _CAMPOS_DA_OCORRENCIA:
                if campo in campos:
                    setattr(linha, campo, getattr(dados, campo))
            linha.data_atividade = (
                data_da_posicao(nova_regra, n) or linha.data_atividade
            )
        else:
            linha.excluida_em = contexto.agora
    return data_da_linha


# --------------------------------------------------------------------------
# Exclusão
# --------------------------------------------------------------------------


async def excluir(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    atividade_id: uuid.UUID,
    alcance: AlcanceSerie,
) -> None:
    """Exclui uma ocorrência ou interrompe a série (§8.5.8). Idempotente."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    atividade = await obter_do_usuario_ou_404(
        sessao,
        Atividade,
        atividade_id,
        contexto.usuario_id,
        incluir_excluidos=True,
    )
    if atividade.excluida_em is not None:
        return
    if alcance == AlcanceSerie.SOMENTE_ESTA:
        atividade.excluida_em = contexto.agora
        await sessao.flush()
        return
    if atividade.serie_id is None or atividade.concluida_em is not None:
        raise ErroNegocio(CodigoErro.ALCANCE_INVALIDO)
    k = atividade.numero_ocorrencia
    if k is None:
        msg = "ocorrência de série sem número"
        raise RuntimeError(msg)
    serie = await sessao.get_one(SerieAtividade, atividade.serie_id)
    serie.numero_final = (
        k - 1 if serie.numero_final is None else min(serie.numero_final, k - 1)
    )
    linhas = (
        await sessao.scalars(
            select(Atividade).where(
                Atividade.serie_id == serie.id,
                Atividade.numero_ocorrencia >= k,
                Atividade.excluida_em.is_(None),
                Atividade.concluida_em.is_(None),
            )
        )
    ).all()
    for linha in linhas:
        linha.excluida_em = contexto.agora
    await sessao.flush()
