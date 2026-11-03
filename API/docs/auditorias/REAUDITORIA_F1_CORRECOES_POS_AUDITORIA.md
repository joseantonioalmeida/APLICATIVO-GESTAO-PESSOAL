# Reauditoria independente das correções da F1

| Campo | Valor |
| --- | --- |
| Documento | `docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md` (primeira entrega neste caminho) |
| Fase | F1 — Fundação técnica: correções pós-auditoria |
| Data | 2026-10-11. Fechamento técnico às 21:58:32 -0300 |
| Auditor | Claude Opus 5.5, modo LOCAL (WSL) |
| Antecedentes | `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` (veredito histórico **`BLOQUEADO`**, preservado) e `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` |
| Objeto | Árvore de trabalho sobre `bd2b2e0f1e4f2674b528175e535b0931badec34a`, sem commit da F1 (manifesto em §2 e §5) |
| Veredito | **F1 `APROVADO_COM_P3`** |

---

## 1. Veredito e limites

**F1: `APROVADO_COM_P3`.**

- **Os três achados impeditivos (P2) foram corrigidos e verificados:**
  - ACH-MV-F1-001: gate de formatação;
  - ACH-MV-F1-002: valores de colunas no log de 500 de banco;
  - ACH-MV-F1-003: fixture de settings.
- **O ACH-MV-F1-004 (P3) foi encerrado** com prova de escrita em cópia.
- **Ficam em acompanhamento, sem bloquear a F1:**
  - ACH-MV-F1-005 (P3): `alembic/` fora do Ruff e do Pyright, a decidir antes do Prompt F2;
  - ACH-MV-F1-006 (P3): precisão dos relatos;
  - ACH-MV-F1-007 (P3, **novo**): o comando normativo de `docker compose config` sem `--env-file` faz o Docker Compose ler o `.env`.

A aprovação vale **somente** para o objeto do manifesto (§2 e §5). Ela não libera a F2 e não substitui o commit, que cabe ao usuário (G6). Qualquer mudança posterior nesses arquivos invalida a aplicação automática deste veredito.

**Limites:**

- O relatório final do Sonnet não existe como arquivo. Usei as alegações listadas na mensagem M6, §7 (`indice.md` §4).
- O log histórico do RED não está disponível. Ele foi **reproduzido** em cópia cujo conteúdo foi comprovado por hash (§6.4); isso é reprodução, não o registro histórico.
- O bloco de revalidação do baseline da F1 (Prompt F1 §1.2, a–e) continua indisponível (ACH-MV-ARQ-019, §4).
- O `.env` real não foi lido, copiado nem hasheado.

---

## 2. Identidade do objeto

| Item | Constatação |
| --- | --- |
| Raiz | `/home/jose/projects/app_gestão_pessoal/API` |
| Branch | `main...origin/main`, sem divergência |
| HEAD | `bd2b2e0f1e4f2674b528175e535b0931badec34a`. O reflog tem só o commit inicial |
| Índice do Git | Vazio (`git diff --cached --name-status` sem saída) |
| `git status --short` | 23 linhas, os mesmos caminhos da §1 do prompt de correções |
| Rastreados alterados ou removidos contra o baseline | Os mesmos 8 da auditoria. `pyproject.toml` passou de +5/−1 para +8/−1: são as 3 linhas da DEC-MV-26 |
| Não rastreados | Os 27 da F1, mais `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` e `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` (criados pelo auditor na auditoria anterior) |
| Ignorados presentes | Os mesmos 13 caminhos da auditoria (`.env`, `.venv/`, caches e `src/api.egg-info/`) |
| Manifesto do objeto (48 arquivos) | **Bloco B: 42/42** iguais à auditoria. **Bloco A: 6/6 alterados**, com os hashes declarados pelo Sonnet (§5) |
| Documentos da auditoria anterior | Relatório `5494d3d450047b95c8e458195cde205d909f680de31c060f65e68d206f7aa357` e prompt de correções `4d711cd17361427b9282a626fdfd4832a83bfa66119650631f45ad132139da5c`: iguais aos registrados na Etapa A das correções |

**Prova do delta das correções.** Copiei o estado atual dos 6 arquivos para uma pasta temporária e apliquei ao contrário:

1. a emenda `env_file=None` (10 linhas acrescentadas);
2. os 6 diffs extraídos do próprio prompt de correções (hash `4d711cd1…`).

O resultado tem **exatamente** os hashes do bloco A auditado (6/6 OK). Portanto o delta é só a correção prescrita mais a emenda. Os 6 arquivos também são idênticos byte a byte ao estado que o Opus validou em cópia antes da implementação.

**Arquivos criados ou alterados pelo auditor nesta reauditoria:**

- este relatório;
- os 5 documentos da reconciliação (§9), editados **depois** do fechamento técnico.

Nenhum arquivo técnico foi tocado.

---

## 3. Fontes, aprovações e precedência da emenda

**Fontes lidas.** Hashes no início da reauditoria, antes da reconciliação:

