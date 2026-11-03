# ADR-0001 — Arquitetura da API MinhaVida

| Campo | Valor |
| --- | --- |
| ID | ADR-0001 |
| Título | Arquitetura da API MinhaVida: camadas, transações, concorrência, idempotência, autenticação, erros, recorrência, lembretes, leitura consistente e testes |
| Estado | **PARCIALMENTE ACEITO.** D-01, D-02, D-03, D-04, D-08 e D-14 foram aceitas em 2026-10-11 (DEC-MV-01 a 04). D-09 foi aceita na convenção de nomes em 2026-10-11 (DEC-MV-25) e no restante em 2026-10-13 (DEC-MV-07). D-07 e D-13 (DEC-MV-09) e D-15 (DEC-MV-12) foram aceitas em 2026-10-13, e D-05 só nas travas de linha da recuperação (DEC-MV-14, escopo limitado da F3). Registro em `indice.md` §4. As demais decisões continuam PROPOSTAS. O ADR como um todo **não** está aceito |
| Data | 2026-10-09. Atualizado em 2026-10-11 e em 2026-10-13 (D-09 aceita; depois, D-07, D-13 e D-15 aceitas e D-05 aceita em escopo limitado, com os diffs AD-1 a AD-3 do dossiê da F3) |
| Autor | Claude Opus 5.5 |
| Fontes | `CLAUDE.md` (diretrizes, telas 1–11 e contrato de tabelas), `docs/arquitetura/analise_projeto_minhavida.md`, `docs/arquitetura/arquitetura_api_minhavida.md` (detalhamento canônico), diretrizes de stack do usuário |
| Relacionados | ADR-0002 (identificadores UUID) |

> Este ADR registra **as decisões e suas justificativas**. Os contratos detalhados (endpoints, algoritmos, sequências) têm uma única fonte canônica: `docs/arquitetura/arquitetura_api_minhavida.md`. Aqui eles são apenas referenciados, para não haver duplicação divergente.

## 1. Contexto e problema

A API MinhaVida atende um aplicativo pessoal de atividades, compromissos (“importâncias”) e finanças. O repositório está na fase inicial:

- uma rota de exemplo;
- engine criada na importação;
- nenhuma tabela, nenhum teste e nenhum commit.

O domínio é rico em invariantes:

- séries recorrentes com ocorrências estáveis;
- pagamento vinculado de forma única;
- lembretes versionados;
- idempotência de cadastros;
- totais exatos em centavos;
- datas no fuso da conta.

O workflow do projeto exige que o implementador (Sonnet) não tome decisões arquiteturais. Portanto, essas decisões precisam estar fechadas antes de cada fase.

## 2. Forças e restrições a preservar

- Stack fixada pelo usuário: Python, FastAPI async, SQLAlchemy 2.x Async, Pydantic v2, Alembic com conexão async, PostgreSQL, pytest, Testcontainers, uv, Ruff e Pyright.
- **Service pode executar `flush`; service não executa `commit`.** O router define a fronteira transacional. Jobs têm ponto de entrada próprio.
- Contrato de tabelas do `CLAUDE.md` (13 tabelas, 134 colunas), salvo a mudança de tipo de ID do ADR-0002.
- Nomenclatura `snake_case`/`PascalCase` e PT-BR na documentação e nos comentários.
- Nenhum serviço externo, biblioteca ou padrão sem necessidade demonstrada.
- **Escopo financeiro (instrução do usuário, 2026-10-11):** receitas e despesas são cadastradas e editadas manualmente pelo usuário, e os totais são calculados a partir desses registros. Não há integração com bancos, Open Finance, gateways ou processadores de pagamento, nem importação de extratos ou conciliação, e nada é preparado “para uso futuro”. Detalhe em `arquitetura_api_minhavida.md` §1.1.
- Ambiente: WSL2, Docker Desktop, um único desenvolvedor e uso pessoal. Volume e SLAs não informados (metas são propostas a validar).

## 3. Decisões

Cada decisão tem um ID estável `D-NN`. A coluna “Aprovação” indica a decisão do usuário correspondente, registrada em `analise_projeto_minhavida.md` §9. A coluna “Estado” vale por decisão. As aprovações estão registradas em `indice.md` §4.

