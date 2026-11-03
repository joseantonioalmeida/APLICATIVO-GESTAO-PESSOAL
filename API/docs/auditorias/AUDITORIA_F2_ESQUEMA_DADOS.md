# Auditoria independente da F2 — Esquema de dados

| Campo | Valor |
| --- | --- |
| Projeto | API MinhaVida — gestão pessoal e finanças |
| Fase | F2 — Esquema de dados |
| Auditor | Claude Opus 5.5 (arquiteto e auditor independente) |
| Data | 2026-10-13 |
| Instrução desta auditoria | `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md`, SHA-256 `3854631cd82b8cb13f0c2fb92a9e729f21446112428a258906a897e217271db3` |
| Prompt implementado | `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md`, SHA-256 `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c`, com a emenda F2-D1 e as respostas D2 e D3 |
| Baseline | `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30` (pai `bd2b2e0f1e4f2674b528175e535b0931badec34a`), modo A, F2 sem commit |
| Evidências desta auditoria | `$HOME/minhavida_evidencias/f2_auditoria_VJ4xnCZ6/` (manifesto `MANIFESTO_EVIDENCIAS.sha256`, SHA-256 `9b6562e2c0511deee3f775a1abe350d3e04189b09e83b30db60d6b5bef1555f9`) |
| Evidências do Sonnet (preservadas, não alteradas) | `$HOME/minhavida_evidencias/f2/` e `$HOME/minhavida_evidencias/f2_sha256_logs.txt` |
| **Veredito** | **`APROVADO_COM_P3`** |

Convenção de origem das afirmações: **observado** (lido diretamente no arquivo ou no banco), **reproduzido** (executado por mim nesta auditoria), **declarado** (afirmado pelo Sonnet, sem prova própria), **inferido** (dedução a partir de evidência indireta) e **não verificado**.

---

## 1. Veredito e impedimentos

**F2: `APROVADO_COM_P3`.** Não há P0, P1 ou P2 abertos. Os requisitos e as provas obrigatórias da F2 estão satisfeitos no objeto identificado na §2. Restam três achados P3, todos com origem na especificação ou na documentação normativa (o Prompt F2 e o plano de fases, ambos do Opus). Nenhum deles afeta o código, os testes, a migração ou a configuração entregues.

Comprovado (reproduzido):

- 41 testes da fase e 4 regressões passaram, sem skip nem xfail (logs `10` e `11`).
- Ruff, formatação e Pyright limpos, agora cobrindo `alembic/` (logs `20` a `25`).
- O esquema materializado pela revisão entregue é **idêntico** a um oráculo montado diretamente do `CLAUDE.md`: 134 colunas, 85 restrições com definição completa e 8 índices (sonda S1).
- Cada um dos 88 casos negativos dos testes atinge exatamente a restrição pretendida, não só o SQLSTATE (sonda de violações, log `42`).
- Seeds: as 30 grafias do `CLAUDE.md`, 30 UUIDv7 distintos e reexecução que preserva os mesmos IDs (S5). Rodam na mesma transação da migração (S2).
- A revisão é compatível com o modo offline: o SQL é gerado sem `.env` nem conexão, e, aplicado num banco vazio, produz o mesmo catálogo (S3).
- `eager_defaults` busca os padrões por `RETURNING` na própria instrução de INSERT e de UPDATE (S4).

Impedimentos: **nenhum**. Nada obrigatório ficou sem verificação.

---

## 2. Objeto auditado

### 2.1. Identificação (observado; logs `00a` a `00i`)

- Diretório: `/home/jose/projects/app_gestão_pessoal/API`. Branch `main`, à frente de `origin/main` por 1 commit (o `90412ec`), o que não afeta a auditoria local.
- `HEAD` = `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`; `HEAD^` = `bd2b2e0f1e4f2674b528175e535b0931badec34a`; árvore da F1 com 51 arquivos.
- Índice do Git vazio. `git status`: 17 arquivos ` M` e 25 `??`, sem nenhum outro item.

Três referências, conforme a instrução §1.1:

1. **Commit da F1** (`90412ec`): base do diff.
2. **Os 11 documentos de preparação** (Prompt F2 §1.2): todos com o SHA-256 da tabela (log `00g`):

| Documento | SHA-256 (igual à tabela do Prompt F2 §1.2) |
| --- | --- |
| `CLAUDE.md` | `35fda3df29e2ae1bd2172a35c430944f4b5fb7d08dd26e0c9bf2123da0405e7d` |
| `docs/adr/0001_arquitetura_api_minhavida.md` | `7f7c4745c204a026a3742617bc8525ece2d0b99a722e37ec87d94a0740e23760` |
| `docs/adr/0002_identificadores_uuid.md` | `951fb3936affa3eb1dcab67f89507eb9620630e938b2868b2f3ebf4b632b7593` |
| `docs/arquitetura/analise_projeto_minhavida.md` | `a61962f06274c2bed1775e425d3e1b55a0b0a41995a336b890e7fa83503c4303` |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `c691fca0219a1b69674c8a2762d9c3be800ba6b6c081e5414a2b476eafe3db24` |
| `docs/arquitetura/indice.md` | `28f2d37479aa02209ebdd23112032f7aa684cf5c067552426d6d8195db45ad0b` |
| `docs/arquitetura/matriz_requisitos_api.md` | `ed3b2accbc0ed565fbfe9283d4e56c694cecf72ae537e42414789ab06788330c` |
| `docs/arquitetura/plano_fases_api.md` | `05253430f13e462017ff9e0ad788c95692a9bd56b36a4dd9ef20ff02fa01a4ec` |
| `docs/arquitetura/plano_validacao_auditoria.md` | `ba7f8d9234748da3dde04b822d0b4c383b6ebfaed18ed8fb64edb9dd17ae1669` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md` | `e1d6ac1ac2282bac95b39981a1369f40dd1cc4a94acc45d5e9f5764e42350e05` |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md` | `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c` |

As emendas F2-D1, D2 e D3 foram instruções do usuário ao Sonnet e não mudaram os bytes desses documentos. `uv.lock`: `b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d`, igual ao baseline.

3. **Manifestos da entrega:**
   - manifesto final do Sonnet (`f2/18c_sha256_f2.log`): conferido contra o disco, **30/30 OK** (log `00h`);
   - logs do Sonnet contra `f2_sha256_logs.txt`: **27/27 OK** (log `00i`);
   - manifesto independente, gerado antes das verificações: `00_manifesto_antes.sha256`, com 76 arquivos (rastreados mais não rastreados não ignorados, sem o `.env`). Ao fim das verificações, `50_manifesto_pos.sha256` é **idêntico** (log `50`).

Os três hashes completos citados na instrução §1.2 conferem com o manifesto original do Sonnet e com o disco. Não houve divergência de transcrição.

### 2.2. Arquivos da implementação F2 (SHA-256 completo, igual a `18c` e ao disco)

