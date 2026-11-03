# Prompt Master — Opus 5.5 — Auditoria independente da F3: Identidade e acesso

| Campo | Valor |
| --- | --- |
| Projeto | API MinhaVida — Gestão pessoal e finanças |
| Papel | Engenheiro de Software Principal / auditor independente |
| Trabalho autorizado | Auditar a F3 entregue pelo Sonnet, produzir evidências e emitir veredito |
| Estado informado da entrega | ENTREGUE_PARA_AUDITORIA |
| Ambiente | LOCAL, WSL2 Ubuntu, repositório do usuário |
| Baseline técnico | `91be324c88c5a3f99a49b1b1700963e32ef257e9` — F2 concluída |
| Data desta instrução | 2026-10-13 |
| Saída principal | `docs/auditorias/AUDITORIA_F3_IDENTIDADE_ACESSO.md` |

Você é o auditor independente da implementação da F3. Examine o objeto real entregue e reproduza as verificações necessárias. O relatório do Sonnet é uma fonte de alegações a conferir, não uma prova suficiente de correção.

O fato de você ter escrito a arquitetura, o Prompt Master ou a emenda não lhes confere presunção de correção. Identifique também falhas de especificação, com origem e impacto separados dos defeitos de implementação.

Esta mensagem autoriza a auditoria, os testes direcionados, as sondas externas necessárias e a redação do relatório. Não autoriza corrigir a aplicação, editar suas fontes normativas, aprovar novas decisões arquiteturais, fazer commit ou iniciar a F4.

## 0. Regras absolutas

1. Preserve código, testes, modelos, migrações, configuração, dependências, lockfile e documentos recebidos. Auditor não implementa correções no objeto auditado.
2. No repositório, a única nova saída autorizada desta auditoria é o relatório indicado no cabeçalho. Evidências, scripts de sondas e cópias descartáveis ficam fora do repositório.
3. Se o relatório já existir, preserve-o. Identifique se esta é uma retomada; caso seja uma nova execução, use um nome com sufixo explícito e informe o caminho efetivo. Não sobrescreva histórico.
4. Não execute `git add`, commit, push, merge, reset, stash, restore, checkout destrutivo, clean ou amend. Não limpe nem reorganize a entrega.
5. Nunca leia, copie, imprima, altere ou calcule hash do `.env` real. Não faça dumps de ambiente. `.env.exemplo` pode ser inspecionado.
6. Não instale nem atualize dependências. Não execute `uv add`, `uv sync`, `uv lock` ou equivalentes. Use o ambiente entregue com `uv run --frozen --no-sync`.
7. Não execute Ruff com correção nem formatação com escrita sobre o objeto. Use `ruff check --no-fix` e `ruff format --check`.
8. Não execute automaticamente a suíte completa, `pytest` sem seleção, `task test` ou tarefas agregadoras. A seleção desta auditoria está na §10.
9. Use PostgreSQL real e descartável para os testes de banco e concorrência. Não substitua por SQLite nem por mocks de transação ou de travas.
10. Não conecte a banco de desenvolvimento/produção nem a SMTP real. Não envie e-mails reais. Testes usam dados sintéticos e os substitutos de e-mail previstos no contrato.
11. Na CLI do Alembic, somente `alembic heads`. Não execute comandos que carreguem `alembic/env.py`, como upgrade, downgrade, check ou geração de SQL pela CLI. A F3 não cria migração.
12. Não execute Docker Compose nesta auditoria. Testcontainers pode criar e remover somente os recursos descartáveis desta execução.
13. Não altere expectativas, timeouts, markers, fixtures ou seleções para fazer um resultado passar. Registre a falha real.
14. Não exponha senha, código, JWT, token de redefinição, hashes de credenciais ou dados pessoais reais. Use sentinelas sintéticas nas sondas de vazamento.
15. Não refaça F1/F2 por padrão, não gere Prompt F4 e não acrescente funcionalidades de fases futuras.
16. Qualquer mutação experimental, correção candidata ou teste adicional de auditoria deve ocorrer em cópia externa identificada. Um resultado nessa cópia não aprova o objeto original.

## 1. Objeto, versões e estado de partida

Raiz esperada, a confirmar por leitura:

`/home/jose/projects/app_gestão_pessoal/API`

### 1.1. Fontes operacionais congeladas

