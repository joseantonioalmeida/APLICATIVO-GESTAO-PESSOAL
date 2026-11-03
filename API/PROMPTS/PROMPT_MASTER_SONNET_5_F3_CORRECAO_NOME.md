# Prompt Master — Sonnet 5 — F3: correção dirigida do ACH-MV-F3-002 (nome com separadores Unicode)

| Campo | Valor |
| --- | --- |
| Fase | F3 — Identidade e acesso, correção pós-auditoria |
| Estado | **`PRONTO_PARA_ETAPA_A`** (2026-10-13). Autoriza somente a Etapa A (§5) |
| Autor | Claude Opus 5.5 |
| Destinatário | Claude Sonnet 5 (implementação) |
| Modo | LOCAL (WSL do usuário) |
| Origem | `docs/auditorias/AUDITORIA_F3_IDENTIDADE_ACESSO.md` (SHA-256 `223c1eb97a7a741226154842bf38f654c77c60965bf08a409a80bab82354885c`), veredito histórico `APROVADO_COM_P3`, achado ACH-MV-F3-002 |
| Decisão do usuário | Mensagem de 2026-10-13 que reconhece o veredito e aprova ampliar a validação do nome para recusar também as categorias Unicode `Zl` e `Zp`, além de `Cc`, mantendo o código `NOME_COMPLETO_INVALIDO` e as demais regras. O registro no `indice.md` §4 ocorre no fechamento documental |
| Evidências | `$HOME/minhavida_evidencias/f3_correcao_002/` |

---

## 0. Regras absolutas

1. **Etapa A** (§5): somente leitura. Não crie, altere nem formate arquivos do repositório, não instale nada e não execute testes. Termine pedindo “pode implementar”.
2. **Etapa B** (§6): só depois do “pode implementar” do usuário. Execute os passos na ordem, com os comandos exatamente como escritos.
3. **Todo comando de shell**, inclusive de diagnóstico ou leitura (`git`, `sha256sum`, `rg`, `grep`, `diff`, `python`), grava a saída completa e o código de saída num log próprio em `$EV`: `comando > "$EV/NN_nome.log" 2>&1; echo "codigo_saida=$?" >> "$EV/NN_nome.log"`. Não use `| tee`, `| grep` nem pipeline que esconda o código do comando principal. Uma reexecução recebe sufixo `_2`, `_3`; nunca sobrescreva um log. Comando sem log é desvio. Esta regra existe por causa do ACH-MV-F3-003.
4. Arquivos alteráveis: **somente** os dois de §3. Qualquer outro arquivo do repositório, inclusive documentos, é protegido.
5. Proibidos:
   - `git add`, `commit`, `push`, `merge`, `reset`, `restore`, `stash`, `checkout -- <arquivo>` e `clean`;
   - `uv add`, `uv sync` e `uv lock`;
   - `ruff check --fix` e `ruff format` com escrita;
   - `# noqa`, `# type: ignore` ou `# pyright: ignore` novos;
   - mudanças em `pyproject.toml`, `uv.lock`, migrações, modelos ou configuração;
   - suíte completa, `task` e Docker Compose;
   - Alembic pela CLI, salvo `alembic heads`.
6. Nunca leia, copie, imprima, edite ou calcule hash do `.env` real. Não conecte a banco real e não consulte contas existentes: a investigação de cadastros antigos está fora do escopo (§2.3).
7. O conteúdo de §4 é **exato** e já passou em `ruff check`, `ruff format --check`, Pyright e nos testes, numa cópia externa do objeto. Copie-o sem alteração. Se algum gate falhar, **pare** e relate; não ajuste nada por conta própria.
8. Não se declare aprovado. Ao final, pare para a reauditoria dirigida do Opus (§8).

---

## 1. Estado de partida

| Item | Valor |
| --- | --- |
| HEAD | `91be324c88c5a3f99a49b1b1700963e32ef257e9` (modo A, F3 sem commit) |
| Índice do Git | Vazio |
| Manifesto do objeto aprovado | `$HOME/minhavida_evidencias/f3_correcao_002_prep_emkGcHMV/MANIFESTO_OBJETO_APROVADO.sha256`, SHA-256 `ff505d0aa321547d91761789c60c7d05ca1d77cb44c6aac9d598a9b8437b66c8`, 108 arquivos (`git ls-files -co --exclude-standard`, sem `.env`) |
| `git status --porcelain --untracked-files=all` | 47 linhas do objeto aprovado, mais a linha deste prompt (`?? PROMPTS/PROMPT_MASTER_SONNET_5_F3_CORRECAO_NOME.md`), que fica fora do manifesto. Total: 48 |
| `src/api_gestao_pessoal/schemas/autenticacao.py` | Antes: `cf1d6b77b50e05936ef6ad00b459e59c5c2e2b44043cdecc405c3ca6327ce216` → depois: `57ca591c2ef9ca45489798a45dbcbf6a4e5bed851fc1215bc8958420bb220208` |
| `tests/identidade/test_registro.py` | Antes: `e3955f9217d01b768016c3e4e3c87e669369278cd864366333c480a1e052b088` → depois: `49d85548dd987669c81f7ebe90a80450eed8e12a3c96119f9dd32e2f35ea8684` |
| Documento restaurado (ACH-MV-F3-001) | `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md`, `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695` (no manifesto). Achado encerrado pelo Opus depois desta conferência |