| Fonte | SHA-256 |
| --- | --- |
| `CLAUDE.md` | `565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473` |
| `docs/arquitetura/indice.md` | `0d100e6d7c95aed221878152c221b8a8dcb4dc95bb7572d41c00d5824f01777e` |
| `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` | `5494d3d450047b95c8e458195cde205d909f680de31c060f65e68d206f7aa357` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` | `4d711cd17361427b9282a626fdfd4832a83bfa66119650631f45ad132139da5c` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md` | `38386a4fdfd3ce1c4f05214cc7a327e94fe8fff6db4dcf97f7d5a354a9472785` |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `2a2f155e92af0fcbb06400234545974b0dff334677cea3c1c734528fc4e6b70b` |
| `docs/arquitetura/plano_validacao_auditoria.md` | `92d210fbcb833b19f21f8dc51d25bb000c5be8c8e861038bd2dd6eeac6ef92e5` |
| `docs/arquitetura/analise_projeto_minhavida.md` | `44bb46f0c36437305c45c82d7c04a4fa0fe5320dd120c9f79d4d406f67b6364f` |
| `docs/arquitetura/plano_fases_api.md` | `5f9048f750f7bbc232a68048daad2f8622f150f398d06399fa5010a2a7a26afe` |
| `docs/arquitetura/matriz_requisitos_api.md` | `e0f9c1a485106204f5d64bf3250ef0a1239b36e672fc0f015a9339d2ef6ec09c` |

Além delas: o código instalado de `pydantic_settings` (`main.py`, linhas 405–450; `sources/providers/dotenv.py`, linhas 40–117).

**Aprovações aplicadas,** registradas em `indice.md` §4 com as referências M1 a M6:

- DEC-MV-01 a 05;
- DEC-MV-25, em escopo limitado;
- **DEC-MV-26, opção B** (M4);
- implementação da F1 e imports relativos em `tests/` (declarados em M3);
- correções ACH-MV-F1-001 a 003 (M6);
- emenda `env_file=None` (M5 e M6);
- P-DOC-01 a 05 (M6).

DEC-MV-06 a 24 seguem pendentes. Nenhuma foi ampliada.

**Precedência da emenda.** É instrução explícita do usuário ao Sonnet, com precedência sobre o prompt de correções §7.3 e §7.5 (`indice.md` §3, item 1). Não é desvio do implementador. O prompt de correções e o relatório anterior ficaram de propósito sem alteração, para não quebrar os hashes travados na Etapa A.

**Contrato efetivo da fixture:**

1. só valores explícitos e padrões;
2. sem valores de ambiente, dotenv ou segredos;
3. sem abertura do `.env`;
4. produção inalterada;
5. a cópia interna de `os.environ` é admitida.

---

## 4. Achados

| Achado | Sev. | Estado anterior | Evidência nova | Conclusão | Pendência |
| --- | --- | --- | --- | --- | --- |
| ACH-MV-F1-001 | P2 | ABERTO | O delta do `pyproject.toml` são só as 3 linhas da DEC-MV-26. `ruff format --check .`: rc 0 e `26 files already formatted` (só `.py`, a mesma cobertura de antes). Lint inalterado (`All checks passed!`). Sonda S2 | **VERIFICADO (encerrado)** | — |
| ACH-MV-F1-002 | P2 | ABERTO | `erros.py:196-212` e `:292-298` conferidos. REG-F1-01 passou (2 casos). Na saída formatada real: 0 sentinelas, 0 `DETAIL`, 0 `Failing row`, 0 `Key (`, 0 `Traceback`, 0 `[SQL`; identificadores e `[id_requisicao]` presentes. RED reproduzido (§6.4) | **VERIFICADO (encerrado)** | — |
| ACH-MV-F1-003 | P2 | ABERTO | Código da biblioteca lido (o dotenv é construído antes do hook; `env_file=None` faz `_read_env_files` retornar `{}`). REG-F1-02 passou. Sonda S1: **0 aberturas** com a `SettingsTeste` entregue, 1 abertura no controle. Sonda S1′: a versão sem a emenda abre 1 vez e reprova a asserção estrutural | **VERIFICADO (encerrado)** | — |
| ACH-MV-F1-004 | P3 | ABERTO (acompanhamento) | Sonda S2: `ruff format .` com escrita em cópia reformatou o controle `.py` e manteve os 14 `.md` intactos. No contraste sem a DEC-MV-26, reescreveu o documento de arquitetura | **ENCERRADO.** O incidente histórico continua registrado na auditoria anterior (§7.1) | — |
| ACH-MV-F1-005 | P3 | ABERTO | Sem mudança: `exclude` com `"alembic"` e Pyright `include = ["src", "tests"]`. A DEC-MV-26 não alterou isso, e `alembic/` **continua sem cobertura automática** | ABERTO. Não bloqueia a F1 | Decidir antes do Prompt F2 |
| ACH-MV-F1-006 | P3 | ABERTO | O relatório das correções ainda usa `<2 nós>` e “o mesmo comando” no lugar dos comandos literais, e o log do RED histórico não foi preservado (§7). As demais alegações conferem | ABERTO (acompanhamento). Não bloqueia | Exigir comandos literais e logs preservados no próximo prompt |
| **ACH-MV-F1-007** | P3 | **novo** | `docker compose config --quiet` sem `--env-file` lê o `.env` do diretório. Provado com `.env` sintético (§6.5): sem o flag, a interpolação passa só por causa do arquivo; com `--env-file /dev/null`, falha. O comando estava prescrito no Prompt F1 §14, passo 10, e no prompt de correções §10, passo 13, e foi usado na auditoria anterior (comando 7). Saída suprimida por `--quiet`: nenhum valor foi exposto | ABERTO. Origem: comandos normativos do Opus, **não** a implementação | P-DOC-06 (§9) |
| ACH-MV-ARQ-019 | P2 | Conteúdo verificado; encerramento formal pendente | Sem nova evidência histórica. HEAD = `bd2b2e0`, com exatamente os 22 caminhos de `analise` §3.5 (verificado de novo). Os arquivos da F1 têm `mtime` ≥ 19:33:43, posterior ao commit (19:13:38). O usuário declarou a revalidação (M3). Uma execução atual **não** comprova retroativamente o passo §1.2 da F1 | Critério substantivo atendido. **Encerramento formal pendente** do bloco de revalidação. Lacuna documental, não falha técnica. Não afeta o veredito da F1, porque o objeto está identificado por manifesto e o baseline foi verificado de forma independente | Anexar o bloco, ou decisão do usuário |
| ACH-MV-ARQ-006 | P3 | Critério atendido no objeto | `compose.yaml` inalterado (`bb1d211f…`) e igual ao Prompt F1 §9.3. `config` válido com dotenv neutro | Encerrar no G6, quando o arquivo entrar no histórico pelo commit da F1 | Commit do usuário |

