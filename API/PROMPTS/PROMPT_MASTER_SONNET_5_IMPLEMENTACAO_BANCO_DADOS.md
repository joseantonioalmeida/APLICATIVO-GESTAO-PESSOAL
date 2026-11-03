# Prompt Master — Sonnet 5 — Fundação do banco de dados MinhaVida

Você é o desenvolvedor backend sênior responsável pela API de Gestão Pessoal e Finanças, chamada MinhaVida. Sua tarefa é implementar a fundação de persistência da API com **PostgreSQL, SQLAlchemy assíncrono e Alembic usando conexão assíncrona**, seguindo integralmente o contrato de tabelas reproduzido no Anexo A.

Entregue código real, migrações executáveis, testes de integração e documentação de execução. Respeite o fluxo de aprovação do projeto antes de modificar arquivos. Depois da aprovação aplicável, avance até concluir este escopo; uma proposta de arquitetura ou exemplos isolados não constituem a entrega.

## 1. Fontes, contexto e autoridade

Leia este prompt inteiro, incluindo o Anexo A, antes de elaborar o plano.

As fontes desta tarefa são:

1. **Esta solicitação:** PostgreSQL como banco; SQLAlchemy async como ORM; Alembic com conexão async para migrações; implementação da fundação de persistência.
2. **O `CLAUDE.md` real do repositório:** regras de arquitetura, organização, qualidade e fluxo de trabalho. Localize e leia integralmente o arquivo, além das instruções aplicáveis aos diretórios que serão alterados. Não suponha seu conteúdo.
3. **O contrato de tabelas do Anexo A:** fonte de verdade para tabelas, colunas, nomes, tipos, nulabilidade, padrões declarados, relacionamentos, restrições, índices e dados iniciais.
4. **As diretrizes e os requisitos funcionais do projeto:** contexto para interpretar a finalidade dos dados e distinguir persistência de regras dos serviços.

O Anexo A é uma cópia integral do arquivo `Texto colado(20261009-000013).txt`, cujo SHA-256 é `907f2509659cd11a3f620dc8945d7d7c3044040cc4a53c64b44ea9c81eed830c`.

O segundo anexo fornecido pelo usuário, `Texto colado (2)(6).txt`, contém diretrizes de sistema, requisitos das telas e a mesma especificação de tabelas. Seu SHA-256 é `7627ab94bf8d34f5599a6c02d1714cbe26ba00f6f9ff1ba6a240d46bff37b97d`. Algumas linhas iniciais desse texto estão interrompidas por `>`; não complete esses trechos por suposição. Esse anexo não substitui a leitura do `CLAUDE.md` real.

Se o arquivo original de tabelas estiver disponível no repositório, confira seu conteúdo com o Anexo A. Se estiver ausente, o Anexo A fornece o contrato completo para esta tarefa. Se houver divergência relevante entre versões, apresente a diferença e solicite a definição da versão correta antes de implementar o ponto afetado.

A observação antiga do contrato de que o SGBD ainda não foi escolhido está resolvida pela solicitação atual: **usar PostgreSQL**. A alternativa mencionada para SQLite não se aplica. Essa adaptação não autoriza redesenhar as entidades ou alterar seus campos.

Não modifique `CLAUDE.md`, o contrato ou as regras de qualidade para acomodar sua implementação. Se uma instrução do projeto entrar em conflito com o escopo solicitado, exponha o conflito concreto. Se não localizar `CLAUDE.md`, conclua o diagnóstico que puder realizar em modo de leitura e peça sua localização antes de iniciar mudanças no projeto.

## 2. Conduta e fluxo de trabalho

As diretrizes fornecidas estabelecem comunicação, comentários e documentação em PT-BR; nomes de arquivos, variáveis e funções em `snake_case`; classes em `PascalCase`; uso de SQLAlchemy `AsyncSession` e Alembic; validação com Ruff e Pyright; e proibição de executar commits por iniciativa própria.

Respeite especialmente a regra de **Zero Surpresas**: explique o plano concreto de alterações e obtenha a aprovação exigida pelo `CLAUDE.md` antes de criar, alterar, excluir ou refatorar arquivos. Se já houver aprovação explícita e suficiente para esse plano no contexto, prossiga sem pedi-la novamente. Este prompt não dispensa as aprovações do projeto.

Comece com uma etapa somente de leitura:

1. Localize a raiz do repositório e leia as instruções aplicáveis.
2. Inspecione `git status`, o diff existente, a estrutura de diretórios, `pyproject.toml`, o arquivo de lock, a versão de Python, as dependências, a configuração, os modelos e os testes existentes.
3. Confira se já há Alembic, revisões, heads, banco de desenvolvimento e convenções de nomes para constraints. Não crie uma segunda configuração concorrente.
4. Identifique o framework real e sua organização. Não presuma FastAPI nem invente uma arquitetura incompatível com o código encontrado.
5. Compare o contrato com o estado atual e apresente os arquivos que serão criados ou alterados, dependências necessárias, migrações previstas, estratégia de testes e eventuais decisões pendentes.
6. Preserve mudanças anteriores do usuário. Não use `git reset --hard`, `git clean`, restauração indiscriminada de arquivos ou reescrita de histórico. Não execute `git commit`, push ou publicação.

Faça perguntas somente quando houver uma decisão de negócio, uma divergência entre fontes, ausência de instrução indispensável ou a aprovação exigida pelo projeto. Resolva escolhas técnicas rotineiras com base no repositório e explique as escolhas relevantes no plano.

## 3. Escopo da implementação

Implemente:

- Configuração da conexão PostgreSQL por variáveis de ambiente, integrada ao padrão existente.
- Engine assíncrona, fábrica de sessões, ciclo de vida e limites transacionais claros.
- Base declarativa e modelos tipados das 13 tabelas do contrato.
- PKs, FKs simples e compostas, unicidades, CHECKs, padrões e índices previstos.
- Configuração Alembic async e revisões necessárias para chegar ao esquema especificado.
- Os catálogos iniciais de categorias, com todos os valores exatos do contrato.
- Testes de integração em PostgreSQL real para migrações, persistência assíncrona e integridade.
- Documentação curta de configuração, execução, validação e regras que permanecem nos serviços futuros.

Esta etapa não inclui endpoints de CRUD, autenticação completa, envio de e-mails, processamento de notificações, geração de recorrências, relatórios, dashboard, motor de pagamentos ou middleware de idempotência. Crie as estruturas de dados correspondentes, mas não declare esses fluxos implementados apenas porque as tabelas existem.

Não acrescente entidades como conta bancária, carteira, cartão de crédito, orçamento, dispositivo, sessão de login, token JWT, auditoria genérica ou outbox. Não crie uma tabela por tela. Não separe receitas e despesas em duas tabelas.

Não introduza camadas, repositórios genéricos, abstrações ou infraestrutura sem necessidade para este escopo. Reutilize os padrões e componentes existentes. Se faltar PostgreSQL para testes, proponha a menor configuração local compatível com o projeto, sem acrescentar serviços externos ao domínio.

## 4. Fidelidade estrutural ao contrato

O contrato contém **13 tabelas e 134 colunas de domínio**:

| Tabela | Classe sugerida, se o projeto não tiver convenção diferente | Colunas |
| --- | --- | ---: |
| `usuario` | `Usuario` | 8 |
| `recuperacao_senha` | `RecuperacaoSenha` | 10 |
| `categoria_atividade` | `CategoriaAtividade` | 3 |
| `serie_atividade` | `SerieAtividade` | 15 |
| `atividade` | `Atividade` | 15 |
| `categoria_importancia` | `CategoriaImportancia` | 3 |
| `serie_importancia` | `SerieImportancia` | 17 |
| `importancia` | `Importancia` | 15 |
| `categoria_financeira` | `CategoriaFinanceira` | 4 |
| `movimentacao_financeira` | `MovimentacaoFinanceira` | 15 |
| `lembrete_importancia` | `LembreteImportancia` | 11 |
| `notificacao` | `Notificacao` | 8 |
| `requisicao_idempotente` | `RequisicaoIdempotente` | 10 |
| **Total** | | **134** |

