# Decisões e desvios das fases F6, F7 e F8 (e fechamento da F3)

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/decisoes_f6_f8.md` (novo) |
| Data | 2026-11-04 |
| Autor | Claude Sonnet 5.5, por instrução expressa do usuário de decidir de forma independente |
| Escopo | Fechamento da F3; F6 (financeiro), F7 (importâncias) e F8 (vínculo despesa-importância) |

## 1. Fechamento da F3

| Achado | Resolução |
| --- | --- |
| ACH-MV-F3-001 (arquivo de conferência ausente) | Verificado: o arquivo existe e o SHA-256 (`46c49e0d…`) confere. Encerrado |
| ACH-MV-F3-002 (nome com `Zl`/`Zp`) | Corrigido: o cadastro recusa as categorias Unicode `Cc`, `Zl` e `Zp` (`NOME_COMPLETO_INVALIDO`); dois casos novos em `test_registro.py` |
| ACH-MV-F3-003 (comandos sem log) | Só processo; sem ação |
| G6 da F3 | O código da F3 entrou no commit `c8a937a` (reorganização do monorepo) |

## 2. Decisões aprovadas

| Decisão | Resolução |
| --- | --- |
| **DEC-MV-17** (dinheiro como string) | Aprovada como em §4.1/§8.8: entrada `^\d{1,10}(\.\d{1,2})?$`, saída sempre com 2 casas, número JSON rejeitado, variação percentual com 1 casa e `ROUND_HALF_UP`. Limite de R$ 9.999.999.999,99 |
| **DEC-MV-18** (horizonte de séries) | Aprovada: até o último dia do 12º mês após o mês de hoje, só em Todos e Próximos; avulsas sem horizonte. As contagens dos grupos respeitam o horizonte |
| **DEC-MV-19** (`DESATIVADO`) | **Aprovada** (opção com migração): migração `0002` troca o CHECK de `lembrete_importancia.situacao`. Reversível (o `downgrade` converte `DESATIVADO` em `CANCELADO`). Escolhida por distinguir corretamente "desligado pelo usuário" de "cancelado por conclusão" |
| DEC-MV-20 (processador) | Fora do escopo; permanece para a F9 |

## 3. Desvios e escolhas de implementação

1. **`services/consulta_movimentacoes.py` (novo, de suporte).** Concentra a consulta e a conversão de movimentações, para que `financeiro`, `resumo_financeiro` e `pagamentos` as reutilizem sem importar uns aos outros (matriz da §2.2).
2. **Ordenação sem `24:00`.** O horário nulo vai depois dos demais com a chave `(horario IS NULL, COALESCE(horario, 00:00))` em vez de `COALESCE(horario, '24:00')`. O resultado é o mesmo e evita ligar parâmetros de `time` fora do intervalo do Python.
3. **Vínculo via PATCH.** `confirmar_alteracao_vinculo` só é exigida quando há vínculo atual a trocar ou remover; vincular uma despesa ainda sem vínculo não exige confirmação (nada é perdido).
4. **Elegibilidade de importâncias para pagamento** considera as ocorrências já materializadas. Ocorrências futuras de séries ainda não consultadas aparecem depois que a tela de Importâncias as materializa.
5. **`valor_previsto` com `possui_despesa=false`** é recusado (`VALOR_PREVISTO_NAO_PERMITIDO`) em vez de ignorado, como pede o contrato ("proibido caso contrário").
6. **Lembrete no passado na edição.** Ao ativar ou alterar o lembrete de uma importância pendente cuja data/hora resultante já passou, a edição é recusada (`LEMBRETE_NO_PASSADO`), como no cadastro. Nas demais ocorrências de uma série o lembrete fica `CANCELADO`.
7. **Exclusão idempotente.** `DELETE` de movimentação ou importância já excluída devolve 204.
8. **Ocorrências de série e lembretes.** O lembrete de cada ocorrência é criado na materialização (`PENDENTE` se futuro; `CANCELADO` se já passou). O processador (F9) ainda não existe: nenhuma notificação é gerada nesta etapa.

## 4. Resultado

Suíte completa em PostgreSQL 16: 363 testes, Ruff e Pyright limpos. Smoke test com o servidor real (registro, login, importância com despesa, pagamento vinculado e resumo mensal) funcionando.
