# Prompt Master — Opus 5.5 — Auditoria independente da F2: esquema de dados

| Campo | Valor |
| --- | --- |
| Projeto | API MinhaVida — gestão pessoal e finanças |
| Papel | Engenheiro de Software Principal, arquiteto e auditor independente |
| Data de preparação | 2026-10-13 |
| Fase | F2 — Esquema de dados |
| Estado recebido | ENTREGUE_PARA_AUDITORIA, declarado pelo Sonnet |
| Modo | LOCAL, no WSL do usuário |
| Baseline de código | `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30` |
| Prompt implementado | `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md` |
| SHA-256 do Prompt F2 | `007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c` |
| Autorização desta tarefa | Auditar, executar verificações direcionadas e produzir os documentos de auditoria permitidos |
| Autorização que NÃO está incluída | Corrigir implementação, mudar contratos aprovados, fazer commit/merge ou iniciar a F3 |

Você deve realizar a auditoria até produzir um veredito fundamentado. Esta mensagem já autoriza as leituras, verificações e sondas delimitadas abaixo; não encerre a tarefa apenas apresentando um plano ou pedindo autorização para começar a auditoria.

O relatório do Sonnet e suas sondas anteriores são evidências auxiliares. A aprovação depende do objeto real entregue, das fontes normativas e das verificações independentes. Você também escreveu a arquitetura e o Prompt F2: examine possíveis erros de especificação com o mesmo rigor aplicado à implementação.

## 0. Regras absolutas

1. Não implemente correções no objeto auditado. Não altere código, testes, migração, dependências, configuração nem expectativas para fazer uma verificação passar.
2. Não use `ruff check --fix` nem `ruff format` com escrita no repositório. Nesta auditoria use `ruff check --no-fix` e `ruff format --check`. Esta instrução específica prevalece sobre orientações genéricas de autofix do `CLAUDE.md`.
3. Não faça `git add`, commit, push, merge, reset, clean, stash, checkout de arquivos ou restore. Não descarte alterações do usuário. A F2 ainda não tem commit; isso é esperado.
4. Não leia, copie, imprima, edite ou calcule hash do `.env` real. Não carregue as configurações reais para obter uma URL de banco. Não registre segredos em relatórios ou logs.
5. Use PostgreSQL descartável com Testcontainers para provas que acessam banco. Não conecte ao banco de desenvolvimento. Não substitua PostgreSQL por SQLite.
6. Pela CLI do Alembic, somente `heads` e `history`. Operações que executem `env.py` devem usar a API do Alembic com URL explícita e controlada. Isso inclui geração offline de SQL. Não execute `alembic upgrade --sql` pela CLI: a orientação antiga do plano de fases será tratada como pendência documental.
7. Não use `docker compose up`, `down`, prune ou remoção de recursos alheios. Compose apenas para validação com valores fictícios e `--env-file /dev/null`.
8. Não execute a suíte completa, `pytest` sem seleção, `task test` ou outros atalhos que ampliem a seleção. Não rode toda a infraestrutura da F1 por rotina.
9. Preserve os logs do Sonnet. Crie evidências próprias em diretório novo, fora do repositório, sem sobrescrever execuções anteriores.
10. Sondas e mutações, quando justificadas, somente fora do repositório, com dados sintéticos, sem copiar o `.env`. Compare o conteúdo relevante da cópia com o objeto auditado antes da sonda. Uma correção experimental em cópia não corrige a entrega.
11. Não enfraqueça contratos aprovados, não crie arquitetura paralela e não invente funcionalidades para fases futuras. Classifique defeitos do contrato separadamente dos defeitos do código.
12. A F1 permanece aprovada e integrada. Não reabra sua auditoria inteira nem transforme o encerramento formal pendente do ACH-MV-ARQ-019 em novo bloqueio da F2.
13. Escreva em português. Diferencie sempre: observado diretamente, reproduzido, declarado pelo implementador, inferido e não verificado.

## 1. Estado de partida e objeto auditado

### 1.1. Baseline

O baseline da implementação é:

- HEAD esperado: `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`.
- Pai: `bd2b2e0f1e4f2674b528175e535b0931badec34a`.
- Árvore da F1: 51 arquivos.
- Modo A: dez documentos de preparação modificados e o Prompt F2 novo, conforme §1.2 do Prompt F2.
- Sobre esse estado, o Sonnet entregou a implementação ainda sem commit.

Não aplique ao estado pós-implementação a exigência de que os arquivos alterados pela F2 continuem com os hashes anteriores à implementação. Use três referências diferentes:

1. O commit da F1 para identificar a base e o diff.
2. A tabela dos onze documentos de preparação para comprovar sua preservação.
3. O manifesto final do Sonnet e seu manifesto independente para identificar a entrega efetivamente auditada.

O fato de `main` estar à frente de `origin/main` não impede a auditoria local nem exige push.

### 1.2. Escopo de arquivos

Confronte o estado real com a lista exata do Prompt F2 §7.