| ID | Tema | Aprovação | Estado | Fases afetadas |
| --- | --- | --- | --- | --- |
| D-01 | Estilo arquitetural | DEC-MV-01 | **ACEITO** (2026-10-11) | Todas |
| D-02 | Organização de diretórios e nomenclatura | DEC-MV-01 | **ACEITO** (2026-10-11), com conflito registrado sobre importações entre services (REC-MV-029, DEC-MV-24) | Todas |
| D-03 | Configuração e ciclo de vida | DEC-MV-02 (também citada em DEC-MV-01) | **ACEITO** (2026-10-11) | F1+ |
| D-04 | Fronteira transacional | DEC-MV-02 | **ACEITO** (2026-10-11) | F1+ |
| D-05 | Concorrência | DEC-MV-14 | PROPOSTO; travas de linha da recuperação aceitas para a F3 (DEC-MV-14, escopo limitado, 2026-10-13) | F3 (linhas), F4+ |
| D-06 | Idempotência | DEC-MV-15 | PROPOSTO | F4+ |
| D-07 | Autenticação e autorização | DEC-MV-09 | **ACEITO** (2026-10-13) | F3+ |
| D-08 | Contrato de erros | DEC-MV-03 | **ACEITO** (2026-10-11) | F1+ |
| D-09 | Modelo físico e migrações | DEC-MV-07. Convenção de nomes: DEC-MV-25 | **ACEITO**: convenção de nomes em 2026-10-11 (DEC-MV-25); enums, timestamps, `eager_defaults`, mixin, JSON, migração inicial e seeds em 2026-10-13 (DEC-MV-07) | F1 (somente a convenção de nomes), F2 |
| D-10 | Recorrência | DEC-MV-16 | PROPOSTO | F5, F7, F9 |
| D-11 | Lembretes e notificações | DEC-MV-20 | PROPOSTO | F7, F9 |
| D-12 | Leitura consistente e paginação | DEC-MV-14 | PROPOSTO | F4+ |
| D-13 | Tempo e fuso | DEC-MV-09 | **ACEITO** (2026-10-13) | F3+ |
| D-14 | Política de testes | DEC-MV-04 | **ACEITO** (2026-10-11) | Todas |
| D-15 | Envio de e-mail | DEC-MV-12 | **ACEITO** (2026-10-13) | F3 |
| D-16 | Dinheiro na API | DEC-MV-17 | PROPOSTO | F6+ |

O ambiente Alembic sem revisões da F1 não depende de D-09. Ele está coberto por decisões aceitas: a stack com Alembic async (REC-MV-003, DEC-MV-01), a árvore e a regra de importação do `env.py` (arquitetura §2, DEC-MV-01), a engine própria do Alembic (D-03) e a fixture síncrona com CT-F1-17 a 19 (D-14 e plano de validação, DEC-MV-04).

---

### D-01 — Estilo arquitetural: monólito modular em camadas

**Alternativas consideradas:**

- (a) Monólito em camadas `routers → services → models`.
- (b) Camada de repository genérica.
- (c) Microsserviços, broker ou CQRS.
- (d) Event sourcing.

**Decisão recomendada:** (a). Uma aplicação FastAPI, com camadas:

- **routers:** HTTP, validação de entrada via schemas e fronteira transacional;
- **services:** regras de negócio, consultas SQLAlchemy, `flush`;
- **models:** mapeamento ORM;
- **schemas:** DTOs Pydantic;
- **jobs:** pontos de entrada fora do HTTP.

**Sem camada de repository.** A `AsyncSession` já é a unidade de trabalho, e as consultas de indicadores são específicas demais para um repositório genérico.

**Justificativa:** o domínio é coeso, tem um único banco e invariantes que atravessam entidades, como pagamento + importância + lembrete. Essas invariantes exigem transações locais, e distribuir o sistema tornaria a atomicidade inviável sem ganho.

**Custos:** os services conhecem o SQLAlchemy. Por isso, os testes de serviço usam PostgreSQL real.

**Detalhe:** arquitetura §2.

### D-02 — Organização de diretórios e nomenclatura

**Decisão recomendada:**

- Manter os diretórios técnicos já existentes, em inglês: `models/`, `schemas/` e `routers/`.
- Acrescentar, no mesmo padrão, `services/` e `jobs/`.
- Manter os módulos `settings.py`, `database.py` e `main.py`.
- Módulos de domínio e identificadores novos em PT-BR `snake_case`: `atividade.py`, `obter_sessao`, `ErroNegocio`.
- Um arquivo de modelo por tabela.
- Direção de dependências: `routers → services → models`. `schemas` são usados por routers e services.
- `models` não importam `services`, `routers` nem `schemas`.
- Importações entre services são permitidas apenas para módulos de suporte (`services/recorrencia.py`, `services/idempotencia.py`, `services/trava.py`, `services/situacao.py`), nunca de forma circular.

