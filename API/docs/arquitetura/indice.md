# Índice da arquitetura — API MinhaVida

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/indice.md` |
| Fase | F0 — Arquitetura e reconciliação |
| Estado da F0 | **REVISADA PELO USUÁRIO.** DEC-MV-01 a 05, DEC-MV-25 (escopo limitado) e DEC-MV-26 aprovadas em 2026-10-11. DEC-MV-06, 07 e 08 aprovadas em 2026-10-13. DEC-MV-09 a 13 e DEC-MV-14 no escopo limitado da F3 aprovadas em 2026-10-13 (M16). DEC-MV-14 no restante e DEC-MV-15 a 24 pendentes |
| Data | 2026-10-10. Atualizado em 2026-10-11 e em 2026-10-13 (inclusive o fechamento documental da F2, a conferência do commit da F2, a preparação da F3, a revisão dirigida M15 e a liberação da F3, M16) |

## 1. Ordem de leitura

1. `docs/arquitetura/analise_projeto_minhavida.md`: baseline (inclusive o conteúdo do commit de baseline, §3.5), fontes, reconciliações (REC), achados (ACH), riscos e **decisões a aprovar (DEC, §9)**.
2. `docs/adr/0001_arquitetura_api_minhavida.md`: decisões D-01 a D-16.
3. `docs/adr/0002_identificadores_uuid.md`: UUIDv7 e diff do contrato.
4. `docs/arquitetura/arquitetura_api_minhavida.md`: **fonte canônica** dos contratos (escopo financeiro, módulos, HTTP, transações, concorrência, algoritmos, modelo físico, segurança e operação).
5. `docs/arquitetura/plano_fases_api.md`: fases F0–F11, grafo, fichas e cobertura.
6. `docs/arquitetura/plano_validacao_auditoria.md`: política de testes, catálogo de CTs, comandos, evidências, severidade, gates e protocolo de auditoria.
7. `docs/arquitetura/matriz_requisitos_api.md`: rastreabilidade das telas 1–11, do contrato de dados e do escopo financeiro.
8. `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md`: Prompt Master da primeira fase, executado. F1 `APROVADO_COM_P3` e integrada no commit `90412ec`.
9. `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` e `docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md`: auditoria da F1 (`BLOQUEADO`, histórico) e reauditoria das correções (`APROVADO_COM_P3`), com os achados ACH-MV-F1-001 a 007. O prompt das correções está em `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md`.
10. `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md`: Prompt Master da F2 (esquema de dados), executado. F2 `APROVADO_COM_P3`, aguardando integração.
11. `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`: auditoria da F2 (`APROVADO_COM_P3`), com os achados ACH-MV-F2-001 a 003. A instrução da auditoria está em `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md`.
12. `docs/arquitetura/preparacao_f3_identidade_acesso.md`: dossiê da F3 (identidade e acesso), **aprovado** em 2026-10-13 (M16): conferência do commit da F2, avaliação de DEC-MV-09 a 13, contratos da F3, achados ACH-MV-ARQ-026 a 038 (encerrados), diffs normativos (aplicados), revisão M15 (§13) e liberação (§14).
13. `PROMPTS/PROMPT_MASTER_SONNET_5_F3_IDENTIDADE_ACESSO.md`: Prompt Master da F3, em `PRONTO_PARA_ETAPA_A` (2026-10-13).

## 2. Inventário de documentos

| Caminho | Tipo | Estado |
| --- | --- | --- |
| `CLAUDE.md` | Norma do projeto (usuário) | Vigente. **Atualizado em 2026-10-13** com autorização do usuário (M10): identificadores UUID (DEC-MV-06, diff de `analise` §10.1), representação textual das enumerações, `JSON(none_as_null=True)` e regra dos timestamps (DEC-MV-07) e CHECKs de nome (DEC-MV-08). As linhas truncadas 3, 10 e 12 não foram tocadas (ACH-MV-ARQ-012). `analise` §10.2 **não aplicado** (DEC-MV-22 pendente). **Atualizado em 2026-10-13 (M16)** só nos trechos dos diffs CM-1 (tabela 2, parâmetros da recuperação, DEC-MV-11) e CM-2 (tabela 1, forma canônica do e-mail, DEC-MV-09), sem tocar nas linhas 3, 10 e 12 |
| `PROMPTS/PROMPT_MASTER_SONNET_5_IMPLEMENTACAO_BANCO_DADOS.md` | Prompt anterior (banco) | **SUSPENSO**, confirmado pelo usuário em 2026-10-11. Não usar como autorização. Substituído pela F2 do plano. Arquivo não alterado |
| `docs/adr/0001_arquitetura_api_minhavida.md` | ADR | **PARCIALMENTE ACEITO**: D-01, D-02, D-03, D-04, D-08, D-09 e D-14 aceitas (D-09 integral desde 2026-10-13, DEC-MV-07). D-07, D-13 e D-15 aceitas em 2026-10-13 (DEC-MV-09 e 12, M16), com AD-1 e AD-2. D-05 aceita só nas travas de linha da recuperação (DEC-MV-14, escopo limitado; AD-3). Demais PROPOSTAS |
| `docs/adr/0002_identificadores_uuid.md` | ADR | **ACEITO** em 2026-10-13 (DEC-MV-06) |
| `docs/arquitetura/analise_projeto_minhavida.md` | Análise | PROPOSTO, com DEC-MV-01 a 08, 25 e 26 aprovadas. REC-MV-033 e 034 acrescentadas em 2026-10-13. Na preparação da F3 (M14): ACH-MV-ARQ-018 encerrado, ACH-MV-ARQ-026 a 038 registrados e nota da §9. Na liberação da F3 (M16): DEC-MV-09 a 13 e DEC-MV-14 (escopo da F3) aprovadas; RECs 007, 011, 017, 019 e 020 e riscos 03 e 04 atualizados; ACH-MV-ARQ-015 e 026 a 038 encerrados; sincronizações do dossiê §13.4 |
| `docs/arquitetura/arquitetura_api_minhavida.md` | Arquitetura | **PARCIALMENTE ACEITO**: §2, §4.4, §5, §3 (itens da F1) e §10.1 somente na convenção de nomes. §1.1 registra instrução do usuário. §3.4 ganhou o limite de `hide_parameters` e o contrato de log do 500 de banco (P-DOC-03). §10 aceito integralmente em 2026-10-13 (DEC-MV-07, com ADR-0002 e DEC-MV-08), incluindo §10.3.1 (timestamps). Seeds de §10.5 conforme a emenda F2-D1, incorporada depois da auditoria da F2 (A1, M13). Partes da F3 aceitas em 2026-10-13 (M16), com os diffs AR-1 a AR-10 do dossiê da F3: itens da F3 de §3.1, §4.2, códigos de identidade de §4.5, linhas da F3 de §6.2, §6.3 e §6.6, §7, §8.2, §8.3, §9.1 e linhas da F3 de §11. §2.2 com as arestas da F3 (AR-8 revisto), sem mudar D-02 nem a DEC-MV-24 |
| `docs/arquitetura/matriz_requisitos_api.md` | Rastreabilidade | PROPOSTO. Contrato de dados atualizado em 2026-10-13 (DEC-MV-06 a 08). Comprovação estrutural da F2 registrada nas linhas do contrato de dados (M14). Telas 1 a 3 e 4.1.1 em `PLANEJADO`, com as decisões da F3 aprovadas; MZ-1 aplicado; exclusões de Perfil e de logout no servidor decididas (M16) |
| `docs/arquitetura/plano_fases_api.md` | Plano | PROPOSTO. F1 integrada (`90412ec`). F2 `APROVADO_COM_P3` e integrada (`91be324`). F3 com decisões aprovadas e Prompt F3 em `PRONTO_PARA_ETAPA_A`; ficha atualizada pelo PF-1 (M16) |
| `docs/arquitetura/plano_validacao_auditoria.md` | Validação e auditoria | **PARCIALMENTE ACEITO**: §2, §3, §5 e catálogo da F1 (DEC-MV-04), com CT-F1-21 e 22 acrescentados (P-DOC-04). Catálogo da F2 vigente desde 2026-10-13 (DEC-MV-06 a 08); §3.4 precisado (REC-MV-034); texto do CT-F2-07 alinhado à emenda F2-D1 depois da auditoria (B4, M13). Catálogo da F3 vigente desde 2026-10-13, com o PV-1 (CT-F3-22 a 24 e 26 a 29 acrescentados; M16) |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_FUNDACAO_API.md` | Prompt Master F1 | **Executado.** F1 `APROVADO_COM_P3` (reauditoria de 2026-10-11) e integrada no commit `90412ec` (G6, 2026-10-13). §8.5, §11.1 e §14, passo 10, atualizados (P-DOC-01, 02 e 06). Histórico: `PRONTO_PARA_ETAPA_A` em 2026-10-11 |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` | Prompt de correções da F1 | **Executado** e verificado na reauditoria. Preservado sem alteração como evidência histórica (a emenda `env_file=None` está registrada no §4) |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md` | Prompt Master F2 | **Executado.** F2 `APROVADO_COM_P3` (auditoria de 2026-10-13). Versão implementada: SHA-256 `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c`, preservada fora do repositório em `~/minhavida_evidencias/f2_fechamento_DFR1NBKL/antes/`. Notas pós-auditoria em §12 (emenda D3) e §13 (erratas ACH-MV-F2-001 e 002) e estado no cabeçalho (M13), sem alterar o texto original. Histórico: `PRONTO_PARA_ETAPA_A` em 2026-10-13 |
| `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` | Relatório de auditoria | Evidência histórica: F1 `BLOQUEADO` em 2026-10-11. Não alterar |
| `docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md` | Relatório de reauditoria | Evidência histórica: F1 `APROVADO_COM_P3` em 2026-10-11. Não alterar |
| `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md` | Instrução de auditoria (usuário) | Entrada da auditoria da F2 (M12). SHA-256 `3854631cd82b8cb13f0c2fb92a9e729f21446112428a258906a897e217271db3`. Preservada sem alteração |
| `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md` | Relatório de auditoria | Evidência: F2 `APROVADO_COM_P3` em 2026-10-13, aceito em M13 e integrado no commit `91be324`. SHA-256 `f4c529692d6032a052083375f94fc493ea73c1d6449dacfbe1cc16e266cf1560`. Não alterar; os estados posteriores dos achados estão no §5 deste índice |
| `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` | Instrução de sessão (usuário) | Entrada da conferência do commit da F2 e da preparação da F3 (M14). SHA-256 `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695`. Preservada sem alteração; fora do commit `91be324` |
| `docs/arquitetura/preparacao_f3_identidade_acesso.md` | Dossiê da F3 | **APROVADO** em 2026-10-13 (M16). Diffs da §8 aplicados; revisão M15 na §13 e liberação na §14. Histórico: entregue para revisão (M14) |
| `PROMPTS/PROMPT_MASTER_SONNET_5_F3_IDENTIDADE_ACESSO.md` | Prompt Master F3 | **`PRONTO_PARA_ETAPA_A`** (2026-10-13, M16). Os SHA-256 dos documentos de preparação estão no seu §1.2; o hash do próprio prompt vai na mensagem de entrega. Aplica as lições do ACH-MV-F2-002. Histórico: `BLOQUEADO — AGUARDANDO_DECISAO` até a M16 |

