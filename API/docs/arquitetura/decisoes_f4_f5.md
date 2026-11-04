# Decisões e desvios das fases F4 e F5

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/decisoes_f4_f5.md` (novo; não altera arquivos protegidos) |
| Data | 2026-11-04 |
| Autor | Claude Sonnet 5.5, por instrução expressa do usuário de decidir de forma independente, a partir de `docs/` e `PROMPTS/` |
| Escopo | F4 (núcleo transacional) e F5 (atividades e recorrência) |

## 1. Decisões tomadas

As propostas já descritas em `arquitetura_api_minhavida.md` e no ADR-0001 foram adotadas **como estão**, por serem coerentes entre si e com os requisitos do `CLAUDE.md`.

| Decisão | Resolução |
| --- | --- |
| **DEC-MV-14** (concorrência, D-05) | Aceita integralmente: trava consultiva por usuário (`pg_advisory_xact_lock`, modos EXCLUSIVA e COMPARTILHADA, sem promoção), `READ COMMITTED`, `lock_timeout`/`statement_timeout` já existentes da F1 |
| **DEC-MV-15** (idempotência, D-06) | Aceita como em §4.3 e §8.4: `Idempotency-Key` obrigatória nos cadastros, hash do conteúdo normalizado, replay com `Idempotency-Replayed`, 422 `CHAVE_IDEMPOTENCIA_REUTILIZADA` |
| **DEC-MV-16** (recorrência, D-10) | Aceita como em §8.5: série guarda a regra, ocorrências materializadas sob demanda, lápides para exclusões, edição e exclusão por alcance |
| **DEC-MV-24** (importações entre services, REC-MV-029) | Vale a matriz da arquitetura §2.2 (mais permissiva). Na F5 não é necessária nenhuma importação entre services de domínio: `atividades` importa apenas serviços de suporte (`autorizacao`, `paginacao`, `recorrencia`, `trava`), o que também satisfaz o D-02 do ADR |

## 2. Desvios deliberados em relação ao texto da arquitetura

1. **Limpeza do registro da trava (`services/trava.py`).** O pseudocódigo manda limpar `sessao.info` em `after_commit`, `after_rollback` e `after_soft_rollback`. Verificado na prática: no SQLAlchemy 2, `after_rollback` também dispara no rollback de um SAVEPOINT, o que apagaria o registro enquanto a trava (transacional) continua ativa. Foi usado `after_transaction_end` limitado à transação **externa** (`parent is None`), que cobre commit, rollback e fechamento. Há teste (`test_rollback_de_savepoint_mantem_a_trava`).
2. **Sobreposição de horários só quando a agenda muda.** Na edição, o aviso 409 `SOBREPOSICAO_HORARIO` só é avaliado se `data`, `horario_inicial` ou `horario_final` forem enviados. Assim, renomear uma atividade que já foi salva com sobreposição confirmada não volta a exigir confirmação.
3. **Intervalo de datas aceito: 2000-01-01 a 2100-12-31** (`DATA_INVALIDA` fora dele). Protege o cálculo de recorrência contra `OverflowError`. Decisão nova, não prevista no contrato.
4. **Validações que dependem de outro campo ficam no service**, com o caminho completo do campo (`repeticao.data_final`), porque o Pydantic perde o caminho em validadores de modelo. O comportamento e os códigos seguem a §4.5.
5. **Conversão avulsa → série** só é aceita com `SOMENTE_ESTA` (o padrão), como no passo 3 de §8.5.7; `ESTA_E_PROXIMAS` em avulsa continua `ALCANCE_INVALIDO`.

## 3. Ambiente de testes

- O ambiente da sessão não tem daemon do Docker. Foi acrescentado um modo opcional: com `TESTE_POSTGRES_URL` apontando para um PostgreSQL descartável chamado `minhavida_teste`, os testes o usam em vez do Testcontainers (`tests/conftest.py`, `tests/apoio/banco.py::ContainerLocal`). Sem a variável, o comportamento original (Testcontainers) é mantido.
- Os testes desta sessão foram executados em PostgreSQL 16 (o contêiner oficial usa a 15). Nenhuma construção específica da 16 é usada.

## 4. Resultado

Suíte completa: ver o relatório final da sessão (testes, Ruff e Pyright).
