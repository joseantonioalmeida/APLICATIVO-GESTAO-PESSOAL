# Plano de validação e auditoria — API MinhaVida

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/plano_validacao_auditoria.md` |
| Estado | **PARCIALMENTE ACEITO** em 2026-10-11 (DEC-MV-04): política de testes (§2, §3 e §5) e catálogo da F1 (§4). As demais seções e os catálogos das outras fases seguem PROPOSTOS, com as decisões de cada fase. Em 2026-10-13, o catálogo da F2 passou a valer com DEC-MV-06 a 08, e §3.4 foi precisado (REC-MV-034). Ainda em 2026-10-13, o catálogo da F3 passou a valer com DEC-MV-09 a 13 e DEC-MV-14 em escopo limitado, com o PV-1 do dossiê da F3 (M16) |
| Data | 2026-10-10. Atualizado em 2026-10-11 (CT-F6-14, nome da F8, §6 e §9) e em 2026-10-13 (§3.4, CT-F1-17 e catálogo da F2; depois da auditoria da F2, texto do CT-F2-07 conforme a emenda F2-D1; nota de proposta no catálogo da F3; depois, catálogo da F3 conforme o PV-1) |
| Relacionados | ADR-0001 D-14, `plano_fases_api.md`, `matriz_requisitos_api.md` |

> Todos os testes, comandos e resultados deste documento são **PLANEJADOS**. Nenhum foi executado na F0.

---

## 1. Objetivo

Definir:

- como cada fase prova o que entrega;
- quais testes executar e em que ordem;
- como o banco e a concorrência são testados;
- quais evidências o implementador entrega;
- como o Opus audita sem alterar o objeto auditado.

---

## 2. Política de testes

### 2.1. Suíte completa é exceção

**Não executar a suíte completa automaticamente** em implementação, correção, hardening, auditoria, microcorreção ou fechamento de subetapa. Os Prompts Master não prescrevem `pytest` sem seleção nem `task test` (que roda tudo e aplica `ruff --fix`, ACH-MV-ARQ-009).

Ordem normal de validação de uma fase:

1. Testes da etapa (arquivos e node IDs da fase).
2. Testes dos arquivos alterados que ainda não foram cobertos pela execução anterior.
3. Regressões diretamente afetadas (listadas na ficha da fase).
4. Stress e concorrência específicos exigidos pelo contrato (marcador `concorrencia`). Normalmente já estão incluídos no item 1, sem repetição.
5. Ruff (verificação), formatação (verificação) e Pyright.
6. Alembic e checagens estruturais pertinentes.

Preparar o schema de teste por migração é pré-requisito dos testes de banco. Isso não obriga a repetir a bateria no gate estrutural final. Seleções sobrepostas são unidas, e evidências válidas do **mesmo conteúdo** são reaproveitadas.

Para propor uma suíte completa, o formulário abaixo é obrigatório:

```text
OBJETIVO DA SUÍTE COMPLETA:
<invariante ou risco concreto a verificar>

POR QUE OS TESTES DIRECIONADOS NÃO SÃO SUFICIENTES:
<lacuna demonstrada, não hipótese genérica>

