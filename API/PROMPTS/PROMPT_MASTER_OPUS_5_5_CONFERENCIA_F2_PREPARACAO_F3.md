# Prompt Master — Opus 5.5 — Conferência do commit da F2 e preparação da F3

## 0. Papel, objetivo e autorização desta sessão

Você é o Engenheiro de Software Principal, arquiteto e revisor crítico independente da API MinhaVida.

O usuário concluiu o commit da F2 e quer que você confira esse commit, registre o G6 quando comprovado e prepare a F3 — Identidade e acesso — com uma avaliação das decisões DEC-MV-09 a DEC-MV-13.

Execute o trabalho documental e de análise até produzir resultados concretos para revisão. Não pare apenas para perguntar se pode analisar ou preparar documentos: isso está autorizado por esta mensagem.

**Esta mensagem NÃO aprova DEC-MV-09 a 13, NÃO aceita novos riscos em nome do usuário e NÃO autoriza implementar a F3.** Recomendar, aprovar uma decisão e autorizar implementação são atos distintos.

Seu trabalho nesta sessão:

1. Conferir o commit da F2 por leitura do Git, do manifesto de fechamento e das evidências existentes.
2. Registrar o encerramento do G6 da F2 somente se a conferência passar.
3. Usar esse commit como baseline técnico da preparação da F3.
4. Avaliar criticamente DEC-MV-09 a 13, inclusive suas dependências, conflitos e riscos.
5. Entregar um dossiê com recomendações, contratos completos e alterações normativas propostas.
6. Preparar um Prompt Master do Sonnet para a F3, concreto e detalhado, ainda BLOQUEADO enquanto houver decisões necessárias sem aprovação.
7. Explicar ao usuário exatamente o que precisa decidir, com opções e escopo delimitados.

Não implemente código de produção, testes da F3, modelos, migrações, configuração ou dependências. Não execute git add, commit, push, merge, reset, checkout, restore ou qualquer outro comando que altere o índice, a branch ou os arquivos existentes fora do escopo documental autorizado.

Não reabra a auditoria técnica da F2 por rotina. Não execute a suíte completa nem repita os testes aprovados apenas porque haverá uma nova fase.

O produto continua sendo um aplicativo simples de gestão pessoal com financeiro manual: receitas e despesas são lançadas pelo usuário, totais e saldo são calculados. Não introduza bancos externos, Open Finance, gateways, execução de Pix, conciliação ou preparação para essas integrações. O envio de recuperação de senha por e-mail é uma funcionalidade distinta e permanece no escopo proposto da F3.

---

## 1. Estado de partida informado pelo usuário

### 1.1. Repositório e commits

Repositório local esperado:

`/home/jose/projects/app_gestão_pessoal/API`

Commit da F2 informado pelo usuário, visível no terminal após `git rev-parse HEAD`:

```text
91be324c88c5a3f99a49b1b1700963e32ef257e9
```

Commit pai esperado, correspondente à F1:

```text
90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30
```

A captura mostra:

- mensagem do commit: `F2: esquema de dados (APROVADO_COM_P3 na auditoria)`;
- 43 arquivos alterados;
- nenhum resultado de `git status --short` após o commit;
- dois commits locais à frente de `origin/main`.

Esses dados são entradas a conferir, não substituem leitura do repositório. Estar à frente do remoto não é falha do G6 local nem requisito para executar push. Não publique nada.

### 1.2. Evidências locais de fechamento da F2

Diretório:

`~/minhavida_evidencias/f2_fechamento_DFR1NBKL/`

Arquivos esperados:

- `lista_commit.txt`: 43 caminhos explícitos, sem inclusões adicionais;
- `manifesto_commit.sha256`: hashes finais desses 43 arquivos;
- `mensagem_commit.txt`: mensagem utilizada pelo usuário;
- `antes/`: cópias dos documentos anteriores ao fechamento, incluindo o Prompt F2 efetivamente implementado.

Composição esperada do delta da F2:

- 30 arquivos da implementação;
- 11 documentos de preparação;
- 2 documentos de auditoria;
- total de 17 modificados e 26 adicionados, sem remoções.

A árvore final esperada tem 77 arquivos, considerando os 51 da F1 e os 26 novos. Contagens são verificações auxiliares: a identidade dos caminhos e dos conteúdos é a prova principal.

Relatório de auditoria imutável:

`docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`

SHA-256 registrado:

```text
f4c529692d6032a052083375f94fc493ea73c1d6449dacfbe1cc16e266cf1560
```

Evidências da auditoria:

`~/minhavida_evidencias/f2_auditoria_VJ4xnCZ6/`

Evidências da implementação:

`~/minhavida_evidencias/f2/`

### 1.3. O que já foi aprovado e encerrado

A F2 recebeu `APROVADO_COM_P3`, sem achado impeditivo. Sua auditoria comprovou o esquema, os seeds, a atomicidade da migração, o SQL offline, os timestamps e os testes direcionados.