| Arquivo | Situação | SHA-256 |
| --- | --- | --- |
| `pyproject.toml` | Modificado | `93932958ba2547476637b3cf75c37ba403c324ec6a1c7dd4763183dbdacba721` |
| `src/api_gestao_pessoal/models/__init__.py` | Modificado | `c33e390a03f64aa05bf9ce8df4f343caae07ba32da7d8d0cbac650497542280d` |
| `src/api_gestao_pessoal/models/base.py` | Modificado | `50844f7fa5c78b09ed82362a4c480fc04b9be0d50813c43f5aae8627803bdf63` |
| `src/api_gestao_pessoal/models/usuario.py` | Modificado | `bd0872b242e7eba7ec090fb0bce23ac2c7deda36d38ffae0e70849a3e731ef0a` |
| `tests/apoio/banco.py` | Modificado | `58fce75d41d2a427812ce317c83bb0864336a37327f28f211ee0d7197f85a94a` |
| `tests/conftest.py` | Modificado | `a385540392111aee5e93a6ee6e413b31fede746a8fef63466e44064122d6608e` |
| `tests/infra/test_alembic_ambiente.py` | Modificado | `8f8ec17f5f73da4d1446a7bc2bb029b044db02e814ffb743c7d549809a2aa0e1` |
| `alembic/versions/20261013_0001_esquema_inicial.py` | Novo | `da1d0f38b161d26021f9242c1d5291d8cc0d4ef8d4f64b4c56c4155875150a24` |
| `src/api_gestao_pessoal/models/atividade.py` | Novo | `d1bddd85363898f06044072df4740aa774d50f9bb660a2bee6961920e327a507` |
| `src/api_gestao_pessoal/models/categoria_atividade.py` | Novo | `93a99ccff163ca196698e0470a553a1f7b3cb941f15c800970add5cc99662a1c` |
| `src/api_gestao_pessoal/models/categoria_financeira.py` | Novo | `dab457f2e8a6802755122d1c98107f9afd0886e840b3696eeccdc847b0723126` |
| `src/api_gestao_pessoal/models/categoria_importancia.py` | Novo | `504e156527744bbaa79e32dc7f8a51fc0f09a97a187ef0de64f4bcd46690aa0e` |
| `src/api_gestao_pessoal/models/enums.py` | Novo | `73d36da9b171fd6f3e062248e33f26237f2adf4eaeebf7bfde74de40712d8a39` |
| `src/api_gestao_pessoal/models/importancia.py` | Novo | `b3884cd956648f7ca32768ae9102642996817a4247b7b07507fc584ec79fa367` |
| `src/api_gestao_pessoal/models/lembrete_importancia.py` | Novo | `d94e98ad52a2955ad90ccfcb35e9d84c5dfa3337ab0cdc61641d493e399e13d8` |
| `src/api_gestao_pessoal/models/movimentacao_financeira.py` | Novo | `580d0567a15fcea497ad71f946bcd980492584d88aad368beaebb6d0a89c22bd` |
| `src/api_gestao_pessoal/models/notificacao.py` | Novo | `929356ebe244fbec296f599e81aff1f5dbc0a104de18adb86b061607e98c515c` |
| `src/api_gestao_pessoal/models/recuperacao_senha.py` | Novo | `2c75f3b4f96ff9e160648d4e2fe4cf176f58444bc8ecf5faf4a41de1f3cd7d25` |
| `src/api_gestao_pessoal/models/requisicao_idempotente.py` | Novo | `294b3a1ca8c793546872cf072ea2b056c267c810b02e0746c46c3aa03e75d882` |
| `src/api_gestao_pessoal/models/serie_atividade.py` | Novo | `8967492cead8dc2db468dd082aae1ebe4b09f7fcff4d1cfb76d7a93876ea8f77` |
| `src/api_gestao_pessoal/models/serie_importancia.py` | Novo | `535e00826010148603f349c42786c20149599d6cd2dfc165980221695052348f` |
| `tests/apoio/esquema.py` | Novo | `318580362b0412b6e2dea3b6b0e9faf3cc9b9ed2960903723682837718b4ceeb` |
| `tests/apoio/migracoes.py` | Novo | `727327d1aa55a52e48430f24fa3c2a751759b8cbc084239c46edcbf28d97e450` |
| `tests/esquema/__init__.py` | Novo | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/esquema/conftest.py` | Novo | `65ade43e9f294d61f6c706f3daa1e8e51db62724943e238ddc8d0c21d166cd8d` |
| `tests/esquema/test_estrutura.py` | Novo | `4a1070fb1e33319ee13bb0d3668d4fb4a9a3af8e9461d1f09c6700170df50769` |
| `tests/esquema/test_identificadores.py` | Novo | `99a1705a70d1240c52794f697549155f279f3225f2741acd65230e61c6f244cb` |
| `tests/esquema/test_migracao.py` | Novo | `8ae5799e7fa06489db67197198e7df3961c828c3e6f4fcc93d74c158914dbb5f` |
| `tests/esquema/test_restricoes.py` | Novo | `d98f4fb62e96bf96fc0d312ba9cdb4e87238e2129c45101d940b171ea17adaea` |
| `tests/esquema/test_tipos_e_tempos.py` | Novo | `5dbb4282dc0169c433ffd61398f246c2da6095eba70b68ed28233f4605400e75` |

### 2.3. Entradas e saídas administrativas (não pertencem à implementação)

| Arquivo | Papel | SHA-256 |
| --- | --- | --- |
| `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md` | Entrada desta auditoria, colocada pelo usuário | `3854631cd82b8cb13f0c2fb92a9e729f21446112428a258906a897e217271db3` |
| `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md` | Este relatório, criado pelo Opus | Calculado depois da gravação (log `51` do diretório de evidências) |

O relatório do Sonnet não foi disponibilizado como arquivo. Usei a síntese transcrita na instrução §4 como evidência auxiliar (§11).

### 2.4. Leitura normativa aplicada

- **F2-D1**: seeds por `instrucoes_categorias() -> list[Insert]` com `op.execute`. Substitui só o trecho de seeds da arquitetura §10.5. Não foi tratada como desvio.
- **D2**: os comandos da Etapa B estão no Prompt F2 §13.
- **D3**: `ls -A1 alembic/versions`. Antes da implementação, a expectativa era só `.gitkeep`; agora há também a revisão `0001`, e `__pycache__` é cache ignorado (log `44`).
- DEC-MV-06, DEC-MV-07, DEC-MV-08, ACH-MV-F1-005 (opção A), REC-MV-033 e REC-MV-034 vigentes.
- DEC-MV-09 a 24 fora do alcance. Nenhum `DESATIVADO`.

---

## 3. Fontes lidas

| Fonte | SHA-256 | Leitura nesta auditoria |
| --- | --- | --- |
| Instrução de auditoria (arquivo) | `3854631cd82b8cb13f0c2fb92a9e729f21446112428a258906a897e217271db3` | Integral (seções conferidas com a mensagem do usuário) |
| `CLAUDE.md` | `35fda3df29e2ae1bd2172a35c430944f4b5fb7d08dd26e0c9bf2123da0405e7d` | Diretrizes §1 e §2 e contrato das 13 tabelas. As 134 colunas foram extraídas por script e os seeds lidos das linhas 823, 879, 946 e 948 |
| `docs/arquitetura/indice.md` | `28f2d37479aa02209ebdd23112032f7aa684cf5c067552426d6d8195db45ad0b` | §3 (precedência), §4 (aprovações e referências M1 a M10) e §5 (gates e pendências) |
| `docs/adr/0002_identificadores_uuid.md` | `951fb3936affa3eb1dcab67f89507eb9620630e938b2868b2f3ebf4b632b7593` | Integral |
| `docs/adr/0001_arquitetura_api_minhavida.md` | `7f7c4745c204a026a3742617bc8525ece2d0b99a722e37ec87d94a0740e23760` | D-09 e menções a seeds (linhas 58, 289 e 430) |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `c691fca0219a1b69674c8a2762d9c3be800ba6b6c081e5414a2b476eafe3db24` | §10.5 (linhas 1725–1752). O restante do §10 é conhecido da preparação, com hash idêntico |
| `docs/arquitetura/plano_fases_api.md` | `05253430f13e462017ff9e0ad788c95692a9bd56b36a4dd9ef20ff02fa01a4ec` | Ficha da F2 (linhas 125–152) |
| `docs/arquitetura/plano_validacao_auditoria.md` | `ba7f8d9234748da3dde04b822d0b4c383b6ebfaed18ed8fb64edb9dd17ae1669` | CT-F1-02 e CT-F1-17 a 19, CT-F2-07 e §7 (severidade) |
| `docs/arquitetura/matriz_requisitos_api.md` | `ed3b2accbc0ed565fbfe9283d4e56c694cecf72ae537e42414789ab06788330c` | Linha T-SEED. O resto é conhecido da preparação, com hash idêntico |
| `docs/arquitetura/analise_projeto_minhavida.md` | `a61962f06274c2bed1775e425d3e1b55a0b0a41995a336b890e7fa83503c4303` | DEC-MV-06 a 08 e REC-MV-033/034, conhecidos da preparação, com hash idêntico. Não relidos |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md` | `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c` | §3 a §6.4 lidos; §6.4 e §6.5 comparados por script com o código e os testes; §7, §8, §10 a §15 lidos |
| `docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md` | `1aefc5f18a214f6857914c23e153174fa106b04337233a5a7923161b07dd0c14` | Só ACH-MV-F1-005 a 007 (linhas 25–27 e 122–128) |
| `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` | `5494d3d450047b95c8e458195cde205d909f680de31c060f65e68d206f7aa357` | Não relida. Nenhum ponto herdado dependia dela além dos já citados na reauditoria |
| Código e testes da entrega (§2.2) | Tabela da §2.2 | Integrais: os 13 modelos, `base.py`, `enums.py`, `__init__.py`, a revisão, o apoio, as fixtures e os 5 arquivos de teste |
| Logs do Sonnet (`f2/`) | `f2_sha256_logs.txt` (27/27) | Todos, inclusive `antes_ruff/sha256_antes_passo9.txt` |

