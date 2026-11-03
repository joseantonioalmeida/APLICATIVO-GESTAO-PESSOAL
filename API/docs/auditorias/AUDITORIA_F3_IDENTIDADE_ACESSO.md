# Auditoria independente da F3 — Identidade e acesso

| Campo | Valor |
| --- | --- |
| Documento | `docs/auditorias/AUDITORIA_F3_IDENTIDADE_ACESSO.md` (primeira execução; nenhum relatório anterior da F3 existia) |
| Data | 2026-10-13 |
| Auditor | Claude Opus 5.5 |
| Instrução | `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F3_IDENTIDADE_ACESSO.md`, SHA-256 `c1e5c9b551c3dc33f36375d919dc8cee16e3b8037f131b399c0952f97d7d4fa2` |
| Objeto | Working tree de `/home/jose/projects/app_gestão_pessoal/API` sobre o commit `91be324c88c5a3f99a49b1b1700963e32ef257e9` (modo A, sem commit da F3) |
| Evidências | `/home/jose/minhavida_evidencias/f3_auditoria_wfK2MyfH/` (logs numerados, sondas, cópias externas e manifesto) |
| Veredito | **`APROVADO_COM_P3`** |

---

## 1. Veredito

**F3: `APROVADO_COM_P3`.**

Justificativa:

- Os 34 CTs (CT-F3-01 a 34) estão implementados e passaram na reprodução desta auditoria: 110 itens do pytest, 0 falhas, 0 skips e 0 xfails. Os 10 cenários de concorrência executaram com sincronização exata.
- As quatro regressões de `tests/infra` passaram (26 itens).
- Os gates de qualidade estão limpos: Ruff, formatação (76 arquivos), Pyright com 0 erros, 0 avisos e 0 informações, e `alembic heads` = `0001 (head)`.
- O objeto técnico é exatamente o manifesto final do implementador (34/34), e os 18 arquivos protegidos estão iguais ao baseline.
- Dependências: só as cinco entradas diretas autorizadas, sem versão alterada nem pacote removido.
- As sondas de mutação mostraram que os testes críticos detectam a falha que deveriam detectar: normalização UTC, limitador do Argon2 e trava da verificação.
- Restam três achados **P3**, nenhum impeditivo (§10):
  - ACH-MV-F3-001: documento de preparação ausente da working tree; precisa ser resolvido antes do commit;
  - ACH-MV-F3-002: nomes com separadores de linha Unicode; tem origem no contrato e pede decisão do usuário;
  - ACH-MV-F3-003: comandos auxiliares sem log; é processual.

A aprovação vale somente para o objeto identificado na §2. O G6 da F3 depende do commit do usuário e da conferência correspondente.

---

## 2. Identificação do objeto

### 2.1. Estado do Git (log `00_identificacao`)

- Raiz: `/home/jose/projects/app_gestão_pessoal/API`; branch `main`; HEAD `91be324c88c5a3f99a49b1b1700963e32ef257e9`; índice vazio.
- `git status --porcelain --untracked-files=all`: 45 linhas.
  - 16 rastreados modificados: 8 documentos da preparação e 8 arquivos técnicos autorizados em §7.2.
  - 29 não rastreados: 26 criados pela F3, 2 documentos da preparação (dossiê e Prompt F3) e a instrução desta auditoria.
- Nenhum arquivo rastreado removido.
- O modo é A, como informado.

### 2.2. Fontes operacionais e normativas (hashes completos)

| Fonte | SHA-256 | Situação |
| --- | --- | --- |
| Prompt F3 implementado | `c976854dc82f98229f87125878fd1447a42665e51a96f22ad04dc7209bc83536` | Igual ao esperado |
| Emenda F3-E1 (`~/minhavida_evidencias/f3_emenda_8NC4DtlF/EMENDA_F3_E1.md`) | `9b3ae10b8f64c5df16bfa4118fd98a24e9f9d05ff850f3b6b5a0769e346ca103` | Igual ao esperado; lida integralmente |
| `CLAUDE.md` | `515dd70023275e566b65a762804964a875144f222d0f46c3a76931f49c6c112a` | Igual ao Prompt F3 §1.2 |
| `docs/arquitetura/indice.md` | `53c4995947e50b82141641e0333be1dc9e2c8dec08a9736d2004da287d2a39c4` | Igual |
| `docs/adr/0001_arquitetura_api_minhavida.md` | `74a9b6bfb50200816e9f126f147896f206962711c490867b70e27a342735474f` | Igual |
| `docs/adr/0002_identificadores_uuid.md` | `951fb3936affa3eb1dcab67f89507eb9620630e938b2868b2f3ebf4b632b7593` | Igual ao baseline |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `a2630f21f6360968daebbeb226906e66835404521d7df2bca185f352d31dc242` | Igual |
| `docs/arquitetura/preparacao_f3_identidade_acesso.md` | `62ffd7250e5262d9bead12551ba654694aab2f446b4dc2565290e3c0b7e59af2` | Igual |
| `docs/arquitetura/plano_validacao_auditoria.md` | `de8d8c848001af5f44a900da875cdf710265f7d4e72c0a99213f4eca374e7690` | Igual |
| `docs/arquitetura/plano_fases_api.md` | `54ccbab4346c926607f867a993d17a8b2d4e9ad40b47995f0dbe4dd76bb98876` | Igual |
| `docs/arquitetura/matriz_requisitos_api.md` | `dc681cac8c32bc9c4ff6d6e67100f30123705e9eb81c19ef381aac210c6a9c58` | Igual |
| `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` | esperado `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695` | **AUSENTE** (ACH-MV-F3-001) |

