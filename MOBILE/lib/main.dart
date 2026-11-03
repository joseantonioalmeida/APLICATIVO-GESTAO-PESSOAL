import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/date_symbol_data_local.dart';

import 'app.dart';
import 'data/repositorio_memoria.dart';

/// Dados de demonstração (usuário julio@email.com / Senha@123).
/// Para iniciar vazio: `flutter run --dart-define=DADOS_DEMO=false`.
const _dadosDemo = bool.fromEnvironment('DADOS_DEMO', defaultValue: true);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('pt_BR');
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);

  // Troque por uma implementação HTTP de `Repositorio` quando a API estiver pronta.
  final repositorio = RepositorioMemoria(demonstracao: _dadosDemo);
  runApp(MinhaVidaApp(repositorio: repositorio));
}
