# ADR-0002 — Identificadores principais em UUID versão 7

| Campo | Valor |
| --- | --- |
| ID | ADR-0002 |
| Título | Identificadores principais em UUIDv7 gerado pela aplicação |
| Estado | **ACEITO** em 2026-10-13 (DEC-MV-06, `docs/arquitetura/indice.md` §4). `CLAUDE.md` atualizado na mesma data (§7) |
| Data | 2026-10-09. Atualizado em 2026-10-13 (aceite e atualização do `CLAUDE.md`) |
| Autor | Claude Opus 5.5 |
| Fontes | `CLAUDE.md`: contrato de tabelas (linhas 764–1152) e seção “MAPEAMENTO PARA SQLALCHEMY”. Diretriz atual do usuário (“UUID para identificadores principais”). `analise_projeto_minhavida.md` REC-MV-001 |
| Substitui | Cláusulas de `CLAUDE.md` que definem `id` como `INT` com auto incremento e as FKs correspondentes como `INT`. Diff em `analise_projeto_minhavida.md` §10.1 |

## 1. Contexto e problema

Divergência entre as duas fontes:

- O contrato de tabelas define que “todos os campos `id` serão inteiros, chaves primárias e gerados automaticamente pelo banco”, com FKs inteiras.
- A diretriz atual de arquitetura do usuário pede UUID para os identificadores principais.

Nenhuma tabela existe ainda: não há migrações, volume nem banco com dados (OBSERVADO). A mudança é viável sem migração de dados.

## 2. Forças e restrições

- Preservar todo o restante do contrato: nomes, nulabilidade, CHECKs, FKs compostas, unicidades, índices e seeds.
- Não manter PK inteira com FK UUID, nem acrescentar `public_id`.
- O PostgreSQL alvo é 15 (`postgres:15-alpine`, DEC-MV-23), que tem `gen_random_uuid()` (v4), mas **não** `uuidv7()` (nativo apenas a partir do 18).
- O Python alvo é 3.14, que oferece `uuid.uuid7()` na biblioteca padrão. Verificado no `.venv`: `hasattr(uuid, "uuid7") is True`.
- Uma mudança de tipo **não autoriza** outras mudanças nas 13 tabelas.

## 3. Alternativas consideradas

| Alternativa | Avaliação |
| --- | --- |
| A. Manter `INT` com identidade (contrato literal) | Contraria a diretriz atual |
| B. UUIDv4 com `server_default=gen_random_uuid()` | Inserções aleatórias no índice B-tree (pior localidade). Funciona em Core e SQL puro |
| C. UUIDv7 nativo no banco (`uuidv7()`) | Exige PostgreSQL 18 e, portanto, troca de versão maior (contra DEC-MV-23) |
| D. **UUIDv7 gerado pela aplicação (`uuid.uuid7()`), sem `server_default`** | Ordenação aproximadamente temporal no índice e uma única fonte de geração. Sem dependência nova ou da versão do PostgreSQL. Inserções por SQL textual precisam informar o `id` |
| E. Biblioteca externa (`uuid6`/`uuid-utils`) | Desnecessária com Python 3.14 |
| F. PK inteira e `public_id` UUID | Proibido pela orientação da sessão. Duplica identidade |

## 4. Decisão recomendada

**D: UUIDv7 gerado pela aplicação.**

### 4.1. Alcance

“Identificadores principais” = a coluna `id` de **todas** as 13 tabelas, inclusive catálogos (`categoria_atividade`, `categoria_importancia` e `categoria_financeira`) e tabelas auxiliares (`recuperacao_senha`, `notificacao` e `requisicao_idempotente`). Todas as FKs que referenciam um `id` também passam a UUID.

Colunas inteiras que **não** são identificadores permanecem inalteradas:

- `INT`: `numero_ocorrencia`, `numero_referencia`, `numero_final`, `tentativas` e `versao_agendamento`;
- `SMALLINT`: `antecedencia_dias`, `lembrete_antecedencia_dias` e `codigo_resposta`.

### 4.2. Representações