O hash deste prompt vem na mensagem do usuário; este arquivo não contém o próprio hash.

---

## 2. Contrato alterado e alcance

### 2.1. Regra nova (aprovada pelo usuário)

`nome_completo`, no cadastro: depois de aparar as extremidades, a presença de **qualquer** caractere das categorias Unicode `Cc` (controle), `Zl` (separador de linha, U+2028) ou `Zp` (separador de parágrafo, U+2029) → 422 `VALIDACAO`, com campo `nome_completo`, código `NOME_COMPLETO_INVALIDO` e a mensagem atual, inalterada: “O nome não pode conter caracteres de controle”.

**Sem outras mudanças:**
- ausente ou vazio continua `NOME_COMPLETO_OBRIGATORIO`;
- mais de 150 caracteres continua `TAMANHO_MAXIMO`;
- a ordem das verificações não muda;
- espaços comuns, espaço rígido (U+00A0, categoria `Zs`), acentos, apóstrofo e hífen continuam aceitos.

### 2.2. Comportamento esperado

| Entrada de `nome_completo` | Resposta | Banco |
| --- | --- | --- |
| `"Ana Silva"` | 422; `campos` com `nome_completo` / `NOME_COMPLETO_INVALIDO`; sem eco da entrada | Nenhum usuário criado |
| `"Ana Silva"` | Idem | Nenhum usuário criado |
| `"Pessoa\r\nTeste"` (caso existente) | Idem, sem mudança | Nenhum usuário criado |
| `"Ana Maria D'Ávila-Souza"` | 201 | Um usuário |
| `"Ana Souza"` | 201 | Um usuário |

### 2.3. Limite da correção

A validação **impede novos cadastros** com esses caracteres. Ela **não corrige** contas já gravadas, se existirem. A F3 ainda não foi integrada, e não há perfil editável (DEC-MV-13). Não investigue nem altere bancos reais. Um eventual tratamento de dados existentes exige decisão própria do usuário.

---

## 3. Arquivos

| Arquivo | Alteração permitida, e nada além |
| --- | --- |
| `src/api_gestao_pessoal/schemas/autenticacao.py` | Os dois trechos de §4.1 |
| `tests/identidade/test_registro.py` | O trecho de §4.2 (quatro casos novos em `CASOS_INVALIDOS`, usados pelo CT-F3-02) |

Precisar de qualquer outro arquivo é **bloqueio**: pare e relate.

---

## 4. Conteúdo exato

### 4.1. `src/api_gestao_pessoal/schemas/autenticacao.py`

Trecho 1: substituir a linha

```python
PADRAO_CODIGO = re.compile(r"[0-9]{8}")
```

por:

```python
PADRAO_CODIGO = re.compile(r"[0-9]{8}")
# Controle (Cc) e separadores de linha (Zl) e de parágrafo (Zp).
CATEGORIAS_PROIBIDAS_NOME = frozenset({"Cc", "Zl", "Zp"})
```

Trecho 2: em `_nome_completo`, substituir a linha

```python
    if any(unicodedata.category(c) == "Cc" for c in nome):
```

por:

```python
    if any(unicodedata.category(c) in CATEGORIAS_PROIBIDAS_NOME for c in nome):
```

### 4.2. `tests/identidade/test_registro.py`

Em `CASOS_INVALIDOS`, logo depois do caso `id="nome_com_controle"` (o bloco que termina com `        id="nome_com_controle",` e `    ),`), inserir exatamente:

```python
    pytest.param(
        Caso(
            {"nome_completo": "Ana Silva"},
            "nome_completo",
            "NOME_COMPLETO_INVALIDO",
        ),
        id="nome_com_separador_de_linha",
    ),
    pytest.param(
        Caso(
            {"nome_completo": "Ana Silva"},
            "nome_completo",
            "NOME_COMPLETO_INVALIDO",
        ),
        id="nome_com_separador_de_paragrafo",
    ),
    pytest.param(
        Caso({"nome_completo": "Ana Maria D'Ávila-Souza"}, None, None),
        id="nome_valido_com_acentos",
    ),
    pytest.param(
        Caso({"nome_completo": "Ana Souza"}, None, None),
        id="nome_valido_com_espaco_rigido",
    ),
```