Alterações de implementação permitidas em arquivos existentes:

- `pyproject.toml`: exclusivamente as três alterações de §9.
- `src/api_gestao_pessoal/models/base.py`.
- `src/api_gestao_pessoal/models/__init__.py`.
- `src/api_gestao_pessoal/models/usuario.py`.
- `tests/conftest.py`: acréscimo de `banco_migrado` e imports necessários.
- `tests/apoio/banco.py`: acréscimo de `TABELAS_DOMINIO` e `limpar_dados`.
- `tests/infra/test_alembic_ambiente.py`: exclusivamente a adaptação do CT-F1-17.

Os arquivos novos são os de §7.2: enumerações, doze modelos, uma revisão, dois módulos de apoio e o pacote de testes de esquema. Confira os caminhos, não apenas a contagem.

Revisão declarada na entrega:

`alembic/versions/20261013_0001_esquema_inicial.py`

Hashes completos disponíveis no relatório, a conferir:

| Arquivo | SHA-256 declarado |
| --- | --- |
| Revisão inicial | `da1d0f38b161d26021f9242c1d5291d8cc0d4ef8d4f64b4c56c4155875150a24` |
| `models/base.py` | `50844f7fa5c78b09ed82362a4c480fc04b9be0d50813c43f5aae8627803bdf63` |
| `models/enums.py` | `73d36da9b171fd6f3e062248e33f26237f2adf4eaeebf7bfde74de40712d8a39` |

Atenção: use o manifesto original do Sonnet como fonte dos hashes completos. Se uma transcrição nesta mensagem ou no relatório estiver malformada, registre a diferença de transcrição e consulte o original; não invente dígitos nem conclua que o código mudou a partir de uma cópia truncada.

### 1.3. Artefatos administrativos

Se o usuário colocar este prompt de auditoria em `PROMPTS/`, ou disponibilizar o relatório do Sonnet como arquivo, registre esses caminhos separadamente como entradas desta auditoria. Não os atribua à implementação do Sonnet nem os confunda com alteração dos onze documentos protegidos.

Faça o mesmo com o relatório de auditoria que você criar. Essas exceções não autorizam outros arquivos extras ou alterações em documentos existentes.

## 2. Fontes normativas e ordem de leitura

Leia o conteúdo real necessário, sem se limitar ao resumo do Sonnet:

1. Esta instrução, a autorização da Etapa B e a emenda F2-D1 consolidada na seção 3.
2. `CLAUDE.md`: diretrizes, contrato das treze tabelas, restrições, índices e mapeamento SQLAlchemy.
3. `docs/arquitetura/indice.md`: precedência, aprovações, gates e pendências.
4. `docs/adr/0001_arquitetura_api_minhavida.md`: decisões aceitas aplicáveis, especialmente D-04, D-09 e D-14.
5. `docs/adr/0002_identificadores_uuid.md`, aceito.
6. `docs/arquitetura/arquitetura_api_minhavida.md`: §1.1, §2.1, §3.2, §10 integral e demais trechos diretamente citados.
7. `docs/arquitetura/plano_fases_api.md`: ficha da F2.
8. `docs/arquitetura/plano_validacao_auditoria.md`: política de testes, infraestrutura, catálogo F2, CT-F1-02 e CT-F1-17 a 19, severidade e auditoria.
9. `docs/arquitetura/matriz_requisitos_api.md`: contrato de dados e cobertura da F2.
10. `docs/arquitetura/analise_projeto_minhavida.md`: decisões DEC-MV-06 a 08 e reconciliações REC-MV-001, 008, 014, 033 e 034.
11. `PROMPTS/PROMPT_MASTER_SONNET_5_F2_ESQUEMA_DADOS.md` integral.
12. Relatório final do Sonnet, logs originais e arquivos entregues.
13. Auditoria e reauditoria da F1 somente nos pontos herdados que afetam esta entrega.

Precedência: instruções explícitas do usuário, `CLAUDE.md`, ADRs aceitos, documentos de arquitetura e Prompt Master, respeitando as substituições expressamente aprovadas. A emenda F2-D1 substitui o trecho específico de seeds da arquitetura. Não estenda essa exceção a outros contratos.

O prompt antigo de implementação do banco continua suspenso. DEC-MV-09 a 24 não estão automaticamente aprovadas pela F2. Não acrescente `DESATIVADO` a enumerações nem implemente decisões futuras.

## 3. Emendas e decisões já aprovadas

### 3.1. F2-D1 — Seeds

O usuário aprovou a recomendação do Opus e autorizou a Etapa B com a seguinte escolha:

- Função `instrucoes_categorias() -> list[Insert]`, com o conteúdo do Prompt F2 §8.3.
- Construção local com `sa.table`, `uuid.uuid7()` e INSERT PostgreSQL com `on_conflict_do_nothing` pelas chaves naturais previstas.
- Ao final de `upgrade()`, após as tabelas e os oito índices:

~~~python
for instrucao in instrucoes_categorias():
    op.execute(instrucao)
