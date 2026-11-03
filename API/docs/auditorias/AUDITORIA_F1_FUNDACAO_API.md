# Auditoria independente da F1 — Fundação técnica da API MinhaVida

| Campo | Valor |
| --- | --- |
| Documento | `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` (primeira execução; não havia relatório anterior neste caminho) |
| Fase auditada | F1 — Fundação técnica (`PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md`) |
| Data | 2026-10-11 |
| Auditor | Claude Opus 5.5, modo LOCAL (WSL) |
| Objeto | Árvore de trabalho sobre o baseline `bd2b2e0f1e4f2674b528175e535b0931badec34a`, **sem commit da F1** (manifesto no anexo A) |
| Veredito | **`BLOQUEADO`** |

---

## 1. Veredito e justificativa principal

**F1: `BLOQUEADO`.**

A implementação segue o Prompt F1 em quase todos os pontos. Os 20 CTs passam com provas reais, há conexões independentes e contenção verdadeira no PostgreSQL, e Ruff (lint), Pyright, Alembic e Compose estão limpos. Ainda assim, três achados P2 impedem a aprovação, e nenhum deles tem correção ou decisão do usuário:

| Achado | Resumo | Origem demonstrada |
| --- | --- | --- |
| ACH-MV-F1-001 | O gate obrigatório `ruff format --check .` falha. A falha **já existia no baseline**: o Ruff 0.16 com `preview = true` formata blocos Python em `.md` e acusa `docs/arquitetura/arquitetura_api_minhavida.md`, que é protegido | Ferramenta/configuração e comandos normativos. **Não** é defeito da implementação |
| ACH-MV-F1-002 | O log dos erros 500 de banco (`logger.exception`) grava valores de colunas. O `DETAIL` do PostgreSQL inclui `Key (col)=(valor)` e `Failing row contains (…)` com a linha inteira. Isso foi confirmado com dados sintéticos e contraria a arquitetura §3.4 (aceita) e §11 (F1+) | Contrato: o Prompt F1 §8.5, item 4, prescreveu `exception`. A implementação seguiu o prompt |
| ACH-MV-F1-003 | A fixture `settings_teste` usa `Settings.model_validate(...)`. Na versão instalada, isso **lê o `.env` do diretório corrente e as variáveis de ambiente** em todos os campos não informados. O contrato pedia `_env_file=None`, e o relatório afirmou isolamento | Implementação (substituição sem verificação) somada a uma incompatibilidade latente do contrato (§11.1 × §9.5) |

O gate obrigatório falho não pode ser ignorado sob `APROVADO_COM_P3` (instrução do usuário e plano de validação §7). A F2 não é liberada.

---

## 2. Objeto auditado

### 2.1. Identificação

| Item | Constatação |
| --- | --- |
| Raiz | `/home/jose/projects/app_gestão_pessoal/API` (`git rev-parse --show-toplevel`) |
| Branch | `main`, sincronizada com `origin/main` (`## main...origin/main`) |
| HEAD | `bd2b2e0f1e4f2674b528175e535b0931badec34a`, igual ao baseline informado. Mensagem: “Baseline da F0: código inicial e documentação de arquitetura”, de 2026-10-11 19:13:38 -0300 |
| `origin/main` | `bd2b2e0f…` (mesmo commit). O histórico tem um único commit |
| Árvore do baseline | 22 caminhos, **idênticos por nome** à lista de `analise_projeto_minhavida.md` §3.5 (comparação por `diff`, não só pela contagem) |
| Índice do Git | Vazio (`git diff --cached` sem saída) |
| Rastreados alterados | 7 (`.gitignore`, `pyproject.toml`, `uv.lock`, `settings.py`, `database.py`, `main.py`, `models/base.py`) |
| Rastreados removidos | 1 (`schemas/message.py`) |
| Novos não rastreados | 27: os 26 de Prompt F1 §7.2, exatamente, e o `compose.yaml` (não rastreado por decisão) |
| Rastreados inalterados | 14, entre eles todos os documentos normativos, `CLAUDE.md`, `README.md` e `models/usuario.py` |
| Ignorados presentes | `.env`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `src/api.egg-info/` e diretórios `__pycache__/` (artefatos, fora do objeto) |

O SHA do baseline não identifica a implementação, porque a F1 não tem commit. O objeto auditado é o **manifesto SHA-256 do anexo A**: 48 arquivos presentes mais 1 removido.

### 2.2. Arquivos da entrega, do usuário e da auditoria

- **Entrega do Sonnet:** os 8 rastreados alterados ou removidos e os 27 novos, todos dentro de Prompt F1 §7. Nenhum arquivo extra deixou de ser explicado.
- **Arquivos posteriores do usuário:** nenhum identificado. O commit `bd2b2e0` é do usuário e antecede a implementação.
- **Artefatos desta auditoria:** somente este relatório e `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md`, criados **depois** de todas as verificações. Cópias, sondas e saídas ficaram no diretório temporário da sessão, fora do repositório.

### 2.3. Limites do material disponível

- O relatório do Sonnet não existe como arquivo no repositório. Usei as alegações resumidas na mensagem do usuário (§1.3 da solicitação).
- Do relatório da Etapa A tive apenas dois hashes completos: o do Prompt F1 e o do documento de arquitetura. Ambos conferem (§7.1). Os hashes das demais fontes da Etapa A e o bloco “Revalidação do baseline” (Prompt F1 §1.2 a–e) não estavam disponíveis.
- O conteúdo do `.env` real não foi lido, por restrição. Por isso não se sabe quais valores do `.env` real a fixture `settings_teste` absorveu, nem nesta auditoria nem na execução do Sonnet (ACH-MV-F1-003).

---

## 3. Fontes, autorizações e pendências normativas

### 3.1. Fontes lidas, com SHA-256

