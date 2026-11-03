# MinhaVida — app Flutter (MOBILE)

As 13 telas do protótipo (login, registro, recuperação de senha em 3 passos, Início,
Atividades, Cadastrar atividade, Importâncias, Cadastrar importância, Financeiro,
Cadastrar receita e Cadastrar despesa), implementadas conforme o `API/CLAUDE.md`.

## Executar
```bash
cd MOBILE
flutter pub get
flutter run
```
Dados de demonstração: **julio@email.com / Senha@123** (o código de recuperação de senha
aparece num aviso na tela, pois não há envio real de e-mail).
Para iniciar vazio: `flutter run --dart-define=DADOS_DEMO=false`.

## Testes e análise
```bash
flutter analyze
flutter test
flutter test --update-goldens test/telas_golden_test.dart   # gera imagens das telas em test/goldens
```

## Arquitetura
- `lib/data/repositorio.dart`: **contrato** de dados. Hoje implementado por
  `repositorio_memoria.dart` (regras de negócio locais). Para ligar a API, crie uma
  implementação HTTP de `Repositorio` e troque-a em `lib/main.dart`; as telas não mudam.
- `lib/screens/`: telas; `lib/widgets/`: componentes; `lib/core/`: tema, formatação, validação.
- Valores monetários trafegam em centavos (inteiros).