**ACH-MV-F1-007 em detalhe:**

- **Fonte:** regra “não leia o `.env`” (Prompt F1 §0, item 6; prompts de auditoria).
- **Impacto:** leitura indireta por ferramenta, sem saída. Não houve exposição de valores. Também não é possível afirmar, sem lê-lo, o que o `.env` real continha.
- **Correção:** P-DOC-06.
- **Encerramento:** comandos normativos com `--env-file /dev/null` aplicados após aprovação, e uso desse flag nos prompts seguintes.
- **Responsáveis:** Opus (texto) e usuário (aprovação).

---

## 5. Comparação dos arquivos

**Seis arquivos corrigidos (bloco A):**

| Arquivo | SHA-256 auditado (bloco A) | SHA-256 atual (= declarado pelo Sonnet) | Delta |
| --- | --- | --- | --- |
| `pyproject.toml` | `54bd1c986794bb98136cfc9997420759f943711ab9b1645b3b10c903883864d5` | `c267322b201acc6229b133020062c4ba02f473ad918c459377ad4432aa1df5a4` | DEC-MV-26 (3 linhas) |
| `src/api_gestao_pessoal/erros.py` | `013d35ffb305d079ae865f1efba3288390eb6aecbca7b03c911e03e66daf3525` | `4e8adcce3eb13b78462c6cbdb96fb3cae39c1758b645c1b24d7c9f9f7bb63836` | §7.2 |
| `tests/apoio/rotas_teste.py` | `8745ba8f239d81236d81ed08aef96221032c61466dbd004826ce81f5eabc9481` | `6982ec6299e05ae5af5ce5cb73c746b6b07ae11ff531ccf060ebebdb2567e59a` | §7.4 |
| `tests/conftest.py` | `44d00c2f24c9c2d143cc3e2de901a342f3bfd93b2a4833e2238b9eb0ad2b7707` | `d94beb8afec10ae275915aafda972c51a5486fccc4ea3b2d79dfb990bdba4408` | §7.3 e emenda |
| `tests/infra/test_configuracao.py` | `aaaa587237ec8461085bf23cf6b1dcaebdc929468bcb13601fb020421c6314de` | `4c2106538fe287e5e415ae02117dc2047523d31723d038354c57fe958c2f4830` | §7.5 (REG-F1-02) e emenda |
| `tests/infra/test_sessao_transacao.py` | `e42dabbda535ae26a5161f3ef3325f1b1c3fd8acc71be2c1d18e778348aa3e48` | `502570597f404f88bf894aea3aa0779466969f6cb5ac3ff871977bde152aea19` | §7.5 (REG-F1-01) |

**Protegidos (bloco B):** 42/42 iguais, entre eles:

- `uv.lock`;
- todos os módulos de produção, exceto `erros.py`;
- `alembic/**`, `compose.yaml`, `.gitignore` e `.env.exemplo`;
- os documentos normativos, até o início da reconciliação.

Não houve mudança de dependências, modelos, routers de produção ou escopo.

**Documentos históricos:** os dois da auditoria anterior estão inalterados (§2) e foram preservados. Este relatório não os sobrescreve.

---

## 6. Resultados

Diretório de todas as execuções no repositório: `/home/jose/projects/app_gestão_pessoal/API`. Execução sequencial.

**Ambiente** (somente leitura):

- uv 0.11.29, Python 3.14.6, Docker Server 29.7.2 e Docker Compose v5.3.1;
- `uv run --help` lista `--no-sync` e `--frozen`;
- `.venv` com 82 distribuições, todas iguais ao `uv.lock`, sem versões divergentes nem extras. Faltam só `mslex`, `pywin32` e `tzdata`, todos marcados com `sys_platform == 'win32'`;
- pacote editável `api` 0.1.0 reinstalado às 21:33:02–21:33:03 (`src/api.egg-info` e `__editable__.api-0.1.0.pth`).

**Isolamento do `.env` real nos testes, confirmado por leitura:**

- os `obter_settings()` dos testes rodam sob `ambiente_limpo` (`chdir(tmp_path)`);
- o app sempre recebe settings injetadas;
- a `SettingsTeste` tem `env_file=None`;
- o REG-F1-02 usa `.env` sintético em `tmp_path`;
- os testes de Alembic ficaram fora da seleção;
- nenhuma variável `UV_*`, `PYTHONPATH`, `DATABASE_URL`, `POSTGRES_*` ou `COMPOSE_*` estava definida (só os nomes foram conferidos);
- a conexão vem do Testcontainers, com a guarda.