## 3. Precedência normativa

1. Instruções explícitas do usuário na sessão corrente, dentro do escopo.
2. `CLAUDE.md`.
3. ADRs **ACEITOS**, por decisão. Um ADR aceito que substitua expressamente uma cláusula do `CLAUDE.md` (ADR-0002 → tipos de ID) prevalece sobre ela. O gate da fase afetada, porém, exige o `CLAUDE.md` já atualizado, para que não haja duas fontes contraditórias vigentes.
4. `arquitetura_api_minhavida.md`, `plano_fases_api.md`, `plano_validacao_auditoria.md` e `matriz_requisitos_api.md`, que precisam estar conformes a 2 e 3.
5. Prompt Master da fase (operacional).
6. O prompt anterior do banco não tem precedência (SUSPENSO).

Regras complementares:

- Documentos e decisões PROPOSTOS não autorizam implementação.
- Uma decisão aceita alcança as seções de detalhe que ela cita **somente na parte que detalha essa decisão**. Partes dessas seções que servem a fases posteriores seguem as decisões dessas fases (por exemplo, as variáveis de F3 e F9 na arquitetura §3.1).
- Uma aprovação com escopo limitado vale só para os itens nomeados. Exemplo: DEC-MV-25 aceita a convenção de nomes, e o restante de D-09 segue PROPOSTO.
- Conflito entre textos aceitos: aplica-se a ordem acima até o usuário decidir. Caso registrado: REC-MV-029. Até DEC-MV-24, vale ADR-0001 D-02 sobre a arquitetura §2.2. Nenhuma fase até a F4 é afetada.
- Instruções de escopo do usuário são registradas em §4 e no documento canônico correspondente (escopo financeiro: arquitetura §1.1).

## 4. Registro de aprovações

> Preenchido somente mediante aprovação explícita do usuário, com data e escopo. Uma aprovação não se estende a decisões ou documentos não citados.

Referências das mensagens do usuário na sessão `8f60e6c4-621a-44be-a17d-8b16d858086c`. M1 a M6 são de 2026-10-11; M7 a M16, de 2026-10-13:

- **M1:** primeira mensagem do dia, com o texto “Aprovo as seguintes decisões, conforme descritas em `docs/arquitetura/analise_projeto_minhavida.md`, seção 9: DEC-MV-01. DEC-MV-02. DEC-MV-03. DEC-MV-04. DEC-MV-05.”
- **M2:** segunda mensagem do dia, com o texto “Aprovo expressamente a DEC-MV-25.”
- **M3:** mensagem que pediu a auditoria independente da F1 (“Prompt Master — Opus 5.5 — Auditoria independente da F1 e preparação condicionada da F2”). Ela declara, no seu §1.2, aprovações dadas antes ao Sonnet, em sessão que não está disponível aqui.
- **M4:** mensagem com o texto “Aprovo a DEC-MV-26, opção B”.
- **M5:** mensagem que pediu a resposta à Etapa A das correções. O Opus preparou a emenda `env_file=None`, e o usuário a encaminhou ao Sonnet como instrução própria (atestado em M6, §1.3).
- **M6:** mensagem que pediu a reauditoria das correções (“Prompt Master — Opus 5.5 — Reauditoria independente das correções da F1”).
- **M7:** mensagem com o texto “Aprovo a P-DOC-06 e a P-DOC-07, exatamente nos escopos da seção 9.1 de docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md.”
- **M8:** mensagem com o texto “Autorizo atualizar a nota desatualizada do indice.md §5 e registrar no §4 as aprovações de P-DOC-06 e P-DOC-07 que já concedi.”
- **M9:** mensagem com o texto “O commit da F1 foi concluído. SHA: 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30”, que pede “reconheça o G6 da F1 como cumprido. Use-o como baseline para a preparação da F2, preservando os P3 em acompanhamento” e “Incorpore esse registro à próxima atualização documental”.
- **M10:** mensagem com o texto “Vamos preparar a F2 — Esquema de dados.”, que aprova expressamente DEC-MV-06, DEC-MV-07 (restante), DEC-MV-08 e a opção A do ACH-MV-F1-005, fixa o baseline `90412ec` e autoriza somente leitura, análise e atualização documental, inclusive do `CLAUDE.md` e dos ADRs, e a preparação do Prompt F2.
- **M11:** mensagem com o texto “O Sonnet concluiu a Etapa A da F2 e identificou uma divergência real entre a arquitetura e o Prompt Master.”, que pede a resolução da D1 e uma emenda para o usuário encaminhar ao Sonnet, sem incluir o “pode implementar”.
- **M12:** mensagem com o texto “Execute a auditoria independente da F2 conforme:”, seguido do caminho `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md`.
- **M13:** mensagem com o texto “Aceito o veredito APROVADO_COM_P3 da F2 e autorizo o fechamento documental nos limites abaixo.”, que autoriza as reconciliações A1 a A4 e B1 a B5 do relatório da F2 (item 1), confirma as aprovações anteriores (item 2), decide os achados (item 3) e fixa os limites (item 4).
- **M14:** mensagem que pediu a conferência do commit da F2 e a preparação da F3 (“Prompt Master — Opus 5.5 — Conferência do commit da F2 e preparação da F3”), salva em `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md`. Informa o SHA do commit da F2 (§1.1), autoriza leitura, análise e atualização documental (§4) e o encerramento documental do ACH-MV-ARQ-018 e do ACH-MV-F2-002 se comprovados (§4 e §10). Não aprova DEC-MV-09 a 13, não aceita riscos e não autoriza implementar a F3 (§0).
- **M15:** mensagem de revisão dirigida dos rascunhos da F3, em seis pontos: data de nascimento estrita, normalização do e-mail, importação entre services × D-02, divergências entre dossiê e prompt, sincronização dos testes de concorrência e explicação da DEC-MV-10. Autorizou ajustar os rascunhos e apresentar reconciliações; não aprovou DEC-MV-09 a 13, a parcela da DEC-MV-14 nem alterações de contratos vigentes (dossiê F3 §13).
- **M16:** mensagem com o texto “Opus, revisei o relatório da revisão dirigida M15 e o dossiê `docs/arquitetura/preparacao_f3_identidade_acesso.md`.”, que aprova exclusivamente DEC-MV-09 (item 1), DEC-MV-10 na opção A (item 2), DEC-MV-11 (item 3), DEC-MV-12 (item 4), DEC-MV-13 (item 5) e DEC-MV-14 só no escopo da F3 (item 6). Autoriza a reconciliação documental, inclusive CM-1, CM-2, AR-8 revisto e AR-10, as sincronizações da §13.4, o registro da M15 e da própria mensagem, a atualização dos estados e a conferência do Prompt F3; preserva o baseline `91be324`; e manda marcar o Prompt F3 como `PRONTO_PARA_ETAPA_A`. É documental: não autoriza implementação, código, testes, migrações, configuração, dependências, `.env`, `git add`, commit, push ou merge. A Etapa B depende do relatório da Etapa A e do “pode implementar”.
- A aprovação da emenda F2-D1, com as respostas D2 e D3, e o “pode implementar” da F2 foram dados pelo usuário ao Sonnet, fora desta sessão. O texto dessas mensagens não está disponível aqui. Estão atestados no §3 da instrução de auditoria e confirmados em M13 (item 2).

Os itens de cada mensagem são citados entre parênteses.