As aprovações aplicadas estão no `indice.md` §4:

- M16: DEC-MV-09 a 13 e DEC-MV-14 só no escopo da recuperação;
- a Emenda F3-E1, aprovada e encaminhada pelo usuário, com reconciliação documental prevista para depois desta auditoria;
- a autorização da Etapa B, atestada pela instrução desta auditoria.

### 2.3. Três conjuntos (log `02_identificacao_hashes_escopo`)

| Conjunto | Resultado |
| --- | --- |
| Preparação documental (Prompt F3 §1.2) | 9 de 10 documentos com o hash da liberação; 1 ausente (ACH-MV-F3-001). O Prompt F3 e a emenda estão íntegros |
| Arquivos técnicos da F3 | 26 criados (= §7.1) e 8 alterados (= §7.2). Nenhum arquivo fora de §7 além desta instrução de auditoria. Todos os 34 com o hash de `17c_sha256_f3.log` do implementador (log `03`: 34/34) |
| Protegidos (§1.1 e §7.3) | Os 18 protegidos de §1.1 estão iguais ao baseline. Modelos, migração `0001`, `alembic/env.py`, `database.py`, `rastreamento.py`, `schemas/erro.py`, `routers/saude.py`, `tests/infra/*` (exceto `test_configuracao.py`) e `tests/apoio/{banco,esquema,rotas_teste}.py` não mudaram |

---

## 3. Alcance das aprovações e da Emenda F3-E1

- **DEC-MV-09:**
  - JWT HS256, 24 h por padrão (5 a 1440 min), claims `{sub, iat, exp, typ, sv}`;
  - validação temporal manual pelo `Relogio`;
  - Argon2id com limitador dedicado; fuso obrigatório;
  - e-mail canônico (R9.9); logout só no cliente.
- **DEC-MV-10, opção A:** 404 `EMAIL_NAO_ENCONTRADO`, com risco aceito.
- **DEC-MV-11:** R11.1 a R11.10.
- **DEC-MV-12:** SMTP em thread, dentro da transação e antes do commit, com as consequências 1 a 6 aceitas.
- **DEC-MV-13:** só `GET /api/v1/usuarios/me`.
- **DEC-MV-14, só no escopo da F3:** travas de linha da recuperação e `INSERT … ON CONFLICT`.
- **Fora do escopo e não implementado:** trava consultiva por usuário, idempotência, refresh, sessões, DEC-MV-21 e DEC-MV-24. Nenhum service importa outro (D-02).
- **Emenda F3-E1:**
  - E1.1: chamada de `Settings` com segredo explícito;
  - E1.2: CT-F3-31 a 33 e `ESPERA_UPDATE_USUARIO`;
  - E1.3: `_em_utc` e CT-F3-34;
  - E1.4: unicidade tipada; sem aumento de prazos;
  - E1.5: Etapa A complementar.
- A ausência dos CT-F3-31 a 34 nos documentos congelados **não** é desvio: a reconciliação foi aprovada para depois da auditoria (Anexo A).

---

## 4. Alegações do Sonnet

| Alegação | Situação | Evidência |
| --- | --- | --- |
| Modo A, HEAD `91be324`, 37 hashes iguais no passo 0 | **Comprovada** pelo log original | `00_revalidacao.log` (íntegro no manifesto `f3_sha256_logs.txt`, 44/44 OK; log `04`) |
| Emenda revalidada antes da implementação (E1.5) | **Comprovada** | `RELATORIO_ETAPA_A_E1.md`, `etapa_a_e1_verificacoes.log` e o bloco da emenda no `00_revalidacao.log` |
| 8 alterados e 26 criados, só de §7 | **Comprovada** | Log `02`; `17a_status.log` |
| 110 testes da fase e 26 regressões aprovados | **Comprovada por reprodução** | Logs `07` (110 passed) e `08` (26 passed) |
| Ruff limpo, 76 arquivos formatados, Pyright sem erros, `0001 (head)` | **Comprovada por reprodução** | Logs `09` a `12` |
| Cinco dependências diretas, sem versão alterada nem pacote removido | **Comprovada** | Logs `05` e `05b`; `02a` e `02e` originais |
| Única supressão é a preexistente em `settings.py` | **Comprovada no objeto final** | Log `05`: só `settings.py:141 # pyright: ignore[reportCallIssue]`, a mesma da linha 42 do baseline |
| Supressões “escritas por engano e removidas antes de qualquer execução” | **Não verificável** | Não há evidência histórica antes dos logs. O estado final está limpo, mas a ausência de execução intermediária não é comprovável |
| Falha do `test_hasher` foi defeito do teste, corrigido e revalidado | **Comprovada** | `06_pytest_identidade.log`: `TypeError: Medidor.hash_medido() missing 1 required positional argument`; `06b` passou; `06_2` com 110 passed |
| Ruff com erros residuais corrigidos à mão; Pyright `LiteralString` corrigido; gates repetidos | **Comprovada pela sequência de logs** | Ordem dos `mtime`, só como indício: `08a` (19:56:29, 38 erros) → `08a_2` → `06_3`/`07_2` → `13` (19:58:35, 2 erros) → `08a_3` → `06_4`/`07_3` → `13_2` (0 erros). A versão final foi validada depois da última alteração e reproduzida nesta auditoria |
| Comandos de diagnóstico e de edição fora do §14 | **Declarada; sem log próprio** | ACH-MV-F3-003 |
| Sondas da Etapa A/A-E1 em `/tmp/claude-1000/.../scratchpad/` | **Não verificada** | O caminho é abreviado e não identifica um arquivo; não foi procurado por glob ambíguo |