A tabela técnica `alembic_version` não faz parte dessa contagem. Se já existirem outras tabelas no projeto, identifique-as; a contagem não autoriza apagá-las.

Crie uma matriz de rastreabilidade verificável entre o Anexo A, os modelos e a migração. Ela deve permitir conferir cada coluna e cada restrição, não apenas os totais. Uma contagem correta não compensa um nome, tipo ou relacionamento incorreto.

Regras obrigatórias:

- Preserve todos os nomes físicos em `snake_case`, inclusive `notificacao.criada_em`, que difere de `criado_em` nas outras tabelas.
- Preserve `excluida_em` em `atividade`, `importancia` e `movimentacao_financeira`. Não troque por `deleted_at` ou `excluido_em`.
- Todos os `id` são `Integer`, PK, não nulos e gerados pelo PostgreSQL. Use uma estratégia compatível com `autoincrement=True` e com o padrão do projeto. FKs não têm geração automática.
- Preserve tamanhos de `VARCHAR`, precisão e escala monetárias, nulabilidade e padrões explicitamente declarados. Não transforme tudo em `Text`, `BigInteger`, UUID ou JSON.
- Não adicione campos por meio de mixins indiscriminados. Os catálogos e `notificacao`, por exemplo, não possuem o mesmo conjunto de campos de auditoria.
- Não invente padrões para fuso, periodicidade, categoria ou horários quando o contrato da coluna não os define. Diferencie um valor inicial do formulário de um `server_default` do banco.
- Armazene `senha_hash`; não crie `senha` em texto puro nem `confirmar_senha`. Não persista códigos de recuperação em texto puro.
- Preserve os três catálogos separados. Eles são compartilhados entre usuários e não possuem `usuario_id`.
- Situação de atividades e importâncias, atraso, saldo, duração, totais e gráficos permanecem calculados. Não adicione colunas para esses resultados.
- Preserve as colunas `situacao` que o contrato efetivamente define para lembretes e requisições idempotentes.
- Não acrescente uma FK de pagamento em `importancia`. O vínculo financeiro fica somente em `movimentacao_financeira.importancia_id`.

## 5. PostgreSQL e mapeamento SQLAlchemy

Use SQLAlchemy no estilo tipado 2.x, com `DeclarativeBase`, `Mapped[...]` e `mapped_column`, respeitando versões compatíveis com o projeto. Não atualize dependências sem relação com esta tarefa. Mantenha o arquivo de lock coerente com as mudanças aprovadas.

### 5.1. Tipos e valores

| Contrato | Mapeamento esperado |
| --- | --- |
| `INT` | `Integer` |
| `SMALLINT` | `SmallInteger` |
| `VARCHAR(n)` | `String(n)` ou Enum textual com comprimento explícito equivalente |
| `BOOLEAN` | `Boolean` |
| `DATE` | `Date`, com `datetime.date` no Python |
| `TIME` | `Time(timezone=False)`, com `datetime.time` para horário civil |
| `DATETIME em UTC` | `DateTime(timezone=True)`, correspondente a `TIMESTAMP WITH TIME ZONE` no PostgreSQL |
| `DECIMAL(12,2)` | `Numeric(12, 2, asdecimal=True)`, com `Decimal` no Python |
| `JSON` | `JSON`; não substituir por `JSONB` por preferência pessoal |

Use instantes conscientes de fuso e normalize-os para UTC. Preserve datas civis e horários locais; não converta `data_movimentacao` em timestamp nem desloque a data de um pagamento por conversão de fuso. O nome IANA permanece em `usuario.fuso_horario`; o timestamp do PostgreSQL não preserva sozinho essa identificação.

Nunca use `float` para dinheiro. O limite individual é `9.999.999.999,99`; os valores persistidos de movimentações são positivos e seu significado depende de `tipo`. `Numeric(12,2)` não substitui a futura validação da entrada: o PostgreSQL pode ajustar a escala, por isso a aplicação deverá rejeitar mais de duas casas antes da gravação. Não afirme que uma coluna numérica isolada cumpre essa regra de entrada.

Para domínios controlados, use enumerações Python com armazenamento textual e constraints de banco. Escolha consistentemente `String` com `CheckConstraint`, ou `Enum(native_enum=False, create_constraint=True, validate_strings=True)` com comprimento e valores persistidos explicitamente corretos. Não crie tipos ENUM nativos do PostgreSQL, pois o contrato define `VARCHAR`.

Preserve os valores técnicos, como `MEDIA`, `CARTAO_DEBITO` e `EM_PROCESSAMENTO`, sem acentos e exatamente como especificados. Não reduza `VARCHAR(20)` ao comprimento inferido do maior membro de uma enumeração.

Use `server_default` para os padrões persistentes declarados no contrato, mantendo eventual default do ORM consistente. Configure uma estratégia explícita para criação e atualização dos timestamps. Diferencie `server_default`, `onupdate` do SQLAlchemy e atualização automática no banco; documente a cobertura real, inclusive para atualizações SQL que não passem pelo ORM. Não acrescente triggers sem justificar sua necessidade no plano.

Trate corretamente a diferença entre SQL `NULL` e JSON `null` em `requisicao_idempotente.resposta`; a coluna opcional deve permitir ausência real de resposta. Não grave credenciais, códigos ou tokens nessa resposta.

### 5.2. Integridade e propriedade dos dados

Crie `ForeignKeyConstraint` para cada par abaixo. Duas FKs independentes não cumprem essa regra.

| Origem | Destino |
| --- | --- |
| `atividade(serie_id, usuario_id)` | `serie_atividade(id, usuario_id)` |
| `importancia(serie_id, usuario_id)` | `serie_importancia(id, usuario_id)` |
| `movimentacao_financeira(importancia_id, usuario_id)` | `importancia(id, usuario_id)` |
| `lembrete_importancia(importancia_id, usuario_id)` | `importancia(id, usuario_id)` |
| `notificacao(lembrete_id, usuario_id)` | `lembrete_importancia(id, usuario_id)` |
| `movimentacao_financeira(categoria_id, tipo)` | `categoria_financeira(id, tipo)` |

Adicione as chaves únicas de destino requeridas: `(id, usuario_id)` nas quatro tabelas de destino com propriedade e `(id, tipo)` em `categoria_financeira`. Preserve também a FK direta de cada `usuario_id` para `usuario.id`.

As FKs compostas de propriedade substituem a FK simples do relacionamento correspondente. Não use `MATCH FULL` nos pares opcionais com `usuario_id`, pois o registro avulso tem o ID relacionado nulo e o usuário obrigatório preenchido. As regras de preenchimento conjunto de série/número continuam sendo CHECKs próprios.

Implemente todas as unicidades do contrato, inclusive:

- E-mail; uma recuperação por usuário; hash do token de redefinição quando preenchido.
- Nomes dos catálogos de atividade e importância; par `(tipo, nome)` do catálogo financeiro.
- `(serie_id, numero_ocorrencia)` em atividade e importância, inclusive para ocorrências excluídas logicamente.
- `movimentacao_financeira.importancia_id` quando preenchido, garantindo um pagamento por ocorrência.
- `lembrete_importancia.importancia_id`, garantindo um lembrete por ocorrência.
- `(lembrete_id, versao_agendamento)` em notificação.
- `(usuario_id, acao, chave)` em requisição idempotente.

O PostgreSQL deve continuar aceitando múltiplos registros avulsos com série nula, múltiplas movimentações sem importância e múltiplos tokens de redefinição nulos. Não use `NULLS NOT DISTINCT` nessas unicidades opcionais. Não substitua a unicidade das ocorrências por índice que ignore excluídas, pois isso permitiria recriar ocorrências removidas.

