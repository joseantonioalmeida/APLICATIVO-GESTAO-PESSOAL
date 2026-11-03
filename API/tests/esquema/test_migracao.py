from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, text

from alembic import command

from ..apoio.esquema import consultar
from ..apoio.migracoes import REVISAO_INICIAL

TABELAS_DOMINIO = {
    "usuario",
    "recuperacao_senha",
    "categoria_atividade",
    "serie_atividade",
    "atividade",
    "categoria_importancia",
    "serie_importancia",
    "importancia",
    "categoria_financeira",
    "movimentacao_financeira",
    "lembrete_importancia",
    "notificacao",
    "requisicao_idempotente",
}
CATEGORIAS_ATIVIDADE = [
    "Trabalho",
    "Estudo",
    "Saúde",
    "Pessoal",
    "Lazer",
    "Outros",
]
CATEGORIAS_IMPORTANCIA = [
    "Contas",
    "Compras",
    "Veículo",
    "Lazer",
    "Saúde",
    "Educação",
    "Pessoal",
    "Outros",
]
CATEGORIAS_RECEITA = [
    "Salário",
    "Trabalho autônomo",
    "Vendas",
    "Rendimentos",
    "Reembolsos",
    "Outros",
]
CATEGORIAS_DESPESA = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Contas",
    "Compras",
    "Saúde",
    "Educação",
    "Lazer",
    "Veículo",
    "Outros",
]


def _tabelas(url: str) -> set[str]:
    linhas = consultar(
        url, "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    )
    return {linha[0] for linha in linhas}


def _contagens(url: str) -> tuple[int, int, int]:
    atividade = consultar(url, "SELECT count(*) FROM categoria_atividade")
    importancia = consultar(url, "SELECT count(*) FROM categoria_importancia")
    financeira = consultar(url, "SELECT count(*) FROM categoria_financeira")
    return atividade[0][0], importancia[0][0], financeira[0][0]


def _contagens_na_conexao(conexao: Connection) -> tuple[int, int, int]:
    resultado: list[int] = []
    for tabela in (
        "categoria_atividade",
        "categoria_importancia",
        "categoria_financeira",
    ):
        consulta = text(f"SELECT count(*) FROM {tabela}")
        resultado.append(conexao.execute(consulta).scalar_one())
    return resultado[0], resultado[1], resultado[2]


def test_upgrade_head_cria_esquema_em_banco_vazio(
    config_migracao: Config, banco_migrado: str
) -> None:
    try:
        command.downgrade(config_migracao, "base")
        assert _tabelas(banco_migrado) == {"alembic_version"}
        command.upgrade(config_migracao, "head")
        assert _tabelas(banco_migrado) == TABELAS_DOMINIO | {"alembic_version"}
        versoes = consultar(
            banco_migrado, "SELECT version_num FROM alembic_version"
        )
        assert versoes == [(REVISAO_INICIAL,)]
    finally:
        command.upgrade(config_migracao, "head")


def test_categorias_iniciais_exatas(conexao: Connection) -> None:
    atividade = conexao.execute(
        text("SELECT nome FROM categoria_atividade")
    ).scalars()
    assert sorted(atividade) == sorted(CATEGORIAS_ATIVIDADE)
    importancia = conexao.execute(
        text("SELECT nome FROM categoria_importancia")
    ).scalars()
    assert sorted(importancia) == sorted(CATEGORIAS_IMPORTANCIA)
    financeiras = conexao.execute(
        text("SELECT tipo, nome FROM categoria_financeira")
    ).all()
    assert sorted((linha[0], linha[1]) for linha in financeiras) == sorted(
        [("RECEITA", nome) for nome in CATEGORIAS_RECEITA]
        + [("DESPESA", nome) for nome in CATEGORIAS_DESPESA]
    )
    total = conexao.execute(
        text(
            "SELECT count(*), count(*) FILTER (WHERE ativa) FROM ("
            "SELECT ativa FROM categoria_atividade UNION ALL "
            "SELECT ativa FROM categoria_importancia UNION ALL "
            "SELECT ativa FROM categoria_financeira) t"
        )
    ).one()
    assert tuple(total) == (30, 30)
    outros = conexao.execute(
        text("SELECT id FROM categoria_financeira WHERE nome = 'Outros'")
    ).scalars()
    assert len(set(outros)) == 2


def test_seeds_idempotentes(
    config_migracao: Config, banco_migrado: str, conexao: Connection
) -> None:
    command.upgrade(config_migracao, "head")
    versoes = consultar(
        banco_migrado, "SELECT version_num FROM alembic_version"
    )
    assert versoes == [(REVISAO_INICIAL,)]
    assert _contagens(banco_migrado) == (6, 8, 16)

    script = ScriptDirectory.from_config(config_migracao).get_revision(
        REVISAO_INICIAL
    )
    for instrucao in script.module.instrucoes_categorias():
        conexao.execute(instrucao)
    assert _contagens_na_conexao(conexao) == (6, 8, 16)

    codigo = Path(script.path).read_text(encoding="utf-8")
    assert "api_gestao_pessoal" not in codigo


def test_downgrade_base_e_upgrade_head(
    config_migracao: Config, banco_migrado: str
) -> None:
    try:
        command.downgrade(config_migracao, "base")
        assert _tabelas(banco_migrado) == {"alembic_version"}
        linhas = consultar(
            banco_migrado, "SELECT count(*) FROM alembic_version"
        )
        assert linhas == [(0,)]
        command.upgrade(config_migracao, "head")
        assert _tabelas(banco_migrado) == TABELAS_DOMINIO | {"alembic_version"}
        versoes = consultar(
            banco_migrado, "SELECT version_num FROM alembic_version"
        )
        assert versoes == [(REVISAO_INICIAL,)]
        assert _contagens(banco_migrado) == (6, 8, 16)
    finally:
        command.upgrade(config_migracao, "head")


def test_alembic_check_sem_diferencas(config_migracao: Config) -> None:
    command.check(config_migracao)
