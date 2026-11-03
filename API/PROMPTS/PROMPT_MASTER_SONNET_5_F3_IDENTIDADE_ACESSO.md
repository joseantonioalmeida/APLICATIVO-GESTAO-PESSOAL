# Prompt Master — Sonnet 5 — F3: Identidade e acesso da API MinhaVida

| Campo | Valor |
| --- | --- |
| Fase | F3 — Identidade e acesso (`docs/arquitetura/plano_fases_api.md`) |
| Estado | **`PRONTO_PARA_ETAPA_A`** (2026-10-13). Autoriza somente a Etapa A (§13). Histórico: `BLOQUEADO — AGUARDANDO_DECISAO` até a aprovação M16 |
| Data | 2026-10-13 |
| Autor | Claude Opus 5.5 (arquitetura) |
| Destinatário | Claude Sonnet 5 (implementação) |
| Modo | LOCAL (WSL do usuário) |
| Baseline técnico | Commit da F2 `91be324c88c5a3f99a49b1b1700963e32ef257e9` (G6 cumprido em 2026-10-13) |
| Dossiê de origem | `docs/arquitetura/preparacao_f3_identidade_acesso.md` |
| Revisão | Revisão dirigida M15 (2026-10-13), aplicada antes da aprovação (dossiê §13) |
| Aprovações | M16 (2026-10-13), registrada no `indice.md` §4: DEC-MV-09 a 13 e DEC-MV-14 no escopo da F3; reconciliação documental aplicada (dossiê §14) |

> **Condições de liberação (cumpridas em 2026-10-13, M16).**
>
> 1. **Decisões:** DEC-MV-09, 10 (opção A), 11, 12 e 13 e DEC-MV-14 **no escopo limitado da F3** (travas de linha da recuperação) aprovadas, conforme o dossiê §4 e o `indice.md` §4. Este prompt segue exatamente essas escolhas.
> 2. **Reconciliação documental:** diffs do dossiê §8 aplicados: `CLAUDE.md` (só CM-1 e CM-2), ADR-0001 (AD-1 a AD-3), arquitetura (AR-1 a AR-10, com AR-8 revisto), plano de fases (PF-1), plano de validação (PV-1) e matriz (MZ-1).
> 3. **Liberação:** estado `PRONTO_PARA_ETAPA_A`. O usuário envia este arquivo com o SHA-256 informado na mensagem de liberação (este arquivo não contém o próprio hash). Os hashes dos documentos de preparação estão em §1.2.
> 4. **Implementação:** só depois da Etapa A e do “pode implementar” do usuário. “Preparar F3”, “aprovo a arquitetura”, “aprovo as decisões” e “conferi o commit” **não** substituem essa autorização.

---

## 0. Regras absolutas

1. **Etapa A** (§13): somente leitura. Não crie, altere nem formate arquivos do repositório, não instale dependências e não execute testes. Termine pedindo “pode implementar”.
2. **Etapa B** (§14): só depois do “pode implementar”. Execute os passos na ordem, com os comandos **exatamente** como escritos.
3. Nunca leia, copie, imprima, edite ou calcule hash do `.env` real. Não use dumps de ambiente.
4. Modo LOCAL: **proibido** `git add`, `git commit`, `git push`, `git merge`, `git reset`, `git checkout -- <arquivo>`, `git restore` e `git stash`. O commit é do usuário.
5. Não execute a suíte completa, `task test`, `task` de qualquer tipo, nem `pytest` sem as seleções de §14.
6. Pela CLI do Alembic, só `uv run --frozen --no-sync alembic heads`. Nenhum comando que execute o `alembic/env.py`, que sem `config.attributes["url_banco"]` leria o `.env`. A F3 não cria revisão.
7. Não execute Docker Compose: não há motivo na F3.
8. Dependências: só no passo 2 da Etapa B, com o comando literal. Depois dele, todo comando `uv run` usa `--frozen --no-sync`. Nenhum `uv sync`, `uv lock` ou `uv add` adicional.
9. Nenhum e-mail real e nenhuma conexão SMTP real. Os testes usam `EnviadorEmailMemoria` e `smtplib` simulado.
10. Logs: cada comando grava a saída completa e o `codigo_saida` em `$HOME/minhavida_evidencias/f3/`, na forma `comando > log 2>&1; echo "codigo_saida=$?" >> log`. Não use `| tee`, `| grep` ou qualquer pipeline que esconda o código do comando. Uma reexecução recebe um nome novo (sufixo `_2`, `_3`); nunca sobrescreva um log.
11. Proibidos: `# noqa`, `# type: ignore`, `# pyright: ignore` novos; mudanças em `[tool.ruff]`, `[tool.pyright]` ou `[tool.pytest.ini_options]`; mudança em modelos, revisão Alembic, esquema, `compose.yaml` ou `alembic.ini`.
12. **Regra e modelo coerentes:** os blocos marcados “conteúdo exato” já passaram em `ruff check`, `ruff format --check` e Pyright com a configuração real do repositório. Copie-os sem alteração. Os demais blocos são **contrato** (nomes, assinaturas e comportamento obrigatórios) ou **pseudocódigo** (comportamento obrigatório, sintaxe livre) e estão identificados como tal.
13. Nunca registre em log senha, código, token (JWT ou de redefinição), hashes, e-mail ou nome. Usuário só por `usuario_id`.
14. Não se declare aprovado. Ao final, pare para a auditoria independente do Opus (§16).

---

## 1. Estado de partida

### 1.1. Baseline técnico (commit `91be324`)

| Arquivo | SHA-256 no baseline | Situação na F3 |
| --- | --- | --- |
| `pyproject.toml` | `93932958ba2547476637b3cf75c37ba403c324ec6a1c7dd4763183dbdacba721` | Alterado só pelo `uv add` (§14, passo 2) |
| `uv.lock` | `b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d` | Idem |
| `.env.exemplo` | `dc824d5228126e5cfa2ef3c6fe3c939fb99fc3303487109bd1d0c443867dfdb0` | Acréscimo exato (§9.2) |
| `src/api_gestao_pessoal/settings.py` | `039937f6322149f5ac87b586192e68418c29a562a0e2419f90669120192dd0f0` | Alterado (§9.1) |
| `src/api_gestao_pessoal/erros.py` | `4e8adcce3eb13b78462c6cbdb96fb3cae39c1758b645c1b24d7c9f9f7bb63836` | Alterado (§10.3) |
| `src/api_gestao_pessoal/main.py` | `bb566f5402050cd6dd60bc581bf17e6925415cc256775f5210f5cfea45e263ee` | Alterado (§8.10) |
| `tests/conftest.py` | `a385540392111aee5e93a6ee6e413b31fede746a8fef63466e44064122d6608e` | Alterado (§11.1) |
| `tests/infra/test_configuracao.py` | `4c2106538fe287e5e415ae02117dc2047523d31723d038354c57fe958c2f4830` | Alterado (§11.1) |
| `src/api_gestao_pessoal/database.py` | `50ab98141652b19a5ba21e690e6d6dacc74aa24b5803764e8c2541388d297def` | Protegido |
| `src/api_gestao_pessoal/rastreamento.py` | `b92bb3c80336d23687aa2330c9fa75707a99620acd5f0e39b1acc9897972fc37` | Protegido |
| `src/api_gestao_pessoal/schemas/erro.py` | `df9c3382d0e5fed29a0f1347354b0cd5cb4b43e142a9944d0f85b90acf63bf5b` | Protegido |
| `src/api_gestao_pessoal/routers/saude.py` | `5fbda750f3739079ea11d5a9a2b114fa795e2db1c4aa6f34786e1d89884d4b32` | Protegido |
| `src/api_gestao_pessoal/routers/__init__.py` | `b58e215bbb12c600de95a10edfb92534199cf042afb39fc67c8ad38e75d06ee5` | Protegido |
| `src/api_gestao_pessoal/schemas/__init__.py` | `5c94fe6bbe63e2782be904b7373d7b90826b1abfd791ebdac7e9ffb1a60e8dc3` | Protegido |
| `src/api_gestao_pessoal/models/__init__.py` | `c33e390a03f64aa05bf9ce8df4f343caae07ba32da7d8d0cbac650497542280d` | Protegido |
| `src/api_gestao_pessoal/models/usuario.py` | `bd0872b242e7eba7ec090fb0bce23ac2c7deda36d38ffae0e70849a3e731ef0a` | Protegido |
| `src/api_gestao_pessoal/models/recuperacao_senha.py` | `2c75f3b4f96ff9e160648d4e2fe4cf176f58444bc8ecf5faf4a41de1f3cd7d25` | Protegido |
| `alembic/versions/20261013_0001_esquema_inicial.py` | `da1d0f38b161d26021f9242c1d5291d8cc0d4ef8d4f64b4c56c4155875150a24` | Protegido |
| `alembic/env.py` | `10563c24868c0921987c9953ad1f3f12915aedc82bdfc5ec59ef9013b5fe55c1` | Protegido |
| `tests/infra/conftest.py` | `f94ccc8eabd61e6bccb820035206c26c4011415a361cf71ae7baa330e06115ef` | Protegido |
| `tests/infra/test_erros.py` | `c0fd9e88367c98ec7a4f0f0fc443e3e1860ee740847595a779f7e7d4a4ed4276` | Protegido (regressão) |
| `tests/infra/test_saude.py` | `c90b30bfd099a22e008cf0fb7485fcb731d08e04cc0e1c1bf0c09068f8ddcacd` | Protegido (regressão) |
| `tests/infra/test_sessao_transacao.py` | `502570597f404f88bf894aea3aa0779466969f6cb5ac3ff871977bde152aea19` | Protegido (regressão) |
| `tests/apoio/banco.py` | `58fce75d41d2a427812ce317c83bb0864336a37327f28f211ee0d7197f85a94a` | Protegido |
| `tests/apoio/esquema.py` | `318580362b0412b6e2dea3b6b0e9faf3cc9b9ed2960903723682837718b4ceeb` | Protegido |
| `tests/apoio/rotas_teste.py` | `6982ec6299e05ae5af5ce5cb73c746b6b07ae11ff531ccf060ebebdb2567e59a` | Protegido |

Fatos do ambiente (verificados em 2026-10-13):

- Python 3.14.6, uv 0.11.29, Docker 29.7.2, imagem `postgres@sha256:fe0737ba566a2c5b2a28f34433c0a423261900ec17b9bf7ad115e1aae7e57f1b`.
- No lock: `pydantic 2.13.5`, `fastapi 0.143.0`, `starlette 1.7.0`, `anyio 4.15.1`, `email-validator 2.3.0`, `sqlalchemy 2.1.4`, `psycopg 3.3.6`.
- `PyJWT`, `argon2-cffi` e `argon2-cffi-bindings` **não** estão no lock.
- `tzdata 2026.5` está no lock, mas não instalado no Linux.

### 1.2. Preparação documental

O baseline técnico é o commit `91be324`. Por cima dele, existem **somente** alterações documentais autorizadas pelo usuário (M14 a M16): a preparação, a revisão dirigida e a reconciliação da liberação (diffs do dossiê §8). São exatamente estes arquivos, além deste prompt, cujo hash vem na mensagem de liberação:

| Documento | SHA-256 na liberação |
| --- | --- |
| `CLAUDE.md` | `515dd70023275e566b65a762804964a875144f222d0f46c3a76931f49c6c112a` |
| `docs/adr/0001_arquitetura_api_minhavida.md` | `74a9b6bfb50200816e9f126f147896f206962711c490867b70e27a342735474f` |
| `docs/arquitetura/analise_projeto_minhavida.md` | `192090a845e7ed9fd1d2248183ba0f99bd0cccdab14236f384da025cb3add4a3` |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `a2630f21f6360968daebbeb226906e66835404521d7df2bca185f352d31dc242` |
| `docs/arquitetura/indice.md` | `53c4995947e50b82141641e0333be1dc9e2c8dec08a9736d2004da287d2a39c4` |
| `docs/arquitetura/matriz_requisitos_api.md` | `dc681cac8c32bc9c4ff6d6e67100f30123705e9eb81c19ef381aac210c6a9c58` |
| `docs/arquitetura/plano_fases_api.md` | `54ccbab4346c926607f867a993d17a8b2d4e9ad40b47995f0dbe4dd76bb98876` |
| `docs/arquitetura/plano_validacao_auditoria.md` | `de8d8c848001af5f44a900da875cdf710265f7d4e72c0a99213f4eca374e7690` |
| `docs/arquitetura/preparacao_f3_identidade_acesso.md` | `62ffd7250e5262d9bead12551ba654694aab2f446b4dc2565290e3c0b7e59af2` |
| `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` | `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695` |

