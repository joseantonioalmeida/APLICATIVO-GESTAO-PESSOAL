// Interface contra a API real: login pela tela, painel inicial e navegação.
// Só roda com API_URL_TESTE definida (ver integracao_api_test.dart).
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/io_client.dart';
import 'package:minhavida/app.dart';
import 'package:minhavida/data/cliente_api.dart';
import 'package:minhavida/data/repositorio_api.dart';
import 'package:minhavida/models/modelos.dart';

import 'apoio/app_teste.dart';

Future<void> esperar(WidgetTester t, Finder f, {int voltas = 80}) async {
  for (var i = 0; i < voltas; i++) {
    await t.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 75)),
    );
    await t.pump(const Duration(milliseconds: 50));
    if (f.evaluate().isNotEmpty) return;
  }
  fail('não apareceu: $f');
}

void main() {
  final url = Platform.environment['API_URL_TESTE'];
  if (url == null || url.isEmpty) {
    test('interface com a API', () {}, skip: 'defina API_URL_TESTE');
    return;
  }
  setUpAll(() async {
    // O flutter_test bloqueia a rede; aqui é desejada (API local de teste).
    HttpOverrides.global = null;
    await iniciarLocale();
  });

  testWidgets('login pela tela, painel e atividade criada na API', (t) async {
    t.view.physicalSize = const Size(390, 844) * 2;
    t.view.devicePixelRatio = 2;
    addTearDown(t.view.resetPhysicalSize);
    addTearDown(t.view.resetDevicePixelRatio);

    final repo = RepositorioApi(
      cliente: ClienteApi(
        base: Uri.parse(url),
        // Sem conexões ociosas: o teste não pode deixar timers pendentes.
        cliente: IOClient(HttpClient()..idleTimeout = Duration.zero),
      ),
      fusoHorario: 'America/Sao_Paulo',
    );
    final email = 'ui${DateTime.now().microsecondsSinceEpoch}@exemplo.com';
    await t.runAsync(() async {
      await repo.registrar(
        nome: 'Carla Menezes',
        email: email,
        senha: 'Senha@12345',
        nascimento: DateTime(1992, 3, 4),
      );
      final hoje = DateTime.now();
      await repo.criarMovimentacao(
        MovimentacaoForm(
          tipo: TipoMov.receita,
          nome: 'Salário',
          valor: 245075,
          categoria: 'Salário',
          data: DateTime(hoje.year, hoje.month, 1),
        ),
      );
      await repo.criarMovimentacao(
        MovimentacaoForm(
          tipo: TipoMov.despesa,
          nome: 'Mercado',
          valor: 123040,
          categoria: 'Alimentação',
          data: DateTime(hoje.year, hoje.month, 1),
        ),
      );
      repo.sair();
    });

    await t.pumpWidget(MinhaVidaApp(repositorio: repo));
    await t.pump(const Duration(milliseconds: 200));
    expect(find.text('Bem-vindo de volta'), findsOneWidget);

    // Credenciais erradas: mensagem da API na tela.
    await t.enterText(find.byType(TextField).at(0), email);
    await t.enterText(find.byType(TextField).at(1), 'errada-demais');
    await t.tap(find.text('Entrar'));
    await esperar(t, find.text('E-mail ou senha inválidos.'));

    await t.enterText(find.byType(TextField).at(1), 'Senha@12345');
    await t.tap(find.text('Entrar'));
    await esperar(t, find.text('Olá, Carla!'));

    // Saldo do mês do painel = receitas - despesas (4.3.1): R$ 1.220,35.
    await esperar(t, find.textContaining('1.220,35'));
    expect(find.textContaining('Receitas'), findsWidgets);

    // Deixa terminar as consultas das demais abas antes de desmontar.
    for (var i = 0; i < 20; i++) {
      await t.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 100)),
      );
      await t.pump(const Duration(milliseconds: 50));
    }
    repo.sair();
    await t.pumpWidget(const SizedBox.shrink());
    await t.pump(const Duration(milliseconds: 50));
  });
}
