# Prompt Master — Sonnet 5 — F1: correções pós-auditoria

| Campo | Valor |
| --- | --- |
| Fase | F1 — Fundação técnica, correções da auditoria independente |
| Estado | **`BLOQUEADO`** até a decisão da DEC-MV-26 (condição de liberação abaixo) |
| Data | 2026-10-11 |
| Autor | Claude Opus 5.5 (auditoria e especificação) |
| Destinatário | Claude Sonnet 5 (implementação) |
| Origem | `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md`, veredito `BLOQUEADO` |

> **Condição de liberação da Etapa A.** Uma das duas fontes abaixo precisa registrar a aprovação expressa da DEC-MV-26, opção B (`exclude = ["*.md"]` em `[tool.ruff.format]`):
>
> - `docs/arquitetura/indice.md` §4;
> - a mensagem do usuário que encaminha este prompt, com o texto “Aprovo a DEC-MV-26, opção B”.
>
> Sem uma delas, **pare** e informe que o prompt continua bloqueado. Se o usuário tiver escolhido outra opção (A ou C), **pare**: este prompt precisa ser revisado pelo Opus.
>
> **Implementação: não autorizada.** A Etapa B só começa com a resposta “pode implementar” do usuário ao plano da Etapa A.

---

## 0. Regras absolutas

1. Comunicação, comentários e documentação em **PT-BR**. Funções e variáveis em `snake_case`; classes em `PascalCase`.
2. **Você não toma decisões arquiteturais.** Aplique literalmente as alterações da §7.
   - Divergência entre este prompt e o repositório: **pare** e relate.
   - Necessidade de mudar algo fora da §6: **pare** e relate.
3. Modo **LOCAL**. Proibido:
   - `git add`, `git commit`, `push`, merge e PR;
   - `git reset`, `git checkout -- …`, `git restore`, `git stash`, `git clean`.
4. Não leia nem exponha o `.env`. Não reproduza credenciais.
5. **Nunca** execute `ruff format .` nem `ruff check --fix .` antes do passo 6 da §10. Antes da DEC-MV-26 aplicada, `ruff format .` reescreve `docs/arquitetura/arquitetura_api_minhavida.md` (ACH-MV-F1-004).
6. Se algum arquivo protegido (§6.2) mudar, **pare imediatamente** e relate o arquivo e o comando. **Não restaure por conta própria.** A restauração é decisão do usuário.
7. Não execute a suíte completa, `task test`, `task lint`, nem `pytest` sem as seleções da §10.
8. Não altere testes, rotas ou fixtures além do especificado. Não acrescente supressões (`noqa`, `pyright: ignore`, `type: ignore`), nem dependências, nem configuração além das 3 linhas da DEC-MV-26.

## 1. Estado de partida verificável

- `HEAD` = `bd2b2e0f1e4f2674b528175e535b0931badec34a` (baseline da F0). A F1 **não tem commit**.
- Índice do Git vazio.
- `src/api_gestao_pessoal/schemas/message.py` removido da árvore de trabalho.
- `git status --short` esperado (a ordem pode variar):

```text
 M .gitignore
 M pyproject.toml
 M src/api_gestao_pessoal/database.py
 M src/api_gestao_pessoal/main.py
 M src/api_gestao_pessoal/models/base.py
 D src/api_gestao_pessoal/schemas/message.py
 M src/api_gestao_pessoal/settings.py
 M uv.lock
?? .env.exemplo
?? PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md
?? alembic.ini
?? alembic/
?? compose.yaml
?? docs/auditorias/
?? src/api_gestao_pessoal/__init__.py
?? src/api_gestao_pessoal/erros.py
?? src/api_gestao_pessoal/models/__init__.py
?? src/api_gestao_pessoal/rastreamento.py
?? src/api_gestao_pessoal/routers/
?? src/api_gestao_pessoal/schemas/__init__.py
?? src/api_gestao_pessoal/schemas/erro.py
?? src/api_gestao_pessoal/schemas/saude.py
?? tests/
```

Se o `HEAD` for outro, se houver arquivos preparados para commit ou se algum hash abaixo divergir, **pare** e relate. Um commit feito pelo usuário depois da auditoria também é motivo de parada: o usuário decide.

### 1.1. Bloco A — arquivos que esta correção altera (estado auditado)