| Modo | Condição |
| --- | --- |
| A — sem commit documental | `git rev-parse HEAD` = `91be324c88c5a3f99a49b1b1700963e32ef257e9`. `git status --porcelain --untracked-files=all` lista exatamente os documentos da tabela acima e este prompt |
| B — com commit documental do usuário | `git diff --name-only 91be324c88c5a3f99a49b1b1700963e32ef257e9 HEAD` lista só documentos da tabela acima e este prompt (todos em `docs/`, `PROMPTS/` ou `CLAUDE.md`). `git status` vazio |

Nos dois modos, os arquivos de §1.1 têm os hashes da tabela de §1.1, e os documentos têm os hashes da tabela acima. Qualquer outra situação é divergência: **pare** e relate.

### 1.3. Revalidação no início da Etapa B

Antes de qualquer alteração, grave em `$HOME/minhavida_evidencias/f3/00_revalidacao.log`:

- (a) `git rev-parse HEAD` e o modo;
- (b) `git status --porcelain --untracked-files=all`;
- (c) `sha256sum` dos arquivos de §1.1;
- (d) `sha256sum` dos documentos de §1.2 e deste prompt.

Tudo precisa coincidir com a Etapa A. Se só um documento irrelevante para a F3 mudou por autorização do usuário, registre o delta e reavalie só o que ele afeta. Se algo técnico mudou, **pare**.

---

## 2. Fontes normativas e precedência

Leia, nesta ordem, registrando o SHA-256 de cada uma:

1. `CLAUDE.md`: §1 e §2; telas 1, 2, 3 e 4.1.1; tabelas 1 (`usuario`) e 2 (`recuperacao_senha`).
2. `docs/arquitetura/indice.md`: §3 (precedência), §4 (aprovações, inclusive as da F3) e §5.
3. `docs/adr/0001_arquitetura_api_minhavida.md`: D-04, D-05 (só as travas da recuperação), D-07, D-08, D-13 e D-15. `docs/adr/0002_identificadores_uuid.md`.
4. `docs/arquitetura/arquitetura_api_minhavida.md`: §2.1, §2.2, §3.1, §3.4, §4.1, §4.2, §4.4, §4.5, §5, §6.2, §6.3, §6.5, §6.6, §7, §8.2, §8.3, §9.1 e §11.
5. `docs/arquitetura/preparacao_f3_identidade_acesso.md`: integral.
6. `docs/arquitetura/plano_validacao_auditoria.md`: §2, §3 e catálogo F3. `docs/arquitetura/plano_fases_api.md`: ficha F3.
7. `docs/arquitetura/matriz_requisitos_api.md`: telas 1, 2, 3 e 4.1.1.
8. Este prompt.

Precedência: instruções explícitas do usuário > `CLAUDE.md` > ADRs aceitos > documentos de arquitetura e planos > dossiê > este prompt. Uma divergência entre este prompt e uma fonte superior é **bloqueio**: pare e relate, sem escolher sozinho.

---

## 3. Decisões, aprovações necessárias e reconciliações

| Item | Conteúdo seguido por este prompt | Estado |
| --- | --- | --- |
| DEC-MV-09 | Dossiê §4.1 (R9.1–R9.9, inclusive o e-mail canônico da R9.9) | **Aprovada** em 2026-10-13 (M16, item 1) |
| DEC-MV-10 | Opção A: 404 `EMAIL_NAO_ENCONTRADO`, com o risco aceito | **Aprovada** em 2026-10-13 (M16, item 2) |
| DEC-MV-11 | Dossiê §4.3 (R11.1–R11.10) | **Aprovada** em 2026-10-13 (M16, item 3) |
| DEC-MV-12 | Dossiê §4.4 e §6.3 | **Aprovada** em 2026-10-13 (M16, item 4) |
| DEC-MV-13 | Só `GET /api/v1/usuarios/me` | **Aprovada** em 2026-10-13 (M16, item 5) |
| DEC-MV-14 (escopo limitado F3) | Dossiê §4.6 | **Aprovada** só nesse escopo em 2026-10-13 (M16, item 6). O restante continua pendente |
| Aprovadas antes | DEC-MV-01 a 08, 25 e 26 | Aprovadas |
| Reconciliações | ACH-MV-ARQ-026 a 038 (dossiê §5.2), por meio dos diffs da §8 do dossiê, inclusive CM-2, AR-8 revisto e AR-10 da revisão M15 | Aplicadas e encerradas em 2026-10-13 (M16; dossiê §14) |
| Organização dos services | ADR-0001 D-02 vigente: nenhum service importa outro na F3 (§8.5) | Contrato vigente, sem exceção. DEC-MV-24 continua pendente para a F5 |

Atualizada na liberação (M16), conforme o `indice.md` §4.

---

## 4. Escopo, exclusões e fronteira com a F4

**Dentro do escopo:**

1. Seis endpoints (§10.2): registro, login, solicitar, verificar e redefinir a recuperação, e `GET /usuarios/me`.
2. Suporte: `tempo.py`, `seguranca.py`, `email.py`, `dependencias.py` e `services/autorizacao.py`.
3. Services `identidade` e `recuperacao_senha`; schemas `autenticacao` e `usuario`; routers `autenticacao` e `usuarios`.
4. Settings da F3, códigos de erro da F3, inclusão dos routers no `main.py`.
5. Dependências do passo 2 (§9.3).
6. Testes `tests/identidade/`, apoio `tests/apoio/relogio.py` e `tests/apoio/identidade.py`, ajustes de `tests/conftest.py` e `tests/infra/test_configuracao.py` (§11.1).

**Fora do escopo:**

- trava consultiva por usuário, `services/trava.py`, idempotência, paginação, catálogos (F4);
- endpoints de domínio (F5+);
- refresh token, logout no servidor, lista de sessões, troca de senha autenticada, edição de perfil, troca de e-mail ou de fuso, exclusão de conta;
- limitação de login ou de requisições (DEC-MV-21, F11);
- CORS, cookies, cabeçalhos de segurança gerais;
- fila, outbox, retry de e-mail, provedor HTTP de e-mail, push;
- qualquer mudança de esquema, modelo ou migração;
- qualquer integração financeira externa (arquitetura §1.1).

**Fronteira com a F4:** a F3 usa somente `SELECT … FOR UPDATE` em `recuperacao_senha` e `INSERT … ON CONFLICT` na primeira emissão. A rota de teste de `obter_do_usuario_ou_404` lê uma importância criada por SQL nos testes; isso **não** autoriza endpoints de importâncias.

---

## 5. Política de testes

- PostgreSQL real descartável via Testcontainers (`postgres:15-alpine`), construído pela migração da F2 (`banco_migrado`). Nunca SQLite, nunca `create_all`.
- Concorrência: requisições HTTP independentes, cada uma com sua sessão e conexão. Portão de largada com uma conexão bloqueadora e `aguardar_espera_por_trava` (§11.1), que exige o número **exato** de requisições paradas na trava esperada; sem `sleep`. O `aguardar_bloqueio` genérico da F2 não é usado na F3. Verificação final por **outra conexão** (`tests/apoio/esquema.py::consultar`).
- Tempo: `RelogioFixo` (§11.2) injetado por `app.dependency_overrides[obter_relogio]`. Limites exatos com `avancar`. Nunca esperar tempo real.
- Argon2 real com parâmetros de teste (1 / 8 KiB / 1) em `settings_teste`, e **um** teste com os parâmetros de produção (CT-F3-29).
- E-mail: `EnviadorEmailMemoria` injetado por `dependency_overrides[obter_enviador_email]`. `smtplib` simulado por `monkeypatch` só no CT-F3-28.
- Fixtures herméticas: `SettingsTeste` (sem `.env` e sem ambiente), segredo sintético.
- Logs: `caplog` **e** um handler de teste com o formato real (`FORMATO_LOG` e `FiltroIdRequisicao`), incluindo exceções.
- Nenhum teste compara tempos de resposta. Nenhum `skip` ou `xfail`. Docker indisponível é **bloqueio**.
- Ao falhar: o mesmo teste → correção dentro do escopo → o mesmo teste → a seleção da fase. Sem reexecução por rotina.

---

## 6. Banco, transações, concorrência e efeitos externos

### 6.1. Fronteira transacional

| Endpoint | Leitura | Escrita | Commit |
| --- | --- | --- | --- |
| Registro | `usuario` por e-mail | `INSERT usuario` e `flush` (`IntegrityError` em `uq_usuario_email` → 409) | Router, depois do service |
| Login | `usuario` por e-mail | Nenhuma | Nenhum (o `close` desfaz a leitura) |
| Solicitar | `usuario`; `recuperacao_senha` `FOR UPDATE` | `INSERT … ON CONFLICT DO NOTHING` ou `UPDATE` e `flush` | Router, depois do envio |
| Verificar | `recuperacao_senha` com junção em `usuario`, `FOR UPDATE OF recuperacao_senha` | `tentativas + 1` ou `verificado_em`/token | Router **sempre**, e então lança o erro (arquitetura §5.3) |
| Redefinir | `recuperacao_senha` por `token_redefinicao_hash` `FOR UPDATE`; `usuario` por id | `senha_hash`; `utilizado_em` | Router |
| `GET /usuarios/me` | `usuario` por `sub` | Nenhuma | Nenhum |

Services nunca executam `commit`, `rollback`, `begin` ou `close`. Nenhum handler faz commit.

### 6.2. Instantes

- Contexto autenticado: `agora = relogio.agora()` capturado **uma vez** em `obter_contexto`, antes de decodificar o token.
- Login e registro: uma captura no service.
- Recuperação: uma captura **depois** de obter a trava da linha. Na primeira emissão, captura imediatamente antes do `INSERT`; se o `INSERT` não inserir, nova captura depois do `FOR UPDATE` (R11.2).

### 6.3. Corridas e garantias

| # | Corrida | Resultado obrigatório |
| --- | --- | --- |
| C1 | Dois registros com o mesmo e-mail | Um 201 e um 409; uma linha |
| C2 | Duas primeiras solicitações (sem linha) | O segundo `INSERT … ON CONFLICT` espera o primeiro. Depois: `DO NOTHING` → `FOR UPDATE` → 429. Se a espera passar de 5 s: 503 `CONFLITO_CONCORRENCIA`. Uma linha, um e-mail |
| C3 | Dois reenvios | Um código novo; o outro recebe 429 |
| C4 | Duas verificações corretas | Um 200 e um 409; um token |
| C5 | Cinco inválidas | `tentativas == 5` exato; cinco respostas 400 |
| C6 | Correta × limite (`tentativas = 4`) | Igual a uma ordem serial |
| C7 | Reenvio × verificação do código antigo | Ordem serial. Depois do reenvio confirmado, o código antigo é inválido e conta como tentativa da nova emissão |
| C8 | Duas redefinições com o mesmo token | Um 200 e um 400; uma troca |
| C9 | Reenvio × redefinição | Ordem serial. Depois do reenvio confirmado, o token dá 400 |
| C10 | Login ou autenticação × redefinição | Sem travas. A partir do commit da redefinição, todo token com o `sv` antigo recebe 401 no próximo uso. Requisições em andamento não são canceladas |
| C11 | Falha de envio | 503 `FALHA_ENVIO_EMAIL`; rollback; repetição imediata permitida |
| C12 | Commit falha depois do envio | 5xx; banco inalterado; o e-mail entregue tem código sem valor |

### 6.4. E-mail (consequências aceitas na DEC-MV-12)

O envio ocorre dentro da transação, antes do commit. Não há atomicidade com o e-mail: um código pode chegar sem valor (situações 2 a 5 do dossiê §4.4).

- `SMTP_TIMEOUT_S` vale por operação de socket.
- `lock_timeout` (5 s) atinge quem espera a linha durante um envio lento.
- `idle_in_transaction_session_timeout` (30 s) encerra a sessão se o envio passar desse total.

Não implemente retry, fila ou compensação.

---

## 7. Arquivos

### 7.1. Criar

```text
src/api_gestao_pessoal/tempo.py                      conteúdo exato (§8.1)
src/api_gestao_pessoal/seguranca.py                  contrato (§8.2, §8.3)
src/api_gestao_pessoal/email.py                      contrato (§8.4)
src/api_gestao_pessoal/dependencias.py               contrato (§8.10)
src/api_gestao_pessoal/services/__init__.py          docstring: """Services da API MinhaVida."""
src/api_gestao_pessoal/services/identidade.py        contrato (§8.5)
src/api_gestao_pessoal/services/recuperacao_senha.py contrato (§8.6–§8.8)
src/api_gestao_pessoal/services/autorizacao.py       contrato (§8.9)
src/api_gestao_pessoal/schemas/autenticacao.py       contrato (§10.1)
src/api_gestao_pessoal/schemas/usuario.py            contrato (§10.1)
src/api_gestao_pessoal/routers/autenticacao.py       contrato (§10.2)
src/api_gestao_pessoal/routers/usuarios.py           contrato (§10.2)
tests/apoio/relogio.py                               conteúdo exato (§11.2)
tests/apoio/identidade.py                            contrato (§11.1)
tests/identidade/__init__.py                         vazio
tests/identidade/conftest.py                         contrato (§11.1)
tests/identidade/rotas_teste_identidade.py           contrato (§11.1)
tests/identidade/test_configuracao_identidade.py     §11.3
tests/identidade/test_seguranca.py                   §11.3
tests/identidade/test_email.py                       §11.3
tests/identidade/test_registro.py                    §11.3
tests/identidade/test_login.py                       §11.3
tests/identidade/test_usuario_atual.py               §11.3
tests/identidade/test_recuperacao.py                 §11.3
tests/identidade/test_recuperacao_concorrencia.py    §11.3
tests/identidade/test_vazamento.py                   §11.3
```