> **Conflito registrado (REC-MV-029, ACH-MV-ARQ-021):** o item acima diverge da matriz de importações da arquitetura §2.2, também aprovada por DEC-MV-01. A matriz admite mais módulos de suporte (`paginacao`, `lembretes`, `autorizacao`, `situacao_importancia`) e três orquestradores de domínio. Até o usuário decidir DEC-MV-24, vale o texto acima, por precedência (`indice.md` §3). Nenhuma fase até a F4 é afetada. A F5 depende da decisão.

**Justificativa:** reaproveita a estrutura existente e preserva a rastreabilidade tabela → arquivo.

**Detalhe:** arquitetura §2.

### D-03 — Configuração e ciclo de vida

**Decisão recomendada:**

- `Settings` (pydantic-settings), obtido por `obter_settings()` com `functools.lru_cache`. Não há mais instância criada na importação.
- Engine e `async_sessionmaker` criados no `lifespan` do FastAPI e guardados em `app.state`. `engine.dispose()` no encerramento.
- `criar_app(settings: Settings | None = None)` é uma fábrica sem I/O. `app = criar_app()` no nível do módulo continua disponível para o uvicorn.
- O driver é psycopg 3, com URL `postgresql+psycopg://`.
- Timeouts por conexão via `options` do libpq: `statement_timeout`, `lock_timeout` e `idle_in_transaction_session_timeout`.
- O Alembic usa a própria engine, sem esses timeouts.

**Justificativa:**

- Elimina o efeito colateral de importação (ACH-MV-ARQ-003).
- Permite injetar a URL do container nos testes.
- Mantém o driver já instalado.

**Detalhe:** arquitetura §3.

### D-04 — Fronteira transacional e ciclo de sessão

**Alternativas consideradas:**

- (a) `async with sessao.begin()` no router. É incompatível com o autobegin disparado pela dependência de autenticação, que já consulta o usuário: SQLAlchemy recusa iniciar uma segunda transação.
- (b) Commit no teardown da dependência. Nesse caso o commit ocorreria depois da resposta, ou de forma implícita.
- (c) Transação única por requisição, iniciada por **autobegin** na primeira consulta (inclusive pela dependência de autenticação). **Somente o router chama `await sessao.commit()`**, explicitamente, como último passo antes de devolver a resposta. Sem commit, o fechamento da sessão desfaz tudo.

**Decisão recomendada:** (c). Regras:

1. `obter_sessao` abre a sessão com `async with fabrica() as sessao: yield sessao`, sem commit, e é declarada com `scope="function"`. Todos os usos passam pelo mesmo alias `SessaoDep`, para que dependências e endpoint compartilhem a mesma sessão.
2. Services recebem `AsyncSession` e `ContextoUsuario` como argumentos. Podem executar `flush()` e nunca executam `commit()`, `rollback()` ou `begin()`. A exceção é `begin_nested()` (SAVEPOINT), quando uma decisão documentada exigir continuar após um conflito esperado.
3. Todo endpoint que escreve, inclusive GET que materializa ocorrências, termina com `await sessao.commit()`. Uma falha no commit vira resposta de erro **antes** de qualquer resposta de sucesso.
4. Erros de negócio são `ErroNegocio`. Sem commit, a transação é desfeita pelo fechamento da sessão.
5. **Exceção controlada:** quando uma tentativa inválida precisa persistir (contador da recuperação de senha), o service **retorna um resultado** (não lança exceção). O router faz `commit()` e só depois lança o `ErroNegocio` correspondente. Nenhum handler de exceção faz commit.
6. Jobs: a função de ponto de entrada abre a sessão, chama services e faz o commit por lote ou por unidade.
7. `expire_on_commit=False` e `autoflush=False` são mantidos, com `flush` explícito antes de consultas dependentes. **Não há `relationship()` ORM na v1**: as consultas usam junções explícitas e os services atribuem as FKs diretamente. Isso elimina I/O implícito e a sobreposição de escrita nas FKs compostas que compartilham `usuario_id`. As respostas são schemas Pydantic montados explicitamente, sem serializar objetos ORM.