```text
54bd1c986794bb98136cfc9997420759f943711ab9b1645b3b10c903883864d5  pyproject.toml
013d35ffb305d079ae865f1efba3288390eb6aecbca7b03c911e03e66daf3525  src/api_gestao_pessoal/erros.py
8745ba8f239d81236d81ed08aef96221032c61466dbd004826ce81f5eabc9481  tests/apoio/rotas_teste.py
44d00c2f24c9c2d143cc3e2de901a342f3bfd93b2a4833e2238b9eb0ad2b7707  tests/conftest.py
aaaa587237ec8461085bf23cf6b1dcaebdc929468bcb13601fb020421c6314de  tests/infra/test_configuracao.py
e42dabbda535ae26a5161f3ef3325f1b1c3fd8acc71be2c1d18e778348aa3e48  tests/infra/test_sessao_transacao.py
```

### 1.2. Bloco B — arquivos protegidos (devem permanecer idênticos do início ao fim)

```text
dc824d5228126e5cfa2ef3c6fe3c939fb99fc3303487109bd1d0c443867dfdb0  .env.exemplo
5b7e3c47d39481cea53c19583158f9fa93185f86346ae0a2cc814ff92e84f973  .gitignore
a876e0b10411037a012498b9fe18d9bc1df32ed8b722a13564dc944ddcfd9135  .python-version
565dc6b262d1bf0dfa54a712eb032606b49cb6a7aa77015a073fc682354ae473  CLAUDE.md
38386a4fdfd3ce1c4f05214cc7a327e94fe8fff6db4dcf97f7d5a354a9472785  PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md
2535a838ff3e3f579de349114ff69433f3a7e00cb3e033e41624901dd7693f41  PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  README.md
85e531a52b75ea3dbe5202fea719e871393606647ab28b739ad82ae842e27306  alembic.ini
10563c24868c0921987c9953ad1f3f12915aedc82bdfc5ec59ef9013b5fe55c1  alembic/env.py
b37123fcbbe9acb6a1890d253752bc7e4cebb2d787e6a0fb35387f99907eafba  alembic/script.py.mako
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  alembic/versions/.gitkeep
bb1d211f5a498400c8ff4e0a4c54da2d6e6647e2c7069fdc3775558dfdcbf997  compose.yaml
756c944897a4ec8f990ec4bae6062cedb480c2488f4913168341c309e2b38fa2  docs/adr/0001_arquitetura_api_minhavida.md
d710c7cc28685a138f615b1070976c12dd39607a2fe31af1b7b99d3035833ec8  docs/adr/0002_identificadores_uuid.md
44bb46f0c36437305c45c82d7c04a4fa0fe5320dd120c9f79d4d406f67b6364f  docs/arquitetura/analise_projeto_minhavida.md
2a2f155e92af0fcbb06400234545974b0dff334677cea3c1c734528fc4e6b70b  docs/arquitetura/arquitetura_api_minhavida.md
0d100e6d7c95aed221878152c221b8a8dcb4dc95bb7572d41c00d5824f01777e  docs/arquitetura/indice.md
e0f9c1a485106204f5d64bf3250ef0a1239b36e672fc0f015a9339d2ef6ec09c  docs/arquitetura/matriz_requisitos_api.md
5f9048f750f7bbc232a68048daad2f8622f150f398d06399fa5010a2a7a26afe  docs/arquitetura/plano_fases_api.md
92d210fbcb833b19f21f8dc51d25bb000c5be8c8e861038bd2dd6eeac6ef92e5  docs/arquitetura/plano_validacao_auditoria.md
d8fda8c0aa1da349c8b8ff625f864c58514c272048d9f391bf38650bd623f894  src/api_gestao_pessoal/__init__.py
50ab98141652b19a5ba21e690e6d6dacc74aa24b5803764e8c2541388d297def  src/api_gestao_pessoal/database.py
bb566f5402050cd6dd60bc581bf17e6925415cc256775f5210f5cfea45e263ee  src/api_gestao_pessoal/main.py
dd692b63d6c5cbbcb4386cb146ef51b9e6d3b00259256aed1a85439eb059ca37  src/api_gestao_pessoal/models/__init__.py
39cb5b83a05e05bcc13f627ca6190706303591763203fb288a17960561041ad9  src/api_gestao_pessoal/models/base.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  src/api_gestao_pessoal/models/usuario.py
b92bb3c80336d23687aa2330c9fa75707a99620acd5f0e39b1acc9897972fc37  src/api_gestao_pessoal/rastreamento.py
b58e215bbb12c600de95a10edfb92534199cf042afb39fc67c8ad38e75d06ee5  src/api_gestao_pessoal/routers/__init__.py
5fbda750f3739079ea11d5a9a2b114fa795e2db1c4aa6f34786e1d89884d4b32  src/api_gestao_pessoal/routers/saude.py
5c94fe6bbe63e2782be904b7373d7b90826b1abfd791ebdac7e9ffb1a60e8dc3  src/api_gestao_pessoal/schemas/__init__.py
df9c3382d0e5fed29a0f1347354b0cd5cb4b43e142a9944d0f85b90acf63bf5b  src/api_gestao_pessoal/schemas/erro.py
2dc25bfdb967b8bb0c88e69a2ee176de1cd5f03aefed898f429bc7ea94d91310  src/api_gestao_pessoal/schemas/saude.py
039937f6322149f5ac87b586192e68418c29a562a0e2419f90669120192dd0f0  src/api_gestao_pessoal/settings.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  tests/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  tests/apoio/__init__.py
b6f740c7ae285ab445bc7ba24bf299f7490e75b7736445c7b016b658df0b52ec  tests/apoio/banco.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  tests/infra/__init__.py
f94ccc8eabd61e6bccb820035206c26c4011415a361cf71ae7baa330e06115ef  tests/infra/conftest.py
202360144c0c35ce6015cab57d15eedd07ad96b17842d4a385cb2ca615337f75  tests/infra/test_alembic_ambiente.py
c0fd9e88367c98ec7a4f0f0fc443e3e1860ee740847595a779f7e7d4a4ed4276  tests/infra/test_erros.py
c90b30bfd099a22e008cf0fb7485fcb731d08e04cc0e1c1bf0c09068f8ddcacd  tests/infra/test_saude.py
b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d  uv.lock
```

