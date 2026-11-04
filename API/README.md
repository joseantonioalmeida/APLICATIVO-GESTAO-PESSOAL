# API MinhaVida

FastAPI + SQLAlchemy (async) + PostgreSQL. Documentação em `docs/` e prompts em `PROMPTS/`.

## Executar
```bash
cp .env.exemplo .env      # preencha os valores (JWT_SEGREDO é obrigatório)
docker compose up -d      # PostgreSQL
uv sync
uv run alembic upgrade head
uv run fastapi dev src/api_gestao_pessoal/main.py
```
A documentação interativa fica em `http://127.0.0.1:8000/docs`.

## Testes e qualidade
```bash
uv run pytest                  # usa Testcontainers (precisa de Docker)
TESTE_POSTGRES_URL=postgresql+psycopg://USUARIO@127.0.0.1:5432/minhavida_teste uv run pytest   # sem Docker
uv run ruff check . && uv run ruff format --check . && uv run pyright
```

## Fases implementadas
F1 a F11: fundação, esquema, identidade, núcleo transacional, atividades e recorrência, financeiro,
importâncias, vínculo despesa-importância, **lembretes e notificações (F9)**, **painel (F10)** e
**consolidação (F11)**. Detalhes em `docs/arquitetura/plano_fases_api.md`, `decisoes_f4_f5.md`,
`decisoes_f6_f8.md` e `decisoes_f9_f11.md`. Operação e checklist de produção: `docs/operacao/operacao.md`.

## Processador de lembretes (notificações do sino)
```bash
uv run python -m api_gestao_pessoal.jobs.processar_lembretes            # contínuo
uv run python -m api_gestao_pessoal.jobs.processar_lembretes --uma-vez  # um ciclo
```
Sem esse processo os lembretes são salvos e agendados, mas nenhuma notificação é gerada.

## Desempenho (separado da suíte padrão)
```bash
uv run pytest tests/desempenho -m performance -q
```