MUDANÇAS QUE JUSTIFICAM A EXECUÇÃO:
<arquivos, contratos e dependências afetados>
```

- A execução precisa estar vinculada ao plano de validação autorizado.
- Se ampliar o plano, apresentar a ampliação e o motivo **antes** de executar.
- Justificativas inválidas: “para garantir”, “por segurança”, “porque terminou”, “porque é importante” e “porque normalmente fazemos”.

### 2.2. Procedimento ao falhar

Teste específico → correção autorizada → mesmo teste novamente → testes da etapa → ampliação somente diante de risco concreto. Baterias grandes não são reiniciadas por rotina.

### 2.3. Verificação documental (F0)

Na F0, as verificações são documentais:

- consistência de IDs e referências cruzadas;
- cercas de código balanceadas;
- contagens do contrato.

Nenhum teste de implementação é executado para criar impressão de aprovação.

---

## 3. Infraestrutura de testes

### 3.1. Estrutura (PLANEJADA)

```text
tests/
├── __init__.py
├── conftest.py              F1: container, guarda, settings, engine, app, cliente
├── apoio/                   F1+: utilitários de teste (concorrência, relógio, fábricas de dados)
│   ├── __init__.py
│   ├── banco.py             garantir_banco_descartavel, aguardar_bloqueio, limpar_dados
│   └── rotas_teste.py       F1: router exclusivo de testes de transação
├── infra/                   F1
├── esquema/                 F2
├── identidade/              F3
├── nucleo/                  F4
├── atividades/              F5 (test_recorrencia_calculo.py é puro, sem banco)
├── financeiro/              F6
├── importancias/            F7
├── pagamentos/              F8
├── lembretes/               F9
├── painel/                  F10
└── integracao/              F11
```

### 3.2. PostgreSQL real via Testcontainers

- Importação: `from testcontainers.community.postgres import PostgresContainer`. O módulo `testcontainers.postgres` está deprecado na 4.15.
- Container: `PostgresContainer("postgres:15-alpine", username="minhavida", password=<gerada com secrets.token_urlsafe(16) na fixture>, dbname="minhavida_teste", driver="psycopg")`. Parâmetros explícitos, porque o container leria `POSTGRES_USER`/`POSTGRES_DB` do ambiente se omitidos.
- A imagem é a mesma do `compose.yaml` (DEC-MV-23). O relatório registra o digest com `docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine`.
- Escopo: **um container por sessão de pytest**, em fixture **síncrona** (`scope="session"`). Isso permite migrar com a API do Alembic sem loop ativo (o `asyncio.run` do `env.py`).
- Engines de teste: por função, com `NullPool` (evita compartilhar conexões entre loops de eventos). A exceção é o teste de pool (CT-F1-14), com pool real.
- Docker ausente ou container que não sobe: os testes de banco **falham** com mensagem clara. Não são pulados (REC-MV-015).

### 3.3. Guarda de banco descartável

`tests/apoio/banco.py::garantir_banco_descartavel(url, container)` é chamada antes de qualquer `TRUNCATE`, `DROP`, `downgrade` ou limpeza. Exige:

- host e porta iguais aos expostos pelo objeto do container;
- `dbname == "minhavida_teste"`;
- URL obtida do container, nunca de variável de ambiente.

Um nome contendo “test” não é prova suficiente. A guarda é testada (CT-F1-20).

### 3.4. Isolamento

| Modo | Uso | Mecanismo |
| --- | --- | --- |
| Commit real + limpeza | Testes de transação, concorrência, HTTP e serviços (padrão a partir da F1) | Engine própria. Ao fim, `limpar_dados()`: um único `TRUNCATE` com a lista explícita das tabelas que não são catálogo, **sem** `RESTART IDENTITY` (não há identidades, ADR-0002) e **sem** `CASCADE` (uma lista incompleta falha, em vez de apagar outra tabela), preservando catálogos e `alembic_version`. Sempre com guarda. *Precisado em 2026-10-13 (REC-MV-034)* |
| Transação revertida (F2+) | Testes de restrição e de introspecção que não confirmam transação | Conexão própria, com transação aberta pela fixture e revertida ao fim do teste. Cada violação esperada roda dentro de `SAVEPOINT` (`begin_nested`), para a transação continuar utilizável. *Acrescentado em 2026-10-13 (REC-MV-034)* |
| Esquema auxiliar de infraestrutura (F1) | Testes de sessão e transação antes de existirem tabelas | Schema `teste_infra`, criado pela fixture, fora do metadata e do Alembic. Evita ruído no `alembic check` |
| Esquema de domínio (F2+) | Todas as fases com tabelas | `alembic upgrade head` uma vez por sessão (fixture síncrona), seguido da limpeza por teste |

Não se usa `create_all` nem `drop_all`.

### 3.5. Concorrência determinística

- Cada participante usa **sua própria engine e conexão**, ou requisições HTTP separadas, cada uma com sua sessão. `asyncio.gather` sobre uma única `AsyncSession` não é teste válido.
- **Portão de largada:** uma conexão “bloqueadora” obtém `pg_advisory_lock` com a mesma chave da trava do usuário (§6.1 da arquitetura). As transações A e B são iniciadas. O teste usa `aguardar_bloqueio(monitor, quantidade=2, timeout=5)`, que consulta `pg_stat_activity` até que `wait_event_type = 'Lock'` para as duas. Depois a bloqueadora libera, e os efeitos finais são verificados.
- Para recursos com trava de linha (recuperação e lembretes), a mesma técnica usa `SELECT … FOR UPDATE` na conexão bloqueadora.
- **Sem `sleep` como sincronização.** Esperas usam polling com timeout explícito (falha clara em 5 s).
- Verificação final sempre por consulta ao banco com **outra conexão**: contagem de linhas, valores e situação. Não basta olhar status HTTP.

### 3.6. Tempo controlável

- `RelogioFixo` injetado (`app.dependency_overrides[obter_relogio]`, ou parâmetro dos services e jobs).
- Nenhum teste calcula “hoje/amanhã” na importação do módulo.
- Casos obrigatórios: virada de dia e de mês (31/10 → 01/11), fuso diferente de UTC perto da meia-noite, 29/02, meses de 28, 29, 30 e 31 dias.

### 3.7. Marcadores

| Marcador | Significado | Situação |
| --- | --- | --- |
| `concorrencia` | Teste com transações concorrentes | Novo (F1, em `pyproject.toml`) |
| `performance` | Orçamento de tempo com volume grande, fora da seleção padrão (`addopts -m 'not performance'`) | Existente |

`pytest-xdist` não é usado nos gates, para não alterar a semântica do container de sessão.

---

## 4. Catálogo de casos de teste (CT)

Formato: `CT-F<fase>-<nn>`. **c** = marcador `concorrencia`. Arquivos previstos entre parênteses.

### F1 — Fundação técnica (`tests/infra/`)

| ID | Caso | Expectativa |
| --- | --- | --- |
| CT-F1-01 | `Settings` (`test_configuracao.py`) | Sem `DATABASE_URL` → `ValidationError`. Esquema diferente de `postgresql+psycopg://` → erro **sem** o valor na mensagem. Padrões conforme arquitetura §3.1 |
| CT-F1-02 | Importação sem efeitos (`test_configuracao.py`) | Subprocesso com ambiente sem `DATABASE_URL` e `cwd` vazio importa `api_gestao_pessoal.main`, `.database` e `.models` com código de saída 0 |
| CT-F1-03 | Cache e injeção (`test_configuracao.py`) | `obter_settings()` retorna o mesmo objeto. `criar_app(settings)` usa as settings injetadas no lifespan |
| CT-F1-04 | `GET /saude` (`test_saude.py`) | 200 `{"situacao":"ativo"}` sem banco |
| CT-F1-05 | `GET /saude/pronto` com banco | 200 `{"situacao":"pronto"}` |
| CT-F1-06 | `GET /saude/pronto` com banco inacessível | 503 `SERVICO_INDISPONIVEL` em ≤ 3 s |
| CT-F1-07 | `ErroNegocio` (`test_erros.py`) | Status e JSON do catálogo. `id_requisicao` igual ao cabeçalho. `campos`/`detalhes` preservados. Cabeçalhos extras aplicados |
| CT-F1-08 | Validação 422 | `codigo = VALIDACAO`. `campos[].campo/codigo/mensagem` mapeados. Valor sensível enviado **ausente** do corpo da resposta. JSON malformado → `CORPO_INVALIDO` |
| CT-F1-09 | 404, 405 e 500 | Formato padrão. Exceção não tratada → 500 `ERRO_INTERNO` sem detalhes. Log com traceback e `id_requisicao` (cliente com `raise_app_exceptions=False`) |
| CT-F1-10 | Commit no router (`test_sessao_transacao.py`) | Registro visível por outra conexão |
| CT-F1-11 | `ErroNegocio` após `flush` | Nada persiste |
| CT-F1-12 | Dependência consulta antes do endpoint | Autobegin seguido do commit do router com sucesso. Dependência e endpoint usam o **mesmo** objeto de sessão |
| CT-F1-13 | Falha no commit (constraint `DEFERRABLE INITIALLY DEFERRED`) | Resposta 500 (nunca 2xx). Nada persiste |
| CT-F1-14 | Devolução de conexões ao pool | Após requisições com sucesso e com erro, `engine.pool.checkedout() == 0` |
| CT-F1-15 **c** | `lock_timeout` | Com `DB_LOCK_TIMEOUT_MS = 200` e outra conexão segurando `pg_advisory_lock(k)`: endpoint de teste → 503 `CONFLITO_CONCORRENCIA` com `Retry-After` |
| CT-F1-16 | `X-Request-ID` | Valor válido é propagado. Ausente ou inválido → gerado (hex de 32) |
| CT-F1-17 | Alembic sem revisões (`test_alembic_ambiente.py`) | `command.upgrade(cfg, "head")` em contexto síncrono. `ScriptDirectory.get_heads() == []`. `command.check(cfg)` sem diferenças. **A partir da F2:** `get_heads() == ["0001"]`, no teste renomeado `test_upgrade_head_com_revisao_inicial` |
| CT-F1-18 | Alembic com `config.attributes["connection"]` | A partir de teste async com `await conn.run_sync(...)`, sem erro de loop aninhado |
| CT-F1-19 | `env.py` | Não contém `api_gestao_pessoal.main` nem URL literal. `alembic.ini` sem `sqlalchemy.url` preenchido |
| CT-F1-20 | Guarda de banco descartável | URL que não pertence ao container → `RuntimeError` antes de qualquer comando |
| CT-F1-21 | Log do 500 de banco sem valores (`test_sessao_transacao.py::test_erro_banco_500_sem_valores_no_log`, REG-F1-01) | Violação UNIQUE diferida no `COMMIT` e violação NOT NULL no `INSERT`, com sentinelas sintéticas → 500 `ERRO_INTERNO`. A saída formatada com o `FORMATO_LOG` real e o `caplog.text` não contêm as sentinelas nem `DETAIL`, e a resposta também não. Controle positivo: o registro existe e contém `sqlstate`, o identificador esperado (`restricao=…` ou `coluna=…`) e `[id_requisicao]` |
| CT-F1-22 | `settings_teste` hermética (`test_configuracao.py::test_settings_teste_ignora_ambiente_e_env`, REG-F1-02) | `.env` sintético em `tmp_path` e variáveis alteradas. Controle positivo: o `Settings` de produção absorve os valores. A fixture mantém os padrões. Asserção **estrutural**: `type(s).model_config.get("env_file") is None`. A ausência de abertura do `.env` não é provada pelo teste: é provada por **sonda comportamental** (audit hook) na auditoria |