| Fonte | Caminho | SHA-256 esperado |
| --- | --- | --- |
| Prompt implementado | `PROMPTS/PROMPT_MASTER_SONNET_5_F3_IDENTIDADE_ACESSO.md` | `c976854dc82f98229f87125878fd1447a42665e51a96f22ad04dc7209bc83536` |
| Emenda aprovada F3-E1 | `~/minhavida_evidencias/f3_emenda_8NC4DtlF/EMENDA_F3_E1.md` | `9b3ae10b8f64c5df16bfa4118fd98a24e9f9d05ff850f3b6b5a0769e346ca103` |

Leia a emenda integralmente. Ela prevalece somente nos pontos que modifica. O arquivo original do Prompt F3 permaneceu congelado de propósito.

Não use os antigos rascunhos bloqueados da F3 nem o prompt da F2 como contrato da implementação atual. Não substitua uma fonte divergente silenciosamente por uma versão da memória.

### 1.2. Evidências do implementador

Leia os arquivos reais, sem modificá-los:

- `~/minhavida_evidencias/f3/RELATORIO_ETAPA_A.md`;
- `~/minhavida_evidencias/f3/RELATORIO_ETAPA_A_E1.md`;
- `~/minhavida_evidencias/f3/RELATORIO_ETAPA_B.md`;
- `~/minhavida_evidencias/f3/etapa_a_verificacoes.log`;
- `~/minhavida_evidencias/f3/etapa_a_e1_verificacoes.log`;
- logs de execução e reexecução referenciados no relatório da Etapa B, inclusive passo 0, comparação do lock e `17c_sha256_f3.log`;
- `~/minhavida_evidencias/f3_sha256_logs.txt`;
- evidências e manifesto pertinentes de `~/minhavida_evidencias/f3_emenda_8NC4DtlF/`.

Se algum caminho não existir, registre a ausência. Não invente seu conteúdo nem procure substitutos por glob ambíguo. Não confunda uma reprodução feita agora com o log original da implementação.

### 1.3. Estado informado — verificar, não presumir

- Modo A: HEAD no baseline da F2, F3 implementada na working tree e ainda sem commit.
- Preparação documental autorizada: 11 documentos, conforme §1.2 do Prompt F3 e relatório da Etapa A.
- A Etapa A complementar registrou 37 hashes coincidentes e o hash da emenda.
- A Etapa B relata 34 CTs, dos quais 10 de concorrência; 110 testes aprovados em `tests/identidade` e 26 regressões aprovadas.
- Gate informado: Ruff limpo, 76 arquivos formatados, Pyright sem erros/avisos e Alembic com `0001 (head)`.
- Dependências: cinco entradas diretas autorizadas; nenhuma versão anterior alterada e nenhum pacote anterior removido.
- O Sonnet informa 14 novos arquivos de produção, 12 em `tests/identidade/`, auxiliares adicionais, alterações de fixtures e supressões temporárias removidas.

Essas contagens não são premissas de aprovação. Reconstrua inventário, cobertura e resultados por evidência.

## 2. Fontes normativas e precedência

Leia e registre caminho e hash das versões efetivamente usadas:

1. Esta instrução de auditoria e as autorizações explícitas pertinentes do usuário: aprovação das decisões da F3, aprovação da Emenda F3-E1 e autorização da Etapa B.
2. `CLAUDE.md`: diretrizes; telas 1, 2, 3 e 4.1.1; tabelas `usuario` e `recuperacao_senha`.
3. `docs/arquitetura/indice.md`: precedência, aprovações, gates e pendências.
4. `docs/adr/0001_arquitetura_api_minhavida.md`, especialmente D-02, D-04, D-05 no alcance da F3, D-07, D-08, D-13 e D-15; e `docs/adr/0002_identificadores_uuid.md`.
5. `docs/arquitetura/arquitetura_api_minhavida.md`: módulos, configuração, erros, transações, concorrência, tempo, identidade, recuperação e segurança.
6. `docs/arquitetura/preparacao_f3_identidade_acesso.md`, incluindo a liberação documental.
7. `docs/arquitetura/plano_validacao_auditoria.md`, `plano_fases_api.md` e `matriz_requisitos_api.md`, nas partes aplicáveis à F3.
8. Prompt F3 congelado e Emenda F3-E1, com os hashes da §1.1.
9. Relatórios, logs e objeto técnico entregue.

Respeite a precedência vigente no índice e o alcance das aprovações. A emenda aprovada pelo usuário é a exceção expressa aos pontos anteriores que ela substitui; não é autorização geral para mudar contratos.

Não interprete a ausência dos CT-F3-31 a 34 nos documentos ainda congelados como desobediência do implementador: esses IDs e as mudanças da E1 foram aprovados, com reconciliação documental posterior prevista. Uma divergência fora desse alcance deve ser analisada normalmente.