### 7.2. Alterar

| Arquivo | Alteração permitida, e nada além |
| --- | --- |
| `pyproject.toml`, `uv.lock` | Só o efeito do comando do passo 2 (§9.3) |
| `.env.exemplo` | Acréscimo exato ao final (§9.2) |
| `src/api_gestao_pessoal/settings.py` | Campos e validadores de §9.1 |
| `src/api_gestao_pessoal/erros.py` | Membros de `CodigoErro` e entradas de `CATALOGO_ERROS` de §10.3. Nada mais |
| `src/api_gestao_pessoal/main.py` | `lifespan` e `include_router` (§8.10) |
| `tests/conftest.py` | Só `settings_teste` e as constantes de §11.1 |
| `tests/infra/test_configuracao.py` | Só as edições exatas de §11.1 |

### 7.3. Protegidos

- Todo `src/api_gestao_pessoal/models/`, `alembic/`, `alembic.ini`, `compose.yaml`, `.gitignore`, `.python-version` e `README.md`.
- `database.py`, `rastreamento.py`, `schemas/erro.py`, `schemas/saude.py`, `routers/saude.py` e os `__init__.py` existentes.
- `tests/esquema/`, `tests/apoio/banco.py`, `tests/apoio/esquema.py`, `tests/apoio/migracoes.py`, `tests/apoio/rotas_teste.py` e os arquivos de `tests/infra/` exceto `test_configuracao.py`.
- `docs/`, `PROMPTS/` e `CLAUDE.md`.

Precisar de um arquivo fora destas listas é **bloqueio**.

---

## 8. Algoritmos e contratos

### 8.1. `tempo.py` (conteúdo exato)

`ContextoUsuario` fica aqui, e não num service, porque é o contexto temporal de D-13 e porque D-02 proíbe importações entre services fora dos módulos de suporte que lista.

```python
"""Relógio da aplicação, contexto da requisição e utilidades de fuso (D-13)."""

import functools
import uuid
import zoneinfo
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol, override

FUSOS_EXCLUIDOS = frozenset({"localtime", "posixrules", "Factory"})
PREFIXOS_EXCLUIDOS = ("posix/", "right/")
TAMANHO_MAXIMO_FUSO = 64


class Relogio(Protocol):
    """Fonte única do instante atual da aplicação."""

    def agora(self) -> datetime:
        """Instante atual, sempre com fuso UTC."""
        ...


class RelogioSistema(Relogio):
    """Relógio real da aplicação, em UTC."""

    @override
    def agora(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ContextoUsuario:
    """Usuário autenticado e instante da requisição, capturados uma vez."""

    usuario_id: uuid.UUID
    fuso: zoneinfo.ZoneInfo
    agora: datetime
    hoje: date


@functools.cache
def _fusos_disponiveis() -> frozenset[str]:
    return frozenset(zoneinfo.available_timezones())


def fuso_valido(chave: str) -> bool:
    """Chave IANA aceita no cadastro (arquitetura §7)."""
    return (
        0 < len(chave) <= TAMANHO_MAXIMO_FUSO
        and chave not in FUSOS_EXCLUIDOS
        and not chave.startswith(PREFIXOS_EXCLUIDOS)
        and chave in _fusos_disponiveis()
    )


def hoje_no_fuso(instante: datetime, fuso: zoneinfo.ZoneInfo) -> date:
    """Data civil do instante no fuso informado."""
    return instante.astimezone(fuso).date()
```

### 8.2. `seguranca.py`: Argon2 e utilitários (contrato)

- Constantes: `TAMANHO_SV = 16`; `PADRAO_SV = re.compile(r"^[0-9a-f]{16}$")`; `ALGORITMO_JWT = "HS256"`; `TIPO_TOKEN = "access"`; `CLAIMS_TOKEN = frozenset({"sub", "iat", "exp", "typ", "sv"})`; `TAMANHO_MAXIMO_TOKEN = 4096`.
- `@dataclass(frozen=True, slots=True) class ParametrosArgon2`: `time_cost: int`, `memory_cost_kib: int`, `parallelism: int`.
- `class HashArmazenadoInvalido(Exception)`: sem argumentos que contenham dados.
- `class HasherSenha`:
  - `__init__(self, parametros: ParametrosArgon2, limitador: anyio.CapacityLimiter) -> None`: cria `argon2.PasswordHasher(time_cost=…, memory_cost=…, parallelism=…, hash_len=32, salt_len=16, type=argon2.Type.ID)`;
  - `async gerar(self, segredo: str) -> str`;
  - `async verificar(self, hash_armazenado: str, segredo: str) -> bool`: `True` se casar; `False` só para `argon2.exceptions.VerifyMismatchError`. Qualquer outra exceção do argon2 (`VerificationError`, `InvalidHashError`) vira `HashArmazenadoInvalido` **`from None`**;
  - `async preparar_ficticio(self) -> None`: calcula e guarda o hash de `secrets.token_urlsafe(32)`;
  - `async verificar_ficticio(self, segredo: str) -> None`: verifica contra o hash fictício e descarta o resultado.

  Toda operação de hash ou verificação roda em `anyio.to_thread.run_sync(função, *args, abandon_on_cancel=False, limiter=self._limitador)`. Nenhuma chamada usa `check_needs_rehash`.
- `def carimbo(senha_hash: str) -> str`: `hashlib.sha256(senha_hash.encode()).hexdigest()[:TAMANHO_SV]`.
- `def gerar_codigo() -> str`: `f"{secrets.randbelow(10**8):08d}"`. Os services chamam **`seguranca.gerar_codigo()`** pelo módulo (`from api_gestao_pessoal import seguranca`), para o teste substituir com `monkeypatch.setattr(seguranca, "gerar_codigo", lambda: "00012345")`.
- `def gerar_token_redefinicao() -> str`: `secrets.token_urlsafe(32)`.
- `def hash_token(token: str) -> str`: `hashlib.sha256(token.encode()).hexdigest()`.

### 8.3. `seguranca.py`: JWT (contrato)

- `class TokenInvalido(Exception)`, sem dados.
- `@dataclass(frozen=True, slots=True) class TokenEmitido`: `token: str`, `expira_em: datetime`.
- `@dataclass(frozen=True, slots=True) class ClaimsToken`: `usuario_id: uuid.UUID`, `sv: str`.
- `def emitir_token(usuario_id: uuid.UUID, senha_hash: str, agora: datetime, configuracao: ConfiguracaoToken) -> TokenEmitido`, em que `ConfiguracaoToken` é uma dataclass imutável de `seguranca.py` com `segredo: SecretStr` e `validade: timedelta`:
  - `base = agora.replace(microsecond=0)`; `iat = int(base.timestamp())`; `exp = iat + int(configuracao.validade.total_seconds())`;
  - `token = jwt.encode({"sub": str(usuario_id), "iat": iat, "exp": exp, "typ": TIPO_TOKEN, "sv": carimbo(senha_hash)}, configuracao.segredo.get_secret_value(), algorithm=ALGORITMO_JWT)`;
  - `expira_em = datetime.fromtimestamp(exp, UTC)`.
- `def decodificar_token(token: str, agora: datetime, configuracao: ConfiguracaoToken) -> ClaimsToken`:
  1. `jwt.decode(token, segredo, algorithms=[ALGORITMO_JWT], options={"verify_signature": True, "verify_exp": False, "verify_iat": False, "verify_nbf": False, "verify_aud": False, "verify_iss": False, "require": ["sub", "iat", "exp", "typ", "sv"]})`. Qualquer `jwt.InvalidTokenError` vira `TokenInvalido` `from None`.
  2. Validação manual; qualquer falha vira `TokenInvalido`:
     - `set(payload) == CLAIMS_TOKEN`;
     - `payload["typ"] == TIPO_TOKEN`;
     - `sub` é `str` e `str(uuid.UUID(sub)) == sub` (`ValueError` → inválido);
     - `type(iat) is int` e `type(exp) is int` (recusa `bool`, `float` e `str`);
     - `0 < exp - iat <= int(configuracao.validade.total_seconds())`;
     - `iat <= agora.timestamp() < exp`;
     - `sv` é `str` e `PADRAO_SV.fullmatch(sv)`.
  3. Devolve `ClaimsToken(usuario_id=uuid.UUID(sub), sv=sv)`.
- O PyJWT não injeta relógio e, desde a 2.6, rejeita `iat` no futuro pelo relógio real. Por isso as três verificações temporais da biblioteca ficam **desligadas** e são substituídas pela validação manual (ACH-MV-ARQ-026). O passo 3 de §14 confirma esse comportamento na versão instalada.

### 8.4. `email.py` (contrato e texto exato)

- `@dataclass(frozen=True, slots=True) class MensagemEmail`: `destinatario: str`, `assunto: str`, `corpo: str`.
- `class FalhaEnvioEmail(Exception)`: `__init__(self, motivo: str)` e atributo `motivo` (nome da classe da causa). A mensagem da exceção é só o motivo.
- `class EnviadorEmail(Protocol)`: `async def enviar(self, mensagem: MensagemEmail) -> None`.
- `class EnviadorEmailMemoria(EnviadorEmail)`:
  - `enviadas: collections.deque[MensagemEmail]` com `maxlen=100`;
  - `falha_programada: FalhaEnvioEmail | None = None`;
  - `enviar`: se houver falha programada, limpa-a e a lança; senão, acrescenta a mensagem.
- `class EnviadorEmailSmtp(EnviadorEmail)`: `__init__(self, settings: Settings)`. `enviar` chama `anyio.to_thread.run_sync(self._enviar_sincrono, mensagem, abandon_on_cancel=False)` (limitador padrão). `_enviar_sincrono`:
  1. Monta `email.message.EmailMessage()`: `From = email.utils.formataddr(("MinhaVida", SMTP_REMETENTE))`, `To = destinatario`, `Subject = assunto`, `set_content(corpo)`.
  2. `contexto = ssl.create_default_context()` (nunca desligar a verificação).
  3. `tls`: `smtplib.SMTP_SSL(host, porta, timeout=SMTP_TIMEOUT_S, context=contexto)`. `starttls` ou `nenhuma`: `smtplib.SMTP(host, porta, timeout=SMTP_TIMEOUT_S)`.
  4. Dentro de `with cliente:`: em `starttls`, `cliente.starttls(context=contexto)` e `cliente.ehlo()`; com credenciais, `cliente.login(usuario, senha)`; depois `cliente.send_message(msg)`.
  5. Captura `smtplib.SMTPException`, `OSError` (inclui `ssl.SSLError` e `TimeoutError`), `UnicodeError` e `ValueError` → `logger.warning("falha no envio de e-mail: motivo=%s codigo_smtp=%s", type(erro).__name__, getattr(erro, "smtp_code", "-"))` e `raise FalhaEnvioEmail(type(erro).__name__) from None`. Nunca registra destinatário, assunto, corpo ou resposta do servidor.
- `def criar_enviador(settings: Settings) -> EnviadorEmail`: `EnviadorEmailMemoria()` com `EMAIL_MODO == "memoria"`; senão, `EnviadorEmailSmtp(settings)`.
- `def mensagem_codigo(nome: str, email: str, codigo: str) -> MensagemEmail`, com assunto `f"{nome}, aqui está seu código"` e corpo, **texto exato** (3.4.4), linhas separadas por `\n` e terminado em `\n`:

```text
Olá, {nome}.
Recebemos uma solicitação para redefinir a senha de sua conta MinhaVida.
{codigo}
Insira este código para concluir a redefinição.
Obrigado por nos ajudar a manter sua conta segura.
Equipe MinhaVida.
```

### 8.5. `services/identidade.py` (contrato e pseudocódigo)

Regras de organização (ADR-0001 D-02, que prevalece sobre a matriz da arquitetura §2.2 até a DEC-MV-24):

- **nenhum service importa outro service na F3**;
- as dependências chegam como parâmetros explícitos, no máximo 5 por função (PLR0913 e PLR0917);
- `ContextoUsuario` vem de `tempo.py` (§8.1);
- `canonicalizar_email` vem de `schemas/autenticacao.py` (§10.1); services importam schemas, conforme D-02.

Assinaturas (contrato):

