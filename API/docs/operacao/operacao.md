# Operação da API MinhaVida

Guia independente de plataforma (a plataforma de deploy ainda não foi escolhida). Nada aqui foi executado em ambiente real.

## 1. Processos

| Processo | Comando | Observações |
| --- | --- | --- |
| API | `uv run uvicorn api_gestao_pessoal.main:app --host 0.0.0.0 --port 8000` (atrás de proxy com TLS) | Vários *workers* são seguros: a consistência vem do banco (travas consultivas, `ON CONFLICT`, `SKIP LOCKED`) |
| Processador de lembretes | `uv run python -m api_gestao_pessoal.jobs.processar_lembretes` | **Um processo basta**; mais de um é seguro (`SKIP LOCKED`). Encerra com `SIGTERM`/`SIGINT` após o item corrente. `--uma-vez` roda um ciclo (útil para *cron*) e sai com código 1 se algum item falhou |
| Migrações | `uv run alembic upgrade head` | Rodar **antes** de subir a nova versão. A cabeça atual é `0002` |

Saúde: `GET /saude` (liveness) e `GET /saude/pronto` (readiness com `SELECT 1`).

## 2. Configuração (variáveis de ambiente / `.env`)

Obrigatórias em produção: `DATABASE_URL` (`postgresql+psycopg://…`), `JWT_SEGREDO` (≥ 32 bytes, gere com `python -c "import secrets; print(secrets.token_urlsafe(32))"`), `AMBIENTE=producao`, `EMAIL_MODO=smtp` com `SMTP_HOST`, `SMTP_REMETENTE` (e credenciais se houver) e `SMTP_SEGURANCA` diferente de `nenhuma`.
Em produção a aplicação **recusa iniciar** com `EMAIL_MODO=memoria|console`, Argon2id abaixo do piso (custo 3, 64 MiB) ou SMTP sem criptografia.
Opcionais: `LOG_NIVEL`, `DB_*`, `JWT_VALIDADE_MINUTOS` (5–1440), `LEMBRETES_INTERVALO_S` (60), `LEMBRETES_LOTE` (100), `LEMBRETES_JANELA_DIAS` (8) e `CORS_ORIGENS` (só para clientes web).

## 3. Banco de dados

- PostgreSQL 15 ou superior (os testes usam 15 em contêiner e 16 localmente).
- Usuário da aplicação sem privilégio de DDL em produção; o usuário de migração é separado.
- Alterações de esquema só por Alembic, com *downgrade* testado (`tests/esquema`).

## 4. Backup e restauração (proposta a validar)

`pg_dump` diário com retenção de 7 dias (RPO 24 h, RTO 4 h) e **teste de restauração periódico** em ambiente descartável. Notificações e lembretes fazem parte do banco; a retirada dos registros de `requisicao_idempotente` ainda não tem rotina (ver §7).

## 5. Job de lembretes: atraso e parada

Se o processador ficar parado, os lembretes vencidos são processados ao voltar, **enquanto a data do compromisso não tiver passado**; depois disso a versão vira `CANCELADO` sem notificação (DEC-MV-20). Monitore: quantidade de `lembrete_importancia` com `situacao='PENDENTE' AND agendado_para < now() - interval '15 minutes'` (deve ser ~0).

## 6. Limitação de tentativas de login (DEC-MV-21) — exigência de borda

A API não limita tentativas (o custo do Argon2id e o limite de concorrência de *hash* reduzem, mas não eliminam, a força bruta). Antes de expor à internet, configure no proxy/WAF, por IP e por rota:

- `POST /api/v1/auth/login`: no máximo ~10 req/min por IP;
- `POST /api/v1/auth/recuperacao/*`: no máximo ~5 req/min por IP.

A recuperação de senha revela se um e-mail tem conta (decisão DEC-MV-10, opção A, aceita). O limitador só reduz o volume de consultas.

## 7. Riscos remanescentes

| Risco | Situação |
| --- | --- |
| Força bruta de login | Mitigação na borda (§6); sem ela, risco aceito só em desenvolvimento |
| Enumeração de contas | Aceita (DEC-MV-10) |
| Token em poder de terceiros vale até expirar (24 h) | Aceito (DEC-MV-09); troca de senha invalida os anteriores |
| Crescimento de `requisicao_idempotente` | Sem rotina de limpeza; definir prazo de garantia contra reenvio antes de criar uma |
| Lembretes atrasados se o job parar | Monitoramento do §5 |
| Primeira consulta de séries muito antigas materializa muitas linhas (≈ 0,5 s para 5 anos de série diária) | Medido; custo único por série |
| Sem *push* do dispositivo | Só notificações internas (sino); push exigiria cadastro de dispositivos |
| Aplicativo guarda o token só em memória | Login a cada abertura; persistência exige armazenamento seguro (decisão pendente) |

## 8. Checklist de produção

- [ ] `AMBIENTE=producao`, `JWT_SEGREDO` gerado e guardado em cofre de segredos
- [ ] SMTP real testado (recuperação de senha de ponta a ponta)
- [ ] TLS no proxy; porta do banco não exposta
- [ ] Limitação de login configurada (§6)
- [ ] `alembic upgrade head` aplicado; backup e restauração testados
- [ ] Processador de lembretes em execução e monitorado
- [ ] `/saude/pronto` no balanceador
- [ ] `uv run pytest -q`, `ruff check --no-fix .`, `ruff format --check .` e `pyright` limpos na versão implantada