---

## 4. Escopo autorizado e diff real

Observado: `git status`, `git diff --no-renames --name-status 90412ec` e conteúdo integral.

| Ponto | Resultado |
| --- | --- |
| Arquivos alterados = Prompt F2 §7.1 (7) | Conforme. Os 7 caminhos são exatamente os da lista |
| Arquivos novos = Prompt F2 §7.2 (23) | Conforme. Os 23 caminhos são exatamente os da lista; a revisão é `alembic/versions/20261013_0001_esquema_inicial.py` |
| Outros itens no status | Os 11 documentos de preparação (hashes preservados) e o prompt de auditoria (entrada administrativa). Nada mais |
| `pyproject.toml` | Só as três alterações do §9 (`02_diff_pyproject.log` e `git diff`) |
| `tests/conftest.py` | Só `banco_migrado` e dois imports. `SettingsTeste` intacta |
| `tests/apoio/banco.py` | Só `TABELAS_DOMINIO` e `limpar_dados`, iguais ao §10.2; imports no topo |
| `tests/infra/test_alembic_ambiente.py` | Só o CT-F1-17 (nome e `get_heads() == [REVISAO_INICIAL]`). CT-F1-18 e 19 intactos |
| `models/base.py` | **Byte a byte** igual ao §6.1. `CONVENCAO_NOMES` byte a byte igual ao baseline (log `48`) |
| `tests/apoio/migracoes.py` | Byte a byte igual ao §10.1 (log `48`) |
| `models/atividade.py` | Byte a byte igual ao modelo de referência do §6.4 (log `48`) |
| `models/enums.py` | Igual ao §6.2, exceto a assinatura de `tipo_enum` unida numa linha pelo `ruff format` (log `48`; ACH-MV-F2-002) |
| Protegidos | `alembic/env.py`, `alembic.ini`, `alembic/script.py.mako`, `compose.yaml` e `database.py` com os hashes do baseline |
| Fora de escopo | Nenhum service, router, schema ou endpoint; nenhum `relationship`, `create_all`, `drop_all`, `stamp`, `TimestampMixin`, `DESATIVADO`, trigger, extensão, `server_onupdate`, `Identity` ou `autoincrement` (log `27`). Nada de integração financeira externa |
| `commit()` | Nenhum em `src/`. Nos testes, só o CT-F2-19 (autorizado) e o apoio da F1, não alterado |

---

## 5. Ambiente e evidências

Reproduzido (logs `01` a `05`):

| Item | Valor |
| --- | --- |
| uv | `uv 0.11.29 (x86_64-unknown-linux-gnu)` |
| Python | `Python 3.14.6` |
| Docker (servidor) | `29.7.2` |
| Imagem | `postgres@sha256:fe0737ba566a2c5b2a28f34433c0a423261900ec17b9bf7ad115e1aae7e57f1b`; servidor `15.19` |
| Bibliotecas | sqlalchemy 2.1.4, alembic 1.20.0, psycopg 3.3.6, pytest 9.1.1, pytest-asyncio 1.4.0, testcontainers 4.15.0, ruff 0.16.10, pyright 1.1.414, fastapi 0.143.0, pydantic-settings 2.15.0 |

Todos os comandos usaram `uv run --frozen --no-sync`. Nada foi instalado nem sincronizado.

O executor `auditar` (arquivo `auditar.sh` no diretório de evidências) grava `<nome>.comando`, `<nome>.log`, `codigo_saida` e `duracao_s`, e recusa sobrescrever uma evidência existente. Os scripts das sondas e suas saídas estão em `sondas/` e `sondas/saida/`.

---

## 6. Mapa CT → node ID → resultado → evidência

Resultados reproduzidos em `10_esquema.log` (41 passed in 20.74s) e `11_regressoes.log` (4 passed in 5.87s). A coluna “Restrição atingida” vem de `42_sonda_violacoes.log` e de `sondas/saida/violacoes.json`.

