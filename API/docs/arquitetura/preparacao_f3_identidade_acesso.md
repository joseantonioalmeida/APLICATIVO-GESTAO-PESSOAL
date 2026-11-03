# Preparação da F3 — Identidade e acesso (dossiê)

| Campo | Valor |
| --- | --- |
| Documento | `docs/arquitetura/preparacao_f3_identidade_acesso.md` |
| Estado | **APROVADO** em 2026-10-13 (M16): DEC-MV-09 a 13 e DEC-MV-14 no escopo limitado da F3, nos termos das §4 e §10, e diffs da §8 aplicados (§14). Histórico: entregue para revisão (M14) e revisado (M15) |
| Data | 2026-10-13 |
| Autor | Claude Opus 5.5 (arquitetura e revisão crítica) |
| Autorização desta preparação | Mensagem do usuário salva em `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` (M14 em `indice.md` §4): leitura, conferência do commit da F2, análise e atualização documental. **Não** aprova DEC-MV-09 a 13, **não** aceita riscos e **não** autoriza implementar |
| Revisão dirigida | Mensagem do usuário de 2026-10-13 com seis pontos de revisão (M15; registro no índice pendente de autorização). Autoriza ajustar os rascunhos e apresentar reconciliações. **Não** aprova DEC-MV-09 a 13, a parcela da DEC-MV-14 nem alterações de contratos vigentes. Registro na §13 |
| Baseline técnico | Commit da F2 `91be324c88c5a3f99a49b1b1700963e32ef257e9` (pai `90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30`), conferido em §1 |
| Aprovação | Mensagem do usuário de 2026-10-13 (M16), registrada no `indice.md` §4. É documental: não autoriza implementação, testes, migrações, configuração, dependências, `.env` nem operações de escrita no Git |
| Prompt derivado | `PROMPTS/PROMPT_MASTER_SONNET_5_F3_IDENTIDADE_ACESSO.md`, estado `PRONTO_PARA_ETAPA_A` (2026-10-13). Histórico: `BLOQUEADO — AGUARDANDO_DECISAO` até a M16 |
| Evidências | Preparação: `~/minhavida_evidencias/f3_preparacao_ItDnDcl1/`. Revisão M15: `~/minhavida_evidencias/f3_revisao_Lbkj9sjq/` (logs, sondas e manifesto) |

Convenção: **verificado** (lido ou executado nesta preparação), **proposto** (recomendação ainda sem aprovação), **aprovado anteriormente** (registrado no `indice.md` §4) e **não executado**. Nenhum teste da aplicação foi executado nesta preparação.

---

## 0. Resumo

> **Atualização de 2026-10-13 (M16).** Decisões aprovadas, diffs da §8 aplicados, ACH-MV-ARQ-015 e 026 a 038 encerrados e Prompt F3 em `PRONTO_PARA_ETAPA_A` (§14). Os itens abaixo descrevem a entrega (M14) e a revisão (M15) e são históricos.

- **G6 da F2: verificado e cumprido.** O commit `91be324` contém exatamente os 43 arquivos do fechamento, com o conteúdo do manifesto (43/43) e os 30 arquivos técnicos aprovados na auditoria (30/30) (§1).
- **Decisões da F3:** as cinco (DEC-MV-09 a 13) continuam `AGUARDANDO_DECISAO`. Recomendo aprovar as cinco **com os refinamentos** da §4, que fecham lacunas de contrato encontradas nesta análise. A DEC-MV-10 envolve aceitar um risco de privacidade, que precisa ser dito na aprovação (§4.2).
- **Dependência omitida:** as travas de linha da recuperação pertencem a D-05, cuja aprovação é a DEC-MV-14 (F4). A F3 precisa de uma **aprovação parcial** da DEC-MV-14, limitada a essas travas (§4.6), no mesmo formato da DEC-MV-25.
- **Achados novos:** 13 (ACH-MV-ARQ-026 a 038), todos de especificação, nenhum da implementação da F2 (§5.2). Os P2 bloqueiam a liberação do Prompt F3 até a aprovação dos diffs da §8.
- **ACH-MV-ARQ-018:** encerrado com a evidência da auditoria da F2 (§5.3).
- **ACH-MV-F2-002:** as quatro lições foram aplicadas e verificadas no Prompt F3 (§11). Encerramento documental registrado no índice.
- **Revisão dirigida (M15):** seis correções nos rascunhos: data de nascimento, e-mail canônico, organização compatível com D-02, divergências entre dossiê e prompt, sincronização dos testes de concorrência e explicação da DEC-MV-10. A revisão traz três propostas novas, ainda sem aprovação: CM-2, AR-8 revisto e AR-10. Detalhes e evidências na §13.

---

## 1. Conferência do commit da F2 (somente leitura)

Comandos e saídas em `00a` a `00j`, `01_conferencia_commit.log` e `02_manifesto_fechamento.log` (diretório de evidências).

| Prova | Resultado |
| --- | --- |
| Raiz e HEAD | `/home/jose/projects/app_gestão_pessoal/API`; `HEAD = 91be324c88c5a3f99a49b1b1700963e32ef257e9`; `HEAD^ = 90412ec4b9ecb6594e0b9e571c1dbba0bb1a4a30` |
| Mensagem | `F2: esquema de dados (APROVADO_COM_P3 na auditoria)`, autor e committer `jose antonio`, 2026-10-13 16:03:21 -0300 |
| Delta | `git diff-tree` = `lista_commit.txt` (43 caminhos). Tipos: 26 `A` e 17 `M`, sem `D` |
| Conteúdo | SHA-256 dos **blobs do commit** (`git cat-file blob HEAD:<caminho>`) = `manifesto_commit.sha256`: **43/43** |
| Objeto técnico | Blobs dos 30 arquivos da implementação = manifesto da auditoria (`f2/18c_sha256_f2.log`): **30/30** |
| Relatório da auditoria | Blob `f4c529692d6032a052083375f94fc493ea73c1d6449dacfbe1cc16e266cf1560`, igual ao registrado |
| Documentos do fechamento | Blobs com os hashes posteriores ao fechamento (por exemplo, `indice.md` `0e802d7edfa32cb5f317c11a95a88a07becdfebc39503600fa6c4aa40962099d`; Prompt F2 `752b32ba19df519d5a940566160dfd66dd03cbe65ff127ca66a4ce152a91dadb`). A versão implementada do Prompt F2 (`007c6918d9aaa5eb9d41237bef6af96624867dca7b1d957e2eaf677022bf847c`) está preservada em `f2_fechamento_DFR1NBKL/antes/` |
| Árvore | 77 arquivos = 51 da F1 + 26 adicionados. Sem `.env`, ambiente virtual ou caches. `.env.exemplo` e `compose.yaml` (interpolado) estão presentes, como esperado |
| Índice e working tree | Índice vazio. Nenhuma diferença em arquivos rastreados. Único não rastreado: `PROMPTS/PROMPT_MASTER_OPUS_5_5_CONFERENCIA_F2_PREPARACAO_F3.md` (entrada desta sessão, fora do commit auditado) |
| Branch | `main`, 2 commits à frente de `origin/main`. Isso não afeta o G6 local; nada foi publicado |

**Diferença identificada, sem efeito no G6:** no diretório de fechamento, só `mensagem_commit.txt` diverge do `MANIFESTO_FECHAMENTO.sha256`. O hash passou de `c7cae4685e2313009f9ba1b0f26b250506b9689976fbe06b1539ae1785d96cdd` para `c0ee547a24c2d32bca7e7db41ac90fc9fb4bb289bd870e537416cb043090e7b8`. O arquivo foi alterado às 16:03:02, 19 segundos antes do commit. O texto atual é idêntico à mensagem do commit, que não tem a linha `Co-Authored-By`; a resposta do fechamento previa essa edição como opcional. A lista e o manifesto do commit estão intactos.

**Conclusão:** G6 da F2 **cumprido**. O commit `91be324` é o baseline técnico da F3. O veredito histórico da F2 continua `APROVADO_COM_P3`. Esta conferência foi só de leitura: não foi uma nova auditoria nem executou testes.

---

## 2. Fontes lidas

SHA-256 completos em `06_fontes_sha256.log`, calculados antes das alterações documentais desta sessão.

| Fonte | SHA-256 | Partes lidas |
| --- | --- | --- |
| `CLAUDE.md` | `35fda3df29e2ae1bd2172a35c430944f4b5fb7d08dd26e0c9bf2123da0405e7d` | §1 e §2; telas 1, 2, 3 e 4.1.1; tabelas 1 (`usuario`) e 2 (`recuperacao_senha`); mapeamento SQLAlchemy. As linhas truncadas 3, 10 e 12 não foram inferidas (ACH-MV-ARQ-012) |
| `docs/arquitetura/indice.md` | `0e802d7edfa32cb5f317c11a95a88a07becdfebc39503600fa6c4aa40962099d` | Integral |
| `docs/arquitetura/analise_projeto_minhavida.md` | `a61962f06274c2bed1775e425d3e1b55a0b0a41995a336b890e7fa83503c4303` | REC-MV-007, 011, 017 a 020; §7 (achados); §8 (riscos); §9 (DEC-MV-09 a 14 e 21) |
| `docs/adr/0001_arquitetura_api_minhavida.md` | `7f7c4745c204a026a3742617bc8525ece2d0b99a722e37ec87d94a0740e23760` | Tabela de decisões; D-03, D-04, D-05, D-07, D-08, D-13, D-14, D-15 e D-16 |
| `docs/adr/0002_identificadores_uuid.md` | `951fb3936affa3eb1dcab67f89507eb9620630e938b2868b2f3ebf4b632b7593` | Contrato aceito (sem reabrir) |
| `docs/arquitetura/arquitetura_api_minhavida.md` | `e2d85ca7819cc3cf5f378d640b5307733c732ff428742de6b8797cf8612a278b` | §2 (árvore e dependências), §3 (Settings, engine, logs), §4 (convenções, autenticação, erros, mensagens), §5, §6 (inclusive §6.6), §7, §8.2, §8.3, §9 e §9.1, §11 e §12 |
| `docs/arquitetura/plano_fases_api.md` | `fef191ba3bc8e4581622788d2d0bb7fa26119fb13b3300ef681d0554500f291f` | §3, fichas F2, F3 e F4 |
| `docs/arquitetura/plano_validacao_auditoria.md` | `fe1aef81eae46e9948b95fbae51e64aa291984e08614c26b4e3c5812af1ed494` | §2, §3, catálogo F3, §5, §6, §8, §9 e §10 |
| `docs/arquitetura/matriz_requisitos_api.md` | `ed3b2accbc0ed565fbfe9283d4e56c694cecf72ae537e42414789ab06788330c` | Convenções, telas 1 a 3, 4.1.1, contrato de dados e exclusões |
| `docs/auditorias/AUDITORIA_F2_ESQUEMA_DADOS.md` | `f4c529692d6032a052083375f94fc493ea73c1d6449dacfbe1cc16e266cf1560` | §2 (objeto), §6 (CT-F2-20), §10 e §13 |
| Prompt F1 / Prompt F2 | `e1d6ac1ac2282bac95b39981a1369f40dd1cc4a94acc45d5e9f5764e42350e05` / `752b32ba19df519d5a940566160dfd66dd03cbe65ff127ca66a4ce152a91dadb` | Regras absolutas, formato dos comandos, erratas do §13 do Prompt F2 |
| Instrução desta sessão | `46c49e0d15ba148f56158b1302f5d7b8893b6a31b334392a719de95451826695` | Integral |
| Código | `settings.py` `039937f6322149f5ac87b586192e68418c29a562a0e2419f90669120192dd0f0`; `main.py` `bb566f5402050cd6dd60bc581bf17e6925415cc256775f5210f5cfea45e263ee`; `database.py` `50ab98141652b19a5ba21e690e6d6dacc74aa24b5803764e8c2541388d297def`; `erros.py` `4e8adcce3eb13b78462c6cbdb96fb3cae39c1758b645c1b24d7c9f9f7bb63836`; `rastreamento.py` `b92bb3c80336d23687aa2330c9fa75707a99620acd5f0e39b1acc9897972fc37`; `schemas/erro.py` `df9c3382d0e5fed29a0f1347354b0cd5cb4b43e142a9944d0f85b90acf63bf5b`; `routers/saude.py` `5fbda750f3739079ea11d5a9a2b114fa795e2db1c4aa6f34786e1d89884d4b32`; `models/usuario.py` `bd0872b242e7eba7ec090fb0bce23ac2c7deda36d38ffae0e70849a3e731ef0a`; `models/recuperacao_senha.py` `2c75f3b4f96ff9e160648d4e2fe4cf176f58444bc8ecf5faf4a41de1f3cd7d25` | Integral |
| Testes e apoio | `tests/conftest.py` `a385540392111aee5e93a6ee6e413b31fede746a8fef63466e44064122d6608e`; `tests/infra/conftest.py` `f94ccc8eabd61e6bccb820035206c26c4011415a361cf71ae7baa330e06115ef`; `tests/infra/test_configuracao.py` `4c2106538fe287e5e415ae02117dc2047523d31723d038354c57fe958c2f4830`; `tests/infra/test_erros.py` `c0fd9e88367c98ec7a4f0f0fc443e3e1860ee740847595a779f7e7d4a4ed4276`; `tests/apoio/rotas_teste.py` `6982ec6299e05ae5af5ce5cb73c746b6b07ae11ff531ccf060ebebdb2567e59a`; `tests/apoio/banco.py` `58fce75d41d2a427812ce317c83bb0864336a37327f28f211ee0d7197f85a94a` | `settings_teste`, `SettingsTeste`, `criar_cliente`, `aguardar_bloqueio`, `limpar_dados`; uso de `Settings` nos testes de configuração; arquivos de `tests/infra` que sobem o app |
| Configuração | `pyproject.toml` `93932958ba2547476637b3cf75c37ba403c324ec6a1c7dd4763183dbdacba721`; `uv.lock` `b951b6b3f69917e7f67c61e430c6a3e5afa8660f500938a666f5a0606bfac06d`; `.env.exemplo` `dc824d5228126e5cfa2ef3c6fe3c939fb99fc3303487109bd1d0c443867dfdb0` | Regras do Ruff (`PL` em preview, `PT`, `FAST`), Pyright, pytest; versões do lock |

O `.env` real não foi lido.

---

## 3. Verificações técnicas desta preparação

Sondas só com bibliotecas já instaladas, sem importar o aplicativo, sem `.env`, sem banco e sem rede (exceto a consulta à documentação oficial abaixo).