- `registrar(sessao: AsyncSession, dados: RegistroEntrada, relogio: Relogio, hasher: HasherSenha) -> UsuarioResposta`
- `entrar(sessao: AsyncSession, dados: LoginEntrada, relogio: Relogio, hasher: HasherSenha, configuracao: ConfiguracaoToken) -> TokenResposta`
- `montar_contexto(sessao: AsyncSession, token: str, agora: datetime, configuracao: ConfiguracaoToken) -> ContextoUsuario`
- `obter_usuario_atual(sessao: AsyncSession, contexto: ContextoUsuario) -> UsuarioResposta`
- `CABECALHO_BEARER = {"WWW-Authenticate": "Bearer"}`

Pseudocódigo normativo:

```python
async def registrar(sessao, dados, relogio, hasher):
    agora = relogio.agora()
    if dados.data_nascimento > hoje_no_fuso(agora, ZoneInfo(dados.fuso_horario)):
        raise ErroNegocio(VALIDACAO, campos=[CampoErro(campo="data_nascimento",
            codigo="DATA_NASCIMENTO_FUTURA", mensagem=MENSAGEM_NASCIMENTO_FUTURO)])
    if await sessao.scalar(select(Usuario.id).where(Usuario.email == dados.email)) is not None:
        raise ErroNegocio(EMAIL_JA_CADASTRADO)                 # dados.email já é canônico (R9.9)
    usuario = Usuario(nome_completo=..., email=dados.email, data_nascimento=..., fuso_horario=...,
                      senha_hash=await hasher.gerar(dados.senha))
    sessao.add(usuario)
    try:
        await sessao.flush()
    except IntegrityError as erro:
        if erro.orig.diag.constraint_name == "uq_usuario_email":   # psycopg 3
            raise ErroNegocio(EMAIL_JA_CADASTRADO) from None
        raise
    return UsuarioResposta(id=usuario.id, nome_completo=..., email=..., data_nascimento=..., fuso_horario=...)

async def entrar(sessao, dados, relogio, hasher, configuracao):
    email = canonicalizar_email(dados.email)                    # None: não canonicalizável
    usuario = None if email is None else await sessao.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:                                         # inexistente ou malformado: mesma resposta
        await hasher.verificar_ficticio(dados.senha)
        raise ErroNegocio(CREDENCIAIS_INVALIDAS)
    if not await hasher.verificar(usuario.senha_hash, dados.senha):
        raise ErroNegocio(CREDENCIAIS_INVALIDAS)
    emitido = emitir_token(usuario.id, usuario.senha_hash, relogio.agora(), configuracao)
    return TokenResposta(access_token=emitido.token, token_type="bearer", expira_em=emitido.expira_em)

async def montar_contexto(sessao, token, agora, configuracao):
    try:
        claims = decodificar_token(token, agora, configuracao)
    except TokenInvalido:
        raise ErroNegocio(NAO_AUTENTICADO, cabecalhos=CABECALHO_BEARER) from None
    usuario = await sessao.get(Usuario, claims.usuario_id)
    if usuario is None or not hmac.compare_digest(claims.sv, carimbo(usuario.senha_hash)):
        raise ErroNegocio(NAO_AUTENTICADO, cabecalhos=CABECALHO_BEARER)
    fuso = ZoneInfo(usuario.fuso_horario)
    return ContextoUsuario(usuario_id=usuario.id, fuso=fuso, agora=agora, hoje=hoje_no_fuso(agora, fuso))

async def obter_usuario_atual(sessao, contexto):
    usuario = await sessao.get(Usuario, contexto.usuario_id)    # mesmo objeto do mapa de identidade
    ...                                                        # None → RuntimeError (invariante)
```

A pré-checagem de e-mail evita o custo do hash no caso comum. A corrida (C1) é resolvida pela constraint. Um e-mail malformado no login segue o mesmo caminho do inexistente: hash fictício e 401 `CREDENCIAIS_INVALIDAS`, sem 422. `HashArmazenadoInvalido` no login **não** é tratado: vira 500 pelo handler genérico, sem dados.

### 8.6. `services/recuperacao_senha.py`: constantes e solicitar (pseudocódigo normativo)

```python
VALIDADE_CODIGO = timedelta(minutes=10)
MAX_TENTATIVAS = 5
INTERVALO_REENVIO = timedelta(seconds=60)

def _segundos_ate_reenvio(rec, agora) -> int:          # >= 1
    emitido_em = rec.expira_em - VALIDADE_CODIGO
    return max(1, math.ceil((emitido_em + INTERVALO_REENVIO - agora).total_seconds()))

def _reenvio_permitido(rec, agora) -> bool:
    return agora >= rec.expira_em - VALIDADE_CODIGO + INTERVALO_REENVIO

async def solicitar_codigo(sessao, dados, relogio, hasher, enviador) -> SolicitacaoCodigoResposta:
    usuario = await sessao.scalar(select(Usuario).where(Usuario.email == dados.email))
    if usuario is None:
        raise ErroNegocio(EMAIL_NAO_ENCONTRADO)
    rec = await _travar_por_usuario(sessao, usuario.id)      # SELECT … FOR UPDATE
    if rec is None:
        agora = relogio.agora()
        codigo = seguranca.gerar_codigo()
        novo_id = await sessao.scalar(
            pg_insert(RecuperacaoSenha)
            .values(id=uuid.uuid7(), usuario_id=usuario.id, tentativas=0,
                    codigo_hash=await hasher.gerar(codigo),
                    expira_em=agora + VALIDADE_CODIGO)
            .on_conflict_do_nothing(index_elements=["usuario_id"])
            .returning(RecuperacaoSenha.id))
        if novo_id is None:                                    # concorrente confirmou antes
            rec = await _travar_por_usuario(sessao, usuario.id)
    if rec is not None:
        agora = relogio.agora()
        if not _reenvio_permitido(rec, agora):
            raise ErroNegocio(REENVIO_MUITO_FREQUENTE,
                              cabecalhos={"Retry-After": str(_segundos_ate_reenvio(rec, agora))})
        codigo = seguranca.gerar_codigo()
        rec.codigo_hash = await hasher.gerar(codigo)
        rec.expira_em = agora + VALIDADE_CODIGO
        rec.tentativas = 0
        rec.verificado_em = rec.token_redefinicao_hash = rec.utilizado_em = None
    await sessao.flush()
    try:
        await enviador.enviar(mensagem_codigo(usuario.nome_completo, usuario.email, codigo))
    except FalhaEnvioEmail:
        raise ErroNegocio(FALHA_ENVIO_EMAIL) from None
    return SolicitacaoCodigoResposta(expira_em=agora + VALIDADE_CODIGO,
                                     reenvio_permitido_em=agora + INTERVALO_REENVIO)
```

`_travar_por_usuario` = `select(RecuperacaoSenha).where(RecuperacaoSenha.usuario_id == usuario_id).with_for_update()`. Assinaturas (contrato): `solicitar_codigo(sessao: AsyncSession, dados: SolicitarCodigoEntrada, relogio: Relogio, hasher: HasherSenha, enviador: EnviadorEmail)`; `verificar_codigo(sessao, dados: VerificarCodigoEntrada, relogio, hasher)`; `redefinir_senha(sessao, dados: RedefinirSenhaEntrada, relogio, hasher)`. Este módulo não importa nenhum service. Divida o código em funções auxiliares para respeitar PLR0911, PLR0912 e PLR0915; o comportamento é o do pseudocódigo.

### 8.7. Verificar (pseudocódigo normativo, arquitetura §5.3)

```python
@dataclass(frozen=True, slots=True)
class ResultadoVerificacao:
    erro: CodigoErro | None
    token: str | None = None
    expira_em: datetime | None = None
    retry_after_s: int | None = None

def _motivo_recusa(rec, agora) -> CodigoErro | None:
    if rec.verificado_em is not None or rec.utilizado_em is not None:
        return CODIGO_JA_VERIFICADO
    if agora >= rec.expira_em:
        return CODIGO_EXPIRADO
    if rec.tentativas >= MAX_TENTATIVAS:
        return TENTATIVAS_ESGOTADAS
    return None

async def verificar_codigo(sessao, dados, relogio, hasher) -> ResultadoVerificacao:
    rec = await sessao.scalar(
        select(RecuperacaoSenha).join(Usuario, Usuario.id == RecuperacaoSenha.usuario_id)
        .where(Usuario.email == dados.email).with_for_update(of=RecuperacaoSenha))
    if rec is None:
        return ResultadoVerificacao(erro=CODIGO_INVALIDO)        # sem usuário ou sem emissão
    agora = relogio.agora()
    motivo = _motivo_recusa(rec, agora)
    if motivo is TENTATIVAS_ESGOTADAS:
        return ResultadoVerificacao(erro=motivo, retry_after_s=_segundos_ate_reenvio(rec, agora))
    if motivo is not None:
        return ResultadoVerificacao(erro=motivo)
    if not await hasher.verificar(rec.codigo_hash, dados.codigo):
        rec.tentativas += 1
        await sessao.flush()
        return ResultadoVerificacao(erro=CODIGO_INVALIDO)        # inclusive a 5ª
    token = seguranca.gerar_token_redefinicao()
    rec.verificado_em = agora
    rec.token_redefinicao_hash = seguranca.hash_token(token)
    await sessao.flush()
    return ResultadoVerificacao(erro=None, token=token, expira_em=rec.expira_em)
```

O router faz `await sessao.commit()` **sempre** e depois:

- com erro: `raise ErroNegocio(resultado.erro, cabecalhos={"Retry-After": str(resultado.retry_after_s)} if resultado.retry_after_s is not None else None)`;
- sem erro: devolve a resposta. O `Cache-Control: no-store` vem da dependência `sem_cache` do decorador (§8.10, §10.2).

Token ou `expira_em` ausentes sem erro é invariante violada (`RuntimeError`).

### 8.8. Redefinir (pseudocódigo normativo)

```python
async def redefinir_senha(sessao, dados, relogio, hasher) -> MensagemResposta:
    rec = await sessao.scalar(
        select(RecuperacaoSenha)
        .where(RecuperacaoSenha.token_redefinicao_hash == seguranca.hash_token(dados.token_redefinicao))
        .with_for_update())
    agora = relogio.agora()
    if rec is None or rec.verificado_em is None or rec.utilizado_em is not None or agora >= rec.expira_em:
        raise ErroNegocio(TOKEN_REDEFINICAO_INVALIDO)
    usuario = await sessao.get(Usuario, rec.usuario_id)          # None → RuntimeError (invariante)
    usuario.senha_hash = await hasher.gerar(dados.nova_senha)
    rec.utilizado_em = agora
    await sessao.flush()
    return MensagemResposta(mensagem="Redefinição de senha concluída com sucesso")
```

### 8.9. `services/autorizacao.py` (contrato)

`async def obter_do_usuario_ou_404[M: Base](sessao: AsyncSession, modelo: type[M], id_recurso: uuid.UUID, usuario_id: uuid.UUID, *, incluir_excluidos: bool = False) -> M`:

- exige `"usuario_id" in modelo.__table__.c`; caso contrário, `TypeError`;
- consulta `id == id_recurso AND usuario_id == usuario_id`;
- quando a coluna `excluida_em` existe e `incluir_excluidos` é falso, acrescenta `excluida_em IS NULL`;
- na ausência, `ErroNegocio(RECURSO_NAO_ENCONTRADO)`.

O recurso de outro usuário é indistinguível do inexistente.

### 8.10. `dependencias.py` e `main.py` (contrato)

`dependencias.py`, sempre com `Annotated` (regra FAST002). As dependências **podem** importar services (`dependencias → services`, arquitetura §2.2):

- `def obter_relogio() -> Relogio`: devolve a instância de módulo `RelogioSistema()`. `RelogioDep`.
- `def obter_settings_app(request: Request) -> Settings`: `request.app.state.settings`. `SettingsDep`.
- `def obter_hasher(request: Request) -> HasherSenha`: `request.app.state.hasher`. `HasherDep`.
- `def obter_enviador_email(request: Request) -> EnviadorEmail`: `request.app.state.enviador_email`. `EnviadorEmailDep`.
- `def obter_configuracao_token(settings: SettingsDep) -> ConfiguracaoToken`: `segredo=JWT_SEGREDO`, `validade=timedelta(minutes=JWT_VALIDADE_MINUTOS)`. `ConfiguracaoTokenDep`.
- `def sem_cache(response: Response) -> None`: `response.headers["Cache-Control"] = "no-store"`. Usada só no decorador (`dependencies=[Depends(sem_cache)]`) das rotas de login e de verificação. O cabeçalho vale para a resposta de sucesso; as respostas de erro são montadas pelos handlers.
- `async def obter_contexto(sessao: SessaoDep, relogio: RelogioDep, configuracao: ConfiguracaoTokenDep, credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))]) -> ContextoUsuario`:
  1. `agora = relogio.agora()` primeiro;
  2. sem credenciais ou com mais de `TAMANHO_MAXIMO_TOKEN` caracteres → `ErroNegocio(NAO_AUTENTICADO, cabecalhos=CABECALHO_BEARER)`;
  3. senão, `await identidade.montar_contexto(sessao, credenciais.credentials, agora, configuracao)`.

  `ContextoDep`. Nenhum log.

