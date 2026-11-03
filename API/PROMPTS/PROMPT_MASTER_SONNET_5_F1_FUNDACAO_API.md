# Prompt Master — Sonnet 5 — F1: Fundação técnica da API MinhaVida

| Campo | Valor |
| --- | --- |
| Fase | F1 — Fundação técnica (`docs/arquitetura/plano_fases_api.md`) |
| Estado | **Executado.** F1 **`APROVADO_COM_P3`** na reauditoria de 2026-10-11 (`docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md`) e integrada no commit `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30` (G6 cumprido em 2026-10-13). Não reenviar ao Sonnet. Histórico: `PRONTO_PARA_ETAPA_A` em 2026-10-11 |
| Data | 2026-10-10. Atualizado em 2026-10-11 e em 2026-10-13 (P-DOC-06 e 07, aprovadas pelo usuário; registro do G6) |
| Autor | Claude Opus 5.5 (arquitetura) |
| Destinatário | Claude Sonnet 5 (implementação) |

> **Situação histórica (2026-10-11, antes da Etapa A).** Os itens 1 a 3 abaixo registram as condições de liberação naquela data. A situação atual está no campo Estado e em `docs/arquitetura/indice.md` §5.
>
> **1. Decisões necessárias à Etapa A: satisfeitas.** DEC-MV-01 a 05 e DEC-MV-25 foram aprovadas pelo usuário em 2026-10-11 (`docs/arquitetura/indice.md` §4). DEC-MV-25 tem escopo limitado: somente `CONVENCAO_NOMES` e sua aplicação ao `Base.metadata` (§6). No ADR-0001 estão aceitas D-01, D-02, D-03, D-04, D-08 e D-14, e D-09 apenas na convenção de nomes. O ADR não está aceito como um todo.
>
> **2. Baseline: pendente.** ACH-MV-ARQ-019 (P2) continua aberto. A Etapa A pode ser executada sem commit. A Etapa B exige o commit de baseline do usuário com o conteúdo de §1.1 e a revalidação de §1.2, salvo exceção aceita expressamente pelo usuário.
>
> **3. Implementação: não autorizada.** A Etapa B só começa quando houver, ao mesmo tempo, a resposta “pode implementar” do usuário ao plano da Etapa A e o baseline atendido (§1.1 e §1.2).

---

## 0. Regras absolutas e modo LOCAL/CLOUD

1. Comunicação, comentários e documentação em **PT-BR**. Funções, variáveis e arquivos em `snake_case`; classes em `PascalCase`.
2. **Você não toma decisões arquiteturais.** Tudo o que este prompt fixa deve ser seguido literalmente.
   - Lacuna arquitetural ou divergência entre este prompt e o repositório: **pare no ponto afetado**, descreva-a e devolva ao Opus.
   - Mudança de contrato ou de escopo: devolva ao usuário.
   - Não “escolha a melhor abordagem” onde o prompt já decidiu.
3. **Service pode executar `flush`; service não executa `commit`.** Nesta fase não há services de domínio. A regra vale para todo código novo: **somente routers** (e, nos testes, as rotas de teste) chamam `commit()`.
4. Modo padrão: **LOCAL**.

   | Ação | LOCAL | CLOUD (somente se a sessão for identificada explicitamente como Cloud e houver autorização de implementação) |
   | --- | --- | --- |
   | Implementar o escopo aprovado | Sim | Sim, na branch da sessão |
   | `git commit` | **Proibido** | Somente na branch da sessão |
   | `git push` | Não por iniciativa própria | Somente da branch da sessão |
   | Pull Request | Não presumir | Somente **draft** |
   | Alterar `main`, merge, force-push, proteção de branch | Proibido | Proibido |
   | Declarar a fase aprovada | Proibido | Proibido |

   Remote Git ou Docker não caracterizam Cloud. No modo Cloud, você entrega branch, SHA, diff, PR draft e evidências, e **para**. A auditoria é local, feita pelo Opus sobre o mesmo SHA, e o merge é decisão do usuário.
5. Não use `git reset --hard`, `git clean`, `git checkout -- .`, `git stash` nem nada que descarte trabalho. Preserve alterações do usuário.
6. Não leia nem exponha valores de `.env`. Não grave segredos em arquivos versionáveis, logs ou relatórios. O `compose.yaml` atual contém credenciais literais: não reproduza esses valores em relatórios, logs ou mensagens. Ele é substituído pelo conteúdo de §9.3 na Etapa B.
7. Não execute a suíte completa, `task test`, nem `pytest` sem a seleção definida em §14.

## 1. Estado de partida e baseline verificável

Baseline observado pelo Opus em 2026-10-09 e conferido novamente em 2026-10-11, com os mesmos hashes (repositório **sem commits**; todos os arquivos não rastreados):