### 6.1. Comandos

| # | Comando literal | rc | Resultado | Duração |
| --- | --- | --- | --- | --- |
| 1 | Os 8 comandos Git do §3 da solicitação | 0 | §2 | — |
| 2 | `uv run --no-sync --frozen pytest tests/infra/test_sessao_transacao.py::test_erro_banco_500_sem_valores_no_log tests/infra/test_configuracao.py::test_settings_teste_ignora_ambiente_e_env -q -p no:cacheprovider` | 0 | `3 passed in 6.37s`; 0 skip, 0 xfail | 8,64 s |
| 3 | `uv run --no-sync --frozen pytest tests/infra/test_configuracao.py tests/infra/test_saude.py tests/infra/test_erros.py tests/infra/test_sessao_transacao.py -q -p no:cacheprovider -rA` | 0 | `26 passed in 8.51s`: 26 `PASSED`, 0 falhas, 0 skip, 0 xfail. As 4 linhas `ERROR` da saída são registros de log capturados pelo `-rA` | 10,72 s |
| 4 | `uv run --no-sync --frozen pytest tests/infra --collect-only -q -p no:cacheprovider` (coleta, sem execução) | 0 | 29 nós: `test_configuracao` 8, `test_saude` 3, `test_erros` 7, `test_sessao_transacao` 8 e `test_alembic_ambiente` 3 | 0,25 s |
| 5 | `uv run --no-sync --frozen ruff check --no-fix .` | 0 | `All checks passed!` | 0,13 s |
| 6 | `uv run --no-sync --frozen ruff format --check .` | 0 | `26 files already formatted` | 0,10 s |
| 7 | `uv run --no-sync --frozen pyright` | 0 | `0 errors, 0 warnings, 0 informations` | 8,54 s |
| 8 | `uv run --no-sync --frozen alembic heads` | 0 | Saída vazia (0 bytes) | 0,55 s |
| 9 | `POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet` | 0 | Válido. `--env-file` é opção global do `docker compose` na v5.3.1 | 0,13 s |
| 10 | Controle negativo: o mesmo comando, sem as 3 variáveis | 1 | `required variable POSTGRES_USER is missing a value`: o `.env` real **não** foi usado | — |
| 11 | `docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine` | 0 | `postgres@sha256:fe0737ba566a2c5b2a28f34433c0a423261900ec17b9bf7ad115e1aae7e57f1b` (inalterado) | — |
| 12 | `uv run --no-sync --frozen ruff format --check -v .`, duas vezes, só leitura (diagnóstico) | 0 | Os `.md` aparecem como `Included path via include` na descoberta do workspace, que é comum a lint e formatação. O `exclude` do formatador os filtra depois, e o resumo conta só 26 `.py` | — |

**Adaptações:**

- `-p no:cacheprovider` nos comandos 2–4 evita gravar `.pytest_cache`;
- `-rA` no comando 3 só lista os nós e não altera a seleção;
- os comandos 12 são verificações extras de leitura, declaradas aqui.

**Não executados, com motivo:**

- `pytest tests/infra/test_alembic_ambiente.py`: o arquivo, `alembic/**` e `alembic.ini` estão inalterados (bloco B), e o único arquivo da coleção que mudou, `tests/conftest.py`, só alterou `SettingsTeste` e `settings_teste`, que os testes de Alembic não usam. Reaproveitei a evidência da auditoria anterior (3 passed, mesmo conteúdo e mesmo ambiente);
- suíte completa: não exigida e sem justificativa;
- `ruff format .` e `ruff check --fix` no repositório;
- `uv sync`.

### 6.2. Saída real do log no caminho 500 de banco

Execução do comando 2, stream do handler real (`StreamHandler` com `FORMATO_LOG`):

```text
ERROR api_gestao_pessoal.erros [regressao-log-0001] erro de banco de dados: sqlstate=23505 classe=UniqueViolation esquema=teste_infra tabela=registro coluna=- restricao=uq_registro_unico
ERROR api_gestao_pessoal.erros [regressao-log-0001] erro de banco de dados: sqlstate=23502 classe=NotNullViolation esquema=teste_infra tabela=registro coluna=valor restricao=-
```

Contagens em toda a saída do comando 2, incluindo o stream do handler:

| Termo | Ocorrências |
| --- | --- |
| `sentinela-` | 0 |
| `DETAIL` | 0 |
| `Failing row` | 0 |
| `Key (` | 0 |
| `already exists` | 0 |
| `violates` | 0 |
| `Traceback` | 0 |
| `The above exception` | 0 |
| `[SQL` | 0 |

A pilha emitida traz só `File "…", line N, in …` e a linha de fonte correspondente, que é código estático, por exemplo `raise error.with_traceback(exc_info[2])`. Não há mensagens de exceção nem valores dinâmicos.

No comando 3, o CT-F1-13 também registra só `sqlstate=23505 … restricao=uq_registro_unico`. O CT-F1-09 continua com traceback no caminho genérico, conforme o contrato.

O REG-F1-01 tem controle positivo: o registro existe e contém `sqlstate`, o identificador e `[id_requisicao]`. Um teste que passasse sem log falharia nas linhas `assert registros` e `assert trecho in saida`.