> CT-F1-21 e CT-F1-22 foram acrescentados em 2026-10-11 (P-DOC-04), com aprovação do usuário, a partir das regressões REG-F1-01 e REG-F1-02 (`docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` e `docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md`).

### F2 — Esquema de dados (`tests/esquema/`)

| ID | Caso |
| --- | --- |
| CT-F2-01 | `upgrade head` em banco vazio → revisão inicial aplicada. 13 tabelas de domínio e `alembic_version` |
| CT-F2-02 | Introspecção das 134 colunas (nome, tipo, comprimento, precisão/escala, nulabilidade, `server_default`) contra uma **expectativa literal** escrita a partir do contrato no próprio teste. Não vale comparar o metadata consigo mesmo |
| CT-F2-03 | 32 colunas `uuid`. PKs sem `column_default` |
| CT-F2-04 | Inserção pelo ORM gera `uuid.UUID` com `version == 7` |
| CT-F2-05 | SQL textual sem `id` → SQLSTATE `23502` |
| CT-F2-06 | 30 categorias exatas (grafia, acentos e separação por catálogo e tipo), todas ativas |
| CT-F2-07 | Segundo `upgrade head` inócuo. Reexecução das instruções de `instrucoes_categorias()` da revisão não duplica. O módulo da revisão não importa `api_gestao_pessoal` |
| CT-F2-08 | `downgrade base` seguido de `upgrade head` no container (com guarda) |
| CT-F2-09 | `alembic check` sem diferenças |
| CT-F2-10 | Nomes de constraints e índices ≤ 63 e idênticos entre metadata e banco, iguais à lista literal de 93 nomes do Prompt F2. Oito índices com a ordem exata de colunas |
| CT-F2-11 | Cinco FKs compostas de propriedade: proprietário correto aceito, outro usuário rejeitado (`23503`) |
| CT-F2-12 | Categoria financeira × tipo (`23503`). “Outros” existe em ambos os tipos como registros distintos |
| CT-F2-13 | Ocorrências: várias avulsas. Par incompleto e número < 1 → `23514`. Duplicata → `23505`. Exclusão lógica não libera o par. `numero_final = 0` aceito |
| CT-F2-14 | Condições financeiras, com casos `NULL`: valor ≤ 0; valor previsto condicional; par de vínculo; receita vinculada; dois pagamentos; excluída com vínculo |
| CT-F2-15 | Domínios: forma × tipo; horários; datas e números de série; nome 3–100 (atividade); prioridade e periodicidade inválidas; antecedência; situação × `enviado_em`; conclusão manual com despesa. Sempre com controles positivos |
| CT-F2-16 | Unicidades de apoio: recuperação por usuário; tokens únicos com vários nulos; lembrete por importância; notificação por versão; versões antigas válidas após mudar a versão do lembrete; idempotência por `(usuario, acao, chave)` |
| CT-F2-17 | `Decimal` (0.01 e 9999999999.99) em ida e volta. `resposta = None` → SQL `NULL` (não JSON `null`) |
| CT-F2-18 | Exclusão física de categoria referenciada → `23503`. Todas as FKs com `confdeltype = 'r'` |
| CT-F2-19 | Timestamps preenchidos. `atualizado_em` muda no update do ORM e é legível sem I/O tardio (`eager_defaults`). `notificacao.criada_em` presente. UPDATE em SQL textual não altera `atualizado_em` (arquitetura §10.3.1) |
| CT-F2-20 | CHECKs extras de nome (DEC-MV-08, aprovada em 2026-10-13): `importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao` |

### F3 — Identidade e acesso (`tests/identidade/`)

> **Vigente desde 2026-10-13 (M16):** textos refinados e CT-F3-22 a 24 e 26 a 29 conforme o PV-1 do dossiê da F3. Cenários, preparação e asserções detalhadas estão no dossiê (`docs/arquitetura/preparacao_f3_identidade_acesso.md` §7.2) e no Prompt F3 §11.3. **c** = concorrência, com a espera exata por trava (`aguardar_espera_por_trava`).