| Camada | Representação |
| --- | --- |
| PostgreSQL | `uuid` |
| SQLAlchemy | `Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7)`, sem `server_default`. FKs: `Mapped[uuid.UUID]` ou `Mapped[uuid.UUID \| None]` com `Uuid(as_uuid=True)` |
| Python | `uuid.UUID` |
| Pydantic e HTTP | `uuid.UUID`, serializado como string canônica minúscula com hífens (36 caracteres). Parâmetros de caminho tipados como `uuid.UUID`. Formato inválido gera 422 `VALIDACAO` |
| Migrações | `sa.Uuid()` sem `server_default`. Os seeds geram `uuid.uuid7()` na execução da revisão |

### 4.3. Geração

- Pelo ORM e pelo Core: o `default=uuid.uuid7` é aplicado em inserções feitas por `insert()` do SQLAlchemy, inclusive em lote, sem `id` informado.
- Por SQL textual: o `id` é obrigatório. A ausência resulta em violação de `NOT NULL`. Isso é intencional: há uma única fonte de geração.
- Não gerar IDs no cliente HTTP. Os IDs são sempre do servidor.

### 4.4. Ordenação e índices

- O `id` **não** é contrato de ordem cronológica. As ordenações de negócio usam colunas explícitas (`criado_em`, datas e horários).
- O `id` aparece somente como **último desempate estável** em ordenações e cursores keyset.
- A natureza temporal do v7 apenas melhora a localidade das PKs. Nenhuma regra depende dela.

### 4.5. Catálogos e seeds

- Os IDs das 30 categorias diferem entre ambientes. O código **nunca** depende de IDs fixos: localiza categorias por chave natural (`nome`, ou `(tipo, nome)`) quando necessário.
- A API expõe os catálogos por endpoint (arquitetura §9.2).
- Os seeds são idempotentes por `INSERT … ON CONFLICT (<chave natural>) DO NOTHING`.

### 4.6. FKs compostas e unicidades

Sem mudança estrutural: os pares passam a ser `(uuid, uuid)` ou `(uuid, varchar)`.

- `UNIQUE(id, usuario_id)` nos 4 destinos.
- `UNIQUE(id, tipo)` em `categoria_financeira`.
- `UNIQUE(serie_id, numero_ocorrencia)`.
- `UNIQUE(importancia_id)`.
- `UNIQUE(lembrete_id, versao_agendamento)`.
- `UNIQUE(usuario_id, acao, chave)`.

## 5. Caminhos de adoção

| Situação | Caminho |
| --- | --- |
| Banco novo (único caso **OBSERVADO**) | A migração inicial da F2 cria as tabelas já com `uuid` |
| Base existente com dados | **Não se aplica** (não há banco nem migração). Se vier a existir antes da F2, a mudança exigirá um ADR próprio: coluna nova, preenchimento, reconstrução das FKs e troca de PK em janela controlada. Não reescrever migração aplicada |

## 6. Diff do contrato físico (32 colunas)

