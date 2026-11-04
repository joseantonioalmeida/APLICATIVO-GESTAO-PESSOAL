// Integração do aplicativo com a API real.
//
// Só roda com a API no ar e a variável API_URL_TESTE definida, por exemplo:
//   API_URL_TESTE=http://localhost:8000 flutter test test/integracao_api_test.dart
// Cada execução cria um usuário novo; nada é apagado do banco.
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:minhavida/data/cliente_api.dart';
import 'package:minhavida/data/repositorio_api.dart';
import 'package:minhavida/models/modelos.dart';

void main() {
  final url = Platform.environment['API_URL_TESTE'];
  if (url == null || url.isEmpty) {
    test(
      'integração com a API',
      () {},
      skip: 'defina API_URL_TESTE para rodar contra a API real',
    );
    return;
  }

  late RepositorioApi repo;
  late String email;
  const senha = 'Senha@12345';
  final agora = DateTime.now();
  final hoje = DateTime(agora.year, agora.month, agora.day);
  DateTime dia(int delta) => DateTime(hoje.year, hoje.month, hoje.day + delta);

  setUpAll(() async {
    repo = RepositorioApi(
      cliente: ClienteApi(base: Uri.parse(url)),
      fusoHorario: 'America/Sao_Paulo',
    );
    email = 'app${agora.microsecondsSinceEpoch}@exemplo.com';
    await repo.registrar(
      nome: 'Maria da Silva',
      email: email,
      senha: senha,
      nascimento: DateTime(1990, 5, 15),
    );
  });

  test('registro autentica e expõe o usuário', () {
    expect(repo.usuario, isNotNull);
    expect(repo.usuario!.nome, 'Maria da Silva');
    expect(repo.usuario!.email, email);
    expect(repo.usuario!.primeiroNome, 'Maria');
  });

  test(
    'login com senha errada devolve ErroApp com a mensagem da API',
    () async {
      final outro = RepositorioApi(cliente: ClienteApi(base: Uri.parse(url)));
      await expectLater(
        outro.entrar(email, 'errada-demais'),
        throwsA(isA<ErroApp>().having((e) => e.status, 'status', 401)),
      );
      final u = await outro.entrar(email.toUpperCase(), senha);
      expect(u.id, repo.usuario!.id);
    },
  );

  test('e-mail já cadastrado', () async {
    final outro = RepositorioApi(cliente: ClienteApi(base: Uri.parse(url)));
    await expectLater(
      outro.registrar(
        nome: 'Maria da Silva',
        email: email,
        senha: senha,
        nascimento: DateTime(1990, 5, 15),
      ),
      throwsA(isA<ErroApp>().having((e) => e.status, 'status', 409)),
    );
  });

  test('recuperação: e-mail inexistente e código inválido', () async {
    await expectLater(
      repo.solicitarCodigo('nao-existe-${agora.microsecondsSinceEpoch}@x.com'),
      throwsA(isA<ErroApp>().having((e) => e.status, 'status', 404)),
    );
    expect(await repo.solicitarCodigo(email), isNull);
    await expectLater(
      repo.verificarCodigo(email, '00000000'),
      throwsA(isA<ErroApp>()),
    );
  });

  test('atividades: cadastro, listagem, indicadores e conclusão', () async {
    final a = await repo.criarAtividade(
      AtividadeForm(
        nome: 'Estudar para a prova',
        categoria: 'Estudo',
        prioridade: Prioridade.alta,
        data: dia(3),
        inicio: 8 * 60,
        fim: 10 * 60,
        descricao: 'Capítulos 1 a 3 do livro de cálculo diferencial',
      ),
    );
    expect(a.serieId, isNull);
    final b = await repo.criarAtividade(
      AtividadeForm(
        nome: 'Academia',
        categoria: 'Saúde',
        prioridade: Prioridade.media,
        data: dia(3),
        inicio: 9 * 60,
        fim: 10 * 60,
      ),
    );
    final c = await repo.consultarAtividades(FiltroAtividades(data: dia(3)));
    expect(c.total, 2);
    expect(c.pendentes, 2);
    expect(c.minutos, 180);
    expect(c.itens.first.nome, 'Estudar para a prova');
    // Prévia na lista (30 caracteres + reticências) e texto completo no detalhe.
    expect(c.itens.first.previa, 'Capítulos 1 a 3 do livro de cá…');
    final det = await repo.obterAtividade(a.id);
    expect(det.descricao, 'Capítulos 1 a 3 do livro de cálculo diferencial');

    // Sobreposição calculada no cliente (08–10 × 09–10).
    final sobre = await repo.sobreposicoes(dia(3), 9 * 60 + 30, 11 * 60);
    expect(sobre.map((x) => x.id).toSet(), {a.id, b.id});
    expect(await repo.sobreposicoes(dia(3), 10 * 60, 11 * 60), isEmpty);

    final concluida = await repo.alterarConclusaoAtividade(a.id, true);
    expect(concluida.concluida, isTrue);
    final de = await repo.alterarConclusaoAtividade(a.id, true); // idempotente
    expect(de.concluidaEm, isNotNull);
    final so = await repo.consultarAtividades(
      FiltroAtividades(data: dia(3), situacao: SituacaoFiltro.concluidas),
    );
    expect((so.total, so.concluidas, so.pendentes), (1, 1, 0));
    final reaberta = await repo.alterarConclusaoAtividade(a.id, false);
    expect(reaberta.concluida, isFalse);

    await repo.editarAtividade(
      b.id,
      AtividadeForm(
        nome: 'Academia (manhã)',
        categoria: 'Saúde',
        prioridade: Prioridade.baixa,
        data: dia(4),
        inicio: 6 * 60,
        fim: 7 * 60 + 30,
      ),
      EscopoSerie.somenteEsta,
    );
    expect((await repo.obterAtividade(b.id)).data, dia(4));
    await repo.excluirAtividade(b.id, EscopoSerie.somenteEsta);
    await expectLater(repo.obterAtividade(b.id), throwsA(isA<ErroApp>()));
  });

  test('atividades: série semanal e alcance', () async {
    final primeira = await repo.criarAtividade(
      AtividadeForm(
        nome: 'Corrida semanal',
        categoria: 'Saúde',
        prioridade: Prioridade.baixa,
        data: dia(10),
        inicio: 18 * 60,
        fim: 19 * 60,
        periodicidade: Periodicidade.semanal,
        dataFinal: dia(24),
      ),
    );
    expect(primeira.serieId, isNotNull);
    expect(primeira.periodicidade, Periodicidade.semanal);
    for (final d in [10, 17, 24]) {
      final r = await repo.consultarAtividades(FiltroAtividades(data: dia(d)));
      expect(r.itens.map((e) => e.nome), contains('Corrida semanal'));
      expect(r.itens.single.periodicidade, Periodicidade.semanal);
      expect(r.itens.single.serieId, isNotNull); // a lista sabe que repete
    }
    final fora = await repo.consultarAtividades(
      FiltroAtividades(data: dia(31)),
    );
    expect(fora.itens.where((e) => e.nome == 'Corrida semanal'), isEmpty);
    final r17 = await repo.consultarAtividades(FiltroAtividades(data: dia(17)));
    await repo.excluirAtividade(r17.itens.single.id, EscopoSerie.estaEProximas);
    expect(
      (await repo.consultarAtividades(FiltroAtividades(data: dia(24)))).total,
      0,
    );
    expect(
      (await repo.consultarAtividades(FiltroAtividades(data: dia(10)))).total,
      1,
    );
  });

  test('atividades: paginação por deslocamento', () async {
    for (var i = 0; i < 12; i++) {
      await repo.criarAtividade(
        AtividadeForm(
          nome: 'Tarefa número ${i.toString().padLeft(2, '0')}',
          categoria: 'Outros',
          prioridade: Prioridade.baixa,
          data: dia(20),
          inicio: (6 + i) * 60,
          fim: (6 + i) * 60 + 30,
        ),
      );
    }
    final f = FiltroAtividades(data: dia(20));
    final p1 = await repo.consultarAtividades(f, limite: 5);
    expect(p1.itens.length, 5);
    expect(p1.total, 12);
    expect(p1.temMais, isTrue);
    final p2 = await repo.consultarAtividades(f, deslocamento: 5, limite: 5);
    final p3 = await repo.consultarAtividades(f, deslocamento: 10, limite: 5);
    final todos = [...p1.itens, ...p2.itens, ...p3.itens];
    expect(todos.length, 12);
    expect(todos.map((e) => e.id).toSet().length, 12);
    expect(todos.first.nome, 'Tarefa número 00');
    expect(todos.last.nome, 'Tarefa número 11');
    // Um limite grande percorre as páginas (a tela inicial pede 1000).
    final tudo = await repo.consultarAtividades(f, limite: 1000);
    expect(tudo.itens.length, 12);
    // Sem memória de cursor, o deslocamento ainda funciona.
    final outro = RepositorioApi(cliente: ClienteApi(base: Uri.parse(url)));
    await outro.entrar(email, senha);
    final solto = await outro.consultarAtividades(
      f,
      deslocamento: 7,
      limite: 3,
    );
    expect(solto.itens.map((e) => e.nome), [
      'Tarefa número 07',
      'Tarefa número 08',
      'Tarefa número 09',
    ]);
  });

  test('importâncias e financeiro: pagamento vinculado', () async {
    final imp = await repo.criarImportancia(
      ImportanciaForm(
        nome: 'Pagamento da internet',
        categoria: 'Contas',
        data: dia(2),
        horario: 14 * 60 + 30,
        temDespesa: true,
        valorPrevisto: 9990,
        descricao: 'Vivo Fibra',
        lembrete: const Lembrete(diasAntes: 1, horario: 9 * 60),
      ),
    );
    expect(imp.valorPrevisto, 9990);
    expect(imp.lembrete?.diasAntes, 1);
    expect(imp.lembrete?.horario, 540);

    final antes = await repo.resumoMes(hoje.year, hoje.month);
    final prox = await repo.proximasImportancias();
    expect(prox.map((i) => i.id), contains(imp.id));
    expect(
      await repo.totalPendentesDoMes(hoje.year, hoje.month),
      greaterThan(0),
    );

    final despesa = await repo.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Pagamento da internet',
        valor: 10500,
        categoria: 'Contas',
        data: dia(-1),
        forma: 'Pix',
        contraparte: 'Vivo',
        importanciaId: imp.id,
      ),
    );
    expect(despesa.importanciaId, imp.id);
    expect(despesa.valor, 10500);
    expect(despesa.forma, 'Pix');

    final paga = await repo.obterImportancia(imp.id);
    expect(paga.concluida, isTrue);
    expect(paga.paga, isTrue);
    expect(paga.valorPago, 10500);
    expect(paga.valorPrevisto, 9990); // previsão preservada (11.6.3)
    expect(paga.movimentacaoId, despesa.id);
    expect(paga.dataPagamento, dia(-1));

    final depois = await repo.resumoMes(dia(-1).year, dia(-1).month);
    final mesmoMes = dia(-1).month == hoje.month;
    if (mesmoMes) {
      expect(depois.despesas - antes.despesas, 10500);
    }
    // Outro envio com a mesma importância é recusado (11.5.4).
    await expectLater(
      repo.criarMovimentacao(
        MovimentacaoForm(
          tipo: TipoMov.despesa,
          nome: 'Pagamento duplicado',
          valor: 10500,
          categoria: 'Contas',
          data: dia(-1),
          importanciaId: imp.id,
        ),
      ),
      throwsA(isA<ErroApp>().having((e) => e.status, 'status', 409)),
    );

    // Excluir a despesa reabre a importância (7.3.7).
    await repo.excluirMovimentacao(despesa.id);
    final reaberta = await repo.obterImportancia(imp.id);
    expect(reaberta.concluida, isFalse);
    expect(reaberta.valorPago, isNull);
  });

  test('vincular despesa existente não duplica lançamento', () async {
    final imp = await repo.criarImportancia(
      ImportanciaForm(
        nome: 'Seguro do carro',
        categoria: 'Veículo',
        data: dia(5),
        temDespesa: true,
        valorPrevisto: 25000,
      ),
    );
    final m = await repo.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Seguro',
        valor: 24000,
        categoria: 'Veículo',
        data: dia(-2),
      ),
    );
    final livres = await repo.despesasSemVinculo();
    expect(livres.map((x) => x.id), contains(m.id));
    final antes = await repo.consultarMovimentacoes(
      FiltroMov(ano: dia(-2).year, mes: dia(-2).month),
    );
    await repo.vincularDespesa(imp.id, m.id);
    final depois = await repo.consultarMovimentacoes(
      FiltroMov(ano: dia(-2).year, mes: dia(-2).month),
    );
    expect(depois.total, antes.total);
    expect((await repo.obterImportancia(imp.id)).paga, isTrue);
    expect(
      (await repo.despesasSemVinculo()).map((x) => x.id),
      isNot(contains(m.id)),
    );
  });

  test('importâncias: sem despesa, filtros e exclusão', () async {
    final imp = await repo.criarImportancia(
      ImportanciaForm(
        nome: 'Aniversário da mãe',
        categoria: 'Pessoal',
        data: dia(-3),
      ),
    );
    final atrasadas = await repo.consultarImportancias(
      FiltroImportancia.atrasados,
      ano: hoje.year,
      mes: hoje.month,
    );
    expect(atrasadas.map((i) => i.id), contains(imp.id));
    expect(await repo.totalAtrasadas(), greaterThan(0));
    await expectLater(
      repo.alterarConclusaoImportancia(imp.id, true).then((i) => i.concluida),
      completion(isTrue),
    );
    final concl = await repo.consultarImportancias(
      FiltroImportancia.concluidos,
      ano: hoje.year,
      mes: hoje.month,
    );
    expect(concl.map((i) => i.id), contains(imp.id));
    await repo.excluirImportancia(imp.id, EscopoSerie.somenteEsta);
    await expectLater(
      repo.obterImportancia(imp.id),
      throwsA(
        isA<ErroApp>().having(
          (e) => e.mensagem,
          'mensagem',
          'Esta importância não está mais disponível.',
        ),
      ),
    );
  });

  test('importâncias: série anual informa a repetição', () async {
    final imp = await repo.criarImportancia(
      ImportanciaForm(
        nome: 'Licenciamento',
        categoria: 'Veículo',
        data: dia(30),
        periodicidade: Periodicidade.anual,
      ),
    );
    expect(imp.periodicidade, Periodicidade.anual);
    final lista = await repo.consultarImportancias(
      FiltroImportancia.todos,
      ano: hoje.year,
      mes: hoje.month,
    );
    final item = lista.firstWhere((i) => i.id == imp.id);
    expect(item.periodicidade, Periodicidade.anual);
    expect(item.serieId, isNotNull);
  });

  test('financeiro: comparações, categorias, filtros e paginação', () async {
    final mes = DateTime(hoje.year, hoje.month, 1);
    final anterior = DateTime(mes.year, mes.month - 1, 1);
    await repo.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.receita,
        nome: 'Salário',
        valor: 245075,
        categoria: 'Salário',
        data: DateTime(anterior.year, anterior.month, 5),
      ),
    );
    final resumo = await repo.resumoMes(anterior.year, anterior.month);
    expect(resumo.receitas, greaterThanOrEqualTo(245075));
    expect(
      resumo.dias.length,
      DateTime(anterior.year, anterior.month + 1, 0).day,
    );
    expect(resumo.saldo, resumo.receitas - resumo.despesas);
    expect(
      resumo.categorias.fold<int>(0, (s, c) => s + c.total),
      resumo.despesas,
    );
    final d5 = await repo.resumoDia(DateTime(anterior.year, anterior.month, 5));
    expect(d5.receitas, greaterThanOrEqualTo(245075));

    // "Outros" existe em receitas e despesas: sem tipo, as duas aparecem.
    await repo.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.receita,
        nome: 'Presente em dinheiro',
        valor: 1000,
        categoria: 'Outros',
        data: DateTime(anterior.year, anterior.month, 6),
      ),
    );
    await repo.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Gasto diverso',
        valor: 500,
        categoria: 'Outros',
        data: DateTime(anterior.year, anterior.month, 7),
      ),
    );
    final outros = await repo.consultarMovimentacoes(
      FiltroMov(ano: anterior.year, mes: anterior.month, categoria: 'Outros'),
    );
    expect(outros.itens.map((m) => m.nome).toSet(), {
      'Presente em dinheiro',
      'Gasto diverso',
    });
    expect(outros.total, 2);

    for (var i = 0; i < 12; i++) {
      await repo.criarMovimentacao(
        MovimentacaoForm(
          tipo: TipoMov.despesa,
          nome: 'Compra ${i.toString().padLeft(2, '0')}',
          valor: 100 + i,
          categoria: 'Alimentação',
          data: DateTime(anterior.year, anterior.month, 8),
        ),
      );
    }
    final f = FiltroMov(
      ano: anterior.year,
      mes: anterior.month,
      tipo: TipoMov.despesa,
      categoria: 'Alimentação',
    );
    final p1 = await repo.consultarMovimentacoes(f, limite: 5);
    expect((p1.itens.length, p1.total, p1.temMais), (5, 12, true));
    final p2 = await repo.consultarMovimentacoes(f, deslocamento: 5, limite: 5);
    final p3 = await repo.consultarMovimentacoes(
      f,
      deslocamento: 10,
      limite: 5,
    );
    final ids = {
      ...p1.itens,
      ...p2.itens,
      ...p3.itens,
    }.map((m) => m.id).toSet();
    expect(ids.length, 12);
    final busca = await repo.consultarMovimentacoes(
      FiltroMov(ano: anterior.year, mes: anterior.month, busca: 'compra 03'),
    );
    expect(busca.itens.single.nome, 'Compra 03');

    // Editar e excluir.
    final m = busca.itens.single;
    await repo.editarMovimentacao(
      m.id,
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Compra 03 corrigida',
        valor: 7777,
        categoria: 'Transporte',
        data: DateTime(anterior.year, anterior.month, 9),
        forma: 'Cartão de débito',
        descricao: 'Ajustada',
      ),
    );
    final editada = await repo.obterMovimentacao(m.id);
    expect(editada.valor, 7777);
    expect(editada.categoria, 'Transporte');
    expect(editada.forma, 'Cartão de débito');
    expect(editada.descricao, 'Ajustada');
    await repo.excluirMovimentacao(m.id);
    await expectLater(repo.obterMovimentacao(m.id), throwsA(isA<ErroApp>()));
  });

  test('comparação do mês corrente: variação percentual (9.4.5)', () async {
    // Usa um usuário novo para ter bases exatas.
    final r = RepositorioApi(
      cliente: ClienteApi(base: Uri.parse(url)),
      fusoHorario: 'America/Sao_Paulo',
    );
    await r.registrar(
      nome: 'Joana Souza',
      email: 'cmp${agora.microsecondsSinceEpoch}@exemplo.com',
      senha: senha,
      nascimento: DateTime(1985, 1, 20),
    );
    final mes = DateTime(hoje.year, hoje.month, 1);
    final ant = DateTime(mes.year, mes.month - 1, 1);
    await r.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Base anterior',
        valor: 100000,
        categoria: 'Moradia',
        data: ant,
      ),
    );
    await r.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Atual',
        valor: 110000,
        categoria: 'Moradia',
        data: mes,
      ),
    );
    final atual = await r.resumoMes(mes.year, mes.month);
    expect(atual.compDespesas.percentual, 10.0);
    expect(atual.compReceitas.mensagem, 'Sem movimentação nos dois períodos');
    final cres = await r.resumoMes(ant.year, ant.month);
    // O mês anterior não tem mês anterior com dados: "Sem base de comparação".
    expect(cres.compDespesas.mensagem, 'Sem base de comparação');
    final futuro = await r.resumoMes(mes.year + 1, mes.month);
    expect(futuro.compDespesas.percentual, isNull);
    expect(futuro.compDespesas.mensagem, isNull);
  });

  test('edições: importância paga e séries com alcance', () async {
    final imp = await repo.criarImportancia(
      ImportanciaForm(
        nome: 'Internet',
        categoria: 'Contas',
        data: dia(6),
        temDespesa: true,
        valorPrevisto: 9990,
        lembrete: const Lembrete(diasAntes: 3, horario: 9 * 60),
      ),
    );
    await repo.criarMovimentacao(
      MovimentacaoForm(
        tipo: TipoMov.despesa,
        nome: 'Internet',
        valor: 9990,
        categoria: 'Contas',
        data: dia(-1),
        importanciaId: imp.id,
      ),
    );
    // Renomear uma importância paga é permitido; retirar a despesa não.
    ImportanciaForm formDe(Importancia i, {String? nome, bool? despesa}) =>
        ImportanciaForm(
          nome: nome ?? i.nome,
          categoria: i.categoria,
          data: i.data,
          temDespesa: despesa ?? i.temDespesa,
          valorPrevisto: i.valorPrevisto,
          lembrete: i.lembrete,
        );
    final paga = await repo.obterImportancia(imp.id);
    await repo.editarImportancia(
      imp.id,
      formDe(paga, nome: 'Internet fibra'),
      EscopoSerie.somenteEsta,
    );
    expect((await repo.obterImportancia(imp.id)).nome, 'Internet fibra');
    await expectLater(
      repo.editarImportancia(
        imp.id,
        formDe(paga, despesa: false),
        EscopoSerie.somenteEsta,
      ),
      throwsA(isA<ErroApp>().having((e) => e.status, 'status', 409)),
    );

    // Série mensal: "esta e próximas" muda o nome das próximas pendentes.
    final serie = await repo.criarImportancia(
      ImportanciaForm(
        nome: 'Aluguel',
        categoria: 'Contas',
        data: dia(40),
        periodicidade: Periodicidade.mensal,
      ),
    );
    final lista = (await repo.consultarImportancias(
      FiltroImportancia.proximos,
      ano: hoje.year,
      mes: hoje.month,
    )).where((i) => i.serieId == serie.serieId).toList();
    expect(lista.length, greaterThanOrEqualTo(3));
    final segunda = lista[1];
    await repo.editarImportancia(
      segunda.id,
      ImportanciaForm(
        nome: 'Aluguel reajustado',
        categoria: 'Contas',
        data: segunda.data,
      ),
      EscopoSerie.estaEProximas,
    );
    final depois = (await repo.consultarImportancias(
      FiltroImportancia.proximos,
      ano: hoje.year,
      mes: hoje.month,
    )).where((i) => i.serieId == serie.serieId).toList();
    expect(depois.first.nome, 'Aluguel');
    expect(depois.skip(1).map((i) => i.nome).toSet(), {'Aluguel reajustado'});

    // Atividade diária: "esta e próximas" com mudança de horário.
    final a = await repo.criarAtividade(
      AtividadeForm(
        nome: 'Leitura diária',
        categoria: 'Estudo',
        prioridade: Prioridade.baixa,
        data: dia(50),
        inicio: 20 * 60,
        fim: 21 * 60,
        periodicidade: Periodicidade.diaria,
        dataFinal: dia(53),
      ),
    );
    final segundoDia = (await repo.consultarAtividades(
      FiltroAtividades(data: dia(51)),
    )).itens.single;
    await repo.editarAtividade(
      segundoDia.id,
      AtividadeForm(
        nome: 'Leitura diária',
        categoria: 'Estudo',
        prioridade: Prioridade.alta,
        data: segundoDia.data,
        inicio: 21 * 60,
        fim: 22 * 60,
      ),
      EscopoSerie.estaEProximas,
    );
    expect((await repo.obterAtividade(a.id)).inicio, 20 * 60);
    for (final d in [51, 52, 53]) {
      final x = (await repo.consultarAtividades(FiltroAtividades(data: dia(d))))
          .itens
          .single;
      expect((x.inicio, x.prioridade), (21 * 60, Prioridade.alta));
    }
  });

  test('notificações: lista vazia e contador', () async {
    expect(await repo.listarNotificacoes(), isEmpty);
    expect(await repo.totalNaoLidas(), 0);
  });

  test('sessão expirada: token inválido aciona o aviso de saída', () async {
    final r = RepositorioApi(cliente: ClienteApi(base: Uri.parse(url)));
    await r.entrar(email, senha);
    var avisou = false;
    r.aoSessaoExpirada = () => avisou = true;
    r.cliente.token = 'token-invalido';
    await expectLater(
      r.consultarAtividades(FiltroAtividades(data: hoje)),
      throwsA(isA<ErroApp>().having((e) => e.status, 'status', 401)),
    );
    expect(avisou, isTrue);
    expect(r.usuario, isNull);
  });

  test('sem conexão: mensagem amigável', () async {
    final r = RepositorioApi(
      cliente: ClienteApi(
        base: Uri.parse('http://127.0.0.1:1'),
        tempoLimite: const Duration(seconds: 2),
      ),
    );
    await expectLater(
      r.entrar('a@b.com', 'x'),
      throwsA(
        isA<ErroApp>().having(
          (e) => e.mensagem,
          'mensagem',
          mensagemSemConexao,
        ),
      ),
    );
  });
}