| Data | Decisão / documento | Escopo aprovado | Referência | Registrado por |
| --- | --- | --- | --- | --- |
| 2026-10-11 | DEC-MV-01 | Conforme `analise` §9: monólito em camadas `routers → services → models`, sem repository; organização de diretórios e nomenclatura; driver psycopg 3. Aceita ADR-0001 D-01, D-02 e D-03 e a arquitetura §2. Ressalva: conflito interno entre D-02 e §2.2 (REC-MV-029), pendente em DEC-MV-24 | M1 (item 1) | Opus |
| 2026-10-11 | DEC-MV-02 | Sessão por requisição com autobegin; commit explícito apenas no router; service só com `flush`; jobs donos da própria transação; engine no `lifespan`. Aceita D-04 (e D-03), a arquitetura §5 e os itens da F1 da arquitetura §3 | M1 (item 1) | Opus |
| 2026-10-11 | DEC-MV-03 | `ErroNegocio`, formato JSON único, catálogo de códigos, validação sem eco. Aceita D-08 e a arquitetura §4.4 | M1 (item 1) | Opus |
| 2026-10-11 | DEC-MV-04 | Testes direcionados; suíte completa como exceção; Testcontainers `postgres:15-alpine`; Ruff de verificação com `--no-fix`; `task test` fora dos gates. Aceita D-14 e o plano de validação §2, §3, §5 e o catálogo da F1 | M1 (item 1) | Opus |
| 2026-10-11 | DEC-MV-05 | Higiene da F1, conforme `analise` §9: `compose.yaml` com `.env` em `127.0.0.1`, `.gitignore`, `requires-python >=3.14`, `pydantic-settings` direto, `httpx` dev, remoção da rota `/` e de `schemas/message.py`, criação de `__init__.py`. Não corresponde a uma decisão do ADR | M1 (item 1) | Opus |
| 2026-10-11 | **DEC-MV-25 (escopo limitado)** | **Somente** a convenção `CONVENCAO_NOMES`, conforme a arquitetura §10.1 e o Prompt F1 §6, com os padrões `pk`, `uq`, `ck`, `fk` e `ix` preservados exatamente, e sua aplicação ao `Base.metadata` por `MetaData(naming_convention=CONVENCAO_NOMES)` na F1. Aceita D-09 apenas nesse item | M2 (item 1) | Opus |
| 2026-10-11 | **Fora da aprovação de DEC-MV-25** | Restante de DEC-MV-07 e de D-09; DEC-MV-06 e ADR-0002; tabelas, migrações e seeds de domínio; alterações no `TimestampMixin`; `eager_defaults`; qualquer outra decisão pendente; a implementação da F1 | M2 (item 1) | Opus |
| 2026-10-11 | **Fora das aprovações deste dia** | DEC-MV-06 a 24; ADR-0001 como um todo e suas decisões D-05 a D-07, D-10 a D-13, D-15 e D-16; ADR-0002; a implementação da F1, que depende do baseline e de “pode implementar”; a aprovação de qualquer fase. DEC-MV-24 permanece pendente, para decisão antes da F5 | M1 (itens 1, 4 e 6) e M2 (itens 1 e 3) | Opus |
| 2026-10-11 | Instrução de escopo financeiro | Financeiro manual, com totais e saldo calculados a partir dos lançamentos; sem integrações financeiras externas nem infraestrutura “para uso futuro”; forma de pagamento descritiva; recuperação de senha por e-mail preservada. Registrado na arquitetura §1.1 (REC-MV-028). Reafirmado na M2 | M1 (itens 2 e 3) e M2 (item 1) | Opus |
| 2026-10-11 | Nomenclatura da F8 | F8 passa a se chamar “Vínculo interno entre despesas e importâncias”, com o mesmo identificador. Não autoriza implementar a F8 nem aprova decisões pendentes | M1 (item 4) | Opus |
| 2026-10-11 | Prompt anterior do banco | Permanece SUSPENSO | M1 (item 6) e M2 (item 2) | Opus |
| 2026-10-11 | Baseline sem credenciais | Instrução do usuário: baseline verificável antes da implementação, sem credenciais no histórico. Orientação em `analise` §3.5 (REC-MV-032). **Não** é exceção ao ACH-MV-ARQ-019, que segue ABERTO | M2 (item 3) | Opus |
| 2026-10-11 | Implementação da F1 | “Pode implementar” dado ao Sonnet após a Etapa A, com revalidação prévia do baseline | Declarado em M3 (§1.2). A mensagem original ao Sonnet não está disponível nesta sessão | Opus (registro em 2026-10-11, na reauditoria) |
| 2026-10-11 | Imports relativos em `tests/` | Autorizados expressamente, preservando a estrutura e sem mudar Ruff, Pyright, `sys.path`, `PYTHONPATH` ou dependências | Declarado em M3 (§1.2) | Opus (registro na reauditoria) |
| 2026-10-11 | **DEC-MV-26, opção B** | `exclude = ["*.md"]` em `[tool.ruff.format]` do `pyproject.toml`, com os comentários do anexo B de `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md`. Não muda comandos nem a cobertura de `.py`. Não inclui `alembic/` nos gates (ACH-MV-F1-005 segue pendente). Alternativas A e C não escolhidas | M4 | Opus (registro na reauditoria; adiado para não alterar os hashes travados pelo prompt de correções) |
| 2026-10-11 | Correções pós-auditoria da F1 | Implementação de `PROMPTS/PROMPT_MASTER_SONNET_5_F1_CORRECOES_POS_AUDITORIA.md` (ACH-MV-F1-001 a 003), inclusive o log de `DBAPIError` 500 (§7.2) e a fixture (§7.3), autorizada ao Sonnet após a Etapa A | Declarado em M6 (§1.2) | Opus |
| 2026-10-11 | Emenda `env_file=None` | `SettingsTeste` com `model_config = SettingsConfigDict(env_file=None)` e asserção estrutural no REG-F1-02. É instrução do usuário ao Sonnet, com precedência sobre o prompt de correções §7.3 e §7.5. Não é desvio do implementador | M5 e M6 (§1.3) | Opus |
| 2026-10-11 | Atualizações documentais P-DOC-01 a 05 | Prompt F1 §8.5 e §11.1; arquitetura §3.4; plano de validação, catálogo da F1 (CT-F1-21 e 22); este índice §4 e §5; `analise` §9. Não alcançam `CLAUDE.md`, ADRs, código ou configuração | M6 (§0, item 5, e §9) | Opus |
| 2026-10-11 | **Fora destas aprovações** | DEC-MV-06 a 24; a liberação da F2; a decisão sobre `alembic/` nos gates (ACH-MV-F1-005); o commit da F1, que cabe ao usuário | M3, M4 e M6 | Opus |
| 2026-10-13 | **P-DOC-06** | Conforme a reauditoria §9.1: Prompt F1 §14, passo 10, passa a usar `POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet`, que também serve de modelo para os próximos prompts. Corrige no Prompt F1 o comando do ACH-MV-F1-007 | M7 | Opus |
| 2026-10-13 | **P-DOC-07** | Conforme a reauditoria §9.1: estados descritivos em `indice.md` §1, §2, §6 e §7, no cabeçalho do Prompt F1 e em `plano_fases_api.md` (cabeçalho e §3, linha da F1). Prompt F1 executado; F1 `APROVADO_COM_P3`, aguardando integração; contagem de CTs (173 + 2) e próxima ação | M7 | Opus |
| 2026-10-13 | Fechamento documental da F1 | Atualização da nota do §5 e este registro no §4. Não alcança código, testes, configuração, dependências, relatórios de auditoria, `CLAUDE.md` nem ADRs | M8 | Opus |
| 2026-10-13 | **Fora destas aprovações** | DEC-MV-06, o restante da DEC-MV-07, DEC-MV-08 e a opção do ACH-MV-F1-005, a tratar separadamente; DEC-MV-09 a 24; qualquer mudança da F2; o commit da F1, que cabe ao usuário | M7 e M8 | Opus |
| 2026-10-13 | **G6 da F1: cumprido** | Commit `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30` (pai `bd2b2e0`), conferido pelo Opus só com leitura: 44 alterações (30 adicionadas, 1 removida, 13 modificadas), árvore de 51 arquivos igual ao manifesto final (51/51) e `git status` vazio. É o baseline da F2. Os P3 em acompanhamento (ACH-MV-F1-005 a 007) foram preservados | M9 e M10 | Opus |
| 2026-10-13 | ACH-MV-ARQ-006 encerrado | Pela conferência do commit: o `compose.yaml` entrou no histórico com SHA-256 `bb1d211f…`, igual ao objeto reauditado e ao Prompt F1 §9.3. Critério previsto na auditoria da F1 e na reauditoria §4 | M10 | Opus |
| 2026-10-13 | **DEC-MV-06** | UUIDv7 gerado pela aplicação, conforme ADR-0002 (agora ACEITO), incluindo a reconciliação das 13 chaves primárias e das 19 estrangeiras. `CLAUDE.md` atualizado pelo diff de `analise` §10.1 | M10 (item 1) | Opus |
| 2026-10-13 | **DEC-MV-07 (restante)** | Convenções físicas de ADR-0001 D-09 (agora aceita integralmente) e da arquitetura §10: modelos, tipos, enumerações com CHECK, timestamps, mixin, migração inicial e seeds | M10 (item 2) | Opus |
| 2026-10-13 | **DEC-MV-08** | Quatro CHECKs de 3 a 100 caracteres: `importancia.nome`, `movimentacao_financeira.nome`, `serie_atividade.nome_padrao` e `serie_importancia.nome_padrao` | M10 (item 3) | Opus |
| 2026-10-13 | **ACH-MV-F1-005, opção A** | `alembic/` no Ruff e no Pyright, com a exceção `PLC0415` restrita a `alembic/env.py`. Especificada para o Sonnet implementar na F2 (Prompt F2 §9). Não aplicada nesta etapa | M10 (item 4) | Opus |
| 2026-10-13 | Preparação documental da F2 | Registro do G6 e do ACH-MV-ARQ-006; registro destas aprovações; reconciliação do `CLAUDE.md`, dos ADRs, da análise, da arquitetura, dos planos, da matriz, deste índice e do cabeçalho do Prompt F1; criação do Prompt F2. Inclui REC-MV-033 (padrões do ORM) e REC-MV-034 (limpeza dos testes) | M10 | Opus |
| 2026-10-13 | **Fora destas aprovações** | Implementação da F2, que depende do “pode implementar” após a Etapa A; DEC-MV-09 a 24; DEC-MV-22 (`analise` §10.2, não aplicado ao `CLAUDE.md`); DEC-MV-19 (valor `DESATIVADO`); encerramento formal do ACH-MV-ARQ-019; `git add`, commit, push e merge | M9 e M10 | Opus |
| 2026-10-13 | **Emenda F2-D1, com as respostas D2 e D3** | Seeds por `instrucoes_categorias() -> list[Insert]`, executadas com `op.execute` no fim de `upgrade()`; substitui só o trecho de seeds da arquitetura §10.5. D2: comandos da Etapa B no Prompt F2 §13. D3: `ls -A1 alembic/versions` na Etapa A | Mensagem ao Sonnet fora desta sessão; atestada na instrução de auditoria §3; confirmada em M13 (item 2). Análise do Opus pedida em M11 | Opus |
| 2026-10-13 | **Etapa B da F2** | “Pode implementar” para o Prompt F2 com a emenda F2-D1 | Mensagem ao Sonnet fora desta sessão; confirmada em M13 (item 2) | Opus |
| 2026-10-13 | Auditoria independente da F2 | Conforme `PROMPTS/PROMPT_MASTER_OPUS_5_5_AUDITORIA_F2_ESQUEMA_DADOS.md` | M12; confirmada em M13 (item 2) | Opus |
| 2026-10-13 | **Veredito da F2 aceito** | `APROVADO_COM_P3` (`docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`). G5 da F2 cumprido; G6 pendente até o commit do usuário | M13 | Opus |
| 2026-10-13 | **Fechamento documental da F2** | A1 a A4 e B1 a B5 do §13 do relatório, inclusive B4: arquitetura §10.5; plano de fases (ficha da F2, itens 10 e 12, e estados); plano de validação (CT-F2-07); notas de emenda e errata no Prompt F2 §12 e §13 e estado no seu cabeçalho, sem apresentar texto corrigido como implementado; este índice. Relatório da auditoria preservado | M13 (itens 1 e 3) | Opus |
| 2026-10-13 | **ACH-MV-F1-005, 006 e 007 encerrados** | Com as evidências da auditoria da F2 (relatório §8.6 e §10.2) | M13 (item 3) | Opus |
| 2026-10-13 | **Achados da F2** | ACH-MV-F2-001 e 003 encerrados depois de aplicadas e conferidas as correções documentais B2 e B1. ACH-MV-F2-002: erratas registradas (B3); a aplicação das lições no próximo Prompt Master continua em acompanhamento | M13 (item 3) | Opus |
| 2026-10-13 | **Fora destas aprovações** | Alterações de código, testes, migração, configuração e dependências; reexecução dos testes; `git add`, commit, push e merge (o commit da F2 e o G6 cabem ao usuário); a F3; DEC-MV-09 a 13 | M13 (item 4) | Opus |
| 2026-10-13 | **G6 da F2: cumprido** | Commit `91be324c88c5a3f99a49b1b1700963e32ef257e9` (pai `90412ec`), informado pelo usuário (M14) e conferido pelo Opus só com leitura: delta = `lista_commit.txt` (43 caminhos; 26 `A`, 17 `M`); blobs = `manifesto_commit.sha256` (43/43); 30 arquivos técnicos = manifesto da auditoria (30/30); relatório da auditoria com o hash registrado; árvore com 77 arquivos, sem `.env` nem caches; índice vazio. Só `mensagem_commit.txt` mudou depois do manifesto do fechamento, e o texto é igual à mensagem do commit. Não foi nova auditoria nem execução de testes. É o baseline técnico da F3 | M14 | Opus |
| 2026-10-13 | ACH-MV-ARQ-018 encerrado | Critério cumprido: DEC-MV-08 aprovada e CT-F2-20 comprovado na auditoria da F2; objeto integrado em `91be324` (`analise` §7) | M14 (§4) | Opus |
| 2026-10-13 | ACH-MV-F2-002 encerrado (documental) | As quatro lições foram aplicadas e verificadas no Prompt F3: blocos exatos validados com Ruff e Pyright; passo para erros residuais; regra e modelo coerentes; `--frozen --no-sync` (dossiê F3 §11). Não implica aprovação das decisões da F3 nem sucesso de testes futuros | M14 (§10) | Opus |
| 2026-10-13 | Preparação documental da F3 | Dossiê e Prompt F3 (rascunho bloqueado) criados; registros deste índice; estados e notas de proposta em `analise`, `plano_fases_api.md`, `plano_validacao_auditoria.md` e `matriz_requisitos_api.md`. Sem alteração de `CLAUDE.md`, ADRs, arquitetura, código, testes, configuração ou dependências | M14 (§4) | Opus |
| 2026-10-13 | **Fora destas aprovações** | DEC-MV-09 a 13 e a parte da DEC-MV-14 usada pela F3; aceitação de riscos (inclusive o da DEC-MV-10); diffs da §8 do dossiê; liberação da Etapa A e implementação da F3; DEC-MV-14 a 24 no restante; `git add`, commit, push e merge | M14 (§0) | Opus |
| 2026-10-13 | Revisão dirigida dos rascunhos da F3 | Dossiê (§13) e Prompt F3 ajustados nos seis pontos; reconciliações e propostas CM-2, AR-8 revisto e AR-10 apresentadas. Nenhuma decisão aprovada; Prompt F3 mantido bloqueado | M15 | Opus |
| 2026-10-13 | **DEC-MV-09** | Conforme o dossiê da F3 §4.1, R9.1 a R9.9: JWT HS256, validade padrão de 24 h, configurável de 5 a 1440 minutos; claims e validação temporal conforme o contrato; Argon2id e seu limitador; fuso obrigatório; dependências especificadas; e-mail canônico em cadastro, login, recuperação e envio. Aceitos: logout só no cliente e token obtido por terceiro utilizável até expirar, salvo troca de senha ou do segredo. Aceita ADR-0001 D-07 e D-13. **Não** aprova refresh, gestão de sessões nem DEC-MV-21 | M16 (item 1) | Opus |
| 2026-10-13 | **DEC-MV-10, opção A** | Requisito 3.4.2 mantido, com 404 `EMAIL_NAO_ENCONTRADO`. Risco aceito: a recuperação revela, pela mensagem e pelo tempo de resposta, se um e-mail está cadastrado, enquanto o requisito vigorar. O usuário declarou ciência de que intervalo de reenvio, limite de tentativas e eventual limitação de requisições não eliminam essa divulgação | M16 (item 2) | Opus |
| 2026-10-13 | **DEC-MV-11** | Conforme o dossiê §4.3, R11.1 a R11.10: validade de 10 minutos, 5 tentativas inválidas por emissão, intervalo de 60 segundos, código de 8 dígitos ASCII e token de redefinição limitado à validade da emissão; quinta tentativa inválida com 400 e as seguintes com 429; senhas de 8 a 128 caracteres, sem composição obrigatória nem normalização | M16 (item 3) | Opus |
| 2026-10-13 | **DEC-MV-12** | Conforme o dossiê §4.4: SMTP em thread, dentro da transação e antes do commit, com TLS, timeouts e tratamento de erros do dossiê. Consequências 1 a 6 aceitas, inclusive o recebimento eventual de um código inválido. Fila, outbox e retry automático fora do escopo. Aceita ADR-0001 D-15 | M16 (item 4) | Opus |
| 2026-10-13 | **DEC-MV-13** | Nesta versão, só `GET /api/v1/usuarios/me`, sem edição de perfil nem alteração do fuso cadastrado. O usuário declarou ciência de que esse fuso define o “hoje” da conta, inclusive em viagens | M16 (item 5) | Opus |
| 2026-10-13 | **DEC-MV-14 (escopo limitado da F3)** | Conforme o dossiê §4.6: travas de linha da recuperação, proteção da primeira emissão com `INSERT … ON CONFLICT`, ordem de aquisição e isolamento especificados. Aceita ADR-0001 D-05 só nesse item. O restante da decisão continua pendente | M16 (item 6) | Opus |
| 2026-10-13 | Reconciliação documental da F3 | Diffs do dossiê §8: CM-1 e CM-2 (`CLAUDE.md`, só esses trechos), AD-1 a AD-3, AR-1 a AR-10 (com AR-8 revisto), PF-1, PV-1 e MZ-1. Sincronizações do §13.4. Registro de M15 e M16. Estados dos documentos e das decisões, com histórico preservado. ACH-MV-ARQ-015 e 026 a 038 encerrados pelos critérios registrados. Ajustes de consistência listados no dossiê §14.2. Conferência do Prompt F3 com as fontes e os hashes de preparação | M16 (reconciliação) | Opus |
| 2026-10-13 | **Prompt F3: `PRONTO_PARA_ETAPA_A`** | Baseline técnico `91be324c88c5a3f99a49b1b1700963e32ef257e9` preservado. Documentos de preparação com SHA-256 no Prompt F3 §1.2. O hash do prompt vai na mensagem de entrega, e este índice não o registra, para não criar hash circular | M16 | Opus |
| 2026-10-13 | **Fora destas aprovações** | Implementação da F3, que depende do relatório da Etapa A e do “pode implementar”; alterações de código, testes, migrações, configuração, dependências e `.env`; `git add`, commit, push e merge; refresh e gestão de sessões; DEC-MV-21; DEC-MV-14 no restante; DEC-MV-15 a 24, com a DEC-MV-24 pendente para a fase correspondente | M16 | Opus |