O fechamento documental posterior foi autorizado e aplicado sem alterar código, testes, migração, configuração ou dependências.

Estados posteriores informados:

- ACH-MV-F1-005, 006 e 007: encerrados;
- ACH-MV-F2-001 e 003: encerrados;
- ACH-MV-F2-002: acompanhamento, até as lições estarem efetivamente aplicadas ao próximo Prompt Master;
- G5 da F2: `APROVADO_COM_P3`;
- G6 da F2: aguarda esta conferência do commit;
- DEC-MV-09 a 13: pendentes;
- DEC-MV-24: vinculada à F5, sem aprovação implícita nesta sessão.

O relatório original de auditoria é histórico e deve permanecer intacto. Seus estados anteriores não anulam o fechamento posterior registrado no índice.

O Prompt F2 foi anotado no fechamento. Não exija que o arquivo atual volte ao hash da versão implementada:

- versão implementada: `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c`;
- versão posterior ao fechamento: `752b32ba19df519d5a940566160dfd66dd03cbe65ff127ca66a4ce152a91dadb`.

Use o manifesto final para conferir os documentos atuais. Preserve a distinção entre histórico da implementação e estado documental posterior.

---

## 2. Ordem de leitura e fontes normativas

Leia primeiro `CLAUDE.md` e `docs/arquitetura/indice.md`, incluindo a precedência, as aprovações e os gates.

Depois leia, nas versões reais do repositório:

1. `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`, especialmente o objeto, os manifestos, os achados e o anexo de reconciliações.
2. Os três arquivos de fechamento indicados em §1.2.
3. `docs/arquitetura/analise_projeto_minhavida.md`: DEC-MV-09 a 13, REC-MV-007, 011, 017, 018 e 019, riscos e achados relevantes.
4. `docs/adr/0001_arquitetura_api_minhavida.md`: D-04, D-05 no alcance das travas de recuperação, D-07, D-08, D-13, D-14 e D-15.
5. `docs/adr/0002_identificadores_uuid.md`: contrato já aceito, sem reabrir a escolha de IDs.
6. `docs/arquitetura/arquitetura_api_minhavida.md`: §§2, 3, 4, 5, 6, 7, 8.2, 8.3, 9.1 e 11, além de referências necessárias.
7. `docs/arquitetura/plano_fases_api.md`: dependências, ficha F3 e fronteira com F4.
8. `docs/arquitetura/plano_validacao_auditoria.md`: política, testes da F3, comandos, evidências, severidades e gates.
9. `docs/arquitetura/matriz_requisitos_api.md`: telas 1, 2 e 3, item 4.1.1 e rastreabilidade correspondente.
10. Os Prompts F1/F2 somente nas partes necessárias para compreender as correções e evitar regressões de processo.
11. Código real relevante: aplicação, settings, dependências existentes, sessões, erros, modelos de usuário/recuperação, fixtures, testes de infraestrutura, `pyproject.toml` e `uv.lock`.

As referências de seção são localizadores. Confirme títulos e conteúdo; se a numeração mudou, registre o local real.

Não invente conteúdo das linhas truncadas do `CLAUDE.md`. Não trate memória da sessão como substituto de fonte disponível. Não infira aprovação a partir da palavra “recomendado”.

Registre para cada fonte caminho, partes efetivamente lidas e SHA-256 completo. Não é necessário reproduzir os arquivos inteiros no chat.

---

## 3. Conferência do commit da F2 — somente leitura

### 3.1. Comandos iniciais

Execute no repositório correto, com captura de resultados fora dele:

```bash
cd /home/jose/projects/app_gestão_pessoal/API
git rev-parse --show-toplevel
git rev-parse HEAD
git rev-parse HEAD^
git status --porcelain=v1 --untracked-files=all
git diff --cached --name-status --no-renames
git show -s --format=fuller HEAD
git diff-tree --no-commit-id --name-status --no-renames -r HEAD
git ls-tree -r --name-only HEAD
```

Não execute os comandos de preparação ou commit presentes nos arquivos de fechamento: o commit já foi feito.

Se o usuário tiver salvo este prompt em `PROMPTS/`, registre esse arquivo como entrada documental desta sessão, fora do commit auditado. Isso, por si só, não invalida a F2. Diferencie novos documentos da sessão de alterações na implementação ou nas fontes previamente aprovadas.

### 3.2. Provas exigidas

Confirme:

1. HEAD igual ao SHA informado e pai igual ao commit da F1.
2. Delta de caminhos, tipos de alteração e conteúdos correspondente à lista e ao manifesto de fechamento.
3. Hashes dos **blobs do commit**, não apenas dos arquivos do working tree. Use leitura por `git cat-file`/`git show` e cálculo de SHA-256, sem executar conteúdo desses arquivos.
4. Os 30 arquivos técnicos da F2 correspondem ao objeto aprovado na auditoria.
5. Documentos do fechamento correspondem ao manifesto posterior, sem exigir os hashes anteriores à reconciliação.
6. Relatório de auditoria com o hash registrado em §1.2.
7. Ausência de `.env` real, caches e ambiente virtual na árvore do commit. `.env.exemplo` e `compose.yaml` sanitizado são arquivos esperados, não confunda com segredos.
8. Índice vazio e ausência de mudanças técnicas posteriores, ou identificação precisa de qualquer diferença.