| ID | Caso |
| --- | --- |
| CT-F3-01 | Registro válido (e-mail com maiúsculas e espaços) → 201 com os 5 campos exatos. E-mail na forma canônica (R9.9). Hash Argon2id (`$argon2id$`), conferido por outra conexão. Resposta sem hash |
| CT-F3-02 | Validações do registro → 422 com `campos[].codigo` exato, sem eco e sem gravação: senha curta, vazia ou ausente (3.4.10), > 128, confirmação diferente (3.4.14); e-mail inválido, com parte local não ASCII ou `@localhost`; nascimento futuro **no fuso informado**; fuso `localtime`, com `..` ou inexistente; nome vazio ou com caractere de controle; `data_nascimento` fora de `AAAA-MM-DD` válido (`DATA_INVALIDA`) |
| CT-F3-03 | E-mail duplicado (com maiúsculas e espaços) → 409. Variantes de um domínio internacionalizado (Unicode composto, decomposto e punycode) → 409. Uma linha |
| CT-F3-04 | Login válido → claims exatas `{sub, iat, exp, typ, sv}`, `exp − iat` igual à validade, `expira_em` igual a `exp` (ISO com `Z`) e `Cache-Control: no-store`. Também com o e-mail digitado em outra variante |
| CT-F3-05 **c** | Dois registros simultâneos com o mesmo e-mail → um 201 e um 409. Uma linha no banco |
| CT-F3-06 | Login com e-mail inexistente, e-mail malformado ou senha errada → mesma resposta 401 `CREDENCIAIS_INVALIDAS`, com verificação fictícia nos dois primeiros |
| CT-F3-07 | Token ausente, esquema diferente, malformado, com mais de 4096 caracteres, assinatura errada, `alg: none`, `typ` errado, `sub` inexistente ou não canônico, claim extra, `iat` booleano, `iat` no futuro ou expirado (pelo `RelogioFixo`) → 401 `NAO_AUTENTICADO` com `WWW-Authenticate: Bearer` |
| CT-F3-08 | `GET /usuarios/me` → os 5 campos do próprio usuário |
| CT-F3-09 | Solicitar código → e-mail no `EnviadorEmailMemoria` com assunto e corpo 3.4.4 e destinatário na forma canônica. Código de 8 dígitos preservando zeros (gerador forçado a `00012345`). Só o hash é gravado; `expira_em` = relógio + 10 min |
| CT-F3-10 | E-mail não cadastrado → 404 `EMAIL_NAO_ENCONTRADO` com a mensagem 3.4.2 (DEC-MV-10, opção A). Nenhum envio; nenhuma linha |
| CT-F3-11 | Reenvio em +59 s → 429 com `Retry-After: 1`, linha inalterada. Em +60 s → 200 e, logo em seguida, tentativas zeradas, verificação, token e uso limpos e código novo. O código antigo → 400 e conta uma tentativa na emissão nova; o novo → 200. Um token emitido antes do reenvio → 400 na redefinição |
| CT-F3-12 | Verificar: correto → token. Incorreto → 400 (mensagem 3.4.8) **e** `tentativas + 1` persistido. A 5ª inválida → 400; a 6ª, mesmo correta → 429 com `Retry-After`. Expirado → 400 `CODIGO_EXPIRADO`. Dígitos não ASCII → 422 `CODIGO_FORMATO` |
| CT-F3-13 | Verificar de novo após sucesso → 409, sem novo token |
| CT-F3-14 **c** | Duas verificações corretas simultâneas → uma 200 e uma 409. Um token |
| CT-F3-15 **c** | Cinco verificações inválidas, comprovadamente simultâneas (espera exata de 5 antes de liberar) → cinco 400 e `tentativas == 5` exato. A sexta, com o código correto → 429 |
| CT-F3-16 | Redefinir → senha nova funciona, a antiga não, `utilizado_em` preenchido, mensagem 3.4.15. JWT anterior → 401 (`sv`) |
| CT-F3-17 **c** | Duas redefinições simultâneas com o mesmo token → uma 200 e uma 400. Uma troca |
| CT-F3-18 | Token expirado (em `expira_em`), usado ou inexistente → 400. Senhas diferentes → 422 `SENHAS_DIFERENTES`. Nova senha curta → 422 `SENHA_FRACA` |
| CT-F3-19 **c** | Reenvio × verificação do código antigo, nas duas ordens → resultado de uma ordem serial. Depois do reenvio confirmado, o código antigo é inválido |
| CT-F3-20 | Falha do envio de e-mail, na primeira emissão e num reenvio → 503 `FALHA_ENVIO_EMAIL`. Linha de recuperação inexistente ou inalterada. Repetição imediata permitida |
| CT-F3-21 | “Hoje” no fuso: relógio às 02:30Z com `America/Sao_Paulo` → data local do dia anterior; `agora` igual ao relógio |
| CT-F3-22 | Settings da F3: segredo com 31 e 32 bytes (inclusive multibyte), placeholder do `.env.exemplo`, faixas, `memoria` e `nenhuma` em `producao`, credenciais sem TLS, SMTP ausente com `smtp` e piso do Argon2 em `producao` → `ValidationError` sem o valor do segredo; valores válidos aceitos |
| CT-F3-23 **c** | Duas **primeiras** solicitações simultâneas → um 200 e um 429. Uma linha; uma mensagem |
| CT-F3-24 | Limites exatos: código válido em `expira_em − 1 s` e expirado em `expira_em`; reenvio em +59 s e +60 s; JWT válido em `exp − 1 s` e 401 em `exp` e em `iat − 1 s` |
| CT-F3-25 | Respostas com exatamente os campos permitidos por endpoint (dossiê da F3 §6.5). Sentinelas (senha, nova senha, e-mail, nome, código e tokens) só nesses campos e ausentes de respostas de erro, de `caplog` e da saída formatada do logger real, inclusive com exceções |
| CT-F3-26 | Commit que falha depois do envio → 5xx; mensagem enviada; banco inalterado; nova solicitação permitida |
| CT-F3-27 **c** | Reenvio × redefinição, nas duas ordens → resultado de uma ordem serial. Depois do reenvio confirmado, o token → 400 |
| CT-F3-28 | `EnviadorEmailSmtp` com `smtplib` simulado: TLS com verificação (`starttls` e `tls`), `ehlo` depois de `starttls`, `login` só com credenciais, `timeout` e fechamento; `SMTPRecipientsRefused` → `FalhaEnvioEmail` sem o endereço na exceção nem no log. Texto exato da mensagem 3.4.4 |
| CT-F3-29 | `HasherSenha`: parâmetros de produção (prefixo `$argon2id$v=19$m=65536,t=3,p=4$`), verificação certa e errada, hash corrompido → `HashArmazenadoInvalido`; limitador de 2 vagas com 5 chamadas → no máximo 2 simultâneas; login não regrava o hash |
| CT-F3-30 | `obter_do_usuario_ou_404` (rota de teste): UUID de outro usuário → 404. UUID malformado → 422. O próprio → 200 |