## 5. Estado dos gates

| Gate | Estado | Observação |
| --- | --- | --- |
| G0 — Baseline e fontes | **Cumprido** | Fontes lidas e lacunas registradas (`analise` §2). Hashes conferidos novamente em 2026-10-11 |
| G1 — Arquitetura da F1 | **Cumprido** (2026-10-11) | DEC-MV-01 a 05 e DEC-MV-25 aceitas. DEC-MV-26 aprovada depois, na auditoria (M4) |
| G1 — Arquitetura da F2 | **Cumprido** (2026-10-13) | DEC-MV-06, 07 e 08 e ACH-MV-F1-005 (opção A) aprovadas. ADR-0002 aceito e D-09 integral. `CLAUDE.md` atualizado |
| G1 — Arquitetura da F3 | **Cumprido** (2026-10-13) | DEC-MV-09 a 13 e DEC-MV-14 em escopo limitado aprovadas (M16); diffs do dossiê F3 §8 aplicados; `CLAUDE.md` atualizado (CM-1 e CM-2) |
| G1 — demais fases | AGUARDANDO_DECISAO | DEC-MV-14 a 24, conforme `analise` §9 |
| G2 — Prompt Master F1 | **Cumprido**: `PRONTO_PARA_ETAPA_A` (2026-10-11) | §8.5 e §11.1 atualizados depois da reauditoria (P-DOC-01 e 02) |
| G2 — Prompt Master F2 | **Cumprido**: `PRONTO_PARA_ETAPA_A` (2026-10-13) | Baseline `90412ec`. As alterações documentais de preparação estão listadas com SHA-256 no Prompt F2 §1.2. Notas pós-auditoria acrescentadas em §12 e §13 (M13) |
| G2 — Prompt Master F3 | **Cumprido**: `PRONTO_PARA_ETAPA_A` (2026-10-13) | Baseline `91be324`. Documentos de preparação com SHA-256 no Prompt F3 §1.2. Histórico: `BLOQUEADO — AGUARDANDO_DECISAO` de M14 a M16 |
| G3 — Etapa A da F3 | **Pendente** | O usuário envia o Prompt F3 ao Sonnet, só para a Etapa A. A Etapa B depende do relatório e do “pode implementar” |
| G3 — Etapa A da F2 | **Cumprido** (2026-10-13) | Relatório da Etapa A trazido pelo usuário em M11 (divergências D1, D2 e D3, resolvidas pela emenda F2-D1). Revalidação no início da Etapa B em `~/minhavida_evidencias/f2/00_revalidacao.log` |
| G3 — Etapa A da F1 | **Cumprido** (declarado pelo usuário em M3) | O relatório da Etapa A não está arquivado no repositório nem disponível nesta sessão |
| Pré-condição da Etapa B da F1 (ACH-MV-ARQ-019) | **Critério substantivo atendido; encerramento formal pendente** | Commit `bd2b2e0` com exatamente os 22 arquivos de `analise` §3.5, verificado pelo Opus na auditoria e na reauditoria. Os arquivos da F1 têm `mtime` posterior ao commit (19:13:38). Falta anexar o bloco de revalidação do Sonnet (Prompt F1 §1.2, a–e), declarada pelo usuário em M3 |
| Autorização da Etapa B | **Concedida** | F1 e correções (M3 e M6). F2: mensagem ao Sonnet fora desta sessão, confirmada em M13 |
| G4 — Entrega da F1 | **Cumprido** | `ENTREGUE_PARA_AUDITORIA`, duas vezes: a F1 e depois as correções |
| G4 — Entrega da F2 | **Cumprido** (2026-10-13) | `ENTREGUE_PARA_AUDITORIA`. Evidências do Sonnet em `~/minhavida_evidencias/f2/` (27 logs conferidos na auditoria) |
| G5 — Auditoria independente da F1 | Histórico: **`BLOQUEADO`** (auditoria de 2026-10-11, ACH-MV-F1-001 a 003, P2). Atual: **`APROVADO_COM_P3`** (reauditoria de 2026-10-11) | `docs/auditorias/AUDITORIA_F1_FUNDACAO_API.md` e `docs/auditorias/REAUDITORIA_F1_CORRECOES_POS_AUDITORIA.md`. P3 ACH-MV-F1-005, 006 e 007 encerrados em 2026-10-13 (M13), com as evidências da auditoria da F2. O veredito vale só para o objeto do manifesto da reauditoria |
| G5 — Auditoria independente da F2 | **`APROVADO_COM_P3`** (2026-10-13), aceito pelo usuário (M13) | `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md` (SHA-256 `f4c529692d6032a052083375f94fc493ea73c1d6449dacfbe1cc16e266cf1560`). Vale para o objeto do manifesto da auditoria (30 arquivos, relatório §2.2). P3: ACH-MV-F2-001 e 003 encerrados; ACH-MV-F2-002 em acompanhamento |
| G6 — Integração da F1 | **Cumprido** (2026-10-13) | Commit `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`, conferido contra o manifesto final (51/51). Baseline da F2 |
| G6 — Integração da F2 | **Cumprido** (2026-10-13) | Commit `91be324c88c5a3f99a49b1b1700963e32ef257e9`, conferido em 2026-10-13 contra a lista e os manifestos do fechamento (43/43) e da auditoria (30/30). Baseline técnico da F3 |

