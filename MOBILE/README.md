# MinhaVida — app Flutter (MOBILE)

As 13 telas do protótipo (login, registro, recuperação de senha em 3 passos, Início,
Atividades, Cadastrar atividade, Importâncias, Cadastrar importância, Financeiro,
Cadastrar receita e Cadastrar despesa), implementadas conforme o `API/CLAUDE.md`.

## Executar
O aplicativo usa a **API** (pasta `../API`) por padrão. Suba a API antes (veja `API/README.md`;
para testar "Esqueceu a senha" use `EMAIL_MODO=console` e leia o código no log da API) e rode:
```bash
cd MOBILE
flutter pub get
flutter run --dart-define=API_URL=http://SEU_IP:8000      # aparelho físico / desktop / web
flutter run                                                 # emulador Android (usa http://10.0.2.2:8000)
```
- Sem `API_URL`: Android → `http://10.0.2.2:8000`; demais plataformas → `http://localhost:8000`.
- O fuso do cadastro é deduzido do aparelho (Brasil); para forçar: `--dart-define=FUSO_HORARIO=America/Sao_Paulo`.
- A sessão fica só em memória: o login é pedido a cada abertura do aplicativo.
- As notificações do sino dependem do processador de lembretes da API
  (`uv run python -m api_gestao_pessoal.jobs.processar_lembretes`).

### Modo demonstração (sem servidor)
```bash
flutter run --dart-define=USAR_MEMORIA=true
```
Dados de demonstração: **julio@email.com / Senha@123** (o código de recuperação de senha
aparece num aviso na tela). Para iniciar vazio: `--dart-define=DADOS_DEMO=false`.

## Testes e análise
```bash
flutter analyze
flutter test
flutter test --update-goldens test/telas_golden_test.dart   # gera imagens das telas em test/goldens
# Integração contra a API real (API no ar; cada execução cria usuários novos):
API_URL_TESTE=http://localhost:8000 flutter test test/integracao_api_test.dart test/integracao_ui_test.dart
```

## Arquitetura
- `lib/data/repositorio.dart`: **contrato** de dados, com duas implementações:
  `repositorio_api.dart` (API MinhaVida, padrão, sobre `cliente_api.dart`) e
  `repositorio_memoria.dart` (demonstração). A escolha é feita em `lib/main.dart`;
  as telas não dependem da implementação.
- `lib/screens/`: telas; `lib/widgets/`: componentes; `lib/core/`: tema, formatação, validação.
- Valores monetários trafegam em centavos (inteiros).