~~~

- Essa escolha substitui exclusivamente a exigência de `inserir_categorias(conexao: Connection) -> None` chamada com `op.get_bind()` em arquitetura §10.5.
- Não criar `inserir_categorias`, não usar `op.get_bind()` na revisão e não importar `Connection` nela.
- CT-F2-07 permanece: executar os itens de `script.module.instrucoes_categorias()` pela fixture `conexao`; contagens 6/8/16.
- Preservar as trinta categorias, UUIDv7, idempotência, transação da migração e ausência de importação dos modelos vivos.
- Os documentos não seriam editados pelo Sonnet. A reconciliação documental seria posterior.

Não reabra a D1 como escolha pendente nem classifique a implementação dessa emenda como desvio não autorizado.

### 3.2. D2 e D3

- D2: comandos da Etapa B no Prompt F2 §13; §14 contém o relatório.
- D3: inspeção inicial com `ls -A1 alembic/versions`. Somente `.gitkeep` era a expectativa ANTES da implementação. Agora deve existir também a revisão 0001; caches ignorados não são revisões.

### 3.3. Demais contratos

DEC-MV-06, DEC-MV-07, DEC-MV-08 e ACH-MV-F1-005, opção A, já foram aprovadas. Isso inclui UUIDv7, modelo físico, quatro CHECKs de nomes e inclusão de Alembic no Ruff/Pyright com exceção PLC0415 restrita ao `alembic/env.py`.

REC-MV-033 e REC-MV-034 fazem parte da preparação vigente: padrões no banco, exceto geração de IDs na aplicação; limpeza explícita sem RESTART IDENTITY/CASCADE e rollback nos testes de restrição.

## 4. Alegações do Sonnet e pontos específicos de atenção

O Sonnet declarou, ainda sem validação independente:

- Revalidação inicial sem divergências; índice vazio; documentos protegidos e `uv.lock` inalterados.
- Metadata com treze tabelas, 134 colunas e 93 nomes de constraints/índices.
- Primeira execução: 41 testes da fase e quatro regressões aprovados.
- Ruff inicial com rc 1; formatação e uma quebra manual de string SQL; nova verificação limpa.
- Reexecução após essas alterações: 41 testes aprovados em 19.13 s e quatro regressões em 13.49 s.
- Ruff final limpo; 50 arquivos formatados; Pyright com zero erros, avisos e informações.
- `alembic heads` = `0001 (head)`; Compose válido.
- Nenhum skip/xfail, nenhuma suíte completa e nenhuma conexão ao banco de desenvolvimento.
- Revisão gerada preservada em `05_revisao_gerada.py`, com revisão manual posterior.

Essas contagens são referências de conferência, não prova suficiente nem autorização para ajustar testes para atingir um número.

### 4.1. D4 — Divergência da descrição em alembic history

A entrega registra:

- Prompt F2 §13, expectativa do passo 14b: `<base> -> 0001 (head), esquema inicial`.
- Prompt F2 §8.2, item 1: docstring obrigatória `Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).`
- Saída declarada: `<base> -> 0001 (head), Esquema inicial: 13 tabelas, constraints, índices e 30 categorias (F2).`

Audite expressamente:

1. A docstring real, o ID, o pai, o arquivo de revisão, o grafo e a saída real de `history`.
2. A origem da descrição no Alembic instalado, por inspeção pontual ou prova controlada.
3. Se a divergência é da especificação de saída, da migração, da evidência ou de mais de uma origem.
4. Se houve descumprimento de condição de parada e quais evidências permitem afirmar a cronologia. Não invente uma sequência apenas a partir de texto resumido ou horários de arquivos.
5. O impacto e a classificação segundo a política de severidade existente.

Não altere a docstring da migração para fazer a saída caber numa expectativa contraditória. Não altere logs e não considere D4 automaticamente aprovada por esta mensagem. Se for apenas uma errata sem impacto técnico, justifique esse diagnóstico e proponha o ajuste documental mínimo. Se exigir exceção a contrato ou a gate, identifique exatamente a decisão que depende do usuário.

Complete as demais verificações mesmo que haja uma pendência documental, desde que não exista risco ou perda da identidade do objeto que impeça a execução.

### 4.2. Outros pontos relatados

- Verifique a remoção dos CHECKs duplicados emitidos pelo autogenerate: o banco deve ter nove CHECKs de enumeração e 27 explícitos, não apenas a contagem de declarações no Python.
- Verifique `length=` em todas as nove colunas enum; não confie no comprimento inferido pelo autogenerate.
- Verifique o diff de `test_estrutura.py`: a correção de listas para tuplas deve preservar os valores esperados independentes, não acomodar um esquema incorreto.
- Verifique a quebra da string SQL e a reexecução depois da última alteração relevante.
- O Sonnet declarou ter removido `# noqa: PT012` antes das execuções. Verifique o estado final e as evidências disponíveis; não afirme conhecer um estado intermediário que não foi preservado.
- A supressão anterior em `settings.py` pertence à F1; não a trate como introduzida pela F2 sem comparar com a base.
- Confirme quais logs existem, inclusive `antes_ruff/`. Diferencie ausência de prova histórica, contradição comprovada e mera truncagem do texto copiado para o chat.