## 3. Decisões preservadas e limites de escopo

Estão aprovadas para esta entrega DEC-MV-09 a 13 e DEC-MV-14 somente no escopo da recuperação da F3. A DEC-MV-24 continua vinculada à F5; a DEC-MV-21 não foi aprovada nesta fase.

Audite a solução aprovada, incluindo:

- JWT HS256, validade padrão de 24 horas, sem refresh e com logout somente no cliente;
- invalidação dos tokens anteriores após troca de senha, conforme `sv`;
- Argon2id e limitador de hashes previstos no contrato;
- resposta explícita de e-mail inexistente da opção A da DEC-MV-10, com risco de enumeração aceito;
- SMTP dentro da transação, antes do commit, com as consequências documentadas;
- consulta do usuário atual, sem edição de perfil ou fuso;
- coordenação de recuperação com travas de linha e unicidade; sem trava consultiva por usuário da F4;
- services podem fazer flush, mas não commit; fronteiras transacionais nos routers;
- nenhum service importa outro service na F3, conforme D-02;
- finanças manuais e ausência de integrações financeiras externas.

Não reproponha refresh, sessões, fila/outbox, limitação de login, alteração de esquema ou edição de perfil apenas porque escolheria outra arquitetura. Se identificar um defeito novo e concreto além das limitações já aceitas, registre-o com evidência e impacto.

## 4. Congelamento e identificação do objeto auditado

Antes dos testes:

1. Registre raiz real, HEAD, branch, estado do índice e `git status --porcelain --untracked-files=all`, sem operações de escrita no Git.
2. Compare a entrega com o baseline técnico e com o estado posterior às Etapas A/A-E1.
3. Separe três conjuntos:
   - preparação documental aprovada, comparada aos hashes da liberação/Etapa A;
   - arquivos técnicos da F3, comparados à lista permitida e ao manifesto da Etapa B;
   - arquivos protegidos, comparados às referências que efetivamente lhes correspondem.
4. Não exija os hashes antigos nos arquivos cuja alteração técnica foi autorizada na F3. Não exija que a preparação documental ainda seja igual ao commit da F2.
5. Compare a lista completa de novos/modificados/removidos com o §7 do Prompt e a E1. `git diff` sozinho não cobre arquivos não rastreados: inspecione-os explicitamente.
6. Gere manifesto inicial dos arquivos relevantes do objeto, incluindo os novos arquivos e as fontes normativas. Nunca inclua o `.env` real, ambientes virtuais, caches ou outros segredos.
7. Ao final, repita a conferência de conteúdo, lista de caminhos, HEAD e índice. As únicas novas saídas esperadas no repositório são o relatório desta auditoria e, se o usuário tiver salvo ali este prompt de entrada, esse documento identificado como tal.

Não exija working tree limpa: a implementação está intencionalmente sem commit. Diferencie esse estado de uma alteração acidental feita durante a auditoria.

Se detectar que a auditoria modificou o objeto, interrompa as operações que escrevem, registre o delta e informe o usuário. Não restaure silenciosamente a cópia auditada nem emita aprovação de uma versão diferente da examinada.

## 5. Alegações específicas do Sonnet que exigem exame

### 5.1. Arquivos e auxiliares adicionais

Confronte os 14 novos arquivos em `src/` informados com a lista real autorizada do Prompt congelado. Identifique cada caminho e sua finalidade; não presuma que um arquivo extra está autorizado por ser pequeno ou útil.

Examine também os auxiliares de testes e o carregamento/agregação de fixtures no `conftest` da F3:

- estão em arquivos permitidos e dentro do conteúdo autorizado?
- preservam escopo, limpeza, isolamento, overrides e coleta?
- criam dependências entre pacotes de testes ou efeitos globais não previstos?
- apenas decompõem funções, ou alteram o contrato para contornar o limite de parâmetros?
- escondem assertions, skips, parametrizações removidas ou o uso de recursos reais?

Distinga liberdade de implementação dentro de pseudocódigo, alteração de bloco de conteúdo exato e ampliação de arquivos/arquitetura. Classifique segundo o contrato, sem conceder autorização retroativa.

### 5.2. Supressões e histórico de validação

Leia a frase completa sobre `# noqa` e `# pyright: ignore` no relatório em arquivo, pois o resumo da conversa está truncado.