| Log | Hipótese | Resultado (verificado) | Limite |
| --- | --- | --- | --- |
| `03_sonda_bibliotecas.log` | Assinatura de `anyio.to_thread.run_sync`; `CapacityLimiter` fora de loop; normalização do `EmailStr`; chaves IANA | anyio 4.15.1: `run_sync(func, *args, abandon_on_cancel=False, cancellable=None, limiter=None)`. Limitador padrão: 40. `EmailStr` minimiza **só o domínio** (`Fulano.Silva@exemplo.com`), apara espaços, recusa `localhost`, `.test`, ponto final e domínio de um rótulo, e **aceita** `josé@exemplo.com`. `ZoneInfo("localtime")` funciona e `localtime` está em `available_timezones()`. `../etc/passwd` e caminhos absolutos dão `ValueError`. 498 chaves no sistema | Lista de fusos depende da base de dados do sistema e do `tzdata` |
| `03` e `04_sonda_cancelamento_anyio.log` | Cancelamento durante trabalho em thread | Pelo **cancel scope do anyio** (caminho do Starlette), com `abandon_on_cancel=False`, o cancelamento espera a thread terminar (0,30 s) e a vaga do limitador só volta depois. Pelo `task.cancel()` **nativo** do asyncio, o retorno é imediato, a thread continua e a vaga é liberada antes do fim. `asyncio.to_thread` nunca espera | A garantia depende de como o cancelamento chega; o comportamento do servidor ASGI não foi sondado aqui |
| `05_sonda_validacao.log` | Serialização de instantes; e-mail ASCII; `\d` | Pydantic 2.13.5 serializa UTC como `2026-10-13T12:00:00Z` (com microssegundos quando houver) e **preserva** outros fusos (`-03:00`). `validate_email(..., allow_smtputf8=False)` recusa `josé@exemplo.com`. `pattern=r"^\d{8}$"` **aceita** dígitos arábicos-índicos e de largura total; `^[0-9]{8}$` recusa | — |
| `07a`–`07c` | Blocos de conteúdo exato do Prompt F3 (`tempo.py` e `tests/apoio/relogio.py`) | `ruff check --no-fix` e `ruff format --check` com o `pyproject.toml` real: limpos. Pyright standard: 0 erros | Validação isolada, fora do repositório |

Documentação oficial consultada (sem instalação):

- PyJWT, `https://pyjwt.readthedocs.io/en/stable/` (`api.html` e `changelog.html`, versão estável mais recente listada: 2.15.1). Fatos usados:
  - `decode(jwt, key, algorithms, options, audience, issuer, leeway)`;
  - opções `verify_exp`, `verify_iat`, `verify_nbf`, `verify_sub`, `verify_jti` e `require`;
  - `require` só verifica presença;
  - desde a 2.6, `iat` no futuro gera `ImmatureSignatureError`;
  - não há como injetar relógio;
  - desde a 2.11, chaves curtas geram `InsecureKeyLengthWarning`, ou `InvalidKeyError` com `enforce_minimum_key_length=True`;
  - desde a 2.10, `sub` precisa ser string.
- argon2-cffi, `https://argon2-cffi.readthedocs.io/en/stable/api.html` (25.1.0). Fatos usados:
  - `PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16, encoding="utf-8", type=Type.ID)`, do perfil `RFC_9106_LOW_MEMORY`;
  - `verify` devolve `True` ou lança `VerifyMismatchError`, `VerificationError` ou `InvalidHashError`;
  - `check_needs_rehash`;
  - a página não trata de GIL nem de segurança entre threads.

As versões que entrarem no lock só serão conhecidas na Etapa B. O Prompt F3 manda conferir esses comportamentos depois da instalação, antes de escrever o código, com parada se divergirem (Prompt F3 §14, passo 3).

---

## 4. Avaliação das decisões

### 4.1. DEC-MV-09 — Autenticação, credenciais e fuso

**Texto e estado atuais.** `analise` §9: “Autenticação: JWT HS256 de 24 h com claim `sv`, Argon2id (`argon2-cffi`), `PyJWT`, sem refresh e logout no cliente. `fuso_horario` obrigatório no registro” — **AGUARDANDO_DECISAO**. Cobre ADR-0001 D-07 e D-13 (ambas PROPOSTAS) e REC-MV-017 e 020.

**Significado prático.** O aplicativo guarda um token assinado que vale até 24 horas. Não há “sair” no servidor: sair apaga o token só no celular. A senha é guardada com um algoritmo lento e próprio para senhas. O fuso do celular é gravado no cadastro e passa a definir o “hoje” da conta.

**O que já limita a decisão.** D-04 (commit só no router), D-08 (catálogo de erros), §3.4 da arquitetura (sem PII em logs), ADR-0002 (IDs UUID), o esquema congelado da F2 (sem tabela de sessão nem coluna de versão de credencial).

**Riscos e controles.**

| Risco | Controle proposto | O que não é garantido |
| --- | --- | --- |
| Token obtido por terceiro | Validade máxima de 24 h. Troca de senha invalida todos os tokens anteriores (`sv`). Troca de `JWT_SEGREDO` invalida **todos** os tokens de todos os usuários (alavanca operacional de emergência) | “Sair” não revoga nada no servidor. Um token roubado vale até expirar, salvo troca de senha ou de segredo. Não há lista de sessões |
| Falsificação de token | HS256 com segredo de pelo menos **32 bytes**; algoritmo fixo; conjunto exato de claims; `typ="access"`; `sub` canônico | Vazamento do segredo compromete todos os tokens até a troca |
| Teste com relógio fixo × biblioteca | Validações temporais da biblioteca desligadas e substituídas por validação manual com o `Relogio` (§6.9). Corrige ACH-MV-ARQ-026 | — |
| Força bruta de senha | Custo do Argon2id. Limitação na borda (DEC-MV-21, **pendente**, F11) | Sem limitador na F3 |
| Exaustão de memória por hash | Limitador próprio de 4 hashes simultâneos (≈ 256 MiB com 64 MiB cada) | Requisições excedentes esperam na fila |
| Enumeração por tempo no login | Hash fictício quando o e-mail não existe, com os mesmos parâmetros | **Não** é tempo constante: consulta, fila do limitador e ramos diferem. Não há teste de tempo |
| Fuso dependente do servidor | Recusar `localtime`, `posixrules`, `Factory` e prefixos `posix/` e `right/` (ACH-MV-ARQ-032) | Aliases antigos podem existir ou não conforme a base de fusos |

**Recomendação principal: aprovar com estes refinamentos.**

- R9.1: validade padrão de 1440 min, configurável só entre 5 e 1440. A faixa atual, até 10080 min (7 dias), permitiria ultrapassar o aprovado sem nova decisão.
- R9.2: claims exatas `{sub, iat, exp, typ, sv}`, com validação temporal manual pelo `Relogio` (§6.9).
- R9.3: segredo com **≥ 32 bytes** em UTF-8. Geração orientada por `secrets.token_urlsafe(32)`. O placeholder do `.env.exemplo` é propositalmente inválido.
- R9.4: `sv` com formato `^[0-9a-f]{16}$`, conferido **antes** de `hmac.compare_digest`, que exige texto ASCII.
- R9.5: Argon2id com 3 / 65536 KiB / 4. Em `producao`, piso de `t ≥ 3` e `m ≥ 65536`. Execução por `anyio.to_thread.run_sync` com limitador dedicado (`ARGON2_MAX_CONCORRENTES = 4`). **Sem** rehash no login, porque mudaria o `sv` e encerraria as outras sessões.
- R9.6: hash fictício calculado uma vez no `lifespan`.
- R9.7: `fuso_horario` obrigatório e validado por `tempo.fuso_valido`. `tzdata` vira dependência direta.
- R9.8: dependências novas `argon2-cffi`, `PyJWT` e `tzdata`. `email-validator` e `anyio` passam a dependências diretas, porque a F3 os importa (lição do ACH-MV-ARQ-011); as versões do lock não mudam.
- R9.9 (revisão M15): **e-mail canônico**. A função `canonicalizar_email` remove os espaços externos, converte para minúsculas, valida com `email_validator.validate_email(check_deliverability=False, allow_smtputf8=False)` e devolve `.ascii_email`, com até 254 caracteres. Um domínio internacionalizado fica em IDNA (`xn--`). Essa forma única é gravada, usada na unicidade e nas buscas do login e da recuperação, e vai no destinatário do SMTP. Variantes do mesmo endereço produzem o mesmo valor: maiúsculas, Unicode composto ou decomposto, largura total e punycode (sonda `01` da revisão). No login, um e-mail que não se canonicaliza segue o caminho do inexistente (hash fictício e 401 `CREDENCIAIS_INVALIDAS`), sem 422 de formato; a resposta não muda. Amplia a regra do `CLAUDE.md` (tabela 1) e por isso exige o diff CM-2.

**Alternativas relevantes.**

- Validade menor, de 1 a 12 h. Reduz a janela de um token roubado, mas, sem refresh, obriga a entrar de novo com frequência no celular. Para mudar, basta configurar entre 5 e 1440 min; não precisa de nova decisão.
- Tabela de sessões ou refresh token. Exigiria esquema novo, proibido pelo contrato vigente, e não é recomendado na v1.

**Impacto.**

- HTTP: `Authorization: Bearer`, 401 `NAO_AUTENTICADO` com `WWW-Authenticate: Bearer`.
- Banco: nenhum.
- Transações: o login só lê.
- Dependências: §6.2.
- Testes: CT-F3-04, 06, 07, 16, 22, 24 e 29.
- Operação: o `.env` real precisa ganhar `JWT_SEGREDO` antes de rodar a API **e** a CLI do Alembic, porque o `env.py` usa `obter_settings()` (ACH-MV-ARQ-028).

**Alterações normativas:** §8, itens AR-1 a AR-6, AD-1 a AD-3 e CM-2.

**Inclui:** D-07 e D-13 com R9.1 a R9.9; o contrato de autenticação da §6.9; as dependências de R9.8.
**Exclui:** refresh token, logout no servidor, lista de sessões, limitação de login (DEC-MV-21), troca de fuso (DEC-MV-13), rehash automático.

### 4.2. DEC-MV-10 — Resposta para e-mail não encontrado

**Texto e estado atuais.** `analise` §9: “Manter a mensagem de 3.4.2 (e-mail não encontrado)” — **AGUARDANDO_DECISAO**. A justificativa da proposta é: “o registro já revela a existência”. Achado associado: ACH-MV-ARQ-015 (P2).

**Significado prático.** Quem digitar um e-mail na tela “Esqueceu a senha” descobre se ele tem conta no MinhaVida.

**Análise crítica.** O argumento original é incompleto. A existência de enumeração no cadastro (409 `EMAIL_JA_CADASTRADO`) não torna inofensivo um segundo canal. Pesam três fatos:

1. O requisito 3.4.2 exige literalmente a mensagem “Não foi possível encontrar seu email”.
2. Com o envio síncrono de D-15, uma resposta genérica **não fecha** o canal: a requisição de um e-mail cadastrado espera o SMTP, e a de um não cadastrado não espera. Fechar o canal exigiria envio assíncrono (fila ou outbox), fora do escopo e não recomendado na v1.
3. Nenhuma limitação de requisições reduz a divulgação. Cada consulta isolada continua mostrando se a conta existe. Um limitador (DEC-MV-21, borda, F11, pendente) só reduziria o volume de consultas por origem, ou seja, a enumeração em massa. A F3 não tem limitador.

**Opções.**

| Opção | Comportamento | Experiência | Requisitos e testes |
| --- | --- | --- | --- |
| **A (recomendada)** | 404 `EMAIL_NAO_ENCONTRADO` com a mensagem de 3.4.2 | O usuário percebe que digitou errado | Literal. CT-F3-10 como está |
| B | 200 com corpo genérico igual para cadastrado e não cadastrado, e envio só quando existe | O usuário que errou o e-mail espera um código que não chega | Exige alterar o requisito 3.4.2 no `CLAUDE.md` e o CT-F3-10. Não fecha o canal de tempo (item 2). A verificação também precisaria equalizar custo |

**Recomendação:** opção **A**, com aceitação **expressa** do risco: a recuperação revela, pela mensagem e pelo tempo de resposta, se um e-mail está cadastrado. O risco é **permanente** enquanto valer a mensagem 3.4.2. Nenhuma fase posterior o elimina sem mudar esse requisito.

O que não mitiga a divulgação:

- o intervalo de 60 s e as 5 tentativas protegem o código de contas existentes; não escondem a existência da conta;
- a limitação de requisições (DEC-MV-21), se for aprovada, só reduz quantas consultas cada origem faz; cada resposta continua reveladora.

Esta decisão **não** aprova a DEC-MV-21.

**Impacto.**

- HTTP: 404 na solicitação.
- Banco, transações e dependências: nenhum.
- Testes: CT-F3-10.
- Operação: risco aceito sem prazo. Reavaliar só se o requisito 3.4.2 mudar (opção B, que também exigiria envio assíncrono para fechar o canal de tempo).

**Inclui:** 404 `EMAIL_NAO_ENCONTRADO`, a aceitação permanente do risco descrito e o diff AR-10.
**Exclui:** DEC-MV-21 e qualquer limitador.

### 4.3. DEC-MV-11 — Recuperação e política de senha

**Texto e estado atuais.** `analise` §9: “Recuperação: 10 min, 5 tentativas inválidas e 60 s entre emissões. Senha com 8–128 caracteres, composição apenas sugerida” — **AGUARDANDO_DECISAO** (REC-MV-011 e 019). O `CLAUDE.md` (tabela 2) marca esses valores como “proposta operacional”.

**Significado prático.** O código vale 10 minutos. Depois de 5 códigos errados é preciso pedir outro. Um novo pedido só é aceito depois de 60 segundos. A senha precisa ter de 8 a 128 caracteres, sem exigir maiúsculas, números ou símbolos.

**Regras exatas propostas (R11):**