## 5. Identificação do objeto e preservação de evidências

Antes dos testes:

1. Registre diretório, branch, HEAD, pai, status completo com arquivos não rastreados e estado do índice.
2. Confira o diff de nomes e depois o conteúdo completo dos arquivos permitidos, incluindo os novos que `git diff` sozinho não mostra.
3. Separe alterações documentais de preparação, implementação F2 e entradas administrativas desta auditoria.
4. Confira os onze documentos de §1.2 do Prompt F2 e seu próprio hash. A emenda não mudou os bytes desses documentos.
5. Confira o manifesto final de implementação contra o disco. Recupere hashes completos dos arquivos originais; o texto do chat contém trechos truncados.
6. Gere um manifesto independente do objeto relevante antes de executar verificações. Não inclua nem abra o `.env`. Não varra ambientes virtuais ou caches; inspecione bibliotecas instaladas apenas pontualmente quando necessário.
7. Examine os logs originais do Sonnet, sem executar scripts neles contidos nem confiar cegamente em `codigo_saida=0`.

Fontes de evidência esperadas:

- `$HOME/minhavida_evidencias/f2/00_revalidacao.log`.
- `$HOME/minhavida_evidencias/f2/05_autogenerate.log`.
- `$HOME/minhavida_evidencias/f2/05_revisao_gerada.py`.
- Logs de testes, lint, formatação, Pyright, Alembic e Compose, incluindo as primeiras tentativas e reexecuções.
- `18a_status.log`, `18b_diff_stat.log` e `18c_sha256_f2.log`.
- `$HOME/minhavida_evidencias/f2_sha256_logs.txt`, conforme o comando original.

Verifique o manifesto antes de confiar nos arquivos. Ausência de evidência original não pode ser reparada fabricando um log retrospectivo. Uma reprodução sua deve receber identificação própria.

Não interrompa toda a auditoria só porque o resumo colado no chat perdeu caracteres. Procure os originais nos caminhos conhecidos. Se não estiverem disponíveis, registre a limitação e seu impacto concreto.

## 6. Auditoria do modelo físico

Faça a conferência campo a campo entre contrato aprovado, modelos e esquema materializado pelo Alembic. Contagem isolada não basta.

### 6.1. Estrutura e integridade

Confirme:

- Treze tabelas e 134 colunas, com nomes, tipos, comprimentos, precisão, escala, nulabilidade e padrões conforme o contrato.
- 32 colunas UUID: treze PKs e dezenove FKs, sem identity/autoincrement/default de banco para IDs.
- Geração de UUIDv7 pela aplicação; INSERT textual sem ID deve ser recusado nos casos previstos.
- 93 nomes: treze PKs, dezessete UNIQUEs, dezenove FKs, 36 CHECKs e oito índices.
- Treze FKs simples e seis compostas, com as colunas e ordens corretas; todas com ON DELETE RESTRICT.
- Constraints de propriedade entre usuários e de compatibilidade de categoria financeira/tipo.
- Nomes das constraints e índices conforme o catálogo, únicos quando exigido e dentro do limite de 63 caracteres.
- Sete enumerações aplicadas nas nove colunas previstas; valores, comprimentos, CHECKs e configuração de validação exatamente contratados.
- Nenhuma coluna, índice, constraint, trigger, extensão ou relacionamento ORM adicional.

### 6.2. Regras que precisam de controles negativos e positivos

Confronte todos os casos do Prompt F2 §10.5, incluindo:

- Propriedade de séries, importâncias, movimentações, lembretes e notificações.
- Categoria financeira compatível com RECEITA/DESPESA.
- Pares de série/ocorrência, unicidade e comportamento após exclusão lógica.
- Valores financeiros positivos; valor previsto condicionado à existência de despesa.
- Vínculo interno de despesa com importância, unicidade e campos associados.
- Formas de movimentação por tipo, horários, datas e números de repetição.
- Antecedência, situação/envio de lembretes e conclusão manual.
- Unicidade de e-mail, recuperação, token, lembrete, notificação por versão e chave idempotente por usuário/ação.
- Os quatro CHECKs de nomes da DEC-MV-08.

Nos casos com NULL, confira a semântica real do PostgreSQL, inclusive interações entre CHECK, NOT NULL, FK e UNIQUE. Não aprove um teste que falha por uma coluna obrigatória omitida quando deveria exercitar outra restrição. Confira SQLSTATE e, quando necessário para identificar a causa, a restrição efetivamente violada.

### 6.3. Valores e timestamps

Verifique:

- Decimal e limites de NUMERIC; ida e volta sem conversão para float.
- `JSON(none_as_null=True)`, com `resposta=None` explícito no ORM e comprovação de SQL NULL; caso positivo com objeto JSON.
- Ausência de `default=` no ORM, exceto IDs, conforme REC-MV-033.
- Mixin somente nas oito tabelas previstas; nomes especiais de criação preservados; remoção do TimestampMixin antigo.
- Datas e horas com os tipos aprovados, sem confundir Date/Time com timestamps que exigem fuso.
- CT-F2-19: criação, atualização por ORM em transação posterior, preservação de criado_em, leitura sem I/O tardio e comportamento do UPDATE textual sem trigger.
- Herança de `eager_defaults`.

Distinga duas alegações: o atributo estar carregado depois do flush e ele ter voltado por RETURNING na própria instrução. Se o contrato afirmar a segunda, uma verificação apenas de atributo não prova o SQL emitido. Inspecione ou faça uma sonda pequena com captura de comandos se necessário; não prescreva outra estratégia antes de observar o comportamento da versão instalada.

### 6.4. Limites da fase e do produto

Não existem novos services, routers, endpoints ou schemas Pydantic nesta fase. Não há integrações bancárias, Open Finance, gateways, execução real de pagamentos, saldo manual ou estruturas preparadas para essas integrações.

As categorias e formas de pagamento são dados descritivos internos. Não confunda seeds de categorias com movimentações financeiras de usuários.

## 7. Auditoria da migração e dos seeds

1. Confirme uma única revisão `0001`, `down_revision=None` e ausência de ramificações inesperadas.
2. Compare a revisão gerada preservada com a final. Justifique cada alteração por §8.2/§8.3; não aceite mudanças de domínio disfarçadas de formatação.
3. Confira a ordem de criação/remoção, constraints, índices, defaults e CHECKs gerados pelos tipos Enum.
4. Confira que a revisão não importa `api_gestao_pessoal` ou modelos vivos e usa construções locais estáveis.
5. Verifique os nomes e acentos exatos das trinta categorias: seis de atividades, oito de importâncias, seis de receitas e dez de despesas; todas ativas.
6. Confira UUIDv7, IDs distintos e as chaves naturais usadas no ON CONFLICT.
7. Verifique a execução dos seeds pelo upgrade real e sua reexecução explícita pelo CT-F2-07. Repetir `upgrade head` sozinho não prova idempotência do corpo dos seeds, porque a revisão já pode estar aplicada.
8. Confira preservação dos registros existentes na reexecução, sem duplicação nem troca de IDs por comportamento diferente do DO NOTHING contratado.
9. Confira upgrade em banco vazio, downgrade e novo upgrade, sempre em banco descartável.
10. Confira `alembic check` com comparação de tipos e defaults habilitada; não altere flags ou filtros para esconder divergências.
11. Examine a fronteira transacional. Se os testes não comprovarem a propriedade alegada de rollback da migração, execute uma sonda mínima em banco descartável que provoque falha depois dos seeds da revisão entregue e confira o estado por outra conexão. Não use apenas a revisão sintética de três tabelas da decisão D1 como prova da entrega de treze tabelas.
12. Confira a compatibilidade offline declarada com a revisão entregue. Use a API do Alembic com `config.attributes["url_banco"]` fictícia e explícita, `config.attributes["configurar_logging"]=False`, captura do SQL fora do repositório e modo `sql=True`. Não use as configurações reais.

Para offline, primeiro leia `env.py` e confirme o caminho sem leitura do `.env` e sem conexão. Verifique DDL e INSERTs com valores literais. Se a validade do SQL ainda ficar incerta, aplique-o exclusivamente em outro banco descartável. Registre separadamente geração e execução; uma não comprova a outra.

Não transforme a sonda em implementação paralela nem copie um script gerado de uma revisão diferente para alegar validação da revisão entregue.

## 8. Auditoria dos testes e do isolamento

Leia os testes e os helpers antes de executá-los.

- CT-F2-02 deve comparar a introspecção com valores literais provenientes do contrato, não com o próprio metadata.
- CT-F2-10 deve verificar nomes, ordem das colunas dos índices e estrutura no banco, não somente conjuntos construídos pelos modelos.
- Casos negativos precisam atingir a restrição pretendida; casos positivos precisam efetivamente persistir dentro da transação do teste e ser consultáveis.
- O helper de violação deve provar exceção DBAPI e SQLSTATE corretos; uma exceção não relacionada ou um bloco de pytest mal colocado não pode contar como sucesso.
- SAVEPOINT e rollback devem manter os casos independentes. Inspecione tratamento de falha e finalização.
- `limpar_dados` deve validar o banco descartável e truncar somente a lista contratada, preservando os catálogos e `alembic_version`. Sem CASCADE/RESTART IDENTITY.
- A URL deve vir do container. Não aceite um nome contendo “teste” como única guarda.
- As novas fixtures não podem modificar SettingsTeste, reintroduzir leitura do `.env` ou alterar os contratos de infraestrutura protegidos.
- Engines, conexões e sessões devem ser encerradas. Testes de downgrade não podem deixar transações que bloqueiem DROP.
- Migração por sessão deve usar o caminho síncrono especificado; não introduzir conflitos de loop de eventos.
- Confira exatamente a alteração permitida do CT-F1-17; CT-F1-18 e CT-F1-19 devem continuar preservados.
- Commit explícito de dados nos testes fica limitado ao caso autorizado CT-F2-19, além da gestão transacional de DDL do Alembic e da limpeza já especificada. Diferencie isso de um commit indevido em código de aplicação.