### F4 — Núcleo transacional compartilhado (`tests/nucleo/`)

| ID | Caso |
| --- | --- |
| CT-F4-01 **c** | Trava EXCLUSIVA bloqueia outra EXCLUSIVA do mesmo usuário até o commit e não bloqueia outro usuário |
| CT-F4-02 **c** | COMPARTILHADA não bloqueia COMPARTILHADA. COMPARTILHADA × EXCLUSIVA bloqueia |
| CT-F4-03 | Reentrância é no-op. Promoção de COMPARTILHADA para EXCLUSIVA → `RuntimeError`. Registro em `sessao.info` limpo após commit e rollback |
| CT-F4-04 | Mesma chave com conteúdo diferente (sequencial) → 422 `CHAVE_IDEMPOTENCIA_REUTILIZADA` |
| CT-F4-05 **c** | Duas requisições simultâneas com a mesma chave e o mesmo conteúdo → um efeito. A segunda recebe replay idêntico (status e corpo) com `Idempotency-Replayed: true` |
| CT-F4-06 **c** | Simultâneas com a mesma chave e conteúdos diferentes → um efeito e um 422 |
| CT-F4-07 | Operação que lança `ErroNegocio` não grava registro. Nova tentativa com a mesma chave executa |
| CT-F4-08 | Chave ausente → 400 `IDEMPOTENCIA_CHAVE_AUSENTE`. Formato inválido → 400 `IDEMPOTENCIA_CHAVE_INVALIDA` |
| CT-F4-09 | Hash canônico: ordem de campos e espaços aparados geram o mesmo hash. `"100"` ≡ `"100.00"`. Parâmetros de caminho incluídos |
| CT-F4-10 | Resposta armazenada igual ao corpo 2xx, sem segredos. `codigo_resposta` e `concluida_em` preenchidos |
| CT-F4-11 | Paginação keyset: predicados corretos com direções mistas e desempate por `id`. Cursor adulterado ou de outros filtros → 422 `CURSOR_INVALIDO` |
| CT-F4-12 | Catálogos: somente ativas, “Outros” por último, financeiras por tipo, autenticação exigida |
| CT-F4-13 | Tipos comuns: `ValorMonetario` aceita `"0.01"` e `"9999999999.99"` e rejeita número JSON, `"1.234"`, `"0"`, `"-1"`, `"1e3"` e `"10000000000.00"`. `NomeTexto` apara e exige 3–100. Descrição vazia → `None`. Horário `HH:MM` |
| CT-F4-14 | Registro idempotente confirmado por outra transação sem trava (simulação de defeito) → `ON CONFLICT` detecta, sem reutilizar transação abortada |

### F5 — Atividades e recorrência (`tests/atividades/`)

| ID | Caso |
| --- | --- |
| CT-F5-01 | Criar avulsa → 201, Pendente, prioridade padrão BAIXA. Idempotência no cadastro |
| CT-F5-02 | Validações com mensagens literais (6.5.1, 6.5.2): nome vazio ou só espaços; categoria inexistente ou inativa; final ≤ inicial; data inexistente; descrição > 200 |
| CT-F5-03 | Sobreposição → 409 com conflitos. Com `confirmar_sobreposicao` → 201. As durações somam (5.2.5) |
| CT-F5-04 | Consulta do dia: itens, prévia de 30 caracteres + `…`, descrição ausente → `null`, `total_data` |
| CT-F5-05 | Indicadores 5.5.3 (90/60/30 min; 1 concluída → Total 3, Concluídas 1, Pendentes 2, 180 min). Depois de concluir mais uma → 3/2/1/180 |
| CT-F5-06 | Filtro de categoria (5.5.4). Filtros combinados. Busca sem diferenciar maiúsculas. `%` e `_` escapados |
| CT-F5-07 | Sem filtros → totais completos. `filtros_ativos` correto |
| CT-F5-08 | Ordenações estáveis. Prioridade com desempate por horário. Mudar a ordenação não altera totais |
| CT-F5-09 | 23 atividades com limite 10: os totais são 23 em todas as páginas. Inserção concorrente entre páginas não duplica nem salta itens |
| CT-F5-10 | Concluir e reabrir: `concluida_em` do relógio. Concluir de novo mantém. Futura pode ser concluída. Filtro Pendentes exclui após concluir |
| CT-F5-11 | Detalhes completos (5.1.8) |
| CT-F5-12 | Edição simples (5.5.6: 1h → 1h30, mais 30 min no total). Mudança de data recalcula as duas datas. Situação inalterada |
| CT-F5-13 | Excluir avulsa → some de listas e indicadores. Repetida → 204. Outro usuário → 404 |
| CT-F5-14 | Pendências anteriores independem dos filtros. `data_mais_antiga` correta. Não são transferidas para hoje |
| CT-F5-15 | Virada do dia com relógio: o padrão “hoje” muda. Consulta por `data` fixa não muda |
| CT-F5-20 | Cálculo puro (sem banco): diária, semanal, mensal 31/01 → 28/02 (ou 29/02) → 31/03, anual 29/02, NENHUMA, data final inclusiva, `numero_final = 0`, `primeira_posicao_em_ou_apos`, `ultima_posicao` |
| CT-F5-21 | Semanal de 08/10/2026 a 22/10/2026 → 08, 15 e 22 (6.5.5). Concluir a primeira não altera as demais (5.5.7) |
| CT-F5-22 | Materialização sob demanda em dia futuro e passado. Série sem fim não materializa além do consultado |
| CT-F5-23 | Excluir somente esta: não reaparece após nova consulta. Demais preservadas |
| CT-F5-24 **c** | Duas consultas simultâneas materializando a mesma série → uma linha por posição |
| CT-F5-25 **c** | Edição “esta e as próximas” concorrente com consulta materializadora → nenhuma ocorrência gerada pela regra substituída |
| CT-F5-26 **c** | Conclusão concorrente com exclusão “esta e as próximas” → resultado serial. Concluída preservada |
| CT-F5-27 **c** | Lista e indicadores coerentes durante escrita concorrente (antes ou depois, nunca misturados) |
| CT-F5-28 | Edição “esta e as próximas”: preserva anteriores, concluídas e exclusões. Muda a referência. Materializa as lacunas antes. A mudança de periodicidade exclui as posições eliminadas. Data final menor que a nova referência → 422 |
| CT-F5-29 | Exclusão “esta e as próximas”: `numero_final = k − 1` (`k = 1` → 0). Pendentes ≥ k excluídas. Concluídas preservadas. Futuras não geradas |
| CT-F5-30 | Concluída só pode ser editada ou excluída individualmente. Conversão avulsa → série |
| CT-F5-31 | “Mais recentes” usa `criado_em` da série, independentemente do momento da materialização |