| CT | Node ID (`tests/esquema/…` salvo indicação) | Resultado | Prova e observações |
| --- | --- | --- | --- |
| CT-F2-01 | `test_migracao.py::test_upgrade_head_cria_esquema_em_banco_vazio` | PASSED | `downgrade base` → só `alembic_version`; `upgrade head` → 13 tabelas e `0001`. `finally: upgrade head` |
| CT-F2-02 | `test_estrutura.py::test_colunas_conforme_contrato` | PASSED | Constante literal com 134 colunas. Confrontei-a por script com a coluna “Introspecção” do §6.4: **0 diferenças** (log `47b`). Não deriva do metadata |
| CT-F2-03 | `test_estrutura.py::test_identificadores_uuid_sem_padrao` | PASSED | 32 `uuid` iguais ao conjunto literal (conferido com o texto do CT-F2-03: 0 diferenças, log `47b`), sem padrão. As 13 PKs só em `id` |
| CT-F2-04 | `test_identificadores.py::test_orm_gera_uuid_v7` | PASSED | `version == 7` e `criado_em` não expirado. Também passou isolado, como primeiro pedido da migração por sessão (log `45`) |
| CT-F2-05 | `test_identificadores.py::test_sql_textual_sem_id_rejeitado` | PASSED | `23502` na coluna `id` de `usuario` e de `categoria_atividade` |
| CT-F2-06 | `test_migracao.py::test_categorias_iniciais_exatas` | PASSED | 6/8/16 nomes literais, 30 `ativa`, `Outros` com 2 IDs |
| CT-F2-07 | `test_migracao.py::test_seeds_idempotentes` | PASSED | Reexecução das instruções da revisão entregue pela `conexao` e contagens 6/8/16; módulo sem `api_gestao_pessoal`. Preservação dos IDs provada à parte (S5) |
| CT-F2-08 | `test_migracao.py::test_downgrade_base_e_upgrade_head` | PASSED | Downgrade, 0 linhas em `alembic_version`, upgrade e 30 categorias |
| CT-F2-09 | `test_migracao.py::test_alembic_check_sem_diferencas` | PASSED | “No new upgrade operations detected.”, com `compare_type` e `compare_server_default` ativos (`env.py` inalterado) |
| CT-F2-10 | `test_estrutura.py::test_nomes_de_restricoes_e_indices` | PASSED | 93 nomes iguais ao §6.5 e 8 índices iguais ao §6.4, com a ordem das colunas (conferido por script: 0 diferenças, log `47b`); iguais ao metadata e ≤ 63 |
| CT-F2-11 | `test_restricoes.py::test_fk_propriedade_{atividade_serie, importancia_serie, movimentacao_importancia, lembrete_importancia, notificacao_lembrete}` | 5 PASSED | `23503` na FK composta pretendida em cada caso (`fk_atividade_serie_id_serie_atividade` etc.); controle positivo do mesmo usuário |
| CT-F2-12 | `test_restricoes.py::test_fk_categoria_financeira_por_tipo` | PASSED | `23503` em `fk_movimentacao_financeira_categoria_id_categoria_financeira` nos dois sentidos; positivo e `Outros` duplo |
| CT-F2-13 | `test_restricoes.py::test_ocorrencias_atividade`, `::test_ocorrencias_importancia` | 2 PASSED | Casos NULL e 0 em `ck_*_serie_numero`; pares repetidos, inclusive o excluído logicamente, em `uq_*_serie_id_numero_ocorrencia`; `ck_serie_*_numero_final`. Positivos: duas avulsas (NULLs distintos na UNIQUE), `(serie, 1)` e `numero_final = 0` |
| CT-F2-14 | `::test_valor_da_movimentacao`, `::test_valor_previsto_condicional`, `::test_vinculo_de_pagamento` | 3 PASSED | `ck_movimentacao_financeira_valor_positivo`; `valor` NULL em `23502` na coluna `valor`; 8 casos em `ck_*_valor_previsto`; `vinculo_par` (2), `vinculo_despesa`, `excluida_sem_vinculo` e `uq_movimentacao_financeira_importancia_id` |
| CT-F2-15 | `::test_forma_por_tipo`, `::test_horarios`, `::test_datas_e_numeros_de_serie`, `::test_nome_da_atividade`, `::test_enumeracoes_invalidas`, `::test_antecedencias`, `::test_situacao_e_envio_do_lembrete`, `::test_conclusao_manual` | 8 PASSED | Restrição pretendida em todos. `CHEQUE` cai no CHECK do enum (`ck_movimentacao_financeira_forma_movimentacao`) e as combinações tipo×forma em `forma_tipo`; `nome` NULL em `23502` na coluna `nome`; 101 caracteres em `22001`; os 9 valores inválidos de enum nos 9 `ck_<tabela>_<coluna>`; `(3, None)` e `(None, 09:00)` em `lembrete_par` |
| CT-F2-16 | `::test_email_unico`, `::test_recuperacao_unica_por_usuario`, `::test_token_redefinicao_unico`, `::test_lembrete_unico_por_importancia`, `::test_notificacao_por_versao`, `::test_idempotencia_por_usuario_acao_chave` | 6 PASSED | `23505` na UNIQUE pretendida em cada caso; tokens NULL múltiplos aceitos; versão 2 aceita e v1 preservada |
| CT-F2-17 | `test_tipos_e_tempos.py::test_decimal_ida_e_volta`, `::test_json_none_vira_null_sql` | 2 PASSED | `Decimal` de ida e volta, com `str()` exato; `22003` para 10¹⁰; `resposta=None` explícito vira SQL `NULL`; objeto JSON em texto exato |
| CT-F2-18 | (a) `test_estrutura.py::test_fks_restrict`; (b) `test_restricoes.py::test_exclusao_fisica_de_categoria_referenciada` | 2 PASSED | (a) 19 FKs com `confdeltype = 'r'`; (b) `23503` em `fk_atividade_categoria_id_categoria_atividade` |
| CT-F2-19 | `test_tipos_e_tempos.py::test_timestamps` | PASSED | 5 transações. O SQL emitido foi provado à parte (S4) |
| CT-F2-20 | `test_restricoes.py::test_nomes_dec_mv_08` | PASSED | `"ab"` e `""` nos 4 CHECKs da DEC-MV-08; positivos `"abc"` |
| CT-F1-02 | `tests/infra/test_configuracao.py::test_importacao_sem_efeitos` | PASSED | Importação dos 13 modelos sem I/O |
| CT-F1-17 | `tests/infra/test_alembic_ambiente.py::test_upgrade_head_com_revisao_inicial` | PASSED | `get_heads() == ["0001"]` e `check` sem diferenças |
| CT-F1-18 | `tests/infra/test_alembic_ambiente.py::test_upgrade_com_conexao_compartilhada` | PASSED | Inalterado |
| CT-F1-19 | `tests/infra/test_alembic_ambiente.py::test_env_sem_app_e_sem_url` | PASSED | Inalterado |

Casos com NULL. A semântica do PostgreSQL foi conferida contra as definições reais (§8.2):

- CHECK com operando NULL resulta em NULL e passa. Por isso as colunas obrigatórias dependem do NOT NULL (`23502` na coluna certa), e as opcionais usam `IS NULL`/`IS NOT NULL` explícitos.
- UNIQUE com NULL não colide, como mostram as duas avulsas e os tokens NULL.
- FK composta `MATCH SIMPLE` com `serie_id`/`importancia_id` NULL não é verificada, o que é o comportamento contratado para as avulsas e os lançamentos sem vínculo.

O helper `esperar_violacao` exige `DBAPIError` e o SQLSTATE exato dentro de um SAVEPOINT. Uma exceção não relacionada ou a ausência de exceção fazem o teste falhar.

---

## 7. Comandos executados (códigos e linhas finais literais)

Diretório: `$HOME/minhavida_evidencias/f2_auditoria_VJ4xnCZ6/`. O comando literal de cada item está em `<nome>.comando`.

| Log | Comando (resumo) | Código | Duração (s) | Linha final literal |
| --- | --- | --- | --- | --- |
| `00a` a `00i` | Identificação, hashes e manifestos | 0 | < 0,03 | `00h`: 30 linhas `: OK`; `00i`: 27 linhas `: OK` |
| `01_uv` | `uv --version` | 0 | 0,25 | `uv 0.11.29 (x86_64-unknown-linux-gnu)` |
| `02_python` | `uv run --frozen --no-sync python --version` | 0 | 0,16 | `Python 3.14.6` |
| `03_docker` | `docker version --format '{{.Server.Version}}'` | 0 | 0,53 | `29.7.2` |
| `04_imagem` | `docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine` | 0 | 0,16 | `postgres@sha256:fe0737ba566a2c5b2a28f34433c0a423261900ec17b9bf7ad115e1aae7e57f1b` |
| `05_versoes` | versões instaladas | 0 | 0,20 | `pydantic-settings 2.15.0` |
| `10_esquema` | `uv run --frozen --no-sync pytest tests/esquema -vv --color=no` | 0 | 21,82 | `============================= 41 passed in 20.74s ==============================` |
| `11_regressoes` | `uv run --frozen --no-sync pytest tests/infra/test_alembic_ambiente.py tests/infra/test_configuracao.py::test_importacao_sem_efeitos -vv --color=no` | 0 | 8,37 | `============================== 4 passed in 5.87s ===============================` |
| `20_ruff` | `uv run --frozen --no-sync ruff check --no-fix .` | 0 | 0,21 | `All checks passed!` |
| `21_formato` | `uv run --frozen --no-sync ruff format --check .` | 0 | 0,07 | `50 files already formatted` |
| `22_pyright` | `uv run --frozen --no-sync pyright` | 0 | 13,45 | `0 errors, 0 warnings, 0 informations` |
| `23_ruff_arquivos` | `ruff check --no-fix --show-files .` | 0 | 0,20 | Inclui `alembic/env.py` e a revisão |
| `24_ruff_sem_excecao_env` | `ruff check --no-fix --isolated --line-length 79 --select PLC0415 alembic/` | **1 (esperado)** | 0,11 | `Found 1 error.`: sem a exceção, `alembic/env.py:28:5` viola a PLC0415. A exceção é necessária e não cobre mais nada |
| `25_pyright_cobertura` | `pyright --outputjson` e contagem de `.py` | 0 | 6,77 | `filesAnalyzed: 50` = 50 arquivos `.py` em `src`, `tests` e `alembic` |
| `26_supressoes` | `noqa`/`type: ignore`/`pyright: ignore` atual × baseline | 0 | 0,02 | Só `settings.py:42 # pyright: ignore[reportCallIssue]`, idêntico no baseline (F1) |
| `27_proibidos` | Construções proibidas | 0 | 0,01 | Só imports legítimos e os `commit()` do CT-F2-19 e do apoio da F1 |
| `30_heads` | `uv run --frozen --no-sync alembic heads` | 0 | 0,66 | `0001 (head)` |
| `31_history` | `uv run --frozen --no-sync alembic history` | 0 | 0,61 | `<base> -> 0001 (head), Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).` |
| `32_compose` | `env POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet` | 0 | 0,59 | Sem saída |
| `40_sonda_principal` | Sondas S1 a S7 (§8) | 0 | 17,23 | `   prioridade: BAIXA \| expirados: set()` |
| `41_checks_catalogo` | Listagem dos 36 CHECKs | **1** | 0,35 | Erro **do meu script** (`NameError`) numa seção final, depois da listagem completa, que é válida. Os comprimentos foram listados em `41b` |
| `41b_comprimentos_enum` | Comprimentos das 9 colunas enum | 0 | 0,11 | `movimentacao_financeira forma_movimentacao character varying(20) padrão: None` |
| `42_sonda_violacoes` | Plugin que registra a restrição de cada caso negativo | 0 | 9,91 | `29 passed in 7.18s` |
| `43_gerada_x_final` | SQL offline da revisão gerada × final | 0 | 0,96 | Diff (§8.3) |
| `44_versions_d3` | `ls -A1 alembic/versions` | 0 | 0,004 | `.gitkeep`, `20261013_0001_esquema_inicial.py` e `__pycache__` (cache ignorado) |
| `45_migracao_pedida_por_teste_async` | CT-F2-04 isolado | 0 | 13,86 | `============================== 1 passed in 11.24s ==============================` |
| `46_modelos_x_contrato` | Comparação por AST dos 13 modelos com o §6.4 | 0 | 0,30 | `tabelas=13 colunas_comparadas=134 problemas=0` |
| `47_literais_testes_x_contrato` | Constantes literais de `test_estrutura.py` × §6.4, §6.5 e CT-F2-03 | 0 | 1,18 | Colunas, nomes e UUIDs iguais; a leitura dos índices falhou por erro **do meu regex** (`ÍNDICES §6.4: 0`), corrigido em `47b` |
| `47b_literais_testes_x_contrato` | Mesma comparação, regex corrigido | 0 | 0,90 | `UUID CT-F2-03: 32 == teste: True []` (antes: `ÍNDICES §6.4: 8 == teste: True`) |
| `48_conteudos_exatos` | `base.py`, `enums.py`, `migracoes.py` e `atividade.py` × blocos exatos do prompt; `CONVENCAO_NOMES` × baseline | 0 | 0,08 | `IDÊNTICA` (só `enums.py` difere, na assinatura formatada) |
| `50_manifesto_pos_verificacoes` | Manifesto depois das verificações | 0 | 0,04 | `índice vazio` (precedido de “objeto idêntico ao manifesto inicial (76 arquivos)”) |