Os dois documentos criados pela auditoria (este prompt e o relatório em `docs/auditorias/`) também são protegidos. Registre os SHA-256 deles na Etapa A e confira-os de novo no fim.

## 2. Fontes normativas e precedência

Leia, nesta ordem:

1. `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md`, integralmente. Em especial §7.1, §7.2, §7.4, §8 e os anexos B e C.
2. `CLAUDE.md`, seções 1 e 2.
3. `docs/arquitetura/indice.md`, §3 a §5.
4. `docs/arquitetura/arquitetura_api_minhavida.md`: §3.4 (logs, seção aceita), §4.4 e §11.
5. `docs/arquitetura/plano_validacao_auditoria.md`: §2, §3 e §5.
6. `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md`: §8.5, §9.5, §11 e §14.
7. Este prompt.

Precedência: instrução explícita do usuário > `CLAUDE.md` > ADRs aceitos > documentos de arquitetura aceitos > prompts.

Este prompt **substitui** dois trechos do Prompt F1:

- §8.5, handler 4: o log do 500 de banco;
- §11.1: a construção de `settings_teste`.

Os dois ajustes alinham a F1 à arquitetura §3.4 e ao plano §3. A atualização dos textos normativos é do Opus, em etapa documental separada (auditoria, anexo C). **Você não edita documentos.**

## 3. Decisões, achados e pendências

| Item | Tratamento neste prompt |
| --- | --- |
| DEC-MV-26 | **Condição de liberação.** Opção B, conforme o anexo B da auditoria |
| ACH-MV-F1-001 (P2): gate de formatação | Corrigido pela DEC-MV-26 (§7.1) |
| ACH-MV-F1-002 (P2): valores de colunas no log do 500 de banco | Corrigido em §7.2, com a regressão REG-F1-01 (§7.5) |
| ACH-MV-F1-003 (P2): `settings_teste` lê `.env` e ambiente | Corrigido em §7.3, com a regressão REG-F1-02 (§7.5) |
| ACH-MV-F1-004 (P3): alteração temporária de documento protegido | Prevenido pela ordem da §10 e pela regra 0.5 |
| ACH-MV-F1-005 (P3): `alembic/` fora do Ruff e do Pyright | **Fora deste prompt.** Será decidido antes da F2 |
| ACH-MV-F1-006 (P3): precisão do relatório | Exigências da §11 |

Não autorizado: DEC-MV-06 a 24, a F2, qualquer tabela ou migração, mudança em `alembic/`, `compose.yaml`, `.gitignore`, `.env.exemplo`, `uv.lock` ou documentos, e a aprovação da fase.

## 4. Escopo e exclusões

**Dentro:** as alterações da §7, exatamente, nos 6 arquivos da §6.1.

