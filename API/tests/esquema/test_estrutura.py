from sqlalchemy import Connection, text

from api_gestao_pessoal.models import Base

UUID = "uuid"
TS = "timestamp with time zone"
HORA = "time without time zone"
DATA = "date"
INTEIRO = "integer"
PEQUENO = "smallint"
BOOLEANO = "boolean"
DINHEIRO = "numeric(12,2)"
AGORA = "now()"
V5 = "character varying(5)"
V7 = "character varying(7)"
V10 = "character varying(10)"
V20 = "character varying(20)"
V50 = "character varying(50)"
V64 = "character varying(64)"
V100 = "character varying(100)"
V120 = "character varying(120)"
V150 = "character varying(150)"
V200 = "character varying(200)"
V254 = "character varying(254)"
V255 = "character varying(255)"
V500 = "character varying(500)"
BAIXA = "'BAIXA'::character varying"

# (coluna, tipo, obrigatória, padrão), na ordem das colunas de cada tabela.
COLUNAS_ESPERADAS: dict[str, tuple[tuple[str, str, bool, str | None], ...]] = {
    "usuario": (
        ("id", UUID, True, None),
        ("nome_completo", V150, True, None),
        ("email", V254, True, None),
        ("senha_hash", V255, True, None),
        ("data_nascimento", DATA, True, None),
        ("fuso_horario", V64, True, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "recuperacao_senha": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("codigo_hash", V255, True, None),
        ("expira_em", TS, True, None),
        ("tentativas", INTEIRO, True, "0"),
        ("verificado_em", TS, False, None),
        ("token_redefinicao_hash", V64, False, None),
        ("utilizado_em", TS, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "categoria_atividade": (
        ("id", UUID, True, None),
        ("nome", V50, True, None),
        ("ativa", BOOLEANO, True, "true"),
    ),
    "serie_atividade": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("categoria_id", UUID, True, None),
        ("nome_padrao", V100, True, None),
        ("descricao_padrao", V200, False, None),
        ("prioridade_padrao", V5, True, BAIXA),
        ("periodicidade", V10, True, None),
        ("data_referencia", DATA, True, None),
        ("numero_referencia", INTEIRO, True, "1"),
        ("horario_inicial_padrao", HORA, True, None),
        ("horario_final_padrao", HORA, True, None),
        ("data_final_repeticao", DATA, False, None),
        ("numero_final", INTEIRO, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "atividade": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("categoria_id", UUID, True, None),
        ("serie_id", UUID, False, None),
        ("numero_ocorrencia", INTEIRO, False, None),
        ("nome", V100, True, None),
        ("descricao", V200, False, None),
        ("prioridade", V5, True, BAIXA),
        ("data_atividade", DATA, True, None),
        ("horario_inicial", HORA, True, None),
        ("horario_final", HORA, True, None),
        ("concluida_em", TS, False, None),
        ("excluida_em", TS, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "categoria_importancia": (
        ("id", UUID, True, None),
        ("nome", V50, True, None),
        ("ativa", BOOLEANO, True, "true"),
    ),
    "serie_importancia": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("categoria_id", UUID, True, None),
        ("nome_padrao", V100, True, None),
        ("descricao_padrao", V200, False, None),
        ("periodicidade", V10, True, None),
        ("data_referencia", DATA, True, None),
        ("numero_referencia", INTEIRO, True, "1"),
        ("horario_padrao", HORA, False, None),
        ("data_final_repeticao", DATA, False, None),
        ("numero_final", INTEIRO, False, None),
        ("possui_despesa_padrao", BOOLEANO, True, "false"),
        ("valor_previsto_padrao", DINHEIRO, False, None),
        ("lembrete_antecedencia_dias", PEQUENO, False, None),
        ("lembrete_horario", HORA, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "importancia": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("categoria_id", UUID, True, None),
        ("serie_id", UUID, False, None),
        ("numero_ocorrencia", INTEIRO, False, None),
        ("nome", V100, True, None),
        ("descricao", V200, False, None),
        ("data_compromisso", DATA, True, None),
        ("horario", HORA, False, None),
        ("possui_despesa", BOOLEANO, True, "false"),
        ("valor_previsto", DINHEIRO, False, None),
        ("concluida_manualmente_em", TS, False, None),
        ("excluida_em", TS, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "categoria_financeira": (
        ("id", UUID, True, None),
        ("nome", V50, True, None),
        ("tipo", V7, True, None),
        ("ativa", BOOLEANO, True, "true"),
    ),
    "movimentacao_financeira": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("categoria_id", UUID, True, None),
        ("tipo", V7, True, None),
        ("nome", V100, True, None),
        ("descricao", V200, False, None),
        ("valor", DINHEIRO, True, None),
        ("data_movimentacao", DATA, True, None),
        ("contraparte", V100, False, None),
        ("forma_movimentacao", V20, False, None),
        ("importancia_id", UUID, False, None),
        ("importancia_vinculada_em", TS, False, None),
        ("excluida_em", TS, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "lembrete_importancia": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("importancia_id", UUID, True, None),
        ("antecedencia_dias", PEQUENO, True, None),
        ("horario", HORA, True, None),
        ("agendado_para", TS, True, None),
        ("versao_agendamento", INTEIRO, True, "1"),
        ("situacao", V10, True, "'PENDENTE'::character varying"),
        ("enviado_em", TS, False, None),
        ("criado_em", TS, True, AGORA),
        ("atualizado_em", TS, True, AGORA),
    ),
    "notificacao": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("lembrete_id", UUID, True, None),
        ("versao_agendamento", INTEIRO, True, None),
        ("titulo", V120, True, None),
        ("mensagem", V500, True, None),
        ("criada_em", TS, True, AGORA),
        ("lida_em", TS, False, None),
    ),
    "requisicao_idempotente": (
        ("id", UUID, True, None),
        ("usuario_id", UUID, True, None),
        ("chave", V64, True, None),
        ("acao", V50, True, None),
        ("conteudo_hash", V64, True, None),
        ("situacao", V20, True, "'EM_PROCESSAMENTO'::character varying"),
        ("codigo_resposta", PEQUENO, False, None),
        ("resposta", "json", False, None),
        ("criado_em", TS, True, AGORA),
        ("concluida_em", TS, False, None),
    ),
}

COLUNAS_UUID = {
    ("usuario", "id"),
    ("recuperacao_senha", "id"),
    ("recuperacao_senha", "usuario_id"),
    ("categoria_atividade", "id"),
    ("serie_atividade", "id"),
    ("serie_atividade", "usuario_id"),
    ("serie_atividade", "categoria_id"),
    ("atividade", "id"),
    ("atividade", "usuario_id"),
    ("atividade", "categoria_id"),
    ("atividade", "serie_id"),
    ("categoria_importancia", "id"),
    ("serie_importancia", "id"),
    ("serie_importancia", "usuario_id"),
    ("serie_importancia", "categoria_id"),
    ("importancia", "id"),
    ("importancia", "usuario_id"),
    ("importancia", "categoria_id"),
    ("importancia", "serie_id"),
    ("categoria_financeira", "id"),
    ("movimentacao_financeira", "id"),
    ("movimentacao_financeira", "usuario_id"),
    ("movimentacao_financeira", "categoria_id"),
    ("movimentacao_financeira", "importancia_id"),
    ("lembrete_importancia", "id"),
    ("lembrete_importancia", "usuario_id"),
    ("lembrete_importancia", "importancia_id"),
    ("notificacao", "id"),
    ("notificacao", "usuario_id"),
    ("notificacao", "lembrete_id"),
    ("requisicao_idempotente", "id"),
    ("requisicao_idempotente", "usuario_id"),
}

NOMES_ESPERADOS = {
    # usuario
    "pk_usuario",
    "uq_usuario_email",
    # recuperacao_senha
    "fk_recuperacao_senha_usuario_id_usuario",
    "pk_recuperacao_senha",
    "uq_recuperacao_senha_token_redefinicao_hash",
    "uq_recuperacao_senha_usuario_id",
    # categoria_atividade
    "pk_categoria_atividade",
    "uq_categoria_atividade_nome",
    # serie_atividade
    "ck_serie_atividade_data_final",
    "ck_serie_atividade_horarios",
    "ck_serie_atividade_nome_padrao_tamanho",
    "ck_serie_atividade_numero_final",
    "ck_serie_atividade_numero_referencia",
    "ck_serie_atividade_periodicidade",
    "ck_serie_atividade_prioridade_padrao",
    "fk_serie_atividade_categoria_id_categoria_atividade",
    "fk_serie_atividade_usuario_id_usuario",
    "pk_serie_atividade",
    "uq_serie_atividade_id_usuario_id",
    # atividade
    "ck_atividade_horarios",
    "ck_atividade_nome_tamanho",
    "ck_atividade_prioridade",
    "ck_atividade_serie_numero",
    "fk_atividade_categoria_id_categoria_atividade",
    "fk_atividade_serie_id_serie_atividade",
    "fk_atividade_usuario_id_usuario",
    "ix_atividade_usuario_concluida_data",
    "ix_atividade_usuario_data",
    "pk_atividade",
    "uq_atividade_serie_id_numero_ocorrencia",
    # categoria_importancia
    "pk_categoria_importancia",
    "uq_categoria_importancia_nome",
    # serie_importancia
    "ck_serie_importancia_data_final",
    "ck_serie_importancia_lembrete_antecedencia",
    "ck_serie_importancia_lembrete_par",
    "ck_serie_importancia_nome_padrao_tamanho",
    "ck_serie_importancia_numero_final",
    "ck_serie_importancia_numero_referencia",
    "ck_serie_importancia_periodicidade",
    "ck_serie_importancia_valor_previsto",
    "fk_serie_importancia_categoria_id_categoria_importancia",
    "fk_serie_importancia_usuario_id_usuario",
    "pk_serie_importancia",
    "uq_serie_importancia_id_usuario_id",
    # importancia
    "ck_importancia_conclusao_manual",
    "ck_importancia_nome_tamanho",
    "ck_importancia_serie_numero",
    "ck_importancia_valor_previsto",
    "fk_importancia_categoria_id_categoria_importancia",
    "fk_importancia_serie_id_serie_importancia",
    "fk_importancia_usuario_id_usuario",
    "ix_importancia_usuario_data",
    "pk_importancia",
    "uq_importancia_id_usuario_id",
    "uq_importancia_serie_id_numero_ocorrencia",
    # categoria_financeira
    "ck_categoria_financeira_tipo",
    "pk_categoria_financeira",
    "uq_categoria_financeira_id_tipo",
    "uq_categoria_financeira_tipo_nome",
    # movimentacao_financeira
    "ck_movimentacao_financeira_excluida_sem_vinculo",
    "ck_movimentacao_financeira_forma_movimentacao",
    "ck_movimentacao_financeira_forma_tipo",
    "ck_movimentacao_financeira_nome_tamanho",
    "ck_movimentacao_financeira_tipo",
    "ck_movimentacao_financeira_valor_positivo",
    "ck_movimentacao_financeira_vinculo_despesa",
    "ck_movimentacao_financeira_vinculo_par",
    "fk_movimentacao_financeira_categoria_id_categoria_financeira",
    "fk_movimentacao_financeira_importancia_id_importancia",
    "fk_movimentacao_financeira_usuario_id_usuario",
    "ix_movimentacao_usuario_categoria_data",
    "ix_movimentacao_usuario_data",
    "ix_movimentacao_usuario_tipo_data",
    "pk_movimentacao_financeira",
    "uq_movimentacao_financeira_importancia_id",
    # lembrete_importancia
    "ck_lembrete_importancia_antecedencia",
    "ck_lembrete_importancia_enviado",
    "ck_lembrete_importancia_situacao",
    "fk_lembrete_importancia_importancia_id_importancia",
    "fk_lembrete_importancia_usuario_id_usuario",
    "ix_lembrete_situacao_agendado",
    "pk_lembrete_importancia",
    "uq_lembrete_importancia_id_usuario_id",
    "uq_lembrete_importancia_importancia_id",
    # notificacao
    "fk_notificacao_lembrete_id_lembrete_importancia",
    "fk_notificacao_usuario_id_usuario",
    "ix_notificacao_usuario_lida_criada",
    "pk_notificacao",
    "uq_notificacao_lembrete_id_versao_agendamento",
    # requisicao_idempotente
    "ck_requisicao_idempotente_situacao",
    "fk_requisicao_idempotente_usuario_id_usuario",
    "pk_requisicao_idempotente",
    "uq_requisicao_idempotente_usuario_id_acao_chave",
}

INDICES_ESPERADOS = {
    (
        "ix_atividade_usuario_data",
        "atividade",
        (
            "usuario_id",
            "data_atividade",
        ),
    ),
    (
        "ix_atividade_usuario_concluida_data",
        "atividade",
        (
            "usuario_id",
            "concluida_em",
            "data_atividade",
        ),
    ),
    (
        "ix_importancia_usuario_data",
        "importancia",
        (
            "usuario_id",
            "data_compromisso",
        ),
    ),
    (
        "ix_movimentacao_usuario_data",
        "movimentacao_financeira",
        (
            "usuario_id",
            "data_movimentacao",
        ),
    ),
    (
        "ix_movimentacao_usuario_tipo_data",
        "movimentacao_financeira",
        (
            "usuario_id",
            "tipo",
            "data_movimentacao",
        ),
    ),
    (
        "ix_movimentacao_usuario_categoria_data",
        "movimentacao_financeira",
        (
            "usuario_id",
            "categoria_id",
            "data_movimentacao",
        ),
    ),
    (
        "ix_lembrete_situacao_agendado",
        "lembrete_importancia",
        (
            "situacao",
            "agendado_para",
        ),
    ),
    (
        "ix_notificacao_usuario_lida_criada",
        "notificacao",
        (
            "usuario_id",
            "lida_em",
            "criada_em",
        ),
    ),
}

CONSULTA_COLUNAS = text(
    "SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod), "
    "a.attnotnull, pg_get_expr(d.adbin, d.adrelid) "
    "FROM pg_attribute a "
    "JOIN pg_class c ON c.oid = a.attrelid "
    "JOIN pg_namespace n ON n.oid = c.relnamespace "
    "LEFT JOIN pg_attrdef d "
    "ON d.adrelid = a.attrelid AND d.adnum = a.attnum "
    "WHERE n.nspname = 'public' AND c.relkind = 'r' "
    "AND c.relname <> 'alembic_version' "
    "AND a.attnum > 0 AND NOT a.attisdropped "
    "ORDER BY c.relname, a.attnum"
)

CONSULTA_NOMES = text(
    "SELECT con.conname FROM pg_constraint con "
    "JOIN pg_class t ON t.oid = con.conrelid "
    "WHERE t.relnamespace = 'public'::regnamespace "
    "AND t.relname <> 'alembic_version' "
    "UNION ALL "
    "SELECT i.relname FROM pg_index x "
    "JOIN pg_class i ON i.oid = x.indexrelid "
    "JOIN pg_class t ON t.oid = x.indrelid "
    "WHERE t.relnamespace = 'public'::regnamespace "
    "AND t.relname <> 'alembic_version' "
    "AND NOT EXISTS (SELECT 1 FROM pg_constraint c "
    "WHERE c.conindid = x.indexrelid)"
)

CONSULTA_INDICES = text(
    "SELECT i.relname, t.relname, array_agg(a.attname ORDER BY k.ordem) "
    "FROM pg_index x "
    "JOIN pg_class i ON i.oid = x.indexrelid "
    "JOIN pg_class t ON t.oid = x.indrelid "
    "CROSS JOIN LATERAL unnest(x.indkey::int2[]) "
    "WITH ORDINALITY AS k(attnum, ordem) "
    "JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum "
    "WHERE i.relname LIKE 'ix\\_%' "
    "GROUP BY i.relname, t.relname"
)


def test_colunas_conforme_contrato(conexao: Connection) -> None:
    linhas = conexao.execute(CONSULTA_COLUNAS).all()
    reais: dict[str, list[tuple[str, str, bool, str | None]]] = {}
    for tabela, coluna, tipo, obrigatoria, padrao in linhas:
        reais.setdefault(tabela, []).append((
            coluna,
            tipo,
            obrigatoria,
            padrao,
        ))
    assert len(COLUNAS_ESPERADAS) == 13
    assert sum(len(c) for c in COLUNAS_ESPERADAS.values()) == 134
    assert set(reais) == set(COLUNAS_ESPERADAS)
    for tabela, esperadas in COLUNAS_ESPERADAS.items():
        assert reais[tabela] == list(esperadas), tabela


def test_identificadores_uuid_sem_padrao(conexao: Connection) -> None:
    linhas = conexao.execute(CONSULTA_COLUNAS).all()
    uuids = {(r[0], r[1]) for r in linhas if r[2] == "uuid"}
    assert len(uuids) == 32
    assert uuids == COLUNAS_UUID
    assert all(r[4] is None for r in linhas if r[2] == "uuid")
    chaves = conexao.execute(
        text(
            "SELECT c.relname, array_agg(a.attname) FROM pg_constraint con "
            "JOIN pg_class c ON c.oid = con.conrelid "
            "JOIN pg_attribute a "
            "ON a.attrelid = c.oid AND a.attnum = ANY (con.conkey) "
            "WHERE con.contype = 'p' "
            "AND con.connamespace = 'public'::regnamespace "
            "AND c.relname <> 'alembic_version' "
            "GROUP BY c.relname"
        )
    ).all()
    assert {r[0]: r[1] for r in chaves} == {
        tabela: ["id"] for tabela in COLUNAS_ESPERADAS
    }


def test_nomes_de_restricoes_e_indices(conexao: Connection) -> None:
    nomes_banco = [r[0] for r in conexao.execute(CONSULTA_NOMES).all()]
    assert len(nomes_banco) == len(set(nomes_banco)) == 93
    assert set(nomes_banco) == NOMES_ESPERADOS
    nomes_metadata = {
        str(c.name)
        for t in Base.metadata.tables.values()
        for c in t.constraints
    } | {str(i.name) for t in Base.metadata.tables.values() for i in t.indexes}
    assert nomes_metadata == NOMES_ESPERADOS
    assert len(NOMES_ESPERADOS) == 93
    assert max(len(nome) for nome in nomes_banco) <= 63
    indices = {
        (r[0], r[1], tuple(r[2]))
        for r in conexao.execute(CONSULTA_INDICES).all()
    }
    assert len(indices) == 8
    assert indices == INDICES_ESPERADOS


def test_fks_restrict(conexao: Connection) -> None:
    linhas = conexao.execute(
        text(
            "SELECT conname, confdeltype FROM pg_constraint "
            "WHERE contype = 'f' AND connamespace = 'public'::regnamespace"
        )
    ).all()
    assert len(linhas) == 19
    assert {r[1] for r in linhas} == {"r"}