---

## 5. Inventário, auxiliares e supressões

### 5.1. Produção (14 arquivos novos em `src/`)

| Arquivo | Finalidade | Autorizado |
| --- | --- | --- |
| `tempo.py` | Relógio, `ContextoUsuario`, fuso | §7.1; **byte a byte igual ao bloco exato validado** |
| `seguranca.py` | Argon2, JWT, geradores, `hash_token` | §7.1 |
| `email.py` | Protocolo, SMTP, memória, texto 3.4.4 | §7.1 |
| `dependencias.py` | Relógio, recursos, `sem_cache`, `ContextoDep` | §7.1 |
| `services/__init__.py`, `identidade.py`, `recuperacao_senha.py`, `autorizacao.py` | Regras de negócio | §7.1. **Nenhum importa outro service** (imports conferidos) |
| `schemas/autenticacao.py`, `schemas/usuario.py` | Entradas, respostas e `canonicalizar_email` | §7.1 |
| `routers/autenticacao.py`, `routers/usuarios.py` | Endpoints e commit | §7.1 |

O app real inclui só os routers `saude`, `autenticacao` e `usuarios` (`main.py`). As rotas `/teste*` existem só nos testes.

### 5.2. Testes e auxiliares

- **`tests/apoio/relogio.py`:** igual ao bloco exato.
- **`tests/apoio/identidade.py`:** tem o contrato mínimo de §11.1 e da E1.2:
  - helpers `registrar`, `entrar`, `linha_recuperacao` e `aguardar_espera_por_trava`;
  - as quatro constantes de espera.

  Os extras (`solicitar`, `verificar`, `redefinir`, `obter_token_redefinicao`, `codigo_de_erro`, `SequenciaCodigos`, `LinhaRecuperacao`, `disparar_simultaneas`, `disparar_em_ordem`) decompõem chamadas repetidas. Não mudam asserções nem escondem recursos: as bloqueadoras e o monitor continuam reais, e os helpers de disparo desfazem a bloqueadora e aguardam as tarefas também em caso de falha.
- **`tests/identidade/conftest.py`:**
  - tem as fixtures exigidas (`relogio`, `enviador`, `app_identidade`, `cliente`, `limpeza` autouse e `monitor`);
  - extras: o agregador `Ambiente`/`ambiente` e a fábrica `abrir_bloqueadora`, que fecha as conexões na desmontagem;
  - a ordem de desmontagem é correta: as bloqueadoras fecham antes da `limpeza`, que é autouse e desmontada por último;
  - os overrides existem só no app de teste, sem efeito global.
- **`test_vazamento.py`:** redefine localmente `app_identidade` para ativar `LOG_NIVEL=DEBUG` e acrescentar as rotas de falha (permitido por §11.1 e §11.3). O banco migrado continua garantido pela fixture `ambiente`.
- **Testes extras, fora dos CTs:** `test_email.py::test_enviador_em_memoria` e `::test_criar_enviador`. Também `test_login.py::test_login_nao_regrava_hash`, ligado ao CT-F3-29.
- **Classificação:** liberdade de implementação dentro dos arquivos permitidos. Os dois blocos de conteúdo exato estão íntegros, e nenhum auxiliar contorna o limite de parâmetros mudando contratos de produção.

### 5.3. Supressões e configuração

- Nenhum `# noqa`, `# type: ignore` ou `# pyright: ignore` novo em `src/`, `tests/` e `alembic/`.
- `[tool.ruff]`, `[tool.pyright]`, `[tool.pytest.ini_options]`, coverage, taskipy, setuptools e o grupo dev estão iguais ao baseline (log `05`).

---

## 6. Matriz CT → requisito → node IDs → resultado

Todos os itens abaixo passaram no log `07` (110 passed, 71,40 s). As asserções foram conferidas contra o Prompt F3 §11.3 e a E1. Os números entre parênteses são itens do pytest.