Se um manifesto temporário estiver ausente, procure a evidência já existente no relatório e no diretório de fechamento. Não reconstrua um “manifesto original” a partir do conteúdo atual e use isso como prova circular. Declare exatamente o alcance comprovado e o que falta.

Se houver divergência real, descreva o caminho, a expectativa, o observado e o efeito. Não altere o arquivo, não restaure automaticamente e não reconheça G6 sem evidência suficiente. Continue a análise documental da F3 no que for independente dessa divergência.

### 3.3. Resultado esperado

Se tudo conferir:

- reconhecer G6 da F2 como cumprido;
- registrar o SHA completo e sua origem no índice;
- usar esse commit como baseline técnico da F3;
- manter o veredito histórico da F2 como `APROVADO_COM_P3`;
- informar que a conferência de integração não foi uma nova auditoria nem uma execução de testes.

Não exija novo commit apenas para registrar que o commit anterior foi conferido. Esse registro pode integrar a preparação documental da F3.

---

## 4. Escopo autorizado de escrita

Crie:

1. `docs/arquitetura/preparacao_f3_identidade_acesso.md` — dossiê de análise, decisões, contratos propostos, riscos e evidências desta preparação.
2. `PROMPTS/PROMPT_MASTER_SONNET_5_F3_IDENTIDADE_ACESSO.md` — rascunho completo da implementação, com estado `BLOQUEADO — AGUARDANDO_DECISAO`.

Se já existir um documento equivalente da F3, leia-o antes e atualize-o preservando sua identidade. Informe o caminho efetivamente utilizado; não crie cópias concorrentes.

Pode atualizar:

- `docs/arquitetura/indice.md` para registrar a conferência da F2, os documentos da F3 e seus estados reais;
- `docs/arquitetura/analise_projeto_minhavida.md` para remeter às propostas da F3, atualizar acompanhamento e registrar achados comprovados;
- `docs/arquitetura/plano_fases_api.md` e `docs/arquitetura/plano_validacao_auditoria.md` para estados e referências coerentes, mantendo propostas não aprovadas claramente separadas;
- `docs/arquitetura/matriz_requisitos_api.md` para registrar a comprovação **estrutural da F2** nas linhas correspondentes, sem marcar fluxos HTTP futuros como implementados.

Também está autorizado a encerrar documentalmente ACH-MV-ARQ-018 se o critério e a evidência da auditoria F2 confirmarem sua resolução. Não generalize isso para todos os achados históricos.

Mudanças de contrato ainda pendentes em `CLAUDE.md`, ADRs ou arquitetura canônica devem ser apresentadas como **diffs propostos no dossiê**, sem substituir silenciosamente o texto vigente e sem marcar decisões como ACEITAS.

Não altere:

- código, testes, modelos, migrações, seeds;
- `pyproject.toml`, `uv.lock`, `alembic.ini`, `compose.yaml` e configurações de ferramentas;
- `.env` real, `.env.exemplo` ou dependências instaladas;
- auditorias históricas e prompts históricos para apagar divergências ou reescrever autorizações anteriores.

Armazene logs e sondas em um diretório novo sob `~/minhavida_evidencias/`, fora do repositório. Não sobrescreva evidências da F1/F2.

---

## 5. Avaliação obrigatória das decisões DEC-MV-09 a 13

As descrições abaixo vêm das propostas anteriores. Confirme-as nas fontes atuais. Nenhuma está aprovada por esta mensagem.

Para **cada decisão**, entregue:

- texto e estado atuais, com fonte;
- significado prático para o usuário;
- requisitos e decisões já aceitas que a limitam;
- riscos concretos e respectivos controles;
- uma recomendação principal fundamentada;
- alternativas apenas quando houver uma escolha relevante;
- impacto em contrato HTTP, banco, transações, dependências, testes e operação;
- alterações normativas exatas necessárias;
- texto curto e específico para uma futura aprovação do usuário;
- o que essa aprovação incluiria e o que deixaria de fora.

Não se limite a repetir “recomendo aprovar” porque foi você quem escreveu a proposta original.

### DEC-MV-09 — Autenticação, credenciais e fuso

Proposta atual:

- JWT HS256 com validade padrão de 24 horas;
- claims `sub`, `iat`, `exp`, `typ` e `sv`;
- `sv` derivado de `senha_hash`, conforme o algoritmo canônico;
- Argon2id com `argon2-cffi`;
- `PyJWT`;
- sem refresh token e com logout apenas no cliente;
- `fuso_horario` obrigatório no registro;
- D-07 e D-13.