`main.py`, no `lifespan`, **antes** de `criar_engine` (uma falha aqui não deixa a engine aberta):

1. `hasher = HasherSenha(ParametrosArgon2(s.ARGON2_TIME_COST, s.ARGON2_MEMORY_COST_KIB, s.ARGON2_PARALLELISM), anyio.CapacityLimiter(s.ARGON2_MAX_CONCORRENTES))`;
2. `await hasher.preparar_ficticio()`;
3. `app.state.hasher = hasher`;
4. `app.state.enviador_email = criar_enviador(s)`.

O restante do `lifespan` não muda. Depois de `app.include_router(saude.router)`:

- `app.include_router(autenticacao.router, prefix="/api/v1")`;
- `app.include_router(usuarios.router, prefix="/api/v1")`.

A importação continua sem I/O (CT-F1-02).

Arestas de importação da F3, todas compatíveis com D-02 e sem ciclo:

| Módulo | Importa da aplicação |
| --- | --- |
| `tempo` | Nada |
| `seguranca` | Nada |
| `email` | `settings` |
| `schemas/autenticacao`, `schemas/usuario` | `tempo` |
| `services/identidade`, `services/recuperacao_senha` | `models`, `schemas`, `erros`, `tempo`, `seguranca`; `recuperacao_senha` também `email` |
| `services/autorizacao` | `models`, `erros`. Nenhum service o importa na F3; só a rota de teste |
| `dependencias` | `database`, `settings`, `erros`, `tempo`, `seguranca`, `email`, `services/identidade` |
| `routers/autenticacao`, `routers/usuarios` | `database`, `dependencias`, `erros`, `schemas`, `services/identidade`, `services/recuperacao_senha` |
| `main` | `database`, `erros`, `rastreamento`, `routers`, `settings`, `seguranca`, `email` |

---

## 9. Configuração, dependências e operação

### 9.1. `Settings` (contrato)

Campos novos, depois dos existentes, que não mudam:

| Campo | Declaração | Regra |
| --- | --- | --- |
| `JWT_SEGREDO` | `SecretStr` (obrigatório) | `field_validator`: `len(valor.get_secret_value().encode("utf-8")) >= TAMANHO_MINIMO_SEGREDO_BYTES` (32); erro `"JWT_SEGREDO deve ter pelo menos 32 bytes"` |
| `JWT_VALIDADE_MINUTOS` | `int = Field(default=1440, ge=5, le=1440)` | — |
| `ARGON2_TIME_COST` | `int = Field(default=3, ge=1, le=10)` | — |
| `ARGON2_MEMORY_COST_KIB` | `int = Field(default=65536, ge=8, le=1048576)` | `>= 8 * ARGON2_PARALLELISM` |
| `ARGON2_PARALLELISM` | `int = Field(default=4, ge=1, le=16)` | — |
| `ARGON2_MAX_CONCORRENTES` | `int = Field(default=4, ge=1, le=32)` | — |
| `EMAIL_MODO` | `Literal["smtp", "memoria"] = "smtp"` | — |
| `SMTP_HOST` | `str \| None = Field(default=None, min_length=1, max_length=253)` | Obrigatório com `smtp` |
| `SMTP_PORTA` | `int = Field(default=587, ge=1, le=65535)` | — |
| `SMTP_SEGURANCA` | `Literal["starttls", "tls", "nenhuma"] = "starttls"` | — |
| `SMTP_USUARIO` | `str \| None = None` | Os dois ou nenhum |
| `SMTP_SENHA` | `SecretStr \| None = None` | Idem |
| `SMTP_REMETENTE` | `str \| None = None` | Obrigatório com `smtp`. Validado com `email_validator.validate_email(v.strip().lower(), check_deliverability=False, allow_smtputf8=False)` e guardado como `.ascii_email`: a mesma regra de `canonicalizar_email`, repetida aqui porque `settings` não importa `schemas` |
| `SMTP_TIMEOUT_S` | `float = Field(default=10, gt=0, le=30)` | — |

`model_validator(mode="after")`, com mensagens que citam só nomes de campos e regras:

- `ARGON2_MEMORY_COST_KIB >= 8 × ARGON2_PARALLELISM`;
- com `EMAIL_MODO == "smtp"`, exigir `SMTP_HOST` e `SMTP_REMETENTE`;
- `SMTP_USUARIO` e `SMTP_SENHA` juntos ou ausentes;
- credenciais proibidas com `SMTP_SEGURANCA == "nenhuma"`;
- com `AMBIENTE == "producao"`: proibir `EMAIL_MODO == "memoria"` e `SMTP_SEGURANCA == "nenhuma"`, e exigir `ARGON2_TIME_COST >= 3` e `ARGON2_MEMORY_COST_KIB >= 65536`.

Constantes nomeadas para todos os números comparados (PLR2004 vale em `src/`).

### 9.2. `.env.exemplo`: acréscimo exato ao final

```text
# --- F3: identidade e acesso ---
# Gere um segredo próprio (pelo menos 32 bytes) e substitua o valor abaixo:
#   uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SEGREDO=TROQUE_ESTE_VALOR
JWT_VALIDADE_MINUTOS=1440
# memoria: não envia e-mail (desenvolvimento e testes; proibido em producao).
EMAIL_MODO=memoria
# Para enviar os códigos de recuperação, use EMAIL_MODO=smtp e preencha:
# SMTP_HOST=smtp.exemplo.com
# SMTP_PORTA=587
# SMTP_SEGURANCA=starttls
# SMTP_USUARIO=USUARIO_SMTP
# SMTP_SENHA=SENHA_SMTP
# SMTP_REMETENTE=nao-responda@exemplo.com
# SMTP_TIMEOUT_S=10
```

`TROQUE_ESTE_VALOR` tem 17 bytes e falha de propósito na validação. Não altere o `.env` real: atualizá-lo é passo do usuário depois da integração. Sem isso, a API e `alembic upgrade` pela CLI recusam iniciar, porque o `env.py` usa `obter_settings()`.

### 9.3. Dependências (passo 2 da Etapa B)

Comando literal (único momento de instalação):

```bash
uv add argon2-cffi pyjwt tzdata email-validator anyio > "$EV/02a_uv_add.log" 2>&1; echo "codigo_saida=$?" >> "$EV/02a_uv_add.log"
```

Critérios, conferidos pelos logs `02b` a `02e` (§14). **Pare** se algum falhar:

- (i) Em `pyproject.toml`, só entradas novas em `[project].dependencies`: `argon2-cffi`, `pyjwt`, `tzdata`, `email-validator` e `anyio`.
- (ii) No lock, nenhum pacote que já existia muda de versão. São permitidos pacotes **novos**: `argon2-cffi`, `argon2-cffi-bindings`, `pyjwt` e as dependências transitivas deles (como `cffi` e `pycparser`), além da mudança de marcadores do `tzdata`.
- (iii) Nenhuma versão é pré-fixada aqui. As versões resolvidas ficam registradas no `02d`.

### 9.4. Sonda de API depois da instalação (passo 3)

Grave em `$EV/sonda_api_f3.py` (fora do repositório) e execute com `uv run --frozen --no-sync python -I -B "$EV/sonda_api_f3.py"`. Conteúdo exato:

```python
"""Sonda F3: confirma o comportamento de PyJWT e argon2-cffi instalados."""
import warnings
from datetime import UTC, datetime, timedelta

import argon2
import jwt

warnings.simplefilter("error")
CHAVE = "s" * 32
OPCOES = {"verify_signature": True, "verify_exp": False, "verify_iat": False,
          "verify_nbf": False, "verify_aud": False, "verify_iss": False,
          "require": ["sub", "iat", "exp", "typ", "sv"]}
resultados = {}
futuro = int((datetime.now(UTC) + timedelta(days=3650)).timestamp())
passado = int((datetime.now(UTC) - timedelta(days=3650)).timestamp())
for nome, iat, exp in [("iat_futuro", futuro, futuro + 60), ("exp_passado", passado, passado + 60)]:
    t = jwt.encode({"sub": "x", "iat": iat, "exp": exp, "typ": "access", "sv": "0" * 16}, CHAVE, algorithm="HS256")
    try:
        jwt.decode(t, CHAVE, algorithms=["HS256"], options=OPCOES); resultados[nome] = "aceito"
    except jwt.InvalidTokenError as e:
        resultados[nome] = type(e).__name__
t = jwt.encode({"sub": "x", "iat": passado, "exp": futuro, "typ": "access"}, CHAVE, algorithm="HS256")
try:
    jwt.decode(t, CHAVE, algorithms=["HS256"], options=OPCOES); resultados["sem_sv"] = "aceito"
except jwt.InvalidTokenError as e:
    resultados["sem_sv"] = type(e).__name__
t = jwt.encode({"sub": "x"}, None, algorithm="none")
try:
    jwt.decode(t, CHAVE, algorithms=["HS256"], options=OPCOES); resultados["alg_none"] = "aceito"
except jwt.InvalidTokenError as e:
    resultados["alg_none"] = type(e).__name__
t = jwt.encode({"sub": "x", "iat": passado, "exp": futuro, "typ": "access", "sv": "0" * 16}, "o" * 32, algorithm="HS256")
try:
    jwt.decode(t, CHAVE, algorithms=["HS256"], options=OPCOES); resultados["assinatura"] = "aceito"
except jwt.InvalidTokenError as e:
    resultados["assinatura"] = type(e).__name__
ph = argon2.PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16, type=argon2.Type.ID)
h = ph.hash("senha-sonda")
resultados["prefixo_argon2"] = h.split("$", 4)[:4] == ["", "argon2id", "v=19", "m=65536,t=3,p=4"]
try:
    ph.verify(h, "outra"); resultados["mismatch"] = "aceito"
except argon2.exceptions.VerifyMismatchError:
    resultados["mismatch"] = "VerifyMismatchError"
print(resultados)
```

Saída esperada:

- `iat_futuro` e `exp_passado`: `aceito` (a biblioteca não aplica limites temporais com essas opções);
- `sem_sv`: `MissingRequiredClaimError`;
- `alg_none` e `assinatura`: uma subclasse de `InvalidTokenError` (por exemplo, `InvalidAlgorithmError` e `InvalidSignatureError`);
- `prefixo_argon2: True`;
- `mismatch: VerifyMismatchError`;
- nenhuma exceção de aviso (`warnings` em modo erro: uma chave de 32 bytes não pode gerar `InsecureKeyLengthWarning`).

Qualquer diferença é **bloqueio**: pare e relate a saída exata.

---

## 10. Schemas, endpoints e erros

### 10.1. Schemas (contrato)

Funções e validadores em `schemas/autenticacao.py`. Os erros usam `pydantic_core.PydanticCustomError(codigo, mensagem)`, com código em `UPPER_SNAKE`, para o handler devolver a mensagem literal.

**E-mail canônico** (uma só representação para gravar, buscar e enviar):

- `def canonicalizar_email(valor: str) -> str | None` (pública, usada pelos validadores e pelo service de login):
  1. `v = valor.strip().lower()`;
  2. `r = email_validator.validate_email(v, check_deliverability=False, allow_smtputf8=False)`; `EmailNotValidError` → `None`;
  3. se `len(r.ascii_email) > 254` → `None`;
  4. devolve `r.ascii_email`: tudo em ASCII, com o domínio internacionalizado em IDNA (`xn--`).
- Variantes do mesmo endereço (maiúsculas, Unicode composto ou decomposto, largura total, punycode) produzem o mesmo valor (sonda `01` da revisão). É esse valor que fica em `usuario.email`, é usado nas buscas e vai no `To` do SMTP.
- `UsuarioResposta.email` devolve o valor canônico; um domínio internacionalizado aparece em ASCII (`xn--`).