Monte o mapa CT → node ID real → prova → resultado. A execução -q do Sonnet não torna o resultado inválido; ela simplesmente não substitui essa análise de cobertura.

F2 não exige stress/concorrência. Não invente esse gate agora. Também não exija OpenAPI, autenticação ou comportamentos de service de fases ainda não implementadas.

## 9. Execução independente e comandos

### 9.1. Ambiente e logs

Confira as versões locais, Docker e o lock. O relatório declarou Python 3.14.6, SQLAlchemy 2.1.4, Alembic 1.20.0, uv 0.11.29 e Docker 29.7.2. Confira também as ferramentas de qualidade e testes pelas versões instaladas/lock.

Digest declarado:

`postgres@sha256:fe0737ba566a2c5b2a28f34433c0a423261900ec17b9bf7ad115e1aae7e57f1b`

Não instale, atualize ou sincronize dependências automaticamente no objeto auditado. Os comandos abaixo usam `--frozen --no-sync` para preservar lock/ambiente. Se o ambiente não contiver o necessário ou uma opção não estiver disponível, registre o impedimento; não altere silenciosamente o ambiente ou o comando.

Crie uma pasta exclusiva de evidências e use Bash. Exemplo de executor que preserva a saída e o código real:

~~~bash
MV_AUDITORIA_BASE="$HOME/minhavida_evidencias"
mkdir -p -- "$MV_AUDITORIA_BASE"
MV_AUDITORIA_DIR="$(mktemp -d "$MV_AUDITORIA_BASE/f2_auditoria_XXXXXXXX")"
export MV_AUDITORIA_DIR

auditar() {
    local nome="$1"
    shift
    local arquivo="$MV_AUDITORIA_DIR/$nome.log"
    local comando="$MV_AUDITORIA_DIR/$nome.comando"
    local rc

    if [ -e "$arquivo" ] || [ -e "$comando" ]; then
        printf 'Evidência já existe: %s\n' "$nome" >&2
        return 2
    fi

    printf '%q ' "$@" > "$comando"
    printf '\n' >> "$comando"

    if "$@" > "$arquivo" 2>&1; then
        rc=0
    else
        rc=$?
    fi

    printf '\ncodigo_saida=%s\n' "$rc" >> "$arquivo"
    cat -- "$arquivo"
    return "$rc"
}
~~~

Execute as chamadas na mesma sessão Bash, ou carregue a função de um script salvo exclusivamente no diretório de evidências. Reutilize o diretório escolhido; não o substitua a cada comando. Se houver nova execução, use novo nome de log. Não use o retorno de `tee` ou `echo` como se fosse o código do comando auditado.

### 9.2. Ordem mínima

Depois de identificar e manifestar o objeto:

~~~bash
auditar 01_uv uv --version
auditar 02_python uv run --frozen --no-sync python --version
auditar 03_docker docker version --format '{{.Server.Version}}'
auditar 04_imagem docker image inspect --format '{{index .RepoDigests 0}}' postgres:15-alpine

auditar 10_esquema uv run --frozen --no-sync pytest tests/esquema -vv --color=no
auditar 11_regressoes uv run --frozen --no-sync pytest tests/infra/test_alembic_ambiente.py tests/infra/test_configuracao.py::test_importacao_sem_efeitos -vv --color=no

auditar 20_ruff uv run --frozen --no-sync ruff check --no-fix .
auditar 21_formato uv run --frozen --no-sync ruff format --check .
auditar 22_pyright uv run --frozen --no-sync pyright

auditar 30_heads uv run --frozen --no-sync alembic heads
auditar 31_history uv run --frozen --no-sync alembic history
auditar 32_compose env POSTGRES_USER=verificacao POSTGRES_PASSWORD=verificacao POSTGRES_DB=verificacao docker compose --env-file /dev/null config --quiet
~~~

O `-vv` é deliberado na auditoria: fornece os node IDs e resultados por caso. Não reexecute só para recuperar uma informação que já esteja disponível no novo log.

Use execução sequencial. Com o mesmo conteúdo entregue, a referência é 41 casos de esquema e quatro regressões, sem skip/xfail. Se o resultado diferir, explique a causa; não modifique coleta ou testes para forçar a contagem.

Os testes e sondas devem comprovar migração/check no PostgreSQL descartável. O sucesso de `heads` e `history` não prova que as tabelas foram criadas corretamente.

