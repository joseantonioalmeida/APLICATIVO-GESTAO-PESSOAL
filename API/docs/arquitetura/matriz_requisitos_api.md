# Matriz de rastreabilidade de requisitos — API MinhaVida

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/matriz_requisitos_api.md` |
| Estado | PROPOSTO |
| Data | 2026-10-10. Atualizado em 2026-10-11 (escopo financeiro e exclusões) e em 2026-10-13 (contrato de dados da F2: DEC-MV-06 a 08; comprovação estrutural da F2 integrada no commit `91be324`; decisões da F3 aprovadas, com o MZ-1 e as situações das telas 1 a 3, M16) |
| Fonte dos requisitos | `CLAUDE.md` (telas 1–11 e contrato de tabelas), identificadores preservados |

## Convenções

- Cadeia de rastreio: **Requisito → caso de uso/endpoint (schema) → dados e invariantes → transação/decisão → fase → verificação (CT) → situação**.
- Abreviações:
  - **X** = trava EXCLUSIVA do usuário;
  - **C** = trava COMPARTILHADA;
  - **Idem** = idempotência por `Idempotency-Key`;
  - **arq** = `arquitetura_api_minhavida.md`.
- Situação:
  - `PLANEJADO` (fase e CT definidos);
  - `AGUARDANDO_DECISAO (DEC-…)`;
  - `NÃO SE APLICA AO BACKEND`, com justificativa: comportamento exclusivamente visual ou de navegação. Nesses casos, o backend fornece os dados indicados.
  - `VERIFICADO (Fn)` ou “Parte Fn … VERIFICADA”: comprovado pela auditoria independente da fase e integrado por commit (G5 e G6). Vale **só** para a parte estrutural indicada; fluxos HTTP e regras de serviço das fases seguintes continuam com a situação própria. A F2 foi auditada em `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md` e integrada no commit `91be324c88c5a3f99a49b1b1700963e32ef257e9`.
- `3.3.1*`: na tela 3.3, o `CLAUDE.md` numera “3.1.1 - CAMPOS OBRIGATÓRIOS”. Tratado como 3.3.1 sem alterar o requisito (REC-MV-025).

---

## Tela 1 — Login

| Req | Caso de uso → endpoint (schema) | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 1.1 | Autenticar → `POST /auth/login` (`LoginEntrada` → `TokenResposta`) | `usuario.email` na forma canônica (R9.9), `senha_hash` Argon2id. Resposta 401 genérica, também para e-mail sem forma canônica | Leitura. D-07 | F3 | CT-F3-04, CT-F3-06, CT-F3-07 | PLANEJADO (DEC-MV-09 aprovada) |

## Tela 2 — Registro

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 2.1 | Criar conta → `POST /auth/registro` (`RegistroEntrada` → `UsuarioResposta`). Data de nascimento em ISO: “modelo BR” é apresentação. `fuso_horario` enviado pelo app (REC-MV-020) | `uq_usuario_email`. Nascimento ≤ hoje no fuso. Senha 8–128. Confirmação igual | Escrita sem trava. Unicidade traduzida para 409. D-07 | F3 | CT-F3-01, 02, 03, 05 | PLANEJADO (DEC-MV-09 e 11 aprovadas) |

## Tela 3 — Esqueceu a senha

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 3 (objetivo) | Três etapas → solicitar, verificar e redefinir (arq §8.3) | `recuperacao_senha` única por usuário | `FOR UPDATE` na linha; `INSERT … ON CONFLICT` na primeira emissão (DEC-MV-14, escopo limitado). §5.3 | F3 | CT-F3-09 a 20, 23, 24, 26 e 27 | PLANEJADO (DEC-MV-11 aprovada) |
| 3.1.1 | E-mail obrigatório → `POST /auth/recuperacao/solicitar` | Formato de e-mail | idem | F3 | CT-F3-09 | PLANEJADO |
| 3.2.1 | Código de 8 dígitos → `POST /auth/recuperacao/verificar` (`codigo` texto `^[0-9]{8}$`, só dígitos ASCII) | Hash lento do código | Persistir a tentativa e depois recusar (§5.3) | F3 | CT-F3-12 | PLANEJADO |
| 3.2 (reenviar) | Reenvio → mesmo endpoint de solicitar | Substitui hash e validade. Zera tentativas. Limpa verificação e token. O código antigo deixa de valer | Intervalo de 60 s (`expira_em − 10 min`) | F3 | CT-F3-11, CT-F3-19, CT-F3-24 | PLANEJADO (DEC-MV-11 aprovada) |
| 3.2 (regra) | Código diferente → `CODIGO_INVALIDO` | — | — | F3 | CT-F3-12 | PLANEJADO |
| 3.3.1* | Nova senha + confirmação → `POST /auth/recuperacao/redefinir` | Token de uso único (SHA-256 em `token_redefinicao_hash`) | `FOR UPDATE` pelo hash. `utilizado_em` na mesma transação | F3 | CT-F3-16, 17, 18 | PLANEJADO |
| 3.4.1 | E-mail obrigatório, válido e cadastrado | Validação de schema e busca | — | F3 | CT-F3-09, 10 | PLANEJADO |
| 3.4.2 | Mensagem “Não foi possível encontrar seu email” → 404 `EMAIL_NAO_ENCONTRADO` | — | Revela a existência da conta (REC-MV-007): risco aceito pelo usuário, sem prazo, enquanto valer 3.4.2 (DEC-MV-10, opção A) | F3 | CT-F3-10 | PLANEJADO (DEC-MV-10 aprovada) |
| 3.4.3 | Enviar o código ao e-mail da conta → `EnviadorEmail` | — | Envio antes do commit (D-15) | F3 | CT-F3-09, 20, 26, 28 | PLANEJADO (DEC-MV-12 aprovada) |
| 3.4.4 | Assunto e mensagem → modelo literal (arq §8.3.1). `{Nome}` = `nome_completo` (interpretação literal) | — | — | F3 | CT-F3-09 | PLANEJADO |
| 3.4.5 | 8 dígitos numéricos → `secrets.randbelow(10**8)` formatado `08d` | Texto, zeros à esquerda preservados | — | F3 | CT-F3-09 | PLANEJADO |
| 3.4.6 | Botão habilitado e navegação | Backend: 200 com `expira_em` e `reenvio_permitido_em` | — | — | — | NÃO SE APLICA AO BACKEND (estado do botão e navegação) |
| 3.4.7 | Código correto habilita e navega | Backend: 200 com `token_redefinicao` | — | F3 | CT-F3-12 | NÃO SE APLICA AO BACKEND (navegação); token PLANEJADO |
| 3.4.8 | Mensagem de código inválido → `CODIGO_INVALIDO` com texto literal | — | — | F3 | CT-F3-12 | PLANEJADO |
| 3.4.9 | Senha ≥ 8 caracteres e mensagem de orientação | Validação 8–128 (REC-MV-019). A orientação é texto do formulário | — | F3 | CT-F3-02 | PLANEJADO (DEC-MV-11 aprovada) |
| 3.4.10 | Mensagem de requisito não atendido → `SENHA_FRACA` literal | — | — | F3 | CT-F3-02, 18 | PLANEJADO |
| 3.4.11 | Máscara `********` | — | — | — | — | NÃO SE APLICA AO BACKEND (exibição) |
| 3.4.12 | Opção “Mostrar” | — | — | — | — | NÃO SE APLICA AO BACKEND (exibição) |
| 3.4.13 | Confirmar = senha → validação de schema | — | — | F3 | CT-F3-18 | PLANEJADO |
| 3.4.14 | “As senhas devem ser idênticas” → `SENHAS_DIFERENTES` | — | — | F3 | CT-F3-18 | PLANEJADO |
| 3.4.15 | Sucesso e redirecionamento → `MensagemResposta` literal. O redirecionamento é do cliente | `sv` invalida tokens anteriores | — | F3 | CT-F3-16 | PLANEJADO |

## Tela 4 — Inicial

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 4.1.1 | Saudação com o nome → `GET /usuarios/me` (`nome_completo`). O avatar é navegação | — | — | F3 | CT-F3-08 | PLANEJADO |
| 4.1.2 | Indicadores do mês → `GET /painel/financeiro` (saldo, despesas e comparação) e `GET /painel/importancias` (`pendentes_mes`). Navegação no cliente | `totais_periodo`. Pendentes do mês incluem atrasadas deste mês | C / X (materialização) | F10 | CT-F10-02, 03 | PLANEJADO |
| 4.1.3 | Hoje e dia da semana → `hoje` e `dia_semana` nas respostas do painel. A atualização na virada do dia é feita pelo cliente | `ContextoUsuario.hoje` no fuso | D-13 | F10 | CT-F10-05 | PLANEJADO |
| 4.1.4 | Atividades de hoje → `GET /painel/atividades-hoje`. Concluir e reabrir → `PUT /atividades/{id}/situacao` | Prévia ≤ 3 (pendentes antes, por horário). Totais de todas. Pendências anteriores | X | F10 (+F5) | CT-F10-01, CT-F5-10 | PLANEJADO |
| 4.1.5 | Resumo do dia → `GET /painel/financeiro` (`dia`) | Data efetiva (`data_movimentacao = hoje`). Importância não paga não soma | C | F10 | CT-F10-02, 04 | PLANEJADO |
| 4.1.6 | Acessos rápidos | Backend: endpoints das telas 5–11 | — | — | — | NÃO SE APLICA AO BACKEND (navegação) |
| 4.1.7 | Movimentações recentes → `movimentacoes_recentes` (≤ 5). Detalhes → `GET /financeiro/movimentacoes/{id}`. “Ver todas” → `GET /financeiro/movimentacoes?mes=` | Ordem data desc, empate por `criado_em` desc | C | F10 (+F6) | CT-F10-02, CT-F6-09 | PLANEJADO |
| 4.1.8 | Próximas importâncias (≤ 3) e aviso de atrasadas → `GET /painel/importancias` | Varredura de próximas (§8.5.5). Atrasos de qualquer mês | X | F10 | CT-F10-03 | PLANEJADO |
| 4.1.9 | Notificações → `GET /notificacoes`, `GET /notificacoes/nao-lidas`, `POST /notificacoes/{id}/leitura` | `lida_em`. `disponivel = false` se excluída. Leitura não conclui nem paga | X (leitura) | F9 | CT-F9-08 | PLANEJADO |
| 4.1.10 | Navegação inferior | — | — | — | — | NÃO SE APLICA AO BACKEND (navegação) |
| 4.2.1 | Referência sempre hoje e mês atual → endpoints do painel sem parâmetro de período | — | — | F10 | CT-F10-08 | PLANEJADO |
| 4.2.2 | Mesmas regras do Financeiro → `resumo_financeiro.totais_periodo` compartilhado | Cada lançamento contado uma vez. Centavos exatos | — | F6/F10 | CT-F10-02, 04 | PLANEJADO |
| 4.2.3 | Saldo sem variação. Comparação de despesas pelas regras 9.2.6–9.2.8 → `comparacao_despesas` | — | D-16 | F10 | CT-F10-02, CT-F6-08 | PLANEJADO |
| 4.2.4 | Pendentes do mês incluem recorrentes. Atrasos com alcance próprio | Materialização do mês e do passado | X | F10 | CT-F10-03 | PLANEJADO |
| 4.2.5 | Concluir e reabrir pela tela inicial = mesma ocorrência, sem efeito financeiro | `concluida_em` | X | F5/F10 | CT-F10-01 | PLANEJADO |
| 4.2.6 | Atualização dos blocos e consistência sem novo login | Sem cache. Leitura direta do banco | — | F10 | CT-F10-01 a 04 | PLANEJADO |
| 4.2.7 | Estados vazios | Listas vazias e zeros somente com consulta bem-sucedida. Mensagens no cliente | — | F10 | CT-F10-06 | PLANEJADO |
| 4.2.8 | Carregamento por bloco. Falha ≠ vazio. Coerência | Endpoints por bloco. Erro estruturado. Trava C | D-12 | F10 | CT-F10-06, 07 | PLANEJADO |
| 4.3.1 | 2.450,75 − 1.230,40 = 1.220,35, igual ao Financeiro | — | — | F10 | CT-F10-02, CT-F6-04 | PLANEJADO |
| 4.3.2 | Dia 100 − 30 = 70. Ontem fica fora | — | — | F10 | CT-F10-02 | PLANEJADO |
| 4.3.3 | 5 atividades, 2 concluídas. Prévia de 3. Concluir mais uma → 3 | — | — | F10 | CT-F10-01 | PLANEJADO |
| 4.3.4 | Importância de 99,90 não altera o saldo. O pagamento entra uma vez | — | — | F10/F8 | CT-F10-04, CT-F8-01 | PLANEJADO |
| 4.3.5 | Futura de outro mês nas próximas, fora do mês. Atrasada de outro mês no aviso | — | — | F10 | CT-F10-03 | PLANEJADO |
| 4.3.6 | Virada de 31/10 para 01/11 | — | Relógio | F10 | CT-F10-05 | PLANEJADO |
| 4.3.7 | Falha financeira por bloco. Zeros só com sucesso | — | — | F10 | CT-F10-06 | PLANEJADO |

## Tela 5 — Atividades

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 5.1.1 | Seletor de data e “Hoje” → `GET /atividades?data=` (omitido = hoje). A preservação de estado na volta dos detalhes é do cliente | `data_atividade` | X (materialização) | F5 | CT-F5-04, 15 | PLANEJADO |
| 5.1.2 | Botão Nova atividade | Endpoint da tela 6 | — | — | — | NÃO SE APLICA AO BACKEND (navegação) |
| 5.1.3 | Filtro de categoria → `categoria_id`. Lista → `GET /categorias/atividades` | Catálogo compartilhado | — | F5/F4 | CT-F5-06, CT-F4-12 | PLANEJADO |
| 5.1.4 | Situação, prioridade, busca e limpar → parâmetros de query. Limpar = omitir | `ILIKE` escapado | — | F5 | CT-F5-06, 07 | PLANEJADO |
| 5.1.5 | Indicadores → `indicadores {total, concluidas, pendentes, tempo_total_minutos}`. A formatação h/min é do cliente | Mesmo `WHERE` da lista | D-12 | F5 | CT-F5-05 | PLANEJADO |
| 5.1.6 | Lista em partes com os campos → `itens` (`AtividadeItem`) com keyset | `descricao_previa` (30 + …) | — | F5 | CT-F5-04, 09 | PLANEJADO |
| 5.1.7 | Ordenações → `ordenacao=HORARIO\|PRIORIDADE\|RECENTES` | Desempate estável por `id`. Momento do cadastro da série (REC-MV-021) | — | F5 | CT-F5-08, 31 | AGUARDANDO_DECISAO (DEC-MV-16) |
| 5.1.8 | Detalhes → `GET /atividades/{id}` (`AtividadeDetalhe`) | Descrição completa, `concluida_em` e repetição | C | F5 | CT-F5-11 | PLANEJADO |
| 5.1.9 | Pendências anteriores → `GET /atividades/pendencias-anteriores`. A navegação para o dia mais antigo com filtro Pendentes é do cliente | Independe dos filtros. Materialização do passado | X | F5 | CT-F5-14 | PLANEJADO |
| 5.1.10 | Navegação inferior | — | — | — | — | NÃO SE APLICA AO BACKEND |
| 5.2.1 | A data planejada define o dia. Sem transferência | Consulta por `data_atividade` | — | F5 | CT-F5-14 | PLANEJADO |
| 5.2.2 | Filtros em conjunto. Limpar mantém a data. Ordenação não altera totais | — | — | F5 | CT-F5-06 a 08 | PLANEJADO |
| 5.2.3 | Lista e indicadores com os mesmos filtros. Universo completo | Consulta agregada separada | D-12 | F5 | CT-F5-05, 09 | PLANEJADO |
| 5.2.4 | Duração e soma em minutos | `(final − inicial)` | — | F5 | CT-F5-05 | PLANEJADO |
| 5.2.5 | Sobrepostas somadas | — | — | F5 | CT-F5-03 | PLANEJADO |
| 5.2.6 | “Hoje” acompanha a virada do dia. Data fixa é mantida | Servidor: `hoje` no fuso. O acompanhamento é do cliente | D-13 | F5 | CT-F5-15 | PLANEJADO |
| 5.3.1 | Começa pendente. Só uma ação explícita conclui | `concluida_em` nulo | — | F5 | CT-F5-01, 10 | PLANEJADO |
| 5.3.2 | Concluir registra o momento. Antecipada permitida | `concluida_em = contexto.agora` | X | F5 | CT-F5-10 | PLANEJADO |
| 5.3.3 | Reabrir. Recorrente individual | — | — | F5 | CT-F5-10, 21 | PLANEJADO |
| 5.3.4 | Filtro retira o item. Mensagens no cliente | — | — | F5 | CT-F5-10 | PLANEJADO |
| 5.3.5 | Envio sem alternância. Falha preserva o estado. Reconsulta | `PUT situacao` com estado alvo (idempotente) | X | F5 | CT-F5-10 | PLANEJADO |
| 5.4.1 | Editar preserva a identidade → `PATCH /atividades/{id}` | Mesmo `id` | X | F5 | CT-F5-12 | PLANEJADO |
| 5.4.2 | Atualizar as datas afetadas. A situação não muda | — | — | F5 | CT-F5-12 | PLANEJADO |
| 5.4.3 | Confirmação de exclusão (cliente) → `DELETE /atividades/{id}` | Exclusão lógica | X | F5 | CT-F5-13 | PLANEJADO |
| 5.4.4 | Alcance em séries → `alcance`, padrão `SOMENTE_ESTA` | — | — | F5 | CT-F5-28, 29 | PLANEJADO |
| 5.4.5 | Alcance pela posição original. Concluída só individualmente | `numero_ocorrencia` | arq §8.5.7 | F5 | CT-F5-28, 30 | PLANEJADO |
| 5.4.6 | Excluídas não reaparecem | Lápide e `numero_final` | arq §8.5.8 | F5 | CT-F5-23, 29 | PLANEJADO |
| 5.4.7 | Falha mantém os dados. Cancelar não altera nada | Rollback | D-04 | F5 | CT-F1-11, CT-F5-12 | PLANEJADO |
| 5.5.1 | Mensagens de vazio → `total_data` distingue os dois casos | — | — | F5 | CT-F5-04 | PLANEJADO |
| 5.5.2 | Carregamento. Falha ≠ vazio | Erro estruturado | D-08 | F1/F5 | CT-F1-09 | PLANEJADO |
| 5.5.3 | 90/60/30 min → 3/1/2/3h. Depois → 3/2/1/3h | — | — | F5 | CT-F5-05 | PLANEJADO |
| 5.5.4 | Filtro Estudo → 2/0/2/2h | — | — | F5 | CT-F5-06 | PLANEJADO |
| 5.5.5 | Descrição de 100 caracteres completa nos detalhes. Prévia de 30 | — | — | F5 | CT-F5-04, 11 | PLANEJADO |
| 5.5.6 | 08:00–09:00 → 09:30: mais 30 min. Mudança de data recalcula | — | — | F5 | CT-F5-12 | PLANEJADO |
| 5.5.7 | Semanal: concluir uma; excluir uma; excluir esta e próximas | — | — | F5 | CT-F5-21, 23, 29 | PLANEJADO |
| 5.5.8 | 23 encontradas, 10 carregadas → totais 23, sem duplicar | Keyset | D-12 | F5 | CT-F5-09 | PLANEJADO |
| 5.5.9 | Virada do dia, data fixa, pendências nas datas originais | — | — | F5 | CT-F5-14, 15 | PLANEJADO |
| 5.5.10 | Cliques repetidos em concluir. Cancelar exclusão | Estado alvo | — | F5 | CT-F5-10, 13 | PLANEJADO |

## Tela 6 — Cadastrar atividade

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 6.1.1 | Nome 3–100 → `POST /atividades` (`AtividadeCriacao.nome`) | `ck_atividade_nome_tamanho`. Aparado | X + Idem | F5 | CT-F5-02 | PLANEJADO |
| 6.1.2 | Categoria única → `categoria_id` ativa | FK `RESTRICT` | — | F5 | CT-F5-02 | PLANEJADO |
| 6.1.3 | Prioridade com padrão BAIXA | `server_default` e padrão do schema | — | F5 | CT-F5-01 | PLANEJADO |
| 6.1.4 | Data válida. Valor inicial vindo da tela | ISO. O preenchimento inicial é do cliente | — | F5 | CT-F5-02 | PLANEJADO |
| 6.1.5 | Horário inicial | `HH:MM` | — | F5 | CT-F5-02 | PLANEJADO |
| 6.1.6 | Horário final | `ck_atividade_horarios` | — | F5 | CT-F5-02 | PLANEJADO |
| 6.2.1 | Descrição ≤ 200 com contador | Validação. O contador é do cliente | — | F5 | CT-F5-02 | PLANEJADO |
| 6.2.2 | Repetir (`NAO_REPETIR\|DIARIA\|SEMANAL\|MENSAL`) | Série | arq §8.5.6 | F5 | CT-F5-21 | PLANEJADO |
| 6.2.3 | Término: sem data final ou até uma data ≥ 1ª ocorrência | `ck_serie_atividade_data_final` | — | F5 | CT-F5-02, 20 | PLANEJADO |
| 6.3.1 | “Salvando…” e sem envios simultâneos | `Idempotency-Key`. O estado do botão é do cliente | D-06 | F4/F5 | CT-F4-05, CT-F5-01 | AGUARDANDO_DECISAO (DEC-MV-15) |
| 6.3.2 | Voltar, cancelar e confirmar descarte | — | — | — | — | NÃO SE APLICA AO BACKEND (diálogo local) |
| 6.3.3 | Campos inválidos identificados | `campos[]` do erro 422 | D-08 | F1/F5 | CT-F1-08, CT-F5-02 | PLANEJADO |
| 6.4.1 | Aparar o nome. Só espaços é inválido | `NomeTexto` | — | F4 | CT-F4-13 | PLANEJADO |
| 6.4.2 | Mesma data. Final > inicial. Sem atravessar a meia-noite | — | — | F5 | CT-F5-02 | PLANEJADO |
| 6.4.3 | Duração automática e tempo total | `duracao_minutos` | — | F5 | CT-F5-05 | PLANEJADO |
| 6.4.4 | Aviso de sobreposição com revisar ou salvar → 409 `SOBREPOSICAO_HORARIO` + `confirmar_sobreposicao` | Materialização do dia antes da verificação | X | F5 | CT-F5-03 | PLANEJADO |
| 6.4.5 | Pendente. Datas passadas permitidas | — | — | F5 | CT-F5-01 | PLANEJADO |
| 6.4.6 | Prévia de 30 caracteres | — | — | F5 | CT-F5-04 | PLANEJADO |
| 6.4.7 | Regras diária, semanal e mensal. Último dia do mês. Data final inclusiva | `data_da_posicao` | arq §8.5.1 | F5 | CT-F5-20 | PLANEJADO |
| 6.4.8 | Situação própria. Alcance. Concluídas preservadas. Nova referência | — | arq §8.5.7, §8.5.8 | F5 | CT-F5-21, 28 a 30 | AGUARDANDO_DECISAO (DEC-MV-16) |
| 6.4.9 | Sucesso e navegação. Edição reutiliza o formulário → 201/200 com `data` | — | — | F5 | CT-F5-01, 12 | PLANEJADO |
| 6.5.1 | Mensagens específicas (“Informe o nome da atividade”, “Selecione uma categoria”) | arq §4.5 | — | F5 | CT-F5-02 | PLANEJADO |
| 6.5.2 | “Informe uma data válida” e horário final | — | — | F5 | CT-F5-02 | PLANEJADO |
| 6.5.3 | 08:00–10:00 → 2h e +1 pendente | — | — | F5 | CT-F5-05 | PLANEJADO |
| 6.5.4 | Descrição > 200 rejeitada. Válidas preservadas | — | — | F5 | CT-F5-02, 04 | PLANEJADO |
| 6.5.5 | Semanal 08–22/10/2026 → 08, 15 e 22 | — | — | F5 | CT-F5-21 | PLANEJADO |
| 6.5.6 | Falha mantém os campos. Sem duplicatas em novas tentativas | Idem | D-06 | F4/F5 | CT-F4-05, 07 | PLANEJADO |
| 6.5.7 | Descartar ou continuar | — | — | — | — | NÃO SE APLICA AO BACKEND (diálogo local; nenhuma requisição é enviada) |

## Tela 7 — Importâncias

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 7.1.1 | Nova importância | Endpoint da tela 8 | — | — | — | NÃO SE APLICA AO BACKEND (navegação) |
| 7.1.2 | Filtros → `filtro=TODOS\|VENCENDO_HOJE\|ESTE_MES\|PROXIMOS\|CONCLUIDOS\|ATRASADOS` | — | X | F7 | CT-F7-05 | PLANEJADO |
| 7.1.3 | Seletor de mês e busca → `mes` (somente `ESTE_MES`) e `busca` | — | — | F7 | CT-F7-05, 15 | PLANEJADO |
| 7.1.4 | Campos do item → `ImportanciaItem` | Situação derivada, prazo, valor previsto ou pago, “Sem despesa” | arq §8.1 | F7/F8 | CT-F7-05, 07, CT-F8-01 | PLANEJADO |
| 7.1.5 | Grupos com quantidades → `grupos`. A subdivisão por mês é do cliente | — | — | F7 | CT-F7-05 | PLANEJADO |
| 7.1.6 | Detalhes e ações → `GET /importancias/{id}` (`ImportanciaDetalhe`) | — | C | F7 | CT-F7-05 | PLANEJADO |
| 7.1.7 | Navegação inferior | — | — | — | — | NÃO SE APLICA AO BACKEND |
| 7.2.1 | Todos: qualquer data | Horizonte de séries | — | F7 | CT-F7-05, 11 | AGUARDANDO_DECISAO (DEC-MV-18) |
| 7.2.2 | Vencendo hoje | pendente e data = hoje | — | F7 | CT-F7-05 | PLANEJADO |
| 7.2.3 | Este mês e “Mês selecionado” → `rotulo_periodo` | — | — | F7 | CT-F7-05 | PLANEJADO |
| 7.2.4 | Próximos | pendente e data > hoje, com horizonte | — | F7 | CT-F7-05, 11 | AGUARDANDO_DECISAO (DEC-MV-18) |
| 7.2.5 | Concluídos | inclui pagos | — | F7/F8 | CT-F7-05 | PLANEJADO |
| 7.2.6 | Atrasados | pendente e data < hoje | — | F7 | CT-F7-05 | PLANEJADO |
| 7.2.7 | Busca com filtro. Quantidades completas | Agregado separado | D-12 | F7 | CT-F7-15 | PLANEJADO |
| 7.3.1 | Situações persistidas × atraso calculado | arq §8.1 | — | F7 | CT-F7-06 | PLANEJADO |
| 7.3.2 | Dias por calendário no fuso. Atualização na virada | `contexto.hoje` | D-13 | F7 | CT-F7-06, 07 | PLANEJADO |
| 7.3.3 | Ordenação dos grupos | `COALESCE(horario,'24:00')`. Conclusão desc | — | F7 | CT-F7-05, 07 | PLANEJADO |
| 7.3.4 | Concluir e reabrir sem despesa. Lembretes futuros | `concluida_manualmente_em`. Ciclo do lembrete | X | F7 | CT-F7-08 | PLANEJADO |
| 7.3.5 | Registrar pagamento: vincular existente ou nova despesa (tela 11). Valor > 0. Data ≤ hoje | `POST /financeiro/despesas` com `importancia_id`. `PUT /importancias/{id}/pagamento` | X + Idem | F8 | CT-F8-01, 02 | PLANEJADO |
| 7.3.6 | Concluída/Pago só após salvar. Sem duplicidade. Uma despesa por ocorrência | `uq_…_importancia_id`. Transação única | arq §8.7 | F8 | CT-F8-01, 02, 05, 06 | PLANEJADO |
| 7.3.7 | Ver despesa. Alterações no lançamento. Exclusão reabre. Sem reabertura isolada | 409 `REABERTURA_EXIGE_REMOVER_PAGAMENTO` | — | F8 | CT-F8-03, 04 | PLANEJADO |
| 7.3.8 | Confirmação. Exclusão preserva a despesa. Alcance em séries | Desvínculo | arq §8.5.8 | F7/F8 | CT-F7-13, CT-F8-11 | PLANEJADO |
| 7.3.9 | Bloco da tela Inicial usa os mesmos registros | `services/importancias` reutilizado | — | F10 | CT-F10-03 | PLANEJADO |
| 7.4.1 | Mensagens de vazio → `possui_importancias` | — | — | F7 | CT-F7-16 | PLANEJADO |
| 7.4.2 | Hoje → Atrasados no dia seguinte. Concluída fora | — | — | F7 | CT-F7-06 | PLANEJADO |
| 7.4.3 | Próximo mês em Próximos | — | — | F7 | CT-F7-05 | PLANEJADO |
| 7.4.4 | Concluir e reabrir sem efeito financeiro | — | — | F7 | CT-F7-08 | PLANEJADO |
| 7.4.5 | Cancelar e confirmar exclusão. Despesa preservada | — | — | F7/F8 | CT-F7-13, CT-F8-11 | PLANEJADO |
| 7.4.6 | Pagamento consistente. Repetição não duplica | Idem e trava | D-05, D-06 | F8 | CT-F8-05, 13 | PLANEJADO |
| 7.4.7 | Carregamento e erro ≠ vazio | Erro estruturado | D-08 | F7 | CT-F1-09 | PLANEJADO |

## Tela 8 — Cadastrar importância

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 8.1.1 | Nome 3–100 → `POST /importancias` | Validação. CHECK `ck_importancia_nome_tamanho` (DEC-MV-08, aprovada em 2026-10-13) | X + Idem | F7 | CT-F7-02 | PLANEJADO |
| 8.1.2 | Categoria (catálogo próprio) | `categoria_importancia` | — | F7 | CT-F7-02 | PLANEJADO |
| 8.1.3 | Data válida | — | — | F7 | CT-F7-02 | PLANEJADO |
| 8.1.4 | Possui despesa? Padrão Não | `possui_despesa` com padrão `false` | — | F7 | CT-F7-01 | PLANEJADO |
| 8.2.1 | Valor previsto > 0, 2 casas, sem arredondar | `ValorMonetario`. `ck_importancia_valor_previsto` | D-16 | F7 | CT-F7-02 | AGUARDANDO_DECISAO (DEC-MV-17) |
| 8.2.2 | “Não” remove o valor. Aviso no cliente | Valor proibido quando `false` | — | F7 | CT-F7-02, 18 | PLANEJADO |
| 8.3.1 | Descrição ≤ 200 | — | — | F7 | CT-F7-02 | PLANEJADO |
| 8.3.2 | Horário opcional, sem horário fictício | `horario` nulo | — | F7 | CT-F7-07 | PLANEJADO |
| 8.3.3 | Repetir, incluindo anual, e término | `serie_importancia` | arq §8.5 | F7 | CT-F7-10 | PLANEJADO |
| 8.3.4 | Lembrar-me: antecedência e horário (padrão 09:00 no cliente) | `lembrete_importancia`. `ck_…_antecedencia` | arq §8.6 | F7 | CT-F7-04 | PLANEJADO |
| 8.4.1 | “Salvando…” e sem simultâneos | Idem | D-06 | F7 | CT-F4-05 | PLANEJADO |
| 8.4.2 | Voltar, cancelar e descartar | — | — | — | — | NÃO SE APLICA AO BACKEND |
| 8.4.3 | Validação junto aos campos, inclusive condicionais | `campos[]` | — | F7 | CT-F7-02 | PLANEJADO |
| 8.5.1 | Aparar e validar | — | — | F7 | CT-F7-02 | PLANEJADO |
| 8.5.2 | Data passada: atrasada imediatamente | `atrasada = true` na resposta 201 | — | F7 | CT-F7-03 | PLANEJADO |
| 8.5.3 | Valor previsto não altera o financeiro | Sem movimentação | — | F7 | CT-F7-01 | PLANEJADO |
| 8.5.4 | Repetições; 29/02 anual; situação e lembrete próprios | — | — | F7 | CT-F7-10 | PLANEJADO |
| 8.5.5 | Lembrete futuro no cadastro | `LEMBRETE_NO_PASSADO` | — | F7 | CT-F7-04 | PLANEJADO |
| 8.5.6 | Notificação no app. Reagendar. Cancelar ao concluir ou excluir. A permissão do dispositivo é do cliente | Versões. Push fora do escopo | arq §8.6 | F7 (agendamento), F9 (notificação) | CT-F7-12, CT-F9-01 | PLANEJADO |
| 8.5.7 | Sucesso e navegação para Todos com destaque | Resposta com `id`. A navegação é do cliente | — | F7 | CT-F7-01 | PLANEJADO |
| 8.5.8 | Editar preserva a identidade. Paga não remove o vínculo | 409 `IMPORTANCIA_PAGA_SEM_ALTERAR_DESPESA` | — | F7/F8 | CT-F7-12, CT-F8-16 | PLANEJADO |
| 8.6.1 | Mensagens de nome, categoria e data | — | — | F7 | CT-F7-02 | PLANEJADO |
| 8.6.2 | “Informe um valor previsto maior que zero” | — | — | F7 | CT-F7-02 | PLANEJADO |
| 8.6.3 | 99,90 pendente; pagamento de 105,00 contabilizado | — | — | F7/F8 | CT-F7-01, CT-F8-01 | PLANEJADO |
| 8.6.4 | Mensal 31/01 → fim de fevereiro → 31/03 | — | — | F7 | CT-F7-10 | PLANEJADO |
| 8.6.5 | 15/10, 3 dias antes, 09:00 → 12/10 09:00 | — | — | F7 | CT-F7-04 | PLANEJADO |
| 8.6.6 | Falha mantém os dados. Sem duplicar registro, ocorrências ou lembretes | Idem e transação única | — | F7 | CT-F4-07, CT-F7-01 | PLANEJADO |
| 8.6.7 | Descartar e continuar (cliente). Editar com alcance sem segundo cadastro | — | — | F7 | CT-F7-12 | PLANEJADO (edição) / NÃO SE APLICA (descarte) |

## Tela 9 — Financeiro

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 9.1.1 | Seletor de mês → `mes` em `resumo` e `movimentacoes` | — | C | F6 | CT-F6-04 | PLANEJADO |
| 9.1.2 | Indicadores, saldo e comparação → `GET /financeiro/resumo`. “Ver detalhes” no cliente | — | — | F6 | CT-F6-04, 08 | PLANEJADO |
| 9.1.3 | Gráfico diário → `grafico_diario` com todos os dias | — | — | F6 | CT-F6-07 | PLANEJADO |
| 9.1.4 | Categorias com total. Ícone no cliente → `categorias_despesa` (completa) | “Outros” próprio | — | F6 | CT-F6-12 | PLANEJADO |
| 9.1.5 | Últimas 5 → `ultimas_movimentacoes` | Vínculo indicado (F8) | — | F6 | CT-F6-09 | PLANEJADO |
| 9.1.6 | Consulta completa em partes, filtros e limpar → `GET /financeiro/movimentacoes` | `filtros_ativos` | — | F6 | CT-F6-09 | PLANEJADO |
| 9.1.7 | Ações de cadastro | Endpoints das telas 10 e 11 | — | — | — | NÃO SE APLICA AO BACKEND (navegação) |
| 9.1.8 | Navegação inferior | — | — | — | — | NÃO SE APLICA AO BACKEND |
| 9.2.1 | Registros válidos. Previstos fora. Vinculada contada uma vez | `excluida_em IS NULL` | — | F6/F8 | CT-F6-11, CT-F8-01 | PLANEJADO |
| 9.2.2 | Saldo = receitas − despesas. Painel com o mesmo cálculo | `totais_periodo` | — | F6 | CT-F6-04 | PLANEJADO |
| 9.2.3 | Valores positivos. Sinal pelo tipo. Centavos exatos | `Decimal` | D-16 | F6 | CT-F6-05 | AGUARDANDO_DECISAO (DEC-MV-17) |
| 9.2.4 | Gráfico e categorias somam os totais | — | — | F6 | CT-F6-07 | PLANEJADO |
| 9.2.5 | Filtros só na lista. Tipo e categoria compatíveis | 422 `CATEGORIA_INVALIDA` | — | F6 | CT-F6-09 | PLANEJADO |
| 9.2.6 | Intervalos de comparação | `intervalos_comparacao` | arq §8.8 | F6 | CT-F6-08 | PLANEJADO |
| 9.2.7 | Fórmula com 1 casa. Base zero | `comparar` | — | F6 | CT-F6-08 | AGUARDANDO_DECISAO (DEC-MV-17, arredondamento) |
| 9.2.8 | Aumento, redução ou estabilidade. Interpretação de despesas no cliente | `tendencia` | — | F6 | CT-F6-08 | PLANEJADO |
| 9.3.1 | Detalhes e importância vinculada → `GET /financeiro/movimentacoes/{id}` | `importancia.disponivel` | C | F6/F8 | CT-F6-09, CT-F8-11 | PLANEJADO |
| 9.3.2 | Editar receita ou despesa. Recalcular meses. Tipo mantido → `PATCH` | `tipo` imutável | X | F6 | CT-F6-06, 10 | PLANEJADO |
| 9.3.3 | Confirmação com aviso (cliente) → `DELETE` | — | — | F6/F8 | CT-F6-11, CT-F8-04 | PLANEJADO |
| 9.3.4 | Exclusão atômica que reabre a importância e reativa lembretes futuros | arq §8.7 | X | F8 | CT-F8-04, 13 | PLANEJADO |
| 9.3.5 | Mês vazio × busca vazia → `possui_movimentacoes_mes` e totais zerados | — | — | F6 | CT-F6-09 | PLANEJADO |
| 9.3.6 | Erro ≠ zeros | Erro estruturado | D-08 | F6 | CT-F1-09 | PLANEJADO |
| 9.4.1 | 2.450,75 / 1.230,40 → 1.220,35. Saldo negativo | — | — | F6 | CT-F6-04, 03 | PLANEJADO |
| 9.4.2 | Setembro × outubro na edição | — | — | F6 | CT-F6-06 | PLANEJADO |
| 9.4.3 | 0,10 + 0,20 = 0,30 | — | — | F6 | CT-F6-05 | PLANEJADO |
| 9.4.4 | Filtros sem alterar indicadores. Limpar restaura | — | — | F6 | CT-F6-09 | PLANEJADO |
| 9.4.5 | 1.000 → 1.100 = 10%. Base zero | — | — | F6 | CT-F6-08 | PLANEJADO |
| 9.4.6 | 28 a 31 dias. Somas conferem | — | — | F6 | CT-F6-07 | PLANEJADO |
| 9.4.7 | Cancelar ou confirmar. Despesa vinculada reabre a importância | — | — | F6/F8 | CT-F6-11, CT-F8-04 | PLANEJADO |

## Tela 10 — Cadastrar receita

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 10.1.1 | Nome 3–100 → `POST /financeiro/receitas` | — | X + Idem | F6 | CT-F6-02 | PLANEJADO |
| 10.1.2 | Valor > 0, 2 casas. Inteiro exibido com centavos | `ValorMonetario`. Saída `"100.00"` | D-16 | F6 | CT-F6-01, 02 | AGUARDANDO_DECISAO (DEC-MV-17) |
| 10.1.3 | Categorias de receita | FK composta `(categoria_id, tipo)` | — | F6 | CT-F6-02 | PLANEJADO |
| 10.1.4 | Data ≤ hoje (padrão hoje no cliente) | Verificação no fuso | — | F6 | CT-F6-02 | PLANEJADO |
| 10.2.1 | Descrição ≤ 200 | — | — | F6 | CT-F6-02 | PLANEJADO |
| 10.2.2 | Origem/pagador ≤ 100 → `contraparte` | — | — | F6 | CT-F6-01 | PLANEJADO |
| 10.2.3 | Forma de recebimento opcional | `ck_…_forma_tipo` | — | F6 | CT-F6-02 | PLANEJADO |
| 10.3.1 | “Salvar receita”, “Salvando…” e “Salvar alterações” | Idem. Os rótulos são do cliente | — | F6 | CT-F6-13 | PLANEJADO |
| 10.3.2 | Voltar e descartar | — | — | — | — | NÃO SE APLICA AO BACKEND |
| 10.3.3 | Validação e formatação monetária | `campos[]`. A formatação é do cliente | — | F6 | CT-F6-02 | PLANEJADO |
| 10.4.1 | Aparar. Valores e datas inválidos. Categoria incompatível | — | — | F6 | CT-F6-02 | PLANEJADO |
| 10.4.2 | Sem arredondamento silencioso | `CASAS_DECIMAIS` | — | F6 | CT-F4-13, CT-F6-02 | PLANEJADO |
| 10.4.3 | Recebimento confirmado. Sem geração mensal | — | — | F6 | CT-F6-01 | PLANEJADO |
| 10.4.4 | Sucesso e navegação para o mês da data | Resposta com `data_movimentacao` | — | F6 | CT-F6-01 | PLANEJADO |
| 10.4.5 | Edição mantém o tipo e o registro | — | — | F6 | CT-F6-10 | PLANEJADO |
| 10.4.6 | Repetição → um registro. Receitas iguais legítimas | Chave nova = nova operação | D-06 | F6 | CT-F6-13 | PLANEJADO |
| 10.5.1 | Mensagens específicas | arq §4.5 | — | F6 | CT-F6-02 | PLANEJADO |
| 10.5.2 | Data futura. Casas decimais | — | — | F6 | CT-F6-02 | PLANEJADO |
| 10.5.3 | 100,00 → receitas 100, despesas 0, saldo 100, sinal positivo | — | — | F6 | CT-F6-04 | PLANEJADO |
| 10.5.4 | 100 → 120 sem duplicar | — | — | F6 | CT-F6-10 | PLANEJADO |
| 10.5.5 | Falha ou perda de conexão: nova tentativa sem duplicar | Replay | D-06 | F6 | CT-F6-13 | PLANEJADO |
| 10.5.6 | Descartar e continuar. Reabrir mostra o confirmado | `GET` detalhe | — | F6 | CT-F6-10 | PLANEJADO (detalhe) / NÃO SE APLICA (descarte) |

## Tela 11 — Cadastrar despesa

| Req | Caso de uso → endpoint | Dados / invariantes | Transação / decisão | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| 11.1.1 | Nome 3–100 → `POST /financeiro/despesas` | — | X + Idem | F6 | CT-F6-03 | PLANEJADO |
| 11.1.2 | Valor pago > 0, 2 casas. Saída negativa no saldo | — | D-16 | F6 | CT-F6-03 | PLANEJADO |
| 11.1.3 | Categorias de despesa = resumo | — | — | F6 | CT-F6-12 | PLANEJADO |
| 11.1.4 | Data ≤ hoje. O vencimento não substitui | — | — | F6/F8 | CT-F6-03, CT-F8-01 | PLANEJADO |
| 11.2.1 | Descrição ≤ 200 | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.2.2 | Destinatário ≤ 100 → `contraparte` | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.2.3 | Forma de pagamento | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.2.4 | Importância vinculada (elegível) → `importancia_id` e `GET /importancias/disponiveis-pagamento` | Elegibilidade | X | F8 | CT-F8-01, 14 | PLANEJADO |
| 11.3.1 | Rótulos do botão e “Salvando…” | Idem. Rótulos no cliente | — | F6/F8 | CT-F6-13 | PLANEJADO |
| 11.3.2 | Voltar, descartar e validação | — | — | F6 | CT-F6-03 | PLANEJADO (validação) / NÃO SE APLICA (descarte) |
| 11.4.1 | Validações sem arredondamento | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.4.2 | Despesa sem vínculo normal. Não cria importância | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.4.3 | Saldo negativo permitido | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.4.4 | Data futura orienta para Importâncias | Mensagem de 11.6.1 | — | F6 | CT-F6-03 | PLANEJADO |
| 11.4.5 | Sucesso conforme a origem do fluxo. Edição preserva | Resposta inclui a importância (F8). Navegação no cliente | — | F6/F8 | CT-F8-01 | PLANEJADO |
| 11.4.6 | Proteção contra repetição também sem vínculo | Idem | D-06 | F6 | CT-F6-13 | PLANEJADO |
| 11.5.1 | Pré-preenchimento e categoria sugerida | `categoria_financeira_sugerida` | — | F8 | CT-F8-15 | PLANEJADO |
| 11.5.2 | Uma operação consistente | Transação única | arq §8.7 | F8 | CT-F8-13 | PLANEJADO |
| 11.5.3 | Pago diferente do previsto. Sem pagamento parcial | — | — | F8 | CT-F8-01 | PLANEJADO |
| 11.5.4 | Uma despesa por ocorrência e vice-versa. Conflito com mensagem literal | `IMPORTANCIA_JA_PAGA` | X + UNIQUE | F8 | CT-F8-05, 06, 12 | PLANEJADO |
| 11.5.5 | Vincular despesa existente → `PUT /importancias/{id}/pagamento` e `GET /financeiro/despesas/disponiveis-vinculo` | Sem alterar valor, categoria ou data | X | F8 | CT-F8-02, 14 | PLANEJADO |
| 11.5.6 | Edição do vínculo com confirmação. Troca atômica | `confirmar_alteracao_vinculo` | X | F8 | CT-F8-03, 09, 10 | PLANEJADO |
| 11.5.7 | Exclusões cruzadas | — | — | F8 | CT-F8-04, 11 | PLANEJADO |
| 11.6.1 | Mensagens. Data futura | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.6.2 | 100 / 30 → 70. 130 → −30 | — | — | F6 | CT-F6-03 | PLANEJADO |
| 11.6.3 | 99,90 previsto e 105,00 pago | — | — | F8 | CT-F8-01 | PLANEJADO |
| 11.6.4 | Vínculo existente sem alterar o total. Nova tentativa preserva | — | — | F8 | CT-F8-02 | PLANEJADO |
| 11.6.5 | 105 → 100. Troca de mês | — | — | F8 | CT-F8-03 | PLANEJADO |
| 11.6.6 | Cancelar e falha sem efeito parcial e sem duplicar | — | — | F8 | CT-F8-13, CT-F6-13 | PLANEJADO |
| 11.6.7 | Remover vínculo × excluir despesa. Atrasada se vencida | — | — | F8 | CT-F8-04, 10 | PLANEJADO |

## Contrato de dados (`CLAUDE.md`, tabelas)

| ID | Item | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- |
| T-01 a T-13 | 13 tabelas e 134 colunas (tipos de ID conforme ADR-0002) | F2 | CT-F2-01 a 03 | VERIFICADO (F2): auditoria `APROVADO_COM_P3` e commit `91be324` |
| T-SEED | 30 categorias | F2 | CT-F2-06, 07 | VERIFICADO (F2) |
| R-USUARIO | Normalização e unicidade de e-mail. Nascimento não futuro. Fuso persistido | F2 (UNIQUE), F3 (aplicação) | CT-F2-16, CT-F3-01 a 03 | Parte F2 (unicidade de e-mail) VERIFICADA (CT-F2-16). Parte F3 PLANEJADA |
| R-RECUPERACAO | Recuperação única. Hashes. Reenvio. Tentativas. Consumo único | F2/F3 | CT-F2-16, CT-F3-11 a 19 | Parte F2 (unicidades de usuário e de token) VERIFICADA (CT-F2-16). Parte F3 PLANEJADA |
| R-SERIE | CHECKs de série. `NENHUMA`. `numero_final = 0` | F2/F5/F7 | CT-F2-13, 15, CT-F5-29 | Parte F2 (CHECKs) VERIFICADA (CT-F2-13, 15). Partes F5 e F7 PLANEJADAS |
| R-OCORRENCIA | Par série/número. Valores próprios. Situação calculada | F2/F5/F7 | CT-F2-13, CT-F5-28 | Parte F2 (par série/número) VERIFICADA (CT-F2-13). Partes F5 e F7 PLANEJADAS |
| R-IMPORTANCIA | Valor previsto condicional. Conclusão manual. Pagamento em um lado | F2/F7/F8 | CT-F2-14, 15, CT-F8-* | Parte F2 (CHECKs condicionais) VERIFICADA (CT-F2-14, 15). Partes F7 e F8 PLANEJADAS |
| R-CATEGORIA | Catálogos compartilhados. Inativas no histórico. Exclusão física impedida | F2/F4 | CT-F2-18, CT-F4-12 | Parte F2 (catálogos e `RESTRICT`) VERIFICADA (CT-F2-18). Parte F4 PLANEJADA |
| R-MOVIMENTACAO | FK `(categoria, tipo)`. Formas por tipo. Vínculo | F2/F6/F8 | CT-F2-12, 14 | Parte F2 (FK por tipo, formas e vínculo) VERIFICADA (CT-F2-12, 14, 15). Partes F6 e F8 PLANEJADAS |
| R-LEMBRETE | Um por ocorrência. Versão. Situação × `enviado_em`. Reagendamento | F2/F7/F9 | CT-F2-15, 16, CT-F7-12, CT-F9-* | Parte F2 (unicidade e situação × envio) VERIFICADA (CT-F2-15, 16). AGUARDANDO_DECISAO (DEC-MV-19) para F7 e F9 |
| R-NOTIFICACAO | Uma por versão. Conteúdo congelado. Lida | F2/F9 | CT-F2-16, CT-F9-08 | Parte F2 (uma por versão) VERIFICADA (CT-F2-16). Parte F9 PLANEJADA |
| R-IDEMPOTENCIA | Unicidade. Conteúdo. Replay. Mesma transação | F2/F4 | CT-F2-16, CT-F4-* | Parte F2 (unicidade) VERIFICADA (CT-F2-16). Protocolo da F4 AGUARDANDO_DECISAO (DEC-MV-15) |
| PROP | 5 FKs compostas de propriedade e `UNIQUE(id, usuario_id)` | F2 | CT-F2-11 | VERIFICADO (F2) |
| RI-1 | Constraints no banco e validações na aplicação | F2+ | CT-F2-*, CTs de validação | Parte F2 (constraints no banco) VERIFICADA (CT-F2-*). Validações de aplicação PLANEJADAS |
| RI-2 | `IS NULL` explícito | F2 | CT-F2-14, 15 | VERIFICADO (F2) |
| RI-3 | Exclusão lógica fora de consultas e totais | F5–F8 | CT-F5-13, CT-F6-11 | PLANEJADO |
| RI-4 | Excluir movimentação vinculada | F8 | CT-F8-04 | PLANEJADO |
| RI-5 | Excluir importância | F7/F8 | CT-F7-13, CT-F8-11 | PLANEJADO |
| RI-6 | Vincular e trocar | F8 | CT-F8-02, 09 | PLANEJADO |
| RI-7 | Serialização. Sem despesa só se não paga | F4/F8 | CT-F8-05 a 09, 16 | PLANEJADO |
| RI-8 | `RESTRICT`. Sem cascata ou `SET NULL` | F2 | CT-F2-18 | VERIFICADO (F2) |
| RI-9 | Exclusão de conta fora do escopo | — | — | Fora do escopo (sem fluxo especificado) |
| REP | Representação de repetições (materialização, alcance, mensal/anual) | F5/F7 | CT-F5-20 a 31, CT-F7-10 a 13, 17 | AGUARDANDO_DECISAO (DEC-MV-16, 18) |
| CALC | Informações calculadas sem coluna | F5–F10 | CTs de indicadores | PLANEJADO |
| IDX | 8 índices iniciais | F2 | CT-F2-10 | VERIFICADO (F2) |
| MAP | Mapeamento SQLAlchemy (Enum textual, `Numeric`, `DateTime` tz, `JSON`) | F1/F2 | CT-F2-02, 17, 19 | VERIFICADO (F2) |

## Escopo financeiro (instrução do usuário, 2026-10-11)

| ID | Item | Fase | Verificação | Situação |
| --- | --- | --- | --- | --- |
| ESC-FIN-1 | Receitas e despesas cadastradas, editadas e excluídas manualmente | F6 | CT-F6-01, 03, 10, 11 | PLANEJADO |
| ESC-FIN-2 | Totais e saldo calculados a partir dos lançamentos do período. Exemplo 3000.00 − (100.00 + 50.00 + 200.00) = 2650.00 | F6 | CT-F6-04, 14 | PLANEJADO |
| ESC-FIN-3 | Sem saldo informado manualmente: nenhuma coluna, tabela ou endpoint de saldo | F2/F6 | CT-F2-02 (introspecção literal), CT-F6-14, auditoria (`plano_validacao_auditoria.md` §9) | Parte F2 (nenhuma coluna ou tabela de saldo) VERIFICADA (CT-F2-02). Parte F6 PLANEJADA |
| ESC-FIN-4 | Forma de recebimento e de pagamento apenas descritiva | F6 | CT-F6-02, 03 | PLANEJADO |
| ESC-FIN-5 | “Registrar pagamento” como informação do usuário. Valor previsto fora dos totais. Despesa vinculada contada uma vez | F7/F8 | CT-F7-01, CT-F8-01, 02 | PLANEJADO |

## Exclusões de escopo registradas

| Item | Motivo | Decisão |
| --- | --- | --- |
| Conexão ou autenticação com bancos; Open Finance/Open Banking | Fora do produto: o financeiro é manual (arquitetura §1.1) | Instrução do usuário em 2026-10-11 (decidido) |
| Importação ou sincronização automática de receitas, despesas, extratos ou faturas | idem | Instrução do usuário em 2026-10-11 (decidido) |
| Gateways ou processadores de pagamento; execução de pagamentos, Pix, transferências ou boletos | idem. A forma de pagamento é só descritiva | Instrução do usuário em 2026-10-11 (decidido) |
| Conciliação com saldos reais de contas bancárias | idem | Instrução do usuário em 2026-10-11 (decidido) |
| Área de Perfil e alteração de fuso | Sem requisitos em `CLAUDE.md` | DEC-MV-13, aprovada em 2026-10-13: na v1, só `GET /api/v1/usuarios/me` |
| Logout no servidor e revogação individual | Sem tabela de sessão | DEC-MV-09, aprovada em 2026-10-13: logout só no cliente; um token vale até expirar, salvo troca de senha ou do segredo |

Exclusões que ainda dependem de aprovação:

| Item | Motivo | Decisão |
| --- | --- | --- |
| Push no dispositivo e cadastro de dispositivos | O contrato atual cobre só a notificação interna | ADR-0001 D-11 |
| Exclusão definitiva de conta | RI-9 | Fora do escopo |
| Limitação de tentativas de login | Infraestrutura de borda | DEC-MV-21 |