**Consequências:**

- **Positivas:** atomicidade natural por requisição, contrato simples e testável (CT-F1-10 a CT-F1-14).
- **Custo:** disciplina de commit em cada router de escrita. Os testes de cada endpoint verificam a persistência por outra conexão.

**Detalhe:** arquitetura §5.

### D-05 — Concorrência: trava transacional do usuário e travas de linha

**Alternativas consideradas:**

- (a) `SELECT … FOR UPDATE` por linha, com ordem global de travas entre tabelas. É preciso, mas frágil: a ordem inversa entre movimentação e importância é fácil de violar.
- (b) Isolamento `SERIALIZABLE` com retries. Gera falhas de serialização frequentes em materialização e reexecuções complexas.
- (c) **Trava consultiva transacional por usuário** (`pg_advisory_xact_lock`) para toda escrita de dados do usuário (e materialização), mais travas de linha somente onde não há usuário autenticado (recuperação) ou onde o consumidor atravessa usuários (processador de lembretes), mais constraints do banco como garantia final.

**Decisão recomendada:** (c), em `READ COMMITTED`:

- Chave da trava: `hashtextextended('minhavida:usuario:' || usuario_id::text, 0)`. Uma colisão entre usuários só causa serialização extra, nunca um resultado incorreto.
- Modo exclusivo para escrita e materialização. Modo compartilhado (`pg_advisory_xact_lock_shared`) para leituras compostas sem escrita.
- `lock_timeout` (5 s) resulta em HTTP 503 `CONFLITO_CONCORRENCIA`, com `Retry-After`. O cliente repete com a mesma `Idempotency-Key`.

**Justificativa:**

- Uso pessoal, com contenção por usuário desprezível.
- Uma única trava elimina deadlocks entre operações do mesmo usuário.
- Torna consistentes as leituras de várias instruções (D-12).
- Simplifica a matriz de corridas.

**Custos:**

- Serializa as operações de um mesmo usuário.
- Exige que **todo** caminho de escrita adquira a trava. A regra é verificada por testes de concorrência por operação.

**Detalhe:** arquitetura §6.

### D-06 — Idempotência

**Decisão recomendada:**

- Cabeçalho `Idempotency-Key`, obrigatório nos endpoints de cadastro listados na arquitetura §4.3.
- Formato: `^[A-Za-z0-9_-]{16,64}$`.
- Escopo: `(usuario_id, acao, chave)`.
- `conteudo_hash` = SHA-256 hexadecimal do JSON canônico (`acao`, parâmetros de caminho e corpo validado e normalizado).

Protocolo, dentro da transação do router:

1. adquirir a trava exclusiva do usuário;
2. executar `INSERT … ON CONFLICT DO NOTHING RETURNING`;
3. se já existir, comparar o hash: diferente → 422 `CHAVE_IDEMPOTENCIA_REUTILIZADA`; igual e `CONCLUIDA` → reenviar `codigo_resposta` e `resposta`, com o cabeçalho `Idempotency-Replayed: true`;
4. se o registro for novo, executar a operação e gravar `CONCLUIDA` com a resposta 2xx, na mesma transação.

Outras regras:

- **Erros não são armazenados:** o rollback remove o registro, e a nova tentativa reavalia o estado atual.
- `EM_PROCESSAMENTO` nunca é visível a outra transação: a trava serializa as transações e o `ON CONFLICT` espera o término da concorrente.
- Retenção indefinida na v1. Uma futura limpeza deverá definir prazo de garantia.
- Operações naturalmente idempotentes (definir situação, editar, excluir, vincular o mesmo par) não exigem chave.

**Detalhe:** arquitetura §4.3 e §8.4.

### D-07 — Autenticação e autorização

**Decisão recomendada:**

- Bearer token JWT HS256 (`PyJWT`), com segredo `JWT_SEGREDO` de pelo menos 32 bytes.
- Validade padrão de 24 h, configurável entre 5 e 1440 minutos (DEC-MV-09, R9.1).
- Claims: `sub` (usuario_id), `iat`, `exp`, `typ="access"` e `sv`, o “carimbo de credencial”: 16 primeiros caracteres hexadecimais de `SHA-256(senha_hash)`.
- A cada requisição, a dependência carrega o usuário pelo `sub` e compara o `sv` em tempo constante. A troca de senha invalida todos os tokens anteriores **sem tabela nova**.
- Sem refresh token. Logout descarta o token no cliente.
- Senhas e códigos com Argon2id (`argon2-cffi`), executados em thread por `anyio.to_thread.run_sync`, com limitador dedicado (`ARGON2_MAX_CONCORRENTES`).
- Login com verificação fictícia quando o e-mail não existe, para aproximar o custo do caminho com e-mail existente (não é tempo constante).
- Validação temporal do token feita pela aplicação com o `Relogio` (arquitetura §8.2).

