# API MinhaVida

FastAPI + SQLAlchemy (async) + PostgreSQL. Documentação em `docs/` e prompts em `PROMPTS/`.

## Executar
```bash
cp .env.exemplo .env      # preencha os valores
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
F1 fundação, F2 esquema, F3 identidade, F4 núcleo transacional, F5 atividades e recorrência,
**F6 financeiro**, **F7 importâncias** e **F8 vínculo despesa-importância**.
Pendentes: F9 (processador de lembretes e notificações), F10 (painel) e F11 (consolidação).
Veja `docs/arquitetura/plano_fases_api.md`, `decisoes_f4_f5.md` e `decisoes_f6_f8.md`.