| Validador | Regra | Erro |
| --- | --- | --- |
| `_email_valido` (cadastro, solicitar, verificar) | Não `str` → `EMAIL_INVALIDO`; `canonicalizar_email(v) is None` → `EMAIL_INVALIDO`; senão, o valor canônico | “Informe um e-mail válido” |
| Login | `email: str = Field(min_length=1, max_length=254)`, sem canonicalizar no schema. O service canonicaliza (§8.5) | Só os genéricos (`OBRIGATORIO`, `TAMANHO_*`) |
| `_senha_nova` | Ausente, não `str` ou com menos de 8 caracteres → `SENHA_FRACA`; mais de 128 → `TAMANHO_MAXIMO`. Sem aparar nem normalizar | “A senha informada não atende os requisitos necessários de 8 caracteres” / “Informe no máximo 128 caracteres.” |
| Confirmação | `field_validator` do campo `confirmar_senha` com `ValidationInfo`: diferente da senha já validada → `SENHAS_DIFERENTES` (campo `confirmar_senha`) | “As senhas devem ser idênticas” |
| `_nome_completo` | Ausente ou vazio depois de `strip()` → `NOME_COMPLETO_OBRIGATORIO`; algum caractere com `unicodedata.category(c) == "Cc"` → `NOME_COMPLETO_INVALIDO`; mais de 150 → `TAMANHO_MAXIMO` | “Informe o nome completo” / “O nome não pode conter caracteres de controle” / “Informe no máximo 150 caracteres.” |
| `_data_civil` | Não `str`, ou `re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v) is None`, ou `date.fromisoformat(v)` com `ValueError` → `DATA_INVALIDA`; senão, a `date` | “Informe uma data válida” |
| `_fuso` | Não `str` ou `not tempo.fuso_valido(v)` → `FUSO_INVALIDO` | “Fuso horário inválido” |
| `_codigo` | Ausente, não `str` ou fora de `^[0-9]{8}$` (`re.fullmatch`) → `CODIGO_FORMATO` | “O código deve conter 8 dígitos numéricos” |

`data_nascimento` é declarada `Annotated[date, BeforeValidator(_data_civil)]`, **sem** `strict`. Na sonda `01` da revisão, o FastAPI 0.143 valida o corpo em modo Python, e `Field(strict=True)` recusa toda data em texto, inclusive `"1990-01-01"`. Já o modo comum aceita data com hora e números inteiros (`0` vira `1970-01-01`). O validador aceita só `AAAA-MM-DD` em dígitos ASCII que formem uma data válida. Ausente → `OBRIGATORIO` (tipo `missing`).

Para campos com mensagem própria quando ausentes, use `Field(default=None, validate_default=True)` com `BeforeValidator` (arquitetura §4.4).

| Schema | Campos |
| --- | --- |
| `RegistroEntrada` | `nome_completo` (`_nome_completo`), `email` (`_email_valido`), `senha` (`_senha_nova`), `confirmar_senha` (`str`, confirmação), `data_nascimento` (`_data_civil`), `fuso_horario` (`_fuso`) |
| `LoginEntrada` | `email` (`str`, 1–254), `senha` (`str`, 1–128) |
| `SolicitarCodigoEntrada` | `email` (`_email_valido`) |
| `VerificarCodigoEntrada` | `email` (`_email_valido`), `codigo` (`_codigo`) |
| `RedefinirSenhaEntrada` | `token_redefinicao` (`str`, 1–128), `nova_senha` (`_senha_nova`), `confirmar_senha` (`str`, confirmação contra `nova_senha`) |
| `TokenResposta` | `access_token: str`, `token_type: Literal["bearer"]`, `expira_em: datetime` |
| `SolicitacaoCodigoResposta` | `expira_em: datetime`, `reenvio_permitido_em: datetime` |
| `VerificacaoCodigoResposta` | `token_redefinicao: str`, `expira_em: datetime` |
| `MensagemResposta` | `mensagem: str` |
| `UsuarioResposta` (`schemas/usuario.py`) | `id: uuid.UUID`, `nome_completo: str`, `email: str`, `data_nascimento: date`, `fuso_horario: str` |

Instantes de resposta sempre em UTC, serializados pelo Pydantic com `Z`. Os relógios garantem UTC.

### 10.2. Endpoints (contrato)

| Router | Rota (com prefixo `/api/v1`) | Assinatura e comportamento |
| --- | --- | --- |
| `autenticacao` (`APIRouter(prefix="/auth", tags=["autenticação"])`) | `POST /auth/registro`, `status_code=201` | `registrar(dados, sessao, relogio, hasher) -> UsuarioResposta`: service, `await sessao.commit()`, resposta |
| idem | `POST /auth/login`, `dependencies=[Depends(sem_cache)]` | `entrar(dados, sessao, relogio, hasher, configuracao) -> TokenResposta`: service; sem commit |
| idem | `POST /auth/recuperacao/solicitar` | `solicitar_codigo(dados, sessao, relogio, hasher, enviador)`: service, commit, resposta |
| idem | `POST /auth/recuperacao/verificar`, `dependencies=[Depends(sem_cache)]` | `verificar_codigo(dados, sessao, relogio, hasher)`: §8.7 |
| idem | `POST /auth/recuperacao/redefinir` | `redefinir_senha(dados, sessao, relogio, hasher)`: service, commit, resposta |
| `usuarios` (`APIRouter(prefix="/usuarios", tags=["usuários"])`) | `GET /usuarios/me` | `obter_usuario_atual(sessao, contexto: ContextoDep) -> UsuarioResposta`: sem commit |

Todos os parâmetros de dependência usam os aliases `Annotated` de §8.10. Nenhuma função passa de 5 parâmetros. As respostas trazem **exatamente** os campos dos schemas (dossiê §6.5). Nenhum log nos routers.

### 10.3. `erros.py`: acréscimos exatos

Novos membros de `CodigoErro`, com valor igual ao nome, e as entradas de `CATALOGO_ERROS`:

| Membro | `HTTPStatus` | Mensagem (texto exato) |
| --- | --- | --- |
| `NAO_AUTENTICADO` | `UNAUTHORIZED` | `Sessão inválida ou expirada. Entre novamente.` |
| `CREDENCIAIS_INVALIDAS` | `UNAUTHORIZED` | `E-mail ou senha inválidos.` |
| `EMAIL_JA_CADASTRADO` | `CONFLICT` | `Este e-mail já está cadastrado.` |
| `EMAIL_NAO_ENCONTRADO` | `NOT_FOUND` | `Não foi possível encontrar seu email.` |
| `REENVIO_MUITO_FREQUENTE` | `TOO_MANY_REQUESTS` | `Aguarde alguns instantes para solicitar um novo código.` |
| `FALHA_ENVIO_EMAIL` | `SERVICE_UNAVAILABLE` | `Não foi possível enviar o código. Tente novamente.` |
| `CODIGO_INVALIDO` | `BAD_REQUEST` | `O código de verificação que você inseriu não é válido. Verifique o código e tente novamente.` |
| `CODIGO_EXPIRADO` | `BAD_REQUEST` | `O código expirou. Solicite um novo código.` |
| `TENTATIVAS_ESGOTADAS` | `TOO_MANY_REQUESTS` | `Limite de tentativas atingido. Solicite um novo código.` |
| `CODIGO_JA_VERIFICADO` | `CONFLICT` | `Este código já foi utilizado. Solicite um novo código.` |
| `TOKEN_REDEFINICAO_INVALIDO` | `BAD_REQUEST` | `A solicitação de redefinição expirou ou é inválida. Solicite um novo código.` |

Os membros e as entradas da F1 não mudam. `DATA_NASCIMENTO_FUTURA` é código de **campo** (com `VALIDACAO`), com a mensagem “A data de nascimento não pode ser futura”.

---

## 11. Testes e rastreabilidade

### 11.1. Apoio e fixtures (contrato)

`tests/conftest.py` (só isto muda):

- constante de módulo `SEGREDO_JWT_TESTE = "segredo-sintetico-de-testes-0123456789"` (39 bytes);
- `settings_teste` passa a devolver `SettingsTeste(DATABASE_URL=SecretStr(url_banco_teste), AMBIENTE="teste", JWT_SEGREDO=SecretStr(SEGREDO_JWT_TESTE), EMAIL_MODO="memoria", ARGON2_TIME_COST=1, ARGON2_MEMORY_COST_KIB=8, ARGON2_PARALLELISM=1)`.

`tests/infra/test_configuracao.py` (só isto muda):

1. Acrescentar a `VARIAVEIS_SETTINGS`, nesta ordem: `"JWT_SEGREDO"`, `"JWT_VALIDADE_MINUTOS"`, `"ARGON2_TIME_COST"`, `"ARGON2_MEMORY_COST_KIB"`, `"ARGON2_PARALLELISM"`, `"ARGON2_MAX_CONCORRENTES"`, `"EMAIL_MODO"`, `"SMTP_HOST"`, `"SMTP_PORTA"`, `"SMTP_SEGURANCA"`, `"SMTP_USUARIO"`, `"SMTP_SENHA"`, `"SMTP_REMETENTE"`, `"SMTP_TIMEOUT_S"`.
2. Nova constante `SEGREDO_SINTETICO = "segredo-sintetico-de-configuracao-0123456789"`.
3. `test_settings_padroes`: antes de `obter_settings()`, `setenv` de `JWT_SEGREDO=SEGREDO_SINTETICO`, `SMTP_HOST=smtp.exemplo.com` e `SMTP_REMETENTE=nao-responda@exemplo.com`. Acrescentar asserções dos padrões da F3:
   - 1440; 3, 65536, 4 e 4;
   - `smtp`, 587, `starttls`, 10;
   - `SMTP_USUARIO is None`, `SMTP_SENHA is None`;
   - `SEGREDO_SINTETICO not in repr(s)`.
4. `test_obter_settings_cacheado`: `setenv` de `JWT_SEGREDO=SEGREDO_SINTETICO` e `EMAIL_MODO=memoria`.
5. `test_settings_teste_ignora_ambiente_e_env`: antes de `controle = Settings(...)`, `setenv` de `JWT_SEGREDO=SEGREDO_SINTETICO` e `EMAIL_MODO=memoria`.
6. Os demais testes não mudam. `test_settings_rejeita_esquema_sem_eco` continua sem `JWT_SEGREDO`, porque o erro de `DATABASE_URL` já ocorre; confirme na execução.

`tests/apoio/identidade.py`:

- `async registrar(cliente, **campos) -> dict[str, Any]`: registro válido com padrões sintéticos (`nome_completo="Pessoa Teste"`, e-mail `f"{uuid.uuid7().hex}@exemplo.com"`, senha `"senha-valida-123"`, `data_nascimento="1990-01-01"`, `fuso_horario="America/Sao_Paulo"`), que exige 201;
- `async entrar(cliente, email, senha) -> str`: devolve o `access_token`, exigindo 200;
- `linha_recuperacao(url, usuario_id) -> tuple | None`: por outra conexão, com `consultar`;
- `async aguardar_espera_por_trava(monitor: AsyncEngine, quantidade: int, padrao: str, timeout: float = 5.0) -> None`, com as constantes de módulo `ESPERA_FOR_UPDATE = "%FROM recuperacao_senha%FOR UPDATE%"`, `ESPERA_INSERT_USUARIO = "%INSERT INTO usuario%"` e `ESPERA_INSERT_RECUPERACAO = "%INSERT INTO recuperacao_senha%"`. A cada `INTERVALO_POLLING_S` (importado de `tests/apoio/banco.py`, 0,02 s), numa conexão nova do `monitor`, conta:

  ```sql
  SELECT count(*) FROM pg_stat_activity
  WHERE datname = current_database() AND state = 'active'
    AND wait_event_type = 'Lock' AND pid <> pg_backend_pid()
    AND query ILIKE :padrao
  ```

  Retorna quando a contagem é **igual** a `quantidade`. Se passar dela, lança `AssertionError` na hora. Se o prazo vencer, lança `TimeoutError` com o padrão e o valor observado. A conexão bloqueadora fica `idle in transaction` e não entra na contagem (sonda `03` da revisão, em PostgreSQL 15 com a mesma imagem).

`tests/identidade/conftest.py`:

- `relogio` → `RelogioFixo(datetime(2026, 10, 13, 12, 0, tzinfo=UTC))`;
- `enviador` → `EnviadorEmailMemoria()`;
- `app_identidade(settings_teste, banco_migrado, relogio, enviador)`: `criar_app(settings_teste)`, inclui o router de `rotas_teste_identidade.py` e define `dependency_overrides[obter_relogio]` e `[obter_enviador_email]`;
- `cliente`: com `criar_cliente`;
- `limpeza` (`autouse`): depois de cada teste, `limpar_dados(banco_migrado, container_postgres)`;
- `monitor`: `create_async_engine(banco_migrado, poolclass=NullPool)`, com `dispose`.

`tests/identidade/rotas_teste_identidade.py`: `APIRouter(prefix="/teste")`, nunca incluído no app real.

- `GET /teste/contexto` devolve `{"usuario_id", "fuso", "agora", "hoje"}` do `ContextoDep`.
- `GET /teste/importancias/{importancia_id}` usa `obter_do_usuario_ou_404(sessao, Importancia, importancia_id, contexto.usuario_id)` e devolve `{"id": ...}`.

Portão de largada (a bloqueadora é uma conexão psycopg com transação aberta, criada depois da preparação):