| # | Regra |
| --- | --- |
| R11.1 | Constantes de módulo, não variáveis de ambiente: `VALIDADE_CODIGO = 10 min`, `MAX_TENTATIVAS = 5`, `INTERVALO_REENVIO = 60 s`. Assim, valores aprovados não mudam por configuração (diff AR-1) |
| R11.2 | Instante de decisão: `agora = relogio.agora()` capturado **uma vez**, logo **depois** de obter a trava da linha (ou, na primeira emissão, imediatamente antes do `INSERT … ON CONFLICT`). Uma requisição que esperou a trava decide com o tempo de depois da espera (ACH-MV-ARQ-037) |
| R11.3 | Código válido enquanto `agora < expira_em`. Expirado em `agora >= expira_em` |
| R11.4 | Emissão: `emitido_em = expira_em − VALIDADE_CODIGO`. Novo pedido permitido quando `agora >= emitido_em + INTERVALO_REENVIO`, ou seja, exatamente aos 60 s. Antes disso, 429 `REENVIO_MUITO_FREQUENTE` com `Retry-After = max(1, ceil(segundos restantes))` |
| R11.5 | Reenvio: substitui `codigo_hash` e `expira_em`, zera `tentativas` e limpa `verificado_em`, `token_redefinicao_hash` e `utilizado_em`. O código anterior deixa de valer no commit |
| R11.6 | Verificação, nesta ordem, depois da trava: (1) sem usuário ou sem linha → 400 `CODIGO_INVALIDO`, sem contagem; (2) `verificado_em` ou `utilizado_em` preenchido → 409 `CODIGO_JA_VERIFICADO`; (3) expirado → 400 `CODIGO_EXPIRADO`; (4) `tentativas >= 5` → 429 `TENTATIVAS_ESGOTADAS` com `Retry-After` até o próximo pedido permitido (mínimo 1); (5) código diferente → `tentativas + 1`, commit e 400 `CODIGO_INVALIDO`; (6) código igual → `verificado_em = agora` e token |
| R11.7 | **Quinta tentativa inválida:** responde 400 `CODIGO_INVALIDO` (mensagem 3.4.8), porque a resposta descreve a própria tentativa. Da sexta em diante, inclusive com o código correto, a resposta é 429 `TENTATIVAS_ESGOTADAS` até um novo pedido |
| R11.8 | Código: 8 caracteres `^[0-9]{8}$` (só ASCII; ACH-MV-ARQ-033), gerado por `secrets.randbelow(10**8)` formatado `08d`, guardado só como hash Argon2id. Zeros à esquerda preservados; nunca convertido em inteiro |
| R11.9 | Token de redefinição: `secrets.token_urlsafe(32)` (43 caracteres, 256 bits), guardado como SHA-256 hexadecimal (64). Vale enquanto `verificado_em` está preenchido, `utilizado_em` é nulo e `agora < expira_em` da **mesma emissão**. O `CLAUDE.md` exige isso: “O token também deverá respeitar `expira_em`”. Consequência: quem verifica o código no 9º minuto tem 1 minuto para redefinir |
| R11.10 | Senha nova (registro e redefinição): de 8 a 128 caracteres, contados em pontos de código Unicode. Sem normalização (nem NFC/NFKC, nem aparo de espaços). Espaços valem como caracteres. Ausente, vazia ou curta → `SENHA_FRACA` (mensagem 3.4.10). Mais de 128 → `TAMANHO_MAXIMO`. A confirmação precisa ser idêntica caractere a caractere → `SENHAS_DIFERENTES` (3.4.14), no campo `confirmar_senha`. Composição não exigida. A senha de login aceita de 1 a 128, sem política |

**Riscos e controles.**

- Força bruta do código: 5 palpites por emissão e 1 emissão por minuto, num espaço de 10⁸. São no máximo cerca de 5 palpites por minuto por conta.
- Vazamento do banco dentro da validade: hash lento do código.
- Token curto ou adivinhável: 256 bits.
- Diferença de normalização entre teclados: limitação conhecida, documentada, sem normalização silenciosa.

**Impacto.**

- HTTP: §6.4.
- Banco: só a tabela `recuperacao_senha`, sem mudança de esquema.
- Transações: §6.7.
- Testes: CT-F3-09 a 19, 23, 24 e 27.

**Inclui:** R11.1 a R11.10.
**Exclui:** composição obrigatória, normalização de senha, bloqueio de conta e limitação de login.

### 4.4. DEC-MV-12 — Envio de e-mail

**Texto e estado atuais.** `analise` §9: “E-mail por SMTP (biblioteca padrão, em thread), enviado dentro da transação antes do commit. Falso em memória nos testes” — **AGUARDANDO_DECISAO**. Cobre D-15 (PROPOSTA).

**Significado prático.** O servidor envia o código pelo seu próprio provedor de e-mail. Se o envio falhar, nada fica gravado e o usuário pode tentar de novo na hora. Em alguns casos de falha, o usuário pode receber um e-mail com um código que não vale.

**Consequências exatas** (nenhuma promessa de atomicidade distribuída: o PostgreSQL não desfaz um e-mail):

| # | Situação | Banco | E-mail | Resposta | O que o usuário vê |
| --- | --- | --- | --- | --- | --- |
| 1 | Falha antes do envio (conexão, DNS, TLS, autenticação) | Rollback | Não enviado | 503 `FALHA_ENVIO_EMAIL` | Pode repetir na hora: o intervalo conta da última emissão **confirmada** |
| 2 | Erro ou timeout durante o envio | Rollback | Indeterminado: pode ter chegado | 503 `FALHA_ENVIO_EMAIL` | Pode receber um código que não vale; o próximo pedido gera um código válido |
| 3 | O servidor SMTP aceitou, mas a confirmação se perdeu | Rollback | Entregue | 503 | Recebe um código que não vale |
| 4 | Envio concluído e commit falhou | Rollback | Entregue | 5xx (mapeamento de D-08) | Recebe um código que não vale. Se havia uma emissão confirmada anterior, aquele código antigo **continua** válido e o intervalo conta dela |
| 5 | Cancelamento da requisição durante a thread de envio | Rollback (sem commit) | Pode ser concluído | Nenhuma resposta útil ao cliente | Pelo cancel scope do anyio, o envio termina antes de o cancelamento propagar. Pelo cancelamento nativo, a thread segue sozinha (sondas `03` e `04`) |
| 6 | Outra solicitação do mesmo usuário espera a trava durante o envio | — | — | Espera até `lock_timeout` (5 s). Se o envio demorar mais, 503 `CONFLITO_CONCORRENCIA` com `Retry-After: 1` | Repetir. Em geral, a segunda tentativa recebe 429 do intervalo |

**Tempos e recursos.**

- O `SMTP_TIMEOUT_S` (10 s) vale por operação de socket do `smtplib`, não para o envio inteiro.
- Enquanto envia, a conexão do banco fica ociosa dentro da transação. Se o total passar de 30 s, o `idle_in_transaction_session_timeout` encerra a sessão, e o commit falha (situação 4).
- Cada envio prende uma conexão do pool (5 + 5).

Esses limites ficam aceitos e documentados, sem retry automático.

**Recomendação: aprovar com o contrato SMTP da §6.3.**

- `SMTP_SEGURANCA` = `starttls` (padrão, porta 587), `tls` (implícito, 465) ou `nenhuma` (só desenvolvimento e teste).
- TLS com `ssl.create_default_context()`, que verifica certificado e nome. Credenciais só com TLS.
- Toda exceção do `smtplib` e de socket vira `FalhaEnvioEmail` sem dados pessoais (ACH-MV-ARQ-034).
- Envio por `anyio.to_thread.run_sync` com o limitador padrão (40), conexão fechada por gerenciador de contexto.
- `EnviadorEmailMemoria` nos testes. O modo `memoria` é proibido em `producao`.

**Alternativa:** confirmar e só depois enviar. O e-mail nunca levaria um código não gravado, mas uma falha de envio deixaria um código confirmado e não entregue. O usuário precisaria esperar o intervalo ou o sistema precisaria de uma segunda transação para desfazer. Não recomendada: complica sem requisito.

**Inclui:** D-15 com o contrato da §6.3 e as consequências 1 a 6 aceitas.
**Exclui:** fila, outbox, retry automático, tabela nova, notificações push, provedor HTTP de e-mail.

### 4.5. DEC-MV-13 — Perfil e alteração de fuso

**Texto e estado atuais.** `analise` §9: “Sem área de Perfil nem alteração de fuso na v1 (apenas `GET /usuarios/me`)” — **AGUARDANDO_DECISAO**. Matriz, “Exclusões que ainda dependem de aprovação”.

**Significado prático.** O aplicativo mostra o nome do usuário (4.1.1), mas ele não pode editar dados nem trocar o fuso. O fuso cadastrado vale para sempre na v1.

**Consequências do fuso fixo** (sem implementar nada futuro):

- “Hoje”, “atrasada”, “vencendo hoje” e os totais do dia seguem o fuso cadastrado, mesmo em viagem. Exemplo: um usuário de `America/Sao_Paulo` em Lisboa vê o “hoje” virar às 03:00 de Lisboa.
- Lembretes (F9) disparam no horário local do fuso cadastrado.
- Nascimento: o fuso só pesa na validação do cadastro.
- Corrigir um fuso errado exigirá uma decisão futura, com reagendamento de lembretes.

**Recomendação:** aprovar.

**Inclui:** só `GET /api/v1/usuarios/me`.
**Exclui:** edição de perfil, troca de e-mail, troca de fuso, troca de senha autenticada, gestão de sessões e exclusão de conta.

### 4.6. Alcance das aprovações: travas da recuperação (DEC-MV-14 parcial)

Fonte: ADR-0001, tabela de decisões, linha D-05: “Concorrência | DEC-MV-14 | PROPOSTO | F3 (linhas), F4+”. O texto de D-05 trata das “travas de linha somente onde não há usuário autenticado (recuperação)”. A arquitetura detalha o mecanismo em §6.2 (linha `recuperacao_senha`), §6.3 (regra 4) e §6.6 (linhas 1 e 2). A DEC-MV-11 aprova parâmetros, não o mecanismo de concorrência.

**Conclusão:** a F3 depende de uma parte da DEC-MV-14. O menor escopo suficiente é uma **aprovação parcial**, com o mesmo formato da DEC-MV-25:

- `SELECT … FOR UPDATE` em `recuperacao_senha`, pela linha do usuário (solicitar e verificar) ou pelo `token_redefinicao_hash` (redefinir);
- `INSERT … ON CONFLICT (usuario_id) DO NOTHING` na primeira emissão, com a unicidade como proteção final;
- a regra 4 de §6.3 (só essa linha; depois, `usuario` na redefinição);
- `READ COMMITTED`.

**Não** inclui a trava consultiva por usuário, os modos exclusivo e compartilhado, `services/trava.py`, a leitura consistente (D-12) nem as travas de lembretes, que continuam na F4 e na F9.

---

## 5. Reconciliações e achados

### 5.1. Tensões verificadas (instrução §6)

| # | Tensão | Fonte | Resolução proposta |
| --- | --- | --- | --- |
| 1 | Respostas legítimas × “respostas sem token/e-mail” | arq §11, linha “Vazamento de segredos e PII”; CT-F3-25 | Lista explícita de campos permitidos por endpoint (§6.5). Tokens e e-mail só nos campos previstos. Erros e logs nunca ecoam entrada (ACH-MV-ARQ-029) |
| 2 | Relógio controlado × PyJWT | arq §4.2, passo 1; §8.2 (linha 748) | `verify_exp`, `verify_iat` e `verify_nbf` desligados; `require` para presença; validação manual completa (§6.9) (ACH-MV-ARQ-026) |
| 3 | Instante único × espera por trava | arq §7; §8.3.1 (captura antes da trava) × §8.3.2 (depois) | Contexto autenticado: instante capturado uma vez na dependência (D-13). Recuperação: instante capturado uma vez, **depois** da trava (R11.2) (ACH-MV-ARQ-037) |
| 4 | Transação × erro de negócio | arq §5.3; D-04 regra 5 | Mantido: o service devolve `ResultadoVerificacao`; o router faz commit e só então lança `ErroNegocio`. Nenhum handler faz commit (§6.7) |
| 5 | Thread × capacidade | D-07 e D-15 (`asyncio.to_thread`) × arq §11 (“pool de threads padrão do anyio”) | `anyio.to_thread.run_sync`: limitador dedicado de 4 para o Argon2 e limitador padrão (40) para o SMTP, `abandon_on_cancel=False`. Garantia de cancelamento condicional (§4.4, situação 5) (ACH-MV-ARQ-031) |
| 6 | Validação e mensagens | arq §9.1, §4.5; matriz 3.2.1 | E-mail: forma canônica única (R9.9; ACH-MV-ARQ-035). Código `^[0-9]{8}$` (ACH-MV-ARQ-033). Senha conforme R11.10. Nome sem caracteres de controle (ACH-MV-ARQ-034). Data civil `AAAA-MM-DD` por validador próprio, sem modo estrito (§6.4) |
| 7 | Dependências e fixtures | `tests/conftest.py::settings_teste`; `tests/infra/test_configuracao.py`; `alembic/env.py` | `settings_teste` ganha valores sintéticos da F3. Quatro testes de configuração recebem valores sintéticos, e `VARIAVEIS_SETTINGS` passa a limpar as novas variáveis (ACH-MV-ARQ-028) |
| 8 | Esquema congelado | ficha F3, item 6 | Verificado: nenhuma coluna, tabela, índice ou revisão nova é necessária. O intervalo de reenvio deriva de `expira_em`, e a validade é constante (R11.1) |

### 5.2. Achados desta preparação

Todos com origem na **especificação** (arquitetura, ADR, plano ou matriz). Nenhum é defeito da implementação da F2. Severidade conforme o plano de validação §7. Estado: **ENCERRADOS** em 2026-10-13 (M16), com a aprovação e a aplicação dos diffs da §8 (`analise` §7). Na entrega, ABERTOS; o critério de encerramento era a aprovação do diff da §8 e a sua aplicação.

