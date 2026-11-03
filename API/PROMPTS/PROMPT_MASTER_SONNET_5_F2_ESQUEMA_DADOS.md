# Prompt Master — Sonnet 5 — F2: Esquema de dados da API MinhaVida

| Campo | Valor |
| --- | --- |
| Fase | F2 — Esquema de dados (`docs/arquitetura/plano_fases_api.md`) |
| Estado | **Executado.** F2 **`APROVADO_COM_P3`** na auditoria de 2026-10-13 (`docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`). A versão implementada tem SHA-256 `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c`; as notas de emenda e de errata em §12 e §13 foram acrescentadas depois da auditoria, sem alterar o texto original. Histórico: `PRONTO_PARA_ETAPA_A` em 2026-10-13 |
| Data | 2026-10-13. Estado e notas pós-auditoria acrescentados em 2026-10-13 (`docs/arquitetura/indice.md` §4, M13) |
| Autor | Claude Opus 5.5 (arquitetura) |
| Destinatário | Claude Sonnet 5 (implementação) |
| Baseline de código | Commit `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30` (F1 integrada, G6) |

> **Condições de liberação (2026-10-13).**
>
> 1. **Decisões: satisfeitas.** O usuário aprovou em 2026-10-13: DEC-MV-06 (ADR-0002, agora ACEITO), o restante da DEC-MV-07 (ADR-0001 D-09, agora aceita integralmente), DEC-MV-08 e a opção A do ACH-MV-F1-005. Registro em `docs/arquitetura/indice.md` §4 (M10). O `CLAUDE.md` já foi atualizado.
> 2. **Baseline: definido.** Código no commit `90412ec`. Por cima dele há somente as alterações documentais de preparação listadas em §1.2, autorizadas pelo usuário.
> 3. **Implementação: não autorizada.** Execute **somente a Etapa A** (§12) e aguarde a resposta “pode implementar” do usuário.

---

## 0. Regras absolutas e modo LOCAL/CLOUD

1. Comunicação, comentários e documentação em **PT-BR**. Funções, variáveis e arquivos em `snake_case`; classes em `PascalCase`.
2. **Você não toma decisões arquiteturais.** Tudo o que este prompt fixa deve ser seguido literalmente.
   - Lacuna arquitetural ou divergência entre este prompt e o repositório: **pare no ponto afetado**, descreva-a e devolva ao Opus.
   - Mudança de contrato ou de escopo: devolva ao usuário.
   - Não “escolha a melhor abordagem” onde o prompt já decidiu.
3. Nesta fase não há services nem routers novos. **Nenhum código de `src/` chama `commit()`.** Nos testes, além dos comandos do Alembic (que confirmam o próprio DDL), somente CT-F2-19 confirma transações (§10.5).
4. Modo padrão: **LOCAL**.

   | Ação | LOCAL | CLOUD (somente se a sessão for identificada explicitamente como Cloud e houver autorização de implementação) |
   | --- | --- | --- |
   | Implementar o escopo aprovado | Sim | Sim, na branch da sessão |
   | `git add`, `git commit` | **Proibido** | Somente na branch da sessão |
   | `git push` | Não por iniciativa própria | Somente da branch da sessão |
   | Pull Request | Não presumir | Somente **draft** |
   | Alterar `main`, merge, force-push, proteção de branch | Proibido | Proibido |
   | Declarar a fase aprovada | Proibido | Proibido |

   Remote Git ou Docker não caracterizam Cloud. No modo Cloud, você entrega branch, SHA, diff, PR draft e evidências, e **para**. A auditoria é local, feita pelo Opus sobre o mesmo SHA, e o merge é decisão do usuário.
5. Não use `git reset`, `git clean`, `git checkout -- .`, `git restore`, `git stash` nem nada que descarte trabalho. Preserve as alterações documentais de preparação (§1.2).
6. **`.env`:** não leia, não copie, não imprima, não calcule hash e não edite. Consequências práticas:
   - **Proibido** rodar pela CLI qualquer comando do Alembic que execute o `alembic/env.py`: `upgrade`, `downgrade`, `check`, `current`, `stamp`, `revision --autogenerate` e qualquer comando com `--sql`. Sem `config.attributes["url_banco"]`, o `env.py` leria `DATABASE_URL` do `.env` e poderia conectar ao banco de desenvolvimento. Pela CLI, só `uv run alembic heads` e `uv run alembic history`, que não executam o `env.py`.
   - Migrações, checagens e o autogenerate rodam **somente** pela API do Alembic, com a URL de um container descartável (§8.1 e §10).
   - Docker Compose: somente o comando de §13, passo 15, com `--env-file /dev/null`. Nunca `docker compose up` ou `down`.
   - Nunca conecte ao banco de desenvolvimento.
7. Não execute a suíte completa, `task test`, `task` de qualquer tipo, nem `pytest` sem a seleção definida em §13.
8. **Comandos literais e logs preservados (lição da F1):**
   - execute cada comando de §13 **exatamente** como escrito, sem trocar opções nem caminhos;
   - grave a saída completa (stdout e stderr) no arquivo de log indicado, em `$HOME/minhavida_evidencias/f2/`, **fora do repositório**, com o código de saída na última linha;
   - não edite, não resuma e não apague logs. Uma nova execução do mesmo passo vai para um log novo, com sufixo `_2`, `_3`, e assim por diante;
   - o relatório (§14) copia literalmente as linhas finais de cada log. Não parafraseie números, contagens nem mensagens.
9. Proibidos: `create_all`, `drop_all`, `stamp`, `relationship()`, triggers, extensões do PostgreSQL e `server_default` em colunas `id`.

## 1. Estado de partida: baseline de código e alterações documentais de preparação

São duas coisas diferentes, e o relatório deve tratá-las separadamente:

- o **baseline de código** é o commit `90412ec`, com a F1 integrada (§1.1);
- as **alterações documentais de preparação** são as mudanças em documentos que o usuário autorizou o Opus a fazer em 2026-10-13 para preparar a F2 (§1.2). Elas **não** são implementação, **não** fazem parte do objeto da F2 e você **não** as altera.

### 1.1. Baseline de código (commit `90412ec`)

- `HEAD` de código: `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`, com pai `bd2b2e0f1e4f2674b528175e535b0931badec34a`.
- Árvore do commit: 51 arquivos (`git ls-tree -r --name-only 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30 | wc -l`).
- Arquivos do commit que esta fase usa ou altera (confira com `git show 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30:<arquivo> | sha256sum`):

| Arquivo | SHA-256 no commit `90412ec` | Papel na F2 |
| --- | --- | --- |
| `pyproject.toml` | `c267322b201acc6229b133020062c4ba02f473ad918c459377ad4432aa1df5a4` | Alterar somente o que §9 manda |
| `uv.lock` | `b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d` | **Não muda** |
| `src/api_gestao_pessoal/models/base.py` | `39cb5b83a05e05bcc13f627ca6190706303591763203fb288a17960561041ad9` | Alterar (§6.1) |
| `src/api_gestao_pessoal/models/__init__.py` | `dd692b63d6c5cbbcb4386cb146ef51b9e6d3b00259256aed1a85439eb059ca37` | Alterar (§6.6) |
| `src/api_gestao_pessoal/models/usuario.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (vazio) | Alterar (§6.4.1) |
| `src/api_gestao_pessoal/database.py` | `50ab98141652b19a5ba21e690e6d6dacc74aa24b5803764e8c2541388d297def` | Usar `criar_fabrica_sessoes` nos testes. **Não alterar** |
| `alembic.ini` | `85e531a52b75ea3dbe5202fea719e871393606647ab28b739ad82ae842e27306` | **Não alterar** |
| `alembic/env.py` | `10563c24868c0921987c9953ad1f3f12915aedc82bdfc5ec59ef9013b5fe55c1` | **Não alterar** |
| `alembic/script.py.mako` | `b37123fcbbe9acb6a1890d253752bc7e4cebb2d787e6a0fb35387f99907eafba` | **Não alterar** |
| `tests/conftest.py` | `d94beb8afec10ae275915aafda972c51a5486fccc4ea3b2d79dfb990bdba4408` | Alterar (§10.1) |
| `tests/apoio/banco.py` | `b6f740c7ae285ab445bc7ba24bf299f7490e75b7736445c7b016b658df0b52ec` | Alterar (§10.2) |
| `tests/infra/test_alembic_ambiente.py` | `202360144c0c35ce6015cab57d15eedd07ad96b17842d4a385cb2ca615337f75` | Alterar somente CT-F1-17 (§10.6) |

Fatos do ambiente, conferidos pelo Opus em 2026-10-13 sem alterar nada:

- Python 3.14.6 (`uuid.uuid7()` disponível, versão 7), SQLAlchemy 2.1.4, Alembic 1.20.0 (`command.revision(..., rev_id=...)` e `op.f` existem), psycopg 3.3.6, pytest 9.1.1, pytest-asyncio 1.4.0, testcontainers 4.15.0, Ruff 0.16.10 e Pyright 1.1.414.
- `alembic/env.py`: hoje fora do Ruff e do Pyright. Com a configuração da opção A (§9), o Ruff acusa **somente** `PLC0415` (import local de `settings`, exigido pelo contrato), a formatação já está correta e o Pyright dá 0 erros.
- O Ruff classifica `alembic` como pacote de primeira parte, por causa do diretório `alembic/` na raiz. Os imports de `alembic` ficam no bloco depois de `sqlalchemy`; o `ruff check --fix` ordena isso.
- O ignore `"tests/*" = ["PLR2004"]` cobre subpastas: comparar contagens literais em `tests/esquema/` não gera aviso.
- `__mapper_args__ = {"eager_defaults": True}` declarado na `Base` é herdado pelos modelos. Colunas de mixin ficam depois das colunas da classe. O `update()` do Core e o UPDATE do ORM acrescentam `atualizado_em=now()` sozinhos.
- Dentro de uma revisão, o Alembic usa a convenção de nomes do `target_metadata` que o `env.py` passa. Por isso, o CHECK de um `sa.Enum(..., name="prioridade")` recebe o nome `ck_<tabela>_prioridade`.

### 1.2. Alterações documentais de preparação (autorizadas em 2026-10-13)

Feitas pelo Opus, com autorização expressa do usuário (`indice.md` §4, M10). São **protegidas**: você não as altera.

| Arquivo | Situação | SHA-256 esperado |
| --- | --- | --- |
| `CLAUDE.md` | Modificado | `35fda3df29e2ae1bd2172a35c430944f4b5fb7d08dd26e0c9bf2123da0405e7d` |
| `docs/adr/0001_arquitetura_api_minhavida.md` | Modificado | `7f7c4745c204a026a3742617bc8525ece2d0b99a722e37ec87d94a0740e23760` |
| `docs/adr/0002_identificadores_uuid.md` | Modificado | `951fb3936affa3eb1dcab67f89507eb9620630e938b2868b2f3ebf4b632b7593` |
| `docs/arquitetura/analise_projeto_minhavida.md` | Modificado | `a61962f06274c2bed1775e425d3e1b55a0b0a41995a336b890e7fa83503c4303` |
| `docs/arquitetura/arquitetura_api_minhavida.md` | Modificado | `c691fca0219a1b69674c8a2762d9c3be800ba6b6c081e5414a2b476eafe3db24` |
| `docs/arquitetura/indice.md` | Modificado | `28f2d37479aa02209ebdd23112032f7aa684cf5c067552426d6d8195db45ad0b` |
| `docs/arquitetura/matriz_requisitos_api.md` | Modificado | `ed3b2accbc0ed565fbfe9283d4e56c694cecf72ae537e42414789ab06788330c` |
| `docs/arquitetura/plano_fases_api.md` | Modificado | `05253430f13e462017ff9e0ad788c95692a9bd56b36a4dd9ef20ff02fa01a4ec` |
| `docs/arquitetura/plano_validacao_auditoria.md` | Modificado | `ba7f8d9234748da3dde04b822d0b4c383b6ebfaed18ed8fb64edb9dd17ae1669` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md` | Modificado | `e1d6ac1ac2282bac95b39981a1369f40dd1cc4a94acc45d5e9f5764e42350e05` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md` (este prompt) | Novo | Informado pelo usuário na mensagem de envio. Registre o valor que você calcular na Etapa A |

Situações aceitas. Qualquer outra é **divergência**: pare e relate.

| Modo | Condição |
| --- | --- |
| **A**: sem commit de preparação | `git rev-parse HEAD` = `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`. `git status --porcelain --untracked-files=all` lista **exatamente** os 10 arquivos acima como ` M` e este prompt como `??`. Nada mais |
| **B**: com commit de preparação do usuário | `git rev-parse HEAD^` = `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`. `git diff --name-status 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30 HEAD` lista **exatamente** os 10 arquivos como `M` e este prompt como `A`. `git status --porcelain --untracked-files=all` vazio |

Nos dois modos, os SHA-256 da tabela devem coincidir. Arquivos ignorados (`.env`, `.venv/`, caches, `src/api.egg-info/`) não contam e **não** devem ser abertos.

### 1.3. Revalidação no início da Etapa B (somente leitura)

Antes de qualquer alteração, execute e registre o bloco “Revalidação do baseline”. Grave as saídas, sem edição, em `$HOME/minhavida_evidencias/f2/00_revalidacao.log`:

1. (a) `git rev-parse HEAD` e `git rev-parse HEAD^`: o modo (A ou B) é o mesmo registrado na Etapa A, e os SHAs coincidem.
2. (b) `git ls-tree -r --name-only 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30 | wc -l` → `51`.
3. (c) `git status --porcelain --untracked-files=all`: igual ao do modo (§1.2).
4. (d) `git show 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30:<arquivo> | sha256sum` e `sha256sum <arquivo>` para cada arquivo de §1.1: iguais à tabela.
5. (e) `sha256sum` dos 11 documentos de §1.2: iguais à tabela e ao valor deste prompt registrado na Etapa A.
6. (f) `sha256sum` das fontes lidas na Etapa A (§2): iguais às registradas no relatório da Etapa A.

Se tudo coincidir, siga para §13, passo 1, sem refazer a Etapa A. Se algo divergir, **pare** e relate o passo e o arquivo. O usuário decide se a Etapa A precisa ser refeita.

## 2. Fontes normativas e precedência

Leia integralmente, nesta ordem, e registre o SHA-256 de cada uma:

1. `CLAUDE.md`: diretrizes (seções 1 e 2), contrato das 13 tabelas, restrições entre registros, regras de integridade, índices e mapeamento SQLAlchemy. **Atualizado em 2026-10-13**: identificadores UUID, enumerações, JSON, timestamps e CHECKs de nome.
2. `docs/arquitetura/indice.md`: §3 (precedência), §4 (aprovações) e §5 (gates).
3. `docs/adr/0002_identificadores_uuid.md` (ACEITO) e `docs/adr/0001_arquitetura_api_minhavida.md`: D-04, D-09 e D-14 (aceitas).
4. `docs/arquitetura/arquitetura_api_minhavida.md`: §10 integral (aceito), §2.1 (árvore de `models/`) e §3.2 (`criar_fabrica_sessoes`).
5. `docs/arquitetura/plano_validacao_auditoria.md`: §2, §3 (em especial §3.4), §4 (CT-F1-02, CT-F1-17 a 19 e todo o catálogo da F2), §5 e §6.
6. `docs/arquitetura/analise_projeto_minhavida.md`: §4 (REC-MV-001, 008, 014, 033 e 034) e §9 (DEC-MV-06 a 08).
7. Este prompt.

Precedência: instruções explícitas do usuário na sessão > `CLAUDE.md` > ADRs **aceitos** > documentos de arquitetura > este prompt. O prompt `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md` está **SUSPENSO**: não o use.

## 3. Decisões aprovadas e reconciliações aplicáveis

> Registro completo em `docs/arquitetura/indice.md` §4. Estas aprovações **não** autorizam a implementação, que depende do “pode implementar”, nem as decisões DEC-MV-09 a 24.

| Decisão | Conteúdo | Aprovação |
| --- | --- | --- |
| DEC-MV-06 | UUIDv7 gerado pela aplicação (`uuid.uuid7()`) nas 13 PKs e nas 19 FKs, sem `server_default` (ADR-0002) | **APROVADA** em 2026-10-13 |
| DEC-MV-07 | Restante de D-09 e arquitetura §10: `Enum` textual com CHECK, `CriadoAtualizadoMixin` (substitui o `TimestampMixin`), timestamps no servidor, `eager_defaults`, `JSON(none_as_null=True)`, nomes de até 63 caracteres, uma migração inicial com as 13 tabelas e os 30 seeds | **APROVADA** em 2026-10-13 |
| DEC-MV-08 | CHECKs `char_length(...) BETWEEN 3 AND 100` em `importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao` | **APROVADA** em 2026-10-13 |
| ACH-MV-F1-005, opção A | `alembic/` no Ruff e no Pyright, com `PLC0415` ignorada só em `alembic/env.py` (§9) | **APROVADA** em 2026-10-13 |
| DEC-MV-01 a 05, 25 e 26 | Arquitetura, sessão, erros, testes, higiene, convenção de nomes e `exclude = ["*.md"]` no formatador | Aprovadas em 2026-10-11 (contexto) |

Reconciliações implementadas nesta fase:

- REC-MV-001 (UUID);
- REC-MV-008 (mixin);
- REC-MV-014 (CHECKs de nome);
- REC-MV-033: **sem `default=` no ORM**, exceto `id`. Os padrões ficam só no banco e voltam por `RETURNING`;
- REC-MV-034: `limpar_dados()` sem `RESTART IDENTITY` e sem `CASCADE`, e testes de restrição com transação revertida.

## 4. Escopo e exclusões

**Dentro do escopo:**

1. `models/enums.py` com as 7 enumerações e a fábrica `tipo_enum` (§6.2).
2. `models/base.py`: `eager_defaults` na `Base`, `CriadoAtualizadoMixin` e **remoção** do `TimestampMixin` (§6.1).
3. Os 13 modelos (§6.4), um por arquivo, e `models/__init__.py` exportando todos (§6.6).
4. A revisão Alembic `0001` com as 13 tabelas, as 85 constraints, os 8 índices e os 30 seeds idempotentes (§8).
5. `pyproject.toml`: somente as três alterações do ACH-MV-F1-005, opção A (§9).
6. Testes `tests/esquema/` (CT-F2-01 a CT-F2-20), apoio de testes, fixture de migração por sessão e atualização de CT-F1-17 (§10).

**Fora do escopo (não implementar):**

- services, routers, schemas Pydantic e endpoints;
- `relationship()` (ADR-0001 D-04, item 7);
- índices, CHECKs, UNIQUEs ou colunas além dos listados em §6;
- `default=` no ORM, exceto `id` (REC-MV-033);
- o valor `DESATIVADO` em `SituacaoLembrete` (DEC-MV-19, **não** aprovada);
- triggers, funções e extensões do PostgreSQL;
- qualquer dependência nova, `uv add`, `uv lock` ou mudança no `uv.lock`;
- mudanças em `compose.yaml`, `.env.exemplo`, `.gitignore`, `alembic.ini`, `alembic/env.py` e `alembic/script.py.mako`;
- qualquer dependência, tabela, configuração ou abstração para integrações financeiras externas (arquitetura §1.1).

## 5. Política de testes e justificativa do alcance

- Seleções fixas em §13: `tests/esquema` (testes da fase) e, como regressões, `tests/infra/test_alembic_ambiente.py` (CT-F1-17 a 19, que agora encontram a revisão `0001`) e `tests/infra/test_configuracao.py::test_importacao_sem_efeitos` (CT-F1-02: importar os 13 modelos não faz I/O).
- O restante de `tests/infra` não é afetado: não usa as tabelas de domínio. Não rode `tests/infra` inteiro nem a suíte completa.
- Ao falhar: o mesmo teste → correção autorizada → o mesmo teste → a seleção da fase. Nada de reexecutar por rotina.
- Docker indisponível = **BLOQUEIO**. Não pule testes nem marque `xfail`.
- Sem `sleep` como sincronização. Esta fase não tem testes de concorrência.

## 6. Contrato físico

### 6.1. `models/base.py` (conteúdo-alvo exato)

`CONVENCAO_NOMES` permanece **byte a byte** igual ao baseline (DEC-MV-25). O `TimestampMixin` é removido. Nenhum outro arquivo o usa: confirme na Etapa A (§12, passo 6).

```python
"""Base declarativa, convenção de nomes e mixin de timestamps."""