| CT | Requisito / regra | Node ID(s) | Resultado |
| --- | --- | --- | --- |
| 01 | 2.1; R9.9 | `test_registro.py::test_registro_valido` (1) | Passou |
| 02 | 2.1, 3.4.10, 3.4.14; R11.10; `_data_civil`; fuso; nome | `test_registro.py::test_validacoes_do_registro` (21) | Passou |
| 03 | Unicidade canônica (R9.9) | `test_registro.py::test_email_duplicado` (4: ASCII, IDN em maiúsculas, NFD e punycode) | Passou |
| 04 | 1.1; claims; `Cache-Control` | `test_login.py::test_login_valido` (1) | Passou |
| 05 **c** | C1 | `test_registro.py::test_registros_simultaneos` (1) | Passou |
| 06 | Login indistinguível, inclusive e-mail malformado | `test_login.py::test_credenciais_invalidas_indistinguiveis` (1) | Passou |
| 07 | Token recusado (13 casos) | `test_login.py::test_tokens_recusados` (13) | Passou |
| 08 | 4.1.1 | `test_usuario_atual.py::test_usuario_atual` (1) | Passou |
| 09 | 3.4.3 a 3.4.5; destinatário canônico | `test_recuperacao.py::test_solicitar_codigo` (1) | Passou |
| 10 | 3.4.2 (DEC-MV-10 A) | `test_recuperacao.py::test_email_nao_encontrado` (1) | Passou |
| 11 | Reenvio (R11.4, R11.5) | `test_recuperacao.py::test_reenvio`, `::test_reenvio_anula_token` (2) | Passou |
| 12 | Verificação (R11.6, R11.7, 3.4.8) | `test_recuperacao.py::test_verificacao` (1) | Passou |
| 13 | 409 sem novo token | `test_recuperacao.py::test_verificar_de_novo` (1) | Passou |
| 14 **c** | C4 | `test_recuperacao_concorrencia.py::test_verificacoes_corretas_simultaneas` (1) | Passou |
| 15 **c** | C5 (espera exata de 5) | `…::test_cinco_invalidas_simultaneas` (1) | Passou |
| 16 | 3.4.15; `sv` | `test_recuperacao.py::test_redefinir` (1) | Passou |
| 17 **c** | C8 | `…::test_redefinicoes_simultaneas` (1) | Passou |
| 18 | Redefinição inválida | `test_recuperacao.py::test_redefinir_invalido` (1) | Passou |
| 19 **c** | C7, duas ordens | `…::test_reenvio_e_verificacao[verificar_antes]`, `[reenviar_antes]` (2) | Passou |
| 20 | C11 | `test_recuperacao.py::test_falha_de_envio` (1) | Passou |
| 21 | D-13 | `test_usuario_atual.py::test_hoje_no_fuso` (1) | Passou |
| 22 | Settings da F3 | `test_configuracao_identidade.py::test_settings_da_f3` (28) | Passou |
| 23 **c** | C2 | `…::test_primeiras_solicitacoes_simultaneas` (1) | Passou |
| 24 | Limites exatos | `test_recuperacao.py::test_limites_da_recuperacao`, `test_login.py::test_limites_do_token` (2) | Passou |
| 25 | Não vazamento | `test_vazamento.py::test_sem_vazamento` (1) | Passou |
| 26 | C12 | `test_recuperacao.py::test_commit_falha_depois_do_envio` (1) | Passou |
| 27 **c** | C9, duas ordens | `…::test_reenvio_e_redefinicao[redefinir_antes]`, `[reenviar_antes]` (2) | Passou |
| 28 | SMTP e texto 3.4.4 | `test_email.py::test_enviador_smtp` (5), `::test_mensagem_codigo` (1) | Passou |
| 29 | Hasher e token | `test_seguranca.py::test_hasher`, `::test_token_unidade`; `test_login.py::test_login_nao_regrava_hash` (3) | Passou |
| 30 | `obter_do_usuario_ou_404` | `test_usuario_atual.py::test_obter_do_usuario_ou_404` (1) | Passou |
| 31 **c** | C3 (E1.2) | `…::test_reenvios_simultaneos` (1) | Passou |
| 32 **c** | C6, duas ordens (E1.2) | `…::test_verificacao_correta_e_limite[invalida_antes]`, `[correta_antes]` (2) | Passou |
| 33 **c** | C10 (E1.2) | `…::test_login_durante_redefinicao` (1) | Passou |
| 34 | UTC (E1.3) | `test_recuperacao.py::test_expira_em_utc_com_sessao_em_outro_fuso` (1) | Passou |

**Contagem:**
- 34 CTs em 108 itens, já contando `test_login_nao_regrava_hash` no CT-F3-29;
- mais 2 itens de testes extras (`test_enviador_em_memoria` e `test_criar_enviador`), o que dá 110 coletados e 110 aprovados;
- concorrência: 13 itens para os 10 CTs marcados (log `06b`).

**Regressões** (log `08`, 26 passed): `tests/infra/test_configuracao.py` (8), `test_erros.py`, `test_saude.py` e `test_sessao_transacao.py`.
- `test_configuracao.py` é idêntico à versão validada na sonda da E1.1.
- `tests/esquema` e `tests/infra/test_alembic_ambiente.py` não entraram, conforme a seleção do §14. Nenhum deles usa `settings_teste`, e os testes de Alembic injetam a URL; o único teste sem URL é estático. Não há risco concreto que justifique ampliar a seleção.

---

## 7. Evidências por tema

### 7.1. Concorrência

Os 10 cenários foram conferidos item a item:

- **Requisições e conexões:** requisições HTTP independentes, uma sessão por requisição e engine com pool. Bloqueadora psycopg dedicada e monitor `NullPool` separado.
- **Espera:** contagem **exata** de sessões `active` esperando `Lock`, filtrada pelo texto da consulta.
  - CT-F3-15 exige 5 paradas;
  - CT-F3-19, 27 e 32 usam o portão de ordem (1 e depois 2);
  - CT-F3-33 espera 1 no `UPDATE usuario SET`.
- **Conferência do estado:** por outra conexão (`linha_recuperacao`/`consultar`), nunca pelo mapa de identidade.
- **Falhas:** os helpers de disparo desfazem a bloqueadora e aguardam as tarefas também em caso de falha, e as bloqueadoras são fechadas na desmontagem. Nenhum prazo foi aumentado, e nenhum 503 foi aceito no lugar do resultado contratual.
- **Sonda `14d` (mutação):** sem `with_for_update(of=RecuperacaoSenha)` na verificação, os CT-F3-14 e 15 **falham**, com `TimeoutError … observadas: 0`. Os testes detectam a falta da trava; o controle (`14a`) passa.
- **Sonda `16` (CT-F3-33 com falha forçada dentro do bloco `try`):** o teste falha, o seguinte da mesma sessão passa, e não aparece aviso de tarefa pendente. A hipótese de vazamento de tarefa no caminho de falha **não se confirmou**; não há achado.

### 7.2. Transações e travas