As sequências ` `, ` ` e ` ` ficam **escritas como escape** no arquivo-fonte, não como caracteres literais. A função `test_validacoes_do_registro` não muda. Ela já confere:
- 422 `VALIDACAO`, campo e código exatos;
- ausência de eco dos valores com 7 ou mais caracteres;
- `contar_usuarios == 0` nos inválidos;
- 201 e `contar_usuarios == 1` nos válidos.

Depois das duas edições, os arquivos têm os SHA-256 “depois” de §1. Hash diferente é desvio: pare e relate.

Validação prévia do Opus, numa cópia externa (`f3_correcao_002_prep_emkGcHMV/`):
- com a correção: Ruff limpo, 76 arquivos formatados, Pyright com 0 erros e `test_registro.py` com 31 aprovados;
- só com os testes novos e sem a correção: os dois casos de separador **falham**, prova de que o teste distingue o defeito.

---

## 5. Etapa A — somente leitura, relatório e parada

```bash
EV="$HOME/minhavida_evidencias/f3_correcao_002"; mkdir -p "$EV"
git rev-parse HEAD > "$EV/a01_head.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a01_head.log"
git status --porcelain --untracked-files=all > "$EV/a02_status.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a02_status.log"
git diff --cached --name-only > "$EV/a03_indice.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a03_indice.log"
sha256sum "$HOME/minhavida_evidencias/f3_correcao_002_prep_emkGcHMV/MANIFESTO_OBJETO_APROVADO.sha256" PROMPTS/PROMPT_MASTER_SONNET_5_F3_CORRECAO_NOME.md docs/auditorias/AUDITORIA_F3_IDENTIDADE_ACESSO.md > "$EV/a04_hashes_fontes.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a04_hashes_fontes.log"
sha256sum -c "$HOME/minhavida_evidencias/f3_correcao_002_prep_emkGcHMV/MANIFESTO_OBJETO_APROVADO.sha256" > "$EV/a05_manifesto.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a05_manifesto.log"
grep -F -c 'PADRAO_CODIGO = re.compile(r"[0-9]{8}")' src/api_gestao_pessoal/schemas/autenticacao.py > "$EV/a06_trecho1.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a06_trecho1.log"
grep -F -c 'if any(unicodedata.category(c) == "Cc" for c in nome):' src/api_gestao_pessoal/schemas/autenticacao.py > "$EV/a07_trecho2.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a07_trecho2.log"
grep -F -c 'id="nome_com_controle",' tests/identidade/test_registro.py > "$EV/a08_ancora_teste.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a08_ancora_teste.log"
uv run --frozen --no-sync pytest "tests/identidade/test_registro.py::test_validacoes_do_registro" --collect-only -q --color=no -p no:cacheprovider > "$EV/a09_coleta.log" 2>&1; echo "codigo_saida=$?" >> "$EV/a09_coleta.log"
```

Esperado:
- `a01`: o HEAD de §1.
- `a02`: 48 linhas de status, além da linha `codigo_saida`.
- `a03`: vazio.
- `a04`: hashes do manifesto, deste prompt (o da mensagem) e da auditoria iguais aos informados.
- `a05`: 108 `OK`, nenhum `FAILED`, `codigo_saida=0`.
- `a06`, `a07` e `a08`: `1`.
- `a09`: 21 itens coletados (a coleta não executa testes).

Leia também:
- a auditoria: §1, §7.5 e §10 (ACH-MV-F3-002);
- este prompt;
- `_nome_completo` em `schemas/autenticacao.py`;
- `CASOS_INVALIDOS` e `test_validacoes_do_registro` em `test_registro.py`.

Grave `$EV/RELATORIO_ETAPA_A.md` com os resultados, as divergências (ou “nenhuma”), os riscos e o pedido explícito: **“Aguardo ‘pode implementar’ para a correção do ACH-MV-F3-002.”** Não implemente antes da resposta do usuário.

---

## 6. Etapa B — implementação e validação

