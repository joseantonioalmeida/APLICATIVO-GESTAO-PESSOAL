# Análise do projeto e reconciliação normativa — API MinhaVida

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/analise_projeto_minhavida.md` |
| Fase | F0 — Arquitetura e reconciliação |
| Estado | PROPOSTO. DEC-MV-01 a 05, DEC-MV-25 (escopo limitado) e DEC-MV-26 **aprovadas** em 2026-10-11. DEC-MV-06, 07 e 08 **aprovadas** em 2026-10-13 (`indice.md` §4). DEC-MV-09 a 13 e DEC-MV-14 no escopo limitado da F3 **aprovadas** em 2026-10-13 (M16). DEC-MV-14 no restante e DEC-MV-15 a 24 pendentes |
| Data | 2026-10-09. Atualizado em 2026-10-11 (aprovações, escopo financeiro, §3.5, REC-MV-028 a 032, ACH-MV-ARQ-021 a 025, DEC-MV-24 e 25) e em 2026-10-13 (DEC-MV-06 a 08, §10.1 aplicado, REC-MV-033 e 034, ACH-MV-ARQ-001, 002, 006 e 018; depois, na preparação da F3: ACH-MV-ARQ-018 encerrado, ACH-MV-ARQ-026 a 038 e nota da §9; na liberação da F3 (M16): decisões da F3, RECs correspondentes, riscos 03 e 04 e ACH-MV-ARQ-015 e 026 a 038 encerrados) |
| Autor | Claude Opus 5.5 (arquitetura/auditoria) |

Legenda usada em todo o documento:

- **OBSERVADO:** fato verificado diretamente no repositório ou no ambiente nesta sessão.
- **EXIGIDO PELO CONTRATO:** regra presente em `CLAUDE.md` (diretrizes, requisitos das telas ou contrato de tabelas).
- **PROPOSTO:** decisão ou recomendação do Opus, que ainda depende de aprovação do usuário.
- **NÃO VERIFICADO:** informação não confirmada nesta sessão. Ela não deve ser tratada como fato.

---

## 1. Escopo e método

Esta análise foi feita em modo somente leitura. Comandos executados:

- `git rev-parse` e `git status`.
- Leitura integral do `CLAUDE.md`. O conteúdo carregado pelo harness corresponde ao arquivo em disco: 1.152 linhas.
- Leitura integral de `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md`.
- Leitura de `pyproject.toml`, `uv.lock` (versões resolvidas), `compose.yaml`, `.gitignore`, `.python-version` e de todo o código em `src/`.
- Leitura de `.env` com redação de valores. Só os nomes das chaves foram expostos.
- Inspeção das bibliotecas instaladas em `.venv`, para confirmar APIs.
- Execução de `docker --version`, `docker compose version`, `docker ps -a` e `docker volume ls`.
- Comparação textual do contrato de tabelas (`CLAUDE.md`, linhas 764–1152) com o Anexo A do prompt anterior.

Não houve instalação, migração, seed, teste, correção automática nem alteração de banco.

---

## 2. Inventário de fontes

| # | Caminho real | Finalidade | SHA-256 (conteúdo atual) | Estado de aprovação conhecido | Precedência |
| --- | --- | --- | --- | --- | --- |
| F-01 | `CLAUDE.md` | Diretrizes de comportamento e código, requisitos das telas 1–11 e contrato de tabelas | `565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473` | Arquivo do projeto, criado pelo usuário. Instruções vigentes | 1 (após instruções explícitas da sessão) |
| F-02 | `CLAUDE.md`, linhas 764–1152 | Contrato de tabelas (13 tabelas) | Trecho extraído: `fec67d03…26254e` (com linha final em branco) | Vigente como parte de F-01. Alteração de tipos de ID proposta em ADR-0002 | Parte de F-01 |
| F-03 | `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md` | Prompt anterior de implementação do banco | `2535a838ff3e3f579de349114ff69433f3a7e00cb3e033e41624901dd7693f41` | Não executado e não aprovado como arquitetura. **SUSPENSO** por esta análise (seção 6) | Nenhuma até a reconciliação |
| F-04 | `pyproject.toml` | Dependências diretas e configuração de Ruff, Pyright, pytest e taskipy | `b3bf08c5b0702b0c8189929ce7b52de36d357c943d6aece5c1d92331ab4bb779` | Configuração do usuário | Estado observado |
| F-05 | `uv.lock` | Versões resolvidas | `77f733b52de6ab0af9b20be2c33351ffd9dcc57c73de7010275bfcd0e1a1755f` | Gerado pelo uv | Estado observado |
| F-06 | `compose.yaml` | PostgreSQL de desenvolvimento | `f6bb783c8a360f10be6b26ab62d6d1012bca0bb925fbff86d61d45934c1b8ab8` | Configuração do usuário, modificada em 2026-10-09 | Estado observado |
| F-07 | `src/api_gestao_pessoal/**` | Código inicial | Hashes na seção 3.2 | Código do usuário | Estado observado |

### 2.1. Mapeamento dos anexos citados no prompt da sessão

| Anexo citado | SHA-256 informado | Equivalente real no repositório | Verificação |
| --- | --- | --- | --- |
| `Texto colado(20261009-000013).txt` (contrato original das tabelas) | `907f2509…eed830c` | O arquivo não está no repositório. O conteúdo equivalente está em `CLAUDE.md`, linhas 764–1152, e no Anexo A de F-03 | **NÃO VERIFICADO por hash.** Ver nota abaixo |
| `Texto colado (2)(6).txt` (diretrizes, telas e tabelas) | `7627ab94…7b97d` | Conteúdo equivalente a `CLAUDE.md` | **NÃO VERIFICADO por hash.** O hash de `CLAUDE.md` difere (`565dc6b2…`), então a identidade byte a byte não foi comprovada. As mesmas linhas truncadas por `>` estão presentes (linhas 3, 10 e 12) |

Sobre o contrato de tabelas:

- **OBSERVADO:** o trecho de tabelas do `CLAUDE.md` é idêntico ao Anexo A do prompt anterior. A única diferença é uma linha em branco no fim do `CLAUDE.md` (`diff` vazio após remover essa linha). O prompt anterior afirma que o Anexo A reproduz integralmente o anexo de hash `907f2509…`.
- **NÃO VERIFICADO:** essa afirmação. O anexo original não está disponível para cálculo.
- Conclusão: este trabalho usa `CLAUDE.md` como fonte real e vigente. Nenhuma divergência de conteúdo entre as duas cópias foi encontrada.

### 2.2. Fontes ausentes ou incompletas

| Item | Situação | Impacto | O que fica bloqueado |
| --- | --- | --- | --- |
| Anexos originais `Texto colado…` | Ausentes do repositório | Nenhum. O conteúdo equivalente está em `CLAUDE.md` | Nada |
| `CLAUDE.md`, linhas 3, 10 e 12 | Truncadas por `>` no próprio arquivo (OBSERVADO) | O sentido das regras é legível: ler integralmente, Zero Surpresas e Anti-Alucinação. O texto final não foi completado por suposição | Nada. Registrado como ACH-MV-ARQ-012 |
| ADRs e documentação de arquitetura anteriores | Inexistentes (OBSERVADO) | Este conjunto é o primeiro | Nada |
| `AGENTS.md` e instruções por diretório | Inexistentes (OBSERVADO) | Nenhum | Nada |
| Requisitos da área “Perfil” | Ausentes em `CLAUDE.md` (apenas citada na navegação) | Não há CRUD de perfil a implementar | Ver DEC-MV-13 |

---

## 3. Baseline do repositório

### 3.1. Git e ambiente (OBSERVADO)

| Item | Valor |
| --- | --- |
| Raiz | `/home/jose/projects/app_gestão_pessoal/API` |
| Branch | `main`, **sem nenhum commit** (`git rev-parse HEAD` falha: “unknown revision”) |
| Remote | Nenhum configurado (`git remote -v` vazio) |
| Arquivos | Todos não rastreados: `.gitignore`, `.python-version`, `CLAUDE.md`, `PROMPTS/`, `README.md` (vazio), `compose.yaml`, `pyproject.toml`, `src/`, `uv.lock` |
| `.env` | Contém apenas a chave `DATABASE_URL`, com **valor vazio** (`""`) |
| Python no `.venv` | 3.14.6. `.python-version` = 3.14 |
| uv | 0.11.29 |
| Docker | 29.7.2. Compose v5.3.1 |
| Containers e volumes do projeto | Nenhum container existe. Não há volume com o nome do projeto, então não há banco de desenvolvimento com dados |
| Projeto instalado | Editável no `.venv` (`__editable__.api-0.1.0.pth` → `src`) |
| Diretório irmão `../MOBILE` | Vazio. Fora do escopo |

> **Consequência para auditoria (ACH-MV-ARQ-019, P2):** sem commit, o objeto auditado não pode ser identificado por SHA nem por `git diff`. Pelo tratamento de P2 (`plano_validacao_auditoria.md` §7), o achado **bloqueia a fase** até a correção ou uma decisão explícita do usuário. Alcance do bloqueio (REC-MV-031):
>
> - A Etapa A da F1 é somente leitura e pode ocorrer sem o commit. Ela registra o resultado de `git rev-parse HEAD`.
> - A **Etapa B** da F1 (implementação) só começa com um commit de baseline do usuário ou com a exceção aceita explicitamente por ele (estado `ACEITO_COMO_EXCECAO`, com o risco registrado no índice §4). Depois que a implementação altera arquivos, não é mais possível criar esse baseline.
> - Recomendado: fazer o commit antes de enviar o Prompt F1 ao Sonnet, para que a Etapa A já registre o SHA.
> - Se a Etapa A ocorrer antes do commit, o Sonnet registra o SHA e faz a **revalidação do baseline** (Prompt F1 §1.2) no início da Etapa B, antes de alterar qualquer arquivo. A revalidação confere o conteúdo do commit e os hashes, sem refazer a análise.
> - Um commit vazio, parcial ou com outros arquivos não atende ao achado. O conteúdo exigido e as exclusões estão em §3.5.
>
> Enquanto não houver commit, os hashes registrados em §3.2 e no Prompt F1 §1 servem de referência.

### 3.2. Código existente (OBSERVADO)

| Arquivo | SHA-256 | Conteúdo relevante |
| --- | --- | --- |
| `src/api_gestao_pessoal/main.py` | `2fd86f1d…3311` | `app = FastAPI()`. Rota síncrona `GET /` que retorna `{"Message": "Olá, Mundo!"}` |
| `src/api_gestao_pessoal/settings.py` | `2824d057…4a58` | `Settings(BaseSettings)` com `DATABASE_URL: str`, `env_file=".env"`, `hide_input_in_errors=True`. **`settings = Settings()` instanciado na importação** |
| `src/api_gestao_pessoal/database.py` | `1df53423…b2c9` | **`engine = create_async_engine(settings.DATABASE_URL, hide_parameters=True)` na importação**. `async_session_factory` com `autocommit=False`, `autoflush=False`, `expire_on_commit=False`. `get_session()` faz `yield` da sessão sem commit nem rollback explícitos |
| `src/api_gestao_pessoal/models/base.py` | `ccd6fc1c…bc31` | `Base(DeclarativeBase)` sem convenção de nomes. `TimestampMixin` com `created_at` e `updated_at` |
| `src/api_gestao_pessoal/models/usuario.py` | vazio (`e3b0c442…`) | — |
| `src/api_gestao_pessoal/schemas/message.py` | `fc4d4b2f…f270` | `Message(BaseModel)` com campo `Message: str` (PascalCase) |
| `src/api_gestao_pessoal/routers/` | diretório vazio | — |

Também foi **OBSERVADO** que não existem:

- `__init__.py` nos pacotes.
- `ErroNegocio` ou qualquer mecanismo de erro.
- Alembic (`alembic.ini`, diretório e revisões).
- O diretório `tests/`.
- CI.
- Documentação.

### 3.3. Configuração de ferramentas (OBSERVADO em `pyproject.toml`)

- `requires-python = ">=3.12"`. Porém Ruff usa `target-version = "py314"` e Pyright usa `pythonVersion = "3.14"`.
- Ruff: `fix = true` no nível `[tool.ruff]`, então **`ruff check .` aplica correções**. Regras: `I, F, E, W, PL, PT, FAST`, com `preview = true`. O diretório `alembic` está excluído do Ruff.
- Pyright: `typeCheckingMode = "standard"` e `include = ["src", "tests"]` (`tests/` ainda não existe). Há comentários sobre `factory_boy`, que não é dependência, indicando resíduo de modelo de outro projeto.
- pytest: `addopts = "-s --color=yes --tb=short -m 'not performance'"`, marcador `performance`, `asyncio_mode = "auto"` e `asyncio_default_fixture_loop_scope = "function"`.
- taskipy: `test = "pytest -x -s --cov=api_gestao_pessoal -vv"`, com `pre_test = "task lint"` (`ruff check . --fix`) e `post_test = "coverage html"`. Ou seja, **executa a suíte completa e altera arquivos**.
- Coverage: omite `alembic/*`.

### 3.4. Stack: versão encontrada × alvo × incompatibilidades

| Componente | Encontrado (uv.lock / ambiente) | Alvo proposto | Observação |
| --- | --- | --- | --- |
| Python | 3.14.6 (`.venv`). `requires-python >=3.12` | **3.14** (`requires-python = ">=3.14"`) | Necessário para `uuid.uuid7()` da biblioteca padrão (ADR-0002). Ver ACH-MV-ARQ-010 |
| FastAPI | 0.143.0 (`fastapi[standard]`) | Mantido | Suporta `Depends(..., scope="function")`, verificado em `fastapi/param_functions.py` |
| Starlette | 1.7.0 | Mantido | — |
| Pydantic | 2.13.5. pydantic-settings 2.15.0 (transitivo) | Mantido. `pydantic-settings` passa a dependência direta | `settings.py` importa `pydantic_settings` diretamente |
| SQLAlchemy | **2.1.4** (`pyproject`: `>=2.0.52`) | Mantido (2.1.x) | APIs verificadas: `Uuid`, `Enum(length=…)`, `JSON(none_as_null=…)`, `postgresql.insert().on_conflict_do_nothing`, `Mapper.eager_defaults`. `autocommit=False` ainda é aceito como `Literal[False]` |
| Alembic | 1.20.0 | Mantido | Template async e `run_sync` |
| Driver PostgreSQL | psycopg 3.3.6 (binary), que suporta async | **psycopg 3**, URL `postgresql+psycopg://` | Não adicionar `asyncpg` (REC-MV-003) |
| PostgreSQL | Imagem `postgres:15-alpine` (compose). Versão exata do patch: **NÃO VERIFICADO** (imagem ainda não baixada) | **15** (mantido, DEC-MV-23). Testes com a mesma imagem | O PG 15 não tem `uuidv7()` nativo, então a geração é feita na aplicação |
| pytest | 9.1.1. pytest-asyncio 1.4.0. pytest-xdist 3.8.0. pytest-cov 7.1.0 | Mantidos | — |
| Testcontainers | 4.15.0. O módulo vigente é `testcontainers.community.postgres` (`testcontainers.postgres` está deprecado) | Mantido | O `driver` padrão do container é `psycopg2`, então é preciso passar `driver="psycopg"` |
| httpx | 0.28.1 (transitivo) | Passa a dependência dev direta | Cliente ASGI dos testes. `raise_app_exceptions` disponível |
| Ruff / Pyright | 0.16.10 / 1.1.414 | Mantidos | — |
| Hash de senha | Ausente | `argon2-cffi` (F3, DEC-MV-09) | Nova dependência a aprovar |
| JWT | Ausente | `PyJWT` (F3, DEC-MV-09) | Nova dependência a aprovar |
| tzdata | 2026.5 (transitivo) | Passa a dependência direta na F3 | Garante a base IANA independentemente do sistema |

Nenhuma dependência é atualizada nesta sessão. Versões novas entram pelo `uv add` da fase correspondente e ficam fixadas em `uv.lock`.

### 3.5. Commit de baseline: conteúdo, exclusões e verificação (ACH-MV-ARQ-019, REC-MV-032)

Estado observado em 2026-10-11, somente com leitura (`git status --ignored`, `git ls-files --stage`, `git check-ignore -v` e uma varredura de credenciais que não exibiu valores):

| Item | Resultado |
| --- | --- |
| Commits | Nenhum. `main` sem histórico |
| Preparado para commit (índice) | Nada. `git ls-files --stage` sem entradas |
| Ignorados | `.env` (regra 1 do `.gitignore`) e `.venv/` (regra `*` em `.venv/.gitignore`, criada pelo uv) |
| Não ignorados que **não** devem entrar | `compose.yaml`: valores literais em `POSTGRES_USER` e `POSTGRES_PASSWORD` (ACH-MV-ARQ-006). `src/api_gestao_pessoal/__pycache__/main.cpython-314.pyc`: artefato de compilação |
| Demais arquivos candidatos | Nenhuma credencial real. As ocorrências nos documentos e no Prompt F1 são placeholders (`USUARIO:SENHA`), valores fictícios de teste ou pseudocódigo |
| Dado pessoal não secreto | §3.1 registra o caminho local, que contém o nome do usuário do sistema. Não é credencial |
| Identidade do Git | `user.name` e `user.email` definidos. Eles ficarão gravados no commit |

**Conteúdo exigido do baseline: exatamente estes 22 arquivos.**

```text
.gitignore
.python-version
CLAUDE.md
README.md
pyproject.toml
uv.lock
src/api_gestao_pessoal/main.py
src/api_gestao_pessoal/settings.py
src/api_gestao_pessoal/database.py
src/api_gestao_pessoal/models/base.py
src/api_gestao_pessoal/models/usuario.py
src/api_gestao_pessoal/schemas/message.py
docs/adr/0001_arquitetura_api_minhavida.md
docs/adr/0002_identificadores_uuid.md
docs/arquitetura/analise_projeto_minhavida.md
docs/arquitetura/arquitetura_api_minhavida.md
docs/arquitetura/indice.md
docs/arquitetura/matriz_requisitos_api.md
docs/arquitetura/plano_fases_api.md
docs/arquitetura/plano_validacao_auditoria.md
PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md
PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md
```

Ficam fora: `.env` e `.venv/` (ignorados), `compose.yaml` (credenciais) e `__pycache__/`. O diretório vazio `routers/` não é rastreado pelo Git. A F1 cria `routers/__init__.py`.

**Tratamento do `compose.yaml` (recomendado):**

- Fica **fora** do commit de baseline e continua não rastreado no diretório de trabalho. Nenhum ajuste de configuração é feito antes da F1.
- O estado de partida continua verificável: o hash `f6bb783c…` está registrado em §2 (F-06) e no Prompt F1 §1, e esses documentos entram no commit.
- Quem ajusta é o Sonnet, na Etapa B da F1. O ajuste é o já aprovado em DEC-MV-05 (REC-MV-024, ACH-MV-ARQ-006): reescrever o arquivo com o conteúdo exato do Prompt F1 §9.3 (credenciais lidas do `.env` e porta em `127.0.0.1`).
- O arquivo entra no histórico só na integração da F1 (G6), já sem credenciais. A auditoria compara o arquivo com o bloco de §9.3 e confere `grep POSTGRES_PASSWORD`.
- Hashes de referência: **não mudam**. O de partida continua `f6bb783c…`. O de chegada é o do conteúdo de §9.3: o relatório da F1 o informa e o Opus o confere.
- Até a F1, não use `git add -A` nem `git add .`, porque o `compose.yaml` seria incluído. Depois da F1, preencha no `.env` `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` e `DATABASE_URL` (Prompt F1 §9.3). Usar valores novos é recomendável, porque os atuais ficaram em texto no diretório de trabalho, mas não é obrigatório.

Alternativa não recomendada: o usuário aplicar à mão o conteúdo de §9.3 antes do baseline. Isso transfere ao usuário um item da F1 atribuído ao Sonnet por DEC-MV-05. Também exige que o Opus atualize o hash de partida do `compose.yaml` (aqui e no Prompt F1 §1) depois do ajuste, e que o item de §7.1 do prompt passe de “reescrever” para “conferir”.

**Comandos para o usuário, a revisar antes de executar** (adição explícita, sem `-A`):

```bash
cd /home/jose/projects/app_gestão_pessoal/API
git config user.name && git config user.email   # identidade gravada no commit
git add -- .gitignore .python-version CLAUDE.md README.md pyproject.toml uv.lock \
  src/api_gestao_pessoal/main.py src/api_gestao_pessoal/settings.py \
  src/api_gestao_pessoal/database.py src/api_gestao_pessoal/models/base.py \
  src/api_gestao_pessoal/models/usuario.py src/api_gestao_pessoal/schemas/message.py \
  docs/adr/0001_arquitetura_api_minhavida.md docs/adr/0002_identificadores_uuid.md \
  docs/arquitetura/analise_projeto_minhavida.md docs/arquitetura/arquitetura_api_minhavida.md \
  docs/arquitetura/indice.md docs/arquitetura/matriz_requisitos_api.md \
  docs/arquitetura/plano_fases_api.md docs/arquitetura/plano_validacao_auditoria.md \
  PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md \
  PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md
git ls-files | wc -l                                         # esperado: 22
git ls-files | grep -E 'compose\.yaml|(^|/)\.env|__pycache__' || echo "ok: nada indevido preparado"
git commit -m "Baseline da F0: código inicial e documentação de arquitetura"
git rev-parse HEAD                                           # SHA do baseline
git ls-tree -r --name-only HEAD | wc -l                      # esperado: 22
git status --short   # esperado: somente ?? compose.yaml e ?? src/api_gestao_pessoal/__pycache__/
```

Se a contagem não for 22 ou se a verificação apontar algum arquivo, não faça o commit. Desfaça a preparação com `git rm --cached -- <arquivo>`, que não apaga o arquivo do disco.

O achado só é encerrado depois da verificação: revalidação do baseline pelo Sonnet (Prompt F1 §1.2) e conferência do Opus na auditoria da F1.

---

## 4. Matriz de reconciliação normativa

Os identificadores `REC-MV-NNN` são estáveis. Uma divergência resolvida permanece registrada, com a evidência de resolução preenchida.

| ID | Fontes e trechos | Divergência | Impacto | Decisão/recomendação do Opus | Aprovação necessária | Fases bloqueadas | Evidência de resolução |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REC-MV-001 | `CLAUDE.md` (tabelas): “Todos os campos `id` serão inteiros, chaves primárias e gerados automaticamente” e linhas `INT` de cada tabela. Diretriz atual do usuário: “UUID para identificadores principais” | Tipo das PKs e FKs | 32 das 134 colunas, migração inicial, schemas HTTP e seeds | ADR-0002: UUIDv7 gerado pela aplicação (`uuid.uuid7()`) nas 13 PKs e nas 19 FKs. Tipo PostgreSQL `uuid`. Diff proposto do contrato no ADR-0002 §6 | Sim (DEC-MV-06) e atualização do `CLAUDE.md` | F2 e seguintes | Aprovada em 2026-10-13 (DEC-MV-06). `CLAUDE.md` atualizado na mesma data (§10.1). Implementação e prova na F2 (CT-F2-02 a 05) |
| REC-MV-002 | Prompt anterior §6: “Defina claramente quem inicia, confirma e desfaz transações”, deixando a escolha ao implementador. Diretriz atual: service faz `flush`, nunca `commit`, e o router define a fronteira | Escolha transacional aberta × contrato fechado | Todas as fases com escrita | ADR-0001 D-04: sessão por requisição com autobegin. Só o router chama `commit()`. Jobs têm ponto de entrada próprio | Sim (DEC-MV-02) | F1 | Aprovada em 2026-10-11 (DEC-MV-02). Implementação na F1 |
| REC-MV-003 | Prompt anterior §2.4 (“Não presuma FastAPI”) e §6 (“utilize `asyncpg`” na ausência de driver async). Stack atual explícita: FastAPI async, psycopg já instalado | Stack inferida × explícita | Driver e organização | Stack fixada: FastAPI, Pydantic v2, SQLAlchemy 2.1 Async, Alembic async, PostgreSQL, pytest, Testcontainers, uv, Ruff e Pyright. Driver **psycopg 3** (já adotado e com suporte async). `asyncpg` não é introduzido | Sim (DEC-MV-01) | F1 | Aprovada em 2026-10-11 (DEC-MV-01). Implementação na F1 |
| REC-MV-004 | Prompt anterior §10 (“Execute também a suíte de testes apropriada”). taskipy `test` executa a suíte completa com `--fix`. Política atual: testes direcionados, suíte completa como exceção | Gatilhos implícitos de suíte completa | Custo e tempo dos gates | Política do `plano_validacao_auditoria.md` §2. `task test` proibido em gates. Comandos pytest sempre com seleção explícita | Sim (DEC-MV-04) | F1 | Aprovada em 2026-10-11 (DEC-MV-04). Aplicada no Prompt F1 §5 e §14 |
| REC-MV-005 | `CLAUDE.md` §1: “Zero Commits: Nunca execute `git commit` por conta própria”. Workflow atual: exceção Cloud (commit, push e PR draft somente na branch da sessão) | Exceção não prevista no `CLAUDE.md` | Modo Cloud | No modo LOCAL a proibição continua integral. A exceção Cloud só se aplica a sessões identificadas explicitamente como Cloud e com autorização de implementação. Proposta de diff no `CLAUDE.md` na seção 10 | Sim (DEC-MV-22) | Nenhuma no modo LOCAL. Execução Cloud depende da aprovação | Pendente |
| REC-MV-006 | `CLAUDE.md` §2: `uv run ruff check --fix .` e `uv run ruff format .`. Prompt da sessão: auditoria com `uv run ruff check .`. `pyproject`: `fix = true` | Os comandos alteram arquivos. Com `fix = true`, até `ruff check .` corrige | Integridade do objeto auditado | Implementador: comandos do `CLAUDE.md`, dentro do escopo autorizado. Verificação e auditoria: `uv run ruff check --no-fix .`, `uv run ruff format --check .` e `uv run pyright` | Sim (DEC-MV-04 e DEC-MV-22) | F1 (gates) | Documentado em `plano_validacao_auditoria.md` §5. DEC-MV-04 aprovada em 2026-10-11 (verificação e auditoria). A alteração do `CLAUDE.md` depende de DEC-MV-22 |
| REC-MV-007 | Tela 3, 3.4.2: “Não foi possível encontrar seu email”. Boa prática de segurança: resposta genérica contra enumeração de contas | A mensagem revela se o e-mail está cadastrado | Privacidade | Manter 3.4.2, porque o registro (e-mail único) já revela a existência da conta. Mitigar com intervalo mínimo de reenvio, limite de tentativas e futura limitação na borda | Sim (DEC-MV-10) | F3 | Aprovada em 2026-10-13 (DEC-MV-10, opção A), com o risco aceito sem prazo enquanto valer 3.4.2. A justificativa desta linha é histórica: a revelação no cadastro não torna inofensivo um segundo canal, e intervalo, tentativas ou limitação na borda não reduzem a divulgação (dossiê da F3 §4.2) |
| REC-MV-008 | `models/base.py` `TimestampMixin` (`created_at`/`updated_at` em todas as tabelas). Contrato: `criado_em`/`atualizado_em` em 8 tabelas, `notificacao.criada_em`, catálogos sem timestamps, `requisicao_idempotente` sem `atualizado_em` | Nomes e alcance | Fidelidade do esquema | **SUBSTITUIR** na F2 por mixin `CriadoAtualizadoMixin` aplicado só às 8 tabelas com as duas colunas. Demais colunas declaradas explicitamente | Sim (DEC-MV-07) | F2 | Aprovada em 2026-10-13 (DEC-MV-07): `CriadoAtualizadoMixin` substitui o `TimestampMixin` na F2 (arquitetura §10.1 e §10.3.1) |
| REC-MV-009 | `database.py`/`settings.py`: engine e settings criados na importação, com `DATABASE_URL` vazio. Prompt anterior §6: “Não crie engines e conexões como efeito colateral de importar” | Efeito colateral de importação | Importar o app ou os modelos falha sem ambiente. Alembic e testes acoplados | F1: `obter_settings()` com cache, engine criada no `lifespan` e fábrica de sessões em `app.state` | Sim (DEC-MV-02) | F1 | Aprovada em 2026-10-11 (DEC-MV-02). Implementação na F1 |
| REC-MV-010 | `requires-python >=3.12` × `.python-version` 3.14, Ruff `py314` e Pyright 3.14 | Versão mínima inconsistente | `uuid.uuid7()` exige 3.14 | `requires-python = ">=3.14"` na F1 | Sim (DEC-MV-05) | F1 | Aprovada em 2026-10-11 (DEC-MV-05). Implementação na F1 |
| REC-MV-011 | Tabela 2 (`recuperacao_senha`): “Proposta operacional: validade total de dez minutos e até cinco tentativas… limitação adicional de reenvios” | Valores marcados como proposta, não aprovados | Fluxo de recuperação | Adotar 10 min, 5 tentativas inválidas por emissão e intervalo mínimo de 60 s entre emissões (calculado por `expira_em − 10 min`, sem coluna nova) | Sim (DEC-MV-11) | F3 | Aprovada em 2026-10-13 (DEC-MV-11, R11.1 a R11.10). Implementação na F3 |
| REC-MV-012 | 7.2.1/7.2.4 (Todos e Próximos incluem futuros de “qualquer data”) e 7.2.7 (quantidades do resultado completo) × séries sem data final | Uma série sem fim gera infinitas ocorrências futuras | Contagem e listagem impossíveis | Horizonte de listagem de ocorrências de **série** em Todos e Próximos: até o último dia do 12º mês após o mês atual. Registros avulsos sem horizonte | Sim (DEC-MV-18) | F7 | Pendente |
| REC-MV-013 | Tabela 11: `situacao` ∈ {PENDENTE, ENVIADO, CANCELADO}. 8.3.4/8.5.8: o usuário pode desativar o lembrete na edição. 7.3.4/7.3.7: a reabertura reativa lembretes futuros | Não há como distinguir “desativado pelo usuário” de “cancelado por conclusão” quando a linha já tem notificações (FK impede apagar) | A reabertura reativaria um lembrete desligado pelo usuário | Acrescentar o valor `DESATIVADO` (10 caracteres, cabe em `VARCHAR(10)`) ao domínio, com `enviado_em` nulo. Migração aditiva na F7 | Sim (DEC-MV-19) | F7 | Pendente |
| REC-MV-014 | Tabela 5: CHECK de nome 3–100 só em `atividade`. Telas 8.1.1, 10.1.1 e 11.1.1 exigem 3–100 para importância, receita e despesa | CHECK parcial | A integridade dos outros nomes depende só da aplicação | Recomendação: CHECKs equivalentes em `importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao`. Sem aprovação, a F2 segue o contrato literal | Sim (DEC-MV-08) | F2 (conteúdo) | Aprovada em 2026-10-13 (DEC-MV-08): quatro CHECKs, registrados no `CLAUDE.md` e na arquitetura §10.4. Prova na F2 (CT-F2-20) |
| REC-MV-015 | Prompt anterior §10: “Se não houver PostgreSQL disponível, prepare… e indique que a verificação não foi executada”. Política atual: PostgreSQL real via Testcontainers obrigatório | Entrega parcial sem banco | Prova de integridade | Sem Docker/Testcontainers a fase fica **BLOQUEADA**, não “parcial”. Docker está disponível (OBSERVADO) | Sim (DEC-MV-04) | F1+ | Aprovada em 2026-10-11 (DEC-MV-04). Aplicada no Prompt F1 §5 e §12 |
| REC-MV-016 | Prompt anterior §2 (“Resolva escolhas técnicas rotineiras… explique as escolhas”). Workflow atual: o Sonnet não toma decisões arquiteturais | O implementador decide × o arquiteto decide | Risco de desvio | Prompts Master trazem decisões fechadas. Lacuna arquitetural volta ao Opus | Não (regra do workflow do usuário) | — | Refletido no Prompt Master F1 §0 |
| REC-MV-017 | Ausência de requisitos de sessão, logout e revogação. Tabela 1 sem coluna de versão de credencial. Prompt anterior proíbe tabelas de sessão ou token | Revogação após redefinição de senha | Um token roubado continuaria válido após a troca de senha | JWT HS256 com claim `sv` derivado de `senha_hash`: tokens anteriores à troca de senha perdem validade sem tabela nova. Logout apenas no cliente | Sim (DEC-MV-09) | F3 | Aprovada em 2026-10-13 (DEC-MV-09). Implementação na F3 |
| REC-MV-018 | Não há requisito de limitação de tentativas de login. Não há Redis nem coluna para isso | Força bruta de senha | Segurança em produção | Não implementar limitador em memória (falsa garantia entre processos). Limitação na borda (proxy) antes da exposição pública. Até lá, aceitar o risco | Sim (DEC-MV-21) | Exposição em produção (F11) | Pendente |
| REC-MV-019 | 3.4.9: “no mínimo 8 caracteres alfanuméricos e especiais”, com mensagem que apenas *sugere* composição. 3.4.10: “não atende os requisitos necessários de 8 caracteres” | Composição obrigatória ou sugerida? | Validação de senha | Exigir apenas o mínimo de 8 e o máximo de 128 caracteres (o máximo limita custo de hash). A composição é recomendada, não exigida. A mesma política vale no registro (tela 2) | Sim (DEC-MV-11) | F3 | Aprovada em 2026-10-13 (DEC-MV-11, R11.10). Implementação na F3 |
| REC-MV-020 | Tabela 1: `fuso_horario` obrigatório, “obtido do dispositivo”. Tela 2 não lista esse campo | Campo técnico ausente da tela | Contrato do registro | O registro exige `fuso_horario` (IANA) no corpo, enviado pelo app sem exibição ao usuário | Incluída em DEC-MV-09 | F3 | Aprovada em 2026-10-13 (DEC-MV-09, R9.7). Implementação na F3 |
| REC-MV-021 | 5.1.7 “Mais recentes = momento do cadastro”. Ocorrências de série são materializadas sob demanda, com `atividade.criado_em` igual ao momento da materialização | O momento da materialização não é o do cadastro | Ordenação dependeria do histórico de navegação | Momento do cadastro = `serie_atividade.criado_em` para ocorrências de série e `atividade.criado_em` para avulsas | Sim (DEC-MV-16) | F5 | Pendente |
| REC-MV-022 | 8.5.5 (sem notificação retroativa no cadastro) × processamento atrasado (worker parado) | Lembrete vencido durante indisponibilidade | Comportamento após falha | Processar lembretes vencidos enquanto a data do compromisso não passou. Se o compromisso já passou, marcar `CANCELADO` sem notificação | Sim (DEC-MV-20) | F9 | Pendente |
| REC-MV-023 | 9.2.3 (centavos exatos) × JSON number (ponto flutuante nos clientes) | Representação de dinheiro na API | Precisão | Valores monetários trafegam como **string** decimal (`"1234.56"`). Número JSON é rejeitado | Sim (DEC-MV-17) | F6 e F7 | Pendente |
| REC-MV-024 | `compose.yaml`: usuário e senha do banco em texto e porta `5432` publicada em todas as interfaces | Segredo de desenvolvimento versionável e banco exposto na rede local | Risco local | Interpolar do `.env` e publicar em `127.0.0.1` (F1) | Sim (DEC-MV-05) | F1 | Aprovada em 2026-10-11 (DEC-MV-05). Implementação na F1 |
| REC-MV-025 | `CLAUDE.md` linha 3 do 3.3 (“3.1.1 - CAMPOS OBRIGATÓRIOS” dentro de 3.3) | Numeração repetida | Rastreabilidade | Tratado como `3.3.1` na matriz, sem alterar o requisito | Não | — | Matriz usa `3.3.1*` |
| REC-MV-026 | `CLAUDE.md` 4.1.6 e 4.1.10 (botão “+”, navegação) | Comportamento puramente visual | — | `NÃO SE APLICA AO BACKEND` na matriz | Não | — | Matriz |
| REC-MV-027 | Tabela 7/8 (importância com lembrete) × materialização sob demanda | Ocorrências de série nunca consultadas não teriam lembrete criado | Lembretes de séries não disparariam | O processador de lembretes materializa antecipadamente as ocorrências de séries com lembrete (janela de 8 dias) | Incluída em DEC-MV-20 | F9 | Pendente |
| REC-MV-028 | Instrução do usuário de 2026-10-11 (escopo financeiro). `CLAUDE.md` 8.5.3, 9.2.1–9.2.3, 10.2.3, 10.4.3, 11.2.3 e 11.4.3. `plano_fases_api.md` (F8 “Integração de pagamentos”) | Nenhuma divergência de conteúdo: integrações financeiras externas **nunca estiveram previstas** nos documentos da F0. O nome “Integração de pagamentos” da F8 podia sugerir integração externa | Escopo e nomenclatura | Escopo consolidado em `arquitetura_api_minhavida.md` §1.1. F8 renomeada para “Vínculo interno entre despesas e importâncias”, com o mesmo identificador. CT-F6-14 com o exemplo do usuário. Verificação de escopo na auditoria (`plano_validacao_auditoria.md` §9) | Não. Instrução explícita do usuário | — | Aplicado em 2026-10-11: arquitetura §1.1 e §8.7, ADR-0001 §2, plano de fases, plano de validação, matriz e Prompt F1 §4 |
| REC-MV-029 | ADR-0001 D-02: importações entre services “apenas para módulos de suporte (`recorrencia`, `idempotencia`, `trava`, `situacao`)”. Arquitetura §2.2: suporte = `trava`, `idempotencia`, `paginacao`, `recorrencia`, `situacao_importancia`, `lembretes` e `autorizacao`, mais as importações de domínio `pagamentos → financeiro, importancias`, `painel → atividades, resumo_financeiro, importancias, notificacoes` e `processamento_lembretes → importancias`. **Os dois textos foram aprovados por DEC-MV-01** | D-02 é mais restritiva: omite `paginacao`, `lembretes` e `autorizacao`, cita `situacao.py` (o arquivo previsto é `situacao_importancia.py`) e proíbe os orquestradores de §2.2 | Os algoritmos de §8.6.3, §8.7, §8.8 (exclusão vinculada) e §8.10 dependem das importações de §2.2. Primeira fase afetada: F5 (`atividades` importa `autorizacao` e `paginacao`). F1 a F4 não têm importação entre services que viole qualquer das duas regras | Recomendação: D-02 passa a remeter à matriz de §2.2 como regra exaustiva (DEC-MV-24). Até a decisão, vale D-02, por precedência (ADR aceito prevalece sobre a arquitetura, `indice.md` §3) | Sim (DEC-MV-24) | F5 em diante (G1 da F5) | Pendente. Conflito anotado em ADR-0001 D-02 e na arquitetura §2.2, sem alterar as regras |
| REC-MV-030 | ADR-0001 D-09 (“Fases afetadas: F1 (Alembic), F2”) e §5 (“F1: … e o Alembic de D-09”). `plano_fases_api.md`, F1 (gate “G1 para … o Alembic de D-09”; esquema “`MetaData` com convenção de nomes”). Arquitetura §2.1, aprovada por DEC-MV-01 (“`base.py` … F1: naming convention”). §9: DEC-MV-07, que inclui a convenção de nomes, bloqueava só a F2. Prompt F1: bloqueios restritos a DEC-MV-01 a 05 | O mapeamento de gates omitia que a F1 implementa um item de D-09, cuja aprovação (DEC-MV-07) está pendente | O Prompt F1 seria liberado com conteúdo não aprovado (convenção de nomes, arquitetura §10.1) | Análise por item: (a) o **ambiente Alembic sem revisões** está coberto por decisões aprovadas: stack com Alembic async (REC-MV-003, DEC-MV-01), árvore e regra de importação do `env.py` (arquitetura §2, DEC-MV-01), engine própria do Alembic (D-03) e fixture síncrona com CT-F1-17 a 19 (D-14 e plano de validação, DEC-MV-04); (b) a **convenção de nomes** tem lugar aprovado (§2.1), mas o conteúdo está pendente (§10.1, D-09). Recomendação: aprovar esse item antecipadamente (DEC-MV-25). Alternativa: adiá-lo para a F2, o que exige alterar a anotação aprovada de §2.1 e o Prompt F1 | Sim (DEC-MV-25) | **F1** (G2) | **Resolvido em 2026-10-11:** DEC-MV-25 aprovada com escopo limitado (`indice.md` §4). Mapeamentos corrigidos em ADR-0001 (tabela e §5), plano de fases (F1) e Prompt F1 (cabeçalho, §2, §3 e §6) |
| REC-MV-031 | ACH-MV-ARQ-019 classificado como P2 (§7). `plano_validacao_auditoria.md` §7: P2 “bloqueia a fase até correção ou decisão explícita do usuário”. Prompt F1: “Recomendado, mas não bloqueante”. `indice.md` §7: “Opcional e recomendado”. `plano_fases_api.md`, F1: “recomendado” | A severidade P2 era apresentada como opcional | A F1 poderia começar sem base Git verificável, contrariando o tratamento de P2 | Severidade mantida em P2. Alcance do bloqueio definido em §3.1: a Etapa A (somente leitura) pode ocorrer; a Etapa B exige commit de baseline do usuário ou exceção aceita explicitamente por ele | Não para a correção, que aplica o critério de P2 já usado na classificação. Uma exceção, se desejada, é decisão do usuário | F1 (Etapa B) | Corrigido em 2026-10-11: §3.1, §7, índice, plano de fases, plano de validação §6 e Prompt F1. Conteúdo do baseline e revalidação: §3.5 e Prompt F1 §1.1 e §1.2 (REC-MV-032). O achado continua ABERTO |
| REC-MV-032 | Instrução do usuário (2026-10-11): baseline verificável **sem** credenciais no histórico. `indice.md` §7 (versão anterior): `git add -A` excluindo só caches. ACH-MV-ARQ-006 (credenciais literais no `compose.yaml`). DEC-MV-05 e REC-MV-024 (o ajuste do `compose.yaml` é tarefa do Sonnet na F1) | A orientação anterior gravaria as credenciais do `compose.yaml` no primeiro commit | Credenciais de desenvolvimento no histórico do Git | Baseline com lista explícita de 22 arquivos. `compose.yaml` fora do baseline até ser reescrito na F1 conforme DEC-MV-05. Hashes de referência mantidos. Revalidação do baseline no início da Etapa B quando a Etapa A ocorrer antes do commit (§3.5, Prompt F1 §1.1 e §1.2) | Não. Aplica a instrução do usuário e a DEC-MV-05 já aprovada | F1 (Etapa B) | Orientação corrigida em 2026-10-11. O efeito será verificado na revalidação e na auditoria da F1 |
| REC-MV-033 | Arquitetura §10.3: “O ORM espelha os mesmos padrões em `default=` quando útil”. ADR-0001 D-09: timestamps e `eager_defaults` | Critério aberto (“quando útil”) para repetir no ORM os padrões do banco | Duas fontes de padrão podem divergir, e o Prompt F2 não pode deixar a escolha ao implementador | Sem `default=` no ORM, exceto `id` (`uuid.uuid7`). O banco aplica os padrões, e o `eager_defaults` devolve os valores por `RETURNING` | Não. Precisa o texto de DEC-MV-07, já aprovada, sem mudar o esquema | F2 | Aplicado em 2026-10-13: arquitetura §10.3 e Prompt F2 |
| REC-MV-034 | Plano de validação §3.4 (aceito por DEC-MV-04): `limpar_dados()` com “`TRUNCATE` … `RESTART IDENTITY CASCADE` restrito à lista explícita”; modo “Esquema de domínio (F2+)” com limpeza por teste. ADR-0002 (DEC-MV-06): não há colunas de identidade | `RESTART IDENTITY` perde o objeto com UUID. `CASCADE` truncaria em silêncio uma tabela referenciadora ausente da lista | Limpeza de teste que apaga além do previsto, sem falha visível | `TRUNCATE` único com a lista explícita das 10 tabelas que não são catálogo, **sem** `RESTART IDENTITY` e **sem** `CASCADE`: uma lista incompleta falha, em vez de apagar outra tabela. Os testes de restrição da F2 revertem a transação ao fim de cada teste, com `SAVEPOINT` por violação esperada. Só os testes que confirmam transações usam `limpar_dados()` | Não. Decorre de DEC-MV-06 e reforça a guarda de DEC-MV-04, sem afrouxá-la | F2 | Aplicado em 2026-10-13: plano de validação §3.4 e Prompt F2 |

---

## 5. Auditoria do contrato de dados (13 tabelas)

A contagem foi refeita a partir de `CLAUDE.md` e confere com o baseline: **13 tabelas, 134 colunas, 8 índices iniciais e 30 categorias** (6 + 8 + 6 + 10).

| Tabela | Colunas | IDs afetados pelo UUID (PK + FKs) |
| --- | ---: | ---: |
| `usuario` | 8 | 1 |
| `recuperacao_senha` | 10 | 2 |
| `categoria_atividade` | 3 | 1 |
| `serie_atividade` | 15 | 3 |
| `atividade` | 15 | 4 |
| `categoria_importancia` | 3 | 1 |
| `serie_importancia` | 17 | 3 |
| `importancia` | 15 | 4 |
| `categoria_financeira` | 4 | 1 |
| `movimentacao_financeira` | 15 | 4 |
| `lembrete_importancia` | 11 | 3 |
| `notificacao` | 8 | 3 |
| `requisicao_idempotente` | 10 | 2 |
| **Total** | **134** | **32** |

Análise dos 13 pontos obrigatórios:

| # | Ponto | Situação no contrato | Conclusão |
| --- | --- | --- | --- |
| 1 | `senha_hash`, sem `confirmar_senha`. Recuperação única. Hashes de código e token. Consumo único | `usuario_id` único em `recuperacao_senha`. `token_redefinicao_hash` único quando preenchido. `utilizado_em` presente | **Suficiente.** O consumo único é garantido por trava de linha e atualização condicional (arquitetura §8.3). O intervalo entre reenvios usa `expira_em − 10 min`, sem coluna nova |
| 2 | Catálogos separados e compartilhados, com histórico preservado ao desativar | `ativa` e unicidades presentes. FKs `RESTRICT` | Suficiente |
| 3 | Unicidade `(serie_id, numero_ocorrencia)` também após exclusão lógica. Várias avulsas com nulos | UNIQUE padrão do PostgreSQL (NULLs distintos) | Suficiente. Não usar `NULLS NOT DISTINCT` nem índice parcial que ignore excluídas |
| 4 | FKs compostas de propriedade (5) e `UNIQUE(id, usuario_id)` nos 4 destinos | Especificadas | Suficiente, com UUID nas duas colunas |
| 5 | FK composta `(categoria_id, tipo)` e `UNIQUE(tipo, nome)` e `UNIQUE(id, tipo)` | Especificadas | Suficiente |
| 6 | Pagamento em um único lado. Uma despesa por importância e uma importância por despesa | `movimentacao_financeira.importancia_id` UNIQUE | Suficiente |
| 7 | Pares opcionais e CHECKs com `NULL` | Especificados com `IS NULL`/`IS NOT NULL` | Suficiente. A F2 testa os casos com `NULL` |
| 8 | Decimal e `Numeric(12,2)` sem float | Especificado | Suficiente. A API transporta valores como string (DEC-MV-17) |
| 9 | Instantes com fuso, datas civis, TIME e fuso IANA | Especificado | Suficiente |
| 10 | Exclusão lógica. Sem cascatas. Desvinculação atômica. Notificações preservadas | Especificado (Regras de Integridade 3–9) | Suficiente. A atomicidade é garantida pela transação do router e pela trava do usuário |
| 11 | `notificacao.criada_em` e nomes exatos | Especificado | O mixin atual diverge (REC-MV-008) |
| 12 | Sem colunas derivadas | Especificado | Suficiente |
| 13 | Suficiência para autenticação, idempotência, geração e processamento concorrente | — | **Duas lacunas:** (a) lembrete desativado × cancelado (REC-MV-013, alteração mínima: valor de domínio `DESATIVADO`); (b) horizonte de listagem de séries (REC-MV-012, regra de contrato, sem esquema). Autenticação (claim `sv`), idempotência (trava + `ON CONFLICT`) e concorrência (trava consultiva do usuário) **não exigem tabelas novas** |

---

## 6. Revisão cláusula a cláusula do prompt anterior

Arquivo: `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md`.

**Estado: SUSPENSO — não usar como autorização de implementação.** Suspensão confirmada pelo usuário em 2026-10-11 (`indice.md` §4). O escopo dele (as 13 tabelas) passa a ser a **F2** do plano de fases. O Prompt Master da F2 será gerado no baseline real após a F1, incorporando as classificações abaixo.

Classificações usadas:

- **MANTER:** permanece válida.
- **ESPECIFICAR:** permanece, com detalhe fechado nos documentos da F0.
- **SUBSTITUIR:** deixa de valer e é trocada por outra regra.
- **BLOQUEADA POR DECISÃO:** depende de decisão do usuário.

| Seção do prompt anterior | Conteúdo | Classificação | Tratamento |
| --- | --- | --- | --- |
| Abertura e §1 (fontes) | Stack PG + SQLAlchemy async + Alembic async. Anexo A como fonte | ESPECIFICAR | A fonte vigente é `CLAUDE.md`. O Anexo A é cópia idêntica (seção 2.1). Tipos de ID conforme ADR-0002 |
| §1 (“SGBD resolvido: PostgreSQL”) | PostgreSQL | MANTER | — |
| §2 (fluxo e Zero Surpresas) | Etapa de leitura e aprovação | MANTER | Integrado à Etapa A dos novos prompts |
| §2.4 (“Não presuma FastAPI”) | Framework inferido | SUBSTITUIR | Stack explícita (REC-MV-003) |
| §2 (“Resolva escolhas técnicas rotineiras”) | O implementador decide | SUBSTITUIR | Decisões fechadas pelo Opus (REC-MV-016) |
| §3 (escopo) | 13 tabelas, Alembic, seeds, testes, documentação curta | ESPECIFICAR | Dividido: F1 (fundação técnica, Alembic vazio, testes de infraestrutura) e F2 (esquema completo) |
| §3 (exclusões: sem CRUD, sem autenticação, sem tabelas extras) | Escopo negativo | MANTER | — |
| §4 (fidelidade estrutural, 134 colunas) | Nomes, tamanhos, mixins | MANTER | — |
| §4 (“Todos os `id` são `Integer`… Não transforme em UUID”) | INT | **SUBSTITUIR** | ADR-0002 (UUIDv7). Depende de DEC-MV-06 (**BLOQUEADA POR DECISÃO** até a aprovação) |
| §5.1 (tipos) | Mapeamentos | ESPECIFICAR | `INT` de chave → `Uuid`. Enum: `sqlalchemy.Enum(native_enum=False, create_constraint=True, validate_strings=True, length=<contrato>)` (D-09) |
| §5.1 (timestamps, “Configure uma estratégia explícita”) | Escolha aberta | ESPECIFICAR | `server_default=now()` e `onupdate=now()` com `eager_defaults=True` (D-09) |
| §5.1 (JSON NULL × JSON null) | — | ESPECIFICAR | `JSON(none_as_null=True)` |
| §5.2 (FKs compostas, unicidades, CHECKs) | — | MANTER | Nomes explícitos onde a convenção exceder 63 caracteres |
| §5.3 (exclusão e 8 índices) | — | MANTER | Nomes de índices explícitos e curtos (D-09) |
| §6 (“utilize `asyncpg`”) | Driver | SUBSTITUIR | psycopg 3 (`postgresql+psycopg://`) |
| §6 (sessão e transação) | “Defina quem inicia, confirma…” | SUBSTITUIR | D-04: router confirma e service faz `flush` |
| §6 (sem `create_all`) | — | MANTER | Testes de esquema criam o banco por migração. Testes de infraestrutura da F1 usam o schema auxiliar `teste_infra`, fora do metadata |
| §7 (Alembic async, `def upgrade`) | — | MANTER | — |
| §7 (“função de migração adaptável… sem `asyncio.run()` em loop ativo”) | — | ESPECIFICAR | `env.py` aceita `config.attributes["connection"]` (padrão do cookbook). A fixture de testes é síncrona (D-14) |
| §8 (30 seeds) | — | ESPECIFICAR | UUIDv7 gerado na execução da migração e `ON CONFLICT DO NOTHING` sobre a chave natural |
| §9 (regras de serviço futuras) | — | MANTER | Mapeadas às fases F3–F9 |
| §10 (verificação, PG real) | — | MANTER | — |
| §10 (“Se não houver PostgreSQL… indique”) | Entrega parcial | SUBSTITUIR | Fase bloqueada (REC-MV-015) |
| §10 (`ruff check --fix`, `ruff format`) | Gates que alteram arquivos | ESPECIFICAR | Implementador × verificação `--no-fix`/`--check` (REC-MV-006) |
| §10 (“Execute também a suíte de testes apropriada”) | Suíte | SUBSTITUIR | Seleções explícitas (REC-MV-004) |
| §10 (`downgrade base` e novo `upgrade`) | — | MANTER | Somente no container descartável, com guarda de URL |
| §11 (relatório, sem commit) | — | MANTER | Modo LOCAL. Exceção Cloud delimitada no Prompt Master |
| Anexo A | Contrato | ESPECIFICAR | Prevalece `CLAUDE.md`, atualizado conforme ADR-0002 após aprovação |

**Proposta (não aplicada):** após a aprovação do usuário, acrescentar no topo do prompt anterior o aviso:

> `> ESTADO: SUSPENSO em 2026-10-09 — substituído pelo plano de fases (docs/arquitetura/plano_fases_api.md, F2). Não usar como autorização.`

---

## 7. Registro de achados da arquitetura

Severidades conforme `plano_validacao_auditoria.md` §7. Estados possíveis: `ABERTO`, `DOCUMENTADO` (tratado na documentação da F0), `CORRIGIR_NA_FASE`, `AGUARDANDO_DECISAO` e `ENCERRADO` (critério cumprido e comprovado).

| ID | Sev. | Fato (fonte) | Impacto | Fases | Correção recomendada | Critério de encerramento | Responsável | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACH-MV-ARQ-001 | P2 | Contrato com PK `INT` × diretriz UUID (`CLAUDE.md` 764+) | A implementação divergiria da diretriz ou do contrato | F2+ | ADR-0002 + diff do `CLAUDE.md` | DEC-MV-06 aprovada e `CLAUDE.md` atualizado | Usuário (aprovação), Opus (ADR) | DOCUMENTADO. DEC-MV-06 aprovada e `CLAUDE.md` atualizado em 2026-10-13. Implementação e prova na F2 (CT-F2-02 a 05) |
| ACH-MV-ARQ-002 | P2 | O prompt anterior contém instruções contraditórias com a arquitetura (seção 6) | Seu uso produziria implementação incorreta | F2 | SUSPENSO. Novo Prompt Master da F2 | Aviso aplicado ou registro do usuário. Prompt F2 gerado | Usuário/Opus | DOCUMENTADO. Suspensão confirmada pelo usuário em 2026-10-11 e Prompt F2 gerado em 2026-10-13 (`PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md`) |
| ACH-MV-ARQ-003 | P2 | Engine e settings instanciados na importação. `DATABASE_URL` vazio (`database.py:17`, `settings.py:15`, `.env`) | Importar o app falha sem ambiente. Alembic e testes não conseguem injetar URL | F1 | Criação preguiçosa no `lifespan` (D-03) | CT-F1-01 e CT-F1-02 passando | Sonnet (F1) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-004 | P2 | `get_session` sem contrato de commit/rollback (`database.py:29-31`) | Atomicidade indefinida | F1 | D-04 | CT-F1-10 a CT-F1-14 passando | Sonnet (F1) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-005 | P3 | `TimestampMixin` com nomes em inglês e aplicação genérica (`base.py:11-24`) | Colunas fora do contrato se usado | F2 | Substituir (REC-MV-008) | Introspecção da F2 | Sonnet (F2) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-006 | P3 | Credenciais em texto e porta em `0.0.0.0` (`compose.yaml`) | Exposição local e no primeiro push | F1 | Interpolação do `.env` e `127.0.0.1`. Até lá, o arquivo fica fora do commit de baseline (§3.5) | `docker compose config` sem segredos literais e arquivo idêntico ao Prompt F1 §9.3 | Sonnet (F1). Usuário preenche `.env` | VERIFICADO e encerrado em 2026-10-13. A conferência do commit da F1 (`90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`, 51/51 arquivos iguais ao manifesto) mostrou o `compose.yaml` com SHA-256 `bb1d211f5a498400c8ff4e0a4c54da2d6e6647e2c7069fdc3775558dfdcbf997`, igual ao objeto reauditado e ao Prompt F1 §9.3, sem credenciais literais |
| ACH-MV-ARQ-007 | P3 | `.gitignore` só com `.env`. `__pycache__` presente em `src` | Artefatos versionáveis | F1 | Ampliar `.gitignore` | `git status` sem caches | Sonnet (F1) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-008 | P2 | `fix = true` no Ruff (`pyproject.toml`) torna `ruff check .` modificador. O prompt da sessão sugere esse comando para auditoria | A auditoria alteraria o objeto auditado | Todas | Usar `--no-fix` e `--check` em verificação | Planos usam `--no-fix` | Opus | DOCUMENTADO |
| ACH-MV-ARQ-009 | P3 | taskipy `test` roda a suíte completa com `ruff --fix` | Contraria a política de testes | Todas | Proibir `task test` em gates | Planos sem `task test` | Opus | DOCUMENTADO |
| ACH-MV-ARQ-010 | P3 | `requires-python >=3.12` × alvo 3.14 | `uuid.uuid7()` indisponível em 3.12/3.13 | F1/F2 | `>=3.14` | `pyproject` atualizado | Sonnet (F1) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-011 | P3 | `pydantic-settings` e `httpx` usados ou necessários, mas só transitivos | Quebra se o extra `standard` mudar | F1 | Dependências diretas | `uv.lock` coerente | Sonnet (F1) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-012 | P3 | `CLAUDE.md` linhas 3, 10 e 12 truncadas em `>` | Texto normativo incompleto | — | O usuário restaura o texto original | Linhas completas | Usuário | ABERTO |
| ACH-MV-ARQ-013 | P2 | Lacuna: listagem futura infinita de séries (REC-MV-012) | Requisito 7.2.7 inexequível como escrito | F7 | DEC-MV-18 | Decisão registrada | Usuário | AGUARDANDO_DECISAO |
| ACH-MV-ARQ-014 | P2 | Lacuna de esquema: lembrete desativado × cancelado (REC-MV-013) | A reabertura reativaria um lembrete desligado | F7 | DEC-MV-19 | Decisão registrada | Usuário | AGUARDANDO_DECISAO |
| ACH-MV-ARQ-015 | P2 | Conflito 3.4.2 × enumeração de contas (REC-MV-007) | Privacidade | F3 | DEC-MV-10 | Decisão registrada | Usuário | **ENCERRADO** em 2026-10-13: DEC-MV-10 aprovada na opção A, com o risco aceito expressamente (`indice.md` §4, M16) |
| ACH-MV-ARQ-016 | P2 | Sem limitação de tentativas de login (REC-MV-018) | Força bruta em produção | F11 | DEC-MV-21 | Limitação na borda ou risco aceito formalmente | Usuário | AGUARDANDO_DECISAO |
| ACH-MV-ARQ-017 | P3 | `Message.Message` em PascalCase (`schemas/message.py`) viola a convenção | Estilo | F1 | Remover a rota `/` e o schema (DEC-MV-05) | Arquivos removidos | Sonnet (F1) | CORRIGIR_NA_FASE |
| ACH-MV-ARQ-018 | P3 | CHECK de nome só em `atividade` (REC-MV-014) | Integridade parcial | F2 | DEC-MV-08 | Decisão registrada | Usuário | **ENCERRADO** em 2026-10-13: DEC-MV-08 aprovada (M10); CT-F2-20 passou na auditoria da F2, com os 8 casos negativos atribuídos aos 4 CHECKs e catálogo idêntico ao oráculo (`docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md` §6 e §8.2); integrado no commit `91be324`. Encerramento autorizado na preparação da F3 (`indice.md` §4, M14) |
| ACH-MV-ARQ-019 | P2 | Repositório sem commits | Auditoria sem base Git verificável | F1+ | Commit de baseline pelo usuário. Obrigatório antes da Etapa B da F1; recomendado antes da Etapa A (§3.1, REC-MV-031) | `HEAD` válido cujo conteúdo é exatamente a lista de §3.5, com os hashes de §3.2 e do Prompt F1 §1, verificado na revalidação do Sonnet (Prompt F1 §1.2) e na auditoria do Opus. Alternativa: exceção aceita expressamente pelo usuário e registrada no índice §4. Commit vazio ou SHA qualquer não encerram o achado | Usuário (commit). Sonnet e Opus (verificação) | ABERTO. **Bloqueia a Etapa B da F1** |
| ACH-MV-ARQ-020 | P3 | Resíduos de modelo em `pyproject` (factory_boy, `include tests` inexistente) | Ruído | — | Nenhuma ação obrigatória | — | — | ABERTO (informativo) |
| ACH-MV-ARQ-021 | P2 | ADR-0001 D-02 e arquitetura §2.2, ambos aprovados por DEC-MV-01, divergem sobre importações entre services (REC-MV-029) | Documentação contraditória conduziria a implementação incorreta a partir da F5 | F5+ | DEC-MV-24 | Decisão registrada e D-02 ou §2.2 ajustado conforme a decisão | Usuário (decisão), Opus (ajuste) | AGUARDANDO_DECISAO |
| ACH-MV-ARQ-022 | P2 | O mapeamento de gates da F1 omitia a dependência da convenção de nomes (D-09, DEC-MV-07 pendente) (REC-MV-030) | O Prompt F1 seria liberado com conteúdo não aprovado | F1 | DEC-MV-25 | DEC-MV-25 decidida e Prompt F1 coerente com a decisão | Usuário (decisão), Opus (prompt) | DOCUMENTADO. DEC-MV-25 aprovada em 2026-10-11 e Prompt F1 atualizado para `PRONTO_PARA_ETAPA_A` |
| ACH-MV-ARQ-023 | P3 | Hashes abreviados incorretos em §3.2: `models/base.py` e `schemas/message.py` traziam sufixos de outros arquivos. Os hashes completos do Prompt F1 §1 estavam corretos | Evidência de baseline inconsistente | — | Corrigir §3.2 | Sufixos conferidos com `sha256sum` em 2026-10-11 | Opus | DOCUMENTADO (corrigido em 2026-10-11) |
| ACH-MV-ARQ-024 | P2 | A orientação de commit de baseline do índice §7 (2026-10-11, versão anterior) usava `git add -A` excluindo só caches e incluiria o `compose.yaml` com credenciais literais (REC-MV-032) | Credenciais gravadas no histórico do Git | F1 | Lista explícita de arquivos e `compose.yaml` fora do baseline (§3.5) | Orientação corrigida antes de qualquer execução. Nenhum `git add` ou commit foi feito | Opus | DOCUMENTADO (corrigido em 2026-10-11) |
| ACH-MV-ARQ-025 | P3 | O resumo de D-09 no ADR-0001 omitia o padrão `ix_%(table_name)s_%(column_0_N_name)s`, presente na arquitetura §10.1 e no Prompt F1 §6, que são as fontes citadas na aprovação de DEC-MV-25 | Resumo divergente das fontes aprovadas | F1 | Alinhar o resumo do ADR às fontes aprovadas, sem mudar a convenção | ADR-0001 D-09 com os cinco padrões | Opus | DOCUMENTADO (corrigido em 2026-10-11) |
| ACH-MV-ARQ-026 | P2 | arq §4.2 (passo 1) e §8.2: desligar só `verify_exp`. Desde a 2.6, o PyJWT rejeita `iat` no futuro pelo relógio real e não aceita relógio injetado | Testes com `RelogioFixo` e validação de tempo inconsistentes | F3 | Desligar `verify_exp`, `verify_iat` e `verify_nbf` e validar manualmente com o `Relogio` (dossiê F3 (`preparacao_f3_identidade_acesso.md`) §6.9) | Diffs AR-2 e AR-4 aprovados e aplicados | Usuário (aprovação), Opus (diff) | **ENCERRADO** em 2026-10-13 (M16): Diffs AR-2 e AR-4 aplicados na arquitetura |
| ACH-MV-ARQ-027 | P3 | Segredo JWT: ≥ 32 bytes (ADR D-07, arq §11) × ≥ 32 caracteres (arq §3.1) | Regra ambígua | F3 | ≥ 32 bytes UTF-8 | Diff AR-1 aplicado | Opus | **ENCERRADO** em 2026-10-13 (M16): Diff AR-1 aplicado |
| ACH-MV-ARQ-028 | P2 | Settings obrigatórias da F3 quebrariam `settings_teste`, quatro testes de `tests/infra/test_configuracao.py` e a CLI do Alembic sem `.env` atualizado; a ficha F3 não lista esses arquivos | Implementação bloqueada ou fora do escopo | F3 | Edições exatas no Prompt F3 §7 e §11.1; passo operacional do `.env` | Diff PF-1 aplicado e Prompt F3 liberado | Usuário (aprovação), Opus | **ENCERRADO** em 2026-10-13 (M16): Diff PF-1 aplicado e Prompt F3 liberado com as edições de `tests/conftest.py` e `tests/infra/test_configuracao.py` |
| ACH-MV-ARQ-029 | P2 | arq §11 e CT-F3-25 (“respostas sem token/e-mail”) contradizem login, verificação e `UsuarioResposta` | Teste impossível ou funcionalidade removida | F3 | Lista de campos permitidos por endpoint (dossiê F3 (`preparacao_f3_identidade_acesso.md`) §6.5) | Diffs AR-7 e PV-1 aplicados | Usuário (aprovação), Opus | **ENCERRADO** em 2026-10-13 (M16): Diffs AR-7 e PV-1 aplicados |
| ACH-MV-ARQ-030 | P2 | As travas de linha da recuperação (D-05) pertencem à DEC-MV-14 (F4), mas são usadas na F3 | F3 dependeria de decisão não aprovada | F3 | Aprovação parcial da DEC-MV-14 (dossiê F3 (`preparacao_f3_identidade_acesso.md`) §4.6) | Aprovação registrada no `indice.md` §4 | Usuário | **ENCERRADO** em 2026-10-13 (M16): DEC-MV-14 aprovada no escopo limitado da F3 e registrada (`indice.md` §4, M16) |
| ACH-MV-ARQ-031 | P3 | `asyncio.to_thread` (D-07, D-15) × “pool padrão do anyio” (arq §11); memória do Argon2 sem limite próprio | Garantias inconsistentes e risco de memória | F3 | `anyio.to_thread.run_sync` com limitador dedicado | Diffs AR-5 e AD-1 aplicados | Opus | **ENCERRADO** em 2026-10-13 (M16): Diffs AR-5 e AD-1 aplicados |
| ACH-MV-ARQ-032 | P3 | arq §7: a regra de fuso aceita `localtime` (dependente do servidor) | Fuso com significado variável | F3 | `tempo.fuso_valido` com exclusões | Diff AR-3 aplicado | Opus | **ENCERRADO** em 2026-10-13 (M16): Diff AR-3 aplicado |
| ACH-MV-ARQ-033 | P3 | arq §9.1 e matriz 3.2.1: `^\d{8}$` aceita dígitos não ASCII | Contrato do código ambíguo | F3 | `^[0-9]{8}$` | Diffs AR-6 e MZ-1 aplicados | Opus | **ENCERRADO** em 2026-10-13 (M16): Diffs AR-6 e MZ-1 aplicados |
| ACH-MV-ARQ-034 | P3 | O handler genérico registra a exceção; exceções do `smtplib` carregam o destinatário; nome com CR/LF quebraria o cabeçalho | E-mail em log; falha de envio | F3 | `FalhaEnvioEmail` sem dados; nome sem caracteres de controle | Prompt F3 liberado com o contrato | Opus | **ENCERRADO** em 2026-10-13 (M16): Prompt F3 liberado com o contrato de `FalhaEnvioEmail` e do nome sem caracteres de controle |
| ACH-MV-ARQ-035 | P3 | `EmailStr` só minimiza o domínio e aceita SMTPUTF8; o `CLAUDE.md` exige minúsculas | Unicidade inconsistente | F3 | Forma canônica (R9.9) | Diffs AR-6 e CM-2 aplicados | Opus | **ENCERRADO** em 2026-10-13 (M16): Diffs AR-6 e CM-2 aplicados |
| ACH-MV-ARQ-036 | P3 | Pseudocódigo de arq §8.2 e §8.3 viola PLR0913 e PLR0911 (Ruff ativo) | Implementação literal reprovaria no lint | F3 | Parâmetros explícitos (até 5) e avaliação auxiliar | Diff AR-4 aplicado | Opus | **ENCERRADO** em 2026-10-13 (M16): Diff AR-4 aplicado |
| ACH-MV-ARQ-037 | P3 | arq §8.3.1 captura o instante antes da trava; §8.3.2, depois | Decisão com tempo anterior à espera | F3 | Instante depois da trava (R11.2) | Diff AR-5 aplicado | Opus | **ENCERRADO** em 2026-10-13 (M16): Diff AR-5 aplicado |
| ACH-MV-ARQ-038 | P3 | `ContextoUsuario`: arq §4.2 inclui `nome_completo`; D-13 não | Contrato divergente | F3 | Campos de D-13 | Diff AR-2 aplicado | Opus | **ENCERRADO** em 2026-10-13 (M16): Diff AR-2 aplicado |

Achados P0/P1: **nenhum**.

---

## 8. Riscos

| ID | Risco | Probabilidade/impacto | Mitigação | Fase |
| --- | --- | --- | --- | --- |
| RSK-MV-01 | Custo da primeira materialização de séries diárias antigas (pendências anteriores e atrasos) | Média/baixo-médio (centenas a milhares de linhas, uma única vez por intervalo) | Inserção em lote com `ON CONFLICT DO NOTHING` e índices de série. Medição na F11 com volume representativo | F5, F7, F11 |
| RSK-MV-02 | A trava por usuário serializa leituras compostas com escritas do mesmo usuário | Baixa/baixo (uso pessoal) | Trava compartilhada em leituras sem materialização. `lock_timeout` de 5 s com resposta 503 repetível | F4+ |
| RSK-MV-03 | JWT sem revogação no logout | Média/médio se o token vazar | Validade padrão de 24 h e claim `sv`. Risco aceito na DEC-MV-09 (2026-10-13) | F3 |
| RSK-MV-04 | SMTP lento mantém a transação de recuperação aberta | Baixa/baixo | Timeout de 10 s por operação de socket. A trava atinge só a linha do usuário. Consequências aceitas na DEC-MV-12 (2026-10-13; tabela de D-15) | F3 |
| RSK-MV-05 | Versões recentes (Python 3.14, SQLAlchemy 2.1, Starlette 1.x) com incompatibilidades pontuais | Média/baixo | A Etapa A confirma as APIs. Testes reais | F1+ |
| RSK-MV-06 | Lembretes atrasados se o processo do job parar | Média/médio | Readiness e monitoramento (F11). Regra de atraso (DEC-MV-20) | F9, F11 |
| RSK-MV-07 | PostgreSQL 15 com fim de suporte em nov/2027 (**NÃO VERIFICADO** nesta sessão. Data de calendário conhecida do projeto PostgreSQL) | Certa/baixo | Planejar atualização de versão maior antes da produção prolongada | F11 |
| RSK-MV-08 | Relógio do banco (`criado_em`) × relógio da aplicação (demais instantes) | Baixa/baixo | Comparações sempre na mesma origem. Documentado em D-13 | Todas |

---

## 9. Decisões que o usuário precisa aprovar

Ordenadas pelo gate que bloqueiam. Recomendação = proposta do Opus. “Efeito se aprovada” indica o que passa a valer.

**Estado em 2026-10-11:** DEC-MV-01 a 05 e DEC-MV-25 **APROVADAS** pelo usuário (registro e escopo no `indice.md` §4). DEC-MV-25 foi aprovada com escopo limitado. DEC-MV-06 a 24 continuam pendentes. DEC-MV-24 e 25 foram acrescentadas nesta data (REC-MV-029 e REC-MV-030). DEC-MV-26 foi acrescentada pela auditoria da F1 (`docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md`, anexo B) e **APROVADA** na opção B, também em 2026-10-11 (`indice.md` §4, M4).

**Estado em 2026-10-13:** DEC-MV-06, DEC-MV-07 (restante de D-09) e DEC-MV-08 **APROVADAS** pelo usuário (`indice.md` §4, M10). Na mesma mensagem, o usuário escolheu a opção A do ACH-MV-F1-005 (`alembic/` no Ruff e no Pyright). DEC-MV-09 a 24 continuam pendentes.

**Estado em 2026-10-13 (preparação da F3):** DEC-MV-09 a 13 continuam **pendentes**. A avaliação crítica, os refinamentos (R9.1–R9.9 e R11.1–R11.10; a R9.9 veio da revisão M15), o contrato SMTP e os textos sugeridos de aprovação estão no dossiê F3 (`preparacao_f3_identidade_acesso.md`) §4 e §10. A DEC-MV-10 envolve aceitar um risco de privacidade. A F3 depende também de uma aprovação **parcial** da DEC-MV-14, limitada às travas de linha da recuperação (dossiê §4.6). Nenhuma decisão foi aprovada por essa preparação, e a coluna de recomendação abaixo continua como na proposta original; vale a análise do dossiê.

**Estado em 2026-10-13 (liberação da F3):** DEC-MV-09 a 13 **APROVADAS** e DEC-MV-14 **APROVADA só no escopo da F3** (travas de linha da recuperação), conforme o dossiê da F3 §4 (`indice.md` §4, M16). Na DEC-MV-10, opção A, o usuário aceitou o risco de enumeração sem prazo, enquanto valer 3.4.2. DEC-MV-14 no restante e DEC-MV-15 a 24 continuam pendentes; a DEC-MV-24 segue para antes da F5.

| ID | Decisão | Recomendação | Efeito se aprovada | Documentos | Bloqueia |
| --- | --- | --- | --- | --- | --- |
| DEC-MV-01 | Arquitetura em camadas `routers → services → models`, sem repository, monólito modular. Organização de diretórios e nomenclatura. Driver psycopg 3 | **APROVADA em 2026-10-11** | Base de todas as fases | ADR-0001 D-01–D-03, arquitetura §2 | **F1** |
| DEC-MV-02 | Fronteira transacional: sessão por requisição (autobegin), commit explícito apenas no router, service só com `flush`, jobs como donos da própria transação. Engine criada no `lifespan` | **APROVADA em 2026-10-11** | Contrato transacional único | ADR-0001 D-04, arquitetura §5 | **F1** |
| DEC-MV-03 | Contrato de erros `ErroNegocio` com formato JSON único, catálogo de códigos e erros de validação sem eco da entrada | **APROVADA em 2026-10-11** | Erros estáveis | ADR-0001 D-08, arquitetura §4.4 | **F1** |
| DEC-MV-04 | Política de testes: direcionados, suíte completa como exceção, Testcontainers `postgres:15-alpine`, Ruff de verificação com `--no-fix`, `task test` fora dos gates | **APROVADA em 2026-10-11** | Gates reprodutíveis | ADR-0001 D-14, plano de validação | **F1** |
| DEC-MV-05 | Escopo de higiene da F1: `compose.yaml` com `.env` em `127.0.0.1`, `.gitignore`, `requires-python >=3.14`, `pydantic-settings` direto, `httpx` dev, remoção da rota `/` e de `schemas/message.py`, criação de `__init__.py` | **APROVADA em 2026-10-11** | Alterações em arquivos existentes do usuário na F1 | Plano F1, Prompt Master F1 | **F1** |
| DEC-MV-06 | UUIDv7 gerado na aplicação para as 13 PKs e 19 FKs (ADR-0002), com atualização do `CLAUDE.md` pelo diff proposto | **APROVADA em 2026-10-13**, incluindo a reconciliação das 13 PKs e das 19 FKs no `CLAUDE.md` (§10.1, aplicada) | Contrato físico com UUID. INT abandonado | ADR-0002 | **F2** |
| DEC-MV-07 | Convenções físicas: Enum textual do SQLAlchemy (`native_enum=False`), convenção de nomes (já aprovada para a F1 por DEC-MV-25), timestamps no servidor, `JSON(none_as_null=True)`, uma migração inicial com as 13 tabelas e os seeds | **APROVADA em 2026-10-13**: restante de D-09 e arquitetura §10 (modelos, tipos, enumerações com CHECK, timestamps, mixin, migração inicial e seeds) | Detalhe do Prompt F2 | ADR-0001 D-09 | **F2** |
| DEC-MV-08 | CHECKs extras de nome 3–100 em importância, movimentação e séries | **APROVADA em 2026-10-13**: os quatro CHECKs (`importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao`) | Integridade uniforme | REC-MV-014 | F2 (conteúdo) |
| DEC-MV-09 | Autenticação: JWT HS256 de 24 h com claim `sv`, Argon2id (`argon2-cffi`), `PyJWT`, sem refresh e logout no cliente. `fuso_horario` obrigatório no registro | **APROVADA em 2026-10-13**, conforme o dossiê da F3 §4.1 (R9.1 a R9.9), inclusive o e-mail canônico | Novas dependências na F3 | ADR-0001 D-07 | **F3** |
| DEC-MV-10 | Manter a mensagem de 3.4.2 (e-mail não encontrado) | **APROVADA em 2026-10-13, opção A**, com o risco aceito sem prazo enquanto valer 3.4.2. A justificativa original (“o registro já revela a existência”) é histórica e incompleta (dossiê da F3 §4.2) | Resposta 404 na solicitação de código | REC-MV-007 | **F3** |
| DEC-MV-11 | Recuperação: 10 min, 5 tentativas inválidas e 60 s entre emissões. Senha com 8–128 caracteres, composição apenas sugerida | **APROVADA em 2026-10-13**, conforme o dossiê da F3 §4.3 (R11.1 a R11.10) | Parâmetros da F3 | REC-MV-011, REC-MV-019 | **F3** |
| DEC-MV-12 | E-mail por SMTP (biblioteca padrão, em thread), enviado dentro da transação antes do commit. Falso em memória nos testes | **APROVADA em 2026-10-13**, conforme o dossiê da F3 §4.4, com as consequências 1 a 6 aceitas | Configuração SMTP por ambiente | ADR-0001 D-15 | **F3** |
| DEC-MV-13 | Sem área de Perfil nem alteração de fuso na v1 (apenas `GET /usuarios/me`) | **APROVADA em 2026-10-13**: só `GET /api/v1/usuarios/me` | Escopo reduzido documentado | Matriz | F3 (escopo) |
| DEC-MV-14 | Concorrência por trava transacional consultiva do usuário (exclusiva para escrita e materialização, compartilhada para leitura composta), além de travas de linha na recuperação e nos lembretes | Aprovar. **Aprovada parcialmente em 2026-10-13**, só nas travas de linha da recuperação usadas pela F3 (dossiê da F3 §4.6). O restante continua pendente | Mecanismo central da F4 | ADR-0001 D-05 e D-12 | **F4** |
| DEC-MV-15 | Idempotência: cabeçalho `Idempotency-Key` obrigatório nos cadastros, hash SHA-256 do conteúdo canônico, armazenamento só de respostas 2xx e retenção indefinida na v1 | Aprovar | Protocolo da F4 | ADR-0001 D-06 | **F4** |
| DEC-MV-16 | Recorrência materializada sob demanda (inclusive em GET), algoritmos da arquitetura §8.5 e definição de “Mais recentes” (REC-MV-021) | Aprovar | Base de F5 e F7 | ADR-0001 D-10 | **F5** |
| DEC-MV-17 | Dinheiro como string JSON. Variação percentual com 1 casa, `ROUND_HALF_UP` | Aprovar | Contrato monetário | ADR-0001 D-16 | **F6** |
| DEC-MV-18 | Horizonte de 12 meses para ocorrências de séries em Todos e Próximos | Aprovar | Listas finitas | REC-MV-012 | **F7** |
| DEC-MV-19 | Valor `DESATIVADO` em `lembrete_importancia.situacao` (migração aditiva) | Aprovar | Distinção correta na reabertura | REC-MV-013 | **F7** |
| DEC-MV-20 | Processador de lembretes como processo separado (`python -m …`), com materialização antecipada de 8 dias e regra de lembrete atrasado | Aprovar | Desenho da F9 | ADR-0001 D-11 | **F9** |
| DEC-MV-21 | Limitação de login na borda antes de produção. Risco aceito em desenvolvimento | Aprovar | Gate de exposição pública | REC-MV-018 | F11 (produção) |
| DEC-MV-22 | Atualizar o `CLAUDE.md` com a exceção Cloud e os comandos Ruff de verificação (diff na seção 10) | Aprovar | Normas sem contradição | REC-MV-005, REC-MV-006 | Nenhuma no modo LOCAL |
| DEC-MV-23 | Manter PostgreSQL 15 (`postgres:15-alpine`) no desenvolvimento e nos testes | Aprovar | Sem mudança de imagem | §3.4 | Nenhuma |
| DEC-MV-24 | Importações entre services: ADR-0001 D-02 passa a remeter à matriz da arquitetura §2.2 como regra exaustiva (suporte: `trava`, `idempotencia`, `paginacao`, `recorrencia`, `situacao_importancia`, `lembretes`, `autorizacao`; domínio: `pagamentos`, `painel` e `processamento_lembretes`, conforme a tabela) | Aprovar. §2.2 é o texto detalhado, e os algoritmos de §8.6.3, §8.7, §8.8 e §8.10 dependem dele | Fim do conflito entre dois textos aprovados (REC-MV-029). Sem aprovação, vale D-02 e os algoritmos citados precisam ser revistos | ADR-0001 D-02, arquitetura §2.2 | **F5** |
| DEC-MV-25 | Convenção de nomes do `MetaData` (arquitetura §10.1, parte de D-09) aprovada antecipadamente para a F1. O restante de DEC-MV-07 continua pendente para a F2 | **APROVADA em 2026-10-11, com escopo limitado:** somente `CONVENCAO_NOMES` (padrões `pk`, `uq`, `ck`, `fk` e `ix` de §10.1, preservados exatamente) e `MetaData(naming_convention=CONVENCAO_NOMES)` em `Base` na F1. Não abrange o restante de DEC-MV-07/D-09, DEC-MV-06, tabelas, migrações ou seeds de domínio, `TimestampMixin`, `eager_defaults` nem a implementação da F1 | Prompt F1 passa a `PRONTO_PARA_ETAPA_A`. Alternativa: adiar a convenção para a F2, alterando §2.1 e o Prompt F1 | ADR-0001 D-09, arquitetura §10.1, Prompt F1 §6 e §7.1 | **F1** (G2) |
| DEC-MV-26 | Reconciliar os comandos de formatação na raiz (`CLAUDE.md` §2, Prompt F1 §14, plano §5.1) com os documentos protegidos. Com `preview = true`, o Ruff formatava blocos Python em `.md` (ACH-MV-F1-001 e 004) | **APROVADA em 2026-10-11, opção B:** `exclude = ["*.md"]` em `[tool.ruff.format]`, com os comentários do anexo B da auditoria F1. Opções A (delimitar os comandos) e C (formatar os documentos) não escolhidas | `ruff format .` e `ruff format --check .` passam a ser seguros. Documentos fora do formatador; lint e cobertura de `.py` inalterados. Aplicada pelo Sonnet e verificada na reauditoria (`docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md`) | `pyproject.toml`; auditoria F1, anexo B | **F1** (G5) |

---

## 10. Diffs propostos para o `CLAUDE.md`

**§10.1 foi aplicado em 2026-10-13** pelo Opus, com autorização expressa do usuário (DEC-MV-06, `indice.md` §4, M10). Na mesma data, o `CLAUDE.md` recebeu os ajustes de DEC-MV-07 (representação textual escolhida, `JSON(none_as_null=True)` e regra dos timestamps) e de DEC-MV-08 (CHECKs de nome). As linhas truncadas 3, 10 e 12 (ACH-MV-ARQ-012) não foram tocadas. **§10.2 não foi aplicado:** depende de DEC-MV-22, pendente.

### 10.1. Identificadores (DEC-MV-06)

```diff
-Os nomes de tabelas e colunas serão escritos em `snake_case`, sem espaços e sem acentos. “Obrigatório” significa `NOT NULL`; “opcional” significa que a coluna aceita `NULL`. Todos os campos `id` serão inteiros, chaves primárias e gerados automaticamente pelo banco. As chaves estrangeiras não terão auto incremento.
+Os nomes de tabelas e colunas serão escritos em `snake_case`, sem espaços e sem acentos. “Obrigatório” significa `NOT NULL`; “opcional” significa que a coluna aceita `NULL`. Todos os campos `id` serão UUID (tipo `uuid` do PostgreSQL), chaves primárias, versão 7, gerados pela aplicação com `uuid.uuid7()` (ver docs/adr/0002_identificadores_uuid.md). As chaves estrangeiras que referenciam um `id` também serão UUID.
```

Todas as linhas `- id (chave primária, auto incremento, INT, obrigatório).` passam a:

```diff
-- id (chave primária, auto incremento, INT, obrigatório).
+- id (chave primária, UUID v7 gerado pela aplicação, obrigatório).
```

Nas 19 FKs (`usuario_id`, `categoria_id`, `serie_id`, `importancia_id`, `lembrete_id`), o tipo `INT` passa a `UUID`. A lista completa por tabela está no ADR-0002 §6. As colunas `numero_ocorrencia`, `numero_referencia`, `numero_final`, `tentativas` e `versao_agendamento` **permanecem `INT`**.

Na tabela de mapeamento:

```diff
-| INT | Integer; PK gerada com primary_key=True e autoincrement=True conforme o dialeto. |
+| UUID (identificadores) | Uuid; PK com primary_key=True e default=uuid.uuid7 (aplicação), sem server_default. |
+| INT (demais colunas inteiras) | Integer. |
```

O parágrafo sobre o SGBD não informado e o SQLite passa a registrar: “SGBD: PostgreSQL (decisão do usuário)”.

### 10.2. Exceção Cloud e comandos de verificação (DEC-MV-22)

Acréscimo proposto à seção 1 do `CLAUDE.md`:

```diff
 - **Zero Commits:** Nunca execute `git commit` por conta própria. Apenas gere o código, rode os testes e apresente os relatórios.
+  - Exceção Cloud: somente em sessão do implementador identificada explicitamente como Cloud e após a autorização de implementação, são permitidos commit e push **apenas na branch da sessão** e Pull Request **draft**. Nunca alterar `main`, fazer merge ou declarar a fase aprovada. O merge depende da auditoria local e do usuário.
```

Acréscimo proposto à seção 2:

```diff
 - **Qualidade e Tipagem:** O código deve passar limpo nas seguintes ferramentas de CI local antes de ser considerado pronto:
   - `uv run ruff check --fix .`
   - `uv run ruff format .`
   - `uv run pyright` (Nenhum erro de tipagem é tolerado).
+  - Verificação sem alterar arquivos (auditoria e gates): `uv run ruff check --no-fix .`, `uv run ruff format --check .` e `uv run pyright`. Como o `pyproject.toml` define `fix = true`, `ruff check .` sem `--no-fix` altera arquivos.
```