Finalize comparando novamente os hashes do objeto, os onze documentos, o lock, o status e o índice. Separe os artefatos administrativos autorizados e caches ignorados. Se o objeto mudou de forma não autorizada durante a auditoria, não aplique o veredito ao conteúdo novo sem explicar e resolver a perda de identidade.

### 9.3. Falhas e ampliação de testes

Quando surgir falha, registre comando, código, saída, condição e origem provável. Uma reprodução do node específico é permitida para esclarecer uma falha concreta. Não repita as seleções grandes por rotina e não corrija o código.

Para sondas, registre antes: dúvida concreta, arquivo/contrato afetado, resultado que confirmaria a hipótese e limite do experimento. Use a menor prova suficiente; não faça mutação sistemática de todos os testes.

A suíte completa não está autorizada por este prompt. Se você demonstrar que é indispensável, apresente, antes de executá-la:

- OBJETIVO DA SUÍTE COMPLETA.
- POR QUE OS TESTES DIRECIONADOS NÃO SÃO SUFICIENTES.
- MUDANÇAS OU EVIDÊNCIAS CONCRETAS QUE JUSTIFICAM A EXECUÇÃO.

“Para garantir”, “por segurança” ou “porque terminou” não justificam a ampliação.

## 10. Pendências herdadas da F1

Avalie somente o que esta fase efetivamente altera ou exercita:

| Achado | Verificação na F2 |
| --- | --- |
| ACH-MV-F1-005 | Ruff e Pyright realmente incluem Alembic; somente a exceção PLC0415 aprovada para env.py; sem exceções adicionais |
| ACH-MV-F1-006 | Precisão do relatório e dos logs: tentativas, falhas intermediárias, reexecuções, comandos e códigos reais |
| ACH-MV-F1-007 | Compose com --env-file /dev/null e operações Alembic sem carregar o .env real |

Não declare encerramento apenas por promessa do implementador. Se houver evidência suficiente, recomende encerramento no relatório. Caso contrário, mantenha acompanhamento com o motivo exato.

ACH-MV-ARQ-006 foi encerrado na conferência da F1. O ACH-MV-ARQ-019 tem lacuna formal histórica, sem invalidar o baseline já reconhecido. Não acrescente uma exigência de commit intermediário.

## 11. Achados e veredito

Use a política do plano de validação §7:

- P0: risco crítico imediato; interromper a ação perigosa.
- P1: violação grave de segurança, isolamento ou integridade.
- P2: descumprimento funcional/contratual relevante ou ausência de prova obrigatória; bloqueia até correção ou decisão explícita.
- P3: questão localizada sem comprometimento dos requisitos obrigatórios ou da confiança na prova; acompanhamento justificado.

Classifique pelo impacto demonstrado. Não rebaixe defeito só porque nasceu no seu prompt, nem transforme qualquer diferença de texto em defeito funcional grave.

Use `ACH-MV-F2-NNN` sem colidir com IDs existentes. Para cada achado:

1. ID, severidade, estado e título.
2. Origem: implementação, teste, especificação, ferramenta, ambiente ou evidência.
3. Fato e fonte com caminho/seção/linha.
4. Reprodução, comando, resultado e log.
5. Impacto e fases afetadas.
6. Correção recomendada, sem aplicá-la.
7. Critério objetivo de encerramento.
8. Necessidade ou não de decisão do usuário.

Vereditos:

- `APROVADO`: requisitos e provas obrigatórias satisfeitos, sem pendências.
- `APROVADO_COM_P3`: requisitos e provas obrigatórias satisfeitos, somente P3 justificados.
- `BLOQUEADO`: P0/P1/P2 aberto, decisão indispensável pendente ou impossibilidade de verificar requisito obrigatório.

Uma hipótese não verificada não é fato comprovado. Uma verificação que não pôde ser feita não é teste aprovado. Se a limitação impede o veredito, indique a prova mínima que falta.

## 12. Reconciliação documental

Nesta tarefa, preserve os documentos normativos existentes e o Prompt F2 implementado. Produza no relatório um anexo com as alterações propostas, sem aplicá-las:

1. Arquitetura §10.5: incorporar a emenda F2-D1 já aprovada.
2. Plano de fases, F2 item 10: corrigir §14 para §13.
3. Prompt F2 §12, passo 8: registrar `ls -A1` como emenda operacional histórica.
4. Plano de fases, orientação offline: substituir a sugestão de CLI que carregaria configurações pela API com URL explícita e controlada.
5. Índice: registrar a aprovação da emenda D1 e, quando autorizado o fechamento documental, o resultado real da auditoria.
6. D4: propor a correção compatível com a conclusão técnica, preservando o histórico do que foi solicitado e executado.

Separe “já aprovado, falta incorporar ao documento” de “nova decisão solicitada”. Não peça outra aprovação arquitetural para D1/D2/D3. Não invente aprovação da D4.

A falta de incorporação física de uma emenda válida não torna a implementação divergente dessa emenda. Avalie o impacto documental pela política existente, sem abrir uma nova rodada completa de auditoria por rotina.