Implemente os CHECKs expressamente definidos no contrato: domínios textuais; nome da atividade com 3 a 100 caracteres; horário final maior que inicial; limites de números e datas das séries; pares de campos preenchidos em conjunto; valores previstos condicionados a `possui_despesa`; conclusão manual somente sem despesa; valores financeiros positivos; vínculo permitido somente para despesa; remoção de vínculo em movimentação excluída; formas financeiras permitidas conforme o tipo; antecedências permitidas; e coerência entre situação do lembrete e `enviado_em`.

Para condições envolvendo colunas opcionais, escreva `IS NULL` e `IS NOT NULL` explicitamente quando necessário. No PostgreSQL, um CHECK que resulta em `NULL` não rejeita a linha. Por exemplo, apenas `valor_previsto > 0` não exige preenchimento quando `possui_despesa` é verdadeiro.

Não imponha limites arbitrários ou regras ausentes da fonte. Em particular, `numero_final = 0` é válido; uma ocorrência concluída pode existir além do limite atual de geração; `NENHUMA` é um valor permitido em séries; e notificações antigas não devem ter sua versão vinculada por FK à versão corrente mutável do lembrete.

Use nomes estáveis e distintos para constraints e índices, respeitando os limites do PostgreSQL. Inspecione o SQL gerado. Configure relacionamentos ORM sem ambiguidades nas FKs compartilhadas, com joins, lado gravável e `back_populates` coerentes. Não use `overlaps` apenas para esconder uma colisão de escrita; comprove que associar objetos não modifica indevidamente `usuario_id` ou `tipo`.

As FKs de propriedade protegem associações, não substituem a autorização de acesso. Registre que consultas futuras precisam ser filtradas pelo usuário autenticado; esta etapa não implementa uma política completa de autorização nem acrescenta RLS sem previsão no projeto.

### 5.3. Exclusão e índices

Use `RESTRICT` ou `NO ACTION` nas referências de negócio, de forma consistente. Categorias referenciadas não podem ser apagadas fisicamente. Preserve a estratégia de exclusão lógica do contrato.

Não configure cascata que apague uma movimentação ao remover uma importância ou desfazer um vínculo. Não use `delete-orphan` nesse relacionamento. Não use `SET NULL` genérico em FK composta com `usuario_id`. Não invente exclusão definitiva em cascata de uma conta, cujo fluxo ainda não está definido.

Crie os oito índices iniciais, com a ordem exata das colunas:

1. `atividade(usuario_id, data_atividade)`.
2. `atividade(usuario_id, concluida_em, data_atividade)`.
3. `importancia(usuario_id, data_compromisso)`.
4. `movimentacao_financeira(usuario_id, data_movimentacao)`.
5. `movimentacao_financeira(usuario_id, tipo, data_movimentacao)`.
6. `movimentacao_financeira(usuario_id, categoria_id, data_movimentacao)`.
7. `lembrete_importancia(situacao, agendado_para)`.
8. `notificacao(usuario_id, lida_em, criada_em)`.

Esses índices não substituem as constraints únicas. Evite duplicar índices já fornecidos por PKs e unicidades. Qualquer índice adicional precisa de uma consulta ou necessidade concreta identificada no projeto e de justificativa no plano.

## 6. Infraestrutura assíncrona

Use `create_async_engine`, `async_sessionmaker` e `AsyncSession`. Na ausência de um driver PostgreSQL assíncrono já adotado, utilize `asyncpg` e URL `postgresql+asyncpg://...`. Se o projeto já tiver outro driver PostgreSQL com suporte async configurado, preserve-o quando compatível e explique a escolha. Não use driver síncrono na execução normal da API.

Obtenha a URL pela configuração existente; forneça exemplo sem credenciais reais. Não registre a senha do banco em logs ou relatórios. Não crie engines e conexões como efeito colateral de importar os modelos.

A infraestrutura deve ter fábrica reutilizável de sessões, uma sessão por unidade de trabalho, fechamento garantido e descarte da engine no encerramento aplicável. Use `expire_on_commit=False` para o fluxo assíncrono, salvo exigência comprovada do projeto com tratamento explícito equivalente. Não compartilhe uma `AsyncSession` entre tarefas concorrentes.

Defina claramente quem inicia, confirma e desfaz transações. Não espalhe commits em modelos, helpers e dependências de maneira que impeça uma operação de negócio atômica. Uma falha deve permitir rollback completo. A infraestrutura deve suportar transações futuras envolvendo importância, movimentação, lembrete e idempotência sem confirmar etapas intermediárias.

Evite I/O implícito ao acessar relacionamentos. Adote carregamento explícito ou eager loading nas consultas de teste e nas integrações necessárias, conforme o padrão do projeto. Verifique o comportamento depois de flush, commit e encerramento de sessão; não esconda `MissingGreenlet` com exceções genéricas.

Use exclusivamente Alembic para evoluir o esquema da aplicação. Não chame `Base.metadata.create_all()` ou `drop_all()` no startup, no fluxo normal da API ou como substituto das migrações nos testes desta entrega.

## 7. Alembic com conexão assíncrona

O Alembic utiliza sua API de migração por meio da conexão adaptada. **Configuração async não significa escrever `async def upgrade()` e `async def downgrade()` nas revisões.** Use o padrão oficial com engine async e `await connection.run_sync(...)` no ambiente de execução; as funções das revisões permanecem `def upgrade()` e `def downgrade()`.

Se não houver Alembic, configure o equivalente ao template `alembic init -t async`, dentro da organização aprovada. Se já houver, adapte a configuração existente e preserve seu histórico. Não crie outra base, não renumere revisões aplicadas e não use `stamp` para simular migrações executadas.

Garanta:

- `target_metadata` apontando para a única base correta, com os 13 modelos efetivamente importados e registrados.
- Configuração de URL sem segredo em `alembic.ini` e sem dependência de importação do servidor HTTP para carregar o metadata.
- Execução online com driver async e transações adequadas; descarte dos recursos da conexão.
- Função de migração adaptável ao modo de execução utilizado pelos testes, sem chamar `asyncio.run()` dentro de um loop já ativo.
- Migrações em ordem de dependência, com reversão coerente de FKs, índices e tabelas.
- Revisão manual do resultado de `--autogenerate`, particularmente CHECKs, unicidades, padrões e FKs compostas; autogeração não é prova de equivalência completa.
- Um histórico válido, sem criar heads paralelos acidentalmente. Se o repositório já tiver mais de um head, explique a situação antes de qualquer tentativa de unificação.

Em projeto novo, crie a migração inicial. Em projeto existente, crie somente as revisões necessárias a partir do estado real. Não destrua tabelas ou dados existentes para fabricar uma base limpa.

## 8. Dados iniciais obrigatórios

Cadastre exatamente **30 categorias**, preservando acentos, grafia e separação por catálogo/tipo:

| Destino | Valores | Quantidade |
| --- | --- | ---: |
| `categoria_atividade` | Trabalho; Estudo; Saúde; Pessoal; Lazer; Outros | 6 |
| `categoria_importancia` | Contas; Compras; Veículo; Lazer; Saúde; Educação; Pessoal; Outros | 8 |
| `categoria_financeira`, `RECEITA` | Salário; Trabalho autônomo; Vendas; Rendimentos; Reembolsos; Outros | 6 |
| `categoria_financeira`, `DESPESA` | Alimentação; Transporte; Moradia; Contas; Compras; Saúde; Educação; Lazer; Veículo; Outros | 10 |

As categorias começam ativas. Não adicione usuários, atividades ou lançamentos financeiros de demonstração na migração.

Para um banco inicial vazio, os catálogos pequenos podem acompanhar a migração inicial, usando estruturas SQLAlchemy locais à revisão. Se o repositório já tiver um mecanismo versionado de seeds, use-o e documente sua execução. As migrações não devem importar modelos vivos da aplicação, cujo código poderá mudar depois.

Evite depender de IDs numéricos fixos. Preserve a geração automática do banco. Executar novamente o fluxo normal de atualização ou o seed reutilizável não pode duplicar categorias; um segundo `alembic upgrade head` sem revisões pendentes deve ser inócuo. Em bases existentes, identifique categorias presentes antes de propor inserções ou alterações.

## 9. Regras dos serviços que a estrutura deverá suportar