- Os services só fazem `flush`.
- Os routers fazem o commit em registro, solicitação e redefinição. Na verificação, o commit vem **antes** do erro, com `Retry-After` em `TENTATIVAS_ESGOTADAS`. O login e o usuário atual não fazem commit.
- Nenhum handler faz commit.
- **SQL real (sonda `15`):**
  - a verificação usa `… JOIN usuario … FOR UPDATE OF recuperacao_senha` e trava só a recuperação;
  - solicitar e redefinir usam `FOR UPDATE` simples em `recuperacao_senha`;
  - a primeira emissão usa `INSERT … ON CONFLICT (usuario_id) DO NOTHING RETURNING id`.
- **Ordem das travas:**
  - nenhum fluxo trava `usuario` antes de `recuperacao_senha`;
  - a redefinição trava a recuperação e depois atualiza `usuario` (`FOR NO KEY UPDATE`);
  - o `INSERT` da recuperação faz só `FOR KEY SHARE` em `usuario`, que é compatível com esse lock.

  Não há ciclo de espera nem deadlock concreto.
- **Relógio:** capturado depois da trava no reenvio e na verificação. Na primeira emissão, é capturado antes do `INSERT`, como em R11.2. Se o `ON CONFLICT` não inserir, o reenvio recaptura o instante.

### 7.3. JWT, credenciais e contexto

- **Biblioteca:** PyJWT 2.15.1 instalado = lock.
- **`jwt.decode`:**
  - `algorithms=["HS256"]` e `verify_signature=True`;
  - `verify_exp`, `verify_iat` e `verify_nbf` desligados;
  - `require` com as cinco claims.
- **Validação manual completa:**
  - conjunto exato de claims; `typ == "access"`;
  - `sub` como UUID canônico;
  - `type(...) is int` para `iat` e `exp` (recusa `bool`);
  - `0 < exp − iat ≤ validade`; `iat ≤ agora < exp`;
  - `sv` no formato `^[0-9a-f]{16}$` antes de `hmac.compare_digest`.
- **Cobertura:** CT-F3-07 (13 casos), CT-F3-24 (limites `iat − 1 s`, `exp − 1 s` e `exp`) e `test_token_unidade`.
- **Tokens iguais:** sob o `RelogioFixo`, T1 e T2 do CT-F3-33 são iguais, como previsto na E1.2. Os dois são recusados depois do commit pela mudança de `sv`.
- **Hasher:**
  - Argon2id com `hash_len` 32 e `salt_len` 16;
  - `anyio.to_thread.run_sync(…, abandon_on_cancel=False, limiter=limitador)`;
  - hash fictício preparado no `lifespan`, antes da engine;
  - `VerifyMismatchError` → `False`; demais erros → `HashArmazenadoInvalido` sem dados;
  - sem `check_needs_rehash`.
- **Teste do limitador:** mede execuções **simultâneas** (contador `ativas` e eventos), e não chamadas concluídas.
  - **Sonda `14c`:** sem o `limiter`, o `test_hasher` **falha** (`assert not True`: a terceira execução entrou).
- **Segredo:** ≥ 32 bytes UTF-8; o placeholder `TROQUE_ESTE_VALOR` é recusado (CT-F3-22).

### 7.4. Recuperação

Os itens de R11 foram conferidos no código e nos CTs 09 a 20, 23, 24, 26, 27 e 31 a 34:

- **Código:** `secrets.randbelow(10**8)` formatado com zeros à esquerda; guardado como hash Argon2id; padrão `[0-9]{8}` com `fullmatch` (ASCII).
- **Prazos:** 10 min de validade, 5 tentativas e 60 s de intervalo, como constantes. `Retry-After` calculado com `ceil` e mínimo 1.
- **Reenvio:** substitui o hash e o `expira_em`, zera as tentativas e limpa verificação, token e uso.
- **Token de redefinição:** `token_urlsafe(32)`, guardado como SHA-256 hexadecimal, com a validade da emissão.
- **Redefinição:** troca a senha e marca `utilizado_em` na mesma transação.

### 7.5. E-mail SMTP

- **Contrato SMTP:** assunto e corpo exatos; `To` canônico.
- **Segurança e conexão:**
  - `ssl.create_default_context()` (`CERT_REQUIRED` e `check_hostname`);
  - `starttls` + `ehlo`; `SMTP_SSL` no modo `tls`;
  - `login` só com credenciais;
  - `timeout`; `with` fecha a conexão.
- **Erros:** exceções de SMTP, de socket, `UnicodeError` e `ValueError` viram `FalhaEnvioEmail(nome da classe) from None`, com log só do motivo e do código SMTP.
- **Cobertura:** CT-F3-28 inclui `SMTPRecipientsRefused` com endereço sentinela, ausente da exceção e do log.
- **Injeção de cabeçalho:** não ocorre. O `email.message` recusa U+2028, U+0085 e U+2029 com `ValueError` (sonda `17`). O efeito funcional disso está no ACH-MV-F3-002.

### 7.6. UTC (E1.3)

- `_em_utc` lança `RuntimeError` se `utcoffset()` for `None` e normaliza com `astimezone(UTC)`. É aplicada ao único instante de resposta lido do banco.
- **Override na sessão da requisição:** o CT-F3-34 substitui `obter_sessao` na própria aplicação (`dependency_overrides`) por sessões de uma engine com `-c TimeZone=America/Sao_Paulo`. A engine é descartada no `finally`, e o app é recriado a cada teste.
- **Sonda `14b` (mutação sem `_em_utc`):** o teste **falha** com `'2026-10-13T09:10:00-03:00' == '2026-10-13T12:10:00Z'`. Isso prova que o override incide na sessão da requisição e que o teste distingue a falha.

### 7.7. Não vazamento e configuração