Avalie a validade de 24 horas, o risco de token obtido por terceiro e o alcance real do logout e da revogação após redefinição. Não afirme que logout no cliente revoga um token no servidor.

Confronte a regra de 32 bytes de segredo no ADR com a regra de 32 caracteres em Settings. Proponha uma especificação inequívoca, sem gerar ou solicitar segredo real.

Especifique o relógio, os tipos das claims, algoritmo permitido, claims obrigatórias, limites temporais, comportamento de token malformado e comparação de `sv`. Confira a integração proposta com o comportamento real da versão de PyJWT escolhida; não assuma que desabilitar apenas `verify_exp` torna todas as validações temporais compatíveis com `RelogioFixo`.

Analise o uso do hash fictício no login, os parâmetros de Argon2, a execução fora do event loop e o custo sob concorrência. Não prometa “tempo constante” para toda a requisição com base apenas na presença de um hash fictício. Distinga o controle implementável das limitações.

Preserve a regra proposta de não refazer o hash no login quando isso mudaria `sv`, salvo proposta explícita submetida ao usuário.

### DEC-MV-10 — Resposta para e-mail não encontrado

Proposta atual: preservar a mensagem de 3.4.2 e responder 404 `EMAIL_NAO_ENCONTRADO` na solicitação de recuperação.

Explique a exposição da existência de uma conta. A existência de enumeração no cadastro não torna automaticamente inofensivo outro canal de enumeração.

Compare a proposta com uma resposta genérica, mostrando o impacto na experiência, nos requisitos literais, nos testes e na resposta HTTP. Não substitua a mensagem já especificada sem decisão do usuário.

Diferencie controles da F3 de medidas previstas para F11. DEC-MV-21 continua pendente e não pode ser declarada aprovada como efeito indireto desta decisão.

### DEC-MV-11 — Recuperação e política de senha

Proposta atual:

- código válido por 10 minutos;
- até 5 tentativas inválidas por emissão;
- intervalo de 60 segundos entre emissões;
- senha de 8 a 128 caracteres;
- composição apenas sugerida.

Defina limites inclusivos/exclusivos, instante usado, prazo do token de redefinição, reutilização, contagem e persistência das tentativas, reenvio e invalidação da emissão anterior.

Esclareça a resposta da quinta tentativa inválida e das solicitações seguintes. Não deixe o Sonnet escolher entre interpretações diferentes.

Considere entrada ausente, tamanho excessivo, Unicode, espaços e confirmação. Não aplique normalização silenciosa à senha nem presuma restrições de composição não aprovadas.

Diferencie código curto protegido por hash lento de token aleatório de alta entropia protegido por digest. Preserve zeros à esquerda e defina o conjunto de caracteres aceito para o código.

Avalie as condições simultâneas descritas em §7, inclusive a primeira emissão, quando a linha de recuperação ainda não existe.

### DEC-MV-12 — Envio de e-mail

Proposta atual:

- `smtplib` e `email.message`;
- execução em thread;
- envio dentro da transação antes do commit;
- implementação em memória nos testes;
- sem fila ou outbox.

Apresente claramente as consequências de:

1. falha antes do envio;
2. erro ou timeout durante o envio;
3. servidor SMTP ter aceitado a mensagem, mas o cliente perder a confirmação;
4. envio concluído seguido de falha do commit;
5. cancelamento da requisição durante uma operação em thread;
6. outra solicitação esperar a trava enquanto o envio está em andamento.

Não atribua atomicidade distribuída a uma transação PostgreSQL. Não prometa desfazer um e-mail enviado. Não introduza outbox, broker, retry automático ou tabela nova por preferência pessoal.

Avalie timeout SMTP, timeouts do banco, validação TLS, STARTTLS, fechamento de conexão e sanitização das exceções. Defina o comportamento por ambiente e os valores que precisam estar em Settings.

### DEC-MV-13 — Perfil e alteração de fuso

Proposta atual: apenas `GET /api/v1/usuarios/me`; sem área de Perfil nem alteração de fuso na v1.

Explique que o fuso cadastrado continuará sendo usado mesmo se o dispositivo mudar de fuso. Avalie o efeito disso em “hoje”, nascimento, atividades e lembretes, sem implementar funcionalidades futuras.

Não inclua endpoints de edição de perfil, troca de e-mail, troca de fuso ou gestão de sessões sem nova autorização.

### Alcance das aprovações

Revise o mapeamento dos gates: D-05 menciona travas de linha na F3, mas está associado a DEC-MV-14, prevista para F4. Determine se o contrato de recuperação está integralmente coberto pelo escopo a aprovar em DEC-MV-11/12 ou se há uma aprovação parcial adicional realmente necessária.

Se existir dependência omitida, apresente o menor escopo necessário com fonte e justificativa. Não aprove toda a DEC-MV-14 nem antecipe as travas consultivas da F4. Não crie decisões adicionais para escolhas puramente mecânicas.

---

## 6. Reconciliações que precisam ser avaliadas antes da liberação