Documente estas regras como obrigações da camada de aplicação ainda fora deste escopo. Não as apresente como garantidas por uma simples declaração de modelo:

- Normalização e validação do e-mail; verificação de fuso IANA; bloqueio de nascimento futuro e de movimentação com data posterior a hoje no fuso da conta.
- Hash de senha e de código; geração de código de oito dígitos preservando zeros iniciais; validade, tentativas, reenvio e consumo único do token de recuperação, com operações atômicas.
- Geração limitada de ocorrências; manutenção de `numero_ocorrencia`; datas mensais/anuais de referência; edição e exclusão por alcance; preservação de ocorrências concluídas e excluídas.
- Verificação do estado atual da importância antes de vincular pagamento; exclusão lógica e desvinculação na mesma transação; preservação dos efeitos financeiros ao excluir um compromisso.
- Agendamento e reagendamento de lembretes; incremento de versão somente em mudança real; envio e criação de notificação na mesma transação; preservação de notificações antigas.
- Idempotência com comparação do conteúdo, repetição da resposta, controle de concorrência e gravação atômica com a operação de negócio.
- Consultas por usuário, exclusão de registros removidos dos resultados ativos e cálculos consistentes para os indicadores.

Não implemente CHECKs dependentes de `hoje`, de estado mutável de outra tabela ou de consultas entre linhas para fingir que essas regras de serviço foram resolvidas. Registre na matriz o que o banco garante e o que dependerá dos serviços. Constraints de propriedade e unicidade continuam obrigatórias nesta etapa.

## 10. Verificação obrigatória

Use PostgreSQL real e descartável para testes de integração, com URL de teste explícita, independente da configuração de produção. Não substitua esses testes por SQLite ou mocks. Só execute downgrade, remoção de schema ou limpeza destrutiva após comprovar que o alvo é o ambiente isolado criado para testes; um nome contendo `test` sozinho não comprova isolamento.

Adote as ferramentas de teste já existentes. Se faltarem, inclua apenas dependências compatíveis e necessárias, com justificativa. Os testes devem provar comportamentos do contrato e usar também escrita direta pelo SQLAlchemy Core ou SQL parametrizado para verificar as constraints do banco, sem depender exclusivamente de validações do ORM.

Cubra, no mínimo:

1. **Migração real:** banco vazio de teste → `upgrade head`; verificação da revisão aplicada, das 13 tabelas de domínio e dos catálogos; segundo `upgrade head` sem duplicação. No mesmo ambiente descartável, `downgrade base` e novo `upgrade head` devem funcionar quando aplicável ao histórico do projeto.
2. **Fidelidade do esquema:** todas as 134 colunas, tipos, comprimentos, precisão/escala, nulabilidade, padrões declarados, PKs, FKs, unicidades, CHECKs e oito índices. Use introspecção no banco migrado e comparação com uma expectativa derivada do contrato, além da conferência do metadata. Não compare o modelo somente com uma cópia de si mesmo.
3. **Persistência async:** inserção, consulta, atualização e rollback; geração de IDs; valores padrão; timestamps conscientes de fuso; fechamento de sessões e resolução dos relacionamentos compostos.
4. **Propriedade:** os cinco relacionamentos compostos entre entidades de usuários aceitam o proprietário correto e rejeitam outro usuário, mesmo quando ambos os IDs existem.
5. **Categoria financeira:** rejeição de categoria de receita em despesa e vice-versa; aceite de Outros para ambos os tipos como registros distintos.
6. **Ocorrências:** múltiplas avulsas são válidas; série e número incompletos são rejeitados; número inválido e repetição do par são rejeitados; exclusão lógica não libera o par para recriação; `numero_final = 0` é aceito.
7. **Condições financeiras:** valor zero ou negativo é rejeitado; valor previsto obrigatório quando há despesa e nulo quando não há; pares de vínculo incompletos são rejeitados; receita não pode pagar importância; dois pagamentos não podem ocupar a mesma importância; movimentação excluída não mantém vínculo.
8. **Outros domínios:** formas de movimentação por tipo; horários e datas de série; limites de nome definidos; prioridade e periodicidade inválidas; antecedência e situação de lembrete; coerência de `enviado_em`; conclusão manual vedada quando há despesa. Inclua casos com `NULL` para capturar CHECKs incompletos.
9. **Unicidades de apoio:** recuperação corrente por usuário, tokens preenchidos únicos com múltiplos nulos permitidos, lembrete único por importância, notificação única por versão e chave de idempotência por usuário/ação. Versões antigas de notificação permanecem válidas após alteração da versão corrente do lembrete.
10. **Precisão e conservação:** round-trip de valores `Decimal`, inclusive centavos e limite válido; tentativa de exclusão física de categoria referenciada rejeitada; relacionamentos sem cascatas que apaguem histórico financeiro.

Nos testes negativos, valide a constraint esperada ou o SQLSTATE correspondente; não considere qualquer erro genérico como sucesso. Isole os casos e faça rollback após violações, para não confundir transação abortada com falha da próxima regra. Inclua controles positivos para mostrar que as constraints não bloquearam combinações válidas.

Depois do upgrade, execute `alembic check` com as opções de comparação adequadas ao projeto. Um resultado limpo indica ausência de diferenças detectáveis pelo autogenerate, mas não substitui a introspecção e os testes de CHECKs.

Execute os gates estabelecidos no `CLAUDE.md`, incluindo os comandos fornecidos nas diretrizes:

```bash
uv run ruff check --fix .
uv run ruff format .
uv run pyright
```

Inspecione o baseline e o diff antes de comandos de correção. Se eles alcançarem alterações não autorizadas ou trabalho existente do usuário, resolva esse alcance no plano; não faça uma reformatação global surpresa. Não desative regras, reduza o escopo de tipagem, acrescente ignores indiscriminados ou remova testes para tornar o gate verde. Registre problemas preexistentes separadamente.

Execute também a suíte de testes apropriada e os comandos Alembic pelo gerenciador do projeto. Documente os comandos reais usados, o resultado e os bloqueios. Se não houver PostgreSQL disponível, prepare o código, testes e instruções possíveis, mas indique expressamente que a verificação de integração não foi executada. Não declare sucesso ou invente logs.

## 11. Critérios de conclusão e relatório

Considere a entrega concluída somente quando:

- As mudanças aprovadas estiverem implementadas nos arquivos reais do projeto.
- O contrato de 13 tabelas e 134 colunas estiver atendido integralmente, sem alterações silenciosas.
- O banco migrado tiver as constraints, os oito índices iniciais e os 30 registros de catálogo exigidos.
- O ORM e a conexão operarem de forma assíncrona; o Alembic utilizar a adaptação async correta.
- Os testes em PostgreSQL e os gates do projeto tiverem sido executados com evidências, ou os bloqueios remanescentes estiverem explicitamente declarados como entrega parcial.
- Não houver segredos adicionados, histórico de migrações reescrito ou alterações alheias ao escopo.

Na resposta final, apresente de forma objetiva:

1. O que foi implementado e onde estão os arquivos principais.
2. Como configurar a conexão e executar as migrações e os testes.
3. A conferência de conformidade do contrato, com eventuais divergências ou decisões aprovadas.
4. Resultados reais dos testes, Ruff, Pyright e verificação das migrações.
5. Regras de serviço que permanecem para a próxima etapa e qualquer bloqueio concreto.

Não execute commit e não avance automaticamente para endpoints ou demais funcionalidades. Entregue a fundação do banco dentro do escopo aprovado.

## 12. Referências técnicas oficiais

Use as referências abaixo para conferir a sintaxe compatível com as versões efetivas do projeto. Elas orientam a implementação técnica e não substituem o contrato de domínio:

- [SQLAlchemy — asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html): engine, sessões e cuidados com I/O e concorrência.
- [Alembic — Using Asyncio with Alembic](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic): ambiente async e adaptação da conexão.
- [Alembic — Autogenerate e alembic check](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#running-alembic-check-to-test-for-new-upgrade-operations): verificação e limites da comparação de schema.

## Anexo A — Contrato integral das tabelas

O texto entre os marcadores abaixo reproduz integralmente o arquivo de tabelas fornecido. Preserve-o como referência; observações gerais sobre SGBD não escolhido ou SQLite devem ser lidas à luz da decisão explícita por PostgreSQL neste prompt. Em caso de diferença entre um resumo acima e este contrato, siga o contrato e sinalize a diferença, ressalvada a escolha de stack já definida pelo usuário.

<!-- INICIO_DO_CONTRATO_ORIGINAL -->
TABELAS DO BANCO DE DADOS — PROPOSTA PARA MODELAGEM COM SQLALCHEMY

Este modelo considera os cadastros, as repetições, os pagamentos, os lembretes e a recuperação de senha definidos para o aplicativo. A numeração abaixo corresponde às tabelas, independentemente da numeração das telas.

Os nomes de tabelas e colunas serão escritos em `snake_case`, sem espaços e sem acentos. “Obrigatório” significa `NOT NULL`; “opcional” significa que a coluna aceita `NULL`. Todos os campos `id` serão inteiros, chaves primárias e gerados automaticamente pelo banco. As chaves estrangeiras não terão auto incremento.

O banco de dados ainda não foi informado. Por isso, esta é uma especificação lógica com tipos e restrições a mapear no SQLAlchemy; a migração deverá adaptar auto incremento, datas com fuso e particularidades de índices ao SGBD escolhido.


DECISÕES DA MODELAGEM:

- Armazenar `senha_hash`, usando um algoritmo próprio para senhas, como Argon2id. `confirmar_senha` pertencerá somente ao formulário e à validação da requisição; não será uma coluna.
- Receitas e despesas compartilharão `movimentacao_financeira`, diferenciadas pelo campo `tipo`.
- Cada linha de `atividade` ou `importancia` representará uma ocorrência concreta. Quando houver repetição, uma tabela de série guardará as regras e os valores padrão para gerar as ocorrências.
- Atividades e importâncias sem repetição terão `serie_id = NULL`, sem precisar criar uma série.
- Saldo, totais, duração, prazo, situação de atraso e situação de conclusão serão calculados a partir dos registros, conforme as regras ao final. Isso evita manter valores duplicados que possam divergir.

1 - USUARIO — `usuario`

- id (chave primária, auto incremento, INT, obrigatório).
- nome_completo (VARCHAR(150), obrigatório).
- email (VARCHAR(254), obrigatório, único).
- senha_hash (VARCHAR(255), obrigatório).
- data_nascimento (DATE, obrigatório).
- fuso_horario (VARCHAR(64), obrigatório; exemplo: America/Sao_Paulo).
- criado_em (DATETIME em UTC, obrigatório; preenchido na criação).
- atualizado_em (DATETIME em UTC, obrigatório; atualizado nas alterações).

Regras: normalizar o e-mail de forma consistente no cadastro e no login, adotando nesta proposta remoção de espaços externos e conversão para minúsculas. Aplicar unicidade ao valor normalizado. Validar a estrutura do e-mail e impedir data de nascimento futura na aplicação. O fuso será inicialmente obtido do dispositivo e persistido na conta para permitir cálculos e lembretes quando o usuário não estiver com o aplicativo aberto.

Não criar as colunas `senha` em texto puro nem `confirmar_senha`. O hash já conterá as informações necessárias ao algoritmo de verificação, conforme o formato da biblioteca utilizada.

2 - RECUPERACAO_SENHA — `recuperacao_senha`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório, único).
- codigo_hash (VARCHAR(255), obrigatório; representação protegida do código enviado).
- expira_em (DATETIME em UTC, obrigatório).
- tentativas (INT, obrigatório, padrão 0).
- verificado_em (DATETIME em UTC, opcional).
- token_redefinicao_hash (VARCHAR(64), opcional, único quando preenchido).
- utilizado_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Finalidade: atender às etapas de enviar o código, verificar os oito dígitos e autorizar a nova senha.

Manter uma única recuperação corrente por usuário. No reenvio, substituir o código protegido e a validade, zerar as tentativas e remover a verificação, o token e o uso anteriores. Assim, o código antigo deixa de ser válido. O código informado é uma sequência de oito caracteres numéricos, podendo começar com zero; não deve ser convertido para inteiro nem armazenado em texto puro.

Após verificar o código, emitir um token aleatório de alta entropia, de uso único, para autorizar a etapa de redefinição. Guardar somente seu hash. O campo `token_redefinicao_hash` pode conter um digest hexadecimal de um token forte; isso não significa usar um hash rápido para armazenar senhas ou códigos curtos. Para o código, usar uma proteção adequada, como o hash lento já utilizado para senhas.

Proposta operacional: validade total de dez minutos e até cinco tentativas de código por emissão, com limitação adicional de reenvios na aplicação. O token também deverá respeitar `expira_em`. Verificar o código uma vez não deverá permitir a emissão repetida de novos tokens. Atualizar a senha e marcar `utilizado_em` na mesma transação, validando novamente token, prazo e uso. Utilizar bloqueio ou atualização condicional para que duas solicitações simultâneas não consumam o mesmo token; proteger também a contagem de tentativas concorrentes.

3 - CATEGORIA_ATIVIDADE — `categoria_atividade`

- id (chave primária, auto incremento, INT, obrigatório).
- nome (VARCHAR(50), obrigatório, único).
- ativa (BOOLEAN, obrigatório, padrão verdadeiro).

Dados iniciais: Trabalho, Estudo, Saúde, Pessoal, Lazer e Outros.

Uma categoria desativada continuará disponível no histórico dos registros existentes, mas não será oferecida em novos cadastros. Impedir exclusão física de categoria referenciada.

4 - SERIE_ATIVIDADE — `serie_atividade`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- categoria_id (chave estrangeira → categoria_atividade.id, INT, obrigatório).
- nome_padrao (VARCHAR(100), obrigatório).
- descricao_padrao (VARCHAR(200), opcional).
- prioridade_padrao (VARCHAR(5), obrigatório, padrão BAIXA; valores: BAIXA, MEDIA ou ALTA).
- periodicidade (VARCHAR(10), obrigatório; valores: NENHUMA, DIARIA, SEMANAL ou MENSAL).
- data_referencia (DATE, obrigatório; data de referência da regra vigente).
- numero_referencia (INT, obrigatório, padrão 1; posição da ocorrência correspondente à data de referência).
- horario_inicial_padrao (TIME, obrigatório).
- horario_final_padrao (TIME, obrigatório).
- data_final_repeticao (DATE, opcional; limite inclusivo informado pelo usuário).
- numero_final (INT, opcional; última posição que poderá ser gerada; zero encerra a geração antes da primeira ocorrência).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Esta tabela guardará o padrão para gerar tarefas recorrentes. A opção NENHUMA permitirá encerrar uma repetição preservando sua origem: nesse caso, a regra vigente produzirá somente a ocorrência de referência. Para uma atividade inicialmente avulsa, utilizar apenas a tabela `atividade`.

Restrições: horário final maior que inicial; `numero_referencia >= 1`; `numero_final >= 0`, quando informado; data final da repetição igual ou posterior à referência, quando informada. O limite por número será usado principalmente para interromper uma série a partir de uma ocorrência, sem depender de datas que possam ter sido editadas individualmente.

5 - ATIVIDADE — `atividade`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- categoria_id (chave estrangeira → categoria_atividade.id, INT, obrigatório).
- serie_id (chave estrangeira → serie_atividade.id, INT, opcional).
- numero_ocorrencia (INT, opcional; posição estável dentro da série).
- nome (VARCHAR(100), obrigatório).
- descricao (VARCHAR(200), opcional).
- prioridade (VARCHAR(5), obrigatório, padrão BAIXA; valores: BAIXA, MEDIA ou ALTA).
- data_atividade (DATE, obrigatório).
- horario_inicial (TIME, obrigatório).
- horario_final (TIME, obrigatório).
- concluida_em (DATETIME em UTC, opcional).
- excluida_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Restrições: nome com 3 a 100 caracteres; horário final maior que inicial. `serie_id` e `numero_ocorrencia` deverão estar ambos preenchidos ou ambos nulos; quando houver número, ele deverá ser maior ou igual a 1. Criar unicidade para o par `(serie_id, numero_ocorrencia)`.