### 6.3. Sonda S1: abertura do dotenv pela `SettingsTeste` entregue

- **Metodologia:**
  - diretório temporário novo, contendo só um `.env` sintético com `DATABASE_URL` sintético, `AMBIENTE=producao`, `DB_STATEMENT_TIMEOUT_MS=123`, `DB_POOL_SIZE=9` e `DB_LOCK_TIMEOUT_MS=777`;
  - variáveis de ambiente sintéticas `LOG_NIVEL=DEBUG` e `DB_POOL_SIZE=7`;
  - `sys.addaudithook` registrando eventos `open` de arquivos chamados `.env`, instalado **antes** de qualquer import do projeto;
  - os módulos foram importados do repositório (`PYTHONPATH=<repo>/src:<repo>`, `PYTHONDONTWRITEBYTECODE=1`), com origem conferida por hash: `tests/conftest.py` = `d94beb8a…` (entregue) e `settings.py` = `039937f6…`.
  - Script no anexo A.
- **Resultados** (rc 0, 1,11 s):

| Construção | Aberturas de `.env` | Do `.env` sintético | Do `.env` real | `LOG_NIVEL` | `DB_POOL_SIZE` | `DB_STATEMENT_TIMEOUT_MS` | `DB_LOCK_TIMEOUT_MS` | Host do banco |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Controle: `Settings(DATABASE_URL=…, AMBIENTE="teste")` | **1** | 1 | 0 | DEBUG (ambiente) | 7 (ambiente vence o dotenv, 9) | 123 (dotenv) | 777 (dotenv) | explícito |
| `SettingsTeste(DATABASE_URL=…, AMBIENTE="teste")` entregue | **0** | 0 | 0 | INFO | 5 | 15000 | 5000 | explícito |

- **Validador:** a `SettingsTeste` rejeita `postgresql://…` sem ecoar o segredo, e sem abrir `.env`.
- **Configuração herdada:** `env_file=None`, `extra="ignore"`, `hide_input_in_errors=True` e `env_file_encoding="utf-8"`. A produção mantém `env_file=".env"`.
- **Contagem do controle:** exatamente 1 abertura neste ambiente. A sonda é conclusiva, porque o controle detectou abertura.
- **S1′ (discriminação da emenda):** mesma sonda contra uma cópia com a `SettingsTeste` **sem** a emenda (conftest `6d0a434bf51a08f20e38b21ca7d668e5906e94c3edc272a91394fa6505e74f93`, versão do prompt de correções §7.3).
  - Os valores ficaram isolados (`DB_POOL_SIZE` 5), mas houve **1 abertura** do `.env` sintético.
  - O REG-F1-02 entregue, executado contra essa versão, reprova em `assert '.env' is None` (`1 failed in 7.23s`).
  - Conclusão: o teste estrutural e a sonda comportamental distinguem as duas versões. A asserção estrutural sozinha não substitui a observação de I/O.

### 6.4. RED reproduzido

- **Objeto:** cópia temporária (`copiaA`) com `pyproject.toml`, `erros.py` e `tests/conftest.py` iguais ao bloco A auditado e com as rotas e os dois arquivos de teste iguais aos entregues, mais o restante do objeto igual ao bloco B. Tudo conferido por hash. É o estado “passo 1 concluído, correção não aplicada”.
- **Comando** (diretório da cópia): `python -m pytest tests/infra/test_sessao_transacao.py::test_erro_banco_500_sem_valores_no_log tests/infra/test_configuracao.py::test_settings_teste_ignora_ambiente_e_env -q -p no:cacheprovider -rf`, com o Python do `.venv`.
- **Resultado:** rc 1, `3 failed in 5.41s`:
  - os dois casos do REG-F1-01 em `assert '<sentinela>' not in '…'`;
  - o REG-F1-02 em `assert 7 == 5`.
- É **reprodução**, não o log histórico. O `assert 7 == 5` prova contaminação de valores. A prova sobre a leitura do arquivo é a S1′.

### 6.5. Sondas S2 (formatador) e S3 (Compose)

- **S2.** A cópia `copiaF` foi feita com `git ls-files -co --exclude-standard`, sem `.env` e sem `.venv`, e com o `pyproject.toml` igual ao entregue. Registrei os hashes dos 14 `.md` antes (12 normativos e 2 da auditoria anterior) e criei um `.py` desformatado de controle.
  - `ruff format --no-cache .` com cwd na cópia: rc 0, `1 file reformatted, 26 files left unchanged`, stderr vazio. O controle ficou formatado e os 14 `.md` intactos.
  - Contraste (`copiaG`, mesma cópia sem as 3 linhas da DEC-MV-26): rc 0, `1 file reformatted, 39 files left unchanged`. O arquivo reformatado foi `docs/arquitetura/arquitetura_api_minhavida.md`.
  - Depois das sondas, o repositório real seguia 48/48 inalterado.
- **S3.** Cópia de `compose.yaml` com `.env` sintético (`POSTGRES_*=sintetico`) e sem variáveis no ambiente:
  - `docker compose config --quiet`: rc 0, porque leu o `.env` do diretório;
  - `docker compose --env-file /dev/null config --quiet`: rc 1, variável ausente.

Todos os containers das sondas e testes foram removidos (`docker ps -a` vazio). Nenhum recurso de terceiros foi tocado.

---

## 7. Confronto das alegações do Sonnet

As alegações são as da mensagem M6, §7.