| Tabela | Coluna | Antes | Depois |
| --- | --- | --- | --- |
| `usuario` | `id` | INT PK auto incremento | UUID PK (v7, aplicação) |
| `recuperacao_senha` | `id` | INT PK | UUID PK |
| `recuperacao_senha` | `usuario_id` | INT FK → usuario | UUID FK → usuario |
| `categoria_atividade` | `id` | INT PK | UUID PK |
| `serie_atividade` | `id` | INT PK | UUID PK |
| `serie_atividade` | `usuario_id` | INT FK | UUID FK |
| `serie_atividade` | `categoria_id` | INT FK | UUID FK |
| `atividade` | `id` | INT PK | UUID PK |
| `atividade` | `usuario_id` | INT FK | UUID FK |
| `atividade` | `categoria_id` | INT FK | UUID FK |
| `atividade` | `serie_id` | INT FK (composta com usuario_id) | UUID FK (composta) |
| `categoria_importancia` | `id` | INT PK | UUID PK |
| `serie_importancia` | `id` | INT PK | UUID PK |
| `serie_importancia` | `usuario_id` | INT FK | UUID FK |
| `serie_importancia` | `categoria_id` | INT FK | UUID FK |
| `importancia` | `id` | INT PK | UUID PK |
| `importancia` | `usuario_id` | INT FK | UUID FK |
| `importancia` | `categoria_id` | INT FK | UUID FK |
| `importancia` | `serie_id` | INT FK (composta) | UUID FK (composta) |
| `categoria_financeira` | `id` | INT PK | UUID PK |
| `movimentacao_financeira` | `id` | INT PK | UUID PK |
| `movimentacao_financeira` | `usuario_id` | INT FK | UUID FK |
| `movimentacao_financeira` | `categoria_id` | INT FK (composta com tipo) | UUID FK (composta) |
| `movimentacao_financeira` | `importancia_id` | INT FK (composta com usuario_id) | UUID FK (composta) |
| `lembrete_importancia` | `id` | INT PK | UUID PK |
| `lembrete_importancia` | `usuario_id` | INT FK | UUID FK |
| `lembrete_importancia` | `importancia_id` | INT FK (composta) | UUID FK (composta) |
| `notificacao` | `id` | INT PK | UUID PK |
| `notificacao` | `usuario_id` | INT FK | UUID FK |
| `notificacao` | `lembrete_id` | INT FK (composta) | UUID FK (composta) |
| `requisicao_idempotente` | `id` | INT PK | UUID PK |
| `requisicao_idempotente` | `usuario_id` | INT FK | UUID FK |

Contagem: 13 PKs + 19 FKs = 32 colunas. As **134 colunas permanecem** (nenhuma coluna é criada ou removida).

## 7. Atualização da referência normativa

1. Com a aprovação (DEC-MV-06), o usuário aplica o diff de `analise_projeto_minhavida.md` §10.1 ao `CLAUDE.md`, ou autoriza explicitamente o Opus a aplicá-lo. **Feito em 2026-10-13:** o Opus aplicou o diff com autorização expressa do usuário (`indice.md` §4, M10): 13 PKs e 19 FKs como UUID, linha de mapeamento e SGBD PostgreSQL.
2. Este ADR passa a ACEITO e o índice (`docs/arquitetura/indice.md`) registra a aprovação. **Feito em 2026-10-13.**
3. **Gate de entrada da F2:** `CLAUDE.md` já atualizado. Assim não há duas fontes contraditórias vigentes durante a implementação. **Cumprido em 2026-10-13.**
4. O prompt anterior de banco (INT) permanece SUSPENSO e não é usado.

## 8. Consequências

- **Positivas:**
  - Identificadores não sequenciais (não revelam volume).
  - Geração sem ida ao banco: os IDs ficam conhecidos antes do `flush`, o que facilita montar respostas e chaves de idempotência.
  - Tipo uniforme.
- **Custos e riscos:**
  - 16 bytes por chave, contra 4 do INT. Impacto desprezível no volume previsto.
  - Inserções por SQL textual precisam do `id`.
  - IDs de catálogo diferem entre ambientes.
  - Exige Python ≥ 3.14 (`requires-python` ajustado na F1).
- **Reversibilidade:** fácil antes da F2. Cara depois de haver dados.

## 9. Critérios de verificação (F2)

- Introspecção: as 32 colunas com tipo `uuid` e as 13 PKs sem `column_default` (CT-F2-03).
- Inserção pelo ORM gera `uuid.UUID` com `version == 7` (CT-F2-04).
- Inserção por SQL textual sem `id` é rejeitada com SQLSTATE `23502` (CT-F2-05).
- Segundo `alembic upgrade head` e reexecução da lógica de seed sem duplicar as 30 categorias (CT-F2-07).
- Na F3+: parâmetro de caminho com UUID malformado → 422. UUID válido de outro usuário → 404 (CT-F3-30).

## 10. Aprovação

**ACEITO em 2026-10-13** pelo usuário (DEC-MV-06), incluindo a reconciliação das 13 chaves primárias e das 19 chaves estrangeiras. Registro em `docs/arquitetura/indice.md` §4. A implementação é da F2 e depende do “pode implementar” do usuário após a Etapa A.