Compare o estado final com o baseline e verifique supressões novas, configurações enfraquecidas e mudanças em regras de lint/tipagem/testes. Uma supressão preexistente em `settings.py` não é um desvio novo.

Reconstrua, até onde os logs permitem, a sequência de falhas, correções e reexecuções: teste do limitador, Ruff, erros `LiteralString` e gates finais. Confirme que a versão final foi efetivamente validada após a última alteração relevante.

Separe:

- o que está comprovado no objeto final;
- o que consta apenas do relato do implementador;
- eventual infração processual demonstrada;
- histórico impossível de reconstruir.

Não use apenas mtime ou narrativa para afirmar que uma supressão nunca foi executada. Ausência de evidência histórica não equivale automaticamente a defeito funcional, mas também não pode ser declarada como conformidade comprovada.

### 5.3. Seleção de testes

A ausência de execução de `tests/esquema` e `tests/infra/test_alembic_ambiente.py` não é, por si, falha: o §14 definiu regressões direcionadas. Confira esse alcance no prompt efetivamente implementado.

Se uma alteração compartilhada de fixture ou configuração introduzir risco concreto nesses arquivos, identifique o risco e selecione somente os testes diretamente afetados. Não transforme isso em nova auditoria geral da F2.

## 6. Auditoria funcional, de identidade e segurança

Construa a rastreabilidade CT → requisito → implementação → node IDs → resultado. Os 34 CTs não equivalem necessariamente a 34 itens do pytest; parametrizações devem ser contabilizadas corretamente.

### 6.1. HTTP e validação

Confira os seis endpoints previstos: registro, login, solicitar código, verificar código, redefinir senha e `GET /api/v1/usuarios/me`.

Verifique métodos, prefixos, status, campos exatos, mensagens, códigos de erro, `WWW-Authenticate`, `Retry-After` e `Cache-Control: no-store` onde exigidos. Confirme que rotas exclusivas de teste não são incluídas na aplicação real.

Examine:

- `_data_civil`: formato ASCII `AAAA-MM-DD`, data existente, rejeição de datetime/números/coerções indevidas e distinção entre ausência e valor inválido;
- nascimento futuro segundo o relógio e fuso aprovados;
- nome aparado, limites e caracteres de controle;
- representação canônica do e-mail, coerente entre persistência, unicidade, login, recuperação e destinatário SMTP;
- domínios internacionalizados e rejeição da parte local não ASCII, conforme R9.9;
- caminho de e-mail malformado no login conforme contrato, sem criar respostas diferenciadas não autorizadas;
- senha de 8 a 128 caracteres nos fluxos aplicáveis, sem trim, normalização silenciosa ou composição obrigatória;
- confirmação de senha e ausência de persistência de senha em claro ou confirmação.

### 6.2. JWT, credenciais e contexto

Verifique a biblioteca realmente instalada e a chamada real de encode/decode; use código/documentação primária se uma dúvida de API exigir confirmação.

Comprove a verificação de assinatura com algoritmo fixo e as claims previstas (`sub`, `iat`, `exp`, `typ`, `sv`), seus tipos e formatos, limites temporais, rejeição de booleanos onde exigido inteiro e rejeição de claims não permitidas.

Confirme que desabilitar a validação temporal da biblioteca está compensado integralmente pela validação contratada com `Relogio`. Não aceite uma assinatura válida como prova de token temporalmente válido.

Verifique usuário inexistente, `sv`, comparação adequada, invalidação após redefinição, segredo mínimo e placeholders recusados. Confira os limites exatos de `iat`/`exp` e validade máxima aprovada.

No hasher, examine parâmetros, execução fora do event loop, limitador dedicado, hash fictício, tratamento de hash armazenado inválido e ausência de rehash no login. O teste de concorrência do limitador precisa medir execuções simultâneas, não apenas chamadas concluídas.

Tokens iguais emitidos com relógio fixo e claims iguais não constituem defeito por si. Não exija `jti`, aleatoriedade adicional ou desigualdade de tokens sem previsão contratual.

### 6.3. Recuperação e atomicidade

Confira a ordem real de decisões e suas fronteiras transacionais:

- código ASCII de oito dígitos, zeros à esquerda preservados, geração criptográfica e armazenamento como hash;
- dez minutos, cinco tentativas inválidas por emissão e sessenta segundos entre emissões;
- relógio capturado no ponto definido, especialmente após espera de trava;
- reenvio anulando código, token, verificação e uso anteriores, e zerando tentativas;
- quinta inválida com 400 e persistência de `tentativas`; seguintes com 429, conforme os demais estados e sua precedência;
- sucesso de verificação emitindo o token uma única vez; repetição conforme o contrato;
- token de redefinição armazenado como hash, com validade herdada da mesma emissão;
- redefinição atualizando senha e uso de token atomicamente;
- rollback em falhas, sem commits escondidos em services, helpers ou handlers;
- retorno de erro de negócio depois do commit necessário para conservar a tentativa inválida;
- comportamento de falha no commit após o envio já realizado, sem prometer reversão do e-mail.

Confira o SQL executado e o alvo das travas, inclusive consultas com joins. Não presuma que `with_for_update()` trava somente a tabela desejada. Investigue ampliação de travas, inversão de ordem ou deadlock concreto contra o mecanismo aprovado, sem modificar o objeto.

### 6.4. E-mail, configuração e ausência de vazamento

Verifique assunto/corpo contratados, destinatário canônico, modos SMTP, TLS e validação de certificado/nome, timeout por operação, autenticação permitida e encerramento das conexões.

Simule falhas do SMTP; não use credenciais nem rede SMTP reais. Verifique tradução de exceções, cadeia de exceções e logs formatados, para que mensagens do driver ou servidor não exponham dados.

Inspecione respostas e todos os canais de logging relevantes, incluindo handlers efetivos, traceback/exception chaining e formatação. Conferir só `getMessage()` ou só `caplog` não basta se outro canal puder incluir dados.

Use sentinelas sintéticas de nome, e-mail, senha, código e tokens. Distinga os campos de resposta explicitamente autorizados de vazamentos em erros/logs. Não classifique um token no campo de sucesso previsto como vazamento.

Verifique `SettingsTeste`: fontes externas excluídas e arquivo `.env` real não aberto. Confirme produção versus testes, validações de segredo/fuso/Argon2/SMTP e ausência de I/O no import, conforme os CTs e regressões aplicáveis.

## 7. Emenda F3-E1 — conferência obrigatória

Leia E1.1 a E1.5 no arquivo cujo hash foi informado. Não audite apenas o resumo abaixo.

| Item | O que precisa ser comprovado |
| --- | --- |
| E1.1 / D1 | Chamada de `Settings` corrigida com segredo sintético explícito; preservação das verificações de ambiente/dotenv sintético e da independência de `settings_teste`; `EMAIL_MODO` conforme emenda; Pyright limpo sem nova supressão |
| CT-F3-31 / C3 | Dois reenvios realmente concorrentes: vencedor 200, perdedor 429 e `Retry-After` contratual; somente a emissão vencedora altera o estado e gera/envia o novo código, conforme assertions da emenda |
| CT-F3-32 / C6 | Ambas as ordens com quatro tentativas prévias: inválida antes leva a 400/429 e contador 5; correta antes leva a 200/409 e contador 4; estado de verificação/token coerente |
| CT-F3-33 / C10 | Redefinição efetivamente esperando no UPDATE de usuário; login/leitura continuam no comportamento sem trava previsto; tokens antigos rejeitados depois do commit, mesmo quando os tokens produzidos no relógio fixo sejam iguais |
| E1.3 / CT-F3-34 | Sessão do banco em fuso diferente de UTC; resposta normalizada para UTC com `Z`, mantendo o mesmo instante; datetime sem fuso tratado como defeito, sem conversão implícita pelo fuso local |
| E1.4 | Tratamento tipado de unicidade e orientações de prazo/503 respeitados, sem supressões nem aumento de timeouts |
| E1.5 | Evidências da Etapa A complementar e revalidação da emenda antes da implementação |

No CT-F3-34, prove que o override incide na sessão usada pela requisição; uma sessão separada com outro fuso não comprova o caso. Confira restauração/isolamento do override e das configurações de sessão.

## 8. Concorrência: evidência real

Os dez CTs de concorrência previstos precisam executar. Faça o mapeamento a partir do contrato e da E1, incluindo CT-F3-05, 14, 15, 17, 19, 23, 27, 31, 32 e 33.

Para cada cenário, confira:

1. Requisições independentes, com sessões/conexões independentes.
2. Bloqueadora e monitor identificados; consulta de espera filtrada pela operação e contagem exata definida.
3. Todas as requisições necessárias efetivamente aguardando antes da liberação. No CT-F3-15, são cinco; duas não bastam.
4. Ordem controlada onde a emenda exige as duas ordens, sem depender apenas de `sleep`, ordem de criação das tarefas ou velocidade da máquina.
5. Resultado HTTP e estado persistido conferidos por outra conexão, não pelo identity map de uma sessão usada no fluxo.
6. Nenhuma tarefa esquecida, exceção descartada, timeout ampliado ou 503 aceito no lugar do resultado contratual.
7. Cancelamento/fechamento de tarefas, conexões e bloqueadoras em falhas, conforme o apoio dos testes.