Execuções adicionais justificadas (instrução §9.3):

- `42` repetiu a seleção de `test_restricoes.py` mais dois nodes. Dúvida concreta: o helper só confere o SQLSTATE.
- `45` executou um único node. Dúvida concreta: possível conflito de loop quando um teste assíncrono dispara a migração por sessão.

A suíte completa não foi executada.

---

## 8. Resultados da revisão

### 8.1. Modelos ORM (observado e reproduzido)

- **Comparação por AST com o §6.4** (log `46`, `sondas/compara_modelos_contrato.py`, sem importar a aplicação): 13 classes e 134 colunas, com **0 divergências** nos seguintes pontos:
  - ordem;
  - anotação `Mapped[...]`;
  - tipo SQLAlchemy, PK e `default`;
  - `nullable`, `server_default` e `onupdate`;
  - FK simples com `RESTRICT`;
  - ausência de outros argumentos.
- `default=` só no `id` (`uuid.uuid7`), conforme REC-MV-033.
- O `id` não declara `nullable`, como o modelo de referência do próprio prompt; a PK garante NOT NULL (CT-F2-02). Veja ACH-MV-F2-002, item c.
- O `CriadoAtualizadoMixin` está exatamente nas 8 tabelas previstas. `notificacao.criada_em` e `requisicao_idempotente.criado_em` só têm `server_default`.
- **Enumerações (S6).** As 9 colunas têm `native_enum=False`, `create_constraint=True`, `validate_strings=True`, os valores e o `name=<coluna>` contratados e `length` = 7, 20, 5, 10, 10, 5, 10, 7 e 20. Com o tipo do modelo, `'ALTO'` é recusado pelo SQLAlchemy (`LookupError`) antes de chegar ao banco.
- `eager_defaults=True` está na `Base` e é herdado: `Usuario` e `Atividade` emitem `RETURNING` (S4).
- **Observação sem efeito (não é achado).** `lembrete_importancia.importancia_id` declara a unicidade com `UniqueConstraint("importancia_id")` em `__table_args__`, e não com `unique=True` na coluna, como pede a regra de estilo do §6.4. O nome (`uq_lembrete_importancia_importancia_id`), a definição e o comportamento são idênticos (CT-F2-10, S1 e `test_lembrete_unico_por_importancia`). Não recomendo correção.

### 8.2. Esquema materializado × oráculo do contrato (S1, reproduzido)

Bancos usados:

- `entrega`: `upgrade head` pela API do Alembic com o `alembic.ini` real e `url_banco` do container;
- `oraculo`: `create_all` de um metadata montado **só** a partir do `CLAUDE.md`. As colunas, os tipos e a nulidade foram extraídos por script; os padrões, CHECKs, FKs, UNIQUEs e índices foram transcritos das regras textuais (`sondas/oraculo_contrato.py`).

Comparação de catálogo:

- **diferenças: só a tabela `alembic_version`**, esperada;
- colunas (tipo, nulidade, padrão, identity/generated), restrições (`pg_get_constraintdef`, ação de exclusão e de atualização, *match*, *deferrable*) e índices (`pg_get_indexdef`) iguais.

Números do banco entregue:

| Item | Valor |
| --- | --- |
| Tabelas de domínio | 13 |
| Colunas | 134, das quais 32 `uuid`, nenhuma identity, generated ou padrão de `id` |
| Restrições | 13 PK, 17 UNIQUE, 19 FK e 36 CHECK (**9 de enumeração e 27 explícitos**, log `41`). Nenhum CHECK duplicado |
| Índices sem restrição | 8 |
| Maior nome | 60 caracteres |
| FKs | 19, todas `ON DELETE RESTRICT` (`r`), `ON UPDATE NO ACTION`, `MATCH SIMPLE` e não postergáveis; 13 simples e 6 compostas |
| Triggers / funções em `public` / sequências e visões | Nenhum |
| Extensões | Só `plpgsql`, padrão do PostgreSQL |

Os 36 CHECKs, com a definição normalizada pelo PostgreSQL, estão em `41_checks_catalogo.log`. Confrontei cada um com as regras do `CLAUDE.md`, inclusive:

- a forma `IS NULL`/`IS NOT NULL` explícita das condições opcionais (regra 2 de integridade);
- a FK composta `(categoria_id, tipo)`;
- as cinco FKs compostas de propriedade com `UNIQUE(id, usuario_id)` nos destinos;
- os quatro CHECKs da DEC-MV-08.

### 8.3. Migração e seeds (observado e reproduzido)

- **Grafo.** Uma revisão `0001`, `down_revision = None`, sem ramificações (`heads` e `history`, S7). Docstring igual ao §8.2, item 1.
- **Gerada × final (log `43`).** Normalizando a formatação pelo SQL offline, a versão final difere da gerada **só** em dois pontos:
  - removeu as duas cópias extras de cada CHECK de enumeração que o autogenerate emitira, 18 linhas nas 9 colunas, deixando uma por coluna (o próprio tipo `Enum`);
  - acrescentou os 3 INSERTs de seeds.

  Não há mudança de domínio. O autogenerate já tinha emitido `length=10/20` onde o comprimento difere do maior valor; a versão final declara `length=` nas 9 colunas, conforme o §8.2, item 3. Os imports, a docstring e a formatação mudaram conforme o §8.2 e o `ruff format`.