| CT | Bloqueadora | Padrão e quantidade | Liberação |
| --- | --- | --- | --- |
| CT-F3-05 | `INSERT` de um `usuario` com o mesmo e-mail | `ESPERA_INSERT_USUARIO`, 2 | Desfaz |
| CT-F3-23 | `INSERT` de uma `recuperacao_senha` do usuário | `ESPERA_INSERT_RECUPERACAO`, 2 | Desfaz |
| CT-F3-14, 15 e 17 | `SELECT id FROM recuperacao_senha WHERE usuario_id = … FOR UPDATE` | `ESPERA_FOR_UPDATE`, 2 (14 e 17) ou 5 (15) | Desfaz |
| CT-F3-19 e 27 | Idem | `ESPERA_FOR_UPDATE`: 1 depois da primeira tarefa, 2 depois da segunda | Desfaz |

Sequência: disparar as tarefas (`asyncio.create_task`), chamar `aguardar_espera_por_trava` com a quantidade da tabela (nos casos de ordem, entre um disparo e outro), desfazer a bloqueadora e aguardar as tarefas. Nos casos de ordem, a fila de travas do PostgreSQL concede a linha na ordem de chegada; a sonda `03` confirmou isso em 3 repetições de cada ordem.

Captura de logs (CT-F3-25): fixture que acrescenta ao logger `api_gestao_pessoal` um `logging.StreamHandler(io.StringIO())` com `logging.Formatter(FORMATO_LOG)` e `FiltroIdRequisicao()`, em nível `DEBUG`, e o remove no fim. Use `settings_teste.model_copy(update={"LOG_NIVEL": "DEBUG"})`.

### 11.2. `tests/apoio/relogio.py` (conteúdo exato)

```python
"""Relógio fixo e avançável para os testes (arquitetura §7)."""

from datetime import UTC, datetime, timedelta
from typing import override

from api_gestao_pessoal.tempo import Relogio


class RelogioFixo(Relogio):
    """Devolve sempre o mesmo instante até `avancar` ser chamado."""

    def __init__(self, instante: datetime) -> None:
        if instante.tzinfo is not UTC:
            msg = "RelogioFixo exige instante em UTC"
            raise ValueError(msg)
        self._instante = instante

    @override
    def agora(self) -> datetime:
        return self._instante

    def avancar(self, intervalo: timedelta) -> None:
        self._instante += intervalo
```

### 11.3. Casos e rastreabilidade

Nomes de função obrigatórios. Casos múltiplos podem usar `pytest.mark.parametrize` com `ids` descritivos. Testes de concorrência levam `@pytest.mark.concorrencia`.

| CT | Arquivo :: função | Asserções |
| --- | --- | --- |
| CT-F3-01 | `test_registro.py::test_registro_valido` | 201; chaves exatas de `UsuarioResposta`; e-mail na forma canônica (§10.1); por outra conexão, `senha_hash` começa com `$argon2id$` e é diferente da senha |
| CT-F3-02 | `test_registro.py::test_validacoes_do_registro` | Casos do dossiê §7.2: 422 e `campos[].codigo` exato. Mensagens literais 3.4.10 e 3.4.14. Nenhum valor ecoado. Nenhuma linha gravada. Nascimento: `RelogioFixo` 2026-10-14T02:30Z, `America/Sao_Paulo`: 2026-10-14 → `DATA_NASCIMENTO_FUTURA`; 2026-10-13 → 201 |
| CT-F3-03 | `test_registro.py::test_email_duplicado` | 409 `EMAIL_JA_CADASTRADO`; uma linha. Parametrizado: depois de cadastrar `fulano@exâmple.com`, as variantes `FULANO@EXÂMPLE.COM`, a forma decomposta (NFD) e `fulano@xn--exmple-xta.com` também dão 409 |
| CT-F3-04 | `test_login.py::test_login_valido` | Claims decodificadas sem verificação: conjunto exato; `exp - iat == 86400`; `expira_em` igual a `exp` em ISO com `Z`; `Cache-Control: no-store`; login com o e-mail em maiúsculas e, para um cadastro com domínio internacionalizado, em punycode → 200 |
| CT-F3-05 c | `test_registro.py::test_registros_simultaneos` | Portão com 2 em espera no `INSERT`. Um 201 e um 409 `EMAIL_JA_CADASTRADO`; uma linha |
| CT-F3-06 | `test_login.py::test_credenciais_invalidas_indistinguiveis` | Corpo e status iguais (exceto `id_requisicao`) para e-mail inexistente, e-mail malformado (`sem-arroba`) e senha errada; espião em `HasherSenha.verificar_ficticio` chamado uma vez em cada um dos dois primeiros casos |
| CT-F3-07 | `test_login.py::test_tokens_recusados` | 13 casos do dossiê §7.2 → 401 `NAO_AUTENTICADO` e `WWW-Authenticate: Bearer` |
| CT-F3-08 | `test_usuario_atual.py::test_usuario_atual` | 200; os 5 campos do próprio usuário |
| CT-F3-09 | `test_recuperacao.py::test_solicitar_codigo` | Código forçado `00012345`; assunto e corpo exatos (§8.4); `destinatario` igual ao e-mail canônico gravado; `codigo_hash` Argon2id; `expira_em` = relógio + 10 min |
| CT-F3-10 | `test_recuperacao.py::test_email_nao_encontrado` | 404 com a mensagem 3.4.2; nenhum envio; nenhuma linha |
| CT-F3-11 | `test_recuperacao.py::test_reenvio` e `test_recuperacao.py::test_reenvio_anula_token` | `test_reenvio`, com o gerador forçado a `00012345` e depois a `87654321`: (1) solicitar → 200; (2) duas verificações inválidas → `tentativas == 2` por outra conexão; (3) +59 s: solicitar → 429 com `Retry-After: 1` e linha igual à anterior; (4) +60 s: solicitar → 200 e, **logo em seguida**, por outra conexão: `tentativas == 0`, `verificado_em`, `token_redefinicao_hash` e `utilizado_em` nulos, `codigo_hash` diferente e `expira_em` igual ao relógio + 10 min; a segunda mensagem traz `87654321`; (5) verificar `00012345` → 400 `CODIGO_INVALIDO` e `tentativas == 1` (conta para a emissão nova); (6) verificar `87654321` → 200. `test_reenvio_anula_token`: verificar o código certo → token T; +60 s, solicitar → 200 e, logo em seguida, verificação, token e uso nulos e `tentativas == 0`; redefinir com T → 400 `TOKEN_REDEFINICAO_INVALIDO` |
| CT-F3-12 | `test_recuperacao.py::test_verificacao` | Correto → 200 com token; incorreto → 400 (3.4.8) com `tentativas + 1` por outra conexão; 5ª inválida → 400; 6ª, mesmo correta → 429 com `Retry-After`; expirado → 400 `CODIGO_EXPIRADO`; dígitos não ASCII → 422 `CODIGO_FORMATO` |
| CT-F3-13 | `test_recuperacao.py::test_verificar_de_novo` | 409; `token_redefinicao_hash` inalterado |
| CT-F3-14 c | `test_recuperacao_concorrencia.py::test_verificacoes_corretas_simultaneas` | Portão com 2 em espera (§11.1). Um 200 e um 409 `CODIGO_JA_VERIFICADO`; um único `token_redefinicao_hash` na linha |
| CT-F3-15 c | `test_recuperacao_concorrencia.py::test_cinco_invalidas_simultaneas` | Gerador forçado a `00012345`; cinco verificações com códigos inválidos distintos; `aguardar_espera_por_trava(monitor, 5, ESPERA_FOR_UPDATE)` **antes** de liberar, o que prova as cinco requisições paradas ao mesmo tempo na trava da linha. Depois de liberar: cinco respostas 400 `CODIGO_INVALIDO`; `tentativas == 5` por outra conexão; uma sexta verificação, agora com `00012345`, → 429 `TENTATIVAS_ESGOTADAS` com `Retry-After` |
| CT-F3-16 | `test_recuperacao.py::test_redefinir` | 200 com a mensagem 3.4.15; login com a nova senha → 200; com a antiga → 401; `utilizado_em` preenchido; JWT anterior → 401 |
| CT-F3-17 c | `test_recuperacao_concorrencia.py::test_redefinicoes_simultaneas` | Portão com 2 em espera. Mesmo token nas duas: um 200 e um 400 `TOKEN_REDEFINICAO_INVALIDO`; `utilizado_em` preenchido uma vez |
| CT-F3-18 | `test_recuperacao.py::test_redefinir_invalido` | Token expirado (`RelogioFixo` em `expira_em`), usado e inexistente → 400; senhas diferentes → 422 `SENHAS_DIFERENTES`; curta → 422 `SENHA_FRACA` |
| CT-F3-19 c | `test_recuperacao_concorrencia.py::test_reenvio_e_verificacao` (parametrizado pela ordem) | Gerador forçado a `00012345` e depois a `87654321`; emissão em T0; +60 s; portão de ordem (§11.1). Verificar antes: verificação → 200 e reenvio → 200; ao final, token e verificação nulos e `tentativas == 0`. Reenviar antes: reenvio → 200 e verificação com `00012345` → 400 `CODIGO_INVALIDO`, `tentativas == 1` |
| CT-F3-20 | `test_recuperacao.py::test_falha_de_envio` | Primeira emissão e reenvio: 503 `FALHA_ENVIO_EMAIL`; linha ausente ou inalterada; repetição imediata → 200 |
| CT-F3-21 | `test_usuario_atual.py::test_hoje_no_fuso` | `GET /teste/contexto` com `RelogioFixo` 2026-10-14T02:30Z → `hoje == "2026-10-13"` |
| CT-F3-22 | `test_configuracao_identidade.py::test_settings_da_f3` | Casos do dossiê §7.2; mensagens sem o segredo |
| CT-F3-23 c | `test_recuperacao_concorrencia.py::test_primeiras_solicitacoes_simultaneas` | Portão com 2 em espera no `INSERT`. Um 200 e um 429; uma linha; uma mensagem |
| CT-F3-24 | `test_recuperacao.py::test_limites_da_recuperacao` e `test_login.py::test_limites_do_token` | Código válido em `expira_em − 1 s` e expirado em `expira_em`; reenvio em +59 s e +60 s; JWT válido em `exp − 1 s` e 401 em `exp` e em `iat − 1 s` |
| CT-F3-25 | `test_vazamento.py::test_sem_vazamento` | Sentinelas: senha, nova senha, e-mail, nome e código forçado, além dos tokens obtidos. Respostas com as chaves exatas; sentinelas só nos campos permitidos; ausência total em respostas de erro, em `caplog.text` e na saída do handler formatado. Inclui uma rota de teste que lança `RuntimeError` sem dados e uma `FalhaEnvioEmail` |
| CT-F3-26 | `test_recuperacao.py::test_commit_falha_depois_do_envio` | `dependency_overrides[obter_sessao]` com sessão cujo `commit` lança `DBAPIError` sintético: 5xx; mensagem enviada; banco inalterado; nova solicitação → 200 |
| CT-F3-27 c | `test_recuperacao_concorrencia.py::test_reenvio_e_redefinicao` (parametrizado pela ordem) | Token T obtido; +60 s; portão de ordem. Redefinir antes: redefinição → 200 e reenvio → 200. Reenviar antes: reenvio → 200 e redefinição com T → 400 `TOKEN_REDEFINICAO_INVALIDO`, com a senha antiga ainda válida no login |
| CT-F3-28 | `test_email.py::test_enviador_smtp` (parametrizado) | `smtplib.SMTP` e `SMTP_SSL` simulados: contexto com `verify_mode == ssl.CERT_REQUIRED` e `check_hostname`; `ehlo` depois de `starttls`; `login` só com credenciais; `timeout`; `__exit__` chamado; `SMTPRecipientsRefused` com endereço sentinela → `FalhaEnvioEmail("SMTPRecipientsRefused")`, sem o endereço na exceção nem no log. `test_email.py::test_mensagem_codigo`: texto exato |
| CT-F3-29 | `test_seguranca.py::test_hasher` | Parâmetros de produção: prefixo `$argon2id$v=19$m=65536,t=3,p=4$`; verificação certa e errada; `HashArmazenadoInvalido` para hash corrompido. Limitador de 2 vagas: `monkeypatch` de `argon2.PasswordHasher.hash` com função que conta as execuções simultâneas e espera um `threading.Event`; 5 chamadas → máximo 2. Login não regrava `senha_hash`. Também `test_seguranca.py::test_token_unidade`: emissão e decodificação, inclusive `bool` em `iat` e claim extra |
| CT-F3-30 | `test_usuario_atual.py::test_obter_do_usuario_ou_404` | Importância de outro usuário → 404; UUID malformado → 422; a própria → 200 |

Seleção que comprova cada CT: §14, passos 6 e 7.

---

## 12. Critérios de aceite

**Aceite:**

- CT-F3-01 a 30 da tabela §11.3 passando, sem `skip` nem `xfail`, com a coleta registrada.
- Regressões de `tests/infra` (§14, passo 7) passando.
- Ruff, formatação e Pyright limpos (§14, passos 11 a 13).
- Lock conforme §9.3.
- `alembic heads` = `0001 (head)`.
- Arquivos protegidos com os hashes de §1.1.
- Mensagens literais 3.4.8, 3.4.10, 3.4.14 e 3.4.15 (e 3.4.2 na opção A).
- Nenhum segredo em log ou resposta fora dos campos permitidos.
- Tentativas persistidas.