| ID | Sev. | Fonte e fato | Prova | Correção proposta |
| --- | --- | --- | --- | --- |
| ACH-MV-ARQ-026 | P2 | arq §4.2 e §8.2: desligar só `verify_exp`. Desde a 2.6, o PyJWT rejeita `iat` no futuro pelo relógio real, e não aceita relógio injetado | Changelog 2.6.0 e `api.html` (§3) | §6.9; diffs AR-2 e AR-4 |
| ACH-MV-ARQ-027 | P3 | ADR D-07 e arq §11: “≥ 32 bytes”. arq §3.1: “≥ 32 caracteres” | Leitura | ≥ 32 bytes UTF-8 (AR-1) |
| ACH-MV-ARQ-028 | P2 | Settings obrigatórias da F3 quebrariam `settings_teste`, quatro testes de `tests/infra/test_configuracao.py` e a CLI do Alembic sem `.env` atualizado. A ficha F3 (item 8) não lista esses arquivos | `tests/conftest.py` linhas 82–86; `test_configuracao.py` linhas 17–102 e 136 | Arquivos e edições exatas no Prompt F3 §7; passo operacional para o `.env` |
| ACH-MV-ARQ-029 | P2 | arq §11 (“Respostas sem hash, código ou token”) e CT-F3-25 contradizem login, verificação e `UsuarioResposta` | Leitura | §6.5; AR-7; texto refinado do CT-F3-25 |
| ACH-MV-ARQ-030 | P2 | D-05 (DEC-MV-14, F4) contém as travas de linha da recuperação usadas na F3 | ADR-0001 tabela §3; arq §6.2 e §6.3 | Aprovação parcial (§4.6) |
| ACH-MV-ARQ-031 | P3 | `asyncio.to_thread` × “pool padrão do anyio”; memória do Argon2 sem limite próprio (até 40 × 64 MiB) | Sondas `03` e `04` | Limitador dedicado; AR-5 e AD-1 |
| ACH-MV-ARQ-032 | P3 | arq §7: `ZoneInfo` + recusa de `/..` e de caminho absoluto aceita `localtime` | Sonda `03` | `tempo.fuso_valido` (bloco exato, Prompt F3 §8.1); AR-3 |
| ACH-MV-ARQ-033 | P3 | arq §9.1 e matriz 3.2.1: `^\d{8}$` aceita dígitos não ASCII | Sonda `05` | `^[0-9]{8}$`; AR-6 e MZ-1 |
| ACH-MV-ARQ-034 | P3 | O handler genérico registra a exceção; exceções do `smtplib` (por exemplo, `SMTPRecipientsRefused`) carregam o destinatário; um nome com CR/LF quebraria o cabeçalho “Assunto” | `erros.py` linhas 305–315; leitura | Tradução para `FalhaEnvioEmail` sem PII (§6.3); nome sem caracteres de controle |
| ACH-MV-ARQ-035 | P3 | `EmailStr` só minimiza o domínio e aceita SMTPUTF8. O `CLAUDE.md` (tabela 1) exige minúsculas | Sonda `03` | Forma canônica `canonicalizar_email` (R9.9, §6.4); AR-6 e CM-2 |
| ACH-MV-ARQ-036 | P3 | Pseudocódigo de arq §8.2 e §8.3 viola as regras ativas do Ruff: PLR0913 (`solicitar_codigo` com 6 parâmetros) e PLR0911 (`verificar_codigo` com 7 `return`) | `pyproject.toml` (`PL` em preview) | Parâmetros explícitos, no máximo 5 por função, e avaliação auxiliar (§6.3) |
| ACH-MV-ARQ-037 | P3 | arq §8.3.1 captura `agora` antes da trava; §8.3.2, depois | Leitura | R11.2 |
| ACH-MV-ARQ-038 | P3 | `ContextoUsuario`: arq §4.2 inclui `nome_completo`; D-13 não | Leitura | Campos de D-13 (§6.3); AR-2 |

### 5.3. ACH-MV-ARQ-018 — encerramento

Critério registrado (`analise` §7): “Decisão registrada”, com prova em CT-F2-20. Evidências:

- a DEC-MV-08 foi aprovada (`indice.md` §4, M10);
- o CT-F2-20 passou, e a sonda de violações da auditoria da F2 atribuiu os 8 casos negativos aos 4 CHECKs (`AUDITORIA_F2_ESQUEMA_DADOS.md` §6);
- o catálogo materializado é idêntico ao oráculo (§8.2 da auditoria);
- o objeto está integrado no commit `91be324`.

Estado: **ENCERRADO** em 2026-10-13, com a autorização expressa desta sessão (instrução §4). Nenhum outro achado histórico foi encerrado por extensão.

---

## 6. Contratos propostos da F3

> **Vigente desde 2026-10-13 (M16)**, com as decisões da §10 aprovadas e os diffs da §8 aplicados. Havendo divergência, prevalecem os documentos normativos (`CLAUDE.md`, ADR-0001 e arquitetura), conforme `indice.md` §3. Histórico: proposto na entrega.

### 6.1. Módulos e responsabilidades

| Módulo | Responsabilidade | Pode importar |
| --- | --- | --- |
| `tempo.py` | `Relogio`, `RelogioSistema`, `ContextoUsuario`, `fuso_valido`, `hoje_no_fuso` (conteúdo exato no Prompt F3 §8.1) | Biblioteca padrão |
| `seguranca.py` | `ParametrosArgon2`, `HasherSenha`, `HashArmazenadoInvalido`, `ConfiguracaoToken`, `carimbo`, `emitir_token`, `decodificar_token`, `TokenInvalido`, `gerar_codigo`, `gerar_token_redefinicao`, `hash_token` | `argon2`, `jwt`, `anyio`, biblioteca padrão |
| `email.py` | `MensagemEmail`, `FalhaEnvioEmail`, `EnviadorEmail`, `EnviadorEmailSmtp`, `EnviadorEmailMemoria`, `mensagem_codigo`, `criar_enviador` | `anyio`, `settings`, biblioteca padrão |
| `dependencias.py` | `RelogioDep`, `SettingsDep`, `HasherDep`, `EnviadorEmailDep`, `ConfiguracaoTokenDep`, `sem_cache`, `ContextoDep` | `database`, `settings`, `erros`, `tempo`, `seguranca`, `email`, `services/identidade` |
| `services/identidade.py` | `CABECALHO_BEARER`, `registrar`, `entrar`, `montar_contexto`, `obter_usuario_atual` | `models`, `schemas`, `erros`, `tempo`, `seguranca` |
| `services/recuperacao_senha.py` | `solicitar_codigo`, `verificar_codigo`, `redefinir_senha`, `ResultadoVerificacao`, constantes R11.1 | `models`, `schemas`, `erros`, `tempo`, `seguranca`, `email` |
| `services/autorizacao.py` | `obter_do_usuario_ou_404` | `models`, `erros` |
| `schemas/autenticacao.py`, `schemas/usuario.py` | Entradas, respostas e `canonicalizar_email` (§6.4) | `pydantic`, `pydantic_core`, `email_validator`, `tempo` |
| `routers/autenticacao.py`, `routers/usuarios.py` | Endpoints; commit; §5.3 | `services/identidade`, `services/recuperacao_senha`, `schemas`, `dependencias`, `database`, `erros` |

**Nenhum service importa outro service na F3.** A regra vigente é ADR-0001 D-02: “Importações entre services são permitidas apenas para módulos de suporte (`services/recorrencia.py`, `services/idempotencia.py`, `services/trava.py`, `services/situacao.py`), nunca de forma circular.” Ela prevalece sobre a matriz da arquitetura §2.2 até a DEC-MV-24 (ACH-MV-ARQ-021). Consequências:

- `ContextoUsuario` fica em `tempo.py`, que já é o módulo de D-13, e não em `services/identidade`;
- os recursos (`Relogio`, `HasherSenha`, `EnviadorEmail`, `ConfiguracaoToken`) chegam aos services como parâmetros explícitos, com no máximo 5 por função;
- `services/autorizacao` não aparece na lista de suporte de D-02. Na F3, nenhum service o importa: só a rota de teste do CT-F3-30. O uso por services de domínio, a partir da F5, depende da DEC-MV-24;
- `dependencias.obter_contexto` chama `services/identidade.montar_contexto`, e `routers` chamam os services. Isso segue a direção `dependencias → services` e `routers → services` da §2.2.

O AR-8 anterior, que abria uma exceção para `recuperacao_senha` importar tipos de `identidade`, foi **retirado**. O novo AR-8 (§8) só pede registrar no diagrama da §2.2 as arestas que a F3 usa e que ele não mostra. Nenhuma delas fere regra explícita, e a proposta é recomendável, mas não indispensável.

### 6.2. Settings, `.env.exemplo` e dependências

Campos novos em `Settings` (os de F1 não mudam):

| Campo | Tipo | Padrão | Regra |
| --- | --- | --- | --- |
| `JWT_SEGREDO` | `SecretStr` | obrigatório | `len(valor.encode("utf-8")) >= 32`; o erro não ecoa o valor (`hide_input_in_errors=True` já ativo) |
| `JWT_VALIDADE_MINUTOS` | `int` | 1440 | 5–1440 |
| `ARGON2_TIME_COST` | `int` | 3 | 1–10 |
| `ARGON2_MEMORY_COST_KIB` | `int` | 65536 | 8–1048576 e `>= 8 × ARGON2_PARALLELISM` |
| `ARGON2_PARALLELISM` | `int` | 4 | 1–16 |
| `ARGON2_MAX_CONCORRENTES` | `int` | 4 | 1–32 |
| `EMAIL_MODO` | `Literal["smtp","memoria"]` | `smtp` | `memoria` proibido com `AMBIENTE=producao` |
| `SMTP_HOST` | `str \| None` | `None` | Obrigatório com `smtp`; 1–253 caracteres |
| `SMTP_PORTA` | `int` | 587 | 1–65535 |
| `SMTP_SEGURANCA` | `Literal["starttls","tls","nenhuma"]` | `starttls` | `nenhuma` proibida em `producao` |
| `SMTP_USUARIO` / `SMTP_SENHA` | `str \| None` / `SecretStr \| None` | `None` | Os dois ou nenhum; proibidos com `nenhuma` |
| `SMTP_REMETENTE` | `str \| None` | `None` | Obrigatório com `smtp`; guardado na forma canônica (R9.9). A regra é repetida nas Settings, que não importam `schemas` |
| `SMTP_TIMEOUT_S` | `float` | 10 | `> 0` e `<= 30` (por operação de socket) |

Regras de ambiente (`model_validator(mode="after")`): em `producao`, `ARGON2_TIME_COST >= 3` e `ARGON2_MEMORY_COST_KIB >= 65536`. As mensagens de erro citam o **nome** do campo e a regra, nunca o valor.

`RECUPERACAO_*` saem de `Settings` e viram constantes (R11.1).

`.env.exemplo` (acréscimo exato no Prompt F3 §9.2): placeholder `JWT_SEGREDO=TROQUE_ESTE_VALOR`, com 17 bytes. Ele **falha** de propósito na regra de 32 bytes, então um `.env` copiado sem trocar o valor não sobe, e não é preciso código especial para recusá-lo. Também entra `EMAIL_MODO=memoria` para desenvolvimento sem SMTP, com as variáveis SMTP comentadas e domínios `exemplo.com`.

Dependências, só na Etapa B e depois da aprovação:

- novas: `argon2-cffi`, `PyJWT` e `tzdata`;
- diretas que já estão no lock: `email-validator` (2.3.0) e `anyio` (4.15.1).

O comando e os critérios de parada estão no Prompt F3 §14, passo 2. Nenhuma versão é fixada aqui.

**Passo operacional do usuário depois da integração:** acrescentar `JWT_SEGREDO` (gerado localmente) e `EMAIL_MODO` (e SMTP, se usar `smtp`) ao `.env` real. Sem isso, a API e `alembic upgrade` pela CLI recusam iniciar, porque o `env.py` usa `obter_settings()`.

### 6.3. Suporte: assinaturas e comportamento

- `tempo.Relogio.agora() -> datetime` devolve **sempre** UTC com fuso. `RelogioSistema` usa `datetime.now(UTC)`. `RelogioFixo` (`tests/apoio/relogio.py`) recusa instantes fora de UTC e tem `avancar(timedelta)`.
- `seguranca.ParametrosArgon2(time_cost, memory_cost_kib, parallelism)`, dataclass imutável.
- `seguranca.HasherSenha(parametros, limitador: anyio.CapacityLimiter)`:
  - `async gerar(segredo) -> str`;
  - `async verificar(hash_armazenado, segredo) -> bool`: `False` só para `VerifyMismatchError`; demais erros → `HashArmazenadoInvalido` (sem dados) `from None`;
  - `async preparar_ficticio() -> None`: calcula uma vez o hash de `secrets.token_urlsafe(32)`;
  - `async verificar_ficticio(segredo) -> None`: verifica contra o fictício e descarta o resultado.

  Toda chamada usa `anyio.to_thread.run_sync(..., abandon_on_cancel=False, limiter=limitador)`. O limitador é criado no `lifespan`.
- `seguranca.carimbo(senha_hash) = sha256(senha_hash.encode()).hexdigest()[:16]`.
- `seguranca.ConfiguracaoToken(segredo: SecretStr, validade: timedelta)`, dataclass imutável.
- `seguranca.emitir_token(usuario_id, senha_hash, agora, configuracao: ConfiguracaoToken) -> TokenEmitido(token, expira_em)` (§6.9).
- `seguranca.decodificar_token(token, agora, configuracao: ConfiguracaoToken) -> ClaimsToken(usuario_id, sv)`, que lança `TokenInvalido` (§6.9).
- `seguranca.gerar_codigo() -> str`, `gerar_token_redefinicao() -> str` e `hash_token(token) -> str` (SHA-256 hexadecimal). Os services chamam `seguranca.gerar_codigo()` pelo módulo, para os testes poderem forçar `00012345` com `monkeypatch.setattr(seguranca, "gerar_codigo", ...)`.
- `email.EnviadorEmail` (Protocol): `async enviar(mensagem: MensagemEmail) -> None`, que lança `FalhaEnvioEmail(motivo)`, onde o motivo é o nome da classe da causa.
- `EnviadorEmailSmtp(settings)`:
  - `ssl.create_default_context()`;
  - `starttls` (`SMTP` + `ehlo` + `starttls(context=…)` + `ehlo`), `tls` (`SMTP_SSL(context=…)`) ou `nenhuma`;
  - `login` só com credenciais;
  - `send_message`, dentro de `with`;
  - `timeout=SMTP_TIMEOUT_S`;
  - captura `smtplib.SMTPException`, `OSError` (inclui `ssl.SSLError` e `TimeoutError`), `UnicodeError` e `ValueError`, e relança `FalhaEnvioEmail(type(erro).__name__) from None`;
  - registra `logger.warning("falha no envio de e-mail: motivo=%s codigo_smtp=%s", ...)`, sem destinatário, assunto, corpo ou resposta do servidor.
- `EnviadorEmailMemoria`: `enviadas: collections.deque[MensagemEmail]` com `maxlen=100`, que limita a memória se o modo `memoria` ficar ativo fora dos testes, e `falha_programada: FalhaEnvioEmail | None` (lançada uma vez e limpa).
- `email.mensagem_codigo(nome, email, codigo) -> MensagemEmail`, com o texto exato do Prompt F3 §8.4 (3.4.4).
- Services, com parâmetros explícitos e no máximo 5 cada (ACH-MV-ARQ-036). Nenhum importa `settings` nem outro service:
  - `identidade.registrar(sessao, dados, relogio, hasher)`;
  - `identidade.entrar(sessao, dados, relogio, hasher, configuracao_token)`;
  - `identidade.montar_contexto(sessao, token, agora, configuracao_token)`;
  - `identidade.obter_usuario_atual(sessao, contexto)`;
  - `recuperacao_senha.solicitar_codigo(sessao, dados, relogio, hasher, enviador)`;
  - `recuperacao_senha.verificar_codigo(sessao, dados, relogio, hasher)`;
  - `recuperacao_senha.redefinir_senha(sessao, dados, relogio, hasher)`.