Execute sondas independentes focadas se a inspeção e os testes entregues não demonstrarem efetivamente um desses requisitos. Identifique-as como sondas de auditoria, sem criar novos CTs normativos silenciosamente.

Não use repetições indefinidas até passar. Se houver flake, registre a primeira falha, isole o cenário e explique por que uma repetição é necessária. Preserve todas as saídas.

## 9. Dependências, integridade do esquema e operação

Compare `pyproject.toml` e `uv.lock` com os blobs do baseline da F2, além dos logs do passo 2.

- Verifique as cinco dependências diretas autorizadas: `argon2-cffi`, `pyjwt`, `tzdata`, `email-validator` e `anyio`.
- Diferencie novas entradas diretas de pacotes que já existiam transitivamente.
- Confira versões anteriores preservadas, ausência de remoções indevidas, novos pacotes transitivos, mudanças de marcadores autorizadas e coerência com o ambiente instalado.
- Não instale nada para ocultar discrepância entre ambiente e lock.
- Confira que modelos, migração 0001, `alembic/env.py`, `database.py` e demais protegidos conservam seus contratos e conteúdo esperado.
- Confirme `0001 (head)` e ausência de nova revisão.
- Inspecione `.env.exemplo` sem acessar o `.env` real. Necessidade de o usuário preencher segredo/SMTP é orientação operacional; não preencha por ele.

Não execute migrações de desenvolvimento. Se houver risco concreto na integração das fixtures com a migração, use somente o mecanismo de teste já aprovado, com URL descartável explicitamente fornecida e sem carregar configuração real.

## 10. Execução da auditoria e política de testes

### 10.1. Sequência

1. Identifique o objeto, congele manifestos e leia as fontes.
2. Leia o relatório completo e valide seus logs/manifestos.
3. Inspecione o diff, os novos arquivos e os mecanismos de isolamento antes de executar código.
4. Registre um plano curto de execução e os riscos concretos que cada seleção verifica.
5. Colete e execute a seleção da F3; execute as quatro regressões indicadas abaixo.
6. Faça somente as sondas complementares que resolvam questões concretas de cobertura/correção.
7. Execute Ruff, formatação em modo check, Pyright e Alembic heads.
8. Feche os manifestos e o veredito; só então escreva o relatório no repositório.

Não transforme a auditoria em outra implementação. Uma falha não autoriza corrigir o objeto para continuar. Você pode prosseguir nas verificações independentes seguras para entregar um relatório completo, preservando o resultado impeditivo.

### 10.2. Comandos mínimos de validação

Execute na raiz confirmada, registrando os comandos literais e os códigos reais. Para evitar bytecode novo no objeto, defina `PYTHONDONTWRITEBYTECODE=1` no ambiente dos processos de auditoria.

```bash
uv run --frozen --no-sync pytest tests/identidade --collect-only -q --color=no -p no:cacheprovider

uv run --frozen --no-sync pytest tests/identidade -vv --color=no -p no:cacheprovider

uv run --frozen --no-sync pytest tests/infra/test_configuracao.py tests/infra/test_erros.py tests/infra/test_saude.py tests/infra/test_sessao_transacao.py -vv --color=no -p no:cacheprovider

uv run --frozen --no-sync ruff check --no-fix --no-cache .
uv run --frozen --no-sync ruff format --check --no-cache .
uv run --frozen --no-sync pyright
uv run --frozen --no-sync alembic heads
```

O esperado informado é 110 aprovações na fase e 26 nas regressões. Apure a coleta real e explique qualquer diferença; não ajuste testes para atingir esses números. Registre skips, xfails, warnings e erros de coleta em vez de escondê-los.

Os dez CTs de concorrência já integram `tests/identidade`: não execute automaticamente a mesma bateria novamente apenas para ter um segundo log. Se precisar de seleção adicional, documente o motivo e os node IDs.

### 10.3. Expansão e falhas

Ao encontrar falha, isole o teste/sonda relevante e preserve o primeiro resultado. Não repita baterias grandes nem corrija o repositório.

Para ampliar regressões, registre antes: arquivo compartilhado alterado, comportamento potencialmente afetado, seleção adicional mínima e resultado que distinguirá a hipótese.