- **CT-F3-25:**
  - sentinelas: nome, e-mail, senha, nova senha, código e tokens;
  - respostas de sucesso com as chaves exatas;
  - erros sem eco de entrada (`detalhes` nulo);
  - logs verificados por `caplog` e pelo handler formatado real (`FORMATO_LOG` e `FiltroIdRequisicao`), em `DEBUG`, inclusive com `RuntimeError` e `FalhaEnvioEmail` inesperados.
- **Cadeia de exceções:** `from None` em todas as traduções.
- **`SettingsTeste`:** só a fonte `init_settings`, `env_file=None`.
- **Importação sem I/O:** CT-F1-02 continua passando nas regressões. `RelogioSistema()` e `HTTPBearer` são objetos de módulo sem I/O; `CapacityLimiter` e o hash fictício nascem no `lifespan`.

---

## 8. Dependências, esquema e gates

- **`pyproject.toml`:**
  - novas entradas diretas: `anyio>=4.15.1`, `argon2-cffi>=25.1.0`, `email-validator>=2.3.0`, `pyjwt>=2.15.1` e `tzdata>=2026.5`;
  - nenhuma remoção; os demais campos de `[project]` e todas as seções `[tool.*]` iguais ao baseline.
- **`uv.lock`:**
  - novos: `argon2-cffi` 25.1.0, `argon2-cffi-bindings` 26.1.0, `cffi` 2.1.1, `pycparser` 3.11 e `pyjwt` 2.15.1;
  - `anyio` 4.15.1, `email-validator` 2.3.0 e `tzdata` 2026.5 já existiam como transitivos e só passaram a diretos;
  - nenhuma versão alterada, nenhum pacote removido;
  - a entrada do próprio projeto (`api`) mudou só em `dependencies` e `requires-dist`, com essas cinco.
- **Ambiente instalado:** igual ao lock nos 8 pacotes conferidos (log `05`). Nada foi instalado pela auditoria.
- **Esquema:** modelos, migração `0001` e `env.py` com os hashes do baseline; `alembic heads` = `0001 (head)`; nenhuma revisão nova.
- **`.env.exemplo`:**
  - acréscimo exato de §9.2, com placeholder propositalmente inválido;
  - SMTP comentado; `EMAIL_MODO=memoria`.

  O `.env` real não foi lido. O preenchimento de `JWT_SEGREDO`, `EMAIL_MODO` e SMTP é passo operacional do usuário.

| Gate | Resultado nesta auditoria | Log |
| --- | --- | --- |
| `ruff check --no-fix --no-cache .` | `All checks passed!` (0) | `09` |
| `ruff format --check --no-cache .` | `76 files already formatted` (0) | `10` |
| `pyright` | `0 errors, 0 warnings, 0 informations` (0) | `11` |
| `alembic heads` | `0001 (head)` (0) | `12` |

---

## 9. Falhas intermediárias e limites da reconstrução

Reconstruído pelos logs originais (íntegros, 44/44):

1. O primeiro `pytest tests/identidade` teve 1 falha: um defeito no próprio `test_hasher`, cujo substituto estava vinculado de forma errada. O teste foi corrigido e revalidado isoladamente (`06b`) e depois na seleção (`06_2`).
2. `ruff check --fix` deixou 36 erros residuais, e a formatação reformatou 13 arquivos. Houve correção manual (`08a_2`) e reexecução dos testes (`06_3`, `07_2`).
3. O Pyright acusou 2 erros de `LiteralString` em `schemas/autenticacao.py`. Depois da correção, houve nova rodada completa (`08a_3`, `06_4`, `07_3`, `11_2`, `12_2` e `13_2`). Os testes finais rodaram depois da última correção relevante.

Limites:
- não há evidência da existência e da remoção das supressões citadas no relatório da Etapa B (§6, item 1), nem dos comandos auxiliares sem log (ACH-MV-F3-003);
- a ordem por `mtime` é só um indício;
- não houve servidor SMTP real (contrato: simulação).

O estado final foi reproduzido integralmente nesta auditoria e não depende dessas lacunas.

---

## 10. Achados

IDs `ACH-MV-F3-*` conferidos como livres antes do registro.

| Campo | ACH-MV-F3-001 |
| --- | --- |
| Severidade e gate | **P3**. Não impede a aprovação técnica; precisa ser resolvido antes do commit da F3 (G6) |
| Origem | Documentação/evidência. Alteração da working tree **depois** da entrega e fora do implementador: o arquivo constava no `00_revalidacao.log` e no `17a_status.log` (20:00), e não existia no início desta auditoria |
| Requisito | Prompt F3 §1.2 (conjunto da preparação documental aprovada); `indice.md` §2 e §4 (M14), que citam o arquivo com SHA-256 |
| Local | `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` |
| Reprodução | Log `00_identificacao` (`No such file or directory`) e log `02` (`AUSENTE`), código 0 |
| Esperado / observado | Arquivo presente com SHA-256 `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695` / ausente. Nenhuma cópia nas pastas de evidências, só os hashes. O arquivo nunca foi rastreado pelo Git |
| Impacto | Nenhum sobre o código, os testes ou os gates. Quebra o rastro documental da M14 e a lista de §1.2 usada no commit |
| Correção proposta | O usuário restaura o arquivo com o mesmo hash, a partir da sua cópia da mensagem M14, ou decide expressamente pela remoção, e o fechamento documental registra a decisão |
| Revalidação | `sha256sum PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` = `46c49e0d…` (ou registro da decisão no índice §4) |

