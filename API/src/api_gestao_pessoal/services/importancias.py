"""Importâncias: cadastro, consulta, edição e exclusão (§8.5, §8.9).

Cada linha de `importancia` é uma ocorrência concreta. A situação
(pendente, concluída, paga, atrasada) é sempre derivada. O vínculo com
despesas e os pagamentos pertencem a `pagamentos` (F8).
"""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, case, func, or_, select, tuple_, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from api_gestao_pessoal.erros import CodigoErro, ErroNegocio
from api_gestao_pessoal.models import (
    CategoriaFinanceira,
    CategoriaImportancia,
    Importancia,
    LembreteImportancia,
    MovimentacaoFinanceira,
    SerieImportancia,
)
from api_gestao_pessoal.models.enums import (
    PeriodicidadeImportancia,
    SituacaoLembrete,
    TipoMovimentacao,
)
from api_gestao_pessoal.schemas.atividade import CategoriaRef, TerminoRepeticao
from api_gestao_pessoal.schemas.comum import AlcanceSerie
from api_gestao_pessoal.schemas.erro import CampoErro
from api_gestao_pessoal.schemas.importancia import (
    CategoriaFinanceiraSugerida,
    ConsultaImportanciasResposta,
    FiltroImportancia,
    GrupoImportancia,
    Grupos,
    ImportanciaCriacao,
    ImportanciaDetalhe,
    ImportanciaEdicao,
    ImportanciaItem,
    LembreteEntrada,
    LembreteResposta,
    PagamentoVinculado,
    PeriodicidadeImportanciaApi,
    Prazo,
    RepeticaoImportanciaEntrada,
    SerieImportanciaResposta,
    SituacaoImportancia,
)
from api_gestao_pessoal.services import lembretes
from api_gestao_pessoal.services.autorizacao import obter_do_usuario_ou_404
from api_gestao_pessoal.services.lembretes import ConfigLembrete
from api_gestao_pessoal.services.paginacao import (
    codificar_cursor,
    decodificar_cursor,
    escapar_busca,
)
from api_gestao_pessoal.services.recorrencia import (
    RegraSerie,
    data_da_posicao,
    materializar_posicoes,
    posicao_valida,
    posicoes_no_intervalo,
    somar_meses,
    ultimo_dia_mes,
)
from api_gestao_pessoal.services.situacao_importancia import (
    Movimentacao as M,
)
from api_gestao_pessoal.services.situacao_importancia import (
    concluida as expr_concluida,
)
from api_gestao_pessoal.services.situacao_importancia import (
    momento_conclusao as expr_momento,
)
from api_gestao_pessoal.services.trava import ModoTrava, travar_usuario
from api_gestao_pessoal.tempo import (
    ContextoUsuario,
    primeiro_dia_mes,
    ultimo_dia_do_mes,
)

MENSAGEM_CATEGORIA_INVALIDA = "Selecione uma categoria válida"
MENSAGEM_VALOR_OBRIGATORIO = "Informe um valor previsto maior que zero"
MENSAGEM_VALOR_PROIBIDO = (
    "Remova o valor previsto ou marque que possui despesa"
)
MENSAGEM_LEMBRETE_PASSADO = (
    "O lembrete precisa estar em uma data e horário futuros. "
    "Ajuste ou desative o lembrete"
)
MENSAGEM_DATA_FINAL = (
    "A data final da repetição não pode ser anterior à primeira ocorrência"
)
MESES_DE_HORIZONTE = 12

GRUPOS_DO_FILTRO: dict[FiltroImportancia, list[GrupoImportancia]] = {
    FiltroImportancia.TODOS: list(GrupoImportancia),
    FiltroImportancia.VENCENDO_HOJE: [GrupoImportancia.HOJE],
    FiltroImportancia.ESTE_MES: list(GrupoImportancia),
    FiltroImportancia.PROXIMOS: [GrupoImportancia.PROXIMAS],
    FiltroImportancia.CONCLUIDOS: [GrupoImportancia.CONCLUIDAS],
    FiltroImportancia.ATRASADOS: [GrupoImportancia.ATRASADAS],
}


@dataclass(frozen=True, slots=True)
class FiltrosConsulta:
    """Parâmetros de `GET /importancias` já validados."""

    filtro: FiltroImportancia
    mes: date | None
    busca: str
    limite: int
    cursor: str | None


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------


def _erro_campo(campo: str, codigo: str, mensagem: str) -> ErroNegocio:
    return ErroNegocio(
        CodigoErro.VALIDACAO,
        campos=[CampoErro(campo=campo, codigo=codigo, mensagem=mensagem)],
    )


def _periodicidade_modelo(
    valor: PeriodicidadeImportanciaApi,
) -> PeriodicidadeImportancia:
    if valor == PeriodicidadeImportanciaApi.NAO_REPETIR:
        return PeriodicidadeImportancia.NENHUMA
    return PeriodicidadeImportancia(valor.value)


def _periodicidade_api(
    valor: PeriodicidadeImportancia,
) -> PeriodicidadeImportanciaApi:
    if valor == PeriodicidadeImportancia.NENHUMA:
        return PeriodicidadeImportanciaApi.NAO_REPETIR
    return PeriodicidadeImportanciaApi(valor.value)


def _regra(serie: SerieImportancia) -> RegraSerie:
    return RegraSerie(
        periodicidade=serie.periodicidade.value,
        data_referencia=serie.data_referencia,
        numero_referencia=serie.numero_referencia,
        data_final_repeticao=serie.data_final_repeticao,
        numero_final=serie.numero_final,
    )


def horizonte_de(hoje: date) -> date:
    """Último dia do 12º mês após o mês de hoje (DEC-MV-18)."""
    ano, mes = somar_meses(hoje.year, hoje.month, MESES_DE_HORIZONTE)
    return date(ano, mes, ultimo_dia_mes(ano, mes))