A suíte completa é exceção e não está autorizada automaticamente. Caso a considere indispensável, apresente antes da execução:

```text
OBJETIVO DA SUÍTE COMPLETA:

POR QUE OS TESTES DIRECIONADOS NÃO SÃO SUFICIENTES:

MUDANÇAS QUE JUSTIFICAM A EXECUÇÃO:
```

Não use “para garantir”, “por segurança” ou “porque terminou” como justificativa. Sem uma justificativa concreta nos três campos, mantenha as seleções direcionadas. Preserve as eventuais exigências de autorização já existentes nas fontes normativas, sem criar uma nova etapa de aprovação por conta própria.

## 11. Evidências, sondas e comandos verificáveis

Crie um diretório exclusivo de evidências fora do repositório, por exemplo usando:

```bash
F3_AUD_EVID=$(mktemp -d "$HOME/minhavida_evidencias/f3_auditoria_XXXXXXXX")
```

Registre o caminho absoluto retornado. Nos comandos seguintes, use exatamente esse diretório, inclusive se cada chamada de shell exigir declará-lo de novo. Não o redescubra com `ls .../f3_auditoria_*` ou outro glob que possa selecionar várias sessões.

Cada execução deve preservar: comando, diretório de trabalho, fonte/versão relevante, stdout/stderr, código de saída e nome único do log. Capture `$?` imediatamente após o comando. Não substitua falha pelo status bem-sucedido de `tee`, `grep`, `echo` ou do último estágio de um pipeline.

Exemplo de captura, com o diretório já resolvido:

```bash
uv run --frozen --no-sync pytest tests/identidade -vv --color=no -p no:cacheprovider > "$F3_AUD_EVID/05_pytest_identidade.log" 2>&1
f3_aud_codigo=$?
printf '\ncodigo_saida=%s\n' "$f3_aud_codigo" >> "$F3_AUD_EVID/05_pytest_identidade.log"
```

Leia o código registrado antes de avançar. Reexecuções recebem arquivos novos; os logs do Sonnet permanecem intactos.

Se usar um helper de comandos, seu corpo e alvos precisam ser inspecionáveis. Não carregue funções de shell desconhecidas, não use remoções amplas e não misture limpeza com os comandos de validação. Remova apenas recursos descartáveis identificados desta auditoria; preserve evidências e qualquer arquivo do usuário.

Para uma sonda ou mutação externa, registre:

- hipótese e requisito que verifica;
- cópia de origem e hashes correspondentes ao objeto auditado;
- caminho efetivamente importado do pacote, evitando testar por engano a instalação editável do repositório em vez da cópia;
- configuração e dados sintéticos, sem `.env` real;
- resultado do controle e resultado que distingue a falha;
- limites da conclusão.

Sondas com uma correção candidata são propostas de diagnóstico. Deixe explícito que a correção não foi aplicada e que não substitui a aprovação do objeto entregue.

## 12. Reconciliação documental posterior

A incorporação formal da E1 às fontes ficou prevista para depois da auditoria. Nesta sessão, produza no relatório um anexo com as reconciliações necessárias, sem aplicá-las aos documentos congelados.

Confira, conforme o conteúdo real da emenda:

- Prompt F3: nota histórica da E1 e pontos afetados em §8.7, §11.1, §11.3, §12 e §15;
- arquitetura: recuperação, UTC e rastreabilidade de concorrência;
- dossiê: corridas, CT-F3-31 a 34 e registro da emenda;
- plano de validação: catálogo da F3 e contagens verificadas;
- plano de fases: cobertura da ficha F3;
- matriz: tela 3 e recuperação;
- índice: aprovação da emenda, estados, evidências e contagens.

Preserve o texto e hash da versão implementada. Não registre uma aprovação do usuário inexistente, não altere o objeto para eliminar um achado e não encerre pendências sem evidência.

Separe a consolidação de uma emenda já aprovada de uma nova proposta que ainda exige decisão. Pendência documental já prevista não deve ser confundida com ausência de implementação da E1.

## 13. Achados, severidade e critério de veredito

Use as definições P0/P1/P2/P3 e os gates do plano de validação vigente. Não invente severidade só para liberar ou bloquear a fase.

Para cada achado, registre:

