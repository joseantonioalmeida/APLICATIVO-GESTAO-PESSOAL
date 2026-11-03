// Gera imagens das 13 telas (modo conferência visual com os protótipos).
// Execute: flutter test --update-goldens test/telas_golden_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:minhavida/models/modelos.dart';
import 'package:minhavida/shell/rotas.dart';
import 'package:minhavida/state/app_scope.dart';

import 'apoio/app_teste.dart';

Future<void> foto(WidgetTester t, String nome) async {
  await assentar(t);
  await expectLater(
    find.byType(MaterialApp),
    matchesGoldenFile('goldens/$nome.png'),
  );
}

void main() {
  setUpAll(iniciarLocale);

  testWidgets('01 login', (t) async {
    await abrirApp(t, logado: false);
    await foto(t, '01_login');
    await encerrar(t);
  });

  testWidgets('02 registro', (t) async {
    await abrirApp(t, logado: false);
    await t.tap(find.text('Registrar-se'));
    await assentar(t);
    await foto(t, '02_registro');
    await encerrar(t);
  });

  testWidgets('03-05 recuperação de senha', (t) async {
    await abrirApp(t, logado: false);
    await t.tap(find.text('Esqueceu a senha?'));
    await assentar(t);
    await foto(t, '03_esqueceu');
    await t.enterText(find.byType(TextField).first, 'julio@email.com');
    await t.pump();
    await t.tap(find.text('Enviar'));
    await assentar(t);
    await foto(t, '04_codigo');
    final aviso =
        find.textContaining('código enviado: ').evaluate().first.widget as Text;
    final codigo = RegExp(r'(\d{8})').firstMatch(aviso.data!)!.group(1)!;
    await t.enterText(find.byType(TextField).first, codigo);
    await t.pump();
    await t.tap(find.text('Enviar'));
    await assentar(t);
    await foto(t, '05_nova_senha');
    await encerrar(t);
  });

  testWidgets('06 inicio', (t) async {
    await abrirApp(t);
    await foto(t, '06_inicio');
    await t.drag(find.byType(ListView).first, const Offset(0, -600));
    await assentar(t);
    await foto(t, '06b_inicio_rolado');
    await encerrar(t);
  });

  testWidgets('07 atividades', (t) async {
    await abrirApp(t);
    escopo(t).navegacao.irPara(Aba.atividades);
    await assentar(t);
    await foto(t, '07_atividades');
    await encerrar(t);
  });

  testWidgets('08 cadastrar atividade', (t) async {
    await abrirApp(t);
    abrirFormAtividade(contexto(t), data: DateTime(2025, 9, 29));
    await assentar(t);
    await t.enterText(find.byType(TextField).first, 'Estudar para a prova');
    await t.pump();
    await foto(t, '08_form_atividade');
    await encerrar(t);
  });

  testWidgets('09 importancias', (t) async {
    await abrirApp(t);
    escopo(t).navegacao.irPara(Aba.importancias);
    await assentar(t);
    await foto(t, '09_importancias');
    await encerrar(t);
  });

  testWidgets('10 cadastrar importancia', (t) async {
    await abrirApp(t);
    abrirFormImportancia(contexto(t));
    await assentar(t);
    await foto(t, '10_form_importancia');
    await encerrar(t);
  });

  testWidgets('11 financeiro', (t) async {
    await abrirApp(t);
    escopo(t).navegacao.irPara(Aba.financeiro);
    await assentar(t);
    await foto(t, '11_financeiro');
    await encerrar(t);
  });

  testWidgets('12 cadastrar receita', (t) async {
    await abrirApp(t);
    abrirFormReceita(contexto(t));
    await assentar(t);
    await foto(t, '12_form_receita');
    await encerrar(t);
  });

  testWidgets('13 cadastrar despesa', (t) async {
    final repo = await abrirApp(t);
    final lista = await repo.consultarImportancias(
      FiltroImportancia.hoje,
      ano: 2025,
      mes: 9,
    );
    abrirFormDespesa(contexto(t), importancia: lista.first);
    await assentar(t);
    await foto(t, '13_form_despesa');
    await encerrar(t);
  });
}