Autorização:

- `usuario_id` vem **somente** do token validado.
- Toda consulta de recurso filtra por `usuario_id`.
- Recurso de outro usuário recebe a mesma resposta de inexistente: 404 `RECURSO_NAO_ENCONTRADO`.
- As FKs compostas de propriedade são a segunda linha de defesa.

**Alternativas descartadas:**

- Tokens opacos em tabela: exigiria uma tabela nova, proibida pelo contrato vigente.
- Cookies de sessão: o cliente é mobile, e exigiriam proteção CSRF.

**Detalhe:** arquitetura §4.2, §8.2 e §11.

### D-08 — Contrato de erros

**Decisão recomendada:** exceção única `ErroNegocio(codigo, mensagem=None, *, campos=None, detalhes=None, cabecalhos=None)` em `src/api_gestao_pessoal/erros.py`, com o catálogo `CodigoErro` (StrEnum), que fornece o status HTTP (sempre do catálogo, nunca sobrescrito) e a mensagem padrão. A assinatura tem 5 parâmetros, para respeitar a regra PLR0913 do Ruff, que está ativa.

Resposta JSON única para todos os erros:

```json
{"codigo": "...", "mensagem": "...", "campos": [{"campo": "...", "codigo": "...", "mensagem": "..."}], "detalhes": null, "id_requisicao": "..."}
```

Handlers:

| Exceção | Resposta |
| --- | --- |
| `ErroNegocio` | Status e código do catálogo |
| `RequestValidationError` | 422 `VALIDACAO`, sem eco de `input` |
| `HTTPException` do Starlette | 404/405/outros |
| `DBAPIError` | SQLSTATE `40001`/`40P01`/`55P03` → 503 `CONFLITO_CONCORRENCIA`. `57014` → 503 `TEMPO_ESGOTADO`. Demais → 500 |
| `Exception` | 500 `ERRO_INTERNO`, sem detalhes. Pilha apenas no log |

Mensagens exigidas literalmente pelos requisitos (por exemplo, 3.4.8, 3.4.10, 10.5.2 e 11.6.1) são devolvidas pela API. Mensagens de “campo obrigatório” específicas de tela ficam a cargo do cliente, a partir do código estável do campo.

**Detalhe:** arquitetura §4.4.

### D-09 — Modelo físico e migrações

**Decisão recomendada:**

- **Enumerações:** `sqlalchemy.Enum(EnumPython, native_enum=False, create_constraint=True, validate_strings=True, length=<comprimento do contrato>, name=<nome estável>)`. Os valores técnicos são iguais aos nomes dos membros (`StrEnum`). Sem ENUM nativo.
- Domínios numéricos (`antecedencia_dias`) e domínios dependentes de outra coluna (forma × tipo) usam `CheckConstraint` explícita.
- CHECKs de nome com 3 a 100 caracteres: `atividade.nome` (contrato) e, por DEC-MV-08 (aprovada em 2026-10-13), também `importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao`. Não é uma decisão deste ADR; está registrada aqui por afetar o modelo físico.
- **Convenção de nomes** no `MetaData`. Aceita em 2026-10-11 por DEC-MV-25, **somente** quanto a `CONVENCAO_NOMES` e `MetaData(naming_convention=CONVENCAO_NOMES)`, exatamente como na arquitetura §10.1 e no Prompt F1 §6. Os itens marcados “F2” foram aceitos em 2026-10-13 (DEC-MV-07):
  - `pk_%(table_name)s`
  - `uq_%(table_name)s_%(column_0_N_name)s`
  - `ck_%(table_name)s_%(constraint_name)s`
  - `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`
  - `ix_%(table_name)s_%(column_0_N_name)s`, padrão para índices sem nome explícito. Constava da arquitetura §10.1 e do Prompt F1 §6, mas faltava neste resumo até 2026-10-11 (ACH-MV-ARQ-025).
  - F2: índices com nomes explícitos e curtos (os oito iniciais estão na arquitetura §10).
  - F2: todo nome com no máximo 63 caracteres, verificado por teste.