- **Ordem e operações.** Criação compatível com as FKs. `downgrade()` remove os 8 índices e as 13 tabelas em ordem inversa, sem operações de dados.
- **Isolamento do módulo.** A revisão não importa `api_gestao_pessoal`, `Connection` nem usa `op.get_bind()`. Os seeds seguem a emenda F2-D1: `instrucoes_categorias()` com `sa.table` local, `uuid.uuid7()`, `insert(...).on_conflict_do_nothing` em `nome` e `(tipo, nome)`, executada por `op.execute` no fim de `upgrade()`.
- **Seeds (S5).**
  - As 30 grafias são idênticas às listas do `CLAUDE.md`, inclusive os acentos.
  - Os 30 IDs são distintos e todos UUIDv7, com `ativa = true`.
  - A reexecução de `instrucoes_categorias()` da revisão entregue, numa transação, mantém **as mesmas 30 linhas com os mesmos IDs**, conforme o `DO NOTHING`.
  - O CT-F2-07 prova as contagens; a S5 prova a preservação dos IDs.
- **Fronteira transacional (S2).** Usei uma cópia de `alembic/` com `env.py`, `script.py.mako` e a revisão entregue **byte a byte idênticos** (SHA-256 conferidos) e acrescentei só uma revisão de sonda `9999`, posterior à `0001`. Em `upgrade head`:
  - a `9999` contou **30 categorias** dentro da transação e lançou uma exceção;
  - por outra conexão, o banco ficou **sem nenhuma tabela**, inclusive `alembic_version`.

  Os 13 `CREATE TABLE`, os índices e os seeds são, portanto, desfeitos juntos (`transaction_per_migration=False` e DDL transacional do PostgreSQL).
- **Modo offline (S3), com geração e execução separadas:**
  - **Geração:** `command.upgrade(cfg, "head", sql=True)` com o `alembic.ini` real, `url_banco` fictícia (porta 1) e `configurar_logging=False`. Durante toda a sonda, `obter_settings` foi substituída por uma função que falha: as configurações reais não foram carregadas e não houve conexão.
  - **Conteúdo gerado:** 14 `CREATE TABLE` (13 + `alembic_version`), 8 `CREATE INDEX`, 3 INSERTs de categorias com 30 UUIDv7 literais e os `ON CONFLICT` corretos, `INSERT INTO alembic_version`, nenhum marcador de parâmetro e um par `BEGIN`/`COMMIT` (`sondas/saida/offline_head.sql`).
  - **Execução:** o roteiro, aplicado a um banco vazio, gerou catálogo **idêntico** ao do upgrade online, contagens 6/8/16, UUIDv7 e `alembic_version = 0001`.
- **`alembic check`.** Sem diferenças (CT-F2-09 e CT-F1-17), com `compare_type` e `compare_server_default` ligados. O risco levantado na Etapa A (`'BAIXA'` contra `'BAIXA'::character varying`) não se materializou.

### 8.4. Timestamps e `eager_defaults` (S4, reproduzido)

SQL capturado no `flush` de uma `AsyncSession` criada por `criar_fabrica_sessoes`:

- **INSERT de `Usuario`:** `INSERT INTO usuario (id, nome_completo, email, senha_hash, data_nascimento, fuso_horario) VALUES (...) RETURNING usuario.criado_em, usuario.atualizado_em`. Nenhum SELECT posterior. Atributos não expirados e `criado_em == atualizado_em`.
- **`flush` sem mudança:** nenhuma instrução.
- **UPDATE:** `UPDATE usuario SET nome_completo=..., atualizado_em=now() WHERE usuario.id = ... RETURNING usuario.atualizado_em`. Nenhum SELECT; nada expirado.
- **INSERT de `Atividade`:** `... RETURNING atividade.prioridade, atividade.criado_em, atividade.atualizado_em` (truncado no log por largura). `prioridade = BAIXA`, vinda do padrão do banco.

Assim, a alegação do contrato (§6.3: valores “por `RETURNING`, na própria instrução”) está provada pelo SQL emitido, não só pelo estado dos atributos.

O CT-F2-19 complementa com cinco transações:

- `criado_em = atualizado_em = t1`;
- `atualizado_em = t2` no UPDATE do ORM, com `criado_em = t1` e `t2 > t1`;
- UPDATE textual que **não** altera `atualizado_em` (não há trigger);
- `criada_em`/`criado_em` das tabelas sem mixin iguais a `t5`.

### 8.5. Fixtures e isolamento (observado e reproduzido)

- `garantir_banco_descartavel` (F1) compara o host, a porta e o nome com o container, e não só o nome. `banco_migrado`, `config_migracao` e `limpar_dados` a chamam. As URLs vêm de `container_postgres`.
- `limpar_dados`: `TRUNCATE` da lista explícita de 10 tabelas, montado com `psycopg.sql`, sem `CASCADE` nem `RESTART IDENTITY`. Preserva os catálogos e `alembic_version` (REC-MV-034). Funciona sem `CASCADE` porque todas as tabelas que referenciam `usuario` estão na lista; o CT-F2-19 executa a limpeza no `finally`.
- `conexao` abre uma transação e a reverte no `finally`, com `close()` e `dispose()`. `sessao_orm` faz rollback e `dispose()`. `fabrica_sessoes` faz `dispose()` e a limpeza.
- Os testes de downgrade (CT-F2-01 e 08) não pedem `conexao`, consultam por `consultar()` com conexão independente e restauram `head` no `finally`.
- **Migração por sessão.** Fixture síncrona com `command.upgrade(config_alembic(url), "head")`. Executada isoladamente a partir de um teste assíncrono, sem conflito de loop (log `45`).
- `SettingsTeste` não foi alterada, e nenhuma fixture nova lê o `.env`.
- Commits de dados: só no CT-F2-19, autorizado.

### 8.6. Qualidade e ACH-MV-F1-005 (reproduzido)

- Ruff e formatação limpos, com `alembic/env.py` e a revisão incluídos (logs `20`, `21` e `23`).
- Pyright analisou 50 arquivos, todos os `.py` de `src`, `tests` e `alembic`, com 0 erros (logs `22` e `25`).
- A exceção `PLC0415` está só em `alembic/env.py` e é necessária (log `24`).
- Nenhuma supressão nova (log `26`). O `# noqa: PT012` que o Sonnet declarou ter removido não existe no estado final; o estado intermediário não foi preservado (§11).

---

## 9. D4 — descrição em `alembic history`

**Fatos (observados e reproduzidos):**

1. Revisão `20261013_0001_esquema_inicial.py`, `revision = "0001"`, `down_revision = None`, sem ramificações. A primeira linha da docstring é `Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).`, seguida de uma linha em branco e das linhas `Revision ID`/`Revises`/`Create Date`, exatamente como manda o Prompt F2 §8.2, item 1.
2. Saída real (logs `31` e `14b` do Sonnet, idênticos): `<base> -> 0001 (head), Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).`
3. **Origem no Alembic 1.20.0 instalado:**
   - `Script.doc` devolve `re.split("\n\n", self.longdoc)[0]`, ou seja, o primeiro parágrafo da docstring do módulo (`alembic/script/base.py:838-841`);
   - `cmd_format(include_doc=True)` acrescenta `", %s" % self.doc` (linhas 939-940);
   - `command.history` usa `cmd_format` (`alembic/command.py:597-605`) e não executa o `env.py`;
   - reprodução (S7): `Script.doc` = `'Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).'`, e `cmd_format` = a linha do log;
   - aplicada à revisão **gerada** (`05_revisao_gerada.py`), a mesma regra devolve `'esquema inicial'`.

**Diagnóstico.**

- A divergência nasce **na especificação**: a expectativa do Prompt F2 §13, tabela, linha 14 (`<base> -> 0001 (head), esquema inicial`), descreve a revisão como gerada, antes da edição exigida pelo próprio §8.2, item 1.
- As duas cláusulas são incompatíveis: cumprir o §8.2 produz necessariamente a saída observada.
- A migração está correta, e a evidência é verdadeira e reproduzível.