- `tempo.ContextoUsuario(usuario_id: UUID, fuso: ZoneInfo, agora: datetime, hoje: date)`, conforme D-13 (ACH-MV-ARQ-038). Fica em `tempo.py` para que nenhum service precise importar outro (D-02).
- `dependencias.ContextoDep`:
  - `HTTPBearer(auto_error=False)`;
  - `agora = relogio.agora()` capturado primeiro;
  - `identidade.montar_contexto(sessao, token, agora, configuracao_token)`;
  - qualquer falha → `ErroNegocio(NAO_AUTENTICADO, cabecalhos={"WWW-Authenticate": "Bearer"})`, sem log.
- `dependencias.sem_cache(response: Response) -> None` grava `Cache-Control: no-store`. Fica no decorador das rotas E2 e E4 (`dependencies=[Depends(sem_cache)]`), para que os routers continuem com no máximo 5 parâmetros. Vale para a resposta de sucesso; as de erro são montadas pelos handlers.
- `services.autorizacao.obter_do_usuario_ou_404(sessao, modelo, id_recurso, usuario_id, *, incluir_excluidos=False)`:
  - exige a coluna `usuario_id` no modelo (`TypeError` caso contrário);
  - filtra `excluida_em IS NULL` quando a coluna existe e `incluir_excluidos=False`;
  - na ausência, lança `ErroNegocio(RECURSO_NAO_ENCONTRADO)`.
- `main.criar_app`:
  - no `lifespan`, **antes** de `criar_engine`, cria `app.state.hasher` (com `anyio.CapacityLimiter(ARGON2_MAX_CONCORRENTES)` e `await preparar_ficticio()`) e `app.state.enviador_email = criar_enviador(s)`. Assim, uma falha nessa preparação não deixa a engine aberta;
  - inclui os routers com `prefix="/api/v1"`;
  - a importação continua sem I/O (CT-F1-02).

### 6.4. Endpoints

Todos com resposta JSON, cabeçalho `X-Request-ID` e erros no formato de D-08. Instantes em ISO 8601 UTC com `Z` (sonda `05`); datas civis `YYYY-MM-DD`.

| # | Método e caminho | Router → service | Entrada (validação e normalização) | Sucesso | Falhas |
| --- | --- | --- | --- | --- | --- |
| E1 | `POST /api/v1/auth/registro` | `autenticacao.registrar` → `identidade.registrar` | `RegistroEntrada`. `nome_completo`: aparado; ausente ou vazio → `NOME_COMPLETO_OBRIGATORIO`; caractere de controle (categoria `Cc`) → `NOME_COMPLETO_INVALIDO`; > 150 → `TAMANHO_MAXIMO`. `email`: `canonicalizar_email` (R9.9); sem forma canônica → `EMAIL_INVALIDO`. `senha`, `confirmar_senha`: R11.10. `data_nascimento`: validador próprio antes da conversão. Aceita só texto `AAAA-MM-DD`, com dígitos ASCII, que forme uma data existente; qualquer outra entrada → `DATA_INVALIDA`; ausente → `OBRIGATORIO`. Sem `Field(strict=True)`: o FastAPI valida o corpo em modo Python, e o modo estrito recusa toda data em texto (sonda `01` da revisão). `fuso_horario`: `tempo.fuso_valido` → `FUSO_INVALIDO` | 201 `UsuarioResposta` | 422 `VALIDACAO` (campos acima e `DATA_NASCIMENTO_FUTURA`); 409 `EMAIL_JA_CADASTRADO` |
| E2 | `POST /api/v1/auth/login` | `autenticacao.entrar` → `identidade.entrar` | `LoginEntrada`: `email` 1–254, sem validar formato no schema; o service aplica `canonicalizar_email` e trata a ausência de forma canônica como e-mail inexistente; `senha` 1–128 | 200 `TokenResposta`, `Cache-Control: no-store` (via `sem_cache`) | 401 `CREDENCIAIS_INVALIDAS` (mesma resposta para e-mail inexistente e senha errada); 422 de forma |
| E3 | `POST /api/v1/auth/recuperacao/solicitar` | `autenticacao.solicitar_codigo` → `recuperacao_senha.solicitar_codigo` | `SolicitarCodigoEntrada`: `email` com a validação de E1 | 200 `SolicitacaoCodigoResposta` | 422 `EMAIL_INVALIDO`; 404 `EMAIL_NAO_ENCONTRADO` (se DEC-MV-10 = A); 429 `REENVIO_MUITO_FREQUENTE` + `Retry-After`; 503 `FALHA_ENVIO_EMAIL`; 503 `CONFLITO_CONCORRENCIA` (`lock_timeout`) |
| E4 | `POST /api/v1/auth/recuperacao/verificar` | `autenticacao.verificar_codigo` → `recuperacao_senha.verificar_codigo` (§5.3) | `VerificarCodigoEntrada`: `email` como E1; `codigo` `^[0-9]{8}$` (ausente ou fora do formato → `CODIGO_FORMATO`) | 200 `VerificacaoCodigoResposta`, `Cache-Control: no-store` (via `sem_cache`) | 400 `CODIGO_INVALIDO` / `CODIGO_EXPIRADO`; 409 `CODIGO_JA_VERIFICADO`; 429 `TENTATIVAS_ESGOTADAS` + `Retry-After`; 422 de forma |
| E5 | `POST /api/v1/auth/recuperacao/redefinir` | `autenticacao.redefinir_senha` → `recuperacao_senha.redefinir_senha` | `RedefinirSenhaEntrada`: `token_redefinicao` 1–128; `nova_senha` e `confirmar_senha` conforme R11.10 | 200 `MensagemResposta` (“Redefinição de senha concluída com sucesso”) | 400 `TOKEN_REDEFINICAO_INVALIDO`; 422 (`SENHA_FRACA`, `TAMANHO_MAXIMO`, `SENHAS_DIFERENTES`) |
| E6 | `GET /api/v1/usuarios/me` | `usuarios.obter_usuario_atual` → `identidade.obter_usuario_atual` | `Authorization: Bearer` | 200 `UsuarioResposta` | 401 `NAO_AUTENTICADO` + `WWW-Authenticate: Bearer` |

Consultas, escritas e fronteira transacional:

| # | Leitura | Escrita | Commit | Efeito externo | Autorização |
| --- | --- | --- | --- | --- | --- |
| E1 | `usuario` por e-mail (pré-checagem) | `INSERT usuario` (+ `flush`; `IntegrityError` em `uq_usuario_email` → 409) | Router, depois do service | — | Pública, deliberadamente |
| E2 | `usuario` por e-mail | — | Não há (só leitura) | — | Pública |
| E3 | `usuario` por e-mail; `recuperacao_senha` `FOR UPDATE` | `INSERT … ON CONFLICT DO NOTHING` ou `UPDATE` | Router, depois do envio | E-mail **antes** do commit | Pública |
| E4 | `recuperacao_senha` com junção em `usuario`, `FOR UPDATE OF recuperacao_senha` | `tentativas + 1` ou `verificado_em`/token | Router **sempre** faz commit e então lança o erro, se houver (§5.3) | — | Pública |
| E5 | `recuperacao_senha` por `token_redefinicao_hash` `FOR UPDATE`; `usuario` por id | `usuario.senha_hash`; `utilizado_em` | Router | — | Pública (o token é a credencial) |
| E6 | `usuario` por `sub` (dependência); mesmo objeto pelo mapa de identidade | — | Não há | — | `ContextoDep` |

Critérios de aceite por endpoint: §7 (CTs) e Prompt F3 §12.

### 6.5. Campos permitidos nas respostas

| Endpoint | Campos exatos | Valores sensíveis permitidos |
| --- | --- | --- |
| E1, E6 (`UsuarioResposta`) | `id`, `nome_completo`, `email`, `data_nascimento`, `fuso_horario` | E-mail e nome do **próprio** usuário |
| E2 (`TokenResposta`) | `access_token`, `token_type` (`"bearer"`), `expira_em` | O JWT, só em `access_token` |
| E3 (`SolicitacaoCodigoResposta`) | `expira_em`, `reenvio_permitido_em` | Nenhum (nem código, nem e-mail) |
| E4 (`VerificacaoCodigoResposta`) | `token_redefinicao`, `expira_em` | O token, só em `token_redefinicao` |
| E5 (`MensagemResposta`) | `mensagem` | Nenhum |
| Erros | `codigo`, `mensagem`, `campos[].{campo,codigo,mensagem}`, `detalhes` (`null` na F3), `id_requisicao` | **Nenhum**. Sem eco de entrada |

Proibido em qualquer resposta: `senha_hash`, `codigo_hash`, `token_redefinicao_hash` e o código de 8 dígitos. Proibido em logs, inclusive na saída formatada com exceções: senha, nova senha, código, JWT, token de redefinição, hashes, e-mail e nome.

### 6.6. Erros e mensagens

Códigos de topo da F3, já previstos em arq §4.4 e a acrescentar a `CodigoErro`:

- `NAO_AUTENTICADO` 401
- `CREDENCIAIS_INVALIDAS` 401
- `EMAIL_JA_CADASTRADO` 409
- `EMAIL_NAO_ENCONTRADO` 404
- `REENVIO_MUITO_FREQUENTE` 429
- `FALHA_ENVIO_EMAIL` 503
- `CODIGO_INVALIDO` 400
- `CODIGO_EXPIRADO` 400
- `TENTATIVAS_ESGOTADAS` 429
- `CODIGO_JA_VERIFICADO` 409
- `TOKEN_REDEFINICAO_INVALIDO` 400

As mensagens são as da tabela de arq §4.4. A de `CODIGO_INVALIDO` é a literal de 3.4.8.

Códigos de campo:

- `SENHA_FRACA` (3.4.10 literal);
- `SENHAS_DIFERENTES` (3.4.14 literal);
- `EMAIL_INVALIDO`, `CODIGO_FORMATO`, `DATA_NASCIMENTO_FUTURA` e `FUSO_INVALIDO` (arq §4.5);
- **novos** (acrescentados à arq §4.5 na liberação): `NOME_COMPLETO_OBRIGATORIO` (“Informe o nome completo”) e `NOME_COMPLETO_INVALIDO` (“O nome não pode conter caracteres de controle”);
- os genéricos de arq §4.4: `OBRIGATORIO`, `TAMANHO_MAXIMO`, `TAMANHO_MINIMO`, `DATA_INVALIDA` e `FORMATO_INVALIDO`.

Literais preservados: 3.4.8, 3.4.10, 3.4.14 e 3.4.15. A mensagem 3.4.2 depende da DEC-MV-10.

### 6.7. Algoritmos de recuperação

Pseudocódigo normativo no Prompt F3 §8.6 a §8.8. Resumo:

- **Solicitar:**
  1. Buscar o usuário pelo e-mail na forma canônica (R9.9). Se não existir → 404.
  2. `SELECT … FOR UPDATE` da linha.
  3. Se a linha existe: `agora`, regra de intervalo (R11.4), gerar o código e o hash, `UPDATE` (R11.5) e `flush`.
  4. Se não existe: `agora`, gerar o código e o hash, `INSERT … ON CONFLICT (usuario_id) DO NOTHING RETURNING id`. Sem retorno: `SELECT … FOR UPDATE`, recapturar `agora`, regra de intervalo → 429 se ainda dentro do intervalo; senão, tratar como reenvio.
  5. Enviar. Em caso de `FalhaEnvioEmail` → `ErroNegocio(FALHA_ENVIO_EMAIL) from None`.
  6. Devolver `expira_em` e `reenvio_permitido_em`. O router faz o commit.
- **Verificar:** R11.6, com a avaliação dos passos 1–4 numa função auxiliar `_motivo_recusa(rec, agora) -> CodigoErro | None` (PLR0911). O service devolve `ResultadoVerificacao(erro, token, expira_em, retry_after_s)`. O router faz o commit e lança o erro, com `Retry-After` quando houver.
- **Redefinir:**
  1. `SELECT … FOR UPDATE` por `hash_token(token)`.
  2. `agora`.
  3. Validar: linha encontrada, `verificado_em` preenchido, `utilizado_em` nulo e `agora < expira_em`; senão → 400.
  4. Gravar o hash da nova senha e `utilizado_em = agora`; `flush`.
  5. Router faz o commit.

### 6.8. Concorrência e efeitos

Proteção final: `uq_usuario_email`, `uq_recuperacao_senha_usuario_id` e `uq_recuperacao_senha_token_redefinicao_hash`. Isolamento `READ COMMITTED`.

| # | Corrida | Precondição | Bloqueio | Leitura | Escrita | Commit/rollback | Resultado observável | Garantia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Dois registros com o mesmo e-mail | Sem conta | O segundo `INSERT` espera o índice único da transação do primeiro | Pré-checagem não vê nada | Os dois tentam `INSERT` | Primeiro faz commit; o segundo recebe `23505` → 409 e rollback | Um 201 e um 409; uma linha | Unicidade no banco. Se o primeiro desfizer, o segundo grava |
| C2 | Duas **primeiras** solicitações | Sem linha | `FOR UPDATE` não trava nada. O segundo `INSERT … ON CONFLICT` espera o primeiro (até 5 s) | — | Primeiro insere e envia | Primeiro faz commit. Segundo: `DO NOTHING` → `FOR UPDATE` → 429. Se o primeiro passar de 5 s, o segundo recebe 503 `CONFLITO_CONCORRENCIA` | Um 200 e um 429 (ou 503); um e-mail; uma linha | A trava de uma linha inexistente **não** protege; a proteção é o índice único com `ON CONFLICT` |
| C3 | Dois reenvios | Linha emitida há ≥ 60 s | `FOR UPDATE` serializa | O segundo lê o estado confirmado do primeiro | Primeiro substitui | Segundo → 429 | Um código novo válido; um 429 | Uma emissão por intervalo |
| C4 | Duas verificações corretas | Código válido | `FOR UPDATE` | Segundo vê `verificado_em` | Primeiro grava o token | Segundo → 409 | Um 200 e um 409; um token | Um só token por emissão |
| C5 | Cinco inválidas concorrentes | `tentativas = 0` | `FOR UPDATE` | Cada uma vê o valor confirmado anterior | `+1` cada | Cada uma faz commit e devolve 400 | `tentativas == 5` exato | Contagem exata |
| C6 | Correta × limite | `tentativas = 4` | `FOR UPDATE` | — | — | Inválida antes: 5 e 400; a correta depois recebe 429. Correta antes: 200; a inválida depois recebe 409 | Igual a uma ordem serial | Linearizável |
| C7 | Reenvio × verificação | Código antigo | `FOR UPDATE` | — | — | Reenvio antes: o código antigo é inválido e **conta** como tentativa da nova emissão (400). Verificação antes: token emitido, que o reenvio seguinte limpa | Ordem serial | O código antigo nunca vale depois do reenvio confirmado |
| C8 | Duas redefinições com o mesmo token | Token válido | `FOR UPDATE` pelo hash | Segundo revalida a linha após o commit do primeiro (`EvalPlanQual`) e vê `utilizado_em` | Primeiro troca a senha | Segundo → 400 | Um 200 e um 400; uma troca | Consumo único |
| C9 | Reenvio × redefinição | Token válido | Mesma linha | — | — | Redefinição antes: troca feita, e o reenvio segue a regra de intervalo. Reenvio antes: o `WHERE` da redefinição é reavaliado sobre a nova versão (hash nulo) → nenhuma linha → 400 | Ordem serial | O token não sobrevive a um reenvio confirmado |
| C10 | Login ou autenticação × redefinição | Sessão válida | Nenhum (login e `ContextoDep` só leem) | Antes do commit da redefinição: hash antigo | — | — | Requisições em andamento terminam normalmente. Um login com a senha antiga **antes** do commit emite um token com `sv` antigo | A partir do commit, todo token com `sv` antigo recebe 401 no próximo uso. Não há cancelamento retroativo |
| C11 | Falha de envio | — | Linha travada | — | Alterações desfeitas | Rollback | 503 `FALHA_ENVIO_EMAIL`; banco inalterado | Repetição imediata permitida (§4.4, situações 1–3) |
| C12 | Commit falha depois do envio | — | — | — | — | Rollback | 5xx; e-mail entregue com código sem valor | §4.4, situação 4 |