**Fora:**

- qualquer outra mudança de código, teste ou configuração;
- o caminho do 500 genérico (`tratar_inesperado`, que continua com traceback por causa do CT-F1-09);
- os logs dos 503;
- a lógica de `ErroNegocio`, middleware e saúde.

## 5. Política de testes

- **RED → GREEN.** As regressões novas são escritas e executadas **antes** da correção e precisam falhar pelo motivo esperado (§10, passo 2). Se alguma passar antes da correção, ela não detecta o defeito: **pare**.
- **Seleção final:** os 4 arquivos de teste afetados (§10, passo 8):
  - `test_configuracao.py`, `test_sessao_transacao.py` e `conftest.py` foram alterados;
  - `test_saude.py` e `test_erros.py` dependem de `settings_teste` e dos handlers alterados.

  `tests/infra/test_alembic_ambiente.py` **não** é executado: não depende dos arquivos alterados, e sua evidência do mesmo conteúdo está na auditoria.
- Sem `sleep` como sincronização, sem `skip` ou `xfail`. Docker indisponível é **BLOQUEIO**.
- Ao falhar: o mesmo teste → correção → o mesmo teste → a seleção. Sem reexecuções por rotina.

## 6. Arquivos

### 6.1. Permitidos (somente estas alterações)

| Arquivo | Alteração |
| --- | --- |
| `pyproject.toml` | Somente as 3 linhas da DEC-MV-26 em `[tool.ruff.format]` (§7.1) |
| `src/api_gestao_pessoal/erros.py` | `import traceback`, nova função `_descrever_erro_banco` e o log do 500 em `tratar_banco` (§7.2) |
| `tests/conftest.py` | Classe `SettingsTeste` e fixture `settings_teste` (§7.3) |
| `tests/apoio/rotas_teste.py` | Sentinelas, valor de `falha_no_commit` e nova rota `/registros/violacao-nao-nulo` (§7.4) |
| `tests/infra/test_sessao_transacao.py` | REG-F1-01 (§7.5) |
| `tests/infra/test_configuracao.py` | REG-F1-02 (§7.5) |

### 6.2. Protegidos

Todos os arquivos do bloco B (§1.2), os dois documentos da auditoria, `.env`, `docs/**`, `PROMPTS/**`, `CLAUDE.md`, `README.md`, `alembic/**`, `alembic.ini`, `compose.yaml`, `uv.lock`, `.gitignore`, `.env.exemplo` e o restante do `pyproject.toml`.

## 7. Alterações exatas

Este diff foi validado pelo Opus numa cópia externa do objeto auditado:

- Ruff (lint e formatação) e Pyright limpos, sem supressões;
- as 3 regressões falham contra o código atual e passam com a correção;
- `tests/infra` passa inteiro na cópia (29 testes).

Aplique-o exatamente. Os números de linha referem-se ao estado do bloco A.

### 7.1. DEC-MV-26 (`pyproject.toml`)

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

### 7.2. Log do 500 de banco sem valores (`erros.py`)

Contrato resultante: no 500 de `DBAPIError`, `logger.error` **sem `exc_info`**. A mensagem contém só identificadores (`sqlstate`, classe, esquema, tabela, coluna, restrição) e a pilha de chamadas sem mensagens de exceção, com `extra={"id_requisicao": …}`.

Ficam inalterados:

- o mapeamento de status;
- os 503 (`warning` com o código);
- o handler genérico, que mantém `logger.exception` (CT-F1-09).