## 13. Entregáveis permitidos

### 13.1. Relatório obrigatório

Crie:

`docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md`

Se já existir, preserve a evidência anterior e registre a nova execução de forma identificada; não apague o histórico para substituir um veredito.

Conteúdo obrigatório:

1. Veredito e impedimentos, se houver.
2. Objeto auditado: baseline, HEAD, modo, arquivos, emendas e manifestos.
3. Fontes lidas e hashes completos, sem valores inventados ou truncados.
4. Escopo autorizado versus diff real, com arquivos novos.
5. Ambiente, versões, imagem e diretório das evidências.
6. Mapa CT → node ID → resultado → evidência, incluindo os casos de NULL e controles positivos.
7. Comandos executados, códigos reais, linhas finais literais e duração disponível.
8. Resultados da revisão de modelos, migração, seeds, fixtures e qualidade.
9. Análise específica da D4.
10. Achados P0/P1/P2/P3 e pendências da F1.
11. Provas próprias, evidências reaproveitadas e limites.
12. Manifesto antes/depois mostrando preservação do objeto; declare separadamente os arquivos administrativos criados.
13. Anexo das reconciliações documentais propostas.
14. Próxima ação concreta do usuário.

Preserve saídas brutas fora do repositório e referencie-as. Não apresente uma reprodução sua como log original do Sonnet.

### 13.2. Se houver correção de implementação necessária

Você pode criar, sem alterar o objeto:

`PROMPTS/PROMPT_MASTER_SONNET_5_F2_CORRECOES_POS_AUDITORIA.md`

O prompt deve ser restrito aos achados comprovados e conter baseline/manifesto do objeto atual, fontes, arquivos permitidos, correções exatas, testes diretamente afetados, critérios de aceite, Etapa A e parada antes de implementar.

- Se todas as decisões necessárias já estiverem aprovadas: `PRONTO_PARA_ETAPA_A`.
- Se depender de decisão nova: `RASCUNHO — BLOQUEADO`, com a decisão concreta.
- Não autorize a Etapa B em nome do usuário.
- Não inclua mudanças de preferência arquitetural, novo escopo ou suíte completa automática.
- Se restarem apenas erratas documentais, não invente correções de código nem crie um prompt de implementação desnecessário.

### 13.3. Se a F2 for aprovada

Informe que o usuário pode preparar o commit do objeto aprovado, respeitando as pendências documentais explicitadas e a identidade dos arquivos. Não faça staging, commit ou push.

A auditoria não cumpre G6 e não autoriza F3. Não crie Prompt F3 nesta tarefa; DEC-MV-09 a 13 continuam fora desta autorização.

## 14. Critérios de aceite da própria auditoria

A auditoria estará entregue quando:

- O objeto estiver identificado de forma reproduzível e preservado.
- As emendas aprovadas tiverem sido aplicadas à leitura normativa.
- Todo o escopo F2 tiver sido revisado, incluindo arquivos novos.
- As verificações direcionadas tiverem sido executadas ou suas impossibilidades explicadas com impacto no gate.
- A cobertura tiver sido confrontada com o contrato, além das contagens.
- D4 tiver recebido diagnóstico explícito, sem pré-julgamento.
- Achados, limitações e pendências tiverem critérios de encerramento.
- O veredito estiver fundamentado em evidência real.
- Nenhuma correção tiver sido feita pelo auditor no objeto.
- O relatório tiver sido salvo e a próxima ação estiver clara.

Não exige suíte completa, novo commit, push, implementação de fase futura nem fechamento artificial de todos os P3 históricos.

## 15. Interrupção e retomada

Se a sessão for interrompida, preserve no diretório de evidências um estado de retomada com:

- objeto e manifestos;
- fontes já lidas;
- comandos concluídos e seus logs;
- sondas concluídas;
- achados e dúvidas;
- próximo passo.

Ao retomar, confira a identidade do objeto e continue do ponto válido. Não repita testes aprovados contra o mesmo conteúdo apenas porque houve troca de sessão. Se algum arquivo mudou, reavalie somente a evidência afetada e amplie apenas por risco concreto.

Se ocorrer uma condição insegura, pare a operação afetada, descreva a causa e continue apenas com verificações que permaneçam válidas e seguras. Não transforme indisponibilidade de Docker em skip ou aprovação.

## 16. Resposta final e parada

Responda ao usuário com:

1. `F2: APROVADO`, `F2: APROVADO_COM_P3` ou `F2: BLOQUEADO`.
2. O que foi comprovado e o que ficou sem verificação.
3. Achados impeditivos e P3, em separado.
4. Diagnóstico da D4.
5. Arquivos de auditoria criados e caminhos das evidências.
6. Uma próxima ação concreta: commit pelo usuário, decisão pontual ou correção dirigida pelo Sonnet.

Depois, pare. Não implemente correções, não inicie F3 e não declare integração concluída.

**Comece agora pela identificação do objeto e pela leitura das fontes.**

