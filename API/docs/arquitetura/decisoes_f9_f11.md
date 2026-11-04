# Decisões e desvios das fases F9, F10 e F11 e da integração com o aplicativo

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/decisoes_f9_f11.md` (novo) |
| Data | 2026-11-04 |
| Autor | Claude Sonnet 5.5, por instrução expressa do usuário de decidir de forma independente |
| Escopo | F9 (lembretes e notificações), F10 (painel), F11 (consolidação) e ligação do app Flutter à API |

## 1. Decisões aprovadas

| Decisão | Resolução |
| --- | --- |
| **DEC-MV-20** (processador) | **Aprovada** como em §8.6.3: processo separado (`python -m api_gestao_pessoal.jobs.processar_lembretes [--uma-vez]`), materialização antecipada de `LEMBRETES_JANELA_DIAS` (8) dias para séries com lembrete, `SKIP LOCKED`, uma transação por série e por lembrete. **Regra de atraso:** lembrete vencido cujo compromisso ainda não passou é notificado (texto "amanhã", "hoje"…); se a data do compromisso já passou, a versão vira `CANCELADO` sem notificação |
| **DEC-MV-21** (limitação de login) | **Não implementada na aplicação** (um limitador em memória daria falsa garantia entre processos). Fica como **requisito de borda para produção**: ver `docs/operacao/operacao.md` §6. Risco aceito apenas em desenvolvimento |
| Plataforma de deploy | **Não escolhida** (não há como decidir sem conhecer a infraestrutura do usuário). O guia de operação descreve o necessário de forma independente de plataforma |

## 2. F9 — lembretes e notificações

1. O `services/processamento_lembretes.py` é dono das próprias transações (exceção documentada à regra "o router faz commit"), porque roda fora de uma requisição.
2. A revalidação ocorre **depois** da trava de linha do lembrete (`FOR UPDATE SKIP LOCKED`); o `UPDATE … WHERE situacao='PENDENTE' AND versao_agendamento = :v` garante que uma versão substituída ou cancelada nunca gere notificação. A inserção da notificação usa `ON CONFLICT DO NOTHING` em `(lembrete_id, versao_agendamento)`.
3. O processador não trava a importância: lê o estado sem trava e só toca na linha do lembrete.
4. Título e mensagem ficam congelados no envio: `Lembrete: {nome}` e `{nome} — {prazo} ({DD/MM/AAAA}[ às HH:MM]).[ Valor previsto: R$ 1.234,56.]`.
5. Falha em um item não impede os demais: o item falho é registrado no log, entra numa lista de ignorados do ciclo e permanece `PENDENTE`.
6. `GET /notificacoes`, `GET /notificacoes/nao-lidas` e `POST /notificacoes/{id}/leitura` (idempotente; ler não conclui nem paga). `importancia.disponivel` é falso quando a importância foi excluída; o texto da notificação continua legível.

## 3. F10 — painel

1. `services/painel.py` apenas compõe: financeiro usa `totais_periodo`, `comparacoes` e `ultimas_movimentacoes` (as mesmas funções do resumo mensal); atividades usa `resumo_do_dia` e `pendencias_anteriores`; importâncias usa as mesmas expressões de grupo, ordenação e item da lista (`resumo_painel`).
2. **Próximas importâncias "sem horizonte" (4.1.8):** a lista materializa até o 12º mês (DEC-MV-18). Se houver menos de três, procura mais cinco anos à frente, só em séries (cobre a repetição anual). Está documentado como limite prático.
3. `ResumoFinanceiroResposta` e `_comparacoes` foram refatoradas apenas para reutilização (sem mudança de comportamento).

## 4. F11 — consolidação

| Item | Resultado |
| --- | --- |
| CT-F11-01 | `tests/integracao/test_fluxo_integrado.py`: registro → atividade semanal → receita/despesa (saldo 1.220,35) → importância 99,90 → lembrete e notificação (job) → pagamento 105,00 → painel coerente → exclusão da despesa reabre a importância |
| CT-F11-02 | `tests/desempenho/` (marcador `performance`). Volume de referência: 10 séries diárias × 5 anos (≈ 16.400 atividades), 2.000 movimentações, 500 importâncias. **p95 entre 6 e 50 ms** em todos os endpoints de lista, resumo e painel (meta proposta: 300 ms). Partida a frio (materializar 1.826 ocorrências de uma série): ≈ 0,5 s. `EXPLAIN (ANALYZE, BUFFERS)`: totais, atividades do dia e importâncias do período usam índices; pendências anteriores usa varredura sequencial (99,9 % das linhas casam; 6 ms) |
| Índices | **Nenhum índice novo.** Não há evidência que o justifique (a regra do plano exige evidência e aprovação) |
| CT-F11-03 | `tests/integracao/test_configuracao_producao.py`: segredos obrigatórios, `EMAIL_MODO=smtp` obrigatório em produção (`memoria` e `console` proibidos), SMTP completo |
| Operação | `docs/operacao/operacao.md` |

Como rodar a medição (separada da suíte e do Pyright):

```bash
uv run pytest tests/desempenho -m performance -q
```

## 5. Desvios do contrato (aditivos, todos cobertos por testes)

Necessários para o aplicativo exibir o que o protótipo mostra sem consultas extras:

1. `AtividadeItem` e `ImportanciaItem` ganharam `periodicidade` (`NAO_REPETIR` quando avulsa) e `serie_id`. O texto "Repete semanalmente" e a escolha do alcance (esta / esta e próximas) aparecem na lista.
2. `ImportanciaItem` passou a trazer `momento_conclusao` (antes só no detalhe); a lista de Concluídos usa para exibir quando foi concluída.
3. `ConsultaMovimentacoesResposta.total`: total do filtro (o app mostra "N encontrada(s)" e "Carregar mais (N)").
4. `Settings`: `LEMBRETES_INTERVALO_S`, `LEMBRETES_LOTE`, `LEMBRETES_JANELA_DIAS`, `CORS_ORIGENS` (lista JSON; vazio = sem CORS, que só interessa a clientes web) e `EMAIL_MODO=console` (escreve o e-mail, com o código de recuperação, no log; **proibido em produção**), para testar "Esqueceu a senha" no desenvolvimento.

## 6. Integração do aplicativo Flutter

1. `lib/data/repositorio_api.dart` implementa a mesma interface `Repositorio`; nenhuma tela mudou. `lib/data/cliente_api.dart` cuida do transporte.
2. **Idempotência:** cada cadastro envia `Idempotency-Key`. A chave é mantida enquanto o resultado é desconhecido (falha de rede, 5xx, 408) e descartada após uma resposta definitiva; assim, repetir o mesmo envio não duplica e um novo envio igual, depois do sucesso, é aceito (10.4.6, 11.4.6).
3. **Sessão:** o token (JWT de 24 h) fica **só em memória**. Guardar token em disco exige armazenamento seguro (Keychain/Keystore); não foi adicionada dependência de plugin nativo sem sua aprovação. Consequência: o login é pedido a cada abertura do aplicativo. Um 401 em rota autenticada leva à tela de login.
4. **Fuso horário** do cadastro: o Dart expõe só o deslocamento; usa-se `America/Sao_Paulo` (ou Manaus, Rio Branco, Noronha pelo deslocamento) e `--dart-define=FUSO_HORARIO=` para sobrescrever.
5. **Categorias** continuam por nome na interface; os UUIDs vêm de `/categorias/*` (carregados uma vez por sessão).
6. **Paginação:** a interface usa `deslocamento/limite`; o repositório guarda os cursores já vistos e, sem eles, percorre a lista do início. "Outros" (que existe em receitas e despesas) sem tipo escolhido consulta os dois catálogos.
7. **Sobreposição de horários:** a tela já pergunta ao usuário antes de salvar; o repositório calcula as sobreposições a partir da lista do dia e envia `confirmar_sobreposicao=true`.
8. **Modo demonstração** preservado: `flutter run --dart-define=USAR_MEMORIA=true`.
9. O teste de golden `04_codigo` falhava de forma intermitente porque exibia o código aleatório da recuperação; o repositório em memória aceita um `Random` injetável e os testes usam semente fixa.

## 7. Resultado

- API: 412 testes na suíte padrão (PostgreSQL 16) + 2 de desempenho; Ruff e Pyright limpos.
- App: `flutter analyze` sem avisos; 24 testes existentes; 16 testes de integração contra a API real (`test/integracao_api_test.dart`) e 1 de interface com login pela tela (`test/integracao_ui_test.dart`), executados com `API_URL_TESTE`.