**Condição de parada e cronologia:**

- A linha 14 da tabela de expectativas **não** diz “pare”, ao contrário das linhas 0 e 9.
- O bloqueio do §11 sobre “valor literal deste prompt [que] diverge do comportamento real do PostgreSQL” trata do PostgreSQL. Mesmo aplicado por analogia, o comportamento exigido é registrar o valor observado sem ajustar a expectativa, e foi o que o Sonnet fez: manteve a docstring do §8.2 e relatou a D4.
- Não houve descumprimento de condição de parada.
- Pelas datas de modificação, os passos 14b a 18 foram gravados em sequência, num intervalo de cerca de 1,1 s (de 14:29:52.139 a 14:29:53.221), e são todos de leitura ou hash.
- Nenhum arquivo da entrega foi modificado depois das 14:28:42.55, antes de `07_pytest_esquema_2`. Essas datas são **indicativas** (inferido); a prova forte da identidade é o manifesto (§2.1).

**Impacto e classificação.**

- Nenhum impacto técnico.
- Nenhum teste depende do texto do `history`.
- `heads` está correto e o gate do §11 (“`alembic heads` = `0001 (head)`”) foi cumprido.

Classificação: **errata de especificação, P3** (ACH-MV-F2-001). O ajuste documental mínimo está na §13, B2.

**Não** proponho mudar a docstring da migração. Esta D4 não fica aprovada por este relatório: a errata depende de autorização documental do usuário.

---

## 10. Achados e pendências herdadas

### 10.1. Achados da F2

**ACH-MV-F2-001 — P3 — ABERTO — Expectativa de `alembic history` contraditória no Prompt F2 (D4)**

1. **Origem:** especificação (Prompt F2, do Opus).
2. **Fato:** Prompt F2 §13, tabela de expectativas, linha 14 (linha 1349 do arquivo), exige `<base> -> 0001 (head), esquema inicial`. O §8.2, item 1 (linha 888), exige a docstring cujo primeiro parágrafo o Alembic exibe (§9).
3. **Reprodução:** log `31` e S7 (`40_sonda_principal.log`).
4. **Impacto:** nenhum no objeto. Pode induzir um falso bloqueio ou uma edição indevida da docstring em futuras releituras. Fase afetada: F2, só documental.
5. **Correção recomendada:** errata anotada no Prompt F2, sem reescrever o histórico (§13, B2), e regra para os próximos prompts: expectativas de saída derivadas do conteúdo final, não do artefato gerado.
6. **Critério de encerramento:** errata registrada no Prompt F2 ou no `indice.md`, com remissão a este relatório.
7. **Decisão do usuário:** só a autorização da edição documental.

**ACH-MV-F2-002 — P3 — ABERTO — Erratas de procedimento e de contrato no Prompt F2, sem efeito no objeto**

1. **Origem:** especificação (Prompt F2).
2. **Fatos:**
   - a) §6.2 diz “conteúdo-alvo exato” (log `48`), mas a assinatura de `tipo_enum` em três linhas não é estável sob `ruff format`, e a versão entregue a une numa linha de 79 caracteres. O `CLAUDE.md` §2 obriga o formatador.
   - b) §13, passo 9, não prevê o caso em que `ruff check --fix` termina com código 1 (`09a_ruff_fix.log`: 13 E501 restantes). O Sonnet corrigiu à mão uma string SQL em `test_tipos_e_tempos.py` e repetiu 09a, 09b e 09c com o sufixo `_2`, preservando os logs originais. Isso é razoável, mas são comandos fora da lista literal.
   - c) §6.4 diz “toda coluna informa `nullable=`”, mas o modelo de `id` do próprio prompt não informa. A entrega segue o modelo.
   - d) Os comandos do §13 usam `uv run` sem `--frozen --no-sync`. O `04_metadata.log` mostra a reinstalação do pacote local (`Uninstalled 1 package` / `Installed 1 package`), sem mudança de dependências e com o `uv.lock` inalterado.
3. **Reprodução:** comparação por script do §6.2 com `enums.py`; logs `09a`, `09a_2`, `09b`, `09b_2`, `09c` e `09c_2` do Sonnet; `antes_ruff/sha256_antes_passo9.txt` (14 arquivos alterados entre o snapshot e o estado final, o mesmo número dos “14 files reformatted”).
4. **Impacto:** nenhum no objeto. A verificação final, dos passos 11 a 13, e a minha reprodução estão limpas.
5. **Correção recomendada:** errata no Prompt F2 (§13, B3) e quatro lições para os próximos prompts:
   - conteúdos exatos já formatados pelo Ruff;
   - um passo explícito para erros residuais, com reexecução sufixada;
   - coerência entre a regra e o modelo;
   - `--frozen --no-sync` nos comandos.
6. **Critério de encerramento:** errata e lições registradas, e o próximo Prompt Master (F3) aplicando-as.
7. **Decisão do usuário:** autorização documental.

**ACH-MV-F2-003 — P3 — ABERTO — Plano de fases prescreve `alembic upgrade --sql` pela CLI**

1. **Origem:** documentação normativa (plano de fases, do Opus).
2. **Fato:** `plano_fases_api.md`, ficha da F2, item 12 (linha 151): “SQL gerado (`alembic upgrade --sql` opcional, para revisão)”. Pela CLI, sem `config.attributes["url_banco"]`, o `env.py` cai em `obter_settings()` e lê `DATABASE_URL` do `.env` (`alembic/env.py:23-30`). O Prompt F2 §0, item 6, já proíbe esse uso, e a instrução desta auditoria §0.6 o trata como pendência documental.
3. **Reprodução:** leitura do `env.py`. A geração offline segura foi feita pela API com URL fictícia (S3).
4. **Impacto:** risco de leitura do `.env` real por quem seguir o plano literalmente, da mesma classe do ACH-MV-F1-007. Não ocorreu nesta fase.
5. **Correção recomendada:** §13, B1.
6. **Critério de encerramento:** linha 151 substituída pela orientação via API.
7. **Decisão do usuário:** autorização documental.

Não há achados de implementação, de teste ou de ambiente.

### 10.2. Pendências herdadas da F1

| Achado | Verificação na F2 | Recomendação |
| --- | --- | --- |
| ACH-MV-F1-005 (P3) | Opção A aplicada exatamente (3 alterações): Ruff e Pyright cobrem `alembic/` (logs `23` e `25`); `PLC0415` ignorada só em `alembic/env.py` e necessária (log `24`); nenhuma outra exceção (log `26`) | **Encerrar** |
| ACH-MV-F1-006 (P3) | Todos os passos do §13 com comando (0 a 18, exceto 3 e 6, que são só edição) têm log com o comando literal do prompt e `codigo_saida`; as reexecuções têm sufixo `_2` e os originais foram preservados; há um snapshot de hashes antes do passo 9 e um manifesto de 27 logs (27/27 OK). Os números da síntese do relatório (41 em 19.13s, 4 em 13.49s, 50 arquivos, 0 erros, `0001 (head)`) coincidem com os logs. Limites: o relatório integral não veio como arquivo, e estados anteriores ao passo 7 não foram preservados, por desenho, porque os passos 3 e 6 são só edição | **Encerrar**, com a recomendação de que o próximo prompt peça o relatório gravado em arquivo no diretório de evidências |
| ACH-MV-F1-007 (P3) | O Compose usou `--env-file /dev/null` (log `15` do Sonnet e meu log `32`). Os logs do Sonnet mostram apenas `heads` e `history` pela CLI; o autogenerate, os testes e as minhas sondas usaram a API com `url_banco`, e as sondas provaram que `obter_settings()` não foi chamada | **Encerrar**. O risco análogo do plano de fases foi registrado como ACH-MV-F2-003 |

ACH-MV-ARQ-006 segue encerrado. A lacuna formal do ACH-MV-ARQ-019 não foi reaberta e não bloqueia a F2. Não proponho commit intermediário.

---

## 11. Provas próprias, evidências reaproveitadas e limites