```diff
--- a/src/api_gestao_pessoal/erros.py
+++ b/src/api_gestao_pessoal/erros.py
@@ -1,4 +1,5 @@
 import logging
+import traceback
 from collections.abc import Mapping, Sequence
 from dataclasses import dataclass
 from enum import StrEnum
@@ -192,6 +193,25 @@
     return getattr(request.state, "id_requisicao", None)
 
 
+def _descrever_erro_banco(exc: DBAPIError) -> str:
+    """Resume o erro de banco somente com identificadores.
+
+    A mensagem do driver e o `DETAIL` do PostgreSQL podem conter valores
+    de colunas (arquitetura §3.4); por isso não entram no log.
+    """
+    orig = getattr(exc, "orig", None)
+    diag = getattr(orig, "diag", None)
+    campos = {
+        "sqlstate": getattr(orig, "sqlstate", None),
+        "classe": type(orig if orig is not None else exc).__name__,
+        "esquema": getattr(diag, "schema_name", None),
+        "tabela": getattr(diag, "table_name", None),
+        "coluna": getattr(diag, "column_name", None),
+        "restricao": getattr(diag, "constraint_name", None),
+    }
+    return " ".join(f"{nome}={valor or '-'}" for nome, valor in campos.items())
+
+
 def _dados_de_banco(exc: DBAPIError) -> DadosErro:
     sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)
     if sqlstate in SQLSTATES_CONFLITO:
@@ -269,7 +289,13 @@
         dados = _dados_de_banco(exc)
         extra = {"id_requisicao": _id_requisicao(request) or "-"}
         if dados.status == HTTPStatus.INTERNAL_SERVER_ERROR:
-            logger.exception("erro de banco de dados", extra=extra)
+            # Sem exc_info: o traceback encadeado traria o DETAIL do driver.
+            logger.error(
+                "erro de banco de dados: %s\n%s",
+                _descrever_erro_banco(exc),
+                "".join(traceback.format_tb(exc.__traceback__)).rstrip(),
+                extra=extra,
+            )
         else:
             logger.warning(
                 "erro de banco de dados: %s", dados.codigo, extra=extra
```

### 7.3. Fixture `settings_teste` hermética (`tests/conftest.py`)

`SettingsTeste` usa somente os valores passados explicitamente e os padrões do contrato. Ignora variáveis de ambiente, `.env` e segredos em arquivo. Validadores e padrões de `Settings` continuam valendo.

```diff
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -1,10 +1,13 @@
 import secrets
 from collections.abc import AsyncIterator, Callable, Iterator
 from contextlib import AbstractAsyncContextManager, asynccontextmanager
+from typing import override
 
 import httpx
 import pytest
 from fastapi import FastAPI
+from pydantic import SecretStr
+from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
 from testcontainers.community.postgres import PostgresContainer
 
 from api_gestao_pessoal.settings import Settings
@@ -37,12 +40,30 @@
     return url
 
 
+class SettingsTeste(Settings):
+    """Settings herméticas: só valores explícitos e padrões do contrato.
+
+    Ignora variáveis de ambiente, `.env` e segredos em arquivo.
+    """
+
+    @classmethod
+    @override
+    def settings_customise_sources(
+        cls,
+        settings_cls: type[BaseSettings],
+        init_settings: PydanticBaseSettingsSource,
+        env_settings: PydanticBaseSettingsSource,
+        dotenv_settings: PydanticBaseSettingsSource,
+        file_secret_settings: PydanticBaseSettingsSource,
+    ) -> tuple[PydanticBaseSettingsSource, ...]:
+        return (init_settings,)
+
+
 @pytest.fixture
 def settings_teste(url_banco_teste: str) -> Settings:
-    return Settings.model_validate({
-        "DATABASE_URL": url_banco_teste,
-        "AMBIENTE": "teste",
-    })
+    return SettingsTeste(
+        DATABASE_URL=SecretStr(url_banco_teste), AMBIENTE="teste"
+    )
 
 
 @pytest.fixture
```

### 7.4. Rotas de teste (`tests/apoio/rotas_teste.py`)

As sentinelas são valores sintéticos. O CT-F1-13 continua usando `falha_no_commit`, só com outro valor em `unico`.

```diff
--- a/tests/apoio/rotas_teste.py
+++ b/tests/apoio/rotas_teste.py
@@ -13,6 +13,9 @@
 from api_gestao_pessoal.settings import Settings
 
 CHAVE_TRAVA = 4242
+# Valores sintéticos que nunca podem aparecer em logs ou respostas.
+SENTINELA_UNICO = "sentinela-unico-7f3a"
+SENTINELA_LINHA = "sentinela-linha-9c2e"
 
 router = APIRouter(prefix="/teste")
 
@@ -89,11 +92,24 @@
     for _ in range(2):
         await sessao.execute(
             INSERIR_REGISTRO,
-            {"id": uuid.uuid7(), "valor": "duplicado", "unico": "mesmo"},
+            {
+                "id": uuid.uuid7(),
+                "valor": "duplicado",
+                "unico": SENTINELA_UNICO,
+            },
         )
     await sessao.commit()
 
 
+@router.post("/registros/violacao-nao-nulo")
+async def violacao_nao_nulo(sessao: SessaoDep) -> None:
+    await sessao.execute(
+        INSERIR_REGISTRO,
+        {"id": uuid.uuid7(), "valor": None, "unico": SENTINELA_LINHA},
+    )
+    await sessao.commit()
+
+
 @router.post("/trava")
 async def trava(sessao: SessaoDep) -> dict[str, bool]:
     await sessao.execute(
```