Os campos de nome, categoria, prioridade, descrição e horários serão os valores efetivos daquela ocorrência. Não consultar sempre o padrão da série para exibi-los, pois uma edição individual ou a conclusão de uma ocorrência precisa preservar seus próprios dados.

Situação calculada para registros não excluídos: `concluida_em` nulo significa Pendente; preenchido significa Concluída. Concluir preencherá o campo; reabrir o tornará nulo. A data da atividade continuará sendo sua data planejada.

6 - CATEGORIA_IMPORTANCIA — `categoria_importancia`

- id (chave primária, auto incremento, INT, obrigatório).
- nome (VARCHAR(50), obrigatório, único).
- ativa (BOOLEAN, obrigatório, padrão verdadeiro).

Dados iniciais: Contas, Compras, Veículo, Lazer, Saúde, Educação, Pessoal e Outros.

Manter separada das categorias financeiras: a categoria de um compromisso não necessariamente será a categoria escolhida para o pagamento. Desativar uma categoria não deverá apagar seu histórico.

7 - SERIE_IMPORTANCIA — `serie_importancia`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- categoria_id (chave estrangeira → categoria_importancia.id, INT, obrigatório).
- nome_padrao (VARCHAR(100), obrigatório).
- descricao_padrao (VARCHAR(200), opcional).
- periodicidade (VARCHAR(10), obrigatório; valores: NENHUMA, DIARIA, SEMANAL, MENSAL ou ANUAL).
- data_referencia (DATE, obrigatório).
- numero_referencia (INT, obrigatório, padrão 1).
- horario_padrao (TIME, opcional).
- data_final_repeticao (DATE, opcional; limite inclusivo).
- numero_final (INT, opcional; última posição gerável, admitindo zero).
- possui_despesa_padrao (BOOLEAN, obrigatório, padrão falso).
- valor_previsto_padrao (DECIMAL(12,2), opcional; obrigatório e maior que zero quando houver despesa).
- lembrete_antecedencia_dias (SMALLINT, opcional; valores: 0, 1, 3 ou 7).
- lembrete_horario (TIME, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Esta tabela guardará a configuração para gerar compromissos recorrentes. Aplicar as mesmas regras dos números de ocorrência da série de atividades, acrescentando a repetição anual.

Se `possui_despesa_padrao` for falso, `valor_previsto_padrao` deverá ser nulo. Se for verdadeiro, exigir valor preenchido e positivo. Os dois campos de lembrete deverão estar ambos nulos, para lembrete desativado, ou ambos preenchidos.

8 - IMPORTANCIA — `importancia`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- categoria_id (chave estrangeira → categoria_importancia.id, INT, obrigatório).
- serie_id (chave estrangeira → serie_importancia.id, INT, opcional).
- numero_ocorrencia (INT, opcional).
- nome (VARCHAR(100), obrigatório).
- descricao (VARCHAR(200), opcional).
- data_compromisso (DATE, obrigatório).
- horario (TIME, opcional).
- possui_despesa (BOOLEAN, obrigatório, padrão falso).
- valor_previsto (DECIMAL(12,2), opcional; obrigatório e maior que zero quando houver despesa).
- concluida_manualmente_em (DATETIME em UTC, opcional; utilizado somente em importâncias sem despesa).
- excluida_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Criar unicidade para `(serie_id, numero_ocorrencia)`. Aplicar a mesma regra de preenchimento conjunto desses dois campos utilizada em Atividade. Cada linha terá seus próprios dados, mesmo quando tiver sido gerada a partir de uma série.

Restrições condicionais: se não houver despesa, o valor previsto será nulo; se houver, exigir valor preenchido e positivo. `concluida_manualmente_em` deverá ser nulo quando `possui_despesa` for verdadeiro.

O pagamento será encontrado pelo relacionamento com `movimentacao_financeira`. Não criar nesta tabela outra coluna de valor pago nem uma segunda chave estrangeira de volta para o lançamento; o vínculo ficará em um único lado.

Situação calculada para uma importância não excluída:

- Sem despesa: Concluída quando `concluida_manualmente_em` estiver preenchido; Pendente nos demais casos.
- Com despesa: Concluída/Pago quando houver uma despesa válida vinculada; Pendente quando não houver.
- Atrasada: importância pendente com `data_compromisso` anterior a hoje no fuso da conta. É uma indicação calculada, não um terceiro estado persistido.

9 - CATEGORIA_FINANCEIRA — `categoria_financeira`

- id (chave primária, auto incremento, INT, obrigatório).
- nome (VARCHAR(50), obrigatório).
- tipo (VARCHAR(7), obrigatório; valores: RECEITA ou DESPESA).
- ativa (BOOLEAN, obrigatório, padrão verdadeiro).

Criar unicidade para `(tipo, nome)`. Assim, a categoria Outros poderá existir para receitas e para despesas sem representar o mesmo registro. Criar também a chave única `(id, tipo)` para a chave estrangeira composta da movimentação.

Categorias iniciais de receita: Salário, Trabalho autônomo, Vendas, Rendimentos, Reembolsos e Outros.

Categorias iniciais de despesa: Alimentação, Transporte, Moradia, Contas, Compras, Saúde, Educação, Lazer, Veículo e Outros.

10 - MOVIMENTACAO_FINANCEIRA — `movimentacao_financeira`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- categoria_id (chave estrangeira composta com tipo → categoria_financeira.id/tipo, INT, obrigatório).
- tipo (VARCHAR(7), obrigatório; valores: RECEITA ou DESPESA).
- nome (VARCHAR(100), obrigatório).
- descricao (VARCHAR(200), opcional).
- valor (DECIMAL(12,2), obrigatório, maior que zero).
- data_movimentacao (DATE, obrigatório; data real do recebimento ou pagamento).
- contraparte (VARCHAR(100), opcional; pagador, destinatário ou estabelecimento, conforme o tipo).
- forma_movimentacao (VARCHAR(20), opcional; valores controlados indicados abaixo).
- importancia_id (chave estrangeira → importancia.id, INT, opcional, único quando preenchido).
- importancia_vinculada_em (DATETIME em UTC, opcional).
- excluida_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Receitas: formas PIX, DINHEIRO, TRANSFERENCIA, DEPOSITO ou OUTROS.

Despesas: formas PIX, DINHEIRO, CARTAO_DEBITO, TRANSFERENCIA, BOLETO ou OUTROS.

Restrições importantes:

- `valor > 0`. O sinal exibido e a participação no saldo serão definidos por `tipo`.
- A chave estrangeira composta `(categoria_id, tipo)` deverá apontar para `(categoria_financeira.id, categoria_financeira.tipo)`, impedindo categoria de receita em despesa e vice-versa.
- `importancia_id` somente poderá ser preenchido quando `tipo = DESPESA`.
- A unicidade de `importancia_id` garantirá no máximo um pagamento vinculado a cada ocorrência. Como cada movimentação possui apenas esse campo de vínculo, uma mesma despesa não quitará duas importâncias.
- `importancia_id` e `importancia_vinculada_em` deverão estar ambos nulos ou ambos preenchidos.
- Uma movimentação excluída deverá ficar com esses dois campos de vínculo nulos.
- Na aplicação, exigir uma importância do mesmo usuário, não excluída, com `possui_despesa = verdadeiro` e ainda sem pagamento.
- Validar `data_movimentacao <= hoje` usando o fuso da conta, e não uma data de servidor possivelmente diferente.

O momento de vínculo será necessário para ordenar conclusões: vincular hoje uma despesa antiga conclui a importância hoje, enquanto o gasto continua contabilizado pela data real do pagamento.

11 - LEMBRETE_IMPORTANCIA — `lembrete_importancia`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- importancia_id (chave estrangeira → importancia.id, INT, obrigatório, único).
- antecedencia_dias (SMALLINT, obrigatório; valores: 0, 1, 3 ou 7).
- horario (TIME, obrigatório; horário local do lembrete).
- agendado_para (DATETIME em UTC, obrigatório).
- versao_agendamento (INT, obrigatório, padrão 1).
- situacao (VARCHAR(10), obrigatório, padrão PENDENTE; valores: PENDENTE, ENVIADO ou CANCELADO).
- enviado_em (DATETIME em UTC, opcional).
- criado_em (DATETIME em UTC, obrigatório).
- atualizado_em (DATETIME em UTC, obrigatório).

Cada ocorrência de importância poderá ter no máximo uma configuração de lembrete. `agendado_para` será calculado a partir da data do compromisso, da antecedência, do horário e do fuso do usuário. Ele será persistido para permitir a busca dos lembretes que precisam ser processados.

No reagendamento, incrementar `versao_agendamento`, recalcular `agendado_para` e limpar `enviado_em`, definindo a situação correspondente. Não incrementar a versão em uma mera repetição do mesmo pedido. Uma versão ENVIADO deverá ter `enviado_em` preenchido; PENDENTE e CANCELADO deverão ter esse campo nulo. Notificações de versões anteriores permanecerão em sua própria tabela.

Concluir ou excluir uma importância cancelará lembretes ainda não enviados. Reabri-la permitirá reativar somente lembretes futuros; se for necessária uma nova programação, incrementar a versão. Antes de processar, verificar novamente a versão atual e a situação da importância, evitando disparo de um agendamento substituído.

12 - NOTIFICACAO — `notificacao`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- lembrete_id (chave estrangeira → lembrete_importancia.id, INT, obrigatório).
- versao_agendamento (INT, obrigatório).
- titulo (VARCHAR(120), obrigatório).
- mensagem (VARCHAR(500), obrigatório).
- criada_em (DATETIME em UTC, obrigatório).
- lida_em (DATETIME em UTC, opcional).

Criar unicidade para `(lembrete_id, versao_agendamento)`, garantindo no máximo uma notificação interna para cada programação do lembrete. Criar a notificação e marcar a versão do lembrete como enviada na mesma transação.

`lida_em` nulo representará uma notificação não lida. O título e a mensagem serão o conteúdo daquele envio, preservado mesmo se o nome do compromisso mudar posteriormente. A importância será acessível pelo relacionamento `notificacao → lembrete → importancia`.

Este modelo cobre as notificações internas previstas para o sino do aplicativo. Uma integração opcional de push poderá acrescentar o cadastro de dispositivos ou de assinaturas do provedor escolhido.

13 - REQUISICAO_IDEMPOTENTE — `requisicao_idempotente`

- id (chave primária, auto incremento, INT, obrigatório).
- usuario_id (chave estrangeira → usuario.id, INT, obrigatório).
- chave (VARCHAR(64), obrigatório; identificador aleatório de uma operação enviado pelo aplicativo).
- acao (VARCHAR(50), obrigatório; exemplo: CADASTRAR_DESPESA).
- conteudo_hash (VARCHAR(64), obrigatório; identificação do conteúdo normalizado da solicitação).
- situacao (VARCHAR(20), obrigatório, padrão EM_PROCESSAMENTO; valores: EM_PROCESSAMENTO ou CONCLUIDA).
- codigo_resposta (SMALLINT, opcional).
- resposta (JSON, opcional; resultado mínimo necessário para responder novamente à mesma operação).
- criado_em (DATETIME em UTC, obrigatório).
- concluida_em (DATETIME em UTC, opcional).

Criar unicidade para `(usuario_id, acao, chave)`. O mesmo envio usará a mesma chave nas novas tentativas. Uma operação nova, mesmo com nome e valor iguais, usará outra chave.

Se a mesma chave vier com conteúdo diferente, rejeitar a reutilização. Se a operação já tiver sido concluída, devolver seu resultado sem executar outro cadastro. O registro da operação, a alteração de negócio e a gravação do resultado deverão participar da mesma transação; uma falha deverá desfazer o conjunto.

Esta tabela de apoio atende às exigências de não duplicar atividades, importâncias, séries e movimentações quando houver cliques repetidos ou perda de conexão. Usá-la nas ações de negócio; não guardar senhas, códigos de recuperação ou tokens de acesso no conteúdo da resposta. A limpeza desses registros, caso seja criada depois, deverá definir explicitamente o prazo de garantia contra reenvio.

RESTRIÇÕES ENTRE REGISTROS DO MESMO USUÁRIO

Um `usuario_id` em cada tabela ajuda nas consultas, mas não impede sozinho um vínculo entre registros de usuários diferentes. Para assegurar a propriedade dos relacionamentos, adicionar as seguintes chaves estrangeiras compostas:

| Tabela de origem | Colunas de origem | Tabela e colunas de destino |
| --- | --- | --- |
| atividade | serie_id, usuario_id | serie_atividade.id, serie_atividade.usuario_id |
| importancia | serie_id, usuario_id | serie_importancia.id, serie_importancia.usuario_id |
| movimentacao_financeira | importancia_id, usuario_id | importancia.id, importancia.usuario_id |
| lembrete_importancia | importancia_id, usuario_id | importancia.id, importancia.usuario_id |
| notificacao | lembrete_id, usuario_id | lembrete_importancia.id, lembrete_importancia.usuario_id |

Adicionar `UNIQUE(id, usuario_id)` nas tabelas de destino que participarem dessas referências. Embora o ID já seja único, o par fornece a chave referenciada pela restrição composta. No SQLAlchemy, usar `ForeignKeyConstraint` para cada par; duas chaves estrangeiras independentes não garantem a correspondência entre os valores.

As referências compostas acima substituem a referência simples ao registro relacionado indicada na lista de campos. A referência de `usuario_id` para `usuario.id` continua existindo. As categorias são catálogos compartilhados, por isso não possuem `usuario_id`.

REGRAS DE INTEGRIDADE E EXCLUSÃO

1. Aplicar `NOT NULL`, `UNIQUE`, `CHECK` e as chaves estrangeiras no banco. Manter também validações de formulário e serviço. Limites de caracteres e comparações com a data atual precisarão considerar o dialeto e o fuso do usuário.

2. Para condições opcionais, testar explicitamente `IS NULL` e `IS NOT NULL`. Por exemplo, valor previsto válido exige: sem despesa e valor nulo, ou com despesa e valor não nulo e positivo. Apenas um teste `valor > 0` não torna uma coluna opcional obrigatória quando necessário.

3. Usar exclusão lógica por `excluida_em` em atividades, importâncias e movimentações. Consultas, totais, pagamentos disponíveis para vínculo e indicadores deverão excluir esses registros. O propósito principal é preservar as ocorrências removidas para que a geração de uma série não as recrie.

4. Excluir uma movimentação vinculada deverá, na mesma transação, marcar sua exclusão, remover `importancia_id` e `importancia_vinculada_em` e ajustar o lembrete quando aplicável. A importância voltará a Pendente pela regra de situação calculada.

5. Excluir uma importância deverá marcar sua exclusão, cancelar seu lembrete pendente e remover o vínculo da movimentação, preservando o valor, a data e os efeitos financeiros dessa movimentação. As notificações antigas continuarão legíveis e o acesso ao compromisso indicará sua indisponibilidade.

6. Vincular uma despesa existente deverá preencher o vínculo e o momento do vínculo, sem criar outro lançamento nem contabilizar seu valor novamente. Ao trocar o vínculo, verificar e modificar os registros afetados na mesma transação; recalcular os lembretes das importâncias anterior e nova.

7. A unicidade protege contra dois pagamentos para uma mesma importância, mas não substitui a validação do estado atual do compromisso. Serializar operações concorrentes sobre os mesmos registros, usando os recursos transacionais do banco escolhido. Ao mudar uma importância para sem despesa, exigir que ela não tenha pagamento vinculado.

8. Para essas referências de negócio, preferir `ON DELETE RESTRICT`/`NO ACTION`, com remoção lógica ou desvinculação explícita pelo serviço. Não aplicar exclusão em cascata de importância para movimentação financeira. Não usar `SET NULL` indiscriminadamente em uma FK composta com `usuario_id`, pois isso pode tentar anular também a propriedade do registro.

9. A exclusão definitiva de conta não foi especificada nas telas e precisará de um fluxo próprio antes de configurar cascatas gerais em `usuario`. A configuração `cascade` do relacionamento ORM deverá ser coerente com essas decisões; remover um vínculo não deverá apagar automaticamente uma despesa.

**COMO AS REPETIÇÕES SERÃO REPRESENTADAS**

Uma tarefa avulsa terá uma linha em `atividade`, com série e número nulos. Uma tarefa semanal terá uma linha em `serie_atividade` e uma linha em `atividade` para cada ocorrência necessária. O mesmo princípio valerá para Importâncias.

`numero_ocorrencia` será uma identidade estável: 1, 2, 3 e assim por diante. Alterar individualmente a data de uma tarefa não alterará seu número. Excluir uma ocorrência preencherá sua exclusão lógica e manterá a chave única ocupada, impedindo recriação acidental.

Antes de mostrar uma data, um mês ou um total de pendências, gerar as ocorrências necessárias ao intervalo consultado, incluindo as anteriores relevantes. Uma repetição sem data final não deverá ser materializada infinitamente. Para “próximas três”, buscar e gerar ocorrências até conseguir os próximos itens válidos ou até atingir o limite da série. Os totais mensais não poderão considerar apenas os itens já carregados na tela.

Na repetição mensal, calcular cada data a partir do dia de referência, usando o último dia do mês quando necessário: 31 de janeiro, último dia de fevereiro, 31 de março. Na anual, preservar a referência de 29 de fevereiro, usando 28 em ano não bissexto.

Ao editar somente uma ocorrência, alterar sua linha, sem mudar o padrão da série. Ao editar esta e as próximas pendentes, usar o número original selecionado como limite de alcance. Preservar anteriores, concluídas e exclusões individuais; atualizar os valores padrão e os dados das ocorrências pendentes abrangidas. A geração futura deverá usar a nova referência.

Nesta proposta, a série guarda sua regra vigente, enquanto as ocorrências materializadas preservam seus próprios dados. Antes de mudar a referência da série, materializar todas as posições anteriores ao ponto de alteração, para que nenhum trecho histórico dependa da regra substituída. Ajustar `numero_referencia` e `data_referencia` para manter a correspondência da nova regra. Serializar essa alteração e a geração concorrente.

Ao excluir esta e as próximas pendentes, limitar a geração a `numero_ocorrencia selecionado − 1` e marcar as pendentes abrangidas como excluídas. Ocorrências concluídas já existentes poderão permanecer depois desse limite, pois ele limita a geração, não apaga o histórico.

Para uma mudança de periodicidade que elimine posições pendentes futuras, marcar essas posições como excluídas na mesma operação. Um comando posterior não deverá reativar silenciosamente ocorrências explicitamente excluídas. A lógica de geração e alteração é um serviço da aplicação; o ORM e as tabelas não a executarão automaticamente.

INFORMAÇÕES CALCULADAS — SEM TABELA OU COLUNA PRÓPRIA NESTA VERSÃO

| Informação | Origem do cálculo |
| --- | --- |
| Receitas do dia ou mês | Soma de movimentações RECEITA não excluídas no período. |
| Despesas do dia ou mês | Soma de movimentações DESPESA não excluídas no período. |
| Saldo | Receitas menos despesas do mesmo período. |
| Duração de uma atividade | Horário final menos horário inicial. |
| Tempo total planejado | Soma das durações das ocorrências que correspondem aos filtros. |
| Pendente ou Concluída, em atividades | Ausência ou presença de concluida_em, excluindo registros removidos. |
| Pendente, Concluída ou Pago, em importâncias | Conclusão manual quando sem despesa, ou existência de pagamento válido quando com despesa. |
| Momento de conclusão da importância | concluida_manualmente_em, ou importancia_vinculada_em do pagamento. |
| Valor e data do pagamento | valor e data_movimentacao da despesa vinculada. |
| Atrasada, Hoje ou Em X dias | Situação pendente e comparação da data do compromisso com hoje. |
| Quantidades, gráficos e percentuais | Consultas sobre os mesmos registros usados nos indicadores. |
| Notificações não lidas | Notificações cujo lida_em seja nulo. |

Portanto, não criar tabelas `tela_inicial`, `saldo`, `grafico`, `total_atividades` ou `confirmar_senha`.

**ÍNDICES INICIAIS**

- atividade: `(usuario_id, data_atividade)` e `(usuario_id, concluida_em, data_atividade)`.
- importancia: `(usuario_id, data_compromisso)`.
- movimentacao_financeira: `(usuario_id, data_movimentacao)`, `(usuario_id, tipo, data_movimentacao)` e `(usuario_id, categoria_id, data_movimentacao)`.
- lembrete_importancia: `(situacao, agendado_para)`.
- notificacao: `(usuario_id, lida_em, criada_em)`.

As restrições únicas já indicadas também deverão ser criadas, especialmente e-mail, identificação de ocorrências, vínculo de pagamento, versão de notificação e chave de reenvio. Revisar os demais índices conforme as consultas reais e o volume de dados.

**MAPEAMENTO PARA SQLALCHEMY**

| Especificação | Tipo ou configuração no ORM |
| --- | --- |
| INT | Integer; PK gerada com primary_key=True e autoincrement=True conforme o dialeto. |
| SMALLINT | SmallInteger. |
| VARCHAR(n) | String(n). |
| BOOLEAN | Boolean. |
| DATE | Date, usando datetime.date no Python. |
| TIME | Time, usando datetime.time no Python. |
| DATETIME em UTC | DateTime(timezone=True), com normalização para UTC e adaptação ao banco escolhido. |
| DECIMAL(12,2) | Numeric(12, 2, asdecimal=True), utilizando Decimal no Python. |
| JSON | JSON. |
| Obrigatório/opcional | nullable=False / nullable=True. |
| Chave estrangeira simples | ForeignKey. |
| Chave estrangeira composta | ForeignKeyConstraint. |
| Unicidade simples/composta | unique=True / UniqueConstraint. |
| Regras de domínio | CheckConstraint, além da validação da aplicação. |
| Relação entre objetos | relationship; não substitui PK, FK ou UNIQUE. |

Para os campos de valores controlados, utilizar enumerações Python com armazenamento textual validado. No SQLAlchemy, uma opção é `Enum(..., native_enum=False, create_constraint=True, validate_strings=True)`, com nomes estáveis para as restrições; outra é `String` com `CheckConstraint`. Escolher uma representação e usá-la consistentemente, distinguindo os valores técnicos, como MEDIA, dos rótulos exibidos, como Média.

Dinheiro: DECIMAL(12,2) estabelece um máximo por lançamento de R$ 9.999.999.999,99, um limite técnico proposto a validar no formulário. Não utilizar Float nem converter entradas monetárias primeiro para float. Validar até duas casas decimais antes da gravação, sem arredondar silenciosamente uma entrada com precisão maior. Totais poderão ultrapassar o limite individual e deverão ser calculados com precisão suficiente. Se o banco escolhido for SQLite, revisar esta decisão: sua representação REAL é aproximada; para manter exatidão monetária, considerar valores em centavos inteiros e conversão para Decimal na aplicação.

Datas: o formato DD/MM/AAAA pertence à apresentação. Datas de nascimento, atividades e pagamentos serão valores Date; instantes como criação, conclusão e envio serão normalizados para UTC. A flag timezone=True não garante suporte uniforme a fuso em todos os bancos; confirmar o comportamento do dialeto.

O uso de `relationship` para expressar um pagamento único não basta para impor essa regra no banco: manter também a restrição única de `movimentacao_financeira.importancia_id`.

<!-- FIM_DO_CONTRATO_ORIGINAL -->