Pendências:

| Pendência | Fonte | Impacto | Resolução |
| --- | --- | --- | --- |
| Decisões da F3 | Dossiê F3 §4 e §10 | — | **Resolvido** em 2026-10-13 (M16): DEC-MV-09 a 13 e DEC-MV-14 em escopo limitado aprovadas; diffs da §8 aplicados |
| ACH-MV-ARQ-026 a 038 | Dossiê F3 §5.2; `analise` §7 | — | **Encerrados** em 2026-10-13 (M16), com os diffs aplicados e o Prompt F3 liberado. ACH-MV-ARQ-015 também encerrado (DEC-MV-10) |
| ACH-MV-ARQ-019: encerramento formal | `analise` §3.1 e §3.5; reauditoria §4 | Lacuna documental; não afeta o veredito técnico da F1 | Anexar o bloco de revalidação do relatório da F1, ou decisão expressa do usuário |
| ACH-MV-F1-005, 006 e 007 (P3) | Auditoria F1 §8; reauditoria §4 | — | **Encerrados** em 2026-10-13 (M13), com as evidências da auditoria da F2 (relatório §8.6 e §10.2): `alembic/` coberto pelo Ruff e pelo Pyright só com a exceção aprovada; logs literais e preservados; Compose com `--env-file /dev/null` e Alembic só pela API com URL explícita |
| ACH-MV-F2-001 (P3): expectativa de `alembic history` contraditória no Prompt F2 (D4) | Relatório F2 §9 e §10.1 | Só documental | **Encerrado** em 2026-10-13: errata registrada como nota no Prompt F2 §13 (B2) e conferida; o texto original da expectativa foi preservado |
| ACH-MV-F2-003 (P3): plano de fases prescrevia `alembic upgrade --sql` pela CLI | Relatório F2 §10.1 | Risco de leitura do `.env` real | **Encerrado** em 2026-10-13: ficha da F2, item 12, substituída pela orientação via API (B1) e conferida |
| ACH-MV-F2-002 (P3): erratas de procedimento e de contrato no Prompt F2 | Relatório F2 §10.1 | Nenhum no objeto | **Encerrado** em 2026-10-13 (M14), de forma documental: erratas registradas (B3) e as quatro lições aplicadas e verificadas no Prompt F3 (dossiê F3 §11) |
| Estados de rastreabilidade da F2 | Relatório F2 §6 | Divergência só descritiva | **Resolvido** em 2026-10-13 (M14): a matriz registra a comprovação estrutural da F2, e o ACH-MV-ARQ-018 foi encerrado na análise. Histórico: pendência aberta no fechamento da F2 (M13) |
| DEC-MV-24 pendente | REC-MV-029, ACH-MV-ARQ-021 | Não afeta F1 a F4. Bloqueia a F5 | Decidir antes do Prompt Master da F5 |