### 6.9. Tempo e JWT

- **Emissão:**
  - `base = agora.replace(microsecond=0)`;
  - `iat = int(base.timestamp())`;
  - `exp = iat + validade_s`;
  - `expira_em = datetime.fromtimestamp(exp, UTC)`;
  - `jwt.encode({"sub": str(usuario_id), "iat": iat, "exp": exp, "typ": "access", "sv": carimbo}, segredo, algorithm="HS256")`.
- **Decodificação:** `jwt.decode(token, segredo, algorithms=["HS256"], options={"verify_signature": True, "verify_exp": False, "verify_iat": False, "verify_nbf": False, "verify_aud": False, "verify_iss": False, "require": ["sub", "iat", "exp", "typ", "sv"]})`. Qualquer `jwt.InvalidTokenError` → `TokenInvalido`.
- **Validação manual**, todas obrigatórias:
  - o conjunto de claims é exatamente `{sub, iat, exp, typ, sv}`;
  - `typ == "access"`;
  - `sub` é `str` e `str(UUID(sub)) == sub` (canônico);
  - `iat` e `exp` são `int` e não `bool` (`type(x) is int`);
  - `0 < exp - iat <= validade_s`;
  - `iat <= agora.timestamp() < exp`;
  - `sv` casa `^[0-9a-f]{16}$`.

  Só então o usuário é carregado e comparado com `hmac.compare_digest(sv, carimbo(usuario.senha_hash))`.
- **Limites:** o token vale de `iat` até um instante antes de `exp`, inclusive no limite inferior e exclusive no superior, sem tolerância (leeway 0).
- **Token malformado ou grande demais:** cabeçalho ausente, esquema diferente de `Bearer` ou token com mais de 4096 caracteres → 401, sem decodificar.
- **Instante do contexto autenticado:** capturado na dependência antes de decodificar; `hoje = hoje_no_fuso(agora, ZoneInfo(usuario.fuso_horario))`.

---

## 7. Testes

### 7.1. Política

PostgreSQL real descartável (Testcontainers, `postgres:15-alpine`), construído pela migração da F2 (`banco_migrado`). Também:

- concorrência com requisições independentes e “portão de largada” verificável com `aguardar_espera_por_trava`. O helper exige o número **exato** de requisições paradas na trava esperada, filtrando pelo texto da consulta, e não usa `sleep` (sonda `03` da revisão);
- verificação final por outra conexão;
- `RelogioFixo`;
- Argon2 real com parâmetros reduzidos (1 / 8 KiB / 1), mais **um** teste com os parâmetros de produção;
- `EnviadorEmailMemoria` e `smtplib` simulado, sem e-mail real;
- `SettingsTeste` hermética, sem `.env`;
- captura do logger real **e** da saída formatada, com exceções;
- nenhum teste de tempo de resposta.

Nenhum teste está aprovado: todos estão PLANEJADOS.

### 7.2. Mapa dos CTs

Os 23 CTs existentes mantêm os IDs. Na revisão M15, os casos de concorrência passaram a usar a espera exata por trava (sonda `03` da revisão), e o CT-F3-11 ganhou passos ordenados. Os novos usam IDs livres (`CT-F3-22`, 23, 24, 26, 27, 28 e 29), cuja ausência no catálogo e nos documentos foi conferida. Arquivos em `tests/identidade/`. `c` indica concorrência.

| CT | Arquivo | Cenário, preparação e ação | Asserções e evidência |
| --- | --- | --- | --- |
| CT-F3-01 | `test_registro.py` | Registro válido (e-mail com maiúsculas e espaços) | 201; resposta com os 5 campos exatos; `email` na forma canônica (R9.9); no banco, por outra conexão, `senha_hash` começa com `$argon2id$` e não há senha em claro |
| CT-F3-02 | `test_registro.py` | Parametrizado: senha 7 caracteres, vazia e ausente (`SENHA_FRACA`, 3.4.10 literal); 129 caracteres (`TAMANHO_MAXIMO`); confirmação diferente (`SENHAS_DIFERENTES`, 3.4.14); e-mail inválido, com parte local não ASCII (`josé@exemplo.com`) e `@localhost`; nascimento futuro **no fuso informado** (`RelogioFixo` 2026-10-14T02:30Z, `America/Sao_Paulo`: 2026-10-14 recusado e 2026-10-13 aceito); fuso `localtime`, `../etc/passwd` e inexistente; nome vazio e com `\r\n`; `data_nascimento` `1990-1-1`, `19900101`, `1990-01-01T00:00:00`, `0`, `2001-02-29` e com dígitos não ASCII (`DATA_INVALIDA`) | 422 com `campos[].codigo` exato; nenhum valor ecoado; nada gravado |
| CT-F3-03 | `test_registro.py` | E-mail duplicado com maiúsculas e espaços. Parametrizado: variantes de um endereço com domínio internacionalizado (Unicode composto, decomposto e punycode) depois do cadastro da primeira | 409 `EMAIL_JA_CADASTRADO`; uma linha |
| CT-F3-04 | `test_login.py` | Login válido, também com o e-mail digitado em outra variante (maiúsculas ou punycode) | Claims exatas `{sub, iat, exp, typ, sv}`; `exp - iat == 86400`; `expira_em` = `exp` em ISO `Z`; `Cache-Control: no-store` |
| CT-F3-05 **c** | `test_registro.py` | Portão: uma conexão bloqueadora insere, sem confirmar, um usuário com o e-mail; dois registros simultâneos; `aguardar_espera_por_trava(monitor, 2, "%INSERT INTO usuario%")`; a bloqueadora desfaz | Um 201 e um 409 `EMAIL_JA_CADASTRADO`; uma linha por outra conexão |
| CT-F3-06 | `test_login.py` | E-mail inexistente; e-mail malformado (sem forma canônica); senha errada | Corpo e status idênticos (401 `CREDENCIAIS_INVALIDAS`), salvo `id_requisicao`; o hasher fictício foi chamado (espião) nos dois primeiros casos |
| CT-F3-07 | `test_login.py` | Token ausente, esquema `Basic`, malformado, mais de 4096 caracteres, assinatura errada, `alg: none`, `typ` errado, `sub` inexistente, `sub` não canônico, claim extra, `iat` `bool`, `iat` no futuro do `RelogioFixo`, expirado no `RelogioFixo` | 401 `NAO_AUTENTICADO` com `WWW-Authenticate: Bearer` em todos |
| CT-F3-08 | `test_usuario_atual.py` | `GET /usuarios/me` com token válido | 200 com os 5 campos exatos do próprio usuário |
| CT-F3-09 | `test_recuperacao.py` | Solicitar com o gerador forçado a `00012345` | 200; uma mensagem no `EnviadorEmailMemoria` com assunto e corpo exatos (3.4.4) e o código `00012345`; `destinatario` igual à forma canônica gravada; banco com `codigo_hash` Argon2id ≠ código; `expira_em = agora + 10 min` |
| CT-F3-10 | `test_recuperacao.py` | E-mail não cadastrado | 404 `EMAIL_NAO_ENCONTRADO` com a mensagem 3.4.2 (se DEC-MV-10 = A); nenhuma mensagem enviada; nenhuma linha |
| CT-F3-11 | `test_recuperacao.py` | `test_reenvio`, com o gerador forçado a `00012345` e depois a `87654321`: solicitar; duas verificações inválidas; reenvio em +59 s; reenvio em +60 s; verificar o código antigo; verificar o novo. `test_reenvio_anula_token`: verificar certo, reenviar em +60 s e redefinir com o token anterior | Após as inválidas, `tentativas == 2`. Em +59 s, 429 com `Retry-After: 1` e linha inalterada. Em +60 s, 200 e, **logo em seguida**, por outra conexão: `tentativas == 0`, verificação, token e uso nulos, `codigo_hash` diferente e `expira_em` novo. A mensagem nova traz `87654321`. O código antigo dá 400 `CODIGO_INVALIDO` e deixa `tentativas == 1`, porque conta para a emissão nova. O código novo dá 200. No segundo teste, logo após o reenvio, verificação e token estão nulos, e o token anterior dá 400 `TOKEN_REDEFINICAO_INVALIDO` |
| CT-F3-12 | `test_recuperacao.py` | Correto → token; incorreto → 400 (3.4.8) e `tentativas + 1` por outra conexão; 5 inválidas → a 5ª dá 400 e a 6ª, mesmo correta, dá 429 com `Retry-After`; expirado → 400 `CODIGO_EXPIRADO`; dígitos não ASCII → 422 `CODIGO_FORMATO` | Status, códigos e banco |
| CT-F3-13 | `test_recuperacao.py` | Verificar de novo após sucesso | 409; o hash do token no banco não muda |
| CT-F3-14 **c** | `test_recuperacao_concorrencia.py` | Portão (`FOR UPDATE` bloqueador na linha); duas verificações corretas; `aguardar_espera_por_trava(monitor, 2, "%FROM recuperacao_senha%FOR UPDATE%")` | Um 200 e um 409 `CODIGO_JA_VERIFICADO`; um token |
| CT-F3-15 **c** | idem | Gerador forçado a `00012345`; portão; cinco verificações com códigos inválidos distintos; `aguardar_espera_por_trava(monitor, 5, "%FROM recuperacao_senha%FOR UPDATE%")` **antes** de liberar | A espera exata de 5 prova as cinco requisições paradas ao mesmo tempo na trava da linha. Depois de liberar: cinco respostas 400 `CODIGO_INVALIDO`; `tentativas == 5` por outra conexão; uma sexta verificação, com `00012345`, dá 429 `TENTATIVAS_ESGOTADAS` com `Retry-After` |
| CT-F3-16 | `test_recuperacao.py` | Redefinir | 200 com a mensagem 3.4.15; a nova senha entra; a antiga não; `utilizado_em` preenchido; o JWT anterior dá 401 |
| CT-F3-17 **c** | `test_recuperacao_concorrencia.py` | Duas redefinições com o mesmo token; portão com 2 em espera | Um 200 e um 400 `TOKEN_REDEFINICAO_INVALIDO`; uma troca |
| CT-F3-18 | `test_recuperacao.py` | Token expirado (`RelogioFixo` em `expira_em`), usado e inexistente; senhas diferentes; nova senha curta | 400 / 400 / 400 / 422 `SENHAS_DIFERENTES` / 422 `SENHA_FRACA` |
| CT-F3-19 **c** | `test_recuperacao_concorrencia.py` | Gerador `00012345` e depois `87654321`; emissão; +60 s; portão de ordem: a primeira tarefa, espera de 1; a segunda, espera de 2; libera. Parametrizado pela ordem | Verificar antes: 200 e reenvio 200; ao final, token e verificação nulos e `tentativas == 0`. Reenviar antes: 200 e verificação com `00012345` → 400 `CODIGO_INVALIDO`, `tentativas == 1` |
| CT-F3-20 | `test_recuperacao.py` | `falha_programada` no enviador, na primeira emissão e num reenvio | 503 `FALHA_ENVIO_EMAIL`; linha inexistente ou inalterada; repetição imediata permitida |
| CT-F3-21 | `test_usuario_atual.py` | `RelogioFixo` 2026-10-14T02:30Z; usuário `America/Sao_Paulo`; rota de teste que expõe `ContextoUsuario` | `hoje == 2026-10-13`; `agora` igual ao relógio |
| CT-F3-22 (novo) | `test_configuracao_identidade.py` | Settings da F3: segredo com 31 e 32 bytes (inclusive multibyte); placeholder do `.env.exemplo`; faixas; `memoria` e `nenhuma` em `producao`; credenciais sem TLS; SMTP ausente em `smtp`; piso do Argon2 em `producao` | `ValidationError` sem o valor do segredo na mensagem; valores válidos aceitos |
| CT-F3-23 **c** (novo) | `test_recuperacao_concorrencia.py` | Duas **primeiras** solicitações: a bloqueadora insere, sem confirmar, uma linha do usuário; `aguardar_espera_por_trava(monitor, 2, "%INSERT INTO recuperacao_senha%")`; a bloqueadora desfaz | Um 200 e um 429; uma linha; uma mensagem enviada |
| CT-F3-24 (novo) | `test_recuperacao.py` e `test_login.py` | Limites exatos: código em `expira_em − 1 s` (válido) e em `expira_em` (expirado); reenvio em +59 s e +60 s; JWT em `exp − 1 s` (válido), em `exp` (401) e em `iat − 1 s` (401) | Status e códigos exatos |
| CT-F3-25 (texto refinado) | `test_vazamento.py` | Todos os fluxos de E1–E6, inclusive falhas, com valores sentinela, mais uma exceção inesperada sintética | Cada resposta tem **exatamente** os campos da §6.5; os sentinelas só aparecem nos campos permitidos; nenhum aparece em respostas de erro, em `caplog.records` nem na saída formatada do handler do logger real (com exceções) |
| CT-F3-26 (novo) | `test_recuperacao.py` | Commit falha depois do envio (sessão de teste cujo `commit` lança `DBAPIError` sintético via `dependency_overrides[obter_sessao]`) | 5xx; mensagem enviada; banco inalterado por outra conexão; nova solicitação permitida (sem emissão confirmada) |
| CT-F3-27 **c** (novo) | `test_recuperacao_concorrencia.py` | Token T obtido; +60 s; portão de ordem (como no CT-F3-19). Parametrizado pela ordem | Redefinir antes: redefinição 200 e reenvio 200. Reenviar antes: reenvio 200 e redefinição com T → 400 `TOKEN_REDEFINICAO_INVALIDO`; a senha antiga continua entrando |
| CT-F3-28 (novo) | `test_email.py` | `EnviadorEmailSmtp` com `smtplib` simulado (`monkeypatch`): `starttls` com contexto que verifica certificado; `tls` com `SMTP_SSL`; `login` só com credenciais; `timeout`; fechamento; `SMTPRecipientsRefused` com o endereço sentinela | `FalhaEnvioEmail` com motivo = nome da classe; nenhum endereço na exceção nem no log; conexão fechada em todos os caminhos |
| CT-F3-29 (novo) | `test_seguranca.py` | `HasherSenha` com parâmetros de produção (um hash) e de teste; limitador com 2 vagas e 5 chamadas sincronizadas | Prefixo `$argon2id$v=19$m=65536,t=3,p=4$`; verificação certa e errada; no máximo 2 execuções simultâneas observadas; login não regrava o hash (`senha_hash` inalterado por outra conexão) |
| CT-F3-30 | `test_usuario_atual.py` | Rota de teste `GET /teste/importancias/{id}` com `obter_do_usuario_ou_404` | UUID de outro usuário → 404; UUID malformado → 422; o próprio → 200 |