| Alegação | Classificação | Evidência |
| --- | --- | --- |
| RED: três falhas pelos motivos esperados; linha-resumo omitida pelo filtro | **NÃO VERIFICÁVEL** como registro histórico (log não preservado). **CONFIRMADA por reprodução** em cópia comprovada por hash (§6.4), com a linha-resumo capturada agora | §6.4 |
| GREEN: três testes passaram | **CONFIRMADA** (comando 2) | §6.1 |
| Seleção dos quatro arquivos: 26 passaram | **CONFIRMADA** (comando 3). A diferença para os 29 de `tests/infra` são os 3 nós de Alembic, conferidos na coleta (comando 4) | §6.1 |
| Ruff, Pyright, Alembic e Compose passaram | **CONFIRMADA**. O Compose foi agora validado com dotenv neutro. O comando prescrito ao Sonnet, sem `--env-file`, lia o `.env` (ACH-MV-F1-007) | §6.1 e §6.5 |
| Seis arquivos corrigidos; 42 protegidos e os dois documentos anteriores intactos | **CONFIRMADA** (hashes e prova de delta) | §2 e §5 |
| Nenhuma alteração de dependências nem ações de Git | **CONFIRMADA**: `uv.lock` inalterado, `.venv` igual ao lock, HEAD e reflog inalterados, índice vazio | §2 e §6 |
| `uv run --frozen` reinstalou implicitamente o próprio pacote após mudar o `pyproject.toml` | **CONFIRMADA**. É “implícito”, não “executado”. Só o pacote editável `api` 0.1.0 foi reinstalado (21:33). Nenhuma dependência mudou | §6 |
| A asserção nova verifica configuração; a prova de zero abertura ficou para o Opus | **CONFIRMADA** e prova feita (S1 e S1′) | §6.3 |
| P-DOC-01 a 05 não aplicados pelo implementador | **CONFIRMADA**: os 5 documentos tinham, no início, os hashes da auditoria anterior | §3 |
| Uso de `<2 nós>` e “o mesmo comando” | Lacuna documental: o comando literal não foi registrado, e não o reconstruí como histórico | ACH-MV-F1-006 |
| `-p no:cacheprovider` nos passos 2 e 4 | Sem efeito na seleção. Evita artefato. Aceitável | — |
| Emenda aplicada à mão | Resultado byte a byte igual à emenda validada (§2). Autorizada pelo usuário | §2 |
| `git apply` sem `--index` | Só altera a árvore de trabalho. Índice vazio confirmado. Compatível com a regra que proíbe `git add` | §2 |
| `git status` igual | Não provava conteúdo igual; os hashes foram conferidos | §2 e §5 |
| Integridade histórica do `.env` real | **NÃO VERIFICÁVEL** sem lê-lo. Não afirmo nada sobre ela | — |

---

## 8. Integridade antes e depois da verificação técnica

| Momento | Verificação | Resultado |
| --- | --- | --- |
| Início (congelamento) | Manifesto de 48 arquivos, os 2 documentos anteriores, HEAD, índice e status | §2 |
| Após as sondas S2 | `sha256sum -c` do manifesto | 48/48 iguais |
| Fechamento técnico (21:58:32) | Manifesto, documentos anteriores, HEAD, índice e ignorados | 48/48 iguais; 2/2 iguais; HEAD `bd2b2e0`; índice vazio; 13 ignorados (sem novos) |
| Após a reconciliação documental | Arquivos não documentais do manifesto | **Inalterados.** Só os 5 documentos autorizados mudaram (§9) |

Separação:

- **inalterados durante a reauditoria:** código, testes, configuração, dependências, `compose.yaml`, `alembic/**` e os documentos da auditoria anterior;
- **atualizados depois, com autorização:** os 5 documentos da §9.

Caches ignorados (`__pycache__/`, `.ruff_cache/`) podem ter sido atualizados pelos comandos de verificação. São artefatos, fora do objeto, e não devem ser versionados.

---

## 9. Reconciliação documental

Feita **depois** do fechamento técnico, nos limites autorizados por M6 (§0, item 5, e §9). Não houve formatação automática. As atualizações registram decisões já tomadas.