| Campo | Conteúdo obrigatório |
| --- | --- |
| ID | `ACH-MV-F3-...`, conferindo antes os IDs disponíveis |
| Severidade e gate | Critério aplicado e se impede aprovação |
| Origem | Implementação, teste, contrato, ferramenta/ambiente ou documentação/evidência |
| Requisito | Documento, seção e alcance da aprovação pertinente |
| Local | Arquivo e linha/função reais |
| Reprodução | Comando, node ID ou sonda, com código de saída |
| Esperado / observado | Diferença concreta |
| Impacto | Consequência e alcance |
| Correção proposta | Menor alteração necessária, sem aplicá-la |
| Revalidação | Seleção dirigida que provará a correção |

Não atribua ao Sonnet uma falha originada no contrato literal sem registrar essa origem. Uma falha de contrato pode continuar impeditiva pelo efeito técnico; origem e severidade são dimensões diferentes.

Não aprove enquanto houver requisito obrigatório sem prova suficiente, teste obrigatório falhando, alteração não autorizada que viole um gate ou achado impeditivo segundo o plano. Não considere uma limitação explicitamente aceita como defeito novo sem evidência adicional.

Use os estados de veredito previstos no projeto, normalmente:

- **APROVADO**: critérios obrigatórios cumpridos, sem pendência impeditiva;
- **APROVADO_COM_P3**: critérios cumpridos e somente pendências não impeditivas identificadas;
- **BLOQUEADO**: falha impeditiva ou verificação obrigatória inviável, com motivo preciso.

Se uma fonte obrigatória ou infraestrutura impedir a auditoria, registre o alcance não verificável. Não converta “não consegui verificar” em “passou”.

## 14. Relatório obrigatório

Produza `docs/auditorias/AUDITORIA_F3_IDENTIDADE_ACESSO.md` com:

1. Veredito e justificativa objetiva.
2. Identificação do objeto: HEAD, modo, estado do Git, fontes e hashes, manifesto técnico e separação da preparação documental.
3. Alcance das aprovações e da Emenda F3-E1.
4. Alegações do Sonnet: comprovadas, contraditas ou não verificáveis.
5. Inventário de arquivos e análise dos auxiliares/supressões relatados.
6. Matriz CT-F3-01 a 34 → requisito → node IDs → resultado/evidência, mais regressões.
7. Evidências de concorrência, transações, JWT, recuperação, SMTP, UTC e não vazamento.
8. Dependências, esquema preservado e gates de qualidade.
9. Falhas intermediárias e limites da reconstrução histórica, sem confundir correção posterior com ausência de falha.
10. Achados P0/P1/P2/P3, correções propostas e critérios de reauditoria quando aplicáveis.
11. Comandos realmente executados, códigos de saída, contagens reais e seleções não executadas com justificativa.
12. Manifestos de antes/depois e confirmação de preservação do objeto.
13. Anexo de reconciliações documentais propostas, sem aplicação.
14. Próximo passo exato para o usuário, mantendo F4 fora do escopo.

Calcule o hash do relatório depois de concluído e informe-o na resposta, fora do próprio arquivo. Gere também manifesto das evidências que não inclua a si próprio. Não preencha hashes fictícios nem afirme integridade sem comparar o conteúdo.

## 15. Critérios de conclusão desta auditoria

- Prompt implementado e emenda conferidos pelos hashes completos.
- Objeto técnico preservado durante a auditoria e identificado por manifesto.
- Escopo real confrontado com a lista permitida; auxiliares e supressões analisados sem autorização retroativa.
- Todos os 34 CTs rastreados e os dez cenários de concorrência efetivamente exercitados.
- Testes direcionados, regressões e gates executados sobre a versão entregue, com resultados reais preservados.
- Qualquer teste/sonda adicional justificado por risco concreto.
- Resultados de cópias experimentais separados dos resultados do objeto.
- Limitações aceitas, defeitos novos e lacunas históricas claramente separados.
- Relatório completo e próximo passo coerente com o veredito.

## 16. Resposta final e parada

Responda nesta ordem:

1. **F3: VEREDITO**.
2. O que foi comprovado e o que permaneceu sem verificação.
3. Achados, origem, severidade e efeito sobre a aprovação.
4. Contagens reais da fase, regressões, concorrência e gates.
5. Caminho e SHA-256 do relatório; diretório e manifesto das evidências.
6. Ação seguinte: correção dirigida e reauditoria, ou fechamento documental e commit pelo usuário, conforme os gates.

Uma aprovação vale somente para o objeto identificado. O G6 da F3 continuará dependendo do commit do usuário e de sua conferência, conforme o processo do projeto.

Pare após entregar a auditoria. Não corrija a aplicação, não edite os documentos congelados, não faça commit/merge, não prepare nem implemente a F4.
