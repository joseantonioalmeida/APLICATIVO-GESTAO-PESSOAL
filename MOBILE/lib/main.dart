import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/date_symbol_data_local.dart';

import 'app.dart';
import 'data/cliente_api.dart';
import 'data/repositorio.dart';
import 'data/repositorio_api.dart';
import 'data/repositorio_memoria.dart';

/// Modo demonstração, sem servidor (usuário julio@email.com / Senha@123):
/// `flutter run --dart-define=USAR_MEMORIA=true`.
const _usarMemoria = bool.fromEnvironment('USAR_MEMORIA');

/// Endereço da API: `flutter run --dart-define=API_URL=http://192.168.0.10:8000`.
/// Sem a variável: emulador Android usa 10.0.2.2; os demais, localhost.
const _apiUrl = String.fromEnvironment('API_URL');

/// Fuso IANA enviado no cadastro (padrão: deduzido do aparelho).
const _fuso = String.fromEnvironment('FUSO_HORARIO');

Repositorio _criarRepositorio() {
  if (_usarMemoria) return RepositorioMemoria();
  final url = _apiUrl.isNotEmpty
      ? _apiUrl
      : (defaultTargetPlatform == TargetPlatform.android && !kIsWeb
            ? 'http://10.0.2.2:8000'
            : 'http://localhost:8000');
  return RepositorioApi(
    cliente: ClienteApi(base: Uri.parse(url)),
    fusoHorario: _fuso.isEmpty ? null : _fuso,
  );
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('pt_BR');
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
  runApp(MinhaVidaApp(repositorio: _criarRepositorio()));
}