| Item | Arquivo e trecho | Atualização | SHA-256 antes → depois |
| --- | --- | --- | --- |
| P-DOC-01 | Prompt F1 §8.5, handler 4 | Log do 500 de banco: `logger.error` sem `exc_info`, identificadores, pilha sem mensagens e `id_requisicao`. 503 e demais contratos preservados. O texto anterior foi citado | `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md`: `38386a4f…2785` → `305fed4f471b720e97ab5ea73180b2b0d10403360b82fb4d9bbb3cce82b8840b` (P-DOC-01 e 02 no mesmo arquivo) |
| P-DOC-02 | Prompt F1 §11.1, `settings_teste` | `SettingsTeste(DATABASE_URL=SecretStr(...), AMBIENTE="teste")`, `model_config = SettingsConfigDict(env_file=None)`, hook só com `init_settings`, efeito de não abrir o `.env` e referência à emenda do usuário | Idem |
| P-DOC-03 | Arquitetura §3.4, item `hide_parameters` | Limite de `hide_parameters` diante de `DETAIL` e `Failing row contains` e o contrato de log corrigido | `docs/arquitetura/arquitetura_api_minhavida.md`: `2a2f155e…6b70b` → `d7bb454a76dd08aff7c6f88cc0b3f83770d74ef0021553f669e9642ffaa150f4` |
| P-DOC-04 | Plano de validação §4, catálogo F1 | CT-F1-21 (REG-F1-01) e CT-F1-22 (REG-F1-02), distinguindo a asserção estrutural da sonda comportamental de zero leitura. Nota de origem | `docs/arquitetura/plano_validacao_auditoria.md`: `92d210fb…92e5` → `be6e4e85f59e0dc1acbc4e4289cb2a24c4e41620a5041c8da91d9b7954c5f3d0` |
| P-DOC-05 | `indice.md` §4 e §5 | Referências M3 a M6. Aprovações: implementação da F1, imports relativos, DEC-MV-26, correções, emenda, P-DOC e o que ficou fora. Gates com o histórico (G5 `BLOQUEADO`) e o atual (G5 `APROVADO_COM_P3`). Pendências da F1 e da F2. Nota de que §1, §2, §6 e §7 estão fora do escopo | `docs/arquitetura/indice.md`: `0d100e6d…77e` → `961278af16120c210530a9a6ac3bd4fa7c5e57bf82ec00151287b33e574edea5` |
| P-DOC-05 | `analise` §9 | Linha de estado e linha da DEC-MV-26 (opção B aprovada; A e C não escolhidas) | `docs/arquitetura/analise_projeto_minhavida.md`: `44bb46f0…364f` → `1bdcf137e276fb036f3685d4a84dfac560f1c206e23d6b1baa3e03b39fc863b7` |

**Conferência:**

- diff documental de 5 arquivos (+44 −13 antes do último ajuste do G3);
- cercas de código balanceadas;
- IDs novos definidos: CT-F1-21 e 22 no plano e DEC-MV-26 na análise;
- ACH-MV-F1-001 a 007 e P-DOC-01 a 07 definidos nos relatórios de auditoria;
- nenhum hash antigo foi reaproveitado para representar conteúdo novo.

As datas registradas são as das mensagens (todas de 2026-10-11). Onde a mensagem original ao Sonnet não está disponível, o registro indica “declarado em M3/M6”.

**Não alterados:** `CLAUDE.md`, ADRs, código, testes, configuração, dependências, os dois documentos da auditoria anterior e o prompt antigo do banco.

### 9.1. Propostas que precisam de aprovação (não aplicadas)

| ID | Documento | Alteração proposta | Motivo |
| --- | --- | --- | --- |
| P-DOC-06 | Prompt F1 §14, passo 10, e modelos de comando dos próximos prompts | Trocar por `POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet` | ACH-MV-F1-007. Fora do escopo autorizado em M6, que limitou o Prompt F1 a §8.5 e §11.1 |
| P-DOC-07 | `indice.md` §1, §2, §6 e §7; cabeçalho do Prompt F1; `plano_fases_api.md` (cabeçalho e §3, linha da F1) | Atualizar os estados descritivos: Prompt F1 executado e F1 `APROVADO_COM_P3`, aguardando integração. Atualizar a contagem de CTs na autoverificação (173 + 2) e a próxima ação | Coerência dos estados. Fora do escopo autorizado. Até lá, `indice.md` §5 é a fonte dos estados vigentes, conforme a nota ali registrada |

---

## 10. Estado da F1, estado da F2 e próxima ação

| Item | Estado |
| --- | --- |
| **F1** | **`APROVADO_COM_P3`** (reauditoria de 2026-10-11) sobre o manifesto da §2 e §5. Histórico: `BLOQUEADO` (auditoria de 2026-10-11) |
| P3 em acompanhamento | ACH-MV-F1-005 (decidir antes do Prompt F2), ACH-MV-F1-006 (precisão dos relatos) e ACH-MV-F1-007 (P-DOC-06) |
| Pendência documental de arquitetura | ACH-MV-ARQ-019: encerramento formal |
| G6 — integração da F1 | **Cabe ao usuário.** Commit local do objeto reauditado: os 8 caminhos rastreados alterados ou removidos e os 27 novos da F1, com a lista explícita de arquivos, sem `.env`, `.venv/` ou caches. Também os documentos de auditoria e os 5 documentos reconciliados, se o usuário quiser versioná-los no mesmo commit. Nenhum comando Git foi executado pelo auditor |
| **F2** | **Não liberada. Prompt F2 não criado.** Faltam: F1 integrada por commit; DEC-MV-06 (ADR-0002); restante da DEC-MV-07 (D-09); DEC-MV-08 (aprovar ou rejeitar, com a reconciliação dos CHECKs); `CLAUDE.md` e modelo físico reconciliados com o que for aceito; decisão sobre ACH-MV-F1-005 (`alembic/` nos gates, porque a F2 cria a primeira revisão). DEC-MV-24 continua vinculada à F5 |

**Próxima ação do usuário:**

1. Fazer o commit da F1 com lista explícita de arquivos. Sugestão de verificação antes: `git status --short` e `git diff --cached --name-only`, conferindo que não aparecem `.env`, `.venv/` nem caches.
2. Decidir P-DOC-06 e P-DOC-07, se quiser os estados e comandos normativos coerentes antes da F2.
3. Para preparar a F2: decidir DEC-MV-06, DEC-MV-07, DEC-MV-08 e ACH-MV-F1-005, e aprovar a atualização do `CLAUDE.md` (diff de `analise` §10).

---

## Anexo A — Script da sonda S1