Confira as seguintes tensões nas fontes atuais e resolva-as no plano proposto:

1. **Respostas legítimas versus vazamento.** CT-F3-25 e a descrição de segurança dizem que respostas não contêm token/e-mail, mas login precisa devolver `access_token`, verificação devolve `token_redefinicao` e `UsuarioResposta` contém e-mail. Proponha uma lista explícita de campos permitidos por endpoint e a proibição de eco em erros/logs. Não remova funcionalidades para satisfazer uma asserção genérica nem enfraqueça a proteção de logs.
2. **Relógio controlado versus biblioteca JWT.** Defina quais validações temporais ficam na biblioteca e quais usam `Relogio`, com tratamento consistente de `iat`, `exp` e outras claims aceitas ou rejeitadas. Não desative validações sem substituto quando elas forem necessárias ao contrato.
3. **Instante único versus espera por trava.** Defina quando o instante é capturado nos fluxos de autenticação/recuperação, como a validade é reavaliada após bloqueios e como isso se relaciona com o contrato do contexto autenticado.
4. **Transação versus erro de negócio.** A tentativa inválida precisa persistir: service retorna resultado, router confirma e só então apresenta o erro previsto. O service não passa a executar commit e o handler de erros também não.
5. **Thread usada versus controle de capacidade.** Confira a consistência entre `asyncio.to_thread` e referências ao pool/limitador do AnyIO. Documente o mecanismo real, o comportamento de cancelamento e seus limites, sem inventar garantias.
6. **Validação e mensagens.** Confronte schemas, códigos de erro, literais das telas e CTs, incluindo tamanho máximo da senha, confirmação, data civil e formato do e-mail.
7. **Dependências e fixtures.** A inclusão de JWT/SMTP em Settings não pode fazer testes existentes consultarem o ambiente real nem quebrar sua inicialização por falta de valores sintéticos.
8. **Congelamento do esquema.** A F3 está planejada sem alteração de esquema. Toda necessidade demonstrada de coluna, tabela, índice ou revisão deve virar proposta explícita com impacto, nunca correção silenciosa da revisão 0001.

Esses pontos são verificações dirigidas, não achados automaticamente confirmados. Para registrar um achado, forneça fonte, reprodução ou raciocínio verificável, impacto, severidade e solução proposta. Não reclassifique divergências documentais como defeitos da implementação F2.

---

## 7. Contratos da F3 a deixar fechados no dossiê

### 7.1. HTTP e schemas

A ficha atual prevê seis endpoints:

| Método | Caminho |
| --- | --- |
| POST | `/api/v1/auth/registro` |
| POST | `/api/v1/auth/login` |
| POST | `/api/v1/auth/recuperacao/solicitar` |
| POST | `/api/v1/auth/recuperacao/verificar` |
| POST | `/api/v1/auth/recuperacao/redefinir` |
| GET | `/api/v1/usuarios/me` |

Para cada um, feche:

- função e módulos responsáveis;
- schema de entrada, tipos, limites e normalizações;
- schema de resposta e campos explicitamente permitidos;
- status de sucesso e códigos/mensagens de falha;
- cabeçalhos relevantes, inclusive `Retry-After` e autenticação;
- consultas e escritas realizadas;
- fronteira transacional;
- efeitos externos;
- autorização ou ausência deliberada dela;
- critérios de aceite e testes.

Preserve mensagens literais exigidas nas telas 3.4.8, 3.4.10, 3.4.14 e 3.4.15. Mudança na 3.4.2 depende da escolha de DEC-MV-10.

Especifique a serialização de datas e instantes na API segundo o contrato existente. Não confunda a apresentação brasileira na tela com uma mudança automática do formato JSON.

### 7.2. Autorização e suporte

Defina `ContextoUsuario`, `ContextoDep`, `Relogio`, hasher, enviador de e-mail e `obter_do_usuario_ou_404` com assinaturas e responsabilidades concretas.

Mantenha a direção de dependências já aprovada. Não crie repository, container de injeção ou camada alternativa de erros.

Use o usuário autenticado como fonte de propriedade dos recursos. Testes do helper podem usar rotas exclusivas do aplicativo de teste; isso não autoriza criar endpoints de domínio da F4/F5.

### 7.3. Recuperação, concorrência e efeitos

Produza uma tabela com precondição, bloqueio, leitura, escrita, commit/rollback e resultado observável para:

- dois registros simultâneos do mesmo e-mail;
- duas primeiras solicitações de código para o mesmo usuário;
- duas solicitações de reenvio;
- duas verificações corretas;
- cinco verificações inválidas concorrentes;
- verificação correta concorrendo com o limite de tentativas;
- reenvio concorrendo com verificação;
- duas redefinições com o mesmo token;
- reenvio concorrendo com redefinição;
- login/autenticação concorrendo com redefinição, deixando clara a garantia de invalidação de JWT;
- falha de envio e falha de commit após envio.

Use as constraints existentes como proteção final. Trava de uma linha inexistente não deve ser tratada como proteção suficiente para a primeira emissão.

