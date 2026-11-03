import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:minhavida/app.dart';
import 'package:minhavida/data/repositorio_memoria.dart';
import 'package:minhavida/state/app_scope.dart';

/// Segunda-feira, 29/09/2025, 10:00 - a mesma data dos protótipos.
final agoraFixo = DateTime(2025, 9, 29, 10, 0);
DateTime relogioFixo() => agoraFixo;

/// Prepara locale e fontes (o flutter_test não carrega fontes do pubspec).
Future<void> iniciarLocale() async {
  await initializeDateFormatting('pt_BR');
  final jakarta = FontLoader('PlusJakartaSans');
  for (final peso in [400, 500, 600, 700, 800]) {
    final bytes = File('assets/fonts/PlusJakartaSans-$peso.ttf')
        .readAsBytesSync();
    jakarta.addFont(Future.value(ByteData.sublistView(bytes)));
  }
  await jakarta.load();
  final dir = Platform.environment['FLUTTER_ROOT'] ?? '/opt/flutter';
  final icones = File(
    '$dir/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf',
  );
  if (icones.existsSync()) {
    final l = FontLoader('MaterialIcons')
      ..addFont(Future.value(ByteData.sublistView(icones.readAsBytesSync())));
    await l.load();
  }
}

/// Cria o app com o repositório em memória e relógio fixo.
Future<RepositorioMemoria> abrirApp(
  WidgetTester tester, {
  bool logado = true,
  bool demonstracao = true,
  Size tamanho = const Size(390, 844),
}) async {
  tester.view.physicalSize = tamanho * 2;
  tester.view.devicePixelRatio = 2;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final repo = RepositorioMemoria(
    relogio: relogioFixo,
    demonstracao: demonstracao,
  );
  if (logado) await repo.entrar('julio@email.com', 'Senha@123');
  await tester.pumpWidget(
    MinhaVidaApp(repositorio: repo, relogio: relogioFixo),
  );
  await assentar(tester);
  return repo;
}

/// Avança alguns quadros (sem esperar timers periódicos).
Future<void> assentar(WidgetTester tester) async {
  for (var i = 0; i < 6; i++) {
    await tester.pump(const Duration(milliseconds: 120));
  }
}

BuildContext contexto(WidgetTester tester) =>
    tester.element(find.byType(Scaffold).first);

AppScope escopo(WidgetTester tester) => AppScope.of(contexto(tester));

/// Desmonta a árvore (cancela os timers periódicos das telas).
Future<void> encerrar(WidgetTester tester) async {
  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pump(const Duration(milliseconds: 50));
}