### F6 — Financeiro (`tests/financeiro/`)

| ID | Caso |
| --- | --- |
| CT-F6-01 | Cadastrar receita → 201. Valores como string. Idempotência |
| CT-F6-02 | Validações da receita: mensagens 10.5.1 e 10.5.2, data futura no fuso, categoria de despesa → 422, forma incompatível |
| CT-F6-03 | Cadastrar despesa. Saldo negativo permitido (11.6.2). Data futura com a mensagem de 11.6.1 |
| CT-F6-04 | Resumo 2450.75 / 1230.40 → saldo 1220.35 (9.4.1) |
| CT-F6-05 | 0.10 + 0.20 = 0.30. Saldo 0.20 com despesa de 0.10 (9.4.3) |
| CT-F6-06 | Recebimento de setembro cadastrado em outubro compõe setembro. Editar a data para outubro move o valor, sem duplicar (9.4.2) |
| CT-F6-07 | Gráfico com 28, 29, 30 e 31 dias. Soma diária = totais. Soma das categorias = despesas (9.4.6) |
| CT-F6-08 | Comparação: mês encerrado. Mês atual parcial (31/03 × fevereiro). Mês futuro sem variação. Base zero (as duas mensagens). 1000 → 1100 = `"10.0"`. Arredondamento `HALF_UP` |
| CT-F6-09 | Lista: ordem data desc com empate por `criado_em` desc. Filtros de tipo, categoria e busca. Paginação |
| CT-F6-10 | Editar 100 → 120 sem duplicar (10.5.4). `tipo` imutável |
| CT-F6-11 | Excluir: some dos totais e listas. Repetida → 204 |
| CT-F6-12 | Categorias ordenadas por total. “Outros” como categoria própria |
| CT-F6-13 | Retry após perda da resposta não duplica. Nova chave com os mesmos dados cria outro lançamento (10.4.6) |
| CT-F6-14 | Exemplo de referência do usuário (arquitetura §1.1): receita de 3000.00 e despesas de 100.00, 50.00 e 200.00 no mesmo mês → `despesas = "350.00"` e `saldo = "2650.00"`. Editar a despesa de 50.00 para 80.00 → 380.00 e 2620.00. Excluir a de 200.00 → 180.00 e 2820.00. A resposta não tem campo de saldo editável |
| CT-F6-20 **c** | Resumo consistente durante escrita concorrente |

### F7 — Importâncias (`tests/importancias/`)

| ID | Caso |
| --- | --- |
| CT-F7-01 | Criar sem despesa e com despesa (99.90) sem alterar o saldo (8.6.3, 4.3.4) |
| CT-F7-02 | Validações 8.6.1 e 8.6.2. Valor com 3 casas. Lembrete sem horário |
| CT-F7-03 | Data passada → atrasada imediatamente (8.5.2) |
| CT-F7-04 | Lembrete 15/10, 3 dias antes, 09:00 → 12/10 09:00 local (8.6.5). Lembrete no passado → 422 (8.5.5) |
| CT-F7-05 | Filtros Todos (grupos e contagens), Vencendo hoje, Este mês e Mês selecionado, Próximos (inclui o próximo mês, 7.4.3), Concluídos (conclusão desc), Atrasados |
| CT-F7-06 | Virada do dia: pendente de hoje passa a Atrasados (7.4.2). Concluída fora de ambos |
| CT-F7-07 | Horário nulo por último. `prazo` e `dias_ate_vencimento` |
| CT-F7-08 | Concluir e reabrir sem despesa: sem efeito financeiro (7.4.4). Lembrete cancelado e reativado só se futuro |
| CT-F7-09 | `PUT situacao` em importância com despesa → 409 |
| CT-F7-10 | Mensal 31/01 → 28/02 → 31/03 (8.6.4). Anual 29/02 (8.5.4) |
| CT-F7-11 | Horizonte de 12 meses em Todos e Próximos. Avulsa além do horizonte aparece |
| CT-F7-12 | Edição com alcance e reagendamento de lembretes. Repetir o mesmo pedido não muda a versão |
| CT-F7-13 | Exclusão (somente esta / esta e próximas). Lembretes pendentes cancelados |
| CT-F7-14 | Lembrete desativado não é reativado na reabertura (DEC-MV-19) |
| CT-F7-15 | Busca com filtro. Contagens completas com paginação (7.2.7) |
| CT-F7-16 | Estados vazios: `possui_importancias` distingue “nenhum cadastro” de “nenhum resultado” (7.4.1) |
| CT-F7-17 **c** | Materialização concorrente da mesma série de importância |
| CT-F7-18 | `possui_despesa`: concluída manualmente → 409. Sim → Não limpa o valor |

### F8 — Vínculo interno entre despesas e importâncias (`tests/pagamentos/`)

| ID | Caso |
| --- | --- |
| CT-F8-01 | Despesa com `importancia_id` → Concluída/Pago. Previsão 99.90 preservada. Apenas 105.00 no financeiro (8.6.3, 11.6.3). Lembrete cancelado |
| CT-F8-02 | Vincular despesa existente de 105.00 → conclui sem alterar o total (11.6.4). Repetição → mesmo resultado |
| CT-F8-03 | Editar o valor vinculado de 105 para 100 → despesas −5 e pago = 100 (11.6.5). Mudar o mês transfere |
| CT-F8-04 | Excluir despesa vinculada → importância pendente (atrasada se vencida), lembrete futuro reativado, despesa fora dos totais (9.4.7, 11.6.7) |
| CT-F8-05 **c** | Dois pagamentos simultâneos → um 201 e um 409 `IMPORTANCIA_JA_PAGA`. Uma despesa |
| CT-F8-06 **c** | Mesma despesa vinculada a duas importâncias simultaneamente → um sucesso e um 409 |
| CT-F8-07 **c** | Exclusão de movimentação concorrente com vínculo → estado final coerente |
| CT-F8-08 **c** | Exclusão de importância concorrente com pagamento → nunca há vínculo com importância excluída |
| CT-F8-09 **c** | Troca de vínculo A → B atômica, sem deadlock com troca concorrente |
| CT-F8-10 | Remover vínculo exige confirmação. Despesa mantida nos totais. Importância reaberta (11.6.7) |
| CT-F8-11 | Excluir importância paga preserva a despesa e seus efeitos. Notificações antigas legíveis (7.4.5) |
| CT-F8-12 | Vínculo inválido: receita; sem despesa; excluída; de outro usuário (404); já paga (409 com `movimentacao_id`) |
| CT-F8-13 | Falha injetada após `flush` → nenhuma parte aplicada (11.6.6) |
| CT-F8-14 | Importâncias disponíveis para pagamento e despesas disponíveis para vínculo |
| CT-F8-15 | Categoria financeira sugerida (correspondência por nome; “Pessoal” sem sugestão) |
| CT-F8-16 | `possui_despesa` com pagamento → 409 |