from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

CONVENCAO_NOMES = {
    "pk": "pk_%(table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
}


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os modelos ORM."""

    metadata = MetaData(naming_convention=CONVENCAO_NOMES)
    # Valores gerados no servidor voltam por RETURNING no INSERT e no
    # UPDATE, sem I/O tardio na AsyncSession (DEC-MV-07).
    __mapper_args__ = {"eager_defaults": True}


class CriadoAtualizadoMixin:
    """`criado_em` e `atualizado_em` das 8 tabelas que têm as duas colunas.

    `criado_em`: padrão do banco (`DEFAULT now()`). `atualizado_em`: o
    mesmo padrão na inserção e `onupdate`, aplicado pelo SQLAlchemy nos
    UPDATEs que ele emite. Não há trigger no banco.
    """

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

### 6.2. `models/enums.py` (conteúdo-alvo exato)

```python
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


def tipo_enum(
    classe: type[enum.StrEnum], nome: str, comprimento: int
) -> Enum:
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
```

Chame `tipo_enum` **uma vez por coluna**. Não reutilize uma instância de `Enum` em duas colunas.

### 6.3. Comportamento dos timestamps: `server_default` × `onupdate`

Fonte canônica: arquitetura §10.3.1. Resumo operacional:

| Coluna | Onde a regra vive | INSERT | UPDATE emitido pelo SQLAlchemy (ORM `flush` ou Core `update()`) | UPDATE em SQL textual |
| --- | --- | --- | --- | --- |
| `criado_em`, `criada_em` | `server_default=func.now()`: vira `DEFAULT now()` no DDL, ou seja, regra **do banco** | O banco preenche sempre que a coluna é omitida, inclusive em SQL textual | Não muda | Não muda |
| `atualizado_em` | `server_default=func.now()` (banco) **e** `onupdate=func.now()` (SQLAlchemy; **não existe no banco**) | O banco preenche com o mesmo instante de `criado_em` | O SQLAlchemy acrescenta `atualizado_em=now()` ao `SET`, salvo quando o valor é informado explicitamente | **Não muda**: não há trigger |

- **`server_default`** é uma cláusula `DEFAULT` gravada na tabela. Vale para qualquer cliente que omita a coluna no INSERT: ORM, Core ou SQL textual.
- **`onupdate`** é metadado do SQLAlchemy, **não** vai para o DDL. Só age quando o SQLAlchemy emite um UPDATE. No ORM, isso acontece apenas se algum atributo mapeado mudou; um `flush` sem mudança não altera `atualizado_em`.
- `now()` no PostgreSQL é o **início da transação**. Inserir e atualizar na mesma transação deixa `atualizado_em == criado_em`. Para observar a mudança, o UPDATE precisa ocorrer em outra transação (CT-F2-19).
- `eager_defaults=True` faz o ORM buscar os valores gerados pelo servidor por `RETURNING`, na própria instrução de INSERT ou UPDATE. Sem isso, os atributos ficariam expirados, e o primeiro acesso exigiria nova consulta, que na `AsyncSession` falha com `MissingGreenlet`.
- `notificacao.criada_em` e `requisicao_idempotente.criado_em` têm só `server_default=func.now()`, declarado na própria classe, sem mixin.
- `server_onupdate` não é usado.

### 6.4. Tabelas, colunas, restrições e índices

Regras gerais, válidas para as 13 tabelas:

- Declare as colunas **na ordem da tabela**. As do mixin ficam por último, porque o SQLAlchemy as acrescenta ao fim. CT-F2-02 confere essa ordem.
- Toda coluna informa `nullable=` explicitamente.
- `id`: `Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7)`. É o **único** `default=` do ORM (REC-MV-033).
- `server_default` somente onde a tabela indica, com a expressão exata (`text("...")` ou `func.now()`).
- FK simples: `ForeignKey("<tabela>.id", ondelete="RESTRICT")` na própria coluna. FK composta: `ForeignKeyConstraint([...], [...], ondelete="RESTRICT")` em `__table_args__`, **sem** FK simples na mesma coluna.
- UNIQUE de uma coluna: `unique=True` na coluna. UNIQUE composta: `UniqueConstraint(...)` em `__table_args__`. Não passe `name=`: a convenção nomeia.
- CHECK explícito: `CheckConstraint("<expressão>", name="<nome curto>")`. A convenção acrescenta o prefixo `ck_<tabela>_`. Passar o nome completo duplicaria o prefixo.
- Índices: `Index("<nome completo>", "<col>", ...)` em `__table_args__`. Não use `index=True`.
- A coluna “Introspecção” traz o valor esperado de `format_type(atttypid, atttypmod)` e de `pg_get_expr(adbin, adrelid)` no PostgreSQL, usados em CT-F2-02. “—” = sem padrão.

Modelo de referência de estilo (tabela `atividade`, **completo**; os demais seguem o mesmo padrão):

```python
"""Tabela `atividade`: ocorrência concreta de uma atividade (tabela 5)."""

import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from api_gestao_pessoal.models.base import Base, CriadoAtualizadoMixin
from api_gestao_pessoal.models.enums import Prioridade, tipo_enum


class Atividade(CriadoAtualizadoMixin, Base):
    """Ocorrência de atividade; avulsa quando `serie_id` é nulo."""

    __tablename__ = "atividade"
    __table_args__ = (
        UniqueConstraint("serie_id", "numero_ocorrencia"),
        CheckConstraint(
            "char_length(nome) BETWEEN 3 AND 100", name="nome_tamanho"
        ),
        CheckConstraint("horario_final > horario_inicial", name="horarios"),
        CheckConstraint(
            "(serie_id IS NULL AND numero_ocorrencia IS NULL) OR "
            "(serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL "
            "AND numero_ocorrencia >= 1)",
            name="serie_numero",
        ),
        ForeignKeyConstraint(
            ["serie_id", "usuario_id"],
            ["serie_atividade.id", "serie_atividade.usuario_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_atividade_usuario_data", "usuario_id", "data_atividade"),
        Index(
            "ix_atividade_usuario_concluida_data",
            "usuario_id",
            "concluida_em",
            "data_atividade",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categoria_atividade.id", ondelete="RESTRICT"),
        nullable=False,
    )
    serie_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    numero_ocorrencia: Mapped[int | None] = mapped_column(
        Integer(), nullable=True
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)
    prioridade: Mapped[Prioridade] = mapped_column(
        tipo_enum(Prioridade, "prioridade", 5),
        server_default=text("'BAIXA'"),
        nullable=False,
    )
    data_atividade: Mapped[date] = mapped_column(Date(), nullable=False)
    horario_inicial: Mapped[time] = mapped_column(
        Time(timezone=False), nullable=False
    )
    horario_final: Mapped[time] = mapped_column(
        Time(timezone=False), nullable=False
    )
    concluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    excluida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

Contrato por tabela. Gerado a partir do `CLAUDE.md` atualizado e conferido por compilação offline do DDL: 134 colunas, 32 `uuid` e 93 nomes.

#### 6.4.1. `usuario` → `Usuario` em `models/usuario.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `nome_completo` | `str` | `String(150)` | não | — | — | `character varying(150)` · — |
| 3 | `email` | `str` | `String(254)` | não | — | — | `character varying(254)` · — |
| 4 | `senha_hash` | `str` | `String(255)` | não | — | — | `character varying(255)` · — |
| 5 | `data_nascimento` | `date` | `Date()` | não | — | — | `date` · — |
| 6 | `fuso_horario` | `str` | `String(64)` | não | — | — | `character varying(64)` · — |
| 7 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 8 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (2):

- `pk_usuario`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_usuario_email`: `UNIQUE (email)`. Pela convenção.

#### 6.4.2. `recuperacao_senha` → `RecuperacaoSenha` em `models/recuperacao_senha.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `codigo_hash` | `str` | `String(255)` | não | — | — | `character varying(255)` · — |
| 4 | `expira_em` | `datetime` | `DateTime(timezone=True)` | não | — | — | `timestamp with time zone` · — |
| 5 | `tentativas` | `int` | `Integer()` | não | `text("0")` | — | `integer` · `0` |
| 6 | `verificado_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 7 | `token_redefinicao_hash` | `str \| None` | `String(64)` | sim | — | — | `character varying(64)` · — |
| 8 | `utilizado_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 9 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 10 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (4):

- `fk_recuperacao_senha_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_recuperacao_senha`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_recuperacao_senha_token_redefinicao_hash`: `UNIQUE (token_redefinicao_hash)`. Pela convenção.
- `uq_recuperacao_senha_usuario_id`: `UNIQUE (usuario_id)`. Pela convenção.

#### 6.4.3. `categoria_atividade` → `CategoriaAtividade` em `models/categoria_atividade.py`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `nome` | `str` | `String(50)` | não | — | — | `character varying(50)` · — |
| 3 | `ativa` | `bool` | `Boolean()` | não | `text("true")` | — | `boolean` · `true` |

Restrições e índices (2):

- `pk_categoria_atividade`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_categoria_atividade_nome`: `UNIQUE (nome)`. Pela convenção.

#### 6.4.4. `serie_atividade` → `SerieAtividade` em `models/serie_atividade.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `categoria_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `categoria_atividade.id` | `uuid` · — |
| 4 | `nome_padrao` | `str` | `String(100)` | não | — | — | `character varying(100)` · — |
| 5 | `descricao_padrao` | `str \| None` | `String(200)` | sim | — | — | `character varying(200)` · — |
| 6 | `prioridade_padrao` | `Prioridade` | `tipo_enum(Prioridade, "prioridade_padrao", 5)` | não | `text("'BAIXA'")` | — | `character varying(5)` · `'BAIXA'::character varying` |
| 7 | `periodicidade` | `PeriodicidadeAtividade` | `tipo_enum(PeriodicidadeAtividade, "periodicidade", 10)` | não | — | — | `character varying(10)` · — |
| 8 | `data_referencia` | `date` | `Date()` | não | — | — | `date` · — |
| 9 | `numero_referencia` | `int` | `Integer()` | não | `text("1")` | — | `integer` · `1` |
| 10 | `horario_inicial_padrao` | `time` | `Time(timezone=False)` | não | — | — | `time without time zone` · — |
| 11 | `horario_final_padrao` | `time` | `Time(timezone=False)` | não | — | — | `time without time zone` · — |
| 12 | `data_final_repeticao` | `date \| None` | `Date()` | sim | — | — | `date` · — |
| 13 | `numero_final` | `int \| None` | `Integer()` | sim | — | — | `integer` · — |
| 14 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 15 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (11):

- `ck_serie_atividade_data_final` ← `CheckConstraint(..., name="data_final")`: `data_final_repeticao IS NULL OR data_final_repeticao >= data_referencia`.
- `ck_serie_atividade_horarios` ← `CheckConstraint(..., name="horarios")`: `horario_final_padrao > horario_inicial_padrao`.
- `ck_serie_atividade_nome_padrao_tamanho` ← `CheckConstraint(..., name="nome_padrao_tamanho")`: `char_length(nome_padrao) BETWEEN 3 AND 100`.
- `ck_serie_atividade_numero_final` ← `CheckConstraint(..., name="numero_final")`: `numero_final IS NULL OR numero_final >= 0`.
- `ck_serie_atividade_numero_referencia` ← `CheckConstraint(..., name="numero_referencia")`: `numero_referencia >= 1`.
- `ck_serie_atividade_periodicidade`: gerado pelo `Enum` (`name="periodicidade"`): `periodicidade IN ('NENHUMA', 'DIARIA', 'SEMANAL', 'MENSAL')`.
- `ck_serie_atividade_prioridade_padrao`: gerado pelo `Enum` (`name="prioridade_padrao"`): `prioridade_padrao IN ('BAIXA', 'MEDIA', 'ALTA')`.
- `fk_serie_atividade_categoria_id_categoria_atividade`: `FOREIGN KEY (categoria_id) REFERENCES categoria_atividade (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `fk_serie_atividade_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_serie_atividade`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_serie_atividade_id_usuario_id`: `UNIQUE (id, usuario_id)`. Pela convenção.

#### 6.4.5. `atividade` → `Atividade` em `models/atividade.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `categoria_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `categoria_atividade.id` | `uuid` · — |
| 4 | `serie_id` | `uuid.UUID \| None` | `Uuid(as_uuid=True)` | sim | — | — | `uuid` · — |
| 5 | `numero_ocorrencia` | `int \| None` | `Integer()` | sim | — | — | `integer` · — |
| 6 | `nome` | `str` | `String(100)` | não | — | — | `character varying(100)` · — |
| 7 | `descricao` | `str \| None` | `String(200)` | sim | — | — | `character varying(200)` · — |
| 8 | `prioridade` | `Prioridade` | `tipo_enum(Prioridade, "prioridade", 5)` | não | `text("'BAIXA'")` | — | `character varying(5)` · `'BAIXA'::character varying` |
| 9 | `data_atividade` | `date` | `Date()` | não | — | — | `date` · — |
| 10 | `horario_inicial` | `time` | `Time(timezone=False)` | não | — | — | `time without time zone` · — |
| 11 | `horario_final` | `time` | `Time(timezone=False)` | não | — | — | `time without time zone` · — |
| 12 | `concluida_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 13 | `excluida_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 14 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 15 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (11):

- `ck_atividade_horarios` ← `CheckConstraint(..., name="horarios")`: `horario_final > horario_inicial`.
- `ck_atividade_nome_tamanho` ← `CheckConstraint(..., name="nome_tamanho")`: `char_length(nome) BETWEEN 3 AND 100`.
- `ck_atividade_prioridade`: gerado pelo `Enum` (`name="prioridade"`): `prioridade IN ('BAIXA', 'MEDIA', 'ALTA')`.
- `ck_atividade_serie_numero` ← `CheckConstraint(..., name="serie_numero")`: `(serie_id IS NULL AND numero_ocorrencia IS NULL) OR (serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL AND numero_ocorrencia >= 1)`.
- `fk_atividade_categoria_id_categoria_atividade`: `FOREIGN KEY (categoria_id) REFERENCES categoria_atividade (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `fk_atividade_serie_id_serie_atividade`: `FOREIGN KEY (serie_id, usuario_id) REFERENCES serie_atividade (id, usuario_id) ON DELETE RESTRICT` (composta, em `__table_args__`). Pela convenção.
- `fk_atividade_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_atividade`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_atividade_serie_id_numero_ocorrencia`: `UNIQUE (serie_id, numero_ocorrencia)`. Pela convenção.
- `ix_atividade_usuario_concluida_data`: índice `(usuario_id, concluida_em, data_atividade)`, nome explícito em `Index(...)`.
- `ix_atividade_usuario_data`: índice `(usuario_id, data_atividade)`, nome explícito em `Index(...)`.

#### 6.4.6. `categoria_importancia` → `CategoriaImportancia` em `models/categoria_importancia.py`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `nome` | `str` | `String(50)` | não | — | — | `character varying(50)` · — |
| 3 | `ativa` | `bool` | `Boolean()` | não | `text("true")` | — | `boolean` · `true` |

Restrições e índices (2):

- `pk_categoria_importancia`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_categoria_importancia_nome`: `UNIQUE (nome)`. Pela convenção.

#### 6.4.7. `serie_importancia` → `SerieImportancia` em `models/serie_importancia.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `categoria_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `categoria_importancia.id` | `uuid` · — |
| 4 | `nome_padrao` | `str` | `String(100)` | não | — | — | `character varying(100)` · — |
| 5 | `descricao_padrao` | `str \| None` | `String(200)` | sim | — | — | `character varying(200)` · — |
| 6 | `periodicidade` | `PeriodicidadeImportancia` | `tipo_enum(PeriodicidadeImportancia, "periodicidade", 10)` | não | — | — | `character varying(10)` · — |
| 7 | `data_referencia` | `date` | `Date()` | não | — | — | `date` · — |
| 8 | `numero_referencia` | `int` | `Integer()` | não | `text("1")` | — | `integer` · `1` |
| 9 | `horario_padrao` | `time \| None` | `Time(timezone=False)` | sim | — | — | `time without time zone` · — |
| 10 | `data_final_repeticao` | `date \| None` | `Date()` | sim | — | — | `date` · — |
| 11 | `numero_final` | `int \| None` | `Integer()` | sim | — | — | `integer` · — |
| 12 | `possui_despesa_padrao` | `bool` | `Boolean()` | não | `text("false")` | — | `boolean` · `false` |
| 13 | `valor_previsto_padrao` | `Decimal \| None` | `Numeric(12, 2, asdecimal=True)` | sim | — | — | `numeric(12,2)` · — |
| 14 | `lembrete_antecedencia_dias` | `int \| None` | `SmallInteger()` | sim | — | — | `smallint` · — |
| 15 | `lembrete_horario` | `time \| None` | `Time(timezone=False)` | sim | — | — | `time without time zone` · — |
| 16 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 17 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (12):

- `ck_serie_importancia_data_final` ← `CheckConstraint(..., name="data_final")`: `data_final_repeticao IS NULL OR data_final_repeticao >= data_referencia`.
- `ck_serie_importancia_lembrete_antecedencia` ← `CheckConstraint(..., name="lembrete_antecedencia")`: `lembrete_antecedencia_dias IS NULL OR lembrete_antecedencia_dias IN (0, 1, 3, 7)`.
- `ck_serie_importancia_lembrete_par` ← `CheckConstraint(..., name="lembrete_par")`: `(lembrete_antecedencia_dias IS NULL) = (lembrete_horario IS NULL)`.
- `ck_serie_importancia_nome_padrao_tamanho` ← `CheckConstraint(..., name="nome_padrao_tamanho")`: `char_length(nome_padrao) BETWEEN 3 AND 100`.
- `ck_serie_importancia_numero_final` ← `CheckConstraint(..., name="numero_final")`: `numero_final IS NULL OR numero_final >= 0`.
- `ck_serie_importancia_numero_referencia` ← `CheckConstraint(..., name="numero_referencia")`: `numero_referencia >= 1`.
- `ck_serie_importancia_periodicidade`: gerado pelo `Enum` (`name="periodicidade"`): `periodicidade IN ('NENHUMA', 'DIARIA', 'SEMANAL', 'MENSAL', 'ANUAL')`.
- `ck_serie_importancia_valor_previsto` ← `CheckConstraint(..., name="valor_previsto")`: `(possui_despesa_padrao = false AND valor_previsto_padrao IS NULL) OR (possui_despesa_padrao = true AND valor_previsto_padrao IS NOT NULL AND valor_previsto_padrao > 0)`.
- `fk_serie_importancia_categoria_id_categoria_importancia`: `FOREIGN KEY (categoria_id) REFERENCES categoria_importancia (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `fk_serie_importancia_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_serie_importancia`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_serie_importancia_id_usuario_id`: `UNIQUE (id, usuario_id)`. Pela convenção.

#### 6.4.8. `importancia` → `Importancia` em `models/importancia.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `categoria_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `categoria_importancia.id` | `uuid` · — |
| 4 | `serie_id` | `uuid.UUID \| None` | `Uuid(as_uuid=True)` | sim | — | — | `uuid` · — |
| 5 | `numero_ocorrencia` | `int \| None` | `Integer()` | sim | — | — | `integer` · — |
| 6 | `nome` | `str` | `String(100)` | não | — | — | `character varying(100)` · — |
| 7 | `descricao` | `str \| None` | `String(200)` | sim | — | — | `character varying(200)` · — |
| 8 | `data_compromisso` | `date` | `Date()` | não | — | — | `date` · — |
| 9 | `horario` | `time \| None` | `Time(timezone=False)` | sim | — | — | `time without time zone` · — |
| 10 | `possui_despesa` | `bool` | `Boolean()` | não | `text("false")` | — | `boolean` · `false` |
| 11 | `valor_previsto` | `Decimal \| None` | `Numeric(12, 2, asdecimal=True)` | sim | — | — | `numeric(12,2)` · — |
| 12 | `concluida_manualmente_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 13 | `excluida_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 14 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 15 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (11):

- `ck_importancia_conclusao_manual` ← `CheckConstraint(..., name="conclusao_manual")`: `possui_despesa = false OR concluida_manualmente_em IS NULL`.
- `ck_importancia_nome_tamanho` ← `CheckConstraint(..., name="nome_tamanho")`: `char_length(nome) BETWEEN 3 AND 100`.
- `ck_importancia_serie_numero` ← `CheckConstraint(..., name="serie_numero")`: `(serie_id IS NULL AND numero_ocorrencia IS NULL) OR (serie_id IS NOT NULL AND numero_ocorrencia IS NOT NULL AND numero_ocorrencia >= 1)`.
- `ck_importancia_valor_previsto` ← `CheckConstraint(..., name="valor_previsto")`: `(possui_despesa = false AND valor_previsto IS NULL) OR (possui_despesa = true AND valor_previsto IS NOT NULL AND valor_previsto > 0)`.
- `fk_importancia_categoria_id_categoria_importancia`: `FOREIGN KEY (categoria_id) REFERENCES categoria_importancia (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `fk_importancia_serie_id_serie_importancia`: `FOREIGN KEY (serie_id, usuario_id) REFERENCES serie_importancia (id, usuario_id) ON DELETE RESTRICT` (composta, em `__table_args__`). Pela convenção.
- `fk_importancia_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_importancia`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_importancia_id_usuario_id`: `UNIQUE (id, usuario_id)`. Pela convenção.
- `uq_importancia_serie_id_numero_ocorrencia`: `UNIQUE (serie_id, numero_ocorrencia)`. Pela convenção.
- `ix_importancia_usuario_data`: índice `(usuario_id, data_compromisso)`, nome explícito em `Index(...)`.

#### 6.4.9. `categoria_financeira` → `CategoriaFinanceira` em `models/categoria_financeira.py`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `nome` | `str` | `String(50)` | não | — | — | `character varying(50)` · — |
| 3 | `tipo` | `TipoMovimentacao` | `tipo_enum(TipoMovimentacao, "tipo", 7)` | não | — | — | `character varying(7)` · — |
| 4 | `ativa` | `bool` | `Boolean()` | não | `text("true")` | — | `boolean` · `true` |

Restrições e índices (4):

- `ck_categoria_financeira_tipo`: gerado pelo `Enum` (`name="tipo"`): `tipo IN ('RECEITA', 'DESPESA')`.
- `pk_categoria_financeira`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_categoria_financeira_id_tipo`: `UNIQUE (id, tipo)`. Pela convenção.
- `uq_categoria_financeira_tipo_nome`: `UNIQUE (tipo, nome)`. Pela convenção.

#### 6.4.10. `movimentacao_financeira` → `MovimentacaoFinanceira` em `models/movimentacao_financeira.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `categoria_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | — | `uuid` · — |
| 4 | `tipo` | `TipoMovimentacao` | `tipo_enum(TipoMovimentacao, "tipo", 7)` | não | — | — | `character varying(7)` · — |
| 5 | `nome` | `str` | `String(100)` | não | — | — | `character varying(100)` · — |
| 6 | `descricao` | `str \| None` | `String(200)` | sim | — | — | `character varying(200)` · — |
| 7 | `valor` | `Decimal` | `Numeric(12, 2, asdecimal=True)` | não | — | — | `numeric(12,2)` · — |
| 8 | `data_movimentacao` | `date` | `Date()` | não | — | — | `date` · — |
| 9 | `contraparte` | `str \| None` | `String(100)` | sim | — | — | `character varying(100)` · — |
| 10 | `forma_movimentacao` | `FormaMovimentacao \| None` | `tipo_enum(FormaMovimentacao, "forma_movimentacao", 20)` | sim | — | — | `character varying(20)` · — |
| 11 | `importancia_id` | `uuid.UUID \| None` | `Uuid(as_uuid=True)` | sim | — | — | `uuid` · — |
| 12 | `importancia_vinculada_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 13 | `excluida_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 14 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 15 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (16):

- `ck_movimentacao_financeira_excluida_sem_vinculo` ← `CheckConstraint(..., name="excluida_sem_vinculo")`: `excluida_em IS NULL OR importancia_id IS NULL`.
- `ck_movimentacao_financeira_forma_movimentacao`: gerado pelo `Enum` (`name="forma_movimentacao"`): `forma_movimentacao IN ('PIX', 'DINHEIRO', 'CARTAO_DEBITO', 'TRANSFERENCIA', 'DEPOSITO', 'BOLETO', 'OUTROS')`.
- `ck_movimentacao_financeira_forma_tipo` ← `CheckConstraint(..., name="forma_tipo")`: `forma_movimentacao IS NULL OR (tipo = 'RECEITA' AND forma_movimentacao IN ('PIX','DINHEIRO','TRANSFERENCIA','DEPOSITO','OUTROS')) OR (tipo = 'DESPESA' AND forma_movimentacao IN ('PIX','DINHEIRO','CARTAO_DEBITO','TRANSFERENCIA','BOLETO','OUTROS'))`.
- `ck_movimentacao_financeira_nome_tamanho` ← `CheckConstraint(..., name="nome_tamanho")`: `char_length(nome) BETWEEN 3 AND 100`.
- `ck_movimentacao_financeira_tipo`: gerado pelo `Enum` (`name="tipo"`): `tipo IN ('RECEITA', 'DESPESA')`.
- `ck_movimentacao_financeira_valor_positivo` ← `CheckConstraint(..., name="valor_positivo")`: `valor > 0`.
- `ck_movimentacao_financeira_vinculo_despesa` ← `CheckConstraint(..., name="vinculo_despesa")`: `importancia_id IS NULL OR tipo = 'DESPESA'`.
- `ck_movimentacao_financeira_vinculo_par` ← `CheckConstraint(..., name="vinculo_par")`: `(importancia_id IS NULL) = (importancia_vinculada_em IS NULL)`.
- `fk_movimentacao_financeira_categoria_id_categoria_financeira`: `FOREIGN KEY (categoria_id, tipo) REFERENCES categoria_financeira (id, tipo) ON DELETE RESTRICT` (composta, em `__table_args__`). Pela convenção.
- `fk_movimentacao_financeira_importancia_id_importancia`: `FOREIGN KEY (importancia_id, usuario_id) REFERENCES importancia (id, usuario_id) ON DELETE RESTRICT` (composta, em `__table_args__`). Pela convenção.
- `fk_movimentacao_financeira_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_movimentacao_financeira`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_movimentacao_financeira_importancia_id`: `UNIQUE (importancia_id)`. Pela convenção.
- `ix_movimentacao_usuario_categoria_data`: índice `(usuario_id, categoria_id, data_movimentacao)`, nome explícito em `Index(...)`.
- `ix_movimentacao_usuario_data`: índice `(usuario_id, data_movimentacao)`, nome explícito em `Index(...)`.
- `ix_movimentacao_usuario_tipo_data`: índice `(usuario_id, tipo, data_movimentacao)`, nome explícito em `Index(...)`.

#### 6.4.11. `lembrete_importancia` → `LembreteImportancia` em `models/lembrete_importancia.py` — com `CriadoAtualizadoMixin`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `importancia_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | — | `uuid` · — |
| 4 | `antecedencia_dias` | `int` | `SmallInteger()` | não | — | — | `smallint` · — |
| 5 | `horario` | `time` | `Time(timezone=False)` | não | — | — | `time without time zone` · — |
| 6 | `agendado_para` | `datetime` | `DateTime(timezone=True)` | não | — | — | `timestamp with time zone` · — |
| 7 | `versao_agendamento` | `int` | `Integer()` | não | `text("1")` | — | `integer` · `1` |
| 8 | `situacao` | `SituacaoLembrete` | `tipo_enum(SituacaoLembrete, "situacao", 10)` | não | `text("'PENDENTE'")` | — | `character varying(10)` · `'PENDENTE'::character varying` |
| 9 | `enviado_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |
| 10 | `criado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 11 | `atualizado_em` (mixin) | `datetime` | `DateTime(timezone=True)` | não | `func.now()` + `onupdate=func.now()` | — | `timestamp with time zone` · `now()` |

Restrições e índices (9):

- `ck_lembrete_importancia_antecedencia` ← `CheckConstraint(..., name="antecedencia")`: `antecedencia_dias IN (0, 1, 3, 7)`.
- `ck_lembrete_importancia_enviado` ← `CheckConstraint(..., name="enviado")`: `(situacao = 'ENVIADO' AND enviado_em IS NOT NULL) OR (situacao <> 'ENVIADO' AND enviado_em IS NULL)`.
- `ck_lembrete_importancia_situacao`: gerado pelo `Enum` (`name="situacao"`): `situacao IN ('PENDENTE', 'ENVIADO', 'CANCELADO')`.
- `fk_lembrete_importancia_importancia_id_importancia`: `FOREIGN KEY (importancia_id, usuario_id) REFERENCES importancia (id, usuario_id) ON DELETE RESTRICT` (composta, em `__table_args__`). Pela convenção.
- `fk_lembrete_importancia_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_lembrete_importancia`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_lembrete_importancia_id_usuario_id`: `UNIQUE (id, usuario_id)`. Pela convenção.
- `uq_lembrete_importancia_importancia_id`: `UNIQUE (importancia_id)`. Pela convenção.
- `ix_lembrete_situacao_agendado`: índice `(situacao, agendado_para)`, nome explícito em `Index(...)`.

#### 6.4.12. `notificacao` → `Notificacao` em `models/notificacao.py`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `lembrete_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | — | `uuid` · — |
| 4 | `versao_agendamento` | `int` | `Integer()` | não | — | — | `integer` · — |
| 5 | `titulo` | `str` | `String(120)` | não | — | — | `character varying(120)` · — |
| 6 | `mensagem` | `str` | `String(500)` | não | — | — | `character varying(500)` · — |
| 7 | `criada_em` | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 8 | `lida_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |

Restrições e índices (5):

- `fk_notificacao_lembrete_id_lembrete_importancia`: `FOREIGN KEY (lembrete_id, usuario_id) REFERENCES lembrete_importancia (id, usuario_id) ON DELETE RESTRICT` (composta, em `__table_args__`). Pela convenção.
- `fk_notificacao_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_notificacao`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_notificacao_lembrete_id_versao_agendamento`: `UNIQUE (lembrete_id, versao_agendamento)`. Pela convenção.
- `ix_notificacao_usuario_lida_criada`: índice `(usuario_id, lida_em, criada_em)`, nome explícito em `Index(...)`.

#### 6.4.13. `requisicao_idempotente` → `RequisicaoIdempotente` em `models/requisicao_idempotente.py`

| # | Coluna | `Mapped[...]` | Tipo SQLAlchemy | Nulo | `server_default` | FK simples (`ondelete="RESTRICT"`) | Introspecção (`format_type` · padrão) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid.UUID` | `Uuid(as_uuid=True)`, PK, `default=uuid.uuid7` | não | — | — | `uuid` · — |
| 2 | `usuario_id` | `uuid.UUID` | `Uuid(as_uuid=True)` | não | — | `usuario.id` | `uuid` · — |
| 3 | `chave` | `str` | `String(64)` | não | — | — | `character varying(64)` · — |
| 4 | `acao` | `str` | `String(50)` | não | — | — | `character varying(50)` · — |
| 5 | `conteudo_hash` | `str` | `String(64)` | não | — | — | `character varying(64)` · — |
| 6 | `situacao` | `SituacaoRequisicao` | `tipo_enum(SituacaoRequisicao, "situacao", 20)` | não | `text("'EM_PROCESSAMENTO'")` | — | `character varying(20)` · `'EM_PROCESSAMENTO'::character varying` |
| 7 | `codigo_resposta` | `int \| None` | `SmallInteger()` | sim | — | — | `smallint` · — |
| 8 | `resposta` | `dict[str, Any] \| None` | `JSON(none_as_null=True)` | sim | — | — | `json` · — |
| 9 | `criado_em` | `datetime` | `DateTime(timezone=True)` | não | `func.now()` | — | `timestamp with time zone` · `now()` |
| 10 | `concluida_em` | `datetime \| None` | `DateTime(timezone=True)` | sim | — | — | `timestamp with time zone` · — |

Restrições e índices (4):

- `ck_requisicao_idempotente_situacao`: gerado pelo `Enum` (`name="situacao"`): `situacao IN ('EM_PROCESSAMENTO', 'CONCLUIDA')`.
- `fk_requisicao_idempotente_usuario_id_usuario`: `FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT` (simples, na coluna). Pela convenção.
- `pk_requisicao_idempotente`: `PRIMARY KEY (id)`. Pela convenção.
- `uq_requisicao_idempotente_usuario_id_acao_chave`: `UNIQUE (usuario_id, acao, chave)`. Pela convenção.

### 6.5. Lista literal dos 93 nomes (CT-F2-10)

Totais: 13 `PRIMARY KEY`, 17 `UNIQUE`, 19 `FOREIGN KEY`, 36 `CHECK` e 8 índices. O maior nome tem 60 caracteres.

| Tabela | Quantidade | Nomes |
| --- | --- | --- |
| `usuario` | 2 | `pk_usuario`, `uq_usuario_email` |
| `recuperacao_senha` | 4 | `fk_recuperacao_senha_usuario_id_usuario`, `pk_recuperacao_senha`, `uq_recuperacao_senha_token_redefinicao_hash`, `uq_recuperacao_senha_usuario_id` |
| `categoria_atividade` | 2 | `pk_categoria_atividade`, `uq_categoria_atividade_nome` |
| `serie_atividade` | 11 | `ck_serie_atividade_data_final`, `ck_serie_atividade_horarios`, `ck_serie_atividade_nome_padrao_tamanho`, `ck_serie_atividade_numero_final`, `ck_serie_atividade_numero_referencia`, `ck_serie_atividade_periodicidade`, `ck_serie_atividade_prioridade_padrao`, `fk_serie_atividade_categoria_id_categoria_atividade`, `fk_serie_atividade_usuario_id_usuario`, `pk_serie_atividade`, `uq_serie_atividade_id_usuario_id` |
| `atividade` | 11 | `ck_atividade_horarios`, `ck_atividade_nome_tamanho`, `ck_atividade_prioridade`, `ck_atividade_serie_numero`, `fk_atividade_categoria_id_categoria_atividade`, `fk_atividade_serie_id_serie_atividade`, `fk_atividade_usuario_id_usuario`, `ix_atividade_usuario_concluida_data`, `ix_atividade_usuario_data`, `pk_atividade`, `uq_atividade_serie_id_numero_ocorrencia` |
| `categoria_importancia` | 2 | `pk_categoria_importancia`, `uq_categoria_importancia_nome` |
| `serie_importancia` | 12 | `ck_serie_importancia_data_final`, `ck_serie_importancia_lembrete_antecedencia`, `ck_serie_importancia_lembrete_par`, `ck_serie_importancia_nome_padrao_tamanho`, `ck_serie_importancia_numero_final`, `ck_serie_importancia_numero_referencia`, `ck_serie_importancia_periodicidade`, `ck_serie_importancia_valor_previsto`, `fk_serie_importancia_categoria_id_categoria_importancia`, `fk_serie_importancia_usuario_id_usuario`, `pk_serie_importancia`, `uq_serie_importancia_id_usuario_id` |
| `importancia` | 11 | `ck_importancia_conclusao_manual`, `ck_importancia_nome_tamanho`, `ck_importancia_serie_numero`, `ck_importancia_valor_previsto`, `fk_importancia_categoria_id_categoria_importancia`, `fk_importancia_serie_id_serie_importancia`, `fk_importancia_usuario_id_usuario`, `ix_importancia_usuario_data`, `pk_importancia`, `uq_importancia_id_usuario_id`, `uq_importancia_serie_id_numero_ocorrencia` |
| `categoria_financeira` | 4 | `ck_categoria_financeira_tipo`, `pk_categoria_financeira`, `uq_categoria_financeira_id_tipo`, `uq_categoria_financeira_tipo_nome` |
| `movimentacao_financeira` | 16 | `ck_movimentacao_financeira_excluida_sem_vinculo`, `ck_movimentacao_financeira_forma_movimentacao`, `ck_movimentacao_financeira_forma_tipo`, `ck_movimentacao_financeira_nome_tamanho`, `ck_movimentacao_financeira_tipo`, `ck_movimentacao_financeira_valor_positivo`, `ck_movimentacao_financeira_vinculo_despesa`, `ck_movimentacao_financeira_vinculo_par`, `fk_movimentacao_financeira_categoria_id_categoria_financeira`, `fk_movimentacao_financeira_importancia_id_importancia`, `fk_movimentacao_financeira_usuario_id_usuario`, `ix_movimentacao_usuario_categoria_data`, `ix_movimentacao_usuario_data`, `ix_movimentacao_usuario_tipo_data`, `pk_movimentacao_financeira`, `uq_movimentacao_financeira_importancia_id` |
| `lembrete_importancia` | 9 | `ck_lembrete_importancia_antecedencia`, `ck_lembrete_importancia_enviado`, `ck_lembrete_importancia_situacao`, `fk_lembrete_importancia_importancia_id_importancia`, `fk_lembrete_importancia_usuario_id_usuario`, `ix_lembrete_situacao_agendado`, `pk_lembrete_importancia`, `uq_lembrete_importancia_id_usuario_id`, `uq_lembrete_importancia_importancia_id` |
| `notificacao` | 5 | `fk_notificacao_lembrete_id_lembrete_importancia`, `fk_notificacao_usuario_id_usuario`, `ix_notificacao_usuario_lida_criada`, `pk_notificacao`, `uq_notificacao_lembrete_id_versao_agendamento` |
| `requisicao_idempotente` | 4 | `ck_requisicao_idempotente_situacao`, `fk_requisicao_idempotente_usuario_id_usuario`, `pk_requisicao_idempotente`, `uq_requisicao_idempotente_usuario_id_acao_chave` |

### 6.6. Arquivos de modelo e `models/__init__.py`

- Um arquivo por tabela, com o nome da tabela: `models/usuario.py` (hoje vazio), `models/recuperacao_senha.py`, `models/categoria_atividade.py`, `models/serie_atividade.py`, `models/atividade.py`, `models/categoria_importancia.py`, `models/serie_importancia.py`, `models/importancia.py`, `models/categoria_financeira.py`, `models/movimentacao_financeira.py`, `models/lembrete_importancia.py`, `models/notificacao.py` e `models/requisicao_idempotente.py`.
- Classes: `Usuario`, `RecuperacaoSenha`, `CategoriaAtividade`, `SerieAtividade`, `Atividade`, `CategoriaImportancia`, `SerieImportancia`, `Importancia`, `CategoriaFinanceira`, `MovimentacaoFinanceira`, `LembreteImportancia`, `Notificacao` e `RequisicaoIdempotente`.
- Herança: `class X(CriadoAtualizadoMixin, Base)` nas 8 tabelas marcadas; `class X(Base)` nas demais.
- Cada arquivo e cada classe têm docstring curta em PT-BR.
- `models/__init__.py`: docstring `"""Modelos ORM da API MinhaVida (13 tabelas da F2)."""`, importa `Base`, `CriadoAtualizadoMixin`, as 7 enumerações e as 13 classes, e define `__all__` com esses 22 nomes em ordem alfabética. O `env.py` importa `api_gestao_pessoal.models`. Por isso, sem esse import, o `Base.metadata` ficaria incompleto e o autogenerate e o `alembic check` falhariam.

## 7. Arquivos permitidos, novos e protegidos

### 7.1. Alterar (existentes)

| Arquivo | Alteração |
| --- | --- |
| `pyproject.toml` | Somente §9 |
| `src/api_gestao_pessoal/models/base.py` | §6.1 |
| `src/api_gestao_pessoal/models/__init__.py` | §6.6 |
| `src/api_gestao_pessoal/models/usuario.py` | §6.4.1 |
| `tests/conftest.py` | Somente acrescentar `banco_migrado` e os imports dela (§10.1) |
| `tests/apoio/banco.py` | Somente acrescentar `TABELAS_DOMINIO` e `limpar_dados` (§10.2) |
| `tests/infra/test_alembic_ambiente.py` | Somente CT-F1-17 (§10.6) |

### 7.2. Criar

```text
src/api_gestao_pessoal/models/enums.py
src/api_gestao_pessoal/models/recuperacao_senha.py
src/api_gestao_pessoal/models/categoria_atividade.py
src/api_gestao_pessoal/models/serie_atividade.py
src/api_gestao_pessoal/models/atividade.py
src/api_gestao_pessoal/models/categoria_importancia.py
src/api_gestao_pessoal/models/serie_importancia.py
src/api_gestao_pessoal/models/importancia.py
src/api_gestao_pessoal/models/categoria_financeira.py
src/api_gestao_pessoal/models/movimentacao_financeira.py
src/api_gestao_pessoal/models/lembrete_importancia.py
src/api_gestao_pessoal/models/notificacao.py
src/api_gestao_pessoal/models/requisicao_idempotente.py
alembic/versions/<AAAAMMDD>_0001_esquema_inicial.py
tests/apoio/migracoes.py
tests/apoio/esquema.py
tests/esquema/__init__.py
tests/esquema/conftest.py
tests/esquema/test_migracao.py
tests/esquema/test_estrutura.py
tests/esquema/test_identificadores.py
tests/esquema/test_restricoes.py
tests/esquema/test_tipos_e_tempos.py
```

`<AAAAMMDD>` é a data em que o Alembic gerar o arquivo (§8.1). Deve existir **um único** arquivo em `alembic/versions/` além do `.gitkeep`, que permanece.

### 7.3. Protegidos (não alterar)

`CLAUDE.md`, `.env`, `.env.exemplo`, `.gitignore`, `README.md`, `compose.yaml`, `uv.lock`, `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `docs/**`, `PROMPTS/**`, todo o `src/` fora de `models/`, `tests/apoio/rotas_teste.py`, `tests/infra/*` (exceto CT-F1-17 em `test_alembic_ambiente.py`) e todo o `pyproject.toml` fora de §9.

## 8. Migração inicial (revisão `0001`)

### 8.1. Geração

Gere o esqueleto por autogenerate, **somente** contra um PostgreSQL descartável, com o comando de §13, passo 5. Ele sobe um container `postgres:15-alpine` vazio, passa a URL por `config.attributes["url_banco"]` e cria `alembic/versions/<AAAAMMDD>_0001_esquema_inicial.py` com `rev_id="0001"`. Nunca use `alembic revision --autogenerate` pela CLI (§0, item 6).

### 8.2. Conteúdo obrigatório e revisão manual

Depois de gerar, revise e edite o arquivo até que cumpra **todos** os itens:

1. Docstring do módulo: `"""Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2)."""`, seguida das linhas `Revision ID: 0001`, `Revises:` e `Create Date:` geradas.
2. `revision: str = "0001"` e `down_revision: Union[str, Sequence[str], None] = None`.
3. `upgrade()`:
   - 13 `op.create_table(...)` em ordem compatível com as FKs (a ordem do autogenerate serve);
   - cada coluna com o tipo, a nulabilidade e o `server_default` de §6.4;
   - `sa.Uuid()` nas 32 colunas de identificador, **sem** `server_default`, `sa.Identity` ou `autoincrement`;
   - enumerações como `sa.Enum(<valores>, name="<coluna>", native_enum=False, create_constraint=True, length=<n>)`. O CHECK delas vem do tipo; **não** escreva outro;
   - os demais CHECKs, UNIQUEs, PKs e FKs com `name=op.f("<nome completo de §6.5>")`;
   - FKs com `ondelete="RESTRICT"`;
   - 8 `op.create_index(op.f("<nome>"), "<tabela>", [<colunas na ordem de §6.4>], unique=False)`;
   - ao fim, os seeds de §8.3.
4. `downgrade()`: remove os 8 índices e as 13 tabelas na ordem inversa da criação. Sem `DELETE` nem outras operações de dados.
5. Nada de `import api_gestao_pessoal`, SQL textual de DDL, triggers ou extensões.
6. Nenhuma operação além das acima (por exemplo, `alter_column` ou `drop` de objetos estranhos). Se o autogenerate produzir algo assim, **pare e relate**.

### 8.3. Seeds (código exato, no módulo da revisão)

```python
CATEGORIAS_ATIVIDADE = (
    "Trabalho", "Estudo", "Saúde", "Pessoal", "Lazer", "Outros",
)
CATEGORIAS_IMPORTANCIA = (
    "Contas", "Compras", "Veículo", "Lazer", "Saúde", "Educação",
    "Pessoal", "Outros",
)
CATEGORIAS_RECEITA = (
    "Salário", "Trabalho autônomo", "Vendas", "Rendimentos",
    "Reembolsos", "Outros",
)
CATEGORIAS_DESPESA = (
    "Alimentação", "Transporte", "Moradia", "Contas", "Compras", "Saúde",
    "Educação", "Lazer", "Veículo", "Outros",
)


def instrucoes_categorias() -> list[Insert]:
    """INSERTs idempotentes das 30 categorias, com UUIDv7 gerado agora."""
    categoria_atividade = sa.table(
        "categoria_atividade",
        sa.column("id", sa.Uuid()),
        sa.column("nome", sa.String()),
    )
    categoria_importancia = sa.table(
        "categoria_importancia",
        sa.column("id", sa.Uuid()),
        sa.column("nome", sa.String()),
    )
    categoria_financeira = sa.table(
        "categoria_financeira",
        sa.column("id", sa.Uuid()),
        sa.column("tipo", sa.String()),
        sa.column("nome", sa.String()),
    )
    financeiras = [
        {"id": uuid.uuid7(), "tipo": "RECEITA", "nome": nome}
        for nome in CATEGORIAS_RECEITA
    ] + [
        {"id": uuid.uuid7(), "tipo": "DESPESA", "nome": nome}
        for nome in CATEGORIAS_DESPESA
    ]
    return [
        insert(categoria_atividade)
        .values([
            {"id": uuid.uuid7(), "nome": nome}
            for nome in CATEGORIAS_ATIVIDADE
        ])
        .on_conflict_do_nothing(index_elements=["nome"]),
        insert(categoria_importancia)
        .values([
            {"id": uuid.uuid7(), "nome": nome}
            for nome in CATEGORIAS_IMPORTANCIA
        ])
        .on_conflict_do_nothing(index_elements=["nome"]),
        insert(categoria_financeira)
        .values(financeiras)
        .on_conflict_do_nothing(index_elements=["tipo", "nome"]),
    ]
```

- Imports no módulo: `import uuid` e `from sqlalchemy.dialects.postgresql import Insert, insert`, além dos gerados.
- No fim de `upgrade()`: `for instrucao in instrucoes_categorias(): op.execute(instrucao)`.
- `ativa` não é informada: o padrão `true` do banco se aplica.
- As grafias, inclusive acentos, são exatamente as do `CLAUDE.md`. Os IDs variam entre ambientes. O código nunca depende deles (ADR-0002 §4.5).
- `op.execute` funciona também no modo offline. A função é reexecutável sem duplicar (CT-F2-07).

## 9. Configuração: ACH-MV-F1-005, opção A (alteração exata do `pyproject.toml`)

Três alterações, e nenhuma outra linha muda:

```diff
@@ [tool.ruff]
 exclude = [
     "venv",
     ".venv",
     "env",
     ".env",
     "__pycache__",
     ".pytest_cache",
     ".ruff_cache",
     ".mypy_cache",
-    "alembic",
 ]
@@ [tool.ruff.lint.per-file-ignores]
 # Asserções de teste comparam contra valores esperados literais (ex:
 # contagens); não há constante nomeada sensata para extrair aqui.
 "tests/*" = ["PLR2004"]
+# O env.py importa as Settings dentro de obter_url() para só ler o
+# ambiente quando a URL não vem de config.attributes (ACH-MV-F1-005).
+"alembic/env.py" = ["PLC0415"]
@@ [tool.pyright]
-include = ["src", "tests"]
+include = ["src", "tests", "alembic"]
```

- Sem dependência nova. `uv.lock` inalterado (§13, passos 1 e 16).
- Se o Ruff ou o Pyright exigirem qualquer outra exceção, `noqa` ou `pyright: ignore` em `alembic/` ou em qualquer arquivo, **pare e relate**.

## 10. Testes: apoio, fixtures e casos

### 10.1. `tests/apoio/migracoes.py` (novo, conteúdo exato) e `banco_migrado`

```python
"""Apoio de testes: configuração do Alembic contra o banco descartável."""

from pathlib import Path

from alembic.config import Config

RAIZ = Path(__file__).resolve().parents[2]
ALEMBIC_INI = RAIZ / "alembic.ini"
REVISAO_INICIAL = "0001"


def config_alembic(url: str) -> Config:
    """Config do Alembic com a URL do container, sem logging de arquivo."""
    cfg = Config(str(ALEMBIC_INI))
    cfg.attributes["url_banco"] = url
    cfg.attributes["configurar_logging"] = False
    return cfg
```

Em `tests/conftest.py`, acrescente só esta fixture e seus imports (`from alembic import command` e `from .apoio.migracoes import config_alembic`):

```python
@pytest.fixture(scope="session")
def banco_migrado(
    container_postgres: PostgresContainer, url_banco_teste: str
) -> str:
    """Aplica `upgrade head` uma vez por sessão e devolve a URL."""
    garantir_banco_descartavel(url_banco_teste, container_postgres)
    command.upgrade(config_alembic(url_banco_teste), "head")
    return url_banco_teste
```

### 10.2. `tests/apoio/banco.py` (acréscimo exato)

```python
import psycopg
from psycopg import sql

TABELAS_DOMINIO = (
    "notificacao",
    "lembrete_importancia",
    "movimentacao_financeira",
    "importancia",
    "serie_importancia",
    "atividade",
    "serie_atividade",
    "recuperacao_senha",
    "requisicao_idempotente",
    "usuario",
)


def limpar_dados(url: str, container: PostgresContainer) -> None:
    """Esvazia as tabelas de domínio; preserva catálogos e alembic_version.

    Sem RESTART IDENTITY (não há identidades) e sem CASCADE: uma lista
    incompleta falha, em vez de apagar outra tabela (REC-MV-034).
    """
    garantir_banco_descartavel(url, container)
    instrucao = sql.SQL("TRUNCATE {}").format(
        sql.SQL(", ").join(sql.Identifier(t) for t in TABELAS_DOMINIO)
    )
    with psycopg.connect(url_libpq(url), autocommit=True) as conexao:
        conexao.execute(instrucao)
```

Os imports novos vão para o bloco de imports do topo do arquivo, na ordem que o Ruff exigir.

### 10.3. `tests/apoio/esquema.py` (novo)

Conteúdo obrigatório:

- Constantes: `SQLSTATE_NOT_NULL = "23502"`, `SQLSTATE_FK = "23503"`, `SQLSTATE_UNICO = "23505"`, `SQLSTATE_CHECK = "23514"`, `SQLSTATE_TEXTO_LONGO = "22001"`, `SQLSTATE_NUMERICO_EXCEDIDO = "22003"` e `MOMENTO = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)`.
- `def esperar_violacao(conexao: Connection, sqlstate: str, acao: Callable[[], object]) -> None`: executa `acao()` dentro de `conexao.begin_nested()`, com `pytest.raises(DBAPIError)`, e afirma `getattr(info.value.orig, "sqlstate", None) == sqlstate`. O `SAVEPOINT` mantém a transação externa utilizável.
- `def inserir(conexao: Connection, tabela: str, valores: Mapping[str, object]) -> None`: `INSERT INTO <tabela> (<colunas>) VALUES (:<colunas>)` com `text()` e parâmetros vinculados.
- `def consultar(url: str, instrucao: LiteralString) -> list[tuple[Any, ...]]`: conexão psycopg **independente** (`url_libpq`), usada pelos testes de migração.
- `def id_categoria(conexao: Connection, tabela: str, nome: str, tipo: str | None = None) -> uuid.UUID`.
- Fábricas de linhas válidas. Cada uma gera `id = uuid.uuid7()`, insere por SQL textual (o `id` é informado, ADR-0002 §4.3) e devolve o `id`. Os `campos` sobrescrevem os padrões, inclusive com `None`; `campos` não aceita `id`.

| Fábrica | Valores padrão (fictícios) |
| --- | --- |
| `inserir_usuario(conexao, **campos)` | `nome_completo="Pessoa Teste"`, `email=f"{uuid.uuid7().hex}@exemplo.com"`, `senha_hash="hash-ficticio"`, `data_nascimento=date(1990, 1, 1)`, `fuso_horario="America/Sao_Paulo"` |
| `inserir_serie_atividade(conexao, usuario_id, **campos)` | categoria `Estudo`, `nome_padrao="Estudar"`, `periodicidade="SEMANAL"`, `data_referencia=date(2026, 10, 8)`, `horario_inicial_padrao=time(8, 0)`, `horario_final_padrao=time(10, 0)` |
| `inserir_atividade(conexao, usuario_id, **campos)` | categoria `Estudo`, `nome="Estudar para a prova"`, `data_atividade=date(2026, 10, 8)`, `horario_inicial=time(8, 0)`, `horario_final=time(10, 0)` |
| `inserir_serie_importancia(conexao, usuario_id, **campos)` | categoria `Contas`, `nome_padrao="Pagamento da internet"`, `periodicidade="MENSAL"`, `data_referencia=date(2026, 10, 15)` |
| `inserir_importancia(conexao, usuario_id, **campos)` | categoria `Contas`, `nome="Pagamento da internet"`, `data_compromisso=date(2026, 10, 15)` |
| `inserir_movimentacao(conexao, usuario_id, **campos)` | `tipo="DESPESA"`, `nome="Pagamento da internet"`, `valor=Decimal("105.00")`, `data_movimentacao=date(2026, 10, 15)`. Sem `categoria_id` em `campos`: (`DESPESA`, `Contas`) quando `tipo` é `DESPESA` ou ausente; (`RECEITA`, `Salário`) quando `tipo` é `RECEITA` |
| `inserir_lembrete(conexao, usuario_id, importancia_id, **campos)` | `antecedencia_dias=3`, `horario=time(9, 0)`, `agendado_para=datetime(2026, 10, 12, 12, 0, tzinfo=UTC)` |
| `inserir_notificacao(conexao, usuario_id, lembrete_id, **campos)` | `versao_agendamento=1`, `titulo="Lembrete"`, `mensagem="Pagamento da internet"` |
| `inserir_recuperacao(conexao, usuario_id, **campos)` | `codigo_hash="hash-ficticio"`, `expira_em=datetime(2026, 10, 13, 12, 10, tzinfo=UTC)` |
| `inserir_requisicao(conexao, usuario_id, **campos)` | `chave=uuid.uuid7().hex`, `acao="CADASTRAR_DESPESA"`, `conteudo_hash="0" * 64` |

As fábricas omitem as colunas com padrão no servidor, salvo quando vêm em `campos`.

### 10.4. `tests/esquema/conftest.py` (novo)

| Fixture | Escopo | Contrato |
| --- | --- | --- |
| `conexao` | função, síncrona | `create_engine(banco_migrado, poolclass=NullPool)`. `engine.connect()` e `transacao = c.begin()`. `yield c`. No `finally`: `transacao.rollback()` e `engine.dispose()`. Nada persiste |
| `sessao_orm` | função, async | `create_async_engine(banco_migrado, poolclass=NullPool)` e `criar_fabrica_sessoes(engine)()` (`api_gestao_pessoal.database`). `yield` da sessão. No `finally`: `await sessao.rollback()` e `await engine.dispose()` |
| `fabrica_sessoes` | função, async | Mesma engine e `yield criar_fabrica_sessoes(engine)`. No `finally`: `await engine.dispose()` e `limpar_dados(banco_migrado, container_postgres)`. Uso exclusivo de CT-F2-19 |
| `config_migracao` | função, síncrona | `garantir_banco_descartavel(banco_migrado, container_postgres)` e `return config_alembic(banco_migrado)` |

Os testes que rodam `downgrade` **não** pedem `conexao`, `sessao_orm` nem `fabrica_sessoes`: uma transação aberta bloquearia o `DROP TABLE`. Eles consultam o banco com `consultar(...)`, depois de cada comando. Todo teste que rode `downgrade` restaura `head` em `finally`.

### 10.5. Casos e expectativas

Nomes de arquivos e funções obrigatórios. Quando a coluna Dados lista vários casos, eles podem estar na mesma função, ou em `pytest.mark.parametrize` com `ids` descritivos. Cada caso negativo usa `esperar_violacao` com o SQLSTATE indicado, e cada grupo tem os controles positivos listados. A verificação é sempre feita no banco, nunca só pelo metadata.

**`tests/esquema/test_migracao.py`**

| CT | Função | Dados e expectativa |
| --- | --- | --- |
| CT-F2-01 | `test_upgrade_head_cria_esquema_em_banco_vazio` | `command.downgrade(config_migracao, "base")` → `consultar(url, "SELECT tablename FROM pg_tables WHERE schemaname = 'public'")` = `{alembic_version}`. `command.upgrade(..., "head")` → as 13 tabelas de domínio + `alembic_version`, e `SELECT version_num FROM alembic_version` = `[("0001",)]`. `finally`: `upgrade head` |
| CT-F2-06 | `test_categorias_iniciais_exatas` | Usa `conexao`. `categoria_atividade.nome` = os 6 nomes de §8.3; `categoria_importancia.nome` = os 8; `categoria_financeira (tipo, nome)` = 6 de `RECEITA` + 10 de `DESPESA`, igual a §8.3. Total 30, todas com `ativa = true`. `Outros` aparece duas vezes em `categoria_financeira`, uma por tipo, com `id` diferente |
| CT-F2-07 | `test_seeds_idempotentes` | (1) `command.upgrade(..., "head")` de novo: `version_num` continua `0001` e as contagens 6/8/16 não mudam. (2) `script = ScriptDirectory.from_config(cfg).get_revision("0001")`. Com `conexao`, executar cada item de `script.module.instrucoes_categorias()`: as contagens continuam 6/8/16. (3) `Path(script.path).read_text(encoding="utf-8")` não contém `api_gestao_pessoal` |
| CT-F2-08 | `test_downgrade_base_e_upgrade_head` | `downgrade base` → só `alembic_version`, com 0 linhas. `upgrade head` → 13 tabelas, `0001` e 30 categorias. `finally`: `upgrade head` |
| CT-F2-09 | `test_alembic_check_sem_diferencas` | `command.check(config_migracao)` sem exceção |

**`tests/esquema/test_estrutura.py`** (todos com `conexao`)

| CT | Função | Dados e expectativa |
| --- | --- | --- |
| CT-F2-02 | `test_colunas_conforme_contrato` | Consulta: `SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod), a.attnotnull, pg_get_expr(d.adbin, d.adrelid) FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid JOIN pg_namespace n ON n.oid = c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname <> 'alembic_version' AND a.attnum > 0 AND NOT a.attisdropped ORDER BY c.relname, a.attnum`. Compare com a constante **literal** `COLUNAS_ESPERADAS: dict[str, tuple[tuple[str, str, bool, str \| None], ...]]` (coluna, tipo, obrigatória, padrão), **transcrita de §6.4** na ordem das colunas. 13 tabelas e 134 colunas. **Proibido** derivar a expectativa do `Base.metadata` |
| CT-F2-03 | `test_identificadores_uuid_sem_padrao` | Exatamente 32 colunas `uuid`: as 13 `id` e as 19 FKs (`recuperacao_senha.usuario_id`; `serie_atividade.usuario_id`, `categoria_id`; `atividade.usuario_id`, `categoria_id`, `serie_id`; `serie_importancia.usuario_id`, `categoria_id`; `importancia.usuario_id`, `categoria_id`, `serie_id`; `movimentacao_financeira.usuario_id`, `categoria_id`, `importancia_id`; `lembrete_importancia.usuario_id`, `importancia_id`; `notificacao.usuario_id`, `lembrete_id`; `requisicao_idempotente.usuario_id`), em conjunto literal. As 13 PKs (`contype = 'p'`) cobrem só `id`, sem padrão |
| CT-F2-10 | `test_nomes_de_restricoes_e_indices` | Nomes no banco: `conname` de `pg_constraint` das tabelas de `public` (exceto `alembic_version`), mais os índices dessas tabelas sem constraint (`NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conindid = x.indexrelid)`). Igual ao conjunto **literal** de §6.5 (93 nomes, sem repetição) e igual ao conjunto do metadata (`str(c.name)` de `t.constraints` e `str(i.name)` de `t.indexes`). Todos ≤ 63 caracteres. Ordem das colunas dos 8 índices: `SELECT i.relname, t.relname, array_agg(a.attname ORDER BY k.ordem) FROM pg_index x JOIN pg_class i ON i.oid = x.indexrelid JOIN pg_class t ON t.oid = x.indrelid CROSS JOIN LATERAL unnest(x.indkey::int2[]) WITH ORDINALITY AS k(attnum, ordem) JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum WHERE i.relname LIKE 'ix\_%' GROUP BY i.relname, t.relname` = as 8 tuplas literais de §6.4 |
| CT-F2-18 (a) | `test_fks_restrict` | `SELECT conname, confdeltype FROM pg_constraint WHERE contype = 'f' AND connamespace = 'public'::regnamespace` → 19 linhas, todas `'r'` |

**`tests/esquema/test_identificadores.py`**

| CT | Função | Dados e expectativa |
| --- | --- | --- |
| CT-F2-04 | `test_orm_gera_uuid_v7` | Usa `sessao_orm`. `Usuario(...)` com os campos obrigatórios, `add` e `flush`. `isinstance(u.id, uuid.UUID)` e `u.id.version == 7`. `criado_em` está preenchido e fora de `inspect(u).expired_attributes` |
| CT-F2-05 | `test_sql_textual_sem_id_rejeitado` | Usa `conexao`. INSERT textual sem `id` em `usuario` (com os outros campos obrigatórios) e em `categoria_atividade` (`nome='Teste'`) → `23502` |

**`tests/esquema/test_restricoes.py`** (todos com `conexao`; `A` e `B` são usuários criados no teste)

| CT | Função | Casos negativos → SQLSTATE | Controles positivos |
| --- | --- | --- | --- |
| CT-F2-11 | `test_fk_propriedade_atividade_serie` | Série de A; atividade de B com `serie_id` dessa série e `numero_ocorrencia=1` → `23503` | Mesma atividade com `usuario_id=A` |
| CT-F2-11 | `test_fk_propriedade_importancia_serie` | Igual, com `serie_importancia` e `importancia` → `23503` | `usuario_id=A` |
| CT-F2-11 | `test_fk_propriedade_movimentacao_importancia` | Importância de A (`possui_despesa=True`, `valor_previsto=Decimal("99.90")`); despesa de B com `importancia_id` dela e `importancia_vinculada_em=MOMENTO` → `23503` | Despesa de A com o mesmo vínculo |
| CT-F2-11 | `test_fk_propriedade_lembrete_importancia` | Lembrete de B para a importância de A → `23503` | Lembrete de A |
| CT-F2-11 | `test_fk_propriedade_notificacao_lembrete` | Notificação de B para o lembrete de A → `23503` | Notificação de A |
| CT-F2-12 | `test_fk_categoria_financeira_por_tipo` | `RECEITA` com a categoria (`DESPESA`, `Contas`) → `23503`; `DESPESA` com (`RECEITA`, `Salário`) → `23503` | `RECEITA` com (`RECEITA`, `Salário`). `Outros` existe nos dois tipos, com `id` diferente |
| CT-F2-13 | `test_ocorrencias_atividade` | `serie_id` preenchido e `numero_ocorrencia=None` → `23514`; `serie_id=None` e `numero_ocorrencia=1` → `23514`; número `0` → `23514`; segunda `(serie, 1)` → `23505`; `(serie, 2)` com `excluida_em=MOMENTO` e outra `(serie, 2)` → `23505` (a exclusão lógica não libera o par); `numero_final=-1` na série → `23514` | Duas avulsas do mesmo usuário (série e número nulos); `(serie, 1)`; série com `numero_final=0` |
| CT-F2-13 | `test_ocorrencias_importancia` | Os mesmos casos, com `serie_importancia` e `importancia` | Os mesmos |
| CT-F2-14 | `test_valor_da_movimentacao` | `valor=Decimal("0")` → `23514`; `Decimal("-0.01")` → `23514`; `None` → `23502` | `Decimal("0.01")` |
| CT-F2-14 | `test_valor_previsto_condicional` | `importancia`: (`possui_despesa=False`, `valor_previsto=Decimal("10")`) → `23514`; (`True`, `None`) → `23514`; (`True`, `Decimal("0")`) → `23514`; (`True`, `Decimal("-1")`) → `23514`. Os mesmos casos em `serie_importancia`, com `possui_despesa_padrao` e `valor_previsto_padrao` | (`True`, `Decimal("99.90")`) e (`False`, `None`), nas duas tabelas |
| CT-F2-14 | `test_vinculo_de_pagamento` | Com a importância de A (`possui_despesa=True`, `valor_previsto=Decimal("99.90")`): `importancia_id` sem `importancia_vinculada_em` → `23514`; `importancia_vinculada_em` sem `importancia_id` → `23514`; `RECEITA` vinculada → `23514`; `excluida_em=MOMENTO` com vínculo → `23514`; segunda despesa vinculada à mesma importância → `23505` | Despesa vinculada com os dois campos; despesa excluída sem vínculo |
| CT-F2-15 | `test_forma_por_tipo` | `RECEITA`+`CARTAO_DEBITO` → `23514`; `RECEITA`+`BOLETO` → `23514`; `DESPESA`+`DEPOSITO` → `23514`; `forma_movimentacao='CHEQUE'` → `23514` | `RECEITA`+`PIX`, `RECEITA`+`DEPOSITO`, `DESPESA`+`BOLETO`, `DESPESA`+`CARTAO_DEBITO` e forma `None` |
| CT-F2-15 | `test_horarios` | `atividade` e `serie_atividade` com final igual ao inicial (10:00–10:00) → `23514`; final antes do inicial (10:00–09:00) → `23514` | 08:00–08:01 nas duas |
| CT-F2-15 | `test_datas_e_numeros_de_serie` | Nas duas séries: `data_final_repeticao` um dia antes de `data_referencia` → `23514`; `numero_referencia=0` → `23514`; `numero_final=-1` → `23514` | `data_final_repeticao` igual a `data_referencia`; `numero_final=0` |
| CT-F2-15 | `test_nome_da_atividade` | `"ab"` → `23514`; `""` → `23514`; `None` → `23502`; `"x" * 101` → `22001` (o `VARCHAR(100)` barra antes do CHECK) | `"abc"`; `"x" * 100` |
| CT-F2-15 | `test_enumeracoes_invalidas` | `atividade.prioridade`: `'ALTO'` e `'baixa'` → `23514`; `serie_atividade.prioridade_padrao='ALTO'` → `23514`; `serie_atividade.periodicidade='ANUAL'` → `23514`; `serie_importancia.periodicidade='SEMANA'` → `23514`; nova `categoria_financeira` (`nome='Teste'`, `tipo='OUTRO'`) → `23514`; `movimentacao_financeira.tipo='OUTRO'`, com `categoria_id` explícito → `23514`; `lembrete_importancia.situacao='LIDO'` → `23514`; `requisicao_idempotente.situacao='PARADA'` → `23514`. Todos os valores inválidos cabem no `VARCHAR` da coluna, para que o erro venha do CHECK | `serie_importancia.periodicidade='ANUAL'`; `atividade.prioridade='ALTA'` |
| CT-F2-15 | `test_antecedencias` | `lembrete_importancia.antecedencia_dias=2` → `23514`; `serie_importancia` (`lembrete_antecedencia_dias=5`, `lembrete_horario=time(9, 0)`) → `23514`; (`3`, `None`) → `23514`; (`None`, `time(9, 0)`) → `23514` | Lembretes com `0`, `1`, `3` e `7`, um por importância; série com (`None`, `None`) e com (`7`, `time(9, 0)`) |
| CT-F2-15 | `test_situacao_e_envio_do_lembrete` | `ENVIADO` com `enviado_em=None` → `23514`; `PENDENTE` com `enviado_em=MOMENTO` → `23514`; `CANCELADO` com `enviado_em=MOMENTO` → `23514` | `ENVIADO` com `MOMENTO`; `CANCELADO` com `None` |
| CT-F2-15 | `test_conclusao_manual` | `possui_despesa=True`, `valor_previsto=Decimal("10")`, `concluida_manualmente_em=MOMENTO` → `23514` | `possui_despesa=False` com `concluida_manualmente_em=MOMENTO` |
| CT-F2-16 | `test_email_unico` | Dois usuários com o mesmo e-mail → `23505` | E-mails diferentes |
| CT-F2-16 | `test_recuperacao_unica_por_usuario` | Segunda recuperação do mesmo usuário → `23505` | Uma recuperação por usuário |
| CT-F2-16 | `test_token_redefinicao_unico` | O mesmo `token_redefinicao_hash` (`"a" * 64`) em dois usuários → `23505` | Dois usuários com token `None`; um usuário com o token |
| CT-F2-16 | `test_lembrete_unico_por_importancia` | Segundo lembrete da mesma importância → `23505` | Um lembrete |
| CT-F2-16 | `test_notificacao_por_versao` | Segunda notificação `(lembrete, 1)` → `23505` | Notificação v1; `UPDATE lembrete_importancia SET versao_agendamento = 2`; notificação v2 aceita; ao fim, 2 notificações do lembrete (a v1 permanece) |
| CT-F2-16 | `test_idempotencia_por_usuario_acao_chave` | `(A, 'CADASTRAR_DESPESA', k)` repetida → `23505` | `(A, 'CADASTRAR_RECEITA', k)`; `(B, 'CADASTRAR_DESPESA', k)` |
| CT-F2-18 (b) | `test_exclusao_fisica_de_categoria_referenciada` | Atividade com a categoria `Estudo`; `DELETE FROM categoria_atividade WHERE nome = 'Estudo'` → `23503` | — |
| CT-F2-20 | `test_nomes_dec_mv_08` | Para `importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao`: `"ab"` → `23514` e `""` → `23514` | `"abc"` em cada uma |

**`tests/esquema/test_tipos_e_tempos.py`**

| CT | Função | Dados e expectativa |
| --- | --- | --- |
| CT-F2-17 | `test_decimal_ida_e_volta` | Usa `conexao`. Movimentações com `Decimal("0.01")` e `Decimal("9999999999.99")`: lidas de volta como `Decimal` iguais, com `str()` igual a `"0.01"` e `"9999999999.99"`. `Decimal("10000000000.00")` → `22003` |
| CT-F2-17 | `test_json_none_vira_null_sql` | Usa `sessao_orm`. `Usuario` e `RequisicaoIdempotente(resposta=None)` pelo ORM, com `flush`. `SELECT resposta IS NULL` → `True` (SQL `NULL`, não JSON `null`). Outra requisição com `resposta={"id": "abc"}` → `SELECT resposta::text` = `'{"id": "abc"}'` |
| CT-F2-19 | `test_timestamps` | Usa `fabrica_sessoes`. (1) Transação 1: `t1 = SELECT now()`; `Usuario` com `add` e `flush`; `criado_em == atualizado_em == t1`; os dois atributos fora de `inspect(u).expired_attributes`; `commit`. (2) Transação 2: `t2 = SELECT now()`; `get(Usuario, id)`; muda `nome_completo`; `flush`; `atualizado_em` fora de `expired_attributes`, lido sem I/O e igual a `t2`; `criado_em == t1`; `t2 > t1`; `commit`. (3) Transação 3: `UPDATE usuario SET nome_completo = 'Pessoa Textual' WHERE id = :id` em SQL textual; `commit`. (4) Transação 4: o nome mudou e `atualizado_em` **continua** `t2`. (5) Transação 5: `t5 = SELECT now()`; insira por SQL textual, para o usuário do passo 1, uma importância, um lembrete dela e uma notificação desse lembrete sem `criada_em`, e uma requisição idempotente sem `criado_em`. `notificacao.criada_em` e `requisicao_idempotente.criado_em` lidos são iguais a `t5` |

### 10.6. Regressão CT-F1-17 (`tests/infra/test_alembic_ambiente.py`)

Somente:

- renomear `test_upgrade_head_sem_revisoes` para `test_upgrade_head_com_revisao_inicial`;
- trocar `assert ScriptDirectory.from_config(cfg).get_heads() == []` por `assert ScriptDirectory.from_config(cfg).get_heads() == [REVISAO_INICIAL]`, com `from ..apoio.migracoes import REVISAO_INICIAL`.

O restante do arquivo, inclusive `_config`, CT-F1-18 e CT-F1-19, não muda. Agora o `command.check(cfg)` de CT-F1-17 compara as 13 tabelas e deve continuar sem diferenças.

## 11. Critérios de aceite e bloqueios

**Aceite:**

- CT-F2-01 a CT-F2-20 passando, com os controles positivos e os casos `NULL` de §10.5.
- Regressões CT-F1-02 e CT-F1-17 a 19 passando.
- Ruff e Pyright limpos, agora incluindo `alembic/` (§13).
- `alembic heads` = `0001 (head)`.
- Compose válido com `--env-file /dev/null`.
- `uv.lock`, os arquivos protegidos e os 11 documentos de §1.2 inalterados.

**Reprovação (qualquer um):**

- `commit()` em `src/`; `create_all`, `drop_all` ou `stamp`; `relationship()`.
- `default=` no ORM além do `id`; `TimestampMixin` remanescente.
- Coluna, constraint ou índice fora de §6, nome diferente de §6.5 ou com mais de 63 caracteres.
- FK sem `RESTRICT` ou com `CASCADE`/`SET NULL`.
- Revisão que importe `api_gestao_pessoal`, ou seeds fora de §8.3.
- CT-F2-02 com a expectativa derivada do metadata; ausência dos casos `NULL`.
- Teste pulado ou `xfail`; suíte completa ou `task`.
- Leitura do `.env`; Alembic pela CLI em comando que execute o `env.py`; conexão ao banco de desenvolvimento.
- Arquivo protegido alterado; `noqa`, `pyright: ignore` ou exceção de configuração fora de §9.

**Bloqueios: pare e relate, sem contornar:**

- Divergência na Etapa A ou na revalidação (§1.2 e §1.3).
- Docker indisponível.
- O autogenerate produziu operação fora de §8.2, item 6.
- `alembic check` acusa diferença com a revisão conforme §6. Não mude `env.py`, `compare_type` nem `compare_server_default`.
- Um valor literal deste prompt (por exemplo, a introspecção de CT-F2-02 ou um SQLSTATE) diverge do comportamento real do PostgreSQL. Registre o valor observado exato e **não** ajuste a expectativa por conta própria.
- API das bibliotecas diferente da descrita em §1.1.
- Necessidade de dependência nova, de exceção de qualidade ou de alteração de arquivo protegido.

## 12. Etapa A: leitura, análise e autorização

Somente leitura, sem criar nem alterar arquivos no repositório:

1. `pwd`, `git status --short --branch`, `git rev-parse HEAD` e `git rev-parse HEAD^`. Determine o modo (A ou B) e confira §1.2.
2. `sha256sum` dos arquivos de §1.1 (cópia de trabalho e `git show 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30:<arquivo> | sha256sum`) e dos 11 documentos de §1.2, inclusive este prompt.
3. Leitura das fontes de §2, com o SHA-256 de cada uma.
4. `uv --version`, `uv run python --version` e `docker version --format '{{.Server.Version}}'`.
5. `uv run python -c "import uuid, sqlalchemy, alembic; from alembic.operations import Operations; from sqlalchemy.dialects.postgresql import insert; print(uuid.uuid7().version, sqlalchemy.__version__, alembic.__version__, hasattr(Operations, 'f'))"` → `7 2.1.4 1.20.0 True`.
6. `rg -n "TimestampMixin|created_at|updated_at" src tests alembic` → somente `src/api_gestao_pessoal/models/base.py`.
7. `rg -n "get_heads\(\) == \[\]" tests` → somente `tests/infra/test_alembic_ambiente.py`.
8. `ls alembic/versions` → somente `.gitkeep`.

> Emenda operacional (Etapa A, 2026-10-13): usar `ls -A1 alembic/versions`; `ls` sem `-A` não mostra `.gitkeep`.

Resposta da Etapa A:

- divergências encontradas, ou “nenhuma”;
- modo (A ou B), `HEAD` e o resultado dos passos 1 e 2;
- SHA-256 deste prompt e de cada fonte de §2;
- lista final de arquivos (§7) e de comandos (§13);
- riscos;
- pedido explícito: **“Aguardo ‘pode implementar’ para a F2.”**

**Não implemente antes dessa resposta do usuário.**

## 13. Etapa B: ordem e comandos exatos

Execute na raiz do repositório, nesta ordem. Os logs ficam em `$HOME/minhavida_evidencias/f2/`. Os passos 3 e 6 são só edições de arquivos e não geram log. O passo 2 combina a edição com o comando de log. O passo 10 só roda se o passo 9 alterou algum `.py`.

```bash
# 0. Revalidação do baseline (§1.3), antes de qualquer alteração.
mkdir -p "$HOME/minhavida_evidencias/f2"

# 1. Hash do uv.lock antes.
sha256sum uv.lock > "$HOME/minhavida_evidencias/f2/01_uvlock_antes.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/01_uvlock_antes.log"

# 2. pyproject.toml conforme §9 (edição). Depois:
git diff -- pyproject.toml > "$HOME/minhavida_evidencias/f2/02_diff_pyproject.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/02_diff_pyproject.log"

# 3. enums.py, base.py, os 13 modelos e models/__init__.py (§6), por edição.
# 4. Conferência do metadata, sem banco:
uv run python -c "from api_gestao_pessoal.models import Base; t = Base.metadata.tables; print(len(t), sum(len(x.columns) for x in t.values()), len({str(c.name) for x in t.values() for c in x.constraints} | {str(i.name) for x in t.values() for i in x.indexes}))" > "$HOME/minhavida_evidencias/f2/04_metadata.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/04_metadata.log"

# 5. Revisão 0001 por autogenerate, contra PostgreSQL descartável (§8.1).
uv run python - > "$HOME/minhavida_evidencias/f2/05_autogenerate.log" 2>&1 <<'EOF'
"""Gera a revisão 0001 por autogenerate contra um PostgreSQL descartável."""
import secrets

from alembic import command
from alembic.config import Config
from testcontainers.community.postgres import PostgresContainer

with PostgresContainer(
    "postgres:15-alpine",
    username="minhavida",
    password=secrets.token_urlsafe(16),
    dbname="minhavida_teste",
    driver="psycopg",
) as pg:
    cfg = Config("alembic.ini")
    cfg.attributes["url_banco"] = pg.get_connection_url()
    cfg.attributes["configurar_logging"] = False
    command.revision(
        cfg, message="esquema inicial", autogenerate=True, rev_id="0001"
    )
EOF
echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/05_autogenerate.log"
cp alembic/versions/*_0001_esquema_inicial.py "$HOME/minhavida_evidencias/f2/05_revisao_gerada.py"

# 6. Edição da revisão (§8.2 e §8.3) e dos testes (§10).

# 7. Testes da fase.
uv run pytest tests/esquema -q --color=no > "$HOME/minhavida_evidencias/f2/07_pytest_esquema.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/07_pytest_esquema.log"

# 8. Regressões.
uv run pytest tests/infra/test_alembic_ambiente.py tests/infra/test_configuracao.py::test_importacao_sem_efeitos -q --color=no > "$HOME/minhavida_evidencias/f2/08_pytest_regressoes.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/08_pytest_regressoes.log"

# 9. Correções do implementador (CLAUDE.md §2). Depois, conferir o escopo.
uv run ruff check --fix . > "$HOME/minhavida_evidencias/f2/09a_ruff_fix.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/09a_ruff_fix.log"
uv run ruff format . > "$HOME/minhavida_evidencias/f2/09b_ruff_format.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/09b_ruff_format.log"
git status --short > "$HOME/minhavida_evidencias/f2/09c_status.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/09c_status.log"

# 10. SOMENTE se o passo 9 alterou algum .py: repetir 7 e 8 com sufixo _2.
uv run pytest tests/esquema -q --color=no > "$HOME/minhavida_evidencias/f2/07_pytest_esquema_2.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/07_pytest_esquema_2.log"
uv run pytest tests/infra/test_alembic_ambiente.py tests/infra/test_configuracao.py::test_importacao_sem_efeitos -q --color=no > "$HOME/minhavida_evidencias/f2/08_pytest_regressoes_2.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/08_pytest_regressoes_2.log"

# 11 a 13. Verificação, sem alterar arquivos.
uv run ruff check --no-fix . > "$HOME/minhavida_evidencias/f2/11_ruff_check.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/11_ruff_check.log"
uv run ruff format --check . > "$HOME/minhavida_evidencias/f2/12_ruff_format_check.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/12_ruff_format_check.log"
uv run pyright > "$HOME/minhavida_evidencias/f2/13_pyright.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/13_pyright.log"

# 14. Alembic sem banco e sem env.py.
uv run alembic heads > "$HOME/minhavida_evidencias/f2/14a_alembic_heads.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/14a_alembic_heads.log"
uv run alembic history > "$HOME/minhavida_evidencias/f2/14b_alembic_history.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/14b_alembic_history.log"

# 15. Compose com dotenv neutro (ACH-MV-F1-007).
POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet > "$HOME/minhavida_evidencias/f2/15_compose_config.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/15_compose_config.log"

# 16. uv.lock depois (igual ao passo 1).
sha256sum uv.lock > "$HOME/minhavida_evidencias/f2/16_uvlock_depois.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/16_uvlock_depois.log"

# 17. Imagem de teste.
docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine > "$HOME/minhavida_evidencias/f2/17_digest.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/17_digest.log"

# 18. Objeto entregue.
git status --porcelain --untracked-files=all > "$HOME/minhavida_evidencias/f2/18a_status.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/18a_status.log"
git diff --stat 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30 > "$HOME/minhavida_evidencias/f2/18b_diff_stat.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/18b_diff_stat.log"
git status --porcelain --untracked-files=all | cut -c4- | grep -v '^PROMPTS/\|^docs/\|^CLAUDE.md$' | xargs -d '\n' sha256sum > "$HOME/minhavida_evidencias/f2/18c_sha256_f2.log" 2>&1; echo "codigo_saida=$?" >> "$HOME/minhavida_evidencias/f2/18c_sha256_f2.log"
sha256sum "$HOME"/minhavida_evidencias/f2/*.log "$HOME/minhavida_evidencias/f2/05_revisao_gerada.py" > "$HOME/minhavida_evidencias/f2_sha256_logs.txt"
```

| # | Expectativa |
| --- | --- |
| 0 | Todos os passos de §1.3 coincidem. Senão, **pare**. Bloco gravado em `00_revalidacao.log` |
| 1 e 16 | O mesmo SHA-256: `b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d  uv.lock` |
| 2 | Diff só com as três alterações de §9 |
| 4 | `13 134 93` e `codigo_saida=0` |
| 5 | `codigo_saida=0` e um único `alembic/versions/<AAAAMMDD>_0001_esquema_inicial.py` |
| 7 e 8 | 100 % passando, sem pulados. Registrar contagem e duração |
| 9 | Correções só em arquivos de §7. Se aparecer arquivo fora do escopo em `09c_status.log`, **pare** |
| 11 | `All checks passed!` |
| 12 | Nenhum arquivo a reformatar |
| 13 | `0 errors, 0 warnings, 0 informations` |
| 14 | `0001 (head)` e `<base> -> 0001 (head), esquema inicial` |
| 15 | `codigo_saida=0` e nenhuma outra linha |
| 18 | `18a` com os arquivos de §7 e os 11 de §1.2 (modo A), ou só os de §7 (modo B). Nada mais |

> Errata (auditoria F2, 2026-10-13): a saída correta do passo 14b é `<base> -> 0001 (head), Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).`. O `alembic history` mostra o primeiro parágrafo da docstring exigida em §8.2, item 1; a expectativa original refletia a revisão gerada, antes da edição. (ACH-MV-F2-001)

> Erratas (auditoria F2): (a) §6.2 é exato salvo a formatação do `ruff format`; (b) se `ruff check --fix` deixar erros, corrigir à mão e repetir 09a–09c com sufixo `_2`, preservando os originais; (c) o `id` segue o modelo do §6.4, sem `nullable=` (a PK implica NOT NULL); (d) comandos `uv run` devem usar `--frozen --no-sync` nos próximos prompts. (ACH-MV-F2-002)

## 14. Relatório com evidências reais

Conforme `plano_validacao_auditoria.md` §6, mais as lições da F1:

1. **Objeto entregue, em duas partes:**
   - (i) alterações documentais de preparação: os 11 arquivos de §1.2, com SHA-256 **inalterados**;
   - (ii) alterações da F2: lista de arquivos alterados e criados (§7), com o SHA-256 de cada um (`18c`), e `git diff --stat` contra `90412ec` (`18b`);
   - modo (A ou B), `HEAD` e o bloco “Revalidação do baseline” (§1.3).
2. Ambiente: uv, Python, Docker e digest da imagem (`17`).
3. Para cada passo de §13, na ordem:
   - o comando literal;
   - o `codigo_saida`;
   - as linhas finais do log copiadas **sem edição** (a linha de resumo do pytest, a do Ruff e a do Pyright);
   - o caminho do log.
   Inclua o arquivo `f2_sha256_logs.txt`.
4. Tabela CT → node ID → resultado, com CT-F1-02 e CT-F1-17 a 19.
5. A revisão: o diff entre `05_revisao_gerada.py` e a versão final, com uma explicação curta de cada edição de §8.2 e §8.3.
6. Testes não executados e o motivo. Distinga “não executado”, “inconclusivo”, “falhou” e “passou”.
7. Desvios: nenhum é permitido. Se houver, descreva-os com o ponto de parada.
8. Pendências e riscos observados.

Não declare a fase aprovada.

## 15. Parada e encaminhamento para auditoria

- Após o relatório, **pare**. O estado é `ENTREGUE_PARA_AUDITORIA`.
- Não inicie a F3 nem crie services, routers ou schemas.
- Não faça `git add`, commit, push ou merge (modo LOCAL).
- A auditoria independente é do Opus (`plano_validacao_auditoria.md` §9).
- No modo Cloud: commit e push apenas da branch da sessão, PR **draft**, e entrega de branch, SHA e evidências. A auditoria é local.