```bash
EV="$HOME/minhavida_evidencias/f3_correcao_002"

# 0. Revalidação: repita a01 a a05 com prefixo b00_ (b00_head, b00_status, b00_indice, b00_hashes_fontes, b00_manifesto). Tudo igual à Etapa A.

# 1. Edições de §4, pelo editor, sem shell. Se usar algum comando para editar, ele também recebe log próprio (regra 3).

# 2. Conferência das edições.
sha256sum src/api_gestao_pessoal/schemas/autenticacao.py tests/identidade/test_registro.py > "$EV/b02_hashes_editados.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b02_hashes_editados.log"
git diff -- src/api_gestao_pessoal/schemas/autenticacao.py tests/identidade/test_registro.py > "$EV/b03_diff.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b03_diff.log"
sha256sum -c "$HOME/minhavida_evidencias/f3_correcao_002_prep_emkGcHMV/MANIFESTO_OBJETO_APROVADO.sha256" > "$EV/b04_manifesto_depois.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b04_manifesto_depois.log"

# 3. Teste direcionado do CT-F3-02.
uv run --frozen --no-sync pytest "tests/identidade/test_registro.py::test_validacoes_do_registro" -vv --color=no -p no:cacheprovider > "$EV/b05_pytest_ct_f3_02.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b05_pytest_ct_f3_02.log"

# 4. Seleção da fase (o cadastro é usado por todos os fluxos de identidade).
uv run --frozen --no-sync pytest tests/identidade -vv --color=no -p no:cacheprovider > "$EV/b06_pytest_identidade.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b06_pytest_identidade.log"

# 5. Gates, sem escrita.
uv run --frozen --no-sync ruff check --no-fix --no-cache . > "$EV/b07_ruff_check.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b07_ruff_check.log"
uv run --frozen --no-sync ruff format --check --no-cache . > "$EV/b08_ruff_format_check.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b08_ruff_format_check.log"
uv run --frozen --no-sync pyright > "$EV/b09_pyright.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b09_pyright.log"
uv run --frozen --no-sync alembic heads > "$EV/b10_alembic_heads.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b10_alembic_heads.log"

# 6. Estado final.
git status --porcelain --untracked-files=all > "$EV/b11_status.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b11_status.log"
git diff --cached --name-only > "$EV/b12_indice.log" 2>&1; echo "codigo_saida=$?" >> "$EV/b12_indice.log"
sha256sum "$EV"/*.log > "$EV/b13_sha256_logs.txt" 2>&1; echo "codigo_saida=$?" >> "$EV/b13_sha256_logs.txt"
```

Resultados esperados:

| Log | Esperado |
| --- | --- |
| `b02` | Os dois hashes “depois” de §1 |
| `b03` | Só os trechos de §4 (+2 linhas e 1 linha trocada no schema; +24 linhas no teste) |
| `b04` | Exatamente 2 `FAILED` (os dois arquivos de §3) e 106 `OK`; `codigo_saida=1` por causa dessas duas falhas esperadas |
| `b05` | `25 passed` (21 anteriores + 4 novos), sem skip nem xfail |
| `b06` | `114 passed` (110 + 4), sem skip nem xfail |
| `b07` a `b10` | `All checks passed!`; `76 files already formatted`; `0 errors, 0 warnings, 0 informations`; `0001 (head)` |
| `b11` | 48 linhas de status (além de `codigo_saida`), as mesmas da Etapa A: os dois arquivos de §3 já constavam como não rastreados |
| `b12` | Vazio |

Qualquer falha:
1. Preserve o log.
2. Pare.
3. Relate. Não repita baterias e não altere arquivos fora de §3.

---

## 7. Relatório

Grave `$EV/RELATORIO_ETAPA_B.md` e responda com um resumo e o caminho. Conteúdo:

1. Para cada passo de §6: comando literal, `codigo_saida`, linhas finais sem edição e log.
2. Os hashes de `b02` e o diff de `b03`.
3. Tabela de node IDs dos quatro casos novos com o resultado.
4. Confirmação de que todo comando executado tem log, inclusive os diagnósticos, ou a lista de qualquer exceção.
5. Desvios (nenhum é permitido) e riscos.

Estado ao final: `ENTREGUE_PARA_REAUDITORIA`. Não declare aprovação, não faça operações de escrita no Git e não inicie a F4.

---

## 8. Critérios da reauditoria dirigida (Opus)

1. Manifesto do objeto aprovado: 106 arquivos iguais e só os dois de §3 diferentes, com os hashes “depois” de §1.
2. Diff idêntico a §4; nenhuma supressão nova; nenhuma mudança em dependências, configuração, modelos ou migrações.
3. Logs da Etapa B íntegros (`b13`), com todo comando registrado (regra 3).
4. Reprodução independente:
   - os quatro node IDs novos e o CT-F3-02 completo (25);
   - `tests/identidade` com 114 aprovados;
   - Ruff, formatação, Pyright e `alembic heads`.
5. Sonda `18_sonda_nome_separador` da auditoria repetida numa cópia do objeto corrigido: o cadastro com U+2028 ou U+2029 passa a 422, e um nome válido continua enviando o código no SMTP simulado.
6. Com os critérios atendidos, o ACH-MV-F3-002 é encerrado na reauditoria, sem reescrever a auditoria original. Depois vem o fechamento documental (reconciliações da E1 e desta correção) e, então, o commit do usuário.