Explique a garantia obtida em cada corrida, sem usar apenas “está protegido por transação”. Não exija que uma requisição já em andamento seja cancelada retroativamente se esse não é o contrato.

### 7.4. Settings e dependências

Mapeie exatamente:

- campos novos de Settings, tipos, limites, padrões e condições por ambiente;
- alterações futuras em `.env.exemplo`, só com valores fictícios;
- injeção de settings, relógio, hasher e enviador;
- inicialização e fechamento de recursos;
- dependências novas previstas: `argon2-cffi`, `PyJWT` e `tzdata`;
- uso de outras bibliotecas já instaladas, como a validação de e-mail.

Confira versões reais do lock e do ambiente. Não invente números de versão para bibliotecas ainda não adicionadas.

A inclusão futura de dependências será um passo explícito da Etapa B, condicionado à aprovação. Nesta sessão não execute `uv add`, `uv sync` nem altere o lock.

---

## 8. Verificação técnica permitida nesta preparação

O foco é leitura e desenho de contrato. Não execute testes da aplicação nesta sessão.

Se uma dúvida de API tornar a especificação incerta:

1. leia primeiro o código/documentação da versão instalada e o lock;
2. quando necessário, consulte documentação oficial compatível e registre a fonte;
3. uma sonda mínima em diretório temporário é permitida para comportamento de biblioteca, com dados sintéticos, sem importar o aplicativo real, sem ler `.env` e sem acessar banco ou SMTP real;
4. registre comando, versão, hipótese, resultado e limite;
5. se a dependência não estiver disponível, não instale silenciosamente: registre a confirmação necessária e sua condição de parada.

Sondas não autorizam implementação disfarçada de toda a F3 em uma cópia, nem uma nova auditoria da F2.

Não leia ou exponha credenciais reais. Não use dumps completos de ambiente. Nenhum envio de e-mail real está autorizado.

---

## 9. Política de testes a prescrever para o Sonnet

### 9.1. Cobertura existente

Mapeie todos os CTs já previstos:

`CT-F3-01` a `CT-F3-21`, mais `CT-F3-25` e `CT-F3-30`.

São 23 identificadores atuais; isso não determina o número final de funções ou casos parametrizados. Não invente uma contagem de “passed” antes de conhecer a coleta.

Para cada CT, indique arquivo, cenário, preparação, ação, asserções e evidência. Mantenha os IDs existentes. Novos CTs precisam de justificativa e identificadores livres conferidos no catálogo.

As concorrências já exigidas — CT-F3-05, 14, 15, 17 e 19 — permanecem obrigatórias.

Acrescente cobertura dirigida apenas para lacunas concretas encontradas nesta análise, como primeira emissão concorrente, limites temporais, falha após envio ou distinção entre campos legítimos de resposta e vazamentos.

### 9.2. Qualidade da prova

Prescreva:

- PostgreSQL real descartável via Testcontainers, sem substituir por SQLite;
- migração entregue na F2 como caminho de construção do banco;
- sessões/conexões independentes nos testes de concorrência;
- sincronização verificável, sem usar apenas `gather` ou `sleep` como prova de contenção;
- verificação de persistência de tentativas, consumo do token e rollback por outra conexão;
- `RelogioFixo` e limites exatos, sem esperar minutos reais;
- Argon2 real com parâmetros de teste explicitamente reduzidos, preservando uma verificação separada da configuração prevista para execução normal;
- código forçado `00012345` para preservar zeros;
- enviador em memória e falhas sintéticas; nenhum e-mail real;
- fixtures que não abrem o `.env` real e não absorvem segredos/valores externos;
- captura do logger real e sua saída formatada, incluindo exceções, para provar ausência de dados sensíveis.

Não use comparação de duração exata de duas requisições como prova determinística de resistência à enumeração por tempo.

Teste não executado é PLANEJADO ou NÃO EXECUTADO, nunca aprovado. Não aceite skips ou xfails para ocultar infraestrutura indisponível.

### 9.3. Seleção e execução futura

Padrão:

1. testes específicos do comportamento alterado;
2. `tests/identidade/`;
3. regressões diretamente afetadas da F1/F2, justificadas por arquivos e contratos;
4. concorrência específica obrigatória;
5. Ruff, formatação, Pyright e checks estruturais pertinentes.

A ficha prevê regressão em `tests/infra/test_erros.py`. Verifique se mudanças de Settings, lifespan ou fixtures exigem outros nós concretos. Não transforme isso em execução automática de toda `tests/infra` ou `tests/esquema` sem risco identificado.

Comandos de validação devem usar `uv run --frozen --no-sync`, após o passo autorizado de instalação/sincronização das dependências.

Qualidade em modo de verificação:

```bash
uv run --frozen --no-sync ruff check --no-fix .
uv run --frozen --no-sync ruff format --check .
uv run --frozen --no-sync pyright
```

Não permita `task test` ou `pytest` sem seleção como rotina.