- **Timestamps:**
  - `criado_em`/`criada_em`: `server_default=func.now()`.
  - `atualizado_em`: `server_default=func.now()` e `onupdate=func.now()`.
  - `__mapper_args__ = {"eager_defaults": True}`, para buscar os valores por `RETURNING` sem I/O tardio.
  - Atualizações por SQL textual não são permitidas nos services.
  - O mixin `CriadoAtualizadoMixin` é aplicado somente às 8 tabelas que têm as duas colunas.
- `JSON(none_as_null=True)` em `requisicao_idempotente.resposta`. `Numeric(12, 2, asdecimal=True)`. `Time(timezone=False)`. `DateTime(timezone=True)`.
- **Migrações:**
  - Alembic com template async (`run_sync`). `def upgrade()`/`def downgrade()` síncronos.
  - Diretório `alembic/` na raiz (já previsto no `pyproject`).
  - URL por `config.attributes["url_banco"]` (testes) ou pelas settings.
  - Suporte a `config.attributes["connection"]`.
  - **Uma migração inicial na F2 com as 13 tabelas e os 30 seeds.** Os seeds usam UUIDv7 gerado na execução e `ON CONFLICT DO NOTHING` sobre a chave natural, sem importar modelos vivos.
  - Sem `create_all`, sem `stamp` como prova e sem reescrever revisões aplicadas.
  - As revisões passam pelos mesmos gates do código: `alembic/` incluído no Ruff e no Pyright, com a exceção `PLC0415` restrita a `alembic/env.py` (ACH-MV-F1-005, opção A, aprovada em 2026-10-13; implementada na F2).
  - Downgrade destrutivo apenas em banco descartável. A recuperação em produção é feita por backup.

**Justificativa:** o contrato é fortemente interligado por FKs compostas. Criar as 13 tabelas de uma vez dá um esquema estável às fases de comportamento.

**Detalhe:** arquitetura §10.

### D-10 — Recorrência

**Decisão recomendada:**

- **Materialização sob demanda**, idempotente por `(serie_id, numero_ocorrencia)` com `INSERT … ON CONFLICT DO NOTHING`, sob a trava exclusiva do usuário. Ocorre antes de:
  - consultar um dia ou um mês;
  - calcular pendências e atrasos (todas as posições com data anterior a hoje);
  - buscar “próximas” (varredura limitada por série).
- **Leituras que materializam fazem commit.**
- Invariante: todas as posições anteriores a `numero_referencia` estão materializadas.
- Edição e exclusão por alcance usam a posição original (`numero_ocorrencia`).
- “Mais recentes” usa o momento de cadastro da série (REC-MV-021).
- Sem horizonte arbitrário nos totais. O horizonte de 12 meses vale apenas para a **listagem** de séries em Todos e Próximos (DEC-MV-18).

**Detalhe e pseudocódigo:** arquitetura §8.5.

### D-11 — Lembretes e notificações

**Decisão recomendada:**

- Processo separado: `uv run python -m api_gestao_pessoal.jobs.processar_lembretes`, em laço com intervalo de 60 s e `--uma-vez` para cron e testes.
- Cada ciclo tem duas etapas:
  - (1) materializar as ocorrências de séries com lembrete cuja data esteja em `[hoje, hoje + 8]` no fuso de cada usuário, com uma transação por série sob a trava do usuário;
  - (2) processar lotes de lembretes `PENDENTE` vencidos com `FOR UPDATE SKIP LOCKED`, revalidar a versão e a situação da importância, inserir a `notificacao` da versão e marcar `ENVIADO` com atualização condicional, tudo na mesma transação.
- `UNIQUE(lembrete_id, versao_agendamento)` garante uma notificação por versão.
- Push externo fora do escopo.
- Regra de lembrete atrasado: DEC-MV-20.

**Justificativa:** o estado é durável no banco (não há tarefa em memória), e o processamento concorrente entre instâncias é seguro.

**Detalhe:** arquitetura §8.6.

### D-12 — Leitura consistente e paginação

**Decisão recomendada:**