Execução: `cd <diretório temporário novo com .env sintético> && env -u DATABASE_URL LOG_NIVEL=DEBUG DB_POOL_SIZE=7 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo>/src:<repo> <repo>/.venv/bin/python sonda_dotenv.py <repo>`. Script integral, igual ao executado:

```python
"""Sonda da reauditoria: a SettingsTeste ENTREGUE abre o .env?

Uso: python sonda_dotenv.py <raiz_repo>
Executar com cwd = diretório temporário novo contendo só um .env SINTÉTICO.
O audit hook é instalado antes de qualquer import do projeto.
"""

import hashlib
import json
import os
import sys

RAIZ = os.path.realpath(sys.argv[1])
ENV_REAL = os.path.join(RAIZ, ".env")  # só comparação de caminho; nunca aberto
ENV_SINTETICO = os.path.realpath(os.path.join(os.getcwd(), ".env"))

eventos: list[str] = []


def gancho(evento: str, args: tuple) -> None:
    if evento == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        caminho = os.fsdecode(args[0])
        if os.path.basename(caminho) == ".env":
            eventos.append(os.path.realpath(caminho))


sys.addaudithook(gancho)

from pydantic import SecretStr, ValidationError  # noqa: E402

import api_gestao_pessoal.settings as mod_settings  # noqa: E402
import tests.conftest as mod_conftest  # noqa: E402
from api_gestao_pessoal.settings import Settings  # noqa: E402
from tests.conftest import SettingsTeste  # noqa: E402

eventos.clear()  # descarta eventos de import (não deve haver)


def sha(p: str) -> str:
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


origem = {
    m.__name__: {
        "arquivo": os.path.relpath(m.__file__, RAIZ),
        "sha256": sha(m.__file__),
    }
    for m in (mod_settings, mod_conftest)
}
# a leitura acima é do próprio .py, não de .env
eventos.clear()

URL = SecretStr("postgresql+psycopg://u:p@h:1/minhavida_teste")


def medir(construtor):
    eventos.clear()
    s = construtor()
    abertos = list(eventos)
    return s, abertos


controle, ab_controle = medir(
    lambda: Settings(DATABASE_URL=URL, AMBIENTE="teste")
)
teste, ab_teste = medir(
    lambda: SettingsTeste(DATABASE_URL=URL, AMBIENTE="teste")
)


def resumo(s: Settings) -> dict:
    return {
        "host_db": s.DATABASE_URL.get_secret_value().split("@")[1],
        "AMBIENTE": s.AMBIENTE,
        "LOG_NIVEL": s.LOG_NIVEL,
        "DB_POOL_SIZE": s.DB_POOL_SIZE,
        "DB_STATEMENT_TIMEOUT_MS": s.DB_STATEMENT_TIMEOUT_MS,
        "DB_LOCK_TIMEOUT_MS": s.DB_LOCK_TIMEOUT_MS,
    }


eventos.clear()
try:
    SettingsTeste(DATABASE_URL=SecretStr("postgresql://u:segredo@h/db"))
    validador = "NÃO rejeitou"
except ValidationError as e:
    validador = {"rejeitou": True, "eco_do_segredo": "segredo" in str(e)}
ab_validador = list(eventos)

cfg = SettingsTeste.model_config
print(
    json.dumps(
        {
            "origem_modulos": origem,
            "env_sintetico": ENV_SINTETICO,
            "controle_Settings": {
                "aberturas_env": len(ab_controle),
                "aberturas_do_sintetico": ab_controle.count(ENV_SINTETICO),
                "aberturas_do_real": ab_controle.count(ENV_REAL),
                "valores": resumo(controle),
            },
            "SettingsTeste": {
                "aberturas_env": len(ab_teste),
                "aberturas_do_real": ab_teste.count(ENV_REAL),
                "valores": resumo(teste),
            },
            "validador_SettingsTeste": validador,
            "aberturas_no_validador": len(ab_validador),
            "config_herdada": {
                "env_file": cfg.get("env_file"),
                "extra": cfg.get("extra"),
                "hide_input_in_errors": cfg.get("hide_input_in_errors"),
                "env_file_encoding": cfg.get("env_file_encoding"),
            },
            "config_producao_env_file": Settings.model_config.get("env_file"),
        },
        ensure_ascii=False,
        indent=1,
    )
)
```

## Anexo B — Comandos das sondas S2 e S3

```text
# S2 (cópia descartável, sem .env/.venv)
git ls-files -co --exclude-standard -z | tar --null -T - -cf - | tar -x -C <copiaF>
cd <copiaF>; find . -name '*.md' | sort | xargs sha256sum > md_antes.txt
printf 'x = {  "a":1 }\n' > src/api_gestao_pessoal/_controle_fmt.py
<repo>/.venv/bin/ruff format --no-cache .      # rc 0; 1 reformatted, 26 unchanged
sha256sum -c md_antes.txt                        # 14/14 OK
# contraste: <copiaG> sem as 3 linhas da DEC-MV-26 -> reescreve arquitetura_api_minhavida.md

# S3 (cópia de compose.yaml + .env sintético)
env -u POSTGRES_USER -u POSTGRES_PASSWORD -u POSTGRES_DB docker compose config --quiet                     # rc 0 (leu .env)
env -u POSTGRES_USER -u POSTGRES_PASSWORD -u POSTGRES_DB docker compose --env-file /dev/null config --quiet  # rc 1
```