### F9 — Lembretes e notificações (`tests/lembretes/`)

| ID | Caso |
| --- | --- |
| CT-F9-01 | Lembrete vencido → notificação (título e mensagem) e `ENVIADO`. Não vencido não é processado |
| CT-F9-02 | Materialização antecipada: série com lembrete gera ocorrências em `[hoje, hoje + 8]` com lembretes, e dispara no horário |
| CT-F9-03 | Importância concluída, excluída ou com compromisso passado → `CANCELADO` sem notificação |
| CT-F9-04 **c** | Dois processadores simultâneos → uma notificação por versão |
| CT-F9-05 **c** | Reagendamento durante o processamento → a versão substituída não gera notificação depois da substituição |
| CT-F9-06 **c** | Conclusão ou exclusão durante o processamento → resultado linearizável |
| CT-F9-07 | Falha num item não bloqueia os demais. O item é reprocessado no ciclo seguinte |
| CT-F9-08 | Lista e não lidas. Marcar como lida é idempotente. Importância excluída → `disponivel = false`. A leitura não conclui nem paga (4.1.9) |
| CT-F9-09 | CLI `--uma-vez` encerra. Ao receber o sinal, termina o item corrente |

### F10 — Painel (`tests/painel/`)

| ID | Caso |
| --- | --- |
| CT-F10-01 | Prévia de 3 com pendentes primeiro. Totais sobre todas (4.3.3). Concluir a terceira → 3 |
| CT-F10-02 | Saldo do mês = Financeiro (4.3.1). Dia 100/30 → 70. Lançamento de ontem cadastrado hoje fica fora (4.3.2). Comparação de despesas |
| CT-F10-03 | Pendentes do mês incluem recorrentes ainda não exibidas (4.2.4). Futura de outro mês fica em próximas e fora do mês (4.3.5). Atrasadas de meses anteriores com próximas vazias |
| CT-F10-04 | Importância de 99.90 não altera o saldo. O pagamento move os resumos (4.3.4) |
| CT-F10-05 | Virada de 31/10 para 01/11 com relógio (4.3.6) |
| CT-F10-06 | Vazios com zeros só em caso de sucesso. Falha de um bloco → erro estruturado (4.3.7) |
| CT-F10-07 **c** | Bloco financeiro consistente com escrita concorrente |
| CT-F10-08 | Referência de período independente de consultas a outros meses (4.2.1) |

### F11 — Consolidação (`tests/integracao/`)

| ID | Caso |
| --- | --- |
| CT-F11-01 | Fluxo integrado dirigido: registro → login → atividade recorrente → receita e despesa → importância → pagamento → painel coerente |
| CT-F11-02 | `performance`: volume de referência (arquitetura §12) e `EXPLAIN` das consultas de indicadores. Metas propostas a validar |
| CT-F11-03 | Settings de produção: segredos obrigatórios. `EMAIL_MODO = smtp` |

---

## 5. Comandos de validação

### 5.1. Qualidade

| Papel | Comandos |
| --- | --- |
| Implementador (no escopo autorizado, conforme `CLAUDE.md`) | `uv run ruff check --fix .` → `uv run ruff format .` e depois a verificação abaixo |
| Verificação (gates e auditoria; **não alteram arquivos**) | `uv run ruff check --no-fix .`, `uv run ruff format --check .` e `uv run pyright` |

Observações:

- Com `fix = true` no `pyproject.toml`, `uv run ruff check .` **altera arquivos**. Por isso o `--no-fix` é obrigatório na verificação (ACH-MV-ARQ-008).
- Antes dos comandos de correção, o implementador confere o diff, para que a correção não alcance arquivos fora do escopo. Com o baseline atual, os arquivos existentes em `src/` estão no escopo da F1.

### 5.2. Testes

- Sempre com caminhos, node IDs ou marcadores definidos no Prompt Master da fase. Exemplo da F1: `uv run pytest tests/infra -q`.
- Pyright, stress e medições de desempenho não rodam ao mesmo tempo, para não contaminar medições.

### 5.3. Alembic

| Comando | Quando | Requer banco |
| --- | --- | --- |
| `uv run alembic heads` | Toda fase com migração | Não |
| `uv run alembic history` | Fases com revisões | Não |
| Upgrade, check e downgrade | Executados **pelos testes** contra o container (CT-F1-17, CT-F2-01, CT-F2-08, CT-F2-09) | Container |
| `uv run alembic upgrade head` no banco de desenvolvimento | Somente por ação do usuário, com `.env` preenchido | Banco de desenvolvimento |

`alembic check` complementa a introspecção, mas não prova CHECKs: o autogenerate não compara CHECK constraints.

---

## 6. Evidências exigidas no relatório do implementador

1. Objeto entregue:
   - branch e HEAD do commit de baseline. Quando a Etapa A ocorreu antes do commit, também o bloco de revalidação do baseline (Prompt Master da fase). “Sem commits” + hashes SHA-256 dos arquivos alterados e criados só é aceito com a exceção de ACH-MV-ARQ-019 aceita explicitamente pelo usuário;
   - SHA-256 dos arquivos não rastreados por decisão (na F1, o `compose.yaml`);
   - `git status --short`;
   - `git diff --stat`;
   - lista de arquivos novos.