| Fonte | SHA-256 | Estado normativo usado |
| --- | --- | --- |
| `CLAUDE.md` | `565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473` | Vigente. Diretrizes §1–2 |
| `docs/arquitetura/indice.md` | `0d100e6d7c95aed221878152c221b8a8dcb4dc95bb7572d41c00d5824f01777e` | Precedência §3, aprovações §4, gates §5 |
| `docs/adr/0001_arquitetura_api_minhavida.md` | `756c944897a4ec8f990ec4bae6062cedb480c2488f4913168341c309e2b38fa2` | Parcialmente aceito: D-01–04, D-08, D-14 e D-09 só na convenção |
| `docs/adr/0002_identificadores_uuid.md` | `d710c7cc28685a138f615b1070976c12dd39607a2fe31af1b7b99d3035833ec8` | PROPOSTO (DEC-MV-06 pendente) |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `2a2f155e92af0fcbb06400234545974b0dff334677cea3c1c734528fc4e6b70b` | Aceita em §2, §3 (itens F1), §4.4, §5 e §10.1 (convenção) |
| `docs/arquitetura/plano_validacao_auditoria.md` | `92d210fbcb833b19f21f8dc51d25bb000c5be8c8e861038bd2dd6eeac6ef92e5` | Aceito em §2, §3, §5 e no catálogo F1 (§4). §6–9 usados como protocolo |
| `docs/arquitetura/analise_projeto_minhavida.md` | `44bb46f0c36437305c45c82d7c04a4fa0fe5320dd120c9f79d4d406f67b6364f` | Baseline §3.5, achados ARQ, decisões §9 |
| `docs/arquitetura/plano_fases_api.md` | `5f9048f750f7bbc232a68048daad2f8622f150f398d06399fa5010a2a7a26afe` | Fichas F1 e F2 |
| `docs/arquitetura/matriz_requisitos_api.md` | `e0f9c1a485106204f5d64bf3250ef0a1239b36e672fc0f015a9339d2ef6ec09c` | Consulta |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md` | `38386a4fdfd3ce1c4f05214cc7a327e94fe8fff6db4dcf97f7d5a354a9472785` | Prompt operacional da F1, lido integralmente |
| `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md` | `2535a838ff3e3f579de349114ff69433f3a7e00cb3e033e41624901dd7693f41` | SUSPENSO; não usado |

Todas as fontes têm bytes idênticos aos blobs do baseline.

### 3.2. Autorizações consideradas

1. DEC-MV-01 a 05 aprovadas e DEC-MV-25 em escopo limitado (`indice.md` §4).
2. Implementação da F1 autorizada após a Etapa A, com revalidação prévia do baseline, e imports relativos entre módulos de `tests/` autorizados expressamente. Fonte: mensagem do usuário que solicitou esta auditoria. Essas duas autorizações **ainda não estão registradas** no `indice.md` §4 (proposta P-DOC-05, anexo C).
3. Financeiro manual, sem integrações externas. Prompt antigo do banco SUSPENSO.

Não encontrei aprovação posterior de DEC-MV-06 a 24: o `indice.md` está com bytes idênticos ao baseline, e a mensagem do usuário não as aprova. A aprovação limitada da DEC-MV-25 não foi estendida.

### 3.3. Tensões normativas constatadas

| Tensão | Trechos | Efeito |
| --- | --- | --- |
| Comandos de formatação na raiz × documentos protegidos | `CLAUDE.md` §2 (`uv run ruff format .`); Prompt F1 §14, passos 4 e 7; plano §5.1; Prompt F1 §7.4 (`docs/**` protegido); `pyproject.toml` `[tool.ruff.format] preview = true` | O gate não passa sem alterar documento ou configuração protegidos (ACH-MV-F1-001) |
| Log de 500 com traceback × proibição de PII em logs | Prompt F1 §8.5, item 4 (“`exception` para 500, sem a URL e sem parâmetros”) × arquitetura §3.4 (aceita: “Proibido logar: … senhas, hashes … e-mails e nomes”) e §11 (“Logs sem corpo, e-mail ou nome. `hide_parameters` — F1+”) | A premissa de §3.4, de que `hide_parameters` basta, é incompleta: o `DETAIL` carrega valores (ACH-MV-F1-002). Pela precedência (`indice.md` §3), a arquitetura aceita prevalece sobre o Prompt |
| Fixture literal × regra de supressão única | Prompt F1 §11.1 (`Settings(…, _env_file=None)`) × §9.5 (uma única supressão de Pyright, em `settings.py`) | A forma literal gera `reportCallIssue: No parameter named "_env_file"` (verificado). Além disso, `_env_file=None` não bloqueia variáveis de ambiente (ACH-MV-F1-003) |

---

## 4. Alegações do Sonnet × constatações independentes

| Alegação | Constatação | Situação |
| --- | --- | --- |
| Estado `ENTREGUE_PARA_AUDITORIA` | Coerente: nenhum commit da F1 e HEAD inalterado | Confirmada |
| 26 testes passando, CT-F1-01 a 20, sem skip ou xfail | `26 passed`, 0 skip e 0 xfail. Os 26 nós mapeiam os 20 CTs com os nomes obrigatórios (§5) | Confirmada |
| Ruff de lint passando | `ruff check --no-fix .` → `All checks passed!` (27 arquivos) | Confirmada |
| Pyright com zero erros | `0 errors, 0 warnings, 0 informations` | Confirmada |
| Alembic sem heads | `alembic heads`: saída vazia, rc 0 | Confirmada |
| Compose validado | `docker compose config --quiet` com valores fictícios, rc 0. Arquivo **idêntico byte a byte** ao bloco de Prompt F1 §9.3 | Confirmada |
| `ruff format --check .` falha por blocos Python do documento protegido | Único arquivo acusado: `docs/arquitetura/arquitetura_api_minhavida.md` (15 blocos). A falha **já existe no baseline** (§7.1) | Confirmada, com origem mais precisa |
| `ruff format .` alterou o documento, que foi restaurado do HEAD com hash conferido | Bytes atuais iguais ao blob do baseline (`2a2f155e…`). O `mtime` (19:37:41) é posterior ao commit (19:13:38) e cai dentro da janela da implementação. O mecanismo foi reproduzido em cópia | Compatível. A cronologia intermediária não é verificável (ACH-MV-F1-004) |
| `ruff format --check src tests` passa | `26 files already formatted`, rc 0. Não substitui o gate obrigatório | Confirmada |
| Possíveis valores de colunas no `DETAIL` via `logger.exception` | Confirmado e **mais amplo** do que o relatado. Em violações de CHECK e NOT NULL, `Failing row contains (…)` grava a linha inteira (e-mail, nome e hash sintéticos) | Confirmada, agravada (ACH-MV-F1-002) |
| `aguardar_bloqueio` implementado, não usado no CT-F1-15, testado por sonda externa | O helper está correto: a sonda própria passou nos casos positivo e negativo (§7.3). A sonda do Sonnet não estava disponível | Confirmada pela sonda da auditoria |
| `Field(default=…)` | Padrões e restrições iguais à arquitetura §3.1 (introspecção dos 9 campos) | Confirmada, equivalente |
| `Settings.model_validate(...)` em fixtures, como forma de evitar fontes de ambiente | **Falso.** Com pydantic 2.13.5 e pydantic-settings 2.15.0, a chamada lê `.env` e variáveis de ambiente (§7.4) | **Refutada** (ACH-MV-F1-003) |
| `@override` no filtro de logging | Equivalente; apenas acrescenta verificação estática | Confirmada |
| Uma única supressão de Pyright, no ponto permitido | Única: `settings.py:42`, com justificativa | Confirmada |
| `uv sync` realizado implicitamente | Não houve comando separado. O `.venv` coincide com o `uv.lock` (§7.6) | Confirmada como desvio de procedimento sem impacto observado (ACH-MV-F1-006) |
| `alembic/env.py` fora do alcance automático do Ruff/Pyright | Confirmado: `exclude = [… "alembic"]` preexistente e `include = ["src", "tests"]` (§7.5) | Confirmada (ACH-MV-F1-005) |
| Nenhum commit da F1 e F2 não iniciada | HEAD = baseline, nenhuma revisão Alembic, `Base.metadata.tables` vazio | Confirmada |
| “Nenhum desvio de contrato” | Incorreta. Há gate obrigatório falho, alteração temporária de documento protegido e substituição da fixture com alegação de isolamento falsa | **Refutada** (ACH-MV-F1-006) |

---

## 5. Matriz CT-F1-01 a 20

Seleção executada uma vez: `tests/infra`. Os 26 nós passaram.

| CT | Nó(s) real(is) | Prova verificada na leitura e nas sondas | Resultado |
| --- | --- | --- | --- |
| 01 | `test_configuracao.py::test_settings_exige_database_url`, `::test_settings_rejeita_esquema_sem_eco`, `::test_settings_padroes` | Caminho real `obter_settings()`, com as 10 variáveis removidas, `chdir(tmp_path)` e cache limpo antes e depois. Independente do `.env` real | Passou |
| 02 | `::test_importacao_sem_efeitos` | Subprocesso sem `DATABASE_URL`, `cwd` vazio. Na sonda: `obter_settings.cache_info()` sem chamadas e `app.state` sem engine após a importação | Passou |
| 03 | `::test_obter_settings_cacheado`, `::test_criar_app_usa_settings_injetadas` | Identidade de objeto. `app.state.settings is settings_teste` dentro do lifespan | Passou |
| 04 | `test_saude.py::test_saude_ativo` | 200 `{"situacao":"ativo"}` | Passou |
| 05 | `::test_saude_pronto_com_banco` | `SELECT 1` no container | Passou |
| 06 | `::test_saude_pronto_sem_banco` | `127.0.0.1:1` (recusa imediata). O caminho do timeout de 2 s foi provado à parte: 192.0.2.1 → 503 em 2,005 s | Passou |
| 07 | `test_erros.py::test_erro_negocio_formato` | JSON completo comparado, `X-Teste` e `X-Request-ID` | Passou |
| 08 | `::test_validacao_sem_eco`, `::test_corpo_malformado` | O segredo enviado não aparece no corpo. `CORPO_INVALIDO` sem `campos` | Passou |
| 09 | `::test_rota_inexistente`, `::test_metodo_nao_permitido`, `::test_excecao_inesperada` | 404 e 405 (com `Allow`). 500 sem a mensagem interna, traceback no `caplog` e `id_requisicao` no registro. Na sonda, o 500 genérico tem `X-Request-ID` no cabeçalho e no corpo | Passou |
| 10 | `test_sessao_transacao.py::test_commit_no_router_persiste` | Contagem por conexão psycopg independente | Passou |
| 11 | `::test_erro_apos_escrita_desfaz` | 422 e 0 linhas (outra conexão) | Passou |
| 12 | `::test_dependencia_e_endpoint_mesma_sessao` | `id(sessao)` igual, autobegin na dependência e commit no router | Passou |
| 13 | `::test_falha_no_commit_nao_responde_sucesso` | Constraint `DEFERRABLE INITIALLY DEFERRED`. A falha ocorre no `COMMIT` (visível no traceback da execução) → 500 e 0 linhas | Passou |
| 14 | `::test_conexoes_devolvidas_ao_pool` | `checkedout() == 0` dentro do lifespan, após sucesso e `ErroNegocio`. Na sonda, também após 500 de banco e 500 genérico | Passou |
| 15 **c** | `::test_lock_timeout_vira_503` | Bloqueadora psycopg independente com `pg_advisory_lock(4242)` antes da requisição. Requisição com `lock_timeout` de 200 ms → 503, `CONFLITO_CONCORRENCIA`, `Retry-After: 1`. Após o unlock → 200. Sem `sleep`. Sondas: a requisição bloqueada durou 0,234 s (≥ 200 ms); com `lock_timeout` de 4 s, a requisição foi **observada em espera de Lock** em `pg_stat_activity` e concluiu com 200 após a liberação | Passou. Contenção real comprovada |
| 16 | `test_erros.py::test_id_requisicao_propagado_e_gerado` | Eco do valor válido. Ausente ou `x` → hex de 32. Sonda: 20 requisições concorrentes com 20 ecos corretos; `ContextVar` volta a `None` | Passou |
| 17 | `test_alembic_ambiente.py::test_upgrade_head_sem_revisoes` | Teste síncrono: `upgrade head`, `get_heads() == []` e `check`. A existência de `alembic_version` no container **não** é revisão de domínio | Passou |
| 18 | `::test_upgrade_com_conexao_compartilhada` | `run_sync` com `attributes["connection"]`. O `env.py` usa a conexão direta, sem `asyncio.run` | Passou |
| 19 | `::test_env_sem_app_e_sem_url` | Leitura textual de `env.py` e `alembic.ini` | Passou |
| 20 | `test_configuracao.py::test_guarda_recusa_banco_alheio` | Host `outro` → `RuntimeError` | Passou |

Contagem: 3 + 1 + 2 + 1 + 1 + 1 + 1 + 2 + 3 + 11 × 1 = **26**. O marcador `concorrencia` seleciona exatamente 1 de 26 (`--collect-only -m concorrencia`).

**Validade das provas:** as provas de banco usam outra conexão e o CT-F1-15 produz espera real. O defeito de ACH-MV-F1-002 não é detectado por nenhum CT atual, porque o CT-F1-13 não inspeciona o log. A fixture de ACH-MV-F1-003 torna os resultados dependentes do `.env` real nos 8 campos não informados.

---

## 6. Comandos executados

Ambiente: uv 0.11.29, Python 3.14.6 (`.venv`), Docker Server 29.7.2. O prefixo `uv run --no-sync --frozen` está disponível (`uv run --help`). Execução sequencial, sem paralelismo.

| # | Comando | rc | Resultado | Duração |
| --- | --- | --- | --- | --- |
| 1 | Inventário Git (§3 da solicitação: `pwd`, `rev-parse`, `status`, `ls-tree`, `diff --stat`, `diff --name-status`, `diff --cached`, `ls-files --others`) | 0 | §2.1 | — |
| 2 | `uv run --no-sync --frozen pytest tests/infra -q -p no:cacheprovider -rA --durations=0` | 0 | `26 passed in 11.08s`; 0 skip, 0 xfail | 15,4 s (parede) |
| 3 | `uv run --no-sync --frozen ruff check --no-fix .` | 0 | `All checks passed!` | 0,18 s |
| 4 | `uv run --no-sync --frozen ruff format --check .` | **1** | `1 file would be reformatted, 37 files already formatted` (o arquivo é `docs/arquitetura/arquitetura_api_minhavida.md`) | Não medida (falha na medição) |
| 5 | `uv run --no-sync --frozen pyright` | 0 | `0 errors, 0 warnings, 0 informations` | 7,18 s |
| 6 | `uv run --no-sync --frozen alembic heads` | 0 | Saída vazia (0 bytes) | 0,81 s |
| 7 | `POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose config --quiet` | 0 | Válido | — |
| 8 | `docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine` | 0 | `postgres@sha256:fe0737ba566a2c5b2a28f34433c0a423261900ec17b9bf7ad115e1aae7e57f1b` (igual ao informado) | — |
| 9 | `uv run --no-sync --frozen ruff format --check src tests` | 0 | `26 files already formatted` (complementar) | — |
| 10 | `uv run --no-sync --frozen ruff format --check` nos outros 11 `.md` rastreados | 0 | `11 files already formatted`. Total: 26 + 11 + 1 = 38, o que confirma a composição do comando 4 | — |
| 11 | `uv run --no-sync --frozen ruff format --diff docs/arquitetura/arquitetura_api_minhavida.md` | 1 | 15 trechos, 137 linhas removidas e 384 acrescentadas, em §3.2, §5.3, §6.1, §8.2–§8.8 e §10.1 | — |
| 12 | `ruff format --check --no-cache .` em cópia de `git archive bd2b2e0` (temporário) | 1 | `1 file would be reformatted, 17 files already formatted` (mesmo arquivo): a falha é **preexistente** | — |
| 13 | `ruff check --no-fix --no-cache alembic/env.py` (diagnóstico explícito, fora do gate) | 1 | `PLC0415` em `env.py:28`, o import local exigido pelo Prompt F1 §8.7 | — |
| 14 | `ruff format --check --no-cache alembic/env.py` e `pyright alembic/env.py` | 0 / 0 | Formatado; 0 erros | — |
| 15 | `pytest tests/infra -m concorrencia --collect-only -q -p no:cacheprovider` | 0 | `1/26 tests collected (25 deselected)` | 0,21 s |
| 16 | Sondas externas (§7 e anexo D) | 0 | Ver §7 | sonda de banco: 6,9 s |

Observações:

- No comando 2, os flags `-p no:cacheprovider -rA --durations=0` não alteram a seleção. Evitaram gravar `.pytest_cache` e só ampliaram o relato.
- O comando 4 rodou **uma vez** sobre este conteúdo. O sucesso de outros comandos não representa o sucesso do 4.
- Não executei: `ruff format .`, `ruff check --fix`, `task lint`, `task test`, `pytest` sem seleção, `uv sync`, `uv add`, atualização de lock, `alembic upgrade` fora do container, `docker compose up` nem `docker compose down`.

---

## 7. Investigações específicas

### 7.1. Formatação e documento protegido (ACH-MV-F1-001 e 004)

1. **Configuração efetiva.** Com `[tool.ruff.format] preview = true`, o Ruff 0.16.10 formata blocos Python em Markdown. O formatador considerou 38 arquivos (26 `.py` e 12 `.md`). O lint considerou 27 (26 `.py` e `pyproject.toml`), nenhum `.md`.
2. **Arquivos envolvidos.** Só `docs/arquitetura/arquitetura_api_minhavida.md`. Os outros 11 `.md` e os 26 `.py` já estão formatados.
3. **Proposta do formatador** (`--diff`). Reescreve 15 blocos de pseudocódigo: quebra de argumentos, linhas em branco e alinhamento de comentários. Não muda a semântica, mas muda 521 linhas e o hash de um documento canônico.
4. **Identidade do documento.** O arquivo atual, o blob de `bd2b2e0` e o hash da Etapa A informado (`2a2f155e…`) coincidem.
5. **Origem da falha.** A cópia do baseline falha da mesma forma, então a falha não decorre da F1. O comando normativo de implementação (`ruff format .`, Prompt F1 §14, passo 4, e `CLAUDE.md` §2) **reescreve** o documento protegido, o que foi reproduzido em cópia (hash resultante `16c9b835…`). A falha não é atribuível ao Sonnet.
6. **Restauração.** A igualdade final de bytes, o `mtime` de 19:37:41 (os demais documentos estão em ≤ 18:43:37) e o relato do Sonnet são compatíveis com uma escrita durante a implementação seguida de restauração. Não é possível verificar o conteúdo intermediário nem a duração da alteração.
7. **Incidente registrado** como ACH-MV-F1-004. A restauração não apaga o registro.

**Recomendação (DEC-MV-26, anexo B):** excluir Markdown da formatação com `[tool.ruff.format] exclude = ["*.md"]`. A proposta foi validada numa cópia externa:

- `ruff format --check .` → `26 files already formatted`, rc 0;
- `ruff check --no-fix .` inalterado (27 arquivos, `All checks passed!`);
- `ruff format .` em modo de escrita deixa os 12 `.md` intactos (todos os hashes conferem);
- controle positivo: um `.py` desformatado de propósito continua sendo acusado (rc 1).

**Não aplicada.** A mudança altera configuração protegida e depende do usuário.

### 7.2. Logs e conteúdo de exceções do PostgreSQL (ACH-MV-F1-002)

**Fluxo real.** Em `erros.py:267-277`, `tratar_banco` chama `logger.exception(...)` quando o status é 500. O logger `api_gestao_pessoal.erros` propaga para `api_gestao_pessoal`, que tem um `StreamHandler` com `Formatter(FORMATO_LOG)`. Por causa do `exc_info`, o `Formatter` anexa o traceback com a cadeia de exceções, que inclui a mensagem do driver e o `DETAIL`. `hide_parameters=True` funciona (`[SQL parameters hidden due to hide_parameters=True]`), mas não cobre o `DETAIL`.

**Evidência 1: a própria suíte entregue.** Na execução de `tests/infra`, o log formatado do handler real da aplicação, no CT-F1-13, contém duas vezes `DETAIL:  Key (unico)=(…) already exists.`. O valor é o sintético do teste.

**Evidência 2: sonda com sentinelas sintéticas.** Usei o app original (`criar_app`) com rotas da sonda, um container próprio e captura da saída do handler real em arquivo. O valor é a contagem de ocorrências das sentinelas na saída formatada:

| Caso (SQLSTATE) | `DETAIL` | E-mail | Nome | Hash | `getMessage()` | Corpo HTTP |
| --- | --- | --- | --- | --- | --- | --- |
| UNIQUE (23505) | `Key (email)=(…)` | 2 | 0 | 0 | 0 | 0 |
| CHECK (23514) | `Failing row contains (…)` | 2 | 2 | 2 | 0 | 0 |
| NOT NULL (23502) | `Failing row contains (…)` | 2 | 2 | — (nulo) | 0 | 0 |
| Controle positivo: divisão por zero (22012), mesmo caminho | — | — | — | — | — | Mensagem `division by zero` capturada 2× |
| Controle positivo: exceção genérica | — | — | — | — | — | Mensagem de controle capturada 2× |

Conclusões:

- **Exposição confirmada com dados sintéticos.** Não há exposição real: a F1 não tem tabelas nem dados pessoais. Não alego incidente.
- A ausência de valores em `getMessage()` **não** prova ausência no log: o vazamento está no traceback formatado.
- **Risco futuro concreto.** Na F3, uma `IntegrityError` não traduzida (que a arquitetura §4.4 trata como defeito) registraria e-mail, nome e `senha_hash`, por exemplo via `Failing row contains` numa violação de CHECK ou NOT NULL em `usuario`.
- **Causa normativa.** Prompt F1 §8.5, item 4, e a premissa de §3.4 sobre `hide_parameters`. A arquitetura §3.4, aceita, prevalece sobre o prompt (`indice.md` §3).

**Comportamento seguro esperado** (especificado no prompt de correções):

- no 500 de banco, registrar só identificadores: `sqlstate`, classe, esquema, tabela, coluna, restrição e `id_requisicao`;
- incluir a pilha de chamadas **sem mensagens** (`traceback.format_tb`), sem `exc_info`;
- manter inalterados os 503 (`warning` com o código) e o 500 genérico (traceback completo, exigido pelo CT-F1-09).

Essa proposta foi validada em sonda: `sqlstate=23505 … restricao=uq_registro_unico` e `sqlstate=23502 … coluna=valor`, sem sentinela e sem `DETAIL` na descrição nem na pilha.

**Observação não verificada por execução.** Fora do `ASGITransport`, o `ServerErrorMiddleware` do Starlette relança a exceção genérica depois de responder, e o servidor (uvicorn) registra o traceback de novo, fora do filtro da aplicação. Isso não afeta os erros de banco, tratados no `ExceptionMiddleware`. Fica como ponto da F11.

### 7.3. CT-F1-15 e `aguardar_bloqueio`

- **CT-F1-15:** a contenção é real. A bloqueadora psycopg independente segura `pg_advisory_lock(4242)` antes da requisição, e a requisição usa outra conexão, do pool da app, com `lock_timeout` de 200 ms. A sonda mediu 0,234 s até o 503 e, com 4 s de timeout, observou a sessão em `wait_event_type = 'Lock'` antes de liberar. Não há `sleep` nem mock, e cada participante tem conexão própria. Os recursos são encerrados por context managers. **Sem achado.**
- **Helper:** `tests/apoio/banco.py:35-55` usa polling de 0,02 s com limite por `time.monotonic()` e mensagem clara.
  - Sonda negativa (ninguém bloqueado, timeout 0,3 s): `TimeoutError` em 0,314 s com “observadas: 0”.
  - Sonda positiva (bloqueadora e duas esperas reais em conexões próprias): retornou em 0,02 s, com as duas tarefas ainda bloqueadas; ambas concluíram após o unlock.
- O CT-F1-15 não precisa do helper, porque a trava é obtida antes da requisição e o próprio timeout prova a espera. Não imponho polling adicional, que tornaria o caso frágil. O uso do helper será exigido nos CTs de concorrência da F4 (plano §3.5). **Sem achado.**

### 7.4. Settings e demais ajustes (ACH-MV-F1-003)

**`Settings.model_validate`.** A sonda rodou num diretório temporário com `.env` **sintético** e variáveis `LOG_NIVEL=DEBUG` e `DB_POOL_SIZE=7`:

| Forma | `LOG_NIVEL` | `DB_POOL_SIZE` | Campo do `.env` sintético |
| --- | --- | --- | --- |
| `Settings.model_validate({...})` (entregue) | DEBUG (ambiente) | 7 (ambiente) | lido |
| `Settings(..., _env_file=None)` (contrato §11.1) | DEBUG (ambiente) | 7 (ambiente) | ignorado |
| `Settings(...)` | DEBUG | 7 | lido |
| `SettingsTeste` proposta (só `init_settings`) | INFO | 5 | ignorado |

`DATABASE_URL` e `AMBIENTE` explícitos **prevalecem** sobre o `.env` e sobre a variável `DATABASE_URL` (verificado com valores sintéticos). Portanto **não há risco** de a app de teste apontar para o banco de desenvolvimento, e a guarda continua válida. O problema é de hermeticidade:

- os 8 campos restantes vêm do `.env` real e do shell;
- na F3, `EMAIL_MODO`, `SMTP_*` e `JWT_SEGREDO` seriam herdados do `.env` real pelos testes.

A forma do contrato (`_env_file=None`) gera erro de Pyright e também não isola o ambiente. A correção proposta, `SettingsTeste`, passou em Ruff e Pyright sem supressões, valida o esquema sem eco e foi provada hermética.

**Demais ajustes:**

- `Field(default=…)`: equivalente.
- CT-F1-01 a 03 exercitam `obter_settings()` com ambiente controlado e cache isolado.
- Imports relativos estão dentro da autorização, sem mudança de `sys.path`, Ruff ou Pyright.
- A supressão de Pyright é única e justificada. `@override` é equivalente.
- `criar_app_teste` fica em `tests/apoio/rotas_teste.py` e faz exatamente `criar_app(settings)` + `include_router(router)`. O OpenAPI do app de produção tem só `/saude` e `/saude/pronto`, sem `GET /` e sem rotas de teste.

### 7.5. Alembic e banco descartável

- `env.py` foi revisto manualmente contra Prompt F1 §8.7 e arquitetura §10.5:
  - `fileConfig` condicional;
  - `target_metadata` vindo de `models`;
  - URL de `attributes` ou das Settings, por import local;
  - modo offline com `literal_binds`;
  - online com `NullPool` e `run_sync`;
  - conexão compartilhada usada diretamente;
  - não importa `main` nem `database`.
- `script.py.mako` difere do template async só nas docstrings em PT-BR. `alembic.ini` não tem `sqlalchemy.url`.
- Não há `create_all`, `drop_all` nem `stamp`. O schema `teste_infra` fica fora do metadata. A guarda exige host, porta e nome do container antes de `CREATE`, `DROP` e `TRUNCATE`, e a URL vem do container. O CT-F1-20 prova a recusa.
- **Cobertura de ferramentas:** `alembic/` está fora do Ruff (exclusão preexistente) e do Pyright (`include`). O diagnóstico explícito, fora do gate, deu Pyright com 0 erros e Ruff com `PLC0415`, que corresponde ao import local exigido pelo contrato. **Não declaro** cobertura automática de lint e tipagem para `alembic/` (ACH-MV-F1-005).

### 7.6. Dependências e sincronização

- `pyproject.toml` mudou só nas linhas autorizadas: `requires-python >=3.14`, `pydantic-settings>=2.15.0`, `httpx>=0.28.1` (dev) e o marcador `concorrencia`.
- `uv.lock`: nenhum pacote foi adicionado, removido ou mudou de versão (85 → 85). As 403 linhas removidas são artefatos de Python < 3.14: 390 wheels cp312/cp313, 4 wheels graalpy312, `resolution-markers`, `requires-python` e 3 marcadores `python_full_version < '3.13'`. As versões travadas conferem com Prompt F1 §1.
- `.venv` × lock, verificado só por leitura: as 82 distribuições instaladas coincidem com o lock. Não há versões divergentes nem pacotes extras. Faltam só `mslex`, `pywin32` e `tzdata`, todos com marcador `sys_platform == 'win32'`.
- O passo 2 (`uv sync`) **não foi executado** como comando. A garantia pretendida, ambiente igual ao lock, foi atingida neste ambiente. Registro como desvio de procedimento sem impacto (ACH-MV-F1-006), não como falha de ambiente.

### 7.7. Credenciais e histórico

- O `compose.yaml` é idêntico ao bloco de §9.3: interpolação das três variáveis e porta em `127.0.0.1`.
- O histórico tem um único commit, sem `compose.yaml` nem `.env` em nenhum objeto, e sem objetos inalcançáveis.
- Ocorrências de `POSTGRES_PASSWORD` no HEAD: interpolação, placeholder `SENHA` e o valor fictício `verificacao`. Nenhum valor foi reproduzido.
- Nenhum segredo literal nos arquivos novos. As URLs dos testes são fictícias, e a senha do container de teste é gerada.
- Escopo do produto: não há tabelas de domínio, autenticação, serviços nem infraestrutura financeira externa.

---

## 8. Achados

Escala e estados conforme o plano de validação §7. IDs novos, sem colisão (`ACH-MV-F1-NNN` não existia).

| ID | Sev. | Título | Origem | Estado |
| --- | --- | --- | --- | --- |
| ACH-MV-F1-001 | **P2** | Gate `ruff format --check .` falha por Markdown protegido | Ferramenta, configuração e comandos normativos | ABERTO, aguarda DEC-MV-26 |
| ACH-MV-F1-002 | **P2** | Log de 500 de banco grava valores de colunas (`DETAIL`) | Contrato (Prompt F1 §8.5, item 4), implementação conforme | ABERTO |
| ACH-MV-F1-003 | **P2** | `settings_teste` lê `.env` e variáveis de ambiente | Implementação e contrato (§11.1 × §9.5) | ABERTO |
| ACH-MV-F1-004 | P3 | Documento protegido alterado temporariamente durante a implementação | Comando normativo (§14, passo 4) | ABERTO, acompanhamento |
| ACH-MV-F1-005 | P3 | `alembic/` fora do Ruff e do Pyright | Configuração preexistente | ABERTO, decidir antes da F2 |
| ACH-MV-F1-006 | P3 | Imprecisões no relatório e `uv sync` não executado | Relatório da implementação | ABERTO |

### ACH-MV-F1-001 — P2 — Gate de formatação falha por Markdown protegido

- **Fato:** `ruff format --check .` retorna rc 1 apenas por `docs/arquitetura/arquitetura_api_minhavida.md`. A falha é preexistente: a cópia de `bd2b2e0` também retorna rc 1.
- **Fonte normativa:** Prompt F1 §12 (aceite: Ruff limpo) e §14, passo 7; plano §5.1; `CLAUDE.md` §2; Prompt F1 §7.4 (documentos protegidos).
- **Evidência:** comandos 4 e 9–12 (§6) e §7.1.
- **Impacto:** o gate obrigatório não passa sem alterar documento ou configuração protegidos, e o comando de implementação reescreve o documento canônico a cada execução. Bloqueia a F1 e toda fase futura que use o mesmo gate.
- **Correção recomendada:** DEC-MV-26, opção B (anexo B), aplicada pelo Sonnet no prompt de correções. Nenhuma mudança em documentos.
- **Encerramento:**
  - DEC-MV-26 aprovada e aplicada;
  - no repositório, `ruff format --check .` com rc 0 e nenhum `.md` listado;
  - `ruff check --no-fix .` sem regressão;
  - hashes de `docs/**`, `PROMPTS/**` e `CLAUDE.md` iguais ao anexo A;
  - verificado na reauditoria.
- **Responsáveis:** usuário (decisão), Sonnet (aplicação), Opus (reauditoria).

### ACH-MV-F1-002 — P2 — Log de 500 de banco grava valores de colunas

- **Fato:** `src/api_gestao_pessoal/erros.py:271-272` (`logger.exception`). A saída formatada inclui `DETAIL` com valores, e, em CHECK e NOT NULL, a linha inteira.
- **Fonte normativa:** arquitetura §3.4 (aceita), §11 (F1+) e §12 (“Logs … Sem PII”). Tensão com o Prompt F1 §8.5, item 4 (§3.3).
- **Evidência:** saída da suíte (CT-F1-13) e a sonda da §7.2, com controles positivos.
- **Impacto:** nenhuma exposição real na F1. Exposição confirmada com dados sintéticos. Na F3+, qualquer `IntegrityError` não traduzida grava e-mail, nome e hash de senha. O fundamento de tratamento de erros entregue na F1 é reutilizado por todas as fases.
- **Correção recomendada:** prompt de correções §7.2 e §7.4, com o teste REG-F1-01 (deve falhar antes da correção e passar depois). Atualizar o texto do Prompt F1 §8.5, item 4, e da arquitetura §3.4 (P-DOC-01 e P-DOC-03).
- **Encerramento:**
  - REG-F1-01 falha antes e passa depois;
  - CT-F1-09, 13 e 15 continuam passando;
  - a reauditoria repete a sonda de sentinelas (UNIQUE, CHECK, NOT NULL), com zero sentinelas e zero `DETAIL` na saída formatada e os controles positivos capturados.
- **Responsáveis:** Sonnet (código), Opus (texto normativo e reauditoria), usuário (autorização).

### ACH-MV-F1-003 — P2 — `settings_teste` não é hermética

- **Fato:** `tests/conftest.py:40-45` usa `Settings.model_validate(...)`, que passa pelas fontes do pydantic-settings e lê `.env` do diretório corrente e variáveis de ambiente (§7.4).
- **Fonte normativa:** Prompt F1 §11.1 (`_env_file=None`) e plano §3.2–3.3 (isolamento; a URL vem do container, nunca do ambiente). O relatório alegou isolamento.
- **Evidência:** sondas de §7.4. Teste REG-F1-02 em cópia: com o código atual, `assert 7 == 5` (vermelho).
- **Impacto:**
  - 17 dos 26 testes dependem da fixture, direta ou indiretamente (via `app_teste`);
  - os resultados variam com o `.env` real e o shell;
  - na F3, os testes herdariam a configuração real de SMTP e JWT;
  - nenhum risco ao banco de desenvolvimento, porque `DATABASE_URL` é explícito e prevalece.
- **Origem:** o contrato era inviável na forma literal (Pyright) e não hermético. A implementação substituiu a forma sem verificar e relatou um efeito inexistente. O correto seria parar e relatar (Prompt F1 §9.5 e §12).
- **Correção recomendada:** `SettingsTeste` (somente `init_settings`) e REG-F1-02 (prompt de correções §7.3 e §7.5). Atualizar o Prompt F1 §11.1 (P-DOC-02).
- **Encerramento:** REG-F1-02 falha antes e passa depois; `tests/infra` verde; reauditoria com sonda de `.env` sintético.

### ACH-MV-F1-004 — P3 — Alteração temporária de documento protegido

- **Fato:** `docs/arquitetura/arquitetura_api_minhavida.md` foi escrito durante a implementação (`mtime` de 19:37:41 -0300) e tem hoje os bytes do baseline.
- **Fonte normativa:** Prompt F1 §7.4 e §12. O comando prescrito no §14, passo 4, causa a escrita.
- **Evidência:** §7.1, itens 5 e 6.
- **Limite:** conteúdo intermediário e duração não verificáveis.
- **Impacto:** nenhum efeito persistente constatado. O risco de recorrência continua até a DEC-MV-26.
- **Conduta:** o Sonnet executou o comando prescrito, restaurou o arquivo a partir do HEAD e relatou o ocorrido. A restauração foi uma escrita não prevista. O procedimento previsto era parar e relatar.
- **Encerramento:** DEC-MV-26 aplicada e `ruff format .` comprovadamente sem efeito sobre `.md` (prova em cópia, na reauditoria).

### ACH-MV-F1-005 — P3 — `alembic/` fora do Ruff e do Pyright

- **Fato:** `pyproject.toml` tem `[tool.ruff] exclude` com `"alembic"` desde o baseline, e o `include` do Pyright é `["src", "tests"]`.
- **Impacto:** na F1 é pequeno, porque `env.py` foi revisto manualmente e está conforme. Na F2 é maior: as revisões em `alembic/versions/` ficariam fora dos gates.
- **Correção recomendada:** decidir **antes da liberação do Prompt F2** entre duas opções:
  - incluir `alembic/` no Ruff e no Pyright, com `per-file-ignores` restrito a `alembic/env.py = ["PLC0415"]`;
  - manter a exclusão, com uma lista de revisão manual obrigatória.

  Não faz parte das correções da F1.
- **Encerramento:** decisão registrada no `indice.md` antes do Prompt F2.
- **Responsáveis:** Opus (proposta), usuário (decisão).

### ACH-MV-F1-006 — P3 — Precisão do relatório e procedimento

- **Fatos:**
  - o `uv sync` (§14, passo 2) não foi executado; o ambiente foi verificado igual ao lock;
  - a frase “nenhum desvio de contrato” é incorreta;
  - a alegação sobre `model_validate` é falsa;
  - os hashes completos das fontes da Etapa A não foram apresentados, exceto dois.
- **Impacto:** baixo, porque a evidência foi refeita, mas reduz a confiança no relatório.
- **Encerramento:** o relatório das correções lista os comandos literalmente executados, separa “executado”, “implícito” e “não executado” e descreve cada desvio.

### Achados de arquitetura relacionados

| Achado | Situação constatada |
| --- | --- |
| ACH-MV-ARQ-019 (P2, baseline) | Conteúdo **verificado pelo Opus**: HEAD com exatamente os 22 caminhos de §3.5 e blobs com os hashes do Prompt F1 §1 (os 11 rastreados). O bloco de revalidação do Sonnet (Prompt F1 §1.2, a–e) não estava disponível, então o encerramento formal depende de anexar esse bloco do relatório da F1. Não declarado encerrado |
| ACH-MV-ARQ-006 (P3, credenciais no compose) | O critério técnico está atendido no objeto (arquivo idêntico a §9.3, `config` válido). O arquivo entra no histórico na integração da F1 (G6). Encerrar na conferência do commit da F1 |
| ACH-MV-ARQ-024 (P2, orientação `git add -A`) | Histórico verificado sem `compose.yaml` e sem `.env`. Segue DOCUMENTADO |

---

## 9. Verificações não executadas ou inconclusivas

| Item | Motivo |
| --- | --- |
| Valores do `.env` real absorvidos pela fixture (nesta auditoria e na execução do Sonnet) | Leitura do `.env` proibida. Mecanismo provado só com `.env` sintético |
| Bloco de revalidação do baseline e hashes completos da Etapa A | Não fornecidos como arquivo |
| Conteúdo intermediário do documento alterado e duração da alteração | Não há evidência histórica completa |
| Sonda do Sonnet para `aguardar_bloqueio` | Não disponível. Substituída pela sonda da auditoria |
| Duração do comando 4 | Medição inválida (erro de cálculo no script). O resultado e o rc são válidos |
| Comportamento sob uvicorn (log duplicado de exceção genérica) | Não executado. Observação teórica (§7.2) |
| `statement_timeout` e `idle_in_transaction_session_timeout` em execução | Sem CT no contrato. Configuração conferida só por leitura (`database.py`) |
| `alembic upgrade` no banco de desenvolvimento | Proibido e fora do escopo |

---

## 10. Integridade do objeto durante a auditoria

- O manifesto do início (anexo A) foi conferido de novo ao final: **48/48 iguais**, e o `git status --short` só mudou pelos dois arquivos criados por esta auditoria. Resultado final em §10.1.
- Nenhum comando de escrita foi executado no repositório. Formatações, cópias e aplicações de propostas ocorreram **só** em cópias no diretório temporário da sessão, sem o `.env`.
- Caches ignorados (`.ruff_cache/` e `__pycache__/`) podem ter sido atualizados pelos comandos de verificação e pelo pytest. São artefatos, fora do objeto, e não devem ser versionados. O `.pytest_cache/` não foi gravado (`-p no:cacheprovider`).
- Os containers das sondas foram removidos ao fim de cada sonda (`docker ps -a` vazio).

### 10.1. Conferência final

Executada ao final, depois da gravação do prompt de correções e antes da gravação deste relatório:

| Verificação | Resultado |
| --- | --- |
| Manifesto de 48 arquivos (anexo A) | **48/48 idênticos** ao início da auditoria |
| Bloco B do prompt de correções (42 protegidos) | 42/42 OK |
| Bloco A (6 arquivos a corrigir) | 6/6 OK, inalterados pelo auditor |
| `HEAD` | `bd2b2e0f1e4f2674b528175e535b0931badec34a` (inalterado) |
| Índice do Git | Vazio |
| `git status --short` | Igual ao início, mais os dois arquivos desta auditoria |
| Ignorados presentes | Os mesmos 13 caminhos do início (nenhum novo) |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` (criado pela auditoria) | `4d711cd17361427b9282a626fdfd4832a83bfa66119650631f45ad132139da5c` |
| Este relatório (criado pela auditoria) | Não pode conter o próprio hash. O Sonnet registra o SHA-256 na Etapa A das correções |

Os dois documentos não contêm blocos `python`; os trechos de código estão em blocos `diff`. Assim, não acrescentam falhas ao `ruff format --check .` enquanto a DEC-MV-26 não for decidida. A conferência por `ruff format --check` explícito nos dois arquivos foi feita depois da gravação.

---

## 11. Situação

| Item | Estado |
| --- | --- |
| **F1** | **`BLOQUEADO`** (G5). ACH-MV-F1-001 a 003 (P2) abertos |
| Commit e integração da F1 (G6) | **Não realizar.** A F1 não está aprovada. O commit deve conter o conteúdo reauditado, não o atual |
| Prompt de correções | `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md`: **`BLOQUEADO`** até a DEC-MV-26 (condição de liberação no próprio prompt) |
| Prompt F2 | **Não criado.** A F1 está bloqueada (instrução §10 da solicitação) |
| Gates que faltarão à F2 | F1 aprovada e integrada; DEC-MV-06 (ADR-0002); DEC-MV-07 (restante de D-09); DEC-MV-08 (aceitar ou rejeitar, com reconciliação); `CLAUDE.md` e modelo físico reconciliados (diff do ADR-0002); decisão sobre ACH-MV-F1-005. DEC-MV-24 segue para antes da F5, sem bloquear a F2 |

---

## 12. Próxima ação do usuário

1. **Decidir a DEC-MV-26** (anexo B). Texto pronto para aprovar:

   > Aprovo a DEC-MV-26, opção B: acrescentar `exclude = ["*.md"]` em `[tool.ruff.format]` do `pyproject.toml`, conforme o anexo B de `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md`.

   Para rejeitar, responda “Rejeito a DEC-MV-26” e indique a opção A ou C. O prompt de correções será então revisado antes do envio.
2. **Avaliar a correção dos logs (ACH-MV-F1-002).** Ela retira a mensagem do driver do log de 500 de banco, alinhando o Prompt F1 à arquitetura §3.4, que é aceita. Se preferir manter o traceback completo, isso seria uma exceção ao §3.4, e só você pode aceitá-la.
3. **Enviar o prompt de correções ao Sonnet, só para a Etapa A**, com a aprovação do item 1 na mesma mensagem. Revisar o plano e responder “pode implementar” somente se estiver de acordo.
4. **Não fazer commit da F1 agora.** Depois da implementação das correções, pedir a reauditoria ao Opus. Ela cobre os achados e os efeitos diretos, mais a aplicação das propostas documentais P-DOC-01 a 05 que você aprovar.

---

## Anexo A — Manifesto do objeto auditado

Condição em relação a `bd2b2e0`. A coluna “baseline” traz o SHA-256 do blob no commit; “atual” traz o do arquivo na árvore de trabalho.

| Arquivo | Condição | SHA-256 baseline | SHA-256 atual |
| --- | --- | --- | --- |
| `.env.exemplo` | criado | `—` | `dc824d5228126e5cfa2ef3c6fe3c939fb99fc3303487109bd1d0c443867dfdb0` |
| `.gitignore` | alterado | `69aa73cf5bc3377a7d97f2e8d2bb773195815efe225af7f1be6f5b9306bbe14f` | `5b7e3c47d39481cea53c19583158f9fa93185f86346ae0a2cc814ff92e84f973` |
| `.python-version` | inalterado (protegido) | `a876e0b10411037a012498b9fe18d9bc1df32ed8b722a13564dc944ddcfd9135` | `a876e0b10411037a012498b9fe18d9bc1df32ed8b722a13564dc944ddcfd9135` |
| `CLAUDE.md` | inalterado (protegido) | `565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473` | `565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md` | inalterado (protegido) | `38386a4fdfd3ce1c4f05214cc7a327e94fe8fff6db4dcf97f7d5a354a9472785` | `38386a4fdfd3ce1c4f05214cc7a327e94fe8fff6db4dcf97f7d5a354a9472785` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md` | inalterado (protegido) | `2535a838ff3e3f579de349114ff69433f3a7e00cb3e033e41624901dd7693f41` | `2535a838ff3e3f579de349114ff69433f3a7e00cb3e033e41624901dd7693f41` |
| `README.md` | inalterado (protegido) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `alembic.ini` | criado | `—` | `85e531a52b75ea3dbe5202fea719e871393606647ab28b739ad82ae842e27306` |
| `alembic/env.py` | criado | `—` | `10563c24868c0921987c9953ad1f3f12915aedc82bdfc5ec59ef9013b5fe55c1` |
| `alembic/script.py.mako` | criado | `—` | `b37123fcbbe9acb6a1890d253752bc7e4cebb2d787e6a0fb35387f99907eafba` |
| `alembic/versions/.gitkeep` | criado | `—` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `compose.yaml` | criado (não rastreado por decisão; substitui o arquivo de partida) | `—` | `bb1d211f5a498400c8ff4e0a4c54da2d6e6647e2c7069fdc3775558dfdcbf997` |
| `docs/adr/0001_arquitetura_api_minhavida.md` | inalterado (protegido) | `756c944897a4ec8f990ec4bae6062cedb480c2488f4913168341c309e2b38fa2` | `756c944897a4ec8f990ec4bae6062cedb480c2488f4913168341c309e2b38fa2` |
| `docs/adr/0002_identificadores_uuid.md` | inalterado (protegido) | `d710c7cc28685a138f615b1070976c12dd39607a2fe31af1b7b99d3035833ec8` | `d710c7cc28685a138f615b1070976c12dd39607a2fe31af1b7b99d3035833ec8` |
| `docs/arquitetura/analise_projeto_minhavida.md` | inalterado (protegido) | `44bb46f0c36437305c45c82d7c04a4fa0fe5320dd120c9f79d4d406f67b6364f` | `44bb46f0c36437305c45c82d7c04a4fa0fe5320dd120c9f79d4d406f67b6364f` |
| `docs/arquitetura/arquitetura_api_minhavida.md` | inalterado (protegido) | `2a2f155e92af0fcbb06400234545974b0dff334677cea3c1c734528fc4e6b70b` | `2a2f155e92af0fcbb06400234545974b0dff334677cea3c1c734528fc4e6b70b` |
| `docs/arquitetura/indice.md` | inalterado (protegido) | `0d100e6d7c95aed221878152c221b8a8dcb4dc95bb7572d41c00d5824f01777e` | `0d100e6d7c95aed221878152c221b8a8dcb4dc95bb7572d41c00d5824f01777e` |
| `docs/arquitetura/matriz_requisitos_api.md` | inalterado (protegido) | `e0f9c1a485106204f5d64bf3250ef0a1239b36e672fc0f015a9339d2ef6ec09c` | `e0f9c1a485106204f5d64bf3250ef0a1239b36e672fc0f015a9339d2ef6ec09c` |
| `docs/arquitetura/plano_fases_api.md` | inalterado (protegido) | `5f9048f750f7bbc232a68048daad2f8622f150f398d06399fa5010a2a7a26afe` | `5f9048f750f7bbc232a68048daad2f8622f150f398d06399fa5010a2a7a26afe` |
| `docs/arquitetura/plano_validacao_auditoria.md` | inalterado (protegido) | `92d210fbcb833b19f21f8dc51d25bb000c5be8c8e861038bd2dd6eeac6ef92e5` | `92d210fbcb833b19f21f8dc51d25bb000c5be8c8e861038bd2dd6eeac6ef92e5` |
| `pyproject.toml` | alterado | `b3bf08c5b0702b0c8189929ce7b52de36d357c943d6aece5c1d92331ab4bb779` | `54bd1c986794bb98136cfc9997420759f943711ab9b1645b3b10c903883864d5` |
| `src/api_gestao_pessoal/__init__.py` | criado | `—` | `d8fda8c0aa1da349c8b8ff625f864c58514c272048d9f391bf38650bd623f894` |
| `src/api_gestao_pessoal/database.py` | alterado | `1df5342368bc8e3c8c2f46c549fffb3544bcfb2e9036245e9d57bc0c88e7b2c9` | `50ab98141652b19a5ba21e690e6d6dacc74aa24b5803764e8c2541388d297def` |
| `src/api_gestao_pessoal/erros.py` | criado | `—` | `013d35ffb305d079ae865f1efba3288390eb6aecbca7b03c911e03e66daf3525` |
| `src/api_gestao_pessoal/main.py` | alterado | `2fd86f1d337b0965f1b2d61b557356e963962c626f7a6787132eb89c95ab3311` | `bb566f5402050cd6dd60bc581bf17e6925415cc256775f5210f5cfea45e263ee` |
| `src/api_gestao_pessoal/models/__init__.py` | criado | `—` | `dd692b63d6c5cbbcb4386cb146ef51b9e6d3b00259256aed1a85439eb059ca37` |
| `src/api_gestao_pessoal/models/base.py` | alterado | `ccd6fc1c8be2d07cfc3fba2f5c40e1fa7648ff67938a71717a91367048e2bc31` | `39cb5b83a05e05bcc13f627ca6190706303591763203fb288a17960561041ad9` |
| `src/api_gestao_pessoal/models/usuario.py` | inalterado (protegido) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `src/api_gestao_pessoal/rastreamento.py` | criado | `—` | `b92bb3c80336d23687aa2330c9fa75707a99620acd5f0e39b1acc9897972fc37` |
| `src/api_gestao_pessoal/routers/__init__.py` | criado | `—` | `b58e215bbb12c600de95a10edfb92534199cf042afb39fc67c8ad38e75d06ee5` |
| `src/api_gestao_pessoal/routers/saude.py` | criado | `—` | `5fbda750f3739079ea11d5a9a2b114fa795e2db1c4aa6f34786e1d89884d4b32` |
| `src/api_gestao_pessoal/schemas/__init__.py` | criado | `—` | `5c94fe6bbe63e2782be904b7373d7b90826b1abfd791ebdac7e9ffb1a60e8dc3` |
| `src/api_gestao_pessoal/schemas/erro.py` | criado | `—` | `df9c3382d0e5fed29a0f1347354b0cd5cb4b43e142a9944d0f85b90acf63bf5b` |
| `src/api_gestao_pessoal/schemas/message.py` | removido | `fc4d4b2fa5137f2f6fe74172f2026a88651f05a576733d2727d0b9a184daf270` | `—` |
| `src/api_gestao_pessoal/schemas/saude.py` | criado | `—` | `2dc25bfdb967b8bb0c88e69a2ee176de1cd5f03aefed898f429bc7ea94d91310` |
| `src/api_gestao_pessoal/settings.py` | alterado | `2824d0579509cdad9bf911d5c4783d93c49e60ea74a434494ad564f7e2374a58` | `039937f6322149f5ac87b586192e68418c29a562a0e2419f90669120192dd0f0` |
| `tests/__init__.py` | criado | `—` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/apoio/__init__.py` | criado | `—` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/apoio/banco.py` | criado | `—` | `b6f740c7ae285ab445bc7ba24bf299f7490e75b7736445c7b016b658df0b52ec` |
| `tests/apoio/rotas_teste.py` | criado | `—` | `8745ba8f239d81236d81ed08aef96221032c61466dbd004826ce81f5eabc9481` |
| `tests/conftest.py` | criado | `—` | `44d00c2f24c9c2d143cc3e2de901a342f3bfd93b2a4833e2238b9eb0ad2b7707` |
| `tests/infra/__init__.py` | criado | `—` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/infra/conftest.py` | criado | `—` | `f94ccc8eabd61e6bccb820035206c26c4011415a361cf71ae7baa330e06115ef` |
| `tests/infra/test_alembic_ambiente.py` | criado | `—` | `202360144c0c35ce6015cab57d15eedd07ad96b17842d4a385cb2ca615337f75` |
| `tests/infra/test_configuracao.py` | criado | `—` | `aaaa587237ec8461085bf23cf6b1dcaebdc929468bcb13601fb020421c6314de` |
| `tests/infra/test_erros.py` | criado | `—` | `c0fd9e88367c98ec7a4f0f0fc443e3e1860ee740847595a779f7e7d4a4ed4276` |
| `tests/infra/test_saude.py` | criado | `—` | `c90b30bfd099a22e008cf0fb7485fcb731d08e04cc0e1c1bf0c09068f8ddcacd` |
| `tests/infra/test_sessao_transacao.py` | criado | `—` | `e42dabbda535ae26a5161f3ef3325f1b1c3fd8acc71be2c1d18e778348aa3e48` |
| `uv.lock` | alterado | `77f733b52de6ab0af9b20be2c33351ffd9dcc57c73de7010275bfcd0e1a1755f` | `b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d` |

---

## Anexo B — Proposta de decisão DEC-MV-26 (não aplicada)

**Problema:** ACH-MV-F1-001 e 004.

**Decisão necessária:** como reconciliar os comandos de formatação na raiz com os documentos protegidos.

| Opção | Mudança | Efeitos |
| --- | --- | --- |
| **B (recomendada)** | `pyproject.toml`, `[tool.ruff.format]`: `exclude = ["*.md"]` | Os comandos de `CLAUDE.md`, do Prompt F1 e do plano ficam **inalterados** e passam a ser seguros. A formatação continua cobrindo todo `.py` (26 hoje). O lint não muda (nunca leu `.md`). Nenhum documento muda de hash |
| A | Delimitar os comandos a `src tests` (`CLAUDE.md` §2, Prompt F1 §14, plano §5.1) | Exige alterar `CLAUDE.md` (protegido; DEC-MV-22 pendente) e três documentos. `ruff format .` continuaria reescrevendo documentos se alguém seguir a forma antiga. Diretórios Python futuros precisam ser lembrados nos comandos |
| C | Formatar os documentos | Reescreve 521 linhas de 15 blocos do documento canônico e muda seu hash. Os documentos passam a depender do formatador a cada edição. Pseudocódigo sujeito a reformatação automática |

Diff proposto (validado em cópia externa, §7.1):

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -39,6 +39,9 @@
 
 [tool.ruff.format]
 preview = true
+# Markdown fica fora da formatação: os blocos Python dos documentos
+# normativos (docs/, PROMPTS/, CLAUDE.md) são protegidos (DEC-MV-26).
+exclude = ["*.md"]
 quote-style = "double"
 indent-style = "space"
 
```

- **Arquivos atingidos:** só `pyproject.toml`, que é configuração protegida e por isso depende da sua aprovação.
- **Cobertura mantida:** todo `.py` na formatação; lint inalterado (27 arquivos).
- **Prova de correção:**
  - `ruff format --check .` com rc 0 e `26 files already formatted` (ou o número de `.py` vigente);
  - nenhum `.md` listado;
  - `sha256sum` dos documentos inalterado;
  - controle positivo: `.py` desformatado ainda acusado.
- **Quem aplica:** o Sonnet, no prompt de correções. **Quem registra:** o Opus (`indice.md` §4 e `analise` §9), após a aprovação.

## Anexo C — Propostas documentais (aplicar só após aprovação, em etapa separada)

| ID | Documento | Alteração proposta | Precisa de aprovação |
| --- | --- | --- | --- |
| P-DOC-01 | Prompt F1 §8.5, handler 4 | Trocar “log: `warning` para 503 e `exception` para 500, sem a URL e sem parâmetros” por: “log: `warning` com o código para 503; para 500, `error` **sem `exc_info`**, com `sqlstate`, classe, esquema, tabela, coluna e restrição (`exc.orig.diag`) e a pilha sem mensagens (`traceback.format_tb`). A mensagem do driver e o `DETAIL` nunca entram no log” | Sim: aplicada com a autorização das correções |
| P-DOC-02 | Prompt F1 §11.1, `settings_teste` | Trocar `Settings(DATABASE_URL=url_banco_teste, AMBIENTE="teste", _env_file=None)` por `SettingsTeste(DATABASE_URL=SecretStr(url_banco_teste), AMBIENTE="teste")`, onde `SettingsTeste` sobrescreve `settings_customise_sources` e retorna só `init_settings` | Sim: aplicada com a autorização das correções |
| P-DOC-03 | Arquitetura §3.4, último item (seção aceita) | Acrescentar: “`hide_parameters` não cobre as mensagens do PostgreSQL (`DETAIL`, `Failing row contains`), que podem conter valores; o handler de `DBAPIError` registra apenas identificadores (ACH-MV-F1-002)” | **Sim** (documento aceito) |
| P-DOC-04 | Plano de validação §4, F1 (catálogo aceito) | Acrescentar CT-F1-21 (500 de banco sem valores no log formatado; REG-F1-01) e CT-F1-22 (`settings_teste` ignora ambiente e `.env`; REG-F1-02) | **Sim** (catálogo aceito) |
| P-DOC-05 | `indice.md` §4 e §5; `analise` §9 | Registrar a autorização de implementação da F1 e a dos imports relativos em `tests/` (mensagem desta auditoria), a DEC-MV-26 se aprovada e os gates (G4 entregue; G5 `BLOQUEADO` com referência a este relatório) | Registro das suas próprias decisões |

## Anexo D — Sondas da auditoria

Todas ficaram fora do repositório, no diretório temporário da sessão, com dados sintéticos. Os módulos foram carregados do repositório **sem modificação**: os hashes de `main`, `erros`, `database`, `rastreamento`, `routers.saude`, `tests.apoio.banco` e `tests.apoio.rotas_teste` conferem com o anexo A, com `PYTHONDONTWRITEBYTECODE=1`.

| Sonda | Objetivo | Controle | Resultado |
| --- | --- | --- | --- |
| Sem banco | Fontes de Settings, padrões, metadata, OpenAPI, `.venv` × lock | Três formas de construção comparadas | §7.4 e §7.6 |
| Precedência | `DATABASE_URL` explícito × `.env` e variável de ambiente sintéticos | Valores sintéticos distintos | Explícito prevalece |
| Banco (container `b357253f19a8`, `sonda_auditoria`, guarda de host, porta e nome) | Logs com sentinelas; helper; CT-F1-15 com medição; `X-Request-ID` concorrente; `/saude/pronto` inalcançável | Divisão por zero e exceção genérica | §7.2 e §7.3. Container removido |
| Diagnóstico | Metadados do psycopg para a especificação da correção | — | §7.2 |
| Cópias A e B (`git ls-files -co`, sem `.env`) | Reproduzir a reescrita do documento; validar DEC-MV-26 e as correções propostas | RED (código atual) × GREEN (proposta) | RED: 3 falhas esperadas. GREEN: `29 passed`, Ruff e Pyright limpos. **Validação da especificação, não evidência do objeto** |