**Provas próprias, reproduzidas nesta auditoria:**

- execução das seleções da fase e das regressões;
- Ruff, formatação e Pyright, com a cobertura de `alembic/`;
- `heads`, `history` e Compose;
- comparação por AST dos modelos com o §6.4;
- comparação das constantes literais dos testes com o §6.4, o §6.5 e o CT-F2-03;
- sondas S1 a S7;
- sonda das violações (88 chamadas);
- SQL offline da revisão gerada × final;
- teste assíncrono isolado;
- manifestos antes e depois.

**Evidências do Sonnet reaproveitadas (auxiliares, integridade conferida):**

- `00_revalidacao.log`;
- `05_autogenerate.log` e `05_revisao_gerada.py`, base do diff da §8.3;
- logs `07`, `08`, `09*`, `11` a `18`;
- `antes_ruff/`.

Não executei nenhum script contido nesses logs.

**Limites:**

- O relatório final do Sonnet não estava disponível como arquivo. Confrontei a síntese transcrita na instrução §4, e não encontrei contradição.
- As afirmações sobre a remoção de `# noqa: PT012` e sobre a troca de listas por tuplas em `test_estrutura.py` referem-se a estados **não preservados**. Isso é ausência de prova histórica, não contradição. Pelas datas, `test_estrutura.py` não foi editado depois do `ruff format`, e o `ruff` não troca listas por tuplas; portanto a troca, se houve, é anterior ao primeiro teste registrado (inferido). O estado final foi verificado: os valores esperados são literais, independentes do metadata e iguais ao contrato.
- O oráculo da S1 é independente da implementação, mas não de quem especificou:
  - as colunas vêm do `CLAUDE.md` por extração automática;
  - as regras foram transcritas pelo mesmo autor do Prompt F2.

  A semântica dos CHECKs foi conferida também pelos 88 casos negativos, cada um na restrição pretendida, e pelos controles positivos.
- As datas de modificação dos arquivos são indicativas, e não as uso como prova de cronologia.
- A concorrência está fora do escopo da F2 e não foi exigida.

**Sem verificação:** nenhum requisito obrigatório.

---

## 12. Manifesto antes e depois

- `00_manifesto_antes.sha256` (76 arquivos, sem o `.env`), gerado antes de qualquer teste, e `50_manifesto_pos.sha256`, gerado depois de todas as verificações: **idênticos**. O objeto não mudou durante a auditoria.
- O `.env` não foi aberto, listado com hash, copiado nem impresso.
- Caches gerados pelas execuções (`__pycache__`, `.pytest_cache` e `.ruff_cache`) são ignorados pelo Git e não pertencem ao objeto. As sondas usaram `-B` e `-p no:cacheprovider` quando aplicável.
- Arquivos administrativos:
  - `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md` já estava presente no início, como entrada;
  - este relatório foi o único arquivo criado no repositório pela auditoria.

  O manifesto final, gravado depois deste relatório (log `51`), deve diferir do `50` apenas por este arquivo.

---

## 13. Anexo — reconciliações documentais propostas (não aplicadas)

### A. Já aprovado: falta incorporar ao documento

**A1. Arquitetura §10.5 (emenda F2-D1, aprovada pelo usuário antes da Etapa B).** Linha 1745, texto atual:

> - Seeds: função de módulo `inserir_categorias(conexao: Connection) -> None`, chamada por `upgrade()` com `op.get_bind()` e reexecutável sem duplicar (CT-F2-07).

Texto proposto:

> - Seeds: função de módulo `instrucoes_categorias() -> list[Insert]`, que monta os INSERTs idempotentes (`sa.table` local, `uuid.uuid7()`, `on_conflict_do_nothing` pela chave natural) sem acessar o banco; `upgrade()` os executa no fim com `op.execute`, na transação da migração e também no modo offline. Reexecutável sem duplicar nem trocar IDs (CT-F2-07). Emenda F2-D1.

**A2. Plano de fases, F2, item 10 (D2).** Linha 143: trocar “literais no Prompt F2 §14” por “literais no Prompt F2 §13”.

**A3. Prompt F2 §12, passo 8 (D3).** Preservar a linha 1238 e acrescentar logo abaixo:

> Emenda operacional (Etapa A, 2026-10-13): usar `ls -A1 alembic/versions`; `ls` sem `-A` não mostra `.gitkeep`.

**A4. Índice §4.** Registrar:

- **M11:** mensagem do usuário que aprovou a emenda F2-D1 (com as respostas D2 e D3) e autorizou a Etapa B, atestada no §3 da instrução desta auditoria. Não tive o texto literal; o usuário confirma a referência.
- **M12:** mensagem que pediu esta auditoria.

### B. Nova autorização documental solicitada (não aprovada por este relatório)

**B1. Plano de fases, F2, item 12 (ACH-MV-F2-003).** Linha 151, trocar “SQL gerado (`alembic upgrade --sql` opcional, para revisão)” por:

> SQL gerado em modo offline somente pela API do Alembic (`command.upgrade(cfg, "head", sql=True)`), com `config.attributes["url_banco"]` fictícia, `configurar_logging=False` e saída capturada fora do repositório; nunca `alembic upgrade --sql` pela CLI, que carregaria as configurações reais.

**B2. Prompt F2 §13, tabela, linha 14 (ACH-MV-F2-001, D4).** Manter o texto original e acrescentar uma nota abaixo da tabela:

> Errata (auditoria F2, 2026-10-13): a saída correta do passo 14b é `<base> -> 0001 (head), Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).`. O `alembic history` mostra o primeiro parágrafo da docstring exigida em §8.2, item 1; a expectativa original refletia a revisão gerada, antes da edição.

**B3. Prompt F2, erratas de procedimento (ACH-MV-F2-002).** Nota única no fim do §13:

> Erratas (auditoria F2): (a) §6.2 é exato salvo a formatação do `ruff format`; (b) se `ruff check --fix` deixar erros, corrigir à mão e repetir 09a–09c com sufixo `_2`, preservando os originais; (c) o `id` segue o modelo do §6.4, sem `nullable=` (a PK implica NOT NULL); (d) comandos `uv run` devem usar `--frozen --no-sync` nos próximos prompts.

**B4. (Opcional) Plano de validação, CT-F2-07 (linha 199).** Trocar “Reexecução da função de seed da revisão” por “Reexecução das instruções de `instrucoes_categorias()` da revisão”.

**B5. Fechamento documental da F2 (quando o usuário autorizar):**

- `indice.md` §5: G5 da F2 = `APROVADO_COM_P3`, com remissão a este relatório; ACH-MV-F1-005, 006 e 007, conforme a decisão do usuário sobre as recomendações da §10.2; ACH-MV-F2-001 a 003 em acompanhamento.
- `plano_fases_api.md` §3 e cabeçalho do Prompt F2: estado “auditada, `APROVADO_COM_P3`”.
- Depois do commit pelo usuário: o G6 da F2.

Separação. A1 a A4 são incorporações de decisões já tomadas. B1 a B5 dependem de autorização documental. Nenhuma delas altera código, testes, migração ou configuração, e nenhuma exige prompt de correção para o Sonnet.

---

## 14. Próxima ação do usuário

1. Revisar este relatório.
2. Decidir sobre:
   - aceitar os três P3 em acompanhamento;
   - as recomendações de encerramento do ACH-MV-F1-005, 006 e 007;
   - a autorização das reconciliações A1 a A4 e B1 a B5.
3. Preparar o commit do objeto aprovado, com lista explícita:
   - os 30 arquivos da §2.2;
   - os 11 documentos de preparação (modo A);
   - à sua escolha, o prompt de auditoria e este relatório.

   Confira os hashes contra a §2.2 e o manifesto final. O Opus pode gerar um script de commit com manifesto, como na F1, se o usuário pedir.

Esta auditoria **não** cumpre o G6 da F2, **não** autoriza a F3 e **não** aprova DEC-MV-09 a 13. Não foi criado prompt de correção, porque não há correção de implementação a fazer.