> **Atualização de 2026-10-13 (M15 e M16).** Revisão dirigida dos rascunhos da F3 (M15). Depois, DEC-MV-09 a 13 e DEC-MV-14 em escopo limitado aprovadas, reconciliação documental aplicada, ACH-MV-ARQ-015 e 026 a 038 encerrados, G1 e G2 da F3 cumpridos e Prompt F3 em `PRONTO_PARA_ETAPA_A` (M16). As notas abaixo são históricas.
>
> **Atualização de 2026-10-13 (M14).** G6 da F2 cumprido (commit `91be324`), que passa a ser o baseline técnico da F3. ACH-MV-ARQ-018 e ACH-MV-F2-002 encerrados. Dossiê da F3 entregue para revisão; Prompt F3 em `BLOQUEADO — AGUARDANDO_DECISAO`; DEC-MV-09 a 13 pendentes. As notas abaixo são históricas.
>
> **Atualização de 2026-10-13 (M11 a M13).** Etapa A, entrega e auditoria da F2 concluídas: G3, G4 e G5 da F2 cumpridos, com `APROVADO_COM_P3` aceito pelo usuário. A emenda F2-D1 e as reconciliações A1 a A4 e B1 a B5 do relatório da F2 foram incorporadas. ACH-MV-F1-005 a 007, ACH-MV-F2-001 e ACH-MV-F2-003 encerrados; ACH-MV-F2-002 em acompanhamento. G6 da F2 pendente até o commit do usuário. As notas abaixo são históricas.
>
> **Atualização de 2026-10-13 (M9 e M10).** G6 da F1 cumprido (commit `90412ec`), ACH-MV-ARQ-006 encerrado, G1 e G2 da F2 cumpridos. Os P3 ACH-MV-F1-005 a 007 seguem em acompanhamento.
>
> **Atualização de 2026-10-13 (M7 e M8).** A P-DOC-07 atualizou §1, §2, §6 e §7 deste índice, o cabeçalho do Prompt F1 e o `plano_fases_api.md`, que agora estão coerentes com esta §5. A P-DOC-06 corrigiu o comando do Compose no Prompt F1 §14, passo 10. Assim, a resolução do ACH-MV-F1-007 indicada na tabela de pendências já foi aplicada ao Prompt F1. O achado segue P3 em acompanhamento até os próximos prompts adotarem o mesmo comando. Histórico: em 2026-10-11, após a reauditoria, §1, §2, §6 e §7 ficaram desatualizadas por estarem fora do escopo de M6, e esta §5 era a fonte dos estados vigentes.

## 6. Autoverificação dos critérios de aceite da sessão (F0)