2. Ambiente: `uv --version`, Python, `docker --version`, imagem e digest do PostgreSQL de teste.
3. Cada comando executado, na ordem, com a saída resumida real: contagem de testes passados, falhos e pulados, e duração. Nenhum resultado inventado.
4. Mapeamento CT → node ID → resultado.
5. Testes não executados e o motivo. Distinguir “não executado”, “inconclusivo”, “falhou” e “passou”.
6. Desvios do Prompt Master: nenhum é permitido sem autorização. Se houver, devem estar descritos.
7. Pendências e riscos observados.

---

## 7. Severidade dos achados

| Severidade | Critério | Tratamento no gate |
| --- | --- | --- |
| P0 | Risco crítico imediato (exposição grave de segredos ou dados, ação destrutiva de grande alcance) | Bloqueia o escopo afetado. Interromper a ação perigosa |
| P1 | Violação grave de segurança, isolamento, integridade financeira ou perda/corrupção de dados | Bloqueia a entrega afetada |
| P2 | Descumprimento funcional ou contratual relevante, arquitetura incompleta para requisito necessário, ausência de prova obrigatória | Bloqueia a fase até correção ou decisão explícita do usuário |
| P3 | Questão menor e localizada, que não compromete requisitos obrigatórios nem a confiança na prova | Pode permanecer com justificativa, responsável e acompanhamento |

- A classificação segue o **impacto demonstrado**. Documentação errada que conduz a implementação incorreta pode ser P2. Um teste incapaz de detectar falha crítica não vira P3 porque o código parece correto.
- Registro de achado: `ID` (`ACH-MV-F<n>-NNN`), severidade, fato, fonte/caminho:linha, reprodução ou raciocínio verificável, impacto, fases afetadas, correção recomendada, critério de encerramento, responsável e estado (`ABERTO`, `CORRIGIDO`, `VERIFICADO`, `ACEITO_COMO_EXCECAO`).
- Achado comprovado e hipótese não verificada são diferenciados.

---

## 8. Gates e estados

| Gate | Condição de passagem |
| --- | --- |
| G0 — Baseline e fontes | Repositório identificado, fontes lidas, autorização conhecida, lacunas registradas |
| G1 — Arquitetura | Decisões fechadas ou explicitamente pendentes. Reconciliação completa. Requisitos cobertos. ADRs **aceitos pelo usuário** (com registro) para as decisões da fase |
| G2 — Prompt Master | Coerente com fontes aceitas. Escopo, arquivos, algoritmos, testes e parada definidos. Sem “a definir” |
| G3 — Etapa A do Sonnet | Baseline real confrontado. Plano concreto apresentado. Espera de “pode implementar” |
| G4 — Entrega | Código e evidências (§6). Sem autodeclaração de aprovação |
| G5 — Auditoria independente | Veredito do Opus fundamentado em verificação real (§9) |
| G6 — Integração | Commit/merge pelo usuário (LOCAL) ou merge da branch Cloud auditada. Reconciliação do baseline da fase seguinte |

Estados de fase e de prompt:

- `PROPOSTO`
- `AGUARDANDO_DECISAO`
- `BLOQUEADO`
- `PRONTO_PARA_ETAPA_A`
- `IMPLEMENTACAO_AUTORIZADA`
- `ENTREGUE_PARA_AUDITORIA`
- `APROVADO`
- `APROVADO_COM_P3`

“Concluído” não é usado para encobrir teste não executado ou decisão pendente. Uma exceção aceita pelo usuário fica registrada como exceção, com risco e alcance. Não vira teste aprovado.

---

## 9. Protocolo de auditoria independente (Opus)

1. Ler as fontes vigentes, o ADR, o Prompt Master, a autorização, o relatório e os arquivos reais.
2. Identificar o objeto auditado:
   - base, HEAD ou branch;
   - diff completo, alterações não commitadas e arquivos não rastreados;
   - revisões Alembic;
   - SHA-256 dos arquivos relevantes.

   No modo Cloud, conferir o SHA trazido para o WSL contra o informado.
3. Revisar o **diff completo** autorizado e os desvios de escopo, sem confiar apenas no resumo do implementador.
4. Reexecutar as verificações direcionadas necessárias para sustentar o veredito: seleção da fase e verificação Ruff/Pyright com `--no-fix`/`--check`. Os logs do implementador são evidência auxiliar.
5. Conferir efeitos no banco e resultados esperados, não apenas status HTTP ou contagem de testes. Verificar se os testes realmente detectariam a falha (por exemplo, se um teste de concorrência de fato produz espera).
6. Revisar:
   - transações (commit só no router e jobs);
   - concorrência (trava antes de leituras de decisão);
   - SQL;
   - migrações;
   - segurança (IDOR, segredos e logs);
   - escopo do produto: nenhuma dependência, tabela, configuração ou abstração de integração financeira externa, e nenhum saldo persistido ou editável (arquitetura §1.1);
   - schema e OpenAPI;
   - regressões relevantes.
7. Registrar cada comando executado, com seleção, ambiente, resultado real e limitações.
8. Emitir achados P0–P3 e o veredito: `BLOQUEADO`, `APROVADO` ou `APROVADO_COM_P3`.

Limites do auditor:

- **O Opus não implementa correções durante a auditoria.** Não altera código, testes, migrações, dependências ou configurações para o gate passar. Registra o defeito e encaminha a correção ao Sonnet pelo fluxo de autorização. Se faltar um teste obrigatório, registra a ausência e especifica a prova necessária.
- A reauditoria se concentra nos achados e nos efeitos diretamente afetados, ampliando somente diante de risco concreto.
- Uma mudança posterior ao veredito invalida a aplicação automática do veredito ao novo conteúdo.

---

## 10. Modo LOCAL e exceção Cloud

| Ação | Sonnet local | Sonnet Cloud (após autorização de implementação) |
| --- | --- | --- |
| Implementar o escopo aprovado | Permitido | Permitido na branch da sessão |
| Commit | Proibido | Somente na branch da sessão |
| Push | Não por iniciativa própria | Somente da branch da sessão |
| Pull Request | Não presumir | Somente **draft** |
| Alterar `main`, merge, force-push, proteção de branches | Proibido | Proibido |
| Declarar fase aprovada | Proibido | Proibido |

- O modo padrão é LOCAL, até a sessão ser identificada explicitamente como Cloud. Remote Git ou Docker não caracterizam Cloud.
- Na exceção Cloud, o Sonnet entrega branch, SHA, diff, PR draft e evidências. O usuário traz a branch para o WSL. O Opus local audita o mesmo SHA. O merge é decisão do usuário após a aprovação.