- Leituras compostas (lista + indicadores; resumo financeiro; blocos do painel) ocorrem numa transação que detém a trava do usuário: compartilhada, ou exclusiva se houver materialização.
- Como todo escritor precisa da trava exclusiva, as várias instruções em `READ COMMITTED` enxergam um estado estável do usuário.
- Totais sempre calculados sobre o universo completo dos filtros, por consulta agregada separada da página.
- Paginação **keyset** com cursor opaco (base64url de JSON com as chaves de ordenação e o `id` como desempate final). Não há duplicação nem salto quando há escritas entre páginas.
- O `id` (UUIDv7) é usado **apenas** como desempate estável, nunca como contrato cronológico.

**Detalhe:** arquitetura §4.1 e §6.4.

### D-13 — Tempo e fuso

**Decisão recomendada:**

- Protocolo `Relogio` com `agora() -> datetime` (UTC, com fuso), injetado por dependência. Os testes usam `RelogioFixo`.
- `ContextoUsuario(usuario_id, fuso: ZoneInfo, agora, hoje)` é montado **uma vez por requisição**, com `hoje = agora.astimezone(fuso).date()`.
- Datas civis (`DATE`) são comparadas sem conversão.
- Instantes de negócio (`concluida_em`, `expira_em`, `agendado_para` etc.) vêm do relógio da aplicação.
- `criado_em`/`atualizado_em` vêm do banco (`now()`, início da transação).

**Detalhe:** arquitetura §7.

### D-14 — Política de testes

**Decisão recomendada:**

- PostgreSQL real via Testcontainers (`testcontainers.community.postgres.PostgresContainer("postgres:15-alpine", driver="psycopg")`), um container por sessão de pytest, iniciado por fixture **síncrona**. Isso permite o `asyncio.run` do `env.py` sem loop ativo.
- Engines de teste por função, com `NullPool`, salvo nos testes de pool.
- Guarda de banco descartável antes de qualquer operação destrutiva.
- Testes de concorrência com conexões independentes e coordenação determinística (eventos e travas, não `sleep`).
- Seleções explícitas por fase. Suíte completa somente como exceção justificada.
- Verificação de Ruff com `--no-fix`/`--check`.

**Detalhe:** `docs/arquitetura/plano_validacao_auditoria.md`.

### D-15 — Envio de e-mail

**Decisão recomendada:**

- Protocolo `EnviadorEmail` com implementações `EnviadorEmailSmtp` (biblioteca padrão `smtplib` + `email.message`, executada por `anyio.to_thread.run_sync`) e `EnviadorEmailMemoria` (testes; proibida em `producao`).
- Segurança por `SMTP_SEGURANCA`: `starttls` (padrão, porta 587), `tls` (TLS implícito, 465) ou `nenhuma` (só fora de produção). TLS com `ssl.create_default_context()`, que verifica certificado e nome; credenciais só com TLS. `SMTP_TIMEOUT_S` (10 s) vale por operação de socket. Toda exceção de SMTP ou de socket vira `FalhaEnvioEmail`, sem dados pessoais.
- O envio ocorre **dentro da transação, antes do commit**. O PostgreSQL não desfaz um e-mail; as consequências aceitas na DEC-MV-12 são:

| # | Situação | Banco | E-mail | Resposta | O que o usuário vê |
| --- | --- | --- | --- | --- | --- |
| 1 | Falha antes do envio (conexão, DNS, TLS, autenticação) | Rollback | Não enviado | 503 `FALHA_ENVIO_EMAIL` | Pode repetir na hora: o intervalo conta da última emissão **confirmada** |
| 2 | Erro ou timeout durante o envio | Rollback | Indeterminado: pode ter chegado | 503 `FALHA_ENVIO_EMAIL` | Pode receber um código que não vale; o próximo pedido gera um código válido |
| 3 | O servidor SMTP aceitou, mas a confirmação se perdeu | Rollback | Entregue | 503 | Recebe um código que não vale |
| 4 | Envio concluído e commit falhou | Rollback | Entregue | 5xx (mapeamento de D-08) | Recebe um código que não vale. Se havia uma emissão confirmada anterior, aquele código antigo **continua** válido e o intervalo conta dela |
| 5 | Cancelamento da requisição durante a thread de envio | Rollback (sem commit) | Pode ser concluído | Nenhuma resposta útil ao cliente | Pelo cancel scope do anyio, o envio termina antes de o cancelamento propagar. Pelo cancelamento nativo, a thread segue sozinha |
| 6 | Outra solicitação do mesmo usuário espera a trava durante o envio | — | — | Espera até `lock_timeout` (5 s). Se o envio demorar mais, 503 `CONFLITO_CONCORRENCIA` com `Retry-After: 1` | Repetir. Em geral, a segunda tentativa recebe 429 do intervalo |