| Campo | ACH-MV-F3-002 |
| --- | --- |
| Severidade e gate | **P3**. Não impede: o efeito é localizado e improvável, sem exposição de dados nem injeção de cabeçalho |
| Origem | **Contrato** (dossiê da F3 §6.4 e arquitetura §9.1: o nome recusa só a categoria Unicode `Cc`). A implementação segue o contrato literalmente |
| Requisito | 3.4.3 (envio do código à conta); DEC-MV-12; ACH-MV-ARQ-034, cuja intenção era impedir que o nome quebrasse o cabeçalho “Assunto” |
| Local | `src/api_gestao_pessoal/schemas/autenticacao.py:72-84` (`_nome_completo`); `src/api_gestao_pessoal/email.py:86-92` e `116-132` |
| Reprodução | Sonda `18_sonda_nome_separador` (código 0) na cópia externa `copias/controle`, com `smtplib` simulado |
| Esperado / observado | Uma conta aceita no cadastro deveria poder receber o código. Observado: `Ana Silva` e `Ana Silva` (categorias `Zl` e `Zp`) são aceitos no cadastro, mas `EmailMessage` recusa o assunto (`ValueError`), e todo envio vira `FalhaEnvioEmail(ValueError)` → 503, sem abrir conexão |
| Impacto | A recuperação de senha fica permanentemente indisponível para essas contas no modo SMTP, e o usuário não pode corrigir o nome (DEC-MV-13). O login com senha conhecida não é afetado. Os testes usam o modo memória e não exercitam o caminho |
| Correção proposta | **Nova proposta, exige decisão do usuário:** ampliar `_nome_completo` para recusar também as categorias `Zl` e `Zp`, com o mesmo código `NOME_COMPLETO_INVALIDO`, e acrescentar ao CT-F3-02 o caso `nome_com_separador_unicode`. É mudança de contrato (dossiê §6.4, arquitetura §9.1 e §4.5); não foi aplicada |
| Revalidação | `pytest tests/identidade/test_registro.py::test_validacoes_do_registro` com o caso novo, mais a sonda `18` mostrando 422 no cadastro |

| Campo | ACH-MV-F3-003 |
| --- | --- |
| Severidade e gate | **P3** (processo). Não impede |
| Origem | Processo e evidência do implementador |
| Requisito | Prompt F3 §0, regra 10 (cada comando grava saída completa e código de saída) |
| Local | Relatório da Etapa B §6, itens 1 e 6 |
| Reprodução | Leitura do relatório; os comandos declarados (`rg`, `ruff --output-format concise`, importação de `main`, `pytest --collect-only -m concorrencia` e scripts `python3` de edição) não têm log em `~/minhavida_evidencias/f3/` |
| Esperado / observado | Diagnósticos com log / diagnósticos sem log; supressões declaradas como escritas e removidas sem rastro verificável |
| Impacto | Só rastreabilidade histórica. O objeto final foi validado de forma independente nesta auditoria |
| Correção proposta | Nenhuma no objeto. Lição para os próximos prompts: prescrever um log também para comandos de diagnóstico, ou autorizá-los expressamente sem log |
| Revalidação | Não se aplica |

Achados P0, P1 e P2: **nenhum**.

Hipótese examinada e **não confirmada**: tarefa pendente no caminho de falha do CT-F3-33 (sonda `16`).

---

## 11. Comandos executados

Todos foram executados na raiz confirmada ou na cópia externa indicada, com `PYTHONDONTWRITEBYTECODE=1`, pelo executor inspecionável `executar.sh`, que grava o comando, a pasta de trabalho, a saída e o código real.

| Log | Comando | Código | Resultado |
| --- | --- | --- | --- |
| `00_identificacao` | `git rev-parse`, `git status --porcelain --untracked-files=all`, `sha256sum` das fontes | 0 | Ver §2 |
| `01_manifesto_inicial.sha256` | `git ls-files -m -o --exclude-standard …` + `sha256sum` (45 arquivos) | 0 | Manifesto inicial |
| `02_identificacao_hashes_escopo` | `python3 -I conferir_identificacao.py` | 0 | §1.1, §1.2 e escopo |
| `03_conferencia_manifesto_etapa_b` | `sha256sum -c` dos 34 arquivos de `17c` | 0 | 34/34 |
| `04_integridade_logs_sonnet` | `sha256sum -c f3_sha256_logs.txt` | 0 | 44/44 |
| `05`, `05b` | `uv run --frozen --no-sync python -I conferir_supressoes_deps.py` e consulta da entrada `api` do lock | 0 | §5.3 e §8 |
| `06_pytest_coleta_identidade` | `uv run --frozen --no-sync pytest tests/identidade --collect-only -q --color=no -p no:cacheprovider` | 0 | 110 coletados |
| `06b_pytest_coleta_concorrencia` | idem, com `-m concorrencia` | 0 | 13/110 |
| `07_pytest_identidade` | `uv run --frozen --no-sync pytest tests/identidade -vv --color=no -p no:cacheprovider` | 0 | **110 passed** em 71,40 s |
| `08_pytest_regressoes` | `uv run --frozen --no-sync pytest tests/infra/test_configuracao.py tests/infra/test_erros.py tests/infra/test_saude.py tests/infra/test_sessao_transacao.py -vv --color=no -p no:cacheprovider` | 0 | **26 passed** em 8,05 s |
| `09` a `12` | `ruff check --no-fix --no-cache .`; `ruff format --check --no-cache .`; `pyright`; `alembic heads` | 0, 0, 0, 0 | §8 |
| `13_copia_base_manifesto.sha256` | cópia do objeto (`git ls-files -co --exclude-standard`, sem `.env`) | — | 106 arquivos, iguais ao objeto |
| `14a` | Controle: 4 node IDs na cópia sem mutação | 0 | 4 passed |
| `14b` | CT-F3-34 na cópia sem `_em_utc` | 1 | Falha esperada |
| `14c` | `test_hasher` na cópia sem `limiter` | 1 | Falha esperada |
| `14d` | CT-F3-14 e 15 na cópia sem `FOR UPDATE` | 1 | Falhas esperadas |
| `15_sonda_sql_travas` | Compilação do SQL das travas (cópia) | 0 | §7.2 |
| `16_sonda_falha_caminho_c10` | CT-F3-33 com asserção forçada a falhar + CT-F3-31 (cópia) | 1 | Falha esperada; sem tarefa pendente |
| `17_sonda_cabecalho_email` | `email.message` com U+2028, U+0085 e U+2029 | 0 | `ValueError` nos três |
| `18_sonda_nome_separador` | Cadastro + envio SMTP simulado (cópia) | 0 | ACH-MV-F3-002 |
| `19_preservacao_objeto` | Status, manifestos e caches ao final | 0 | §12 |