A suíte completa só pode ser proposta com:

```text
OBJETIVO DA SUÍTE COMPLETA:
...

POR QUE OS TESTES DIRECIONADOS NÃO SÃO SUFICIENTES:
...

MUDANÇAS QUE JUSTIFICAM A EXECUÇÃO:
...
```

“Por segurança”, “para garantir” e “porque terminou” não são justificativas.

---

## 10. Lições da F2 obrigatórias no novo Prompt Master

Aplique e aponte onde cada uma ficou atendida:

1. **Conteúdo exato coerente com o formatador.** Se prescrever bloco literal, valide sua compatibilidade com a configuração real. Diferencie exemplo, pseudocódigo e conteúdo obrigatório. Não crie divergência apenas por formatação normal.
2. **Erros residuais de lint previstos.** Permita correção mecânica dentro da lista de arquivos autorizados; preserve o log anterior e use novos nomes com sufixo em reexecuções. Nova exceção de lint, mudança de configuração ou desvio de contrato exige parada e descrição concreta.
3. **Regra e exemplo consistentes.** Não prescreva uma regra que o próprio modelo dado viola. Isso vale para nullability, tipos, imports, erros, schemas e timestamps.
4. **Validação sem sincronização implícita.** Use `--frozen --no-sync` nos checks. Separe instalação de dependências da validação, registrando alterações do lock e versões antes/depois.
5. **Expectativas derivadas da versão final.** Saídas de Alembic, mensagens e nomes devem corresponder ao artefato final especificado.
6. **Relatório integral em arquivo.** O Sonnet deve salvar relatório e logs em pasta nova sob `~/minhavida_evidencias/f3/`, sem depender de texto truncado no chat.
7. **Comando, saída e código de saída preservados.** Logs precisam registrar falhas e reexecuções. Não use pipeline que esconda falha do comando.
8. **Alembic seguro.** Não prescreva comandos que executem `env.py` pela CLI e caiam na leitura do `.env`. Operações necessárias usam a API existente com URL explícita de banco descartável; SQL offline usa URL fictícia. Na F3 não há migração nova prevista.
9. **Compose seguro.** Se houver motivo concreto para validá-lo, usar `--env-file /dev/null`, variáveis sintéticas explícitas e `config --quiet`. Não executar Compose sem necessidade nesta preparação.
10. **Formatador e auditoria.** Auditor usa `--no-fix`/`--check`. Implementador pode formatar arquivos autorizados conforme o contrato, com conferência do delta; nenhuma ferramenta pode reescrever documentos protegidos inadvertidamente.

Depois de aplicar e verificar os quatro critérios específicos do ACH-MV-F2-002 no Prompt F3, pode registrar seu encerramento documental com referências precisas. Isso não significa aprovação das decisões da F3 nem sucesso de testes futuros. Se um critério não estiver atendido, mantenha apenas essa parte pendente.

---

## 11. Estrutura obrigatória do Prompt Master do Sonnet

Entregue um documento completo, não uma lista genérica de tarefas.

Use esta estrutura:

0. Regras absolutas.
1. Estado de partida, baseline técnico e preparação documental.
2. Fontes normativas e precedência.
3. Decisões, aprovações necessárias e reconciliações.
4. Escopo, exclusões e fronteira com a F4.
5. Política de testes.
6. Banco, transações, concorrência e efeitos externos.
7. Lista explícita de arquivos permitidos e protegidos.
8. Algoritmos e contratos.
9. Configuração, dependências e detalhes operacionais.
10. Schemas, endpoints e erros.
11. Testes e rastreabilidade.
12. Critérios de aceite.
13. Etapa A — somente leitura, relatório e parada.
14. Etapa B — sequência de implementação e validação, condicionada à autorização.
15. Relatório e evidências.
16. Parada final para auditoria independente.

Requisitos adicionais:

- Obtenha a lista de arquivos a partir da ficha F3 e da inspeção real; inclua alterações de fixtures compartilhadas somente se necessárias e justificadas.
- Proteja modelos, a revisão 0001 e o esquema aprovado da F2. Não autorize refatorações paralelas.
- Escolha uma proposta técnica principal no rascunho e indique claramente de quais aprovações ela depende. Não entregue ao Sonnet alternativas abertas para ele escolher.
- Para escolhas reais ainda pendentes, deixe o prompt BLOQUEADO e mantenha as alternativas no dossiê.
- Não use “conforme melhor prática”, “defina a arquitetura”, “implemente como achar melhor” ou “ajuste os testes até passar”.
- Preencha comandos literais onde o estado permita. Quando uma versão futura de dependência precisar ser confirmada, defina o procedimento e o bloqueio exato; não invente versão.
- A Etapa A confronta baseline, fontes, versões, APIs e plano; não instala dependências, altera código ou executa testes.
- A Etapa B depende das decisões aprovadas, dos documentos reconciliados, do relatório da Etapa A e do “pode implementar” do usuário.
- “Preparar F3”, “aprovo a arquitetura” e “conferi o commit” não substituem essa autorização de implementação.
- Sonnet não faz commit local e não se declara aprovado.
- Preserve a exceção Cloud somente se ela se aplicar: branch da sessão, commit/push e draft PR conforme autorização existente, sem merge nem alteração de main. O modo desta preparação é LOCAL.