### 7.5. Regressões

**REG-F1-01** (`test_erro_banco_500_sem_valores_no_log`, 2 casos):

- violação de UNIQUE diferida no `COMMIT` e violação de NOT NULL no `INSERT`;
- cada caso responde 500 `ERRO_INTERNO`;
- a saída formatada com o `FORMATO_LOG` real e o `caplog.text` não contêm as sentinelas nem `DETAIL`;
- a resposta não contém as sentinelas;
- controle positivo: a saída contém o `sqlstate`, o identificador esperado e o `[id_requisicao]`.

```diff
--- a/tests/infra/test_sessao_transacao.py
+++ b/tests/infra/test_sessao_transacao.py
@@ -1,3 +1,4 @@
+import logging
 from collections.abc import Callable
 from http import HTTPStatus
 
@@ -6,15 +7,22 @@
 from fastapi import FastAPI
 
 from api_gestao_pessoal.erros import CodigoErro
+from api_gestao_pessoal.rastreamento import FORMATO_LOG
 from api_gestao_pessoal.settings import Settings
 
 from ..apoio.banco import url_libpq
-from ..apoio.rotas_teste import CHAVE_TRAVA, criar_app_teste
+from ..apoio.rotas_teste import (
+    CHAVE_TRAVA,
+    SENTINELA_LINHA,
+    SENTINELA_UNICO,
+    criar_app_teste,
+)
 from ..conftest import FabricaCliente
 
 pytestmark = pytest.mark.usefixtures("limpar_registros")
 
 LOCK_TIMEOUT_CURTO_MS = 200
+ID_REGRESSAO_LOG = "regressao-log-0001"
 
 
 async def test_commit_no_router_persiste(
@@ -95,3 +103,46 @@
     assert bloqueada.json()["codigo"] == CodigoErro.CONFLITO_CONCORRENCIA
     assert bloqueada.headers["Retry-After"] == "1"
     assert liberada.status_code == HTTPStatus.OK
+
+
+@pytest.mark.parametrize(
+    ("rota", "esperados"),
+    [
+        (
+            "/teste/registros/falha-no-commit",
+            ("sqlstate=23505", "restricao=uq_registro_unico"),
+        ),
+        (
+            "/teste/registros/violacao-nao-nulo",
+            ("sqlstate=23502", "coluna=valor"),
+        ),
+    ],
+)
+async def test_erro_banco_500_sem_valores_no_log(
+    app_teste: FastAPI,
+    criar_cliente: FabricaCliente,
+    caplog: pytest.LogCaptureFixture,
+    rota: str,
+    esperados: tuple[str, str],
+) -> None:
+    with caplog.at_level(logging.ERROR, logger="api_gestao_pessoal"):
+        async with criar_cliente(app_teste) as cliente:
+            resposta = await cliente.post(
+                rota, headers={"X-Request-ID": ID_REGRESSAO_LOG}
+            )
+    assert resposta.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
+    assert resposta.json()["codigo"] == CodigoErro.ERRO_INTERNO
+    registros = [
+        r for r in caplog.records if r.name == "api_gestao_pessoal.erros"
+    ]
+    assert registros, "o erro de banco não foi registrado"
+    formatador = logging.Formatter(FORMATO_LOG)
+    saida = "\n".join(formatador.format(r) for r in registros)
+    saida += "\n" + caplog.text
+    for sentinela in (SENTINELA_UNICO, SENTINELA_LINHA):
+        assert sentinela not in saida
+        assert sentinela not in resposta.text
+    assert "DETAIL" not in saida
+    for trecho in esperados:
+        assert trecho in saida
+    assert f"[{ID_REGRESSAO_LOG}]" in saida
```

**REG-F1-02** (`test_settings_teste_ignora_ambiente_e_env`):

- monta um `.env` **sintético** em `tmp_path` e altera duas variáveis de ambiente;
- controle positivo: a classe de produção enxerga as alterações;
- a fixture `settings_teste`, obtida depois das alterações, mantém os padrões.

