# MinhaVida

Aplicativo de gestão pessoal e finanças: API (`API/`, FastAPI + PostgreSQL) e
aplicativo (`MOBILE/`, Flutter).

## Subir tudo com Docker (um comando)

```bash
cp .env.exemplo .env
# edite o .env: POSTGRES_PASSWORD e JWT_SEGREDO (os comandos de geração estão no arquivo)
docker compose up -d --build                  # banco + migrações + API + lembretes
docker compose --profile web up -d --build    # o mesmo, mais o aplicativo no navegador
```

| Serviço | O que faz | Endereço |
| --- | --- | --- |
| `db` | PostgreSQL 15 (dados no volume `postgres_data`) | `127.0.0.1:5432` |
| `migrar` | aplica `alembic upgrade head` e termina | — |
| `api` | servidor HTTP (documentação em `/docs`) | http://localhost:8000 |
| `lembretes` | gera as notificações do sino | — |
| `web` (perfil `web`) | aplicativo Flutter no navegador | http://localhost:3000 |

Dia a dia:

```bash
docker compose ps                       # estado e saúde dos serviços
docker compose logs -f api lembretes    # logs (o código de "Esqueceu a senha" aparece aqui)
docker compose up -d --build            # depois de um git pull
docker compose down                     # para tudo (os dados ficam)
docker compose down -v                  # para tudo e APAGA o banco
```

Notas:

- O `.env` fica só na sua máquina (não vai para o git). Use senhas sem caracteres especiais
  de URL (`openssl rand -hex 16`).
- O app web guarda o endereço da API na compilação (`PUBLIC_API_URL`, padrão
  `http://localhost:8000`); mudou o endereço, rode `up -d --build` de novo.
- Para celular físico/emulador Android não há contêiner: use `flutter run` em `MOBILE/`
  apontando `--dart-define=API_URL=http://IP_DO_COMPUTADOR:8000` (e `API_BIND=0.0.0.0` no `.env`).
- Desenvolvimento da API sem contêiner e testes: `API/README.md`. Produção: `API/docs/operacao/operacao.md`.