### Baseline e documentos de preparação

Separe:

- baseline técnico: commit da F2 conferido;
- alterações documentais autorizadas nesta preparação;
- estado/hash do Prompt F3 efetivamente encaminhado ao Sonnet.

Não imponha um novo commit obrigatório só dos documentos. Admita preparação documental sem commit, desde que os caminhos e hashes sejam registrados, ou um commit documental feito voluntariamente pelo usuário.

Não crie hashes circulares: um arquivo não precisa conter seu próprio hash final. Informe esse hash em outro registro ou na mensagem de entrega.

Se uma aprovação posterior modificar uma fonte lida na Etapa A, determine revalidação apenas do delta afetado. Não obrigue repetir toda a análise por uma alteração documental irrelevante.

---

## 12. Gates e condições de parada

Estado esperado ao final desta sessão, se o commit conferir e ainda não houver novas aprovações:

| Item | Estado |
| --- | --- |
| F2 — G5 | APROVADO_COM_P3, histórico preservado |
| F2 — G6 | CUMPRIDO, com SHA e evidência |
| Baseline técnico da F3 | Commit da F2 conferido |
| DEC-MV-09 a 13 | AGUARDANDO_DECISAO, com recomendações concretas |
| Dossiê da F3 | ENTREGUE PARA REVISÃO |
| Prompt Sonnet F3 | BLOQUEADO — AGUARDANDO_DECISAO |
| Implementação F3 | NÃO AUTORIZADA |

Não libere `PRONTO_PARA_ETAPA_A` apenas porque o rascunho está completo. A liberação exige as aprovações aplicáveis e a reconciliação das fontes.

Uma divergência real que exija nova decisão deve indicar:

- fonte e trecho;
- problema concreto;
- fase/gate afetado;
- alternativa recomendada;
- alteração exata;
- critério de desbloqueio.

Não encerre a sessão antecipadamente após encontrar a primeira pendência: conclua a análise e os entregáveis independentes para que o usuário decida sobre um conjunto consolidado.

Não reabra decisões aceitas por preferência arquitetural. Se houver risco concreto novo em contrato aprovado, apresente evidência e proposta limitada, sem alterá-lo silenciosamente.

---

## 13. Critérios de aceite desta preparação

Ao terminar, confira:

- [ ] SHA e pai da F2 verificados no Git.
- [ ] Delta e conteúdos comparados com o fechamento e a auditoria, ou limites declarados.
- [ ] Registro do G6 atualizado somente se comprovado.
- [ ] Código, testes, migração, configuração e dependências preservados.
- [ ] Nenhuma leitura do .env real, envio de e-mail real, instalação ou execução de testes da aplicação.
- [ ] DEC-MV-09 a 13 avaliadas individualmente, sem aprovação implícita.
- [ ] Dependências de aprovação da F3 conferidas, inclusive o alcance das travas de recuperação.
- [ ] Contratos de HTTP, autenticação, tempo, transações, concorrência e SMTP detalhados.
- [ ] Conflitos normativos reconciliados por propostas precisas, sem decisões delegadas ao Sonnet.
- [ ] Todos os CTs existentes da F3 rastreados; novas provas vinculadas a riscos concretos.
- [ ] Lições da F2 aplicadas e estado do ACH-MV-F2-002 coerente.
- [ ] Dossiê e Prompt Master F3 escritos, com estados explícitos.
- [ ] Diffs de alterações normativas pendentes apresentados para aprovação.
- [ ] Referências, IDs e blocos de código conferidos.
- [ ] Nenhum novo requisito artificial de commit, push ou suíte completa.
- [ ] Lista final de arquivos alterados limitada ao escopo documental.

Verificação documental não deve ser relatada como teste de implementação.

---

## 14. Resposta final ao usuário e parada

Apresente primeiro:

1. Resultado da conferência do commit, com SHA completo, G6 e baseline da F3.
2. Tabela das cinco decisões: significado, recomendação, principal risco e escopo da aprovação.
3. Divergências realmente encontradas e soluções propostas.
4. Arquivos criados/atualizados e seus hashes completos.
5. Gates da F3 e o que falta para liberar a Etapa A.
6. Texto sugerido de aprovação, separado por decisão, para o usuário avaliar. Não escreva como se o usuário já o tivesse enviado.
7. A próxima ação única e concreta do usuário.

Separe “verificado”, “proposto”, “aprovado anteriormente” e “não executado”.

Finalize aguardando as decisões do usuário. Não implemente a F3, não peça ao Sonnet para começar e não faça commit.

**Execute agora a conferência do commit da F2 e a preparação documental da F3 neste escopo.**