- Sem fila nem outbox (não há requisito de entrega garantida).

### D-16 — Dinheiro na API

**Decisão recomendada:**

- Valores monetários trafegam como **string** decimal com ponto: `"1234.56"`.
- Entrada: regex `^\d{1,10}(\.\d{1,2})?$`, valor maior que 0. Número JSON é rejeitado. Não há arredondamento.
- Saída: sempre duas casas.
- Somas em `Decimal`, a partir de `SUM(numeric)` do PostgreSQL.
- Variação percentual com uma casa, `ROUND_HALF_UP`.

---

## 4. Impacto nos contratos

| Área | Impacto |
| --- | --- |
| Dados | ADR-0002 (UUID). D-09 (convenções). Valor `DESATIVADO` em lembrete, sujeito a DEC-MV-19 |
| HTTP | Prefixo `/api/v1`. Bearer. `Idempotency-Key`. Cursor keyset. Dinheiro como string. Erro único |
| Transações | D-04, D-05 e D-12 |
| Testes | D-14. Catálogo de casos de teste (CT) por fase |

## 5. Plano de adoção e reversibilidade

- **F1:** D-01 a D-04, D-08 e D-14 (aceitas), incluindo o ambiente Alembic sem revisões (ver nota em §3), e a convenção de nomes de D-09 (aceita por DEC-MV-25).
- **F2:** D-09 e ADR-0002.
- **F3:** D-07, D-13 e D-15.
- **F4:** D-05, D-06 e D-12.
- **F5:** D-10.
- **F6:** D-16.
- **F7/F8:** D-10 e D-11 (agendamento).
- **F9:** D-11.

Reversibilidade:

- D-05 pode evoluir para travas de linha sem mudar o esquema.
- D-07 pode receber refresh token futuramente, com tabela própria e nova aprovação.
- D-09 (UUID) é **irreversível depois de haver dados**. Por isso, a ratificação ocorre antes da F2.

## 6. Critérios de verificação

Os CTs listados em `plano_validacao_auditoria.md` §4 para cada decisão, em especial:

- CT-F1-10 a CT-F1-14 (transações);
- CT-F4-01 a CT-F4-12 (trava e idempotência);
- CT-F5-20 a CT-F5-29 (recorrência);
- CT-F9-01 a CT-F9-08 (lembretes).

## 7. Aprovação

O estado muda para ACEITO **por decisão**, mediante aprovação explícita do usuário, registrada em `docs/arquitetura/indice.md` §4 com data e escopo.

- Aceitas em 2026-10-11: D-01, D-02, D-03, D-04, D-08 e D-14 (DEC-MV-01 a 04). DEC-MV-05 (higiene da F1) não corresponde a uma decisão deste ADR.
- Aceita parcialmente em 2026-10-11: D-09, somente no item “convenção de nomes” (`CONVENCAO_NOMES` e `MetaData(naming_convention=CONVENCAO_NOMES)`), por DEC-MV-25.
- Aceita no restante em 2026-10-13: D-09 (enums, timestamps, `eager_defaults`, `CriadoAtualizadoMixin`, JSON, nomes de até 63 caracteres, migração inicial e seeds), por DEC-MV-07. Com isso, D-09 está aceita integralmente.
- Uma decisão aceita alcança as seções de detalhe que ela cita somente na parte que detalha essa decisão. Partes dessas seções que servem a fases posteriores (por exemplo, as variáveis de F3 e F9 em arquitetura §3.1) seguem as decisões dessas fases.
- Aceitas em 2026-10-13: D-07 e D-13, por DEC-MV-09 (R9.1 a R9.9 do dossiê da F3), e D-15, por DEC-MV-12, com os diffs AD-1 e AD-2.
- Aceita parcialmente em 2026-10-13: D-05, somente nas travas de linha da recuperação usadas pela F3 (`SELECT … FOR UPDATE` em `recuperacao_senha`, `INSERT … ON CONFLICT` na primeira emissão, `READ COMMITTED`), por DEC-MV-14 em escopo limitado (diff AD-3). A trava consultiva por usuário, os modos exclusivo e compartilhado e o restante de D-05 continuam PROPOSTOS.
- As demais decisões continuam PROPOSTAS. O ADR não está aceito como um todo.