### 7.3. Seleção prescrita

1. Testes do comportamento alterado e `tests/identidade/`.
2. Regressões com risco concreto:
   - `tests/infra/test_configuracao.py`: Settings, `settings_teste` e importação sem efeitos (CT-F1-02);
   - `tests/infra/test_erros.py`, `tests/infra/test_saude.py` e `tests/infra/test_sessao_transacao.py`: sobem o app pelo `lifespan` alterado com `settings_teste`.
3. **Não** entram `tests/infra/test_alembic_ambiente.py` (não usa o app nem `obter_settings` com URL injetada) nem `tests/esquema` (modelos e migração inalterados).

A suíte completa não é proposta.

---

## 8. Alterações normativas (aplicadas em 2026-10-13, M16)

Aplicação só depois da aprovação correspondente. Cada item indica o local real. Todos os itens abaixo foram aprovados e aplicados na M16; o registro e os ajustes de consistência estão na §14.

**`CLAUDE.md`**

- **CM-1** (opcional, depois da DEC-MV-11): tabela 2, parágrafo “Proposta operacional: validade total de dez minutos e até cinco tentativas por emissão, com limitação adicional de reenvios na aplicação.” → “Parâmetros aprovados (DEC-MV-11): validade total de dez minutos, até cinco tentativas inválidas por emissão e intervalo mínimo de 60 segundos entre emissões.” Nenhuma outra linha muda. As linhas truncadas 3, 10 e 12 não são tocadas.
- **CM-2** (revisão M15; obrigatório se a R9.9 for aprovada): tabela 1 (`usuario`), parágrafo “Regras”, trecho “adotando nesta proposta remoção de espaços externos e conversão para minúsculas” → “adotando a forma canônica da DEC-MV-09 (R9.9): remoção de espaços externos, conversão para minúsculas, validação sem SMTPUTF8 e domínio internacionalizado em IDNA (ASCII)”. Nenhuma outra linha muda.
  - Efeito: para endereços ASCII, a forma canônica coincide com aparar e passar para minúsculas (sonda `01b` da revisão, 6 casos aceitos); a diferença só aparece em domínios internacionalizados.
  - Alternativa sem CM-2: aceitar só endereços ASCII, recusando `fulano@exâmple.com` com `EMAIL_INVALIDO` e exigindo a forma `xn--`. A regra atual do `CLAUDE.md` bastaria, mas o usuário com domínio internacionalizado teria de digitar o punycode.
  - Variante: gravar a forma Unicode normalizada (`.normalized`) e derivar a ASCII só no envio. A resposta mostraria o domínio legível, mas a busca precisaria normalizar a entrada do mesmo modo, e o SMTP, converter.

**ADR-0001**

- **AD-1** (D-07): “Senhas e códigos com Argon2id (`argon2-cffi`), executados em thread (`asyncio.to_thread`).” → “… executados em thread por `anyio.to_thread.run_sync`, com limitador dedicado (`ARGON2_MAX_CONCORRENTES`).” “Login com verificação fictícia quando o e-mail não existe, para equalizar o tempo de resposta.” → “… para aproximar o custo do caminho com e-mail existente (não é tempo constante).” Acrescentar: “Validação temporal do token feita pela aplicação com o `Relogio` (arquitetura §8.2).”
- **AD-2** (D-15): substituir os dois subitens de “O envio ocorre dentro da transação” pela tabela de consequências 1–6 deste dossiê (§4.4) e pelo contrato de `SMTP_SEGURANCA`.
- **AD-3** (tabela §3): D-05 “PROPOSTO” → “PROPOSTO; travas de linha da recuperação aceitas para a F3 (DEC-MV-14, escopo limitado)”. Só se a aprovação parcial da §4.6 for concedida.

**Arquitetura**

- **AR-1** (§3.1, linhas 232–239):
  - `JWT_SEGREDO`: “≥ 32 caracteres” → “≥ 32 bytes (UTF-8)”;
  - `JWT_VALIDADE_MINUTOS`: “5–10080” → “5–1440”;
  - Argon2 com faixas e piso em produção;
  - nova linha `ARGON2_MAX_CONCORRENTES`;
  - remover as linhas `RECUPERACAO_*` (constantes de DEC-MV-11);
  - `SMTP_STARTTLS` → `SMTP_SEGURANCA`;
  - `SMTP_TIMEOUT_S` “10” → “10, > 0 e ≤ 30 (por operação)”.
- **AR-2** (§4.2, linhas 344–350):
  - passo 1 com as opções da §6.9 deste dossiê e a validação manual;
  - passo 3 precedido da verificação do formato de `sv`;
  - passo 4 com `ContextoUsuario(usuario_id, fuso, agora, hoje)`, sem `nome_completo`.
- **AR-3** (§7, linha 664): regra de fuso de `tempo.fuso_valido` (exclusões `localtime`, `posixrules`, `Factory`, `posix/`, `right/`).
- **AR-4** (§8.2): pseudocódigo com parâmetros explícitos (no máximo 5 por função) e emissão por segundos inteiros. A linha 748 passa a ter as opções e a validação manual da §6.9. A linha 747 passa à forma canônica `canonicalizar_email` (R9.9).
- **AR-5** (§8.2 e §8.3): `asyncio.to_thread` → `HasherSenha` e `EnviadorEmail` assíncronos; instante depois da trava (R11.2); R11.6 e R11.7 no texto das regras de §8.3.2; `Retry-After` em `TENTATIVAS_ESGOTADAS`.
- **AR-6** (§9.1, schemas):
  - `email` na forma canônica `canonicalizar_email` (R9.9); no login, sem validar formato no schema;
  - `data_nascimento` `AAAA-MM-DD` por validador próprio, sem modo estrito (§6.4);
  - `codigo` `^[0-9]{8}$`;
  - `nome_completo` sem caracteres de controle;
  - senha conforme R11.10;
  - `Cache-Control: no-store` em E2 e E4, pela dependência `sem_cache` no decorador.
- **AR-7** (§11, linha “Vazamento de segredos e PII”): “Respostas sem hash, código ou token” → “Respostas só com os campos permitidos por endpoint (lista no dossiê da F3, §6.5); tokens só nos campos próprios; erros sem eco de entrada.” Linha “DoS por hash”: “Pool de threads padrão do anyio” → “Limitador dedicado de hashes”.
- **AR-8** (revisto na M15; §2.2, diagrama): acrescentar ao diagrama as arestas que a F3 usa e que ele não mostra:
  - `main → settings`, `main → seguranca`, `main → email`;
  - `dependencias → settings`, `dependencias → email`, `dependencias → erros`;
  - `routers → database`, `routers → erros`;
  - `email → settings`;
  - `schemas → tempo`.

  Também entram as arestas que já existem desde a F1 (`database → settings` e `erros → schemas`). Nenhuma aresta `services → services`. A matriz de services, D-02 e o conflito ACH-MV-ARQ-021 não mudam. As regras explícitas da §2.2 só restringem `models`, `services` e `alembic/env.py`, por isso a F3 é compatível mesmo sem o AR-8. Ele é recomendado para que o diagrama não fique incompleto.
- **AR-9** (§6.6): nova linha para a primeira emissão concorrente (C2) e referência às linhas C1–C12.
- **AR-10** (revisão M15; §11, linha “Enumeração de contas”): “3.4.2 mantido (DEC-MV-10). O registro já revela. Mitigado por intervalo e tentativas” → “3.4.2 mantido (DEC-MV-10, opção A). Risco aceito: a recuperação revela, pela mensagem e pelo tempo de resposta, se o e-mail tem conta. Intervalo e tentativas protegem o código, não a divulgação. Uma limitação de requisições (DEC-MV-21) só reduziria o volume de consultas”. A coluna de testes passa a “CT-F3-10”. Só se a opção A for aprovada.

**Plano de fases e plano de validação**

- **PF-1** (ficha F3):
  - item 3: dependências conforme R9.8;
  - item 8: acrescentar `tests/conftest.py`, `tests/infra/test_configuracao.py`, `tests/apoio/relogio.py`, `tests/apoio/identidade.py` e `services/__init__.py`;
  - item 9: CT-F3-22 a 24 e 26 a 29;
  - item 10: regressões da §7.3 deste dossiê, com `--frozen --no-sync`.
- **PV-1** (catálogo F3): texto refinado de CT-F3-01 a 07, 09, 11, 12, 14, 15, 17, 19, 21 e 25 e as linhas novas da §7.2 deste dossiê.

**Matriz**

- **MZ-1**: 3.2.1 “`^\d{8}$`” → “`^[0-9]{8}$`”.

---

## 9. Gates da F3 e o que falta

| Item | Estado |
| --- | --- |
| F2 — G5 | `APROVADO_COM_P3` (histórico preservado) |
| F2 — G6 | **CUMPRIDO** (`91be324`, §1) |
| Baseline técnico da F3 | `91be324c88c5a3f99a49b1b1700963e32ef257e9` |
| DEC-MV-09 a 13 | **APROVADAS** em 2026-10-13 (M16) |
| DEC-MV-14 (escopo limitado F3) | **APROVADA** em 2026-10-13 (M16), só nas travas de linha da recuperação |
| G1 — Arquitetura da F3 | **CUMPRIDO** (2026-10-13): decisões aprovadas e diffs da §8 aplicados |
| Dossiê da F3 | **APROVADO** (M16) |
| G2 — Prompt Master F3 | **CUMPRIDO**: `PRONTO_PARA_ETAPA_A` (2026-10-13) |
| Implementação F3 | NÃO AUTORIZADA: depende do relatório da Etapa A e do “pode implementar” |

Condições de liberação, todas cumpridas em 2026-10-13 (M16):

1. Aprovação das decisões da §10, com ou sem ajustes.
2. Autorização para aplicar os diffs da §8 correspondentes, inclusive o CM-2 (`CLAUDE.md`), se a R9.9 for aprovada, e o AR-10, se a opção A for aprovada.
3. O Opus aplica os diffs, ajusta o Prompt F3 às escolhas efetivas (por exemplo, a opção da DEC-MV-10), confere IDs e referências e entrega o prompt com o SHA-256.

A Etapa B depende ainda do relatório da Etapa A e do “pode implementar”.

---

## 10. Textos sugeridos de aprovação

> Textos submetidos ao usuário na M15. A aprovação efetiva é a da M16, registrada no `indice.md` §4, e prevalece sobre estes rascunhos.

- **DEC-MV-09:** “Aprovo a DEC-MV-09 conforme o dossiê da F3 §4.1 (R9.1 a R9.9): JWT HS256 com validade padrão de 24 h (configurável entre 5 e 1440 minutos), claims `sub`, `iat`, `exp`, `typ` e `sv`, validação temporal pela aplicação com o relógio, segredo de pelo menos 32 bytes, Argon2id com `argon2-cffi` (3, 64 MiB, 4) e limitador de 4 hashes simultâneos, sem rehash no login, sem refresh e com logout só no cliente; `fuso_horario` obrigatório e validado conforme §6.3; e-mail na forma canônica ASCII da R9.9 em cadastro, login, recuperação e envio, com o login respondendo 401 para e-mail sem forma canônica; dependências `argon2-cffi`, `PyJWT` e `tzdata` e declaração direta de `email-validator` e `anyio`. Aceito que um token obtido por terceiro valha até expirar, salvo troca de senha ou do segredo. Não aprovo refresh, lista de sessões nem a DEC-MV-21.”
- **DEC-MV-10, opção A:** “Aprovo a DEC-MV-10, opção A: manter a mensagem de 3.4.2 com 404 `EMAIL_NAO_ENCONTRADO`. Aceito, sem prazo e enquanto valer 3.4.2, que a recuperação de senha revele se um e-mail está cadastrado, pela mensagem e pelo tempo de resposta. Estou ciente de que o intervalo de reenvio, o limite de tentativas e uma eventual limitação de requisições (DEC-MV-21, que não aprovo aqui) não reduzem essa divulgação.”
- **DEC-MV-11:** “Aprovo a DEC-MV-11 conforme o dossiê §4.3 (R11.1 a R11.10): 10 minutos, 5 tentativas inválidas por emissão, 60 segundos entre emissões como constantes, a quinta tentativa inválida respondendo 400 e as seguintes 429, código `^[0-9]{8}$`, token de redefinição com a validade da emissão e senha de 8 a 128 caracteres sem composição obrigatória nem normalização.”
- **DEC-MV-12:** “Aprovo a DEC-MV-12 conforme o dossiê §4.4: envio SMTP com `smtplib` em thread, dentro da transação e antes do commit, TLS verificado (`starttls`, `tls` ou `nenhuma` só fora de produção), timeout por operação e exceções traduzidas sem dados pessoais, falso em memória nos testes, sem fila nem outbox. Aceito as consequências 1 a 6 da tabela, inclusive o recebimento eventual de um código sem valor.”
- **DEC-MV-13:** “Aprovo a DEC-MV-13: na v1, só `GET /api/v1/usuarios/me`, sem área de Perfil, sem edição de dados e sem troca de fuso. Ciente de que o fuso cadastrado define o ‘hoje’ da conta mesmo em viagem.”
- **DEC-MV-14, escopo limitado:** “Aprovo a DEC-MV-14 somente no escopo da F3: travas de linha da recuperação (`SELECT … FOR UPDATE` em `recuperacao_senha` e `INSERT … ON CONFLICT` na primeira emissão), conforme o dossiê §4.6. Não aprovo a trava consultiva por usuário nem o restante da DEC-MV-14.”
- **`CLAUDE.md` (CM-2), se a R9.9 for aprovada:** “Autorizo o diff CM-2 do dossiê §8 no `CLAUDE.md`, tabela 1, parágrafo ‘Regras’ de `usuario`, sem tocar em outras linhas.”
- **Diffs:** “Autorizo aplicar os diffs da §8 do dossiê correspondentes às decisões aprovadas (inclusive AR-8 revisto e AR-10), registrar a revisão M15 no índice, sincronizar as linhas dos achados ACH-MV-ARQ-035 e 036 na análise e liberar o Prompt F3 para a Etapa A.”