```diff
--- a/tests/infra/test_configuracao.py
+++ b/tests/infra/test_configuracao.py
@@ -5,7 +5,7 @@
 from pathlib import Path
 
 import pytest
-from pydantic import ValidationError
+from pydantic import SecretStr, ValidationError
 from testcontainers.community.postgres import PostgresContainer
 
 from api_gestao_pessoal.main import criar_app
@@ -27,6 +27,8 @@
     "DB_LOCK_TIMEOUT_MS",
     "DB_IDLE_IN_TRANSACTION_TIMEOUT_MS",
 )
+POOL_DO_AMBIENTE = 7
+STATEMENT_TIMEOUT_DO_ENV_MS = 123
 
 
 @pytest.fixture
@@ -116,3 +118,28 @@
             "postgresql+psycopg://u:p@outro:5432/minhavida_teste",
             container_postgres,
         )
+
+
+def test_settings_teste_ignora_ambiente_e_env(
+    request: pytest.FixtureRequest,
+    monkeypatch: pytest.MonkeyPatch,
+    tmp_path: Path,
+) -> None:
+    monkeypatch.chdir(tmp_path)
+    (tmp_path / ".env").write_text(
+        f"DB_STATEMENT_TIMEOUT_MS={STATEMENT_TIMEOUT_DO_ENV_MS}\n",
+        encoding="utf-8",
+    )
+    monkeypatch.setenv("DB_POOL_SIZE", str(POOL_DO_AMBIENTE))
+    monkeypatch.setenv("LOG_NIVEL", "DEBUG")
+    # Controle positivo: a classe de produção enxerga o ambiente alterado.
+    controle = Settings(DATABASE_URL=SecretStr(URL_VALIDA))
+    assert controle.DB_POOL_SIZE == POOL_DO_AMBIENTE
+    assert controle.LOG_NIVEL == "DEBUG"
+    assert controle.DB_STATEMENT_TIMEOUT_MS == STATEMENT_TIMEOUT_DO_ENV_MS
+    # A fixture usada pelos testes ignora ambiente e .env.
+    s: Settings = request.getfixturevalue("settings_teste")
+    assert s.DB_POOL_SIZE == 5
+    assert s.LOG_NIVEL == "INFO"
+    assert s.DB_STATEMENT_TIMEOUT_MS == 15000
+    assert s.AMBIENTE == "teste"
```

## 8. Critérios de aceite e bloqueios

**Aceite (todos):**

1. RED: os 3 nós das regressões falham antes da correção, pelos motivos da §10, passo 2.
2. GREEN: os 3 nós passam após a correção.
3. Seleção da §10, passo 8: `26 passed`, 0 skip e 0 xfail.
4. `ruff check --no-fix .`: `All checks passed!`.
5. `ruff format --check .`: rc 0, `26 files already formatted`, sem nenhum `.md` listado.
6. `pyright`: `0 errors`.
7. `alembic heads`: saída vazia.
8. `docker compose config --quiet` (valores fictícios): rc 0.
9. Bloco B: 42/42 iguais no fim. Bloco A: os 6 arquivos alterados, e nenhum outro.
10. Única supressão de Pyright continua em `settings.py:42`. Nenhuma outra supressão nova.

**Reprovação (qualquer um):**

- arquivo protegido alterado;
- `ruff format .` ou `ruff check --fix .` executado antes do passo 6;
- supressão nova;
- mudança no handler genérico ou nos 503;
- teste existente alterado além do especificado;
- leitura do `.env`;
- `task test` ou `pytest` sem seleção.

**Bloqueios (pare e relate):**

- condição de liberação ausente;
- `HEAD`, índice ou hashes divergentes (§1);
- regressão que passa antes da correção;
- arquivo protegido alterado por qualquer comando;
- Docker indisponível;
- API instalada diferente da usada na §7;
- `ruff format --check .` listando `.md` depois da DEC-MV-26.

## 9. Etapa A — leitura e plano (somente leitura)

1. `pwd`, `git status --short --branch`, `git rev-parse HEAD` e `git diff --cached --name-only`.
2. Conferência dos blocos A e B com `sha256sum -c`. Salve cada bloco num arquivo **fora do repositório** (por exemplo em `/tmp`) e passe esse arquivo ao comando.
3. Verificação da condição de liberação (cabeçalho).
4. Leitura das fontes da §2, com o registro do SHA-256 de cada uma, inclusive deste prompt e do relatório de auditoria.
5. `uv --version`, `uv run --frozen python --version` e `docker version --format '{{.Server.Version}}'`.
6. Confirmações por `rg` em `.venv`, sem executar código do projeto:
   - `settings_customise_sources` e `PydanticBaseSettingsSource` em `pydantic_settings`;
   - as propriedades `schema_name`, `table_name`, `column_name` e `constraint_name` de `psycopg.errors.Diagnostic`.