**Não executados**, com justificativa:
- suíte completa: não há motivo concreto nos três campos exigidos;
- `tests/esquema` e `tests/infra/test_alembic_ambiente.py`: §6;
- nova bateria completa da concorrência: os 10 cenários já integram o log `07`;
- Docker Compose e comandos do Alembic além de `heads`: proibidos pela instrução.

Os contêineres descartáveis do Testcontainers foram removidos ao fim de cada execução.

---

## 12. Preservação do objeto

- O manifesto inicial (45 arquivos modificados ou novos, log `01`) e o manifesto final do implementador (34 arquivos técnicos) foram reconferidos ao final, **sem divergência** (log `19`).
- `git status` antes da gravação deste relatório era igual ao inicial: 45 linhas, HEAD `91be324` e índice vazio. Depois da gravação, a única linha nova é a deste relatório (conferência final no log `20`).
- Nenhum bytecode nem cache novo em `src/`, `tests/` e `alembic/`.
- A única saída nova no repositório é este relatório. A instrução de auditoria já estava na pasta `PROMPTS/`, salva pelo usuário.
- Mutações e testes adicionais ocorreram só nas cópias de `copias/`. Os resultados dessas cópias são diagnósticos e não aprovam nem substituem o objeto.

---

## 13. Anexo A — Reconciliações documentais propostas (não aplicadas)

### A.1. Consolidação da Emenda F3-E1, já aprovada

| Documento | Ponto | Conteúdo a consolidar |
| --- | --- | --- |
| Prompt F3 | Nota histórica | Registrar a E1 (SHA-256 `9b3ae10b…a103`) sem reescrever a versão implementada (`c976854d…3536`), como foi feito com a F2-D1 |
| Prompt F3 | §8.7 | Retorno de sucesso com `_em_utc(rec.expira_em)` e definição de `_em_utc` |
| Prompt F3 | §11.1 | Item 5 conforme E1.1; constante `ESPERA_UPDATE_USUARIO`; portão com CT-F3-31 a 33 |
| Prompt F3 | §11.3, §12 e §15 | CT-F3-31 a 34; aceite de “01 a 34”; tabela do relatório |
| Arquitetura | §8.3.2 | O pseudocódigo deve continuar igual ao do prompt (com `_em_utc`) |
| Arquitetura | §6.6, linha 2 | Testes CT-F3-31 e 32 (C3 e C6); referência ao CT-F3-33 (C10) |
| Arquitetura | §7 | Instantes de resposta lidos do banco normalizados para UTC |
| Dossiê | §6.8 | Coluna de testes: C3 → CT-F3-31, C6 → CT-F3-32, C10 → CT-F3-33 |
| Dossiê | §7.2 | Linhas CT-F3-31 a 34; registro da E1 e desta auditoria |
| Plano de validação | Catálogo da F3 | CT-F3-31 a 34; total de **186** CTs (182 + 4); 10 de concorrência |
| Plano de fases | Ficha da F3, item 9 | CT-F3-01 a 34; concorrência: 05, 14, 15, 17, 19, 23, 27, 31, 32 e 33 |
| Matriz | Tela 3 (3 objetivo, 3.2, 3.3.1*) e R-RECUPERACAO | Incluir CT-F3-31 a 34 nas verificações |
| Índice | §4, §5 e §6 | Aprovação e encaminhamento da E1; esta auditoria e o veredito (G5 da F3); evidências; contagem de 186 CTs |

### A.2. Propostas novas, que exigem decisão

- **ACH-MV-F3-002:** ampliar a regra do nome (categorias `Zl` e `Zp`). Exige decisão sobre o contrato e uma correção dirigida, depois revalidação.
- **ACH-MV-F3-001:** restaurar o documento ausente ou registrar a remoção por decisão expressa.
- **Lição de processo (ACH-MV-F3-003):** nos próximos prompts, logs obrigatórios também para comandos de diagnóstico.

---

## 14. Próximo passo do usuário

1. **Resolver o ACH-MV-F3-001 antes do commit:** restaurar `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` com o SHA-256 `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695`, ou decidir pela remoção.
2. **Decidir o ACH-MV-F3-002:**
   - aceitar como P3 em acompanhamento; ou
   - autorizar a mudança de contrato e uma correção dirigida, com a revalidação da §10.
3. **Autorizar o fechamento documental** (Anexo A.1, mais o registro desta auditoria e das decisões acima).
4. **Fazer o commit da F3** com lista explícita: os 34 arquivos técnicos, os documentos da preparação, este relatório e a instrução de auditoria, se quiser versioná-la. Depois, informar o SHA para a conferência do G6.

A F4 continua fora do escopo até essas etapas e as decisões correspondentes (DEC-MV-14 no restante e DEC-MV-15).