| Arquivo | SHA-256 esperado |
| --- | --- |
| `CLAUDE.md` | `565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473` |
| `pyproject.toml` | `b3bf08c5b0702b0c8189929ce7b52de36d357c943d6aece5c1d92331ab4bb779` |
| `uv.lock` | `77f733b52de6ab0af9b20be2c33351ffd9dcc57c73de7010275bfcd0e1a1755f` |
| `compose.yaml` | `f6bb783c8a360f10be6b26ab62d6d1012bca0bb925fbff86d61d45934c1b8ab8` |
| `.gitignore` | `69aa73cf5bc3377a7d97f2e8d2bb773195815efe225af7f1be6f5b9306bbe14f` |
| `.python-version` | `a876e0b10411037a012498b9fe18d9bc1df32ed8b722a13564dc944ddcfd9135` |
| `src/api_gestao_pessoal/main.py` | `2fd86f1d337b0965f1b2d61b557356e963962c626f7a6787132eb89c95ab3311` |
| `src/api_gestao_pessoal/settings.py` | `2824d0579509cdad9bf911d5c4783d93c49e60ea74a434494ad564f7e2374a58` |
| `src/api_gestao_pessoal/database.py` | `1df5342368bc8e3c8c2f46c549fffb3544bcfb2e9036245e9d57bc0c88e7b2c9` |
| `src/api_gestao_pessoal/models/base.py` | `ccd6fc1c8be2d07cfc3fba2f5c40e1fa7648ff67938a71717a91367048e2bc31` |
| `src/api_gestao_pessoal/models/usuario.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (vazio) |
| `src/api_gestao_pessoal/schemas/message.py` | `fc4d4b2fa5137f2f6fe74172f2026a88651f05a576733d2727d0b9a184daf270` |

Fatos relevantes:

- Python 3.14.6 no `.venv`. Versões travadas: SQLAlchemy 2.1.4, Alembic 1.20.0, FastAPI 0.143.0, psycopg 3.3.6, Pydantic 2.13.5, pydantic-settings 2.15.0 (transitivo), pytest 9.1.1, pytest-asyncio 1.4.0, testcontainers 4.15.0, Ruff 0.16.10, Pyright 1.1.414 e httpx 0.28.1 (transitivo).
- `.env` contém apenas `DATABASE_URL` (vazio). **Não o altere.**
- Não há Alembic, testes, `ErroNegocio` nem `__init__.py`.

Se algum hash divergir, registre o estado real na Etapa A. Se a divergência afetar o escopo, **pare e relate**.

### 1.1. Commit de baseline (ACH-MV-ARQ-019, P2)

O usuário cria o commit. Você nunca executa `git add` nem `git commit` (modo LOCAL, §0).

`HEAD` deve conter **exatamente** os 22 arquivos listados em `docs/arquitetura/analise_projeto_minhavida.md` §3.5. Por decisão, ficam fora do commit e continuam não rastreados:

- `compose.yaml`, que tem credenciais literais. Você o reescreve na Etapa B (§9.3). Até lá, o estado de partida é conferido pelo hash da tabela acima;
- `.env` e `.venv/`, ignorados;
- `src/api_gestao_pessoal/__pycache__/`.

Um commit vazio, parcial ou com outros arquivos não serve de baseline.

| Situação | Etapa A | Início da Etapa B |
| --- | --- | --- |
| O commit já existe na Etapa A | Registre o SHA e execute §1.2 (a) e (b) | Execute §1.2 completo. O SHA deve ser igual ao da Etapa A |
| O commit ainda não existe na Etapa A | A Etapa A segue normalmente. O relatório declara “sem commit: Etapa B bloqueada (ACH-MV-ARQ-019)” | Depois que o usuário criar o commit, execute §1.2 completo **antes de qualquer alteração**. A revalidação não repete a análise da Etapa A |
| Não há commit no início da Etapa B | — | **Pare** (§12). Só a exceção ACH-MV-ARQ-019 aceita expressamente pelo usuário permite seguir sem commit |

### 1.2. Revalidação do baseline (somente leitura)

1. (a) `git rev-parse HEAD`: registre o SHA. Se a Etapa A registrou um SHA, ele deve ser o mesmo.
2. (b) `git ls-tree -r --name-only HEAD`: exatamente a lista de 22 arquivos da análise §3.5. Não podem aparecer `compose.yaml`, `.env` nem `__pycache__`.
3. (c) `git status --short`: nenhum arquivo rastreado modificado. Os únicos não rastreados aceitos são `compose.yaml` e `src/api_gestao_pessoal/__pycache__/`.
4. (d) `sha256sum` dos arquivos da tabela de §1: valores iguais aos da tabela, inclusive o `compose.yaml` não rastreado. Para os arquivos rastreados, confira também `git show HEAD:<arquivo> | sha256sum`.
5. (e) `sha256sum` das fontes lidas na Etapa A (§2, inclusive este prompt): valores iguais aos registrados no relatório da Etapa A (§13).

Se tudo coincidir, registre o bloco “Revalidação do baseline” (SHA e resultado de a–e) e siga para §14, passo 1. Não refaça a Etapa A. Se algo divergir, **pare** e relate o passo e o arquivo afetados. O usuário decide se a Etapa A precisa ser refeita, no todo ou em parte.

## 2. Fontes normativas, versões e precedência

Leia integralmente, nesta ordem:

1. `CLAUDE.md`: diretrizes (seções 1 e 2) e contrato de tabelas. Na F1 só se aplicam as diretrizes e a parte de Alembic e mapeamento.
2. `docs/arquitetura/indice.md`: precedência e registro de aprovações.
3. `docs/adr/0001_arquitetura_api_minhavida.md`: §2, D-01 a D-04, D-08, D-14 (aceitas) e D-09 somente na convenção de nomes (aceita por DEC-MV-25).
4. `docs/arquitetura/arquitetura_api_minhavida.md`: §1.1, §2, §3, §4.4 e §5 (aceitas nos itens da F1), mais §4.1, §6.5 e §10.1/§10.5 (somente convenção e Alembic) como contexto. O que vale para a F1 nessas seções de contexto está fixado neste prompt.
5. `docs/arquitetura/plano_validacao_auditoria.md`: §2, §3, §4 (F1), §5 e §6.
6. Este prompt.

Precedência: instruções explícitas do usuário na sessão > `CLAUDE.md` > ADRs **aceitos** > documentos de arquitetura > este prompt. O prompt `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md` está **SUSPENSO**: não o use.

## 3. Decisões aprovadas e reconciliações aplicáveis

> Registro completo em `docs/arquitetura/indice.md` §4. Estas aprovações **não** autorizam a implementação nem as decisões DEC-MV-06 a 24.

| Decisão | Conteúdo resumido | Aprovação |
| --- | --- | --- |
| DEC-MV-01 | Camadas `routers → services → models`. Sem repository. Diretórios técnicos existentes mantidos. psycopg 3 | **APROVADA** em 2026-10-11 |
| DEC-MV-02 | Sessão por requisição com autobegin. Commit explícito só no router. Engine no `lifespan` | **APROVADA** em 2026-10-11 |
| DEC-MV-03 | `ErroNegocio` e formato único de erro | **APROVADA** em 2026-10-11 |
| DEC-MV-04 | Testes direcionados. Testcontainers `postgres:15-alpine`. Ruff de verificação com `--no-fix` | **APROVADA** em 2026-10-11 |
| DEC-MV-05 | Higiene: `compose.yaml`, `.gitignore`, `requires-python`, dependências diretas, remoção de `GET /` | **APROVADA** em 2026-10-11 |
| DEC-MV-25 | Somente `CONVENCAO_NOMES` (§6, padrões `pk`, `uq`, `ck`, `fk` e `ix` preservados exatamente) e `MetaData(naming_convention=CONVENCAO_NOMES)` em `Base`. Não abrange o restante de D-09/DEC-MV-07, DEC-MV-06, tabelas, migrações ou seeds de domínio, `TimestampMixin` nem `eager_defaults` | **APROVADA** em 2026-10-11 (escopo limitado) |

O ambiente Alembic sem revisões (§8.7) está coberto pelas decisões aprovadas acima: stack com Alembic async (DEC-MV-01), engine própria do Alembic (D-03) e fixture síncrona com CT-F1-17 a 19 (DEC-MV-04). Ele não depende de DEC-MV-07.

Reconciliações implementadas nesta fase: REC-MV-002, 003, 004, 006, 009, 010, 015 e 024 (`analise_projeto_minhavida.md` §4).

## 4. Escopo e exclusões

**Dentro do escopo:**

1. Configuração preguiçosa (`obter_settings`) com as variáveis F1 de arquitetura §3.1.
2. Engine e fábrica de sessões criadas no `lifespan`. `obter_sessao` e `SessaoDep` com `scope="function"`.
3. Fábrica `criar_app(settings=None)` e `app = criar_app()` sem I/O na importação.
4. `ErroNegocio`, catálogo F1 de `CodigoErro`, handlers e schema de erro.
5. Middleware `X-Request-ID` e configuração de logging.
6. `GET /saude` e `GET /saude/pronto`.
7. Convenção de nomes no `MetaData` de `Base`.
8. Alembic async **sem revisões**.
9. Infraestrutura de testes (Testcontainers, guarda, apoio de concorrência, rotas de teste) e os testes CT-F1-01 a CT-F1-20.
10. Higiene: `compose.yaml`, `.gitignore`, `.env.exemplo`, `requires-python`, dependências diretas, marcador `concorrencia`, remoção de `GET /` e de `schemas/message.py`.

**Fora do escopo (não implementar):**

- Qualquer tabela ou modelo de domínio, ou alteração em `models/usuario.py` e no `TimestampMixin` (F2).
- Autenticação, JWT e hash de senha (F3).
- Trava do usuário e idempotência (F4).
- Endpoints de negócio.
- CORS.
- `eager_defaults` (F2).
- Qualquer dependência além das listadas em §9.
- Qualquer dependência, tabela, configuração ou abstração para integrações financeiras externas (bancos, Open Finance, gateways, Pix, extratos, conciliação). Elas estão fora do escopo do produto (arquitetura §1.1).

## 5. Política de testes e justificativa do alcance

- A F1 cria a suíte. A seleção da fase é `tests/infra`, que nesta fase coincide com todos os testes existentes. Isso decorre do conteúdo da fase, não de uma execução “completa” por rotina.
- Ordem: testes da fase → verificação de qualidade → checagens estruturais (§14).
- Ao falhar: o mesmo teste → correção → o mesmo teste → `tests/infra`. Nada de reexecutar por rotina.
- Concorrência: CT-F1-15 com conexões independentes e espera por polling com timeout. **Sem `sleep` como sincronização.**
- Docker indisponível = **BLOQUEIO**. Não pule testes nem marque `xfail`.

## 6. Banco, constraints e migrations

- Nenhuma tabela de domínio nesta fase.
- `Base.metadata` recebe a convenção de nomes exata da arquitetura §10.1:
  - `pk_%(table_name)s`
  - `uq_%(table_name)s_%(column_0_N_name)s`
  - `ck_%(table_name)s_%(constraint_name)s`
  - `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`
  - `ix_%(table_name)s_%(column_0_N_name)s`
- Aprovação (DEC-MV-25, 2026-10-11): somente `CONVENCAO_NOMES` com esses cinco padrões, preservados exatamente, e `metadata = MetaData(naming_convention=CONVENCAO_NOMES)` em `Base`. O restante de D-09 (enums, timestamps, `eager_defaults`, `CriadoAtualizadoMixin`, nomes explícitos de índices, limite de 63 caracteres, revisões e seeds) não está aprovado e fica fora da F1.
- Alembic async sem revisões. `alembic heads` vazio. `alembic upgrade head` e `alembic check` funcionando contra o container.
- Os testes de transação usam o schema auxiliar `teste_infra`, criado e removido pela fixture. Ele fica fora do metadata, por isso o `alembic check` não o enxerga. **Proibido** `create_all`, `drop_all` e `stamp`.

## 7. Arquivos permitidos, novos e protegidos

### 7.1. Alterar (existentes)

| Arquivo | Alteração exata |
| --- | --- |
| `pyproject.toml` | (a) `requires-python = ">=3.14"`. (b) Em `[tool.pytest.ini_options].markers`, acrescentar `"concorrencia: teste com transações concorrentes em conexões independentes"`, mantendo `performance`. (c) As dependências entram **somente** via `uv add` (§9). Nenhuma outra linha muda |
| `uv.lock` | Somente via `uv` |
| `compose.yaml` | Conteúdo-alvo exato em §9.3 |
| `.gitignore` | Conteúdo-alvo exato em §9.4 |
| `src/api_gestao_pessoal/settings.py` | §8.1 |
| `src/api_gestao_pessoal/database.py` | §8.2 |
| `src/api_gestao_pessoal/main.py` | §8.3 |
| `src/api_gestao_pessoal/models/base.py` | Somente acrescentar `CONVENCAO_NOMES` e `metadata = MetaData(naming_convention=CONVENCAO_NOMES)` em `Base`. **Não** alterar `TimestampMixin` |

### 7.2. Criar (PLANEJADOS)

```text
.env.exemplo
alembic.ini
alembic/env.py
alembic/script.py.mako
alembic/versions/.gitkeep
src/api_gestao_pessoal/__init__.py
src/api_gestao_pessoal/erros.py
src/api_gestao_pessoal/rastreamento.py
src/api_gestao_pessoal/models/__init__.py
src/api_gestao_pessoal/schemas/__init__.py
src/api_gestao_pessoal/schemas/erro.py
src/api_gestao_pessoal/schemas/saude.py
src/api_gestao_pessoal/routers/__init__.py
src/api_gestao_pessoal/routers/saude.py
tests/__init__.py
tests/conftest.py
tests/apoio/__init__.py
tests/apoio/banco.py
tests/apoio/rotas_teste.py
tests/infra/__init__.py
tests/infra/conftest.py
tests/infra/test_configuracao.py
tests/infra/test_saude.py
tests/infra/test_erros.py
tests/infra/test_sessao_transacao.py
tests/infra/test_alembic_ambiente.py
```

### 7.3. Remover

- `src/api_gestao_pessoal/schemas/message.py` (a rota `GET /` sai de `main.py`).

### 7.4. Protegidos (não alterar)

`CLAUDE.md`, `.env`, `README.md`, `docs/**`, `PROMPTS/**`, `src/api_gestao_pessoal/models/usuario.py` e a configuração do Ruff/Pyright/coverage/taskipy no `pyproject.toml` (exceto §7.1).

## 8. Algoritmos, invariantes e contratos transacionais

### 8.1. `settings.py`

- Manter `class Settings(BaseSettings)` com `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", hide_input_in_errors=True)`.
- Campos:
  - `DATABASE_URL: SecretStr` (obrigatório);
  - `AMBIENTE: Literal["desenvolvimento", "teste", "producao"] = "desenvolvimento"`;
  - `LOG_NIVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"`;
  - `DB_POOL_SIZE: int = Field(5, ge=1, le=50)`;
  - `DB_MAX_OVERFLOW: int = Field(5, ge=0, le=50)`;
  - `DB_POOL_TIMEOUT_S: float = Field(10, gt=0)`;
  - `DB_CONNECT_TIMEOUT_S: int = Field(5, ge=1, le=60)`;
  - `DB_STATEMENT_TIMEOUT_MS: int = Field(15000, ge=100)`;
  - `DB_LOCK_TIMEOUT_MS: int = Field(5000, ge=50)`;
  - `DB_IDLE_IN_TRANSACTION_TIMEOUT_MS: int = Field(30000, ge=1000)`.
- `@field_validator("DATABASE_URL")`: se `not valor.get_secret_value().startswith("postgresql+psycopg://")`, lançar `ValueError("DATABASE_URL deve usar o esquema postgresql+psycopg://")`. A mensagem **não** contém o valor.
- `@functools.lru_cache(maxsize=1) def obter_settings() -> Settings: return Settings()`. O Pyright pode acusar o campo obrigatório. Use `Settings()  # pyright: ignore[reportCallIssue]` **somente** nessa linha, com comentário explicando que os valores vêm do ambiente.
- **Remover** a instância `settings = Settings()` do nível de módulo.

### 8.2. `database.py`

Implementar exatamente o contrato de arquitetura §3.2:

- `criar_engine(settings: Settings) -> AsyncEngine`:
  - `hide_parameters=True`, `pool_pre_ping=True`, `pool_recycle=1800`;
  - `pool_size`, `max_overflow` e `pool_timeout` das settings;
  - `connect_args={"connect_timeout": ..., "options": "-c statement_timeout=<ms> -c lock_timeout=<ms> -c idle_in_transaction_session_timeout=<ms>"}`.
- `criar_fabrica_sessoes(engine) -> async_sessionmaker[AsyncSession]` com `expire_on_commit=False` e `autoflush=False`. Sem `autocommit`.
- `async def obter_sessao(request: Request) -> AsyncIterator[AsyncSession]`:
  - obtém `request.app.state.fabrica_sessoes`;
  - `async with fabrica() as sessao: yield sessao`;
  - **sem commit nem rollback explícitos**: o `close()` desfaz o que não foi confirmado.
- `SessaoDep = Annotated[AsyncSession, Depends(obter_sessao, scope="function")]`. **Todo** uso de sessão em dependências e rotas passa por esse alias, para que dependência e endpoint compartilhem a mesma sessão.
- Remover a `engine` e a `async_session_factory` do nível de módulo e `get_session`. Na Etapa A, confirme com `rg -n "get_session|async_session_factory|from api_gestao_pessoal.settings import settings"` que não há outros usos.

### 8.3. `main.py`

- `def criar_app(settings: Settings | None = None) -> FastAPI` conforme arquitetura §3.2:
  - `lifespan` que resolve `settings or obter_settings()`, chama `configurar_logging(s.LOG_NIVEL)`, cria a engine e a fábrica em `app.state` (`settings`, `engine`, `fabrica_sessoes`) e faz `await engine.dispose()` no `finally`;
  - `FastAPI(title="API MinhaVida", version="0.1.0", lifespan=...)`;
  - `app.middleware("http")(middleware_id_requisicao)`;
  - `registrar_tratadores_erro(app)`;
  - `app.include_router(saude.router)`.
- `app = criar_app()` no nível do módulo (nenhum I/O nem leitura de ambiente na importação).
- Remover a rota `GET /` e o import de `Message`.

### 8.4. `rastreamento.py`

- `ID_REQUISICAO: ContextVar[str | None] = ContextVar("id_requisicao", default=None)` e `PADRAO_ID_REQUISICAO = re.compile(r"^[A-Za-z0-9-]{8,64}$")`.
- `async def middleware_id_requisicao(request, call_next)`:
  - obtém `X-Request-ID`; se não casar com o padrão, usa `uuid.uuid4().hex`;
  - define `request.state.id_requisicao`;
  - faz `token = ID_REQUISICAO.set(valor)`;
  - `try`: `resposta = await call_next(request)`, `resposta.headers["X-Request-ID"] = valor`, `return resposta`;
  - `finally`: `ID_REQUISICAO.reset(token)`.
- `class FiltroIdRequisicao(logging.Filter)`: se o registro não tiver `id_requisicao`, preenche com `ID_REQUISICAO.get() or "-"`; retorna `True`.
- `def configurar_logging(nivel: str) -> None`:
  - configura o logger `api_gestao_pessoal` (nível, `StreamHandler` com formato `%(asctime)s %(levelname)s %(name)s [%(id_requisicao)s] %(message)s` e o filtro);
  - é idempotente: não duplica o handler (marcar o handler com um atributo próprio);
  - `propagate = True`, para que o `caplog` capture.
- Nunca logar corpo de requisição, URL do banco ou cabeçalhos.

### 8.5. `erros.py` e `schemas/erro.py`

- `schemas/erro.py`:
  - `class CampoErro(BaseModel): campo: str; codigo: str; mensagem: str`;
  - `class RespostaErro(BaseModel)` com `codigo: str`, `mensagem: str`, `campos: list[CampoErro] = Field(default_factory=list)`, `detalhes: dict[str, Any] | None = None` e `id_requisicao: str | None = None`.
- `erros.py`:
  - `class CodigoErro(StrEnum)` com os códigos F1 de arquitetura §4.4: `VALIDACAO`, `CORPO_INVALIDO`, `RECURSO_NAO_ENCONTRADO`, `METODO_NAO_PERMITIDO`, `ERRO_HTTP`, `CONFLITO_CONCORRENCIA`, `TEMPO_ESGOTADO`, `SERVICO_INDISPONIVEL` e `ERRO_INTERNO`;
  - `CATALOGO_ERROS: dict[CodigoErro, tuple[HTTPStatus, str]]` com status e mensagens **exatamente** como na tabela de §4.4 (`ERRO_HTTP` usa 400 como padrão; o status real vem da `HTTPException`).
  - `class ErroNegocio(Exception)` com `__init__(self, codigo: CodigoErro, mensagem: str | None = None, *, campos: Sequence[CampoErro] | None = None, detalhes: Mapping[str, Any] | None = None, cabecalhos: Mapping[str, str] | None = None)`:
    - o status vem **sempre** do catálogo;
    - `super().__init__(codigo.value)`, sem dados sensíveis.
  - `@dataclass(frozen=True, slots=True) class DadosErro` com `status: int`, `codigo: str`, `mensagem: str`, `campos: tuple[CampoErro, ...] = ()`, `detalhes: Mapping[str, Any] | None = None` e `cabecalhos: Mapping[str, str] | None = None`.
  - `def responder_erro(request: Request, dados: DadosErro) -> JSONResponse`:
    - corpo `RespostaErro(..., id_requisicao=getattr(request.state, "id_requisicao", None))`;
    - cabeçalhos de `dados.cabecalhos` e `X-Request-ID`, quando houver.
  - Handlers (`registrar_tratadores_erro(app)` registra os cinco):
    1. `ErroNegocio` → `DadosErro` do catálogo.
    2. `RequestValidationError`:
       - se algum erro tiver `type == "json_invalid"` → 422 `CORPO_INVALIDO`, sem `campos`;
       - senão, 422 `VALIDACAO` com `campos = converter_erros_validacao(exc.errors())`, mapeando conforme a tabela de arquitetura §4.4;
       - `campo` = `loc` sem o primeiro elemento quando ele for `body`, `query`, `path`, `header` ou `cookie`, unido por `"."`; vazio vira `"corpo"`;
       - **nunca** usa `input` nem valores de `ctx` além de `min_length` e `max_length`.
    3. `StarletteHTTPException`: 404 → `RECURSO_NAO_ENCONTRADO`; 405 → `METODO_NAO_PERMITIDO`, preservando `exc.headers` (`Allow`); demais → `ERRO_HTTP` com `status = exc.status_code`.
    4. `sqlalchemy.exc.DBAPIError`, por `sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)`:
       - `{"40001", "40P01", "55P03"}` → 503 `CONFLITO_CONCORRENCIA` com `Retry-After: 1`;
       - `"57014"` → 503 `TEMPO_ESGOTADO`;
       - demais → 500 `ERRO_INTERNO`;
       - log: `warning` com o código para 503. Para 500, `logger.error` **sem `exc_info`**, com `sqlstate`, classe, esquema, tabela, coluna e restrição (`exc.orig.diag`), a pilha sem mensagens (`traceback.format_tb(exc.__traceback__)`) e `extra={"id_requisicao": ...}`. A mensagem do driver, o `DETAIL`, `str(exc)` e `repr(exc)` nunca entram no log;
       - *atualizado em 2026-10-11 (P-DOC-01), com aprovação do usuário:* correção de ACH-MV-F1-002 (`docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` e `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` §7.2). O texto anterior, “`exception` para 500, sem a URL e sem parâmetros”, gravava valores de colunas pelo `DETAIL` do PostgreSQL.
    5. `Exception` → 500 `ERRO_INTERNO` e `logger.exception("erro inesperado", extra={"id_requisicao": ...})`.

### 8.6. `routers/saude.py` e `schemas/saude.py`

- `class SituacaoSaude(BaseModel): situacao: Literal["ativo", "pronto"]`.
- `router = APIRouter(tags=["saúde"])`.
- `GET /saude` → `SituacaoSaude(situacao="ativo")`.
- `GET /saude/pronto(request: Request)`:
  - `async with asyncio.timeout(2):`, com `async with request.app.state.engine.connect() as conexao: await conexao.execute(text("SELECT 1"))`;
  - em `DBAPIError`, `OSError` ou `TimeoutError`: registrar `warning` (sem URL) e `raise ErroNegocio(CodigoErro.SERVICO_INDISPONIVEL)`;
  - não usa `SessaoDep`.

### 8.7. Alembic

- Use como referência, **somente leitura**, os arquivos do template instalado em `.venv/lib/python3.14/site-packages/alembic/templates/async/`.
- `alembic.ini`:
  - `[alembic]` com `script_location = %(here)s/alembic`, `prepend_sys_path = src`, `path_separator = os`, `file_template = %%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s`;
  - comentário em PT-BR de que a URL vem de `config.attributes["url_banco"]` ou de `DATABASE_URL` (Settings);
  - **sem** `sqlalchemy.url`;
  - seções de logging do template.
- `alembic/env.py`:
  - `if config.config_file_name is not None and config.attributes.get("configurar_logging", True): fileConfig(...)`;
  - `from api_gestao_pessoal.models import Base` → `target_metadata = Base.metadata`;
  - `def obter_url() -> str`: `config.attributes.get("url_banco")` ou, se ausente, `obter_settings().DATABASE_URL.get_secret_value()` (import local de `api_gestao_pessoal.settings`);
  - modo offline: `context.configure(url=obter_url(), target_metadata=..., literal_binds=True, dialect_opts={"paramstyle": "named"}, compare_type=True, compare_server_default=True)`;
  - `def executar_migracoes(conexao: Connection) -> None`: `context.configure(connection=conexao, target_metadata=..., compare_type=True, compare_server_default=True)` e `with context.begin_transaction(): context.run_migrations()`;
  - `async def executar_migracoes_async() -> None`: `create_async_engine(obter_url(), poolclass=pool.NullPool)`, `async with engine.connect() as c: await c.run_sync(executar_migracoes)` e `await engine.dispose()`;
  - modo online: se `config.attributes.get("connection")` for uma `Connection`, chamar `executar_migracoes(conexao)` diretamente; senão, `asyncio.run(executar_migracoes_async())`;
  - **não** importar `api_gestao_pessoal.main` nem `database`.
- `alembic/script.py.mako`: o do template async, com `def upgrade() -> None:` e `def downgrade() -> None:` e docstring em PT-BR.
- `alembic/versions/.gitkeep`: vazio.

### 8.8. Pacotes

- `src/api_gestao_pessoal/__init__.py`: docstring `"""API MinhaVida."""`.
- `models/__init__.py`: `from api_gestao_pessoal.models.base import Base` e `__all__ = ["Base"]`.
- `schemas/__init__.py` e `routers/__init__.py`: docstring curta.

## 9. Detalhes auxiliares, dependências e configuração

### 9.1. Dependências

Executar na Etapa B, após a autorização, nesta ordem:

1. Editar `requires-python` (§7.1).
2. `uv add "pydantic-settings>=2.15.0"`.
3. `uv add --dev "httpx>=0.28.1"`.

Antes e depois, liste as versões travadas com:

```bash
uv run python -c "import tomllib;d=tomllib.load(open('uv.lock','rb'));print(sorted((p['name'],p['version']) for p in d['package']))"
```

**Se alguma versão já travada mudar, PARE e relate antes de seguir.** Não use `uv lock --upgrade`.

### 9.2. `.env.exemplo` (sem valores reais)

```dotenv
# Copie para .env e preencha. Nunca versione o .env.
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@127.0.0.1:5432/db_gestao_pessoal
POSTGRES_USER=USUARIO
POSTGRES_PASSWORD=SENHA
POSTGRES_DB=db_gestao_pessoal
AMBIENTE=desenvolvimento
LOG_NIVEL=INFO
```

### 9.3. `compose.yaml` (conteúdo-alvo exato)

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: db_gestao_pessoal
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:?defina POSTGRES_USER no .env}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?defina POSTGRES_PASSWORD no .env}
      POSTGRES_DB: ${POSTGRES_DB:?defina POSTGRES_DB no .env}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 3s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
```

No relatório, informe ao usuário que ele precisa acrescentar `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` e um `DATABASE_URL` válido ao `.env`. Você não edita o `.env`.

### 9.4. `.gitignore` (conteúdo-alvo exato)

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
.coverage.*
htmlcov/
*.egg-info/
build/
dist/
```

### 9.5. Regras de qualidade ativas (não desativar, não acrescentar ignores)

- Ruff `select = ["I","F","E","W","PL","PT","FAST"]` com `preview = true` e `line-length = 79`. Pontos de atenção:
  - **PLR0913**: máximo de 5 argumentos. Use `DadosErro` (§8.5).
  - **PLR2004**: números mágicos. O ignore `"tests/*"` pode não cobrir subdiretórios. Use `http.HTTPStatus` e constantes nomeadas nos testes. **Não altere** `per-file-ignores`.
  - **PLW1514**: `encoding="utf-8"` em `open` e `read_text`.
  - **PT011**: `pytest.raises(..., match=...)`.
  - **FAST001/FAST002**: `Annotated` em `Depends` e sem `response_model` redundante.
  - **E501**: quebrar strings e comentários longos.
- Pyright `standard` sem erros. `# pyright: ignore[...]` somente na linha prevista em §8.1, com justificativa.
- Se uma regra exigir mudança de configuração para passar, **pare e relate**.

## 10. Schemas, contratos HTTP e `ErroNegocio`

| Rota | Resposta |
| --- | --- |
| `GET /saude` | 200 `{"situacao": "ativo"}` |
| `GET /saude/pronto` | 200 `{"situacao": "pronto"}` ou 503 `{"codigo": "SERVICO_INDISPONIVEL", "mensagem": "Serviço indisponível.", "campos": [], "detalhes": null, "id_requisicao": "…"}` |
| Qualquer erro | Formato `RespostaErro` (arquitetura §4.4), com cabeçalho `X-Request-ID` |

## 11. Testes específicos, dados e resultados esperados

### 11.1. Fixtures (`tests/conftest.py`)

- `IMAGEM_POSTGRES = "postgres:15-alpine"`.
- `container_postgres` (sync, `scope="session"`):
  - `from testcontainers.community.postgres import PostgresContainer`;
  - `PostgresContainer(IMAGEM_POSTGRES, username="minhavida", password=secrets.token_urlsafe(16), dbname="minhavida_teste", driver="psycopg")` como context manager.
- `url_banco_teste` (sync, `scope="session"`): `container.get_connection_url()`, seguido de `garantir_banco_descartavel(url, container)`.
- `settings_teste` (função): `SettingsTeste(DATABASE_URL=SecretStr(url_banco_teste), AMBIENTE="teste")`. Variações via `settings_teste.model_copy(update={...})`.
  - `SettingsTeste(Settings)` fica em `tests/conftest.py`, com `model_config = SettingsConfigDict(env_file=None)` e `settings_customise_sources` retornando somente `(init_settings,)`.
  - Efeito: só valores explícitos e padrões do contrato. Variáveis de ambiente, `.env` e segredos em arquivo não entram no resultado, e o `.env` **não é aberto**, porque a fonte dotenv é construída antes do hook.
  - *Atualizado em 2026-10-11 (P-DOC-02), com aprovação do usuário:* correção de ACH-MV-F1-003 (prompt de correções §7.3), acrescida da emenda `env_file=None` instruída pelo usuário. A forma anterior, `Settings(..., _env_file=None)`, gerava `reportCallIssue` no Pyright e não isolava as variáveis de ambiente.
- `criar_cliente` (async, função): fábrica que recebe um `FastAPI` e entra em `app.router.lifespan_context(app)` e em `httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://teste")`.

### 11.2. Apoio (`tests/apoio/banco.py`)

- `garantir_banco_descartavel(url, container)`:
  - `make_url(url)`;
  - exige `host == container.get_container_host_ip()`, `port == int(container.get_exposed_port(5432))` e `database == "minhavida_teste"`;
  - caso contrário, `RuntimeError("alvo não é o banco descartável de teste")`.
- `url_libpq(url)`: troca `postgresql+psycopg://` por `postgresql://`.
- `async def aguardar_bloqueio(engine, quantidade, timeout=5.0)`:
  - faz polling de `SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND wait_event_type = 'Lock'` até `>= quantidade`, com intervalo de 0,02 s;
  - estoura `TimeoutError` com mensagem clara.

### 11.3. Schema auxiliar (`tests/infra/conftest.py`)

- Fixture `schema_infra` (sync, `scope="session"`), via `psycopg.connect(url_libpq(...), autocommit=True)` e após a guarda:

  ```sql
  CREATE SCHEMA IF NOT EXISTS teste_infra;
  CREATE TABLE IF NOT EXISTS teste_infra.registro (
      id uuid PRIMARY KEY, valor text NOT NULL, unico text,
      CONSTRAINT uq_registro_unico UNIQUE (unico) DEFERRABLE INITIALLY DEFERRED);
  ```

  Teardown: `DROP SCHEMA teste_infra CASCADE`, com guarda.
- Fixture `limpar_registros` (função): `TRUNCATE teste_infra.registro` após cada teste, com guarda.

### 11.4. Rotas de teste (`tests/apoio/rotas_teste.py`, `APIRouter(prefix="/teste")`)

Todas usam `SessaoDep`. Os inserts usam `text(...)` com parâmetros vinculados e `uuid.uuid7()`.

| Rota | Comportamento |
| --- | --- |
| `POST /teste/registros` `{valor}` | INSERT → `commit` → 201 `{"id": ...}` |
| `POST /teste/registros/erro-apos-escrita` | INSERT → `raise ErroNegocio(CodigoErro.VALIDACAO, "erro de teste")` |
| `POST /teste/registros/com-dependencia` | Dependência `consultar_antes(sessao: SessaoDep) -> int` executa `SELECT 1` e retorna `id(sessao)`. O endpoint compara com `id(sessao)` próprio, faz INSERT e `commit`, e retorna 201 `{"id": ..., "mesma_sessao": bool}` |
| `POST /teste/registros/falha-no-commit` | Dois INSERTs com o mesmo `unico` (constraint diferida) → `commit` (falha) |
| `POST /teste/trava` | `SELECT pg_advisory_xact_lock(4242)` → `commit` → 200 |
| `GET /teste/erro-negocio` | `raise ErroNegocio(CodigoErro.VALIDACAO, "Mensagem de teste", campos=[CampoErro(campo="nome", codigo="NOME_OBRIGATORIO", mensagem="Informe o nome")], detalhes={"chave": "valor"}, cabecalhos={"X-Teste": "1"})` |
| `POST /teste/validacao` | Corpo `{nome: str (min_length=3), senha: str, quantidade: int}` → 200 |
| `GET /teste/excecao` | `raise RuntimeError("falha interna de teste")` |

O router de teste é incluído somente no app criado pelos testes: `app = criar_app(settings_teste); app.include_router(router)`.

### 11.5. Casos e expectativas

| CT | Arquivo / teste (nomes obrigatórios) | Expectativa |
| --- | --- | --- |
| CT-F1-01 | `test_configuracao.py::test_settings_exige_database_url`, `::test_settings_rejeita_esquema_sem_eco`, `::test_settings_padroes` | `ValidationError` sem `DATABASE_URL`. Para `postgresql://u:segredo@h/db`, a mensagem não contém “segredo”. Padrões iguais a §8.1 |
| CT-F1-02 | `::test_importacao_sem_efeitos` | Subprocesso `[sys.executable, "-c", "import api_gestao_pessoal.main, api_gestao_pessoal.database, api_gestao_pessoal.models"]` com `env` sem `DATABASE_URL` e `cwd=tmp_path` → `returncode == 0` |
| CT-F1-03 | `::test_obter_settings_cacheado`, `::test_criar_app_usa_settings_injetadas` | Mesmo objeto. `app.state.settings is settings_teste` dentro do lifespan |
| CT-F1-04 | `test_saude.py::test_saude_ativo` | 200 `{"situacao":"ativo"}` |
| CT-F1-05 | `::test_saude_pronto_com_banco` | 200 `{"situacao":"pronto"}` |
| CT-F1-06 | `::test_saude_pronto_sem_banco` | URL para `127.0.0.1:1` → 503 `SERVICO_INDISPONIVEL` em < 3 s (`time.monotonic`) |
| CT-F1-07 | `test_erros.py::test_erro_negocio_formato` | 422, `codigo=VALIDACAO`, `mensagem="Mensagem de teste"`, `campos` e `detalhes` iguais aos enviados, cabeçalho `X-Teste: 1`, `id_requisicao` igual ao `X-Request-ID` enviado (`"teste-12345678"`) |
| CT-F1-08 | `::test_validacao_sem_eco`, `::test_corpo_malformado` | `nome="ab"`, `senha="segredo-super-123"`, `quantidade="x"` → 422 `VALIDACAO` com `campos` contendo `nome/TAMANHO_MINIMO` e `quantidade/FORMATO_INVALIDO`. A string “segredo-super-123” **não** aparece no corpo. Corpo `{` → 422 `CORPO_INVALIDO` |
| CT-F1-09 | `::test_rota_inexistente`, `::test_metodo_nao_permitido`, `::test_excecao_inesperada` | 404 `RECURSO_NAO_ENCONTRADO`. `DELETE /saude` → 405 `METODO_NAO_PERMITIDO`. `GET /teste/excecao` → 500 `ERRO_INTERNO`, corpo sem “falha interna de teste”, `caplog` com traceback |
| CT-F1-10 | `test_sessao_transacao.py::test_commit_no_router_persiste` | Linha visível por conexão psycopg independente |
| CT-F1-11 | `::test_erro_apos_escrita_desfaz` | 422 e 0 linhas |
| CT-F1-12 | `::test_dependencia_e_endpoint_mesma_sessao` | 201, `mesma_sessao is True` e linha persistida |
| CT-F1-13 | `::test_falha_no_commit_nao_responde_sucesso` | 500 `ERRO_INTERNO` e 0 linhas |
| CT-F1-14 | `::test_conexoes_devolvidas_ao_pool` | Após sucesso e erro, `app.state.engine.pool.checkedout() == 0` |
| CT-F1-15 | `::test_lock_timeout_vira_503` (`@pytest.mark.concorrencia`) | `DB_LOCK_TIMEOUT_MS=200`. Conexão independente segura `pg_advisory_lock(4242)` → `POST /teste/trava` → 503 `CONFLITO_CONCORRENCIA`, `Retry-After: 1`. Depois `pg_advisory_unlock(4242)` e `POST /teste/trava` → 200 |
| CT-F1-16 | `test_erros.py::test_id_requisicao_propagado_e_gerado` | Válido é ecoado. Ausente ou `"x"` → gerado com 32 caracteres hex |
| CT-F1-17 | `test_alembic_ambiente.py::test_upgrade_head_sem_revisoes` (teste **síncrono**) | `Config(<raiz>/alembic.ini)`, `attributes["url_banco"]=url` e `["configurar_logging"]=False`. `command.upgrade(cfg, "head")` sem erro. `ScriptDirectory.from_config(cfg).get_heads() == []`. `command.check(cfg)` sem exceção |
| CT-F1-18 | `::test_upgrade_com_conexao_compartilhada` (async) | Engine async do teste → `await conexao.run_sync(lambda c: _upgrade(cfg, c))`, com `cfg.attributes["connection"] = c` → sem erro |
| CT-F1-19 | `::test_env_sem_app_e_sem_url` | `alembic/env.py` (lido com `encoding="utf-8"`) não contém `api_gestao_pessoal.main` nem `postgresql`. Nenhuma linha de `alembic.ini` começa com `sqlalchemy.url` |
| CT-F1-20 | `test_configuracao.py::test_guarda_recusa_banco_alheio` | `garantir_banco_descartavel("postgresql+psycopg://u:p@outro:5432/minhavida_teste", container)` → `RuntimeError` |

A verificação de persistência é sempre feita por **outra conexão** (`psycopg.connect(url_libpq(...))`).

## 12. Critérios de aceite e bloqueios

**Aceite:**

- CT-F1-01 a CT-F1-20 passando.
- Ruff e Pyright limpos (§14).
- `alembic heads` vazio.
- `docker compose config` válido.
- `compose.yaml` idêntico ao bloco de §9.3.
- Nenhum arquivo protegido alterado.
- Nenhuma versão travada alterada.

**Reprovação (qualquer um):**

- `commit()` fora de rota ou router.
- Engine ou settings criadas na importação.
- `create_all`, `drop_all` ou `stamp`.
- Segredo ou credencial literal em arquivo versionável.
- Teste pulado ou `xfail` por falta de Docker.
- Desativação de regra.
- Alteração em `TimestampMixin` ou `models/usuario.py`.
- Execução da suíte por `task test`.

**Bloqueios que exigem parar e relatar:**

- No início da Etapa B, `git rev-parse HEAD` inválido sem exceção ACH-MV-ARQ-019 aceita expressamente pelo usuário, ou qualquer divergência na revalidação do baseline (§1.1 e §1.2).
- Docker indisponível.
- Divergência de baseline.
- API das bibliotecas diferente da descrita (por exemplo, `Depends(scope=...)` inexistente).
- Necessidade de nova dependência.
- Regra de qualidade que exija alterar configuração.

## 13. Etapa A — leitura, análise e autorização

Somente leitura, sem criar nem alterar arquivos:

1. `pwd`, `git status --short --branch` e `git rev-parse HEAD`, que falha se ainda não houver commit. Com commit, execute também §1.2 (a) e (b).
2. `sha256sum` dos arquivos de §1 e comparação com os valores esperados.
3. Leitura das fontes de §2 e registro do SHA-256 de cada uma, usado depois na revalidação (§1.2 e).
4. `uv --version`, `uv run python --version`, `docker version --format '{{.Server.Version}}'`.
5. `rg -n "get_session|async_session_factory|settings import settings|Message" src` para confirmar os pontos de substituição.
6. Leitura do template `.venv/lib/python3.14/site-packages/alembic/templates/async/`.
7. Confirmação, sem executar código de produção, de que `fastapi.Depends` aceita `scope` e de que `testcontainers.community.postgres` existe (`rg` em `.venv`).

Resposta da Etapa A:

- divergências encontradas, ou “nenhuma”;
- SHA de baseline (`git rev-parse HEAD`) com o resultado de §1.2 (a) e (b), ou a declaração “sem commit: Etapa B bloqueada por ACH-MV-ARQ-019”;
- SHA-256 de cada fonte lida (§2);
- lista final de arquivos (§7) e comandos (§14);
- riscos;
- pedido explícito: **“Aguardo ‘pode implementar’ para a F1.”**

**Não implemente antes dessa resposta do usuário.**

## 14. Validação — ordem e comandos exatos (Etapa B)

| # | Comando | Expectativa |
| --- | --- | --- |
| 0 | Revalidação do baseline (§1.2, passos a–e), antes de qualquer alteração | Todos os passos coincidem. Se a Etapa A registrou um SHA, ele é o mesmo. Sem SHA válido e sem exceção aceita, ou com qualquer divergência: **pare** (§12) |
| 1 | Comandos de §9.1, com as duas listagens de versões | Nenhuma versão travada alterada |
| 2 | `uv sync` | Sucesso |
| 3 | `uv run pytest tests/infra -q` | 100 % passando. Registrar contagem e duração |
| 4 | `uv run ruff check --fix .` e depois `uv run ruff format .` | Correções somente nos arquivos do escopo. Conferir com `git status --short` |
| 5 | `uv run pytest tests/infra -q` | **Somente se o passo 4 alterou arquivos `.py`.** Mesmo resultado |
| 6 | `uv run ruff check --no-fix .` | `All checks passed!` |
| 7 | `uv run ruff format --check .` | Nenhum arquivo a reformatar |
| 8 | `uv run pyright` | `0 errors` |
| 9 | `uv run alembic heads` | Saída vazia |
| 10 | `POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet` | Código 0. O `--env-file /dev/null` impede que o Docker Compose leia o `.env` real (ACH-MV-F1-007; P-DOC-06, aprovada em 2026-10-13) |
| 11 | `grep -n "POSTGRES_PASSWORD" compose.yaml` | Somente a linha com `${POSTGRES_PASSWORD:?...}` |
| 12 | `docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine` | Registrar o digest |

Não execute `alembic upgrade` contra o banco de desenvolvimento nem `docker compose up`. A F1 não exige isso.

## 15. Relatório com evidências reais

Conforme `plano_validacao_auditoria.md` §6:

1. Objeto entregue:
   - `git status --short`;
   - SHA de baseline, bloco “Revalidação do baseline” (§1.2) e `git diff --stat` contra ele. Sem commit, somente com a exceção ACH-MV-ARQ-019 aceita;
   - `compose.yaml` (não rastreado por decisão): SHA-256 antes e depois, e confirmação de que o conteúdo final é idêntico ao bloco de §9.3, sem reproduzir os valores antigos;
   - **SHA-256** de cada arquivo criado e alterado;
   - lista de arquivos removidos.
2. Ambiente: uv, Python, Docker e digest da imagem.
3. Saída resumida real de cada comando de §14, na ordem.
4. Tabela CT → node ID → resultado.
5. Versões antes e depois (§9.1).
6. Desvios: nenhum é permitido. Se houver, descrevê-los com a justificativa e o ponto de parada.
7. Instruções ao usuário para preencher o `.env` (§9.3).
8. Pendências e riscos observados.

Não declare a fase aprovada.

## 16. Parada e encaminhamento para auditoria

- Após o relatório, **pare**. O estado é `ENTREGUE_PARA_AUDITORIA`.
- Não inicie a F2 nem crie modelos ou migrações.
- A auditoria independente é do Opus (`plano_validacao_auditoria.md` §9).
- No modo Cloud: commit e push apenas da branch da sessão, PR **draft**, e entrega de branch, SHA e evidências. A auditoria é local.