---

## 11. Lições da F2 no Prompt F3 (ACH-MV-F2-002)

| Lição | Onde ficou atendida no Prompt F3 | Verificação |
| --- | --- | --- |
| (a) Conteúdo exato coerente com o formatador | §8.1 e §11.2 (blocos exatos de `tempo.py` e `tests/apoio/relogio.py`); demais trechos marcados como contrato ou pseudocódigo | Logs `07a` a `07c` da preparação; `tempo.py` revisado nos logs `02a` a `02c` da revisão M15 |
| (b) Erros residuais de lint | §14, passo 9 (correção mecânica dentro da lista; reexecução com sufixo `_2`; parada para nova exceção) | Leitura do prompt |
| (c) Regra e modelo coerentes | §0, regra 12, e §8: os blocos exatos seguem as regras do próprio prompt (`@override`, tipos, sem `noqa`) | Logs `07a` a `07c`; `02a` a `02c` da revisão |
| (d) `--frozen --no-sync` | §14 (todos os checks e testes); instalação separada no passo 2, com lock antes e depois | Leitura do prompt |

Os quatro critérios estão atendidos no rascunho. Encerramento documental do ACH-MV-F2-002 registrado no índice, sem implicar aprovação das decisões da F3 nem sucesso de testes futuros. As lições complementares (expectativas derivadas do artefato final; relatório em arquivo; Alembic e Compose seguros) também estão no Prompt F3 (§0, §13 e §15).

---

## 12. Evidências desta preparação

Diretório: `~/minhavida_evidencias/f3_preparacao_ItDnDcl1/`.

| Log ou arquivo | Conteúdo |
| --- | --- |
| `00a`–`00j` | Estado do Git e commit |
| `01_conferencia_commit.log` | Delta, blobs, árvore e auditoria (script `conferir_commit.sh`) |
| `02_manifesto_fechamento.log` | `MANIFESTO_FECHAMENTO.sha256`: 10 OK e 1 divergência (mensagem) |
| `03`, `04`, `05` | Sondas de bibliotecas (`sondas/*.py`) |
| `06_fontes_sha256.log` | Hashes das fontes |
| `07a`–`07c` | Blocos exatos: Ruff e Pyright |

O manifesto final das evidências e os hashes dos documentos alterados estão no registro do índice e na mensagem de entrega, não aqui (sem hash circular).

---

## 13. Registro da revisão dirigida (M15)

**Autorização:** ajustar os rascunhos (este dossiê e o Prompt F3) e apresentar as reconciliações propostas. **Não** aprova DEC-MV-09 a 13, a parcela da DEC-MV-14 nem alterações de contratos vigentes. Nesta revisão:

- nenhum código, configuração, dependência, `.env` ou estado do Git foi alterado;
- a auditoria da F2 não foi reexecutada;
- o Prompt F3 continua `BLOQUEADO — AGUARDANDO_DECISAO`.

### 13.1. Pontos e resoluções

| # | Ponto | O que a verificação mostrou | Resolução | Onde |
| --- | --- | --- | --- | --- |
| 1 | `data_nascimento` como `date` com `Field(strict=True)` | Sonda `01`: o FastAPI 0.143 valida o corpo com `validate_python`. Em modo estrito, toda data em texto dá 422 `date_type`, inclusive `"1990-01-01"` (só `model_validate_json` aceitaria). Em modo comum, entram `1990-01-01T00:00:00`, `…Z`, `0` (vira 1970-01-01) e `631152000` | Validador `_data_civil` antes da conversão, sem modo estrito. Aceita `1990-01-01`, `2000-02-29` e `9999-12-31`. Recusa as 15 entradas indevidas da sonda com `DATA_INVALIDA`, o mesmo código que o catálogo já dá aos erros `date_*`. Ausente → `OBRIGATORIO` | §6.4 (E1); CT-F3-02; Prompt §10.1 |
| 2 | E-mail com `.normalized` no cadastro e só `strip().lower()` no login | Sonda `01`: variantes de um domínio internacionalizado (maiúsculas, Unicode composto ou decomposto, largura total, punycode) dão o mesmo `.ascii_email`, mas `strip().lower()` não as unifica. O rascunho podia gravar uma forma e buscar outra. Sonda `01b`: para endereços ASCII, `.ascii_email` coincide com aparar e passar para minúsculas | R9.9: `canonicalizar_email` → `.ascii_email` em cadastro, login, recuperação e SMTP (`To` e `SMTP_REMETENTE`). No login, um e-mail sem forma canônica segue o caminho do inexistente: mesma resposta 401, sem 422 novo | §4.1; §6.2; §6.4; CT-F3-01, 03, 04, 06 e 09; CM-2; Prompt §8.5, §9.1 e §10.1 |
| 3 | `services/recuperacao_senha` importando tipos de `services/identidade` | D-02 só permite importar os módulos de suporte que lista (e não inclui `autorizacao`). “Mesma fase” e “sem ciclo” não são exceção aprovada | Nenhuma importação entre services. `ContextoUsuario` vai para `tempo.py` (D-13). Os recursos viram parâmetros explícitos, no máximo 5 por função. `RecursosIdentidade` e `RecursosIdentidadeDep` saem. `autorizacao` não é importado por nenhum service na F3. AR-8 antigo retirado; o novo AR-8 só completa o diagrama | §6.1; §6.3; AR-4; AR-8; Prompt §8.1, §8.5 a §8.8 e §8.10 |
| 4 | Divergências entre dossiê e prompt | `list` × `deque` no enviador em memória; preparação no `lifespan` antes × depois da engine | `deque(maxlen=100)` e preparação **antes** de `criar_engine` nos dois documentos | §6.3; Prompt §8.4 e §8.10 |
| 5 | Sincronização dos testes de concorrência | A espera genérica (`aguardar_bloqueio(monitor, 2)`) termina com 2 sessões quaisquer em espera e não prova que as cinco requisições do CT-F3-15 estavam simultâneas | `aguardar_espera_por_trava`: contagem **exata** de sessões `active` em espera por `Lock`, filtrada pelo texto da consulta. Excede → falha na hora; prazo → falha com o valor observado. CT-F3-11 em passos, com a contagem zerada conferida logo após o reenvio e depois do código antigo | §7.1; §7.2; Prompt §5 e §11 |
| 6 | Explicação da DEC-MV-10 | O texto sugeria que limitar requisições mitigaria a enumeração | Corrigido: nenhuma limitação reduz a divulgação, que é permanente enquanto valer 3.4.2; um limitador só reduz o volume. AR-10 corrige o mesmo raciocínio na arquitetura §11 | §4.2; §10; AR-10 |

Ajuste decorrente do ponto 3: as rotas de login e verificação teriam 6 parâmetros com `response: Response`, o que viola PLR0913. O `Cache-Control: no-store` passou para a dependência `sem_cache`, declarada no decorador.

### 13.2. Evidências da revisão

Diretório: `~/minhavida_evidencias/f3_revisao_Lbkj9sjq/`.

| Log | Conteúdo |
| --- | --- |
| `01_sonda_data_email` | FastAPI e Pydantic: `strict` × modo comum × validador proposto; `email_validator` com variantes de domínio internacionalizado |
| `01b_sonda_email_ascii` | Forma canônica × aparar e minúsculas em entradas ASCII |
| `02a`–`02c` | Bloco exato de `tempo.py` (com `ContextoUsuario`) e de `tests/apoio/relogio.py`: `ruff check`, `ruff format --check` e Pyright limpos |
| `03_sonda_espera_trava` | PostgreSQL 15 descartável (mesma imagem e digest dos testes, removido ao fim; log `03b`). Consulta SQLAlchemy real, sem importar a aplicação. Resultados: 5 sessões paradas na trava com a bloqueadora fora da contagem; `tentativas` vistas 0 a 4 e final 5; concessão na ordem de chegada (3 repetições por ordem); `INSERT` de `usuario` e de `recuperacao_senha` em espera, com um sucesso e um conflito; redefinição sem linha depois do reenvio; falhas do helper por prazo e por excesso |

### 13.3. Propostas novas, para decisão

- **R9.9** (dentro da DEC-MV-09) e **CM-2** (`CLAUDE.md`): forma canônica do e-mail. A alternativa sem CM-2 está na §8.
- **AR-8 revisto:** completar o diagrama da §2.2. Recomendado, não indispensável.
- **AR-10:** corrigir a linha “Enumeração de contas” da arquitetura §11, se a opção A da DEC-MV-10 for aprovada.

### 13.4. Sincronizações fora dos rascunhos (aplicadas em 2026-10-13, M16)

| Documento | Local | Atual | Proposto |
| --- | --- | --- | --- |
| `indice.md` | §4 (registro de mensagens) | Sem a revisão M15 | Linha da M15: revisão dirigida dos rascunhos da F3, sem aprovações |
| `analise_projeto_minhavida.md` | ACH-MV-ARQ-035, colunas de correção e de critério | “Normalização explícita e validação ASCII”; “Diff AR-6 aplicado” | “Forma canônica (R9.9)”; “Diffs AR-6 e CM-2 aplicados” |
| `analise_projeto_minhavida.md` | ACH-MV-ARQ-036, coluna de correção | “`RecursosIdentidade` e avaliação auxiliar” | “Parâmetros explícitos (até 5) e avaliação auxiliar” |
| `analise_projeto_minhavida.md` | §9, nota da preparação da F3 | “R9.1–R9.8” | “R9.1–R9.9” |
| `analise_projeto_minhavida.md` | §9, linha da DEC-MV-10 | Recomendação “Aprovar (o registro já revela a existência)” | Mantida como histórico, com nota para o dossiê §4.2: o argumento é incompleto, e o risco aceito é permanente |

---

## 14. Liberação (M16)

**Autorização:** mensagem do usuário de 2026-10-13 (M16; `indice.md` §4). Aprova DEC-MV-09 a 13 e DEC-MV-14 no escopo da F3 e autoriza a reconciliação documental, inclusive CM-1, CM-2, AR-8 revisto e AR-10, as sincronizações da §13.4, o registro da M15 e da M16 e a liberação do Prompt F3. Não autoriza código, testes, migrações, configuração, dependências, `.env` nem escrita no Git.

### 14.1. Diffs aplicados

| Item | Local |
| --- | --- |
| CM-1, CM-2 | `CLAUDE.md`, só as duas frases (tabela 2, “Proposta operacional…”; tabela 1, “Regras” de `usuario`). Linhas 3, 10 e 12 intactas |
| AD-1, AD-2, AD-3 | ADR-0001: D-07, D-15 e tabela §3; estados de D-05 (parcial), D-07, D-13 e D-15 e §7 |
| AR-1 a AR-10 | Arquitetura: §2.2, §3.1, §4.2, §4.5, §6.2, §6.6, §7, §8.2, §8.3, §9.1 e §11 |
| PF-1 | Plano de fases, ficha da F3 e estados |
| PV-1 | Plano de validação, catálogo da F3 (CT-F3-22 a 24 e 26 a 29 acrescentados) |
| MZ-1 | Matriz, 3.2.1, e situações das telas 1 a 3 |
| §13.4 | Análise (ACH-MV-ARQ-035 e 036, R9.9, nota da DEC-MV-10) e índice (M15 e M16) |

### 14.2. Ajustes de consistência

Feitos para que as fontes normativas não contradigam o que foi aprovado. Nenhum cria regra nova:

- **CM-1:** a §8 citava “até cinco tentativas por emissão”; a frase real do `CLAUDE.md` tem “até cinco tentativas de código por emissão”. A substituição alcançou a frase real inteira, como previsto.
- **ADR-0001:**
  - D-07 deixou de dizer “Validade de 24 h (proposta a validar)” e passou à validade aprovada (R9.1);
  - o primeiro item de D-15 trocou `asyncio.to_thread` e “STARTTLS configurável” por `anyio` e `SMTP_SEGURANCA` (AD-2).
- **Arquitetura:**
  - códigos `NOME_COMPLETO_*` no catálogo §4.5 (AR-6);
  - primeira emissão com `INSERT … ON CONFLICT` na linha `recuperacao_senha` de §6.2 (AR-9);
  - `ContextoUsuario` e `hoje_no_fuso` em `tempo.py` e origem do instante na recuperação, em §7 (AR-2, AR-3 e R11.2);
  - linha “Token roubado” de §11 com a validade aprovada;
  - §5.3 com a assinatura `verificar_codigo(sessao, dados, relogio, hasher)` e o `Retry-After` de `TENTATIVAS_ESGOTADAS` (R11.6), como em §8.3.2;
  - regra de §2.2 sobre o que os services recebem, com os recursos da F3.

  O pseudocódigo de §8.2 e §8.3 é o mesmo do Prompt F3 §8.5 a §8.8.
- **Plano de fases:** itens 7, 11 e 12 da ficha da F3. Verificação fictícia **não** é tempo constante (AD-1); validação temporal toda manual (AR-4); mensagem 3.4.2 (DEC-MV-10).
- **Matriz:** “Área de Perfil e alteração de fuso” e “Logout no servidor” passaram às exclusões decididas (DEC-MV-13 e 09).
- **Análise:** riscos RSK-MV-03 e 04 com as decisões que os aceitam.
- **Este dossiê:**
  - CT-F3-02 passou a dizer “parte local não ASCII”, porque um domínio internacionalizado é válido pela R9.9;
  - estados das §0, §5.2, §6, §8, §9, §10 e §13.4.

Evidências da liberação: `~/minhavida_evidencias/f3_liberacao_gVSk8Hbn/` (cópias de antes, scripts de edição, diffs, verificações e manifesto). Os SHA-256 finais dos documentos estão no Prompt F3 §1.2; o hash do prompt está só na mensagem de entrega.