**Reprovação** (qualquer um):

- `commit()` em services ou handlers;
- trava consultiva ou idempotência;
- mudança de esquema ou modelo;
- `noqa` ou `ignore` novo;
- teste de tempo de resposta;
- e-mail real;
- leitura do `.env`;
- token ou e-mail em log;
- `check_needs_rehash`;
- `asyncio.to_thread` no lugar de `anyio.to_thread.run_sync` com limitador;
- validação temporal do JWT pela biblioteca;
- `^\d` no código;
- importação de um service por outro (ADR-0001 D-02);
- `data_nascimento` sem o validador `_data_civil` ou com `strict`;
- arquivo fora de §7.

**Bloqueios** (pare e relate, sem contornar):

- divergência na Etapa A ou na revalidação;
- critério do lock violado;
- sonda de API diferente do esperado;
- Docker indisponível;
- necessidade de arquivo fora de §7, de exceção de lint ou de mudança de configuração de ferramentas;
- mensagem ou comportamento de biblioteca diferente do descrito.

---

## 13. Etapa A — somente leitura, relatório e parada

1. `pwd`, `git status --short --branch --untracked-files=all`, `git rev-parse HEAD` e `git rev-parse HEAD^`. Determine o modo (§1.2).
2. `sha256sum` dos arquivos de §1.1 e dos documentos de §1.2, inclusive este prompt.
3. Leitura das fontes de §2, com o SHA-256 de cada uma.
4. `uv --version`; `uv run --frozen --no-sync python --version`; `docker version --format '{{.Server.Version}}'`.
5. `uv run --frozen --no-sync python -c "import importlib.metadata as m; [print(p, m.version(p)) for p in ('pydantic', 'fastapi', 'starlette', 'anyio', 'email-validator', 'sqlalchemy', 'psycopg')]"` → os valores de §1.1.
6. `uv run --frozen --no-sync python -c "import importlib.util as u; print([n for n in ('jwt', 'argon2') if u.find_spec(n)])"` → `[]` (ainda não instalados; nada é instalado na Etapa A).
7. `ls -A1 src/api_gestao_pessoal` e `ls -A1 tests` → sem `services/` e sem `identidade/`.
8. `rg -n "settings_teste|Settings\(" tests` → confirmar os pontos de §11.1.

Resposta da Etapa A, também gravada em `$HOME/minhavida_evidencias/f3/RELATORIO_ETAPA_A.md`:

- divergências, ou “nenhuma”;
- modo, HEAD e os resultados dos passos 1 a 8;
- SHA-256 deste prompt e das fontes;
- lista final de arquivos (§7) e de comandos (§14);
- riscos concretos;
- pedido explícito: **“Aguardo ‘pode implementar’ para a F3.”**

**Não implemente antes dessa resposta do usuário.**

---

## 14. Etapa B — sequência de implementação e validação

Execute na raiz do repositório, nesta ordem. Os passos 4 e 5 são só edição. `EV="$HOME/minhavida_evidencias/f3"`.

```bash
EV="$HOME/minhavida_evidencias/f3"; mkdir -p "$EV"

# 0. Revalidação (§1.3) em "$EV/00_revalidacao.log", antes de qualquer alteração.

# 1. Estado antes.
sha256sum uv.lock pyproject.toml > "$EV/01_antes.log" 2>&1; echo "codigo_saida=$?" >> "$EV/01_antes.log"
git show 91be324c88c5a3f99a49b1b1700963e32ef257e9:uv.lock > "$EV/uv.lock.baseline" 2> "$EV/01b_lock_baseline.log"; echo "codigo_saida=$?" >> "$EV/01b_lock_baseline.log"

# 2. Dependências (único passo de instalação; §9.3).
uv add argon2-cffi pyjwt tzdata email-validator anyio > "$EV/02a_uv_add.log" 2>&1; echo "codigo_saida=$?" >> "$EV/02a_uv_add.log"
git diff -- pyproject.toml > "$EV/02b_diff_pyproject.log" 2>&1; echo "codigo_saida=$?" >> "$EV/02b_diff_pyproject.log"
git diff --stat -- uv.lock > "$EV/02c_diff_lock_stat.log" 2>&1; echo "codigo_saida=$?" >> "$EV/02c_diff_lock_stat.log"
uv run --frozen --no-sync python -c "import importlib.metadata as m; [print(p, m.version(p)) for p in ('pyjwt', 'argon2-cffi', 'argon2-cffi-bindings', 'tzdata', 'email-validator', 'anyio')]" > "$EV/02d_versoes.log" 2>&1; echo "codigo_saida=$?" >> "$EV/02d_versoes.log"
uv run --frozen --no-sync python -I -c "import sys, tomllib; a = {p['name']: p.get('version') for p in tomllib.load(open(sys.argv[1], 'rb'))['package']}; b = {p['name']: p.get('version') for p in tomllib.load(open('uv.lock', 'rb'))['package']}; mudou = sorted(n for n in a if n in b and a[n] != b[n]); print('mudaram:', mudou); print('novos:', sorted(set(b) - set(a))); print('removidos:', sorted(set(a) - set(b))); sys.exit(1 if mudou or set(a) - set(b) else 0)" "$EV/uv.lock.baseline" > "$EV/02e_lock_comparacao.log" 2>&1; echo "codigo_saida=$?" >> "$EV/02e_lock_comparacao.log"

# 3. Sonda de API (§9.4). Grave o conteúdo exato em "$EV/sonda_api_f3.py" e então:
uv run --frozen --no-sync python -I -B "$EV/sonda_api_f3.py" > "$EV/03_sonda_api.log" 2>&1; echo "codigo_saida=$?" >> "$EV/03_sonda_api.log"

# 4. Código de produção (§7–§10), por edição. Sem log.
# 5. Testes e apoio (§11), por edição. Sem log. Grave a lista dos .py criados ou
#    alterados (um por linha, caminhos de §7) em "$EV/arquivos_py_f3.txt".

# 6. Testes da fase (inclui a concorrência).
uv run --frozen --no-sync pytest tests/identidade -vv --color=no -p no:cacheprovider > "$EV/06_pytest_identidade.log" 2>&1; echo "codigo_saida=$?" >> "$EV/06_pytest_identidade.log"

# 7. Regressões afetadas (Settings, settings_teste e lifespan).
uv run --frozen --no-sync pytest tests/infra/test_configuracao.py tests/infra/test_erros.py tests/infra/test_saude.py tests/infra/test_sessao_transacao.py -vv --color=no -p no:cacheprovider > "$EV/07_pytest_regressoes.log" 2>&1; echo "codigo_saida=$?" >> "$EV/07_pytest_regressoes.log"

# 8. Correções do implementador, SOMENTE nos arquivos da lista.
uv run --frozen --no-sync ruff check --fix $(cat "$EV/arquivos_py_f3.txt") > "$EV/08a_ruff_fix.log" 2>&1; echo "codigo_saida=$?" >> "$EV/08a_ruff_fix.log"
uv run --frozen --no-sync ruff format $(cat "$EV/arquivos_py_f3.txt") > "$EV/08b_ruff_format.log" 2>&1; echo "codigo_saida=$?" >> "$EV/08b_ruff_format.log"
git status --porcelain --untracked-files=all > "$EV/08c_status.log" 2>&1; echo "codigo_saida=$?" >> "$EV/08c_status.log"

# 9. Se 08a terminar com erro: corrija à mão SÓ os arquivos da lista e repita os
#    três comandos de 8 com sufixo _2 (depois _3), sem apagar os logs anteriores.
#    Se a correção exigir exceção de lint, mudança de configuração ou arquivo
#    fora de §7: PARE e relate.

# 10. SOMENTE se 8 ou 9 alterou algum .py: repita 6 e 7 com sufixo _2.

# 11 a 13. Verificação, sem alterar arquivos.
uv run --frozen --no-sync ruff check --no-fix . > "$EV/11_ruff_check.log" 2>&1; echo "codigo_saida=$?" >> "$EV/11_ruff_check.log"
uv run --frozen --no-sync ruff format --check . > "$EV/12_ruff_format_check.log" 2>&1; echo "codigo_saida=$?" >> "$EV/12_ruff_format_check.log"
uv run --frozen --no-sync pyright > "$EV/13_pyright.log" 2>&1; echo "codigo_saida=$?" >> "$EV/13_pyright.log"

# 14. Alembic sem banco e sem env.py (nenhuma revisão nova).
uv run --frozen --no-sync alembic heads > "$EV/14_alembic_heads.log" 2>&1; echo "codigo_saida=$?" >> "$EV/14_alembic_heads.log"

# 15. Estado depois.
sha256sum uv.lock pyproject.toml > "$EV/15_depois.log" 2>&1; echo "codigo_saida=$?" >> "$EV/15_depois.log"

# 16. Imagem de teste.
docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine > "$EV/16_digest.log" 2>&1; echo "codigo_saida=$?" >> "$EV/16_digest.log"

# 17. Objeto entregue.
git status --porcelain --untracked-files=all > "$EV/17a_status.log" 2>&1; echo "codigo_saida=$?" >> "$EV/17a_status.log"
git diff --stat 91be324c88c5a3f99a49b1b1700963e32ef257e9 > "$EV/17b_diff_stat.log" 2>&1; echo "codigo_saida=$?" >> "$EV/17b_diff_stat.log"
git status --porcelain --untracked-files=all | cut -c4- | grep -v '^PROMPTS/\|^docs/\|^CLAUDE.md$' | xargs -d '\n' sha256sum > "$EV/17c_sha256_f3.log" 2>&1; echo "codigo_saida=$?" >> "$EV/17c_sha256_f3.log"
sha256sum "$EV"/*.log "$EV"/sonda_api_f3.py "$EV"/arquivos_py_f3.txt > "$HOME/minhavida_evidencias/f3_sha256_logs.txt"
```

| Passo | Expectativa |
| --- | --- |
| 0 | Tudo coincide. Senão, **pare** |
| 1 e 15 | `uv.lock` e `pyproject.toml` antes com os hashes de §1.1; depois, iguais ao estado deixado pelo passo 2 |
| 2 | `02a` com `codigo_saida=0`; `02b` só com as 5 entradas de §9.3; `02e` com `mudaram: []`, `removidos: []` e `codigo_saida=0`. Senão, **pare** |
| 3 | Saída de §9.4. Senão, **pare** |
| 6 e 7 | 100 % passando, sem pulados, com a contagem e a duração registradas |
| 8 | `08c` só com arquivos de §7 e os documentos da preparação. Senão, **pare** |
| 11 | `All checks passed!` |
| 12 | Nenhum arquivo a reformatar |
| 13 | `0 errors, 0 warnings, 0 informations` |
| 14 | `0001 (head)` |
| 17 | `17a` com os arquivos de §7 e os documentos da preparação; nada mais |

O pipeline do passo 17c é só um inventário; o código de saída que vale é o de `sha256sum`, registrado no fim do log.

---

## 15. Relatório e evidências

Grave o relatório integral em `$HOME/minhavida_evidencias/f3/RELATORIO_ETAPA_B.md` e responda no chat com um resumo e o caminho do arquivo. O relatório contém:

1. Objeto entregue em duas partes:
   - documentos de preparação (hashes de §1.2 e, para este prompt, da mensagem de liberação, inalterados);
   - alterações da F3 (`17c`) e `git diff --stat` (`17b`).

   Inclui também modo, HEAD e o bloco de revalidação.
2. Ambiente: uv, Python, Docker, digest (`16`) e versões resolvidas (`02d`).
3. Para cada passo de §14, na ordem: comando literal, `codigo_saida`, linhas finais **sem edição** (resumo do pytest, do Ruff e do Pyright) e caminho do log, inclusive reexecuções `_2`.
4. `f3_sha256_logs.txt`.
5. Tabela CT → node ID → resultado, com as regressões.
6. Testes não executados, inconclusivos ou que falharam, com o motivo.
7. Desvios: nenhum é permitido. Se houver, descreva-os com o ponto de parada.
8. Pendências e riscos observados.

Não declare a fase aprovada.

---

## 16. Parada final

- Depois do relatório, **pare**. O estado é `ENTREGUE_PARA_AUDITORIA`.
- Não inicie a F4 nem crie a trava do usuário, a idempotência ou endpoints de domínio.
- Não faça `git add`, commit, push ou merge (modo LOCAL).
- A auditoria independente é do Opus (`plano_validacao_auditoria.md` §9).
- Exceção Cloud, só se a sessão for identificada explicitamente como Cloud: commit e push apenas da branch da sessão e PR **draft**, sem merge nem alteração de `main`.