| Critério | Situação | Evidência |
| --- | --- | --- |
| Fontes efetivamente lidas. Ausências e truncamentos declarados | Atendido | `analise` §1, §2, §2.2 (linhas 3, 10 e 12 do `CLAUDE.md`; anexos ausentes) |
| Baseline separado de propostas e decisões | Atendido | Legenda OBSERVADO / EXIGIDO / PROPOSTO / NÃO VERIFICADO. `analise` §3. Hashes abreviados de §3.2 corrigidos (ACH-MV-ARQ-023). Conteúdo do commit de baseline em §3.5 |
| INT/UUID com proposta concreta, impacto e gate | Atendido | ADR-0002 (diff de 32 colunas). DEC-MV-06. Gate F2 |
| Stack alvo e “service sem commit” refletidos | Atendido | ADR-0001 D-04 (aceita). Arquitetura §5. Prompt F1 §0 e §8.2 |
| Telas 1–11 e contrato rastreados até fase e teste | Atendido | `matriz_requisitos_api.md`, inclusive o escopo financeiro (ESC-FIN-1 a 5) |
| Decisões da F1 fechadas ou bloqueando a liberação | Atendido | DEC-MV-01 a 05 e 25 aprovadas. Prompt F1 em `PRONTO_PARA_ETAPA_A` |
| Nenhuma fase depende silenciosamente de capacidade futura | Atendido | `plano_fases_api.md` §1 e §2 (F6 sem `importancia_id`; F8 aditiva). Dependência da F5 em DEC-MV-24 explicitada |
| Operações críticas com fronteira, mecanismo e resultado | Atendido | Arquitetura §6.6 (15 corridas com CT) |
| Política de testes direcionados, sem gatilho de suíte completa | Atendido | `plano_validacao` §2. `task test` proibido |
| Modo Cloud preserva a auditoria local e o merge pelo usuário | Atendido | `plano_validacao` §10. Prompt F1 §0 |
| Auditoria com evidência real, sem alterar o objeto e sem correções pelo auditor | Atendido | `plano_validacao` §9. Ruff `--no-fix` (ACH-MV-ARQ-008) |
| Sem instruções contraditórias vigentes simultaneamente | Atendido, com ressalvas | Prompt anterior SUSPENSO. Diffs do `CLAUDE.md` pendentes (até lá o `CLAUDE.md` prevalece). Conflito D-02 × §2.2 entre textos aceitos, com regra provisória de precedência (§3) e decisão pendente (DEC-MV-24) |
| Severidade aplicada sem redução para liberar fase | Atendido | ACH-MV-ARQ-019 mantido em P2 e ABERTO, sem exceção registrada (REC-MV-031 e 032) |
| Baseline sem credenciais no histórico | Atendido na orientação | `analise` §3.5: lista explícita de 22 arquivos, `compose.yaml` fora. Orientação anterior corrigida (ACH-MV-ARQ-024). Execução pendente do usuário |
| Etapa A sem commit e Etapa B bloqueada, sem contradição | Atendido | Prompt F1 §1.1, §1.2 e §14, passo 0 (revalidação do baseline) |
| Nada implementado. Nenhum teste apresentado como executado | Atendido | Somente arquivos em `docs/` e o Prompt Master F1. Todos os testes estão PLANEJADOS. Nenhum `git add` ou commit executado |

Verificação documental (não é teste de implementação), refeita em 2026-10-11 após a aprovação de DEC-MV-25:

- Todos os IDs CT, DEC, REC, ACH e ESC-FIN citados existem no documento de origem (173 CTs, 25 DECs, 32 RECs, 25 ACHs e 5 ESC-FIN).
- **Conferência em 2026-10-13 (liberação da F3, M16):** CTs passam a 182 (CT-F3-22 a 24 e 26 a 29 acrescentados pelo PV-1). DEC (26), REC (34), ACH-MV-ARQ (38) e ESC-FIN (5) sem mudança de contagem. IDs citados nos documentos alterados e no Prompt F3 conferidos contra a origem; referências `§` da arquitetura citadas pelo Prompt F3 conferidas contra os títulos; cercas balanceadas; tabelas com colunas coerentes. `CLAUDE.md` alterado só nas linhas de CM-1 e CM-2.
- **Conferência em 2026-10-13 (preparação da F3, M14):** ACH-MV-ARQ passam a 38 (026 a 038 novos, em `analise` §7). CT, DEC e REC sem mudança de contagem: os CTs novos da F3 são só propostas no dossiê (IDs livres CT-F3-22 a 24 e 26 a 29). IDs citados nos documentos alterados conferidos contra a origem; cercas balanceadas.
- **Conferência em 2026-10-13 (fechamento documental da F2):** os achados ACH-MV-F2-001 a 003 estão em `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`. Nos documentos normativos não resta prescrição de `inserir_categorias`, `op.get_bind()` ou `alembic upgrade --sql` pela CLI. Cercas balanceadas nos documentos alterados. CT, DEC e REC sem mudança de contagem.
- **Contagem atualizada em 2026-10-13 (preparação da F2):** RECs passam a 34 (REC-MV-033 e 034). CTs (175), DECs (26) e ACH-MV-ARQ (25) não mudaram. CT-F2-20 deixou de ser condicional.
- **Contagem atualizada em 2026-10-13 (P-DOC-07):** 175 CTs (CT-F1-21 e 22 acrescentados pela P-DOC-04) e 26 DECs (DEC-MV-26). RECs (32), ACH-MV-ARQ (25) e ESC-FIN (5) não mudaram. Os 263 IDs desses tipos citados em `docs/` e nos dois Prompts da F1 existem na origem. Os achados ACH-MV-F1-001 a 007 estão nos relatórios de `docs/auditorias/`.
- Todas as referências `§` da arquitetura existem. As referências `§` entre documentos (análise, índice, planos, ADRs e Prompt F1) foram conferidas contra os títulos de seção.
- Cercas de código balanceadas em todos os documentos.
- Nenhuma credencial do `compose.yaml` reproduzida nos documentos.
- A convenção de nomes tem os mesmos cinco padrões na arquitetura §10.1, no ADR-0001 D-09 e no Prompt F1 §6.
- A lista de 22 arquivos de `analise` §3.5 corresponde aos arquivos não ignorados do repositório, menos `compose.yaml` e `__pycache__/`.
- O nome antigo da F8 só aparece como registro histórico: `plano_fases_api.md` §1 e REC-MV-028.
- Arquivos protegidos (`CLAUDE.md`, prompt anterior, código e configuração) com os hashes do baseline.

## 7. Próxima ação do usuário

Atualizado em 2026-10-13 (liberação da F3, M16). Histórico: a lista anterior, da preparação da F3, foi cumprida com as decisões da M16.

1. Opcional, antes de enviar: commit documental, com lista explícita, dos documentos do Prompt F3 §1.2 (modo B). Sem commit, o Sonnet usa o modo A.
2. Enviar `PROMPTS/PROMPT_MASTER_SONNET_5_F3_IDENTIDADE_ACESSO.md` ao Sonnet com o SHA-256 da mensagem de entrega, autorizando **somente a Etapa A**.
3. Trazer o relatório da Etapa A. A Etapa B depende do seu “pode implementar”.
4. Antes da F5: decidir DEC-MV-24. Opcional: encerrar formalmente o ACH-MV-ARQ-019 e restaurar as linhas truncadas do `CLAUDE.md` (ACH-MV-ARQ-012).