def _validar_despesa(possui: bool, valor: Decimal | None) -> None:  # noqa: FBT001
    if possui and valor is None:
        raise _erro_campo(
            "valor_previsto",
            "VALOR_PREVISTO_OBRIGATORIO",
            MENSAGEM_VALOR_OBRIGATORIO,
        )
    if not possui and valor is not None:
        raise _erro_campo(
            "valor_previsto",
            "VALOR_PREVISTO_NAO_PERMITIDO",
            MENSAGEM_VALOR_PROIBIDO,
        )


def _data_final(
    repeticao: RepeticaoImportanciaEntrada, primeira: date
) -> date | None:
    if (
        repeticao.periodicidade == PeriodicidadeImportanciaApi.NAO_REPETIR
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


def _config(entrada: LembreteEntrada | None) -> ConfigLembrete | None:
    if entrada is None:
        return None
    return ConfigLembrete(entrada.antecedencia_dias, entrada.horario)


def _exigir_futuro(
    config: ConfigLembrete, data: date, contexto: ContextoUsuario
) -> None:
    agendado = lembretes.calcular_agendamento(data, config, contexto.fuso)
    if agendado <= contexto.agora:
        raise _erro_campo(
            "lembrete", "LEMBRETE_NO_PASSADO", MENSAGEM_LEMBRETE_PASSADO
        )


async def _categoria_ativa(
    sessao: AsyncSession, categoria_id: uuid.UUID
) -> None:
    existe = await sessao.scalar(
        select(CategoriaImportancia.id).where(
            CategoriaImportancia.id == categoria_id,
            CategoriaImportancia.ativa.is_(True),
        )
    )
    if existe is None:
        raise _erro_campo(
            "categoria_id", "CATEGORIA_INVALIDA", MENSAGEM_CATEGORIA_INVALIDA
        )


# --------------------------------------------------------------------------
# Itens (conversão de linhas)
# --------------------------------------------------------------------------


def consulta_itens() -> Any:  # noqa: ANN401
    """Importância + categoria + movimentação vinculada (se houver)."""
    return (
        select(
            Importancia,
            CategoriaImportancia.nome,
            M.id,
            M.valor,
            M.data_movimentacao,
            M.importancia_vinculada_em,
        )
        .join(
            CategoriaImportancia,
            CategoriaImportancia.id == Importancia.categoria_id,
        )
        .outerjoin(M, M.importancia_id == Importancia.id)
    )


def _situacao(linha: Any) -> tuple[bool, bool, datetime | None]:  # noqa: ANN401
    """`(concluida, paga, momento)` de uma linha de `consulta_itens`."""
    imp, _, mov_id, _, _, vinculada_em = linha
    if imp.possui_despesa:
        return mov_id is not None, mov_id is not None, vinculada_em
    return (
        imp.concluida_manualmente_em is not None,
        False,
        imp.concluida_manualmente_em,
    )


def montar_item(linha: Any, hoje: date) -> ImportanciaItem:  # noqa: ANN401
    """Converte uma linha de `consulta_itens` em item de lista."""
    imp, categoria_nome, mov_id, mov_valor, mov_data, _ = linha
    concluida, paga, momento = _situacao(linha)
    dias = None if concluida else (imp.data_compromisso - hoje).days
    prazo: Prazo | None = None
    if dias is not None:
        if dias < 0:
            prazo = Prazo.ATRASADA
        elif dias == 0:
            prazo = Prazo.HOJE
        elif dias == 1:
            prazo = Prazo.AMANHA
        else:
            prazo = Prazo.EM_DIAS
    if concluida:
        grupo = GrupoImportancia.CONCLUIDAS
    elif dias is not None and dias < 0:
        grupo = GrupoImportancia.ATRASADAS
    elif dias == 0:
        grupo = GrupoImportancia.HOJE
    else:
        grupo = GrupoImportancia.PROXIMAS
    return ImportanciaItem(
        id=imp.id,
        nome=imp.nome,
        descricao=imp.descricao,
        categoria=CategoriaRef(id=imp.categoria_id, nome=categoria_nome),
        data_compromisso=imp.data_compromisso,
        horario=imp.horario,
        possui_despesa=imp.possui_despesa,
        valor_previsto=imp.valor_previsto,
        pagamento=(
            PagamentoVinculado(
                movimentacao_id=mov_id,
                valor=mov_valor,
                data_movimentacao=mov_data,
            )
            if paga
            else None
        ),
        situacao=(
            SituacaoImportancia.CONCLUIDA
            if concluida
            else SituacaoImportancia.PENDENTE
        ),
        pago=paga,
        atrasada=dias is not None and dias < 0,
        dias_ate_vencimento=dias,
        prazo=prazo,
        recorrente=imp.serie_id is not None,
        serie_id=imp.serie_id,
        grupo=grupo,
        momento_conclusao=momento,
    )


async def _com_periodicidade(
    sessao: AsyncSession, itens: list[ImportanciaItem]
) -> list[ImportanciaItem]:
    """Preenche a repetição dos itens recorrentes (uma consulta só)."""
    ids = [i.id for i in itens if i.recorrente]
    if not ids:
        return itens
    linhas = (
        await sessao.execute(
            select(Importancia.id, SerieImportancia.periodicidade)
            .join(
                SerieImportancia, SerieImportancia.id == Importancia.serie_id
            )
            .where(Importancia.id.in_(ids))
        )
    ).all()
    por_id = {i: _periodicidade_api(p) for i, p in linhas}
    for item in itens:
        item.periodicidade = por_id.get(item.id, item.periodicidade)
    return itens


async def detalhe(
    sessao: AsyncSession, contexto: ContextoUsuario, importancia_id: uuid.UUID
) -> ImportanciaDetalhe:
    """Detalhe completo (404 se não for do usuário ou estiver excluída)."""
    linha = (
        await sessao.execute(
            consulta_itens().where(
                Importancia.id == importancia_id,
                Importancia.usuario_id == contexto.usuario_id,
                Importancia.excluida_em.is_(None),
            )
        )
    ).first()
    if linha is None:
        raise ErroNegocio(CodigoErro.RECURSO_NAO_ENCONTRADO)
    linha_t: Any = linha
    imp: Importancia = linha_t[0]
    (base,) = await _com_periodicidade(
        sessao, [montar_item(linha_t, contexto.hoje)]
    )
    lembrete = await lembretes.obter(sessao, imp.id)
    serie: SerieImportanciaResposta | None = None
    if imp.serie_id is not None:
        s = await sessao.get(SerieImportancia, imp.serie_id)
        if s is not None:
            serie = SerieImportanciaResposta(
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
    sugerida = await sessao.scalar(
        select(CategoriaFinanceira).where(
            CategoriaFinanceira.tipo == TipoMovimentacao.DESPESA,
            CategoriaFinanceira.ativa.is_(True),
            CategoriaFinanceira.nome == linha_t[1],
        )
    )
    return ImportanciaDetalhe(
        **base.model_dump(),
        lembrete=(
            LembreteResposta(
                antecedencia_dias=lembrete.antecedencia_dias,
                horario=lembrete.horario,
                situacao=lembrete.situacao,
                agendado_para=lembrete.agendado_para,
            )
            if lembrete is not None
            else None
        ),
        serie=serie,
        numero_ocorrencia=imp.numero_ocorrencia,
        categoria_financeira_sugerida=(
            CategoriaFinanceiraSugerida(id=sugerida.id, nome=sugerida.nome)
            if sugerida is not None
            else None
        ),
        criado_em=imp.criado_em,
        atualizado_em=imp.atualizado_em,
    )


async def obter(
    sessao: AsyncSession, contexto: ContextoUsuario, importancia_id: uuid.UUID
) -> ImportanciaDetalhe:
    """`GET /importancias/{id}`."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.COMPARTILHADA)
    return await detalhe(sessao, contexto, importancia_id)


# --------------------------------------------------------------------------
# Séries: materialização
# --------------------------------------------------------------------------


def _valores_da_ocorrencia(serie: SerieImportancia):  # noqa: ANN202
    regra = _regra(serie)

    def valores(n: int) -> dict[str, Any]:
        return {
            "id": uuid.uuid7(),
            "usuario_id": serie.usuario_id,
            "categoria_id": serie.categoria_id,
            "serie_id": serie.id,
            "nome": serie.nome_padrao,
            "descricao": serie.descricao_padrao,
            "data_compromisso": data_da_posicao(regra, n),
            "horario": serie.horario_padrao,
            "possui_despesa": serie.possui_despesa_padrao,
            "valor_previsto": serie.valor_previsto_padrao,
        }

    return valores


async def _materializar(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    serie: SerieImportancia,
    posicoes: range,
) -> list[tuple[uuid.UUID, int]]:
    """Insere as posições faltantes e, se houver, os lembretes (§8.6.2)."""
    regra = _regra(serie)
    novas = await materializar_posicoes(
        sessao, Importancia, serie.id, posicoes, _valores_da_ocorrencia(serie)
    )
    if novas and serie.lembrete_antecedencia_dias is not None:
        assert serie.lembrete_horario is not None  # noqa: S101
        config = ConfigLembrete(
            serie.lembrete_antecedencia_dias, serie.lembrete_horario
        )
        linhas: list[dict[str, Any]] = []
        for imp_id, n in novas:
            data = data_da_posicao(regra, n)
            if data is None:
                continue
            agendado = lembretes.calcular_agendamento(
                data, config, contexto.fuso
            )
            linhas.append({
                "id": uuid.uuid7(),
                "usuario_id": serie.usuario_id,
                "importancia_id": imp_id,
                "antecedencia_dias": config.antecedencia_dias,
                "horario": config.horario,
                "agendado_para": agendado,
                "versao_agendamento": 1,
                "situacao": (
                    SituacaoLembrete.PENDENTE
                    if agendado > contexto.agora
                    else SituacaoLembrete.CANCELADO
                ),
            })
        if linhas:
            await sessao.execute(
                pg_insert(LembreteImportancia)
                .values(linhas)
                .on_conflict_do_nothing(index_elements=["importancia_id"])
            )
    return novas


async def _materializar_filtro(
    sessao: AsyncSession, contexto: ContextoUsuario, f: FiltrosConsulta
) -> None:
    """Materializa o que o filtro precisa enxergar (§8.5.4)."""
    hoje = contexto.hoje
    passado = (None, hoje - timedelta(days=1))  # a partir da referência
    futuro = (hoje, horizonte_de(hoje))
    match f.filtro:
        case FiltroImportancia.TODOS:
            intervalos = [passado, futuro]
        case FiltroImportancia.PROXIMOS:
            intervalos = [futuro]
        case FiltroImportancia.ATRASADOS:
            intervalos = [passado]
        case FiltroImportancia.VENCENDO_HOJE:
            intervalos = [(hoje, hoje)]
        case FiltroImportancia.ESTE_MES:
            mes = f.mes or hoje
            intervalos = [(primeiro_dia_mes(mes), ultimo_dia_do_mes(mes))]
        case FiltroImportancia.CONCLUIDOS:
            return
    series = (
        await sessao.scalars(
            select(SerieImportancia).where(
                SerieImportancia.usuario_id == contexto.usuario_id
            )
        )
    ).all()
    for serie in series:
        regra = _regra(serie)
        for ini, fim in intervalos:
            inicio = ini or serie.data_referencia
            if fim < inicio:
                continue
            await _materializar(
                sessao,
                contexto,
                serie,
                posicoes_no_intervalo(regra, inicio, fim),
            )


async def materializar_janela_da_serie(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    serie_id: uuid.UUID,
    inicio: date,
    fim: date,
) -> int:
    """Materializa `[inicio, fim]` de uma série (usado pelo processador).

    Cria também os lembretes das ocorrências novas (§8.6.3). Devolve a
    quantidade de ocorrências criadas; a série precisa ser do usuário.
    """
    serie = await sessao.get(SerieImportancia, serie_id)
    if serie is None or serie.usuario_id != contexto.usuario_id:
        return 0
    inicio = max(inicio, serie.data_referencia)
    if fim < inicio:
        return 0
    novas = await _materializar(
        sessao,
        contexto,
        serie,
        posicoes_no_intervalo(_regra(serie), inicio, fim),
    )
    return len(novas)


# --------------------------------------------------------------------------
# Cadastro
# --------------------------------------------------------------------------


async def criar(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    dados: ImportanciaCriacao,
) -> ImportanciaDetalhe:
    """Cadastra uma importância (dentro de `executar_idempotente`)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    await _categoria_ativa(sessao, dados.categoria_id)
    _validar_despesa(dados.possui_despesa, dados.valor_previsto)
    data_final = _data_final(dados.repeticao, dados.data_compromisso)
    config = _config(dados.lembrete)
    if config is not None:
        _exigir_futuro(config, dados.data_compromisso, contexto)
    if (
        dados.repeticao.periodicidade
        == PeriodicidadeImportanciaApi.NAO_REPETIR
    ):
        imp = Importancia(
            usuario_id=contexto.usuario_id,
            categoria_id=dados.categoria_id,
            nome=dados.nome,
            descricao=dados.descricao,
            data_compromisso=dados.data_compromisso,
            horario=dados.horario,
            possui_despesa=dados.possui_despesa,
            valor_previsto=dados.valor_previsto,
        )
        sessao.add(imp)
        await sessao.flush()
        if config is not None:
            await lembretes.reagendar(
                sessao, imp, config, contexto, pendente=True
            )
            await sessao.flush()
        return await detalhe(sessao, contexto, imp.id)
    serie = SerieImportancia(
        usuario_id=contexto.usuario_id,
        categoria_id=dados.categoria_id,
        nome_padrao=dados.nome,
        descricao_padrao=dados.descricao,
        periodicidade=_periodicidade_modelo(dados.repeticao.periodicidade),
        data_referencia=dados.data_compromisso,
        numero_referencia=1,
        horario_padrao=dados.horario,
        data_final_repeticao=data_final,
        possui_despesa_padrao=dados.possui_despesa,
        valor_previsto_padrao=dados.valor_previsto,
        lembrete_antecedencia_dias=config.antecedencia_dias
        if config
        else None,
        lembrete_horario=config.horario if config else None,
    )
    sessao.add(serie)
    await sessao.flush()
    novas = await _materializar(sessao, contexto, serie, range(1, 2))
    return await detalhe(sessao, contexto, novas[0][0])


# --------------------------------------------------------------------------
# Consulta
# --------------------------------------------------------------------------


def _cond_grupo(
    grupo: GrupoImportancia, hoje: date, horizonte: date | None
) -> Any:  # noqa: ANN401
    concluida = expr_concluida()
    data = Importancia.data_compromisso
    match grupo:
        case GrupoImportancia.ATRASADAS:
            return and_(~concluida, data < hoje)
        case GrupoImportancia.HOJE:
            return and_(~concluida, data == hoje)
        case GrupoImportancia.PROXIMAS:
            cond = and_(~concluida, data > hoje)
            if horizonte is not None:
                cond = and_(
                    cond,
                    or_(Importancia.serie_id.is_(None), data <= horizonte),
                )
            return cond
        case GrupoImportancia.CONCLUIDAS:
            return concluida


_NULO = case((Importancia.horario.is_(None), 1), else_=0)
_HORARIO = func.coalesce(Importancia.horario, time(0, 0))


def _ordenar(grupo: GrupoImportancia, consulta: Any) -> Any:  # noqa: ANN401
    if grupo == GrupoImportancia.CONCLUIDAS:
        return consulta.order_by(expr_momento().desc(), Importancia.id.desc())
    return consulta.order_by(
        Importancia.data_compromisso, _NULO, _HORARIO, Importancia.id
    )


def _keyset(
    grupo: GrupoImportancia,
    chaves: list[Any],
    consulta: Any,  # noqa: ANN401
) -> Any:  # noqa: ANN401
    if grupo == GrupoImportancia.CONCLUIDAS:
        return consulta.where(
            tuple_(expr_momento(), Importancia.id)
            < tuple_(datetime.fromisoformat(chaves[0]), uuid.UUID(chaves[1]))
        )
    return consulta.where(
        tuple_(Importancia.data_compromisso, _NULO, _HORARIO, Importancia.id)
        > tuple_(
            date.fromisoformat(chaves[0]),
            int(chaves[1]),
            time.fromisoformat(chaves[2]),
            uuid.UUID(chaves[3]),
        )
    )


def _chaves_da_linha(grupo: GrupoImportancia, linha: Any) -> list[Any]:  # noqa: ANN401
    imp: Importancia = linha[0]
    if grupo == GrupoImportancia.CONCLUIDAS:
        return [_situacao(linha)[2].isoformat(), str(imp.id)]  # type: ignore[union-attr]
    return [
        imp.data_compromisso.isoformat(),
        1 if imp.horario is None else 0,
        (imp.horario or time(0, 0)).isoformat(),
        str(imp.id),
    ]


@dataclass(frozen=True, slots=True)
class _Contexto:
    """Dados compartilhados entre as etapas de `consultar`."""

    filtros: FiltrosConsulta
    comuns: list[Any]
    hoje: date
    horizonte: date | None
    grupos: list[GrupoImportancia]
    contagens: dict[GrupoImportancia, int]
    cursor_filtros: dict[str, Any]


async def _contar_grupos(
    sessao: AsyncSession,
    comuns: list[Any],
    hoje: date,
    horizonte: date | None,
) -> dict[GrupoImportancia, int]:
    """Quantidade por grupo no universo completo do filtro (7.2.7)."""
    totais = (
        await sessao.execute(
            select(*[
                func.count().filter(_cond_grupo(g, hoje, horizonte))
                for g in GrupoImportancia
            ])
            .select_from(Importancia)
            .outerjoin(M, M.importancia_id == Importancia.id)
            .where(*comuns)
        )
    ).one()
    return dict(zip(GrupoImportancia, (int(t) for t in totais), strict=True))


async def _paginar(
    sessao: AsyncSession, c: _Contexto, chaves: list[Any] | None
) -> tuple[list[ImportanciaItem], str | None]:
    """Preenche a página percorrendo os grupos em ordem (keyset por grupo)."""
    f = c.filtros
    inicio = 0
    chaves_do_grupo: list[Any] = []
    if chaves is not None:
        try:
            inicio = c.grupos.index(GrupoImportancia(chaves[0]))
        except (ValueError, IndexError, TypeError) as exc:
            raise ErroNegocio(CodigoErro.CURSOR_INVALIDO) from exc
        chaves_do_grupo = chaves[1:]
    itens: list[ImportanciaItem] = []
    restante = f.limite
    for idx in range(inicio, len(c.grupos)):
        grupo = c.grupos[idx]
        if c.contagens[grupo] == 0:
            continue
        consulta = consulta_itens().where(
            *c.comuns, _cond_grupo(grupo, c.hoje, c.horizonte)
        )
        if idx == inicio and chaves_do_grupo:
            try:
                consulta = _keyset(grupo, chaves_do_grupo, consulta)
            except (ValueError, IndexError, TypeError) as exc:
                raise ErroNegocio(CodigoErro.CURSOR_INVALIDO) from exc
        linhas = (
            await sessao.execute(_ordenar(grupo, consulta).limit(restante + 1))
        ).all()
        if len(linhas) > restante:
            pagina = linhas[:restante]
            itens += [montar_item(linha, c.hoje) for linha in pagina]
            return itens, codificar_cursor(
                f.filtro.value,
                c.cursor_filtros,
                [grupo.value, *_chaves_da_linha(grupo, pagina[-1])],
            )
        itens += [montar_item(linha, c.hoje) for linha in linhas]
        restante -= len(linhas)
        if restante == 0:
            seguinte = next(
                (g for g in c.grupos[idx + 1 :] if c.contagens[g] > 0), None
            )
            proximo = (
                codificar_cursor(
                    f.filtro.value, c.cursor_filtros, [seguinte.value]
                )
                if seguinte is not None
                else None
            )
            return itens, proximo
    return itens, None


async def consultar(
    sessao: AsyncSession, contexto: ContextoUsuario, f: FiltrosConsulta
) -> ConsultaImportanciasResposta:
    """Lista agrupada com contagens do universo completo (§8.9)."""
    if f.mes is not None and f.filtro != FiltroImportancia.ESTE_MES:
        raise _erro_campo(
            "mes",
            "MES_SO_COM_ESTE_MES",
            "O mês só vale para o filtro Este mês",
        )
    modo = (
        ModoTrava.COMPARTILHADA
        if f.filtro == FiltroImportancia.CONCLUIDOS
        else ModoTrava.EXCLUSIVA
    )
    await travar_usuario(sessao, contexto.usuario_id, modo)
    hoje = contexto.hoje
    mes = (f.mes or hoje) if f.filtro == FiltroImportancia.ESTE_MES else None
    texto_mes = mes.strftime("%Y-%m") if mes else None
    cursor_filtros = {
        "filtro": f.filtro.value,
        "mes": texto_mes,
        "busca": f.busca.strip().lower(),
    }
    chaves = (
        decodificar_cursor(f.cursor, f.filtro.value, cursor_filtros)
        if f.cursor is not None
        else None
    )
    if modo == ModoTrava.EXCLUSIVA:
        await _materializar_filtro(sessao, contexto, f)

    comuns: list[Any] = [
        Importancia.usuario_id == contexto.usuario_id,
        Importancia.excluida_em.is_(None),
    ]
    if mes is not None:
        comuns.append(
            Importancia.data_compromisso.between(
                primeiro_dia_mes(mes), ultimo_dia_do_mes(mes)
            )
        )
    termo = f.busca.strip()
    if termo:
        comuns.append(
            Importancia.nome.ilike(f"%{escapar_busca(termo)}%", escape="\\")
        )
    horizonte = (
        horizonte_de(hoje)
        if f.filtro in {FiltroImportancia.TODOS, FiltroImportancia.PROXIMOS}
        else None
    )
    grupos = GRUPOS_DO_FILTRO[f.filtro]
    contagens = await _contar_grupos(sessao, comuns, hoje, horizonte)
    possui = bool(
        await sessao.scalar(
            select(func.count()).where(
                Importancia.usuario_id == contexto.usuario_id,
                Importancia.excluida_em.is_(None),
            )
        )
    )
    itens, proximo = await _paginar(
        sessao,
        _Contexto(
            f, comuns, hoje, horizonte, grupos, contagens, cursor_filtros
        ),
        chaves,
    )
    rotulo = None
    if mes is not None:
        rotulo = (
            "Este mês"
            if primeiro_dia_mes(mes) == primeiro_dia_mes(hoje)
            else "Mês selecionado"
        )
    return ConsultaImportanciasResposta(
        itens=await _com_periodicidade(sessao, itens),
        proximo_cursor=proximo,
        filtro=f.filtro,
        mes=texto_mes,
        rotulo_periodo=rotulo,
        horizonte_proximas=horizonte,
        possui_importancias=possui,
        grupos=Grupos(
            atrasadas=contagens[GrupoImportancia.ATRASADAS],
            hoje=contagens[GrupoImportancia.HOJE],
            proximas=contagens[GrupoImportancia.PROXIMAS],
            concluidas=contagens[GrupoImportancia.CONCLUIDAS],
        ),
        total=sum(contagens[g] for g in grupos),
    )


# --------------------------------------------------------------------------
# Situação
# --------------------------------------------------------------------------


async def _movimentacao_vinculada(
    sessao: AsyncSession, importancia_id: uuid.UUID
) -> uuid.UUID | None:
    return await sessao.scalar(
        select(MovimentacaoFinanceira.id).where(
            MovimentacaoFinanceira.importancia_id == importancia_id
        )
    )


def esta_concluida(
    imp: Importancia, movimentacao_id: uuid.UUID | None
) -> bool:
    """Concluída: paga (com despesa) ou concluída manualmente."""
    if imp.possui_despesa:
        return movimentacao_id is not None
    return imp.concluida_manualmente_em is not None


async def definir_situacao(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    importancia_id: uuid.UUID,
    situacao: SituacaoImportancia,
) -> ImportanciaDetalhe:
    """Define o estado alvo; repetir é um no-op (§8.5.9)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    imp = await obter_do_usuario_ou_404(
        sessao, Importancia, importancia_id, contexto.usuario_id
    )
    mov_id = await _movimentacao_vinculada(sessao, imp.id)
    if imp.possui_despesa:
        if situacao == SituacaoImportancia.CONCLUIDA and mov_id is None:
            raise ErroNegocio(CodigoErro.CONCLUSAO_EXIGE_PAGAMENTO)
        if situacao == SituacaoImportancia.PENDENTE and mov_id is not None:
            raise ErroNegocio(CodigoErro.REABERTURA_EXIGE_REMOVER_PAGAMENTO)
        return await detalhe(sessao, contexto, imp.id)
    if situacao == SituacaoImportancia.CONCLUIDA:
        if imp.concluida_manualmente_em is None:
            imp.concluida_manualmente_em = contexto.agora
            await sessao.flush()
            await lembretes.cancelar_pendente(sessao, imp.id)
    elif imp.concluida_manualmente_em is not None:
        imp.concluida_manualmente_em = None
        await sessao.flush()
        await lembretes.ao_reabrir_importancia(sessao, imp.id, contexto.agora)
    return await detalhe(sessao, contexto, imp.id)


# --------------------------------------------------------------------------
# Edição
# --------------------------------------------------------------------------


def _validar_alcance(
    imp: Importancia,
    concluida: bool,
    dados: ImportanciaEdicao,  # noqa: FBT001
) -> bool:
    """Valida alcance e repetição (§8.5.7); `True` = editar a série."""
    pede_proximas = dados.alcance == AlcanceSerie.ESTA_E_PROXIMAS
    mexe_repeticao = dados.repeticao is not None
    if concluida:
        if pede_proximas:
            raise ErroNegocio(CodigoErro.ALCANCE_INVALIDO)
        if mexe_repeticao:
            raise ErroNegocio(CodigoErro.REPETICAO_EXIGE_ALCANCE_SERIE)
        return False
    if imp.serie_id is None:
        if pede_proximas:
            raise ErroNegocio(CodigoErro.ALCANCE_INVALIDO)
        return False
    if mexe_repeticao and not pede_proximas:
        raise ErroNegocio(CodigoErro.REPETICAO_EXIGE_ALCANCE_SERIE)
    return pede_proximas


def _resolver_despesa(
    imp: Importancia,
    mov_id: uuid.UUID | None,
    dados: ImportanciaEdicao,
) -> tuple[bool, Decimal | None]:
    """Aplica as regras de `possui_despesa` (§8.7); devolve o estado final."""
    campos = dados.model_fields_set
    possui = imp.possui_despesa
    if "possui_despesa" in campos and dados.possui_despesa is not None:
        possui = dados.possui_despesa
    if possui != imp.possui_despesa:
        if imp.possui_despesa and mov_id is not None:
            raise ErroNegocio(CodigoErro.IMPORTANCIA_PAGA_SEM_ALTERAR_DESPESA)
        if not imp.possui_despesa and imp.concluida_manualmente_em is not None:
            raise ErroNegocio(
                CodigoErro.IMPORTANCIA_CONCLUIDA_SEM_ALTERAR_DESPESA
            )
    valor = (
        dados.valor_previsto
        if "valor_previsto" in campos
        else imp.valor_previsto
    )
    if (
        not possui
        and "valor_previsto" in campos
        and dados.valor_previsto is not None
    ):
        raise _erro_campo(
            "valor_previsto",
            "VALOR_PREVISTO_NAO_PERMITIDO",
            MENSAGEM_VALOR_PROIBIDO,
        )
    if possui != imp.possui_despesa and not possui:
        valor = None
    if possui and "valor_previsto" in campos and dados.valor_previsto is None:
        raise _erro_campo(
            "valor_previsto",
            "VALOR_PREVISTO_OBRIGATORIO",
            MENSAGEM_VALOR_OBRIGATORIO,
        )
    _validar_despesa(possui, valor)
    return possui, valor


async def _sincronizar_lembrete(  # noqa: PLR0913
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    imp: Importancia,
    dados: ImportanciaEdicao,
    *,
    data_mudou: bool,
    pendente: bool,
    validar_futuro: bool,
) -> None:
    """Reagenda/desativa o lembrete de uma linha após a edição (§8.6.2)."""
    mexe = "lembrete" in dados.model_fields_set
    if mexe:
        config = _config(dados.lembrete)
        if config is not None and validar_futuro and pendente:
            _exigir_futuro(config, imp.data_compromisso, contexto)
    else:
        if not data_mudou:
            return
        config = lembretes.config_de(await lembretes.obter(sessao, imp.id))
        if config is None:
            return
    await lembretes.reagendar(sessao, imp, config, contexto, pendente=pendente)


def _aplicar(
    imp: Importancia,
    dados: ImportanciaEdicao,
    possui: bool,  # noqa: FBT001
    valor: Decimal | None,
) -> None:
    campos = dados.model_fields_set
    if "nome" in campos and dados.nome is not None:
        imp.nome = dados.nome
    if "categoria_id" in campos and dados.categoria_id is not None:
        imp.categoria_id = dados.categoria_id
    if "descricao" in campos:
        imp.descricao = dados.descricao
    if "horario" in campos:
        imp.horario = dados.horario
    imp.possui_despesa = possui
    imp.valor_previsto = valor


async def editar(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    importancia_id: uuid.UUID,
    dados: ImportanciaEdicao,
) -> ImportanciaDetalhe:
    """Edita uma ocorrência ou ela e as próximas pendentes (§8.5.7)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    imp = await obter_do_usuario_ou_404(
        sessao, Importancia, importancia_id, contexto.usuario_id
    )
    mov_id = await _movimentacao_vinculada(sessao, imp.id)
    concluida = esta_concluida(imp, mov_id)
    escopo_serie = _validar_alcance(imp, concluida, dados)
    campos = dados.model_fields_set
    if "categoria_id" in campos and dados.categoria_id is not None:
        await _categoria_ativa(sessao, dados.categoria_id)
    possui, valor = _resolver_despesa(imp, mov_id, dados)

    if escopo_serie:
        await _editar_serie(sessao, contexto, imp, dados, (possui, valor))
    else:
        data_antiga = imp.data_compromisso
        if "data_compromisso" in campos and dados.data_compromisso:
            imp.data_compromisso = dados.data_compromisso
        _aplicar(imp, dados, possui, valor)
        await sessao.flush()
        await _sincronizar_lembrete(
            sessao,
            contexto,
            imp,
            dados,
            data_mudou=imp.data_compromisso != data_antiga,
            pendente=not concluida,
            validar_futuro=True,
        )
        if (
            imp.serie_id is None
            and dados.repeticao is not None
            and dados.repeticao.periodicidade
            != PeriodicidadeImportanciaApi.NAO_REPETIR
        ):
            await _converter_em_serie(sessao, imp, dados.repeticao)
    await sessao.flush()
    return await detalhe(sessao, contexto, imp.id)


async def _converter_em_serie(
    sessao: AsyncSession,
    imp: Importancia,
    repeticao: RepeticaoImportanciaEntrada,
) -> None:
    """Avulsa vira a posição 1 de uma nova série (§8.5.7, passo 3)."""
    data_final = _data_final(repeticao, imp.data_compromisso)
    lembrete = await lembretes.obter(sessao, imp.id)
    config = lembretes.config_de(lembrete)
    serie = SerieImportancia(
        usuario_id=imp.usuario_id,
        categoria_id=imp.categoria_id,
        nome_padrao=imp.nome,
        descricao_padrao=imp.descricao,
        periodicidade=_periodicidade_modelo(repeticao.periodicidade),
        data_referencia=imp.data_compromisso,
        numero_referencia=1,
        horario_padrao=imp.horario,
        data_final_repeticao=data_final,
        possui_despesa_padrao=imp.possui_despesa,
        valor_previsto_padrao=imp.valor_previsto,
        lembrete_antecedencia_dias=config.antecedencia_dias
        if config
        else None,
        lembrete_horario=config.horario if config else None,
    )
    sessao.add(serie)
    await sessao.flush()
    imp.serie_id = serie.id
    imp.numero_ocorrencia = 1


def _regra_proposta(
    imp: Importancia,
    regra: RegraSerie,
    dados: ImportanciaEdicao,
    k: int,
) -> RegraSerie:
    """Nova regra da série a partir da posição `k` (§8.5.7, passo 5)."""
    if (
        "data_compromisso" in dados.model_fields_set
        and dados.data_compromisso is not None
        and dados.data_compromisso != imp.data_compromisso
    ):
        referencia = dados.data_compromisso
    elif k >= regra.numero_referencia:
        referencia = data_da_posicao(regra, k) or imp.data_compromisso
    else:
        referencia = imp.data_compromisso
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


def _atualizar_padroes(
    serie: SerieImportancia,
    dados: ImportanciaEdicao,
    possui: bool,  # noqa: FBT001
    valor: Decimal | None,
) -> None:
    campos = dados.model_fields_set
    if "nome" in campos and dados.nome is not None:
        serie.nome_padrao = dados.nome
    if "categoria_id" in campos and dados.categoria_id is not None:
        serie.categoria_id = dados.categoria_id
    if "descricao" in campos:
        serie.descricao_padrao = dados.descricao
    if "horario" in campos:
        serie.horario_padrao = dados.horario
    serie.possui_despesa_padrao = possui
    serie.valor_previsto_padrao = valor
    if "lembrete" in campos:
        config = _config(dados.lembrete)
        serie.lembrete_antecedencia_dias = (
            config.antecedencia_dias if config else None
        )
        serie.lembrete_horario = config.horario if config else None


async def _editar_serie(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    imp: Importancia,
    dados: ImportanciaEdicao,
    despesa: tuple[bool, Decimal | None],
) -> None:
    """`ESTA_E_PROXIMAS` sobre uma ocorrência pendente de série."""
    possui, valor = despesa
    if imp.serie_id is None or imp.numero_ocorrencia is None:
        msg = "ocorrência sem série"
        raise RuntimeError(msg)
    serie = await sessao.get_one(SerieImportancia, imp.serie_id)
    k = imp.numero_ocorrencia
    regra = _regra(serie)
    if k > regra.numero_referencia:
        await _materializar(
            sessao, contexto, serie, range(regra.numero_referencia, k)
        )
    nova_regra = _regra_proposta(imp, regra, dados, k)
    config = _config(dados.lembrete)
    if "lembrete" in dados.model_fields_set and config is not None:
        data_da_linha = data_da_posicao(nova_regra, k) or imp.data_compromisso
        _exigir_futuro(config, data_da_linha, contexto)

    serie.periodicidade = PeriodicidadeImportancia(nova_regra.periodicidade)
    serie.data_referencia = nova_regra.data_referencia
    serie.numero_referencia = k
    serie.data_final_repeticao = nova_regra.data_final_repeticao
    serie.numero_final = nova_regra.numero_final
    _atualizar_padroes(serie, dados, possui, valor)

    linhas = (
        await sessao.scalars(
            select(Importancia)
            .outerjoin(M, M.importancia_id == Importancia.id)
            .where(
                Importancia.serie_id == serie.id,
                Importancia.numero_ocorrencia >= k,
                Importancia.excluida_em.is_(None),
                ~expr_concluida(),
            )
            .order_by(Importancia.numero_ocorrencia)
        )
    ).all()
    for linha in linhas:
        n = linha.numero_ocorrencia
        if n is not None and posicao_valida(nova_regra, n):
            data_antiga = linha.data_compromisso
            nova_data = data_da_posicao(nova_regra, n)
            if nova_data is not None:
                linha.data_compromisso = nova_data
            _aplicar(linha, dados, possui, valor)
            await sessao.flush()
            await _sincronizar_lembrete(
                sessao,
                contexto,
                linha,
                dados,
                data_mudou=linha.data_compromisso != data_antiga,
                pendente=True,
                validar_futuro=False,
            )
        else:
            await _excluir_linha(sessao, contexto, linha)


# --------------------------------------------------------------------------
# Exclusão
# --------------------------------------------------------------------------


async def _excluir_linha(
    sessao: AsyncSession, contexto: ContextoUsuario, imp: Importancia
) -> None:
    """Exclui a linha: cancela o lembrete e desvincula a despesa (RI-5)."""
    imp.excluida_em = contexto.agora
    await sessao.flush()
    await lembretes.cancelar_pendente(sessao, imp.id)
    await sessao.execute(
        update(MovimentacaoFinanceira)
        .where(MovimentacaoFinanceira.importancia_id == imp.id)
        .values(importancia_id=None, importancia_vinculada_em=None)
    )


async def excluir(
    sessao: AsyncSession,
    contexto: ContextoUsuario,
    importancia_id: uuid.UUID,
    alcance: AlcanceSerie,
) -> None:
    """Exclui uma ocorrência ou interrompe a série (§8.5.8). Idempotente."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    imp = await obter_do_usuario_ou_404(
        sessao,
        Importancia,
        importancia_id,
        contexto.usuario_id,
        incluir_excluidos=True,
    )
    if imp.excluida_em is not None:
        return
    if alcance == AlcanceSerie.SOMENTE_ESTA:
        await _excluir_linha(sessao, contexto, imp)
        return
    mov_id = await _movimentacao_vinculada(sessao, imp.id)
    if (
        imp.serie_id is None
        or imp.numero_ocorrencia is None
        or esta_concluida(imp, mov_id)
    ):
        raise ErroNegocio(CodigoErro.ALCANCE_INVALIDO)
    k = imp.numero_ocorrencia
    serie = await sessao.get_one(SerieImportancia, imp.serie_id)
    serie.numero_final = (
        k - 1 if serie.numero_final is None else min(serie.numero_final, k - 1)
    )
    linhas = (
        await sessao.scalars(
            select(Importancia)
            .outerjoin(M, M.importancia_id == Importancia.id)
            .where(
                Importancia.serie_id == serie.id,
                Importancia.numero_ocorrencia >= k,
                Importancia.excluida_em.is_(None),
                ~expr_concluida(),
            )
        )
    ).all()
    for linha in linhas:
        await _excluir_linha(sessao, contexto, linha)


# --------------------------------------------------------------------------
# Painel inicial (§8.10): mesmas regras e funções da tela de Importâncias
# --------------------------------------------------------------------------

LIMITE_PROXIMAS_PAINEL = 3
ANOS_EXTRA_PROXIMAS = 5


@dataclass(frozen=True, slots=True)
class ResumoPainel:
    """Blocos de importâncias da tela inicial."""

    pendentes_mes: int
    proximas: list[ImportanciaItem]
    atrasadas_quantidade: int


async def _materializar_intervalo_do_usuario(
    sessao: AsyncSession, contexto: ContextoUsuario, inicio: date, fim: date
) -> None:
    series = (
        await sessao.scalars(
            select(SerieImportancia).where(
                SerieImportancia.usuario_id == contexto.usuario_id
            )
        )
    ).all()
    for serie in series:
        de = max(inicio, serie.data_referencia)
        if fim >= de:
            await _materializar(
                sessao,
                contexto,
                serie,
                posicoes_no_intervalo(_regra(serie), de, fim),
            )


async def _proximas_do_painel(
    sessao: AsyncSession, usuario_id: uuid.UUID, hoje: date
) -> list[ImportanciaItem]:
    consulta = consulta_itens().where(
        Importancia.usuario_id == usuario_id,
        Importancia.excluida_em.is_(None),
        ~expr_concluida(),
        Importancia.data_compromisso >= hoje,
    )
    linhas = (
        await sessao.execute(
            _ordenar(GrupoImportancia.PROXIMAS, consulta).limit(
                LIMITE_PROXIMAS_PAINEL
            )
        )
    ).all()
    return await _com_periodicidade(
        sessao, [montar_item(linha, hoje) for linha in linhas]
    )


async def resumo_painel(
    sessao: AsyncSession, contexto: ContextoUsuario
) -> ResumoPainel:
    """Pendentes do mês, três próximas e atrasadas (4.1.2, 4.1.8, 4.2.4)."""
    await travar_usuario(sessao, contexto.usuario_id, ModoTrava.EXCLUSIVA)
    hoje = contexto.hoje
    await _materializar_filtro(
        sessao,
        contexto,
        FiltrosConsulta(FiltroImportancia.TODOS, None, "", 1, None),
    )
    proximas = await _proximas_do_painel(sessao, contexto.usuario_id, hoje)
    if len(proximas) < LIMITE_PROXIMAS_PAINEL:
        # Sem horizonte (4.1.8): procura mais adiante, só para séries.
        await _materializar_intervalo_do_usuario(
            sessao,
            contexto,
            horizonte_de(hoje) + timedelta(days=1),
            hoje.replace(year=hoje.year + ANOS_EXTRA_PROXIMAS, day=28),
        )
        proximas = await _proximas_do_painel(sessao, contexto.usuario_id, hoje)
    comuns = [
        Importancia.usuario_id == contexto.usuario_id,
        Importancia.excluida_em.is_(None),
    ]
    pendentes_mes = await sessao.scalar(
        select(func.count())
        .select_from(Importancia)
        .outerjoin(M, M.importancia_id == Importancia.id)
        .where(
            *comuns,
            ~expr_concluida(),
            Importancia.data_compromisso.between(
                primeiro_dia_mes(hoje), ultimo_dia_do_mes(hoje)
            ),
        )
    )
    atrasadas = await sessao.scalar(
        select(func.count())
        .select_from(Importancia)
        .outerjoin(M, M.importancia_id == Importancia.id)
        .where(*comuns, _cond_grupo(GrupoImportancia.ATRASADAS, hoje, None))
    )
    return ResumoPainel(
        pendentes_mes=int(pendentes_mes or 0),
        proximas=proximas,
        atrasadas_quantidade=int(atrasadas or 0),
    )