Resposta da Etapa A:

- divergências encontradas, ou “nenhuma”;
- resultado de §1 e dos dois blocos;
- fonte da aprovação da DEC-MV-26;
- SHA-256 das fontes;
- plano, citando os passos da §10;
- riscos;
- pedido explícito: **“Aguardo ‘pode implementar’ para as correções da F1.”**

## 10. Etapa B — ordem e comandos exatos

| # | Ação ou comando | Expectativa |
| --- | --- | --- |
| 0 | Repetir os passos 1 e 2 da Etapa A | Iguais à Etapa A. Divergência: **pare** |
| 1 | Aplicar §7.4 e §7.5 (rotas e regressões), sem tocar `erros.py` nem `conftest.py` | — |
| 2 | `uv run --frozen pytest "tests/infra/test_sessao_transacao.py::test_erro_banco_500_sem_valores_no_log" "tests/infra/test_configuracao.py::test_settings_teste_ignora_ambiente_e_env" -q` | **`3 failed`**: os dois casos de REG-F1-01 em `assert sentinela not in saida` e REG-F1-02 em `assert 7 == 5`. Outro resultado: **pare** |
| 3 | Aplicar §7.2 e §7.3 | — |
| 4 | O mesmo comando do passo 2 | **`3 passed`** |
| 5 | Aplicar §7.1 (DEC-MV-26) e executar `uv run --frozen ruff format --check .` | Nenhum `.md` listado. Pode listar `.py`; nesse caso siga para o passo 6. Algum `.md` listado: **pare** |
| 6 | `uv run --frozen ruff check --fix .` e depois `uv run --frozen ruff format .` | Correções apenas nos arquivos da §6.1 |
| 7 | `git status --short` e `sha256sum -c <bloco B>` | Status igual ao da §1 (os mesmos caminhos) e 42/42 OK. Qualquer protegido alterado: **pare** (regra 0.6) |
| 8 | `uv run --frozen pytest tests/infra/test_configuracao.py tests/infra/test_saude.py tests/infra/test_erros.py tests/infra/test_sessao_transacao.py -q` | `26 passed`. Registrar contagem e duração |
| 9 | `uv run --frozen ruff check --no-fix .` | `All checks passed!` |
| 10 | `uv run --frozen ruff format --check .` | `26 files already formatted`, rc 0 |
| 11 | `uv run --frozen pyright` | `0 errors` |
| 12 | `uv run --frozen alembic heads` | Saída vazia |
| 13 | `POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose config --quiet` | rc 0 |
| 14 | `sha256sum -c <bloco B>`, `sha256sum` dos 6 arquivos da §6.1, SHA-256 dos dois documentos da auditoria e `git diff --stat bd2b2e0f1e4f2674b528175e535b0931badec34a` | 42/42 OK. Somente os 6 arquivos com hash novo. Documentos da auditoria iguais aos da Etapa A |

Não execute `alembic upgrade` fora dos testes, `docker compose up` nem `docker compose down`.

## 11. Relatório com evidências

1. Bloco de revalidação (§10, passo 0) e fonte da aprovação da DEC-MV-26.
2. Cada comando **literalmente** executado, na ordem, com rc e saída resumida real. Separe “executado”, “implícito” (por exemplo, a sincronização feita por `uv run`) e “não executado”, conforme ACH-MV-F1-006.
3. RED e GREEN, com o motivo de cada falha no passo 2. Use os nomes das sentinelas, não blocos longos de traceback.
4. SHA-256 antes e depois dos 6 arquivos e conferência do bloco B.
5. Diff final dos 6 arquivos contra o bloco A.
6. Desvios: nenhum é permitido. Se houver, descreva-os com o ponto de parada.
7. Pendências e riscos observados.

Não declare a fase aprovada nem os achados encerrados. O encerramento depende da reauditoria.

## 12. Parada

Após o relatório, **pare**. O estado passa a ser `ENTREGUE_PARA_AUDITORIA`.

- Não inicie a F2.
- Não faça commit.
- Não edite documentos.

A reauditoria do Opus se concentra em ACH-MV-F1-001 a 006 e nos efeitos diretos: repete a sonda de logs com sentinelas e a sonda de `.env` sintético. Depois disso, o Opus aplica as propostas documentais aprovadas.
