import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:minhavida/core/formatadores.dart';
import 'package:minhavida/data/repositorio_memoria.dart';
import 'package:minhavida/models/modelos.dart';
import 'package:minhavida/shell/rotas.dart';

import 'apoio/app_teste.dart';

void main() {
  setUpAll(iniciarLocale);

  group('Formatação', () {
    test('centavos e moeda', () {
      expect(Conv.centavos('99,90'), 9990);
      expect(Conv.centavos('1.234,56'), 123456);
      expect(Conv.centavos('100'), 10000);
      expect(() => Conv.centavos('1,234'), throwsFormatException);
      expect(Fmt.moeda(122035), 'R\$ 1.220,35');
      expect(Fmt.duracao(210), '3h 30min');
    });
  });

  group('Regras do repositório', () {
    late RepositorioMemoria repo;
    setUp(() async {
      repo = RepositorioMemoria(relogio: relogioFixo);
      await repo.entrar('julio@email.com', 'Senha@123');
    });

    test('saldo do mês = receitas - despesas e comparações', () async {
      final r = await repo.resumoMes(2025, 9);
      expect(r.receitas, 245075);
      expect(r.despesas, 123040);
      expect(r.saldo, 122035);
      expect(r.compReceitas.percentual, 12.0);
      expect(r.compDespesas.percentual, 8.0);
      expect(r.dias.length, 30);
    });

    test('atividades de hoje: 6 total, 4 concluídas, 10h30', () async {
      final c = await repo.consultarAtividades(
          FiltroAtividades(data: DateTime(2025, 9, 29)),
          limite: 100);
      expect((c.total, c.concluidas, c.pendentes, c.minutos), (6, 4, 2, 630));
      expect((await repo.pendenciasAnteriores()).quantidade, 2);
    });

    test('concluir é idempotente', () async {
      final c = await repo.consultarAtividades(
          FiltroAtividades(data: DateTime(2025, 9, 29)));
      final id = c.itens.firstWhere((a) => !a.concluida).id;
      await repo.alterarConclusaoAtividade(id, true);
      await repo.alterarConclusaoAtividade(id, true);
      expect((await repo.obterAtividade(id)).concluida, true);
    });

    test('série semanal 08, 15 e 22/10', () async {
      await repo.criarAtividade(AtividadeForm(
        nome: 'Reunião',
        categoria: 'Trabalho',
        prioridade: Prioridade.baixa,
        data: DateTime(2026, 10, 8),
        inicio: 480,
        fim: 540,
        periodicidade: Periodicidade.semanal,
        dataFinal: DateTime(2026, 10, 22),
      ));
      var n = 0;
      for (final d in [8, 15, 22]) {
        n += (await repo.consultarAtividades(
                FiltroAtividades(data: DateTime(2026, 10, d))))
            .total;
      }
      expect(n, 3);
    });

    test('pagamento vinculado conta uma vez e exclusão reabre', () async {
      final imp = (await repo.consultarImportancias(FiltroImportancia.hoje,
              ano: 2025, mes: 9))
          .first;
      final antes = (await repo.resumoMes(2025, 9)).despesas;
      final m = await repo.criarMovimentacao(MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: imp.nome,
        valor: 10500,
        categoria: 'Contas',
        data: DateTime(2025, 9, 29),
        importanciaId: imp.id,
      ));
      expect((await repo.resumoMes(2025, 9)).despesas, antes + 10500);
      final paga = await repo.obterImportancia(imp.id);
      expect(paga.concluida && paga.paga, true);
      expect(paga.valorPago, 10500);
      expect(paga.valorPrevisto, 9990);
      expect(
          () => repo.criarMovimentacao(MovimentacaoForm(
                tipo: TipoMov.despesa,
                nome: 'Outra',
                valor: 100,
                categoria: 'Contas',
                data: DateTime(2025, 9, 29),
                importanciaId: imp.id,
              )),
          throwsA(isA<ErroApp>()));
      await repo.excluirMovimentacao(m.id);
      expect((await repo.obterImportancia(imp.id)).concluida, false);
      expect((await repo.resumoMes(2025, 9)).despesas, antes);
    });

    test('data futura rejeitada', () async {
      expect(
          () => repo.criarMovimentacao(MovimentacaoForm(
                tipo: TipoMov.receita,
                nome: 'X',
                valor: 100,
                categoria: 'Outros',
                data: DateTime(2025, 10, 1),
              )),
          throwsA(isA<ErroApp>()));
    });

    test('recuperação de senha', () async {
      expect(() => repo.solicitarCodigo('naoexiste@x.com'),
          throwsA(isA<ErroApp>()));
      final c1 = await repo.solicitarCodigo('julio@email.com');
      final c2 = await repo.solicitarCodigo('julio@email.com');
      if (c1 != c2) {
        expect(() => repo.verificarCodigo('julio@email.com', c1!),
            throwsA(isA<ErroApp>()));
      }
      final tok = await repo.verificarCodigo('julio@email.com', c2!);
      await repo.redefinirSenha(
          email: 'julio@email.com', token: tok, novaSenha: 'NovaSenha1');
      repo.sair();
      await repo.entrar('julio@email.com', 'NovaSenha1');
    });
  });

  group('Telas', () {
    testWidgets('login inválido mostra erro e válido entra', (t) async {
      await abrirApp(t, logado: false);
      await t.tap(find.text('Entrar'));
      await t.pump();
      expect(find.text('Informe seu e-mail'), findsOneWidget);
      await t.enterText(find.byType(TextField).at(0), 'julio@email.com');
      await t.enterText(find.byType(TextField).at(1), 'errada123');
      await t.tap(find.text('Entrar'));
      await assentar(t);
      expect(find.text('E-mail ou senha incorretos.'), findsOneWidget);
      await t.enterText(find.byType(TextField).at(1), 'Senha@123');
      await t.tap(find.text('Entrar'));
      await assentar(t);
      expect(find.text('Olá, Júlio!'), findsOneWidget);
      await encerrar(t);
    });

    testWidgets('formulário de atividade valida campos', (t) async {
      await abrirApp(t);
      abrirFormAtividade(contexto(t));
      await assentar(t);
      await t.tap(find.text('Salvar atividade'));
      await assentar(t);
      expect(find.text('Informe o nome da atividade'), findsOneWidget);
      expect(find.text('Selecione uma categoria'), findsWidgets);
      expect(find.text('Informe o horário inicial'), findsOneWidget);
      await encerrar(t);
    });

    testWidgets('concluir atividade na Início atualiza contagem', (t) async {
      await abrirApp(t);
      expect(find.text('4 de 6 atividades concluídas'), findsOneWidget);
      await t.tap(find.bySemanticsLabel('Concluir atividade').first);
      await assentar(t);
      expect(find.text('5 de 6 atividades concluídas'), findsOneWidget);
      await encerrar(t);
    });
  });
}
