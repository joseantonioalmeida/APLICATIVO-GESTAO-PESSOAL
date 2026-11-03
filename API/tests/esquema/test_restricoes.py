import uuid
from datetime import date, time
from decimal import Decimal

from sqlalchemy import Connection, text

from ..apoio.esquema import (
    MOMENTO,
    SQLSTATE_CHECK,
    SQLSTATE_FK,
    SQLSTATE_NOT_NULL,
    SQLSTATE_TEXTO_LONGO,
    SQLSTATE_UNICO,
    esperar_violacao,
    id_categoria,
    inserir,
    inserir_atividade,
    inserir_importancia,
    inserir_lembrete,
    inserir_movimentacao,
    inserir_notificacao,
    inserir_recuperacao,
    inserir_requisicao,
    inserir_serie_atividade,
    inserir_serie_importancia,
    inserir_usuario,
)

PREVISTO = Decimal("99.90")


def _importancia_com_despesa(
    conexao: Connection, usuario_id: uuid.UUID
) -> uuid.UUID:
    return inserir_importancia(
        conexao, usuario_id, possui_despesa=True, valor_previsto=PREVISTO
    )


# CT-F2-11: propriedade dos relacionamentos entre usuários


def test_fk_propriedade_atividade_serie(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    serie = inserir_serie_atividade(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_atividade(
            conexao, b, serie_id=serie, numero_ocorrencia=1
        ),
    )
    inserir_atividade(conexao, a, serie_id=serie, numero_ocorrencia=1)


def test_fk_propriedade_importancia_serie(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    serie = inserir_serie_importancia(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_importancia(
            conexao, b, serie_id=serie, numero_ocorrencia=1
        ),
    )
    inserir_importancia(conexao, a, serie_id=serie, numero_ocorrencia=1)


def test_fk_propriedade_movimentacao_importancia(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    importancia = _importancia_com_despesa(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_movimentacao(
            conexao,
            b,
            importancia_id=importancia,
            importancia_vinculada_em=MOMENTO,
        ),
    )
    inserir_movimentacao(
        conexao,
        a,
        importancia_id=importancia,
        importancia_vinculada_em=MOMENTO,
    )


def test_fk_propriedade_lembrete_importancia(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    importancia = inserir_importancia(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_lembrete(conexao, b, importancia),
    )
    inserir_lembrete(conexao, a, importancia)


def test_fk_propriedade_notificacao_lembrete(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    importancia = inserir_importancia(conexao, a)
    lembrete = inserir_lembrete(conexao, a, importancia)
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_notificacao(conexao, b, lembrete),
    )
    inserir_notificacao(conexao, a, lembrete)


# CT-F2-12: categoria financeira compatível com o tipo


def test_fk_categoria_financeira_por_tipo(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    contas = id_categoria(conexao, "categoria_financeira", "Contas", "DESPESA")
    salario = id_categoria(
        conexao, "categoria_financeira", "Salário", "RECEITA"
    )
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_movimentacao(
            conexao, a, tipo="RECEITA", categoria_id=contas
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: inserir_movimentacao(
            conexao, a, tipo="DESPESA", categoria_id=salario
        ),
    )
    inserir_movimentacao(conexao, a, tipo="RECEITA", categoria_id=salario)
    outros_receita = id_categoria(
        conexao, "categoria_financeira", "Outros", "RECEITA"
    )
    outros_despesa = id_categoria(
        conexao, "categoria_financeira", "Outros", "DESPESA"
    )
    assert outros_receita != outros_despesa


# CT-F2-13: ocorrências de série


def test_ocorrencias_atividade(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    serie = inserir_serie_atividade(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_atividade(
            conexao, a, serie_id=serie, numero_ocorrencia=None
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_atividade(
            conexao, a, serie_id=None, numero_ocorrencia=1
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_atividade(
            conexao, a, serie_id=serie, numero_ocorrencia=0
        ),
    )
    inserir_atividade(conexao, a, serie_id=serie, numero_ocorrencia=1)
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_atividade(
            conexao, a, serie_id=serie, numero_ocorrencia=1
        ),
    )
    inserir_atividade(
        conexao, a, serie_id=serie, numero_ocorrencia=2, excluida_em=MOMENTO
    )
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_atividade(
            conexao, a, serie_id=serie, numero_ocorrencia=2
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_serie_atividade(conexao, a, numero_final=-1),
    )
    inserir_atividade(conexao, a)
    inserir_atividade(conexao, a)
    inserir_serie_atividade(conexao, a, numero_final=0)


def test_ocorrencias_importancia(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    serie = inserir_serie_importancia(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_importancia(
            conexao, a, serie_id=serie, numero_ocorrencia=None
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_importancia(
            conexao, a, serie_id=None, numero_ocorrencia=1
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_importancia(
            conexao, a, serie_id=serie, numero_ocorrencia=0
        ),
    )
    inserir_importancia(conexao, a, serie_id=serie, numero_ocorrencia=1)
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_importancia(
            conexao, a, serie_id=serie, numero_ocorrencia=1
        ),
    )
    inserir_importancia(
        conexao, a, serie_id=serie, numero_ocorrencia=2, excluida_em=MOMENTO
    )
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_importancia(
            conexao, a, serie_id=serie, numero_ocorrencia=2
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_serie_importancia(conexao, a, numero_final=-1),
    )
    inserir_importancia(conexao, a)
    inserir_importancia(conexao, a)
    inserir_serie_importancia(conexao, a, numero_final=0)


# CT-F2-14: condições financeiras


def test_valor_da_movimentacao(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    for invalido in (Decimal(0), Decimal("-0.01")):
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda invalido=invalido: inserir_movimentacao(
                conexao, a, valor=invalido
            ),
        )
    esperar_violacao(
        conexao,
        SQLSTATE_NOT_NULL,
        lambda: inserir_movimentacao(conexao, a, valor=None),
    )
    inserir_movimentacao(conexao, a, valor=Decimal("0.01"))


def test_valor_previsto_condicional(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    invalidos = (
        (False, Decimal(10)),
        (True, None),
        (True, Decimal(0)),
        (True, Decimal(-1)),
    )
    validos = ((True, PREVISTO), (False, None))
    for possui, valor in invalidos:
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda possui=possui, valor=valor: inserir_importancia(
                conexao, a, possui_despesa=possui, valor_previsto=valor
            ),
        )
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda possui=possui, valor=valor: inserir_serie_importancia(
                conexao,
                a,
                possui_despesa_padrao=possui,
                valor_previsto_padrao=valor,
            ),
        )
    for possui, valor in validos:
        inserir_importancia(
            conexao, a, possui_despesa=possui, valor_previsto=valor
        )
        inserir_serie_importancia(
            conexao,
            a,
            possui_despesa_padrao=possui,
            valor_previsto_padrao=valor,
        )


def test_vinculo_de_pagamento(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    importancia = _importancia_com_despesa(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_movimentacao(conexao, a, importancia_id=importancia),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_movimentacao(
            conexao, a, importancia_vinculada_em=MOMENTO
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_movimentacao(
            conexao,
            a,
            tipo="RECEITA",
            importancia_id=importancia,
            importancia_vinculada_em=MOMENTO,
        ),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_movimentacao(
            conexao,
            a,
            importancia_id=importancia,
            importancia_vinculada_em=MOMENTO,
            excluida_em=MOMENTO,
        ),
    )
    inserir_movimentacao(
        conexao,
        a,
        importancia_id=importancia,
        importancia_vinculada_em=MOMENTO,
    )
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_movimentacao(
            conexao,
            a,
            importancia_id=importancia,
            importancia_vinculada_em=MOMENTO,
        ),
    )
    inserir_movimentacao(conexao, a, excluida_em=MOMENTO)


# CT-F2-15: domínios


def test_forma_por_tipo(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    invalidos = (
        ("RECEITA", "CARTAO_DEBITO"),
        ("RECEITA", "BOLETO"),
        ("DESPESA", "DEPOSITO"),
        ("DESPESA", "CHEQUE"),
    )
    validos = (
        ("RECEITA", "PIX"),
        ("RECEITA", "DEPOSITO"),
        ("DESPESA", "BOLETO"),
        ("DESPESA", "CARTAO_DEBITO"),
        ("DESPESA", None),
        ("RECEITA", None),
    )
    for tipo, forma in invalidos:
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda tipo=tipo, forma=forma: inserir_movimentacao(
                conexao, a, tipo=tipo, forma_movimentacao=forma
            ),
        )
    for tipo, forma in validos:
        inserir_movimentacao(conexao, a, tipo=tipo, forma_movimentacao=forma)


def test_horarios(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    for inicial, final in (
        (time(10, 0), time(10, 0)),
        (time(10, 0), time(9, 0)),
    ):
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda inicial=inicial, final=final: inserir_atividade(
                conexao, a, horario_inicial=inicial, horario_final=final
            ),
        )
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda inicial=inicial, final=final: inserir_serie_atividade(
                conexao,
                a,
                horario_inicial_padrao=inicial,
                horario_final_padrao=final,
            ),
        )
    inserir_atividade(
        conexao, a, horario_inicial=time(8, 0), horario_final=time(8, 1)
    )
    inserir_serie_atividade(
        conexao,
        a,
        horario_inicial_padrao=time(8, 0),
        horario_final_padrao=time(8, 1),
    )


def test_datas_e_numeros_de_serie(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    referencia = date(2026, 10, 8)
    for fabrica in (inserir_serie_atividade, inserir_serie_importancia):
        for campos in (
            {"data_final_repeticao": date(2026, 10, 7)},
            {"numero_referencia": 0},
            {"numero_final": -1},
        ):
            esperar_violacao(
                conexao,
                SQLSTATE_CHECK,
                lambda fabrica=fabrica, campos=campos: fabrica(
                    conexao, a, data_referencia=referencia, **campos
                ),
            )
        fabrica(
            conexao,
            a,
            data_referencia=referencia,
            data_final_repeticao=referencia,
        )
        fabrica(conexao, a, numero_final=0)


def test_nome_da_atividade(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    for nome in ("ab", ""):
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda nome=nome: inserir_atividade(conexao, a, nome=nome),
        )
    esperar_violacao(
        conexao,
        SQLSTATE_NOT_NULL,
        lambda: inserir_atividade(conexao, a, nome=None),
    )
    esperar_violacao(
        conexao,
        SQLSTATE_TEXTO_LONGO,
        lambda: inserir_atividade(conexao, a, nome="x" * 101),
    )
    inserir_atividade(conexao, a, nome="abc")
    inserir_atividade(conexao, a, nome="x" * 100)


def test_enumeracoes_invalidas(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    contas = id_categoria(conexao, "categoria_financeira", "Contas", "DESPESA")
    importancia = inserir_importancia(conexao, a)
    invalidas = (
        lambda: inserir_atividade(conexao, a, prioridade="ALTO"),
        lambda: inserir_atividade(conexao, a, prioridade="baixa"),
        lambda: inserir_serie_atividade(conexao, a, prioridade_padrao="ALTO"),
        lambda: inserir_serie_atividade(conexao, a, periodicidade="ANUAL"),
        lambda: inserir_serie_importancia(conexao, a, periodicidade="SEMANA"),
        lambda: inserir(
            conexao,
            "categoria_financeira",
            {"id": uuid.uuid7(), "nome": "Teste", "tipo": "OUTRO"},
        ),
        lambda: inserir_movimentacao(
            conexao, a, tipo="OUTRO", categoria_id=contas
        ),
        lambda: inserir_lembrete(conexao, a, importancia, situacao="LIDO"),
        lambda: inserir_requisicao(conexao, a, situacao="PARADA"),
    )
    for acao in invalidas:
        esperar_violacao(conexao, SQLSTATE_CHECK, acao)
    inserir_serie_importancia(conexao, a, periodicidade="ANUAL")
    inserir_atividade(conexao, a, prioridade="ALTA")


def test_antecedencias(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    importancia = inserir_importancia(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_lembrete(conexao, a, importancia, antecedencia_dias=2),
    )
    invalidas = (
        (5, time(9, 0)),
        (3, None),
        (None, time(9, 0)),
    )
    for dias, horario in invalidas:
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda dias=dias, horario=horario: inserir_serie_importancia(
                conexao,
                a,
                lembrete_antecedencia_dias=dias,
                lembrete_horario=horario,
            ),
        )
    for dias in (0, 1, 3, 7):
        inserir_lembrete(
            conexao,
            a,
            inserir_importancia(conexao, a),
            antecedencia_dias=dias,
        )
    inserir_serie_importancia(
        conexao, a, lembrete_antecedencia_dias=None, lembrete_horario=None
    )
    inserir_serie_importancia(
        conexao,
        a,
        lembrete_antecedencia_dias=7,
        lembrete_horario=time(9, 0),
    )


def test_situacao_e_envio_do_lembrete(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    importancia = inserir_importancia(conexao, a)
    invalidos = (
        ("ENVIADO", None),
        ("PENDENTE", MOMENTO),
        ("CANCELADO", MOMENTO),
    )
    for situacao, enviado_em in invalidos:
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda situacao=situacao, enviado_em=enviado_em: inserir_lembrete(
                conexao,
                a,
                importancia,
                situacao=situacao,
                enviado_em=enviado_em,
            ),
        )
    inserir_lembrete(
        conexao,
        a,
        inserir_importancia(conexao, a),
        situacao="ENVIADO",
        enviado_em=MOMENTO,
    )
    inserir_lembrete(
        conexao,
        a,
        inserir_importancia(conexao, a),
        situacao="CANCELADO",
        enviado_em=None,
    )


def test_conclusao_manual(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    esperar_violacao(
        conexao,
        SQLSTATE_CHECK,
        lambda: inserir_importancia(
            conexao,
            a,
            possui_despesa=True,
            valor_previsto=Decimal(10),
            concluida_manualmente_em=MOMENTO,
        ),
    )
    inserir_importancia(
        conexao, a, possui_despesa=False, concluida_manualmente_em=MOMENTO
    )


# CT-F2-16: unicidades de apoio


def test_email_unico(conexao: Connection) -> None:
    inserir_usuario(conexao, email="mesmo@exemplo.com")
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_usuario(conexao, email="mesmo@exemplo.com"),
    )
    inserir_usuario(conexao, email="outro@exemplo.com")


def test_recuperacao_unica_por_usuario(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    inserir_recuperacao(conexao, a)
    esperar_violacao(
        conexao, SQLSTATE_UNICO, lambda: inserir_recuperacao(conexao, a)
    )
    inserir_recuperacao(conexao, b)


def test_token_redefinicao_unico(conexao: Connection) -> None:
    token = "a" * 64
    primeiro = inserir_usuario(conexao)
    segundo = inserir_usuario(conexao)
    inserir_recuperacao(conexao, primeiro, token_redefinicao_hash=token)
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_recuperacao(
            conexao, segundo, token_redefinicao_hash=token
        ),
    )
    inserir_recuperacao(conexao, segundo, token_redefinicao_hash=None)
    terceiro = inserir_usuario(conexao)
    inserir_recuperacao(conexao, terceiro, token_redefinicao_hash=None)


def test_lembrete_unico_por_importancia(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    importancia = inserir_importancia(conexao, a)
    inserir_lembrete(conexao, a, importancia)
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_lembrete(conexao, a, importancia),
    )


def test_notificacao_por_versao(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    importancia = inserir_importancia(conexao, a)
    lembrete = inserir_lembrete(conexao, a, importancia)
    inserir_notificacao(conexao, a, lembrete, versao_agendamento=1)
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_notificacao(
            conexao, a, lembrete, versao_agendamento=1
        ),
    )
    conexao.execute(
        text(
            "UPDATE lembrete_importancia SET versao_agendamento = 2 "
            "WHERE id = :id"
        ),
        {"id": lembrete},
    )
    inserir_notificacao(conexao, a, lembrete, versao_agendamento=2)
    total = conexao.execute(
        text("SELECT count(*) FROM notificacao WHERE lembrete_id = :id"),
        {"id": lembrete},
    ).scalar_one()
    assert total == 2


def test_idempotencia_por_usuario_acao_chave(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    b = inserir_usuario(conexao)
    chave = uuid.uuid7().hex
    inserir_requisicao(conexao, a, acao="CADASTRAR_DESPESA", chave=chave)
    esperar_violacao(
        conexao,
        SQLSTATE_UNICO,
        lambda: inserir_requisicao(
            conexao, a, acao="CADASTRAR_DESPESA", chave=chave
        ),
    )
    inserir_requisicao(conexao, a, acao="CADASTRAR_RECEITA", chave=chave)
    inserir_requisicao(conexao, b, acao="CADASTRAR_DESPESA", chave=chave)


# CT-F2-18 (b): categoria referenciada não pode ser excluída


def test_exclusao_fisica_de_categoria_referenciada(
    conexao: Connection,
) -> None:
    a = inserir_usuario(conexao)
    inserir_atividade(conexao, a)
    esperar_violacao(
        conexao,
        SQLSTATE_FK,
        lambda: conexao.execute(
            text("DELETE FROM categoria_atividade WHERE nome = 'Estudo'")
        ),
    )


# CT-F2-20: CHECKs de nome (DEC-MV-08)


def test_nomes_dec_mv_08(conexao: Connection) -> None:
    a = inserir_usuario(conexao)
    for nome in ("ab", ""):
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda nome=nome: inserir_importancia(conexao, a, nome=nome),
        )
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda nome=nome: inserir_movimentacao(conexao, a, nome=nome),
        )
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda nome=nome: inserir_serie_atividade(
                conexao, a, nome_padrao=nome
            ),
        )
        esperar_violacao(
            conexao,
            SQLSTATE_CHECK,
            lambda nome=nome: inserir_serie_importancia(
                conexao, a, nome_padrao=nome
            ),
        )
    inserir_importancia(conexao, a, nome="abc")
    inserir_movimentacao(conexao, a, nome="abc")
    inserir_serie_atividade(conexao, a, nome_padrao="abc")
    inserir_serie_importancia(conexao, a, nome_padrao="abc")
