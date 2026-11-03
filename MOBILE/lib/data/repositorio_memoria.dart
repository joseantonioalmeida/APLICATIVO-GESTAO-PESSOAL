import 'dart:math';

import '../core/formatadores.dart';
import '../models/modelos.dart';
import 'repositorio.dart';

/// Implementação local (em memória) do [Repositorio].
///
/// Reproduz as regras de negócio dos requisitos (séries, vínculo de pagamento,
/// comparações, lembretes etc.) para que o aplicativo funcione por completo
/// antes da API existir. Os dados são perdidos ao fechar o aplicativo.
class RepositorioMemoria implements Repositorio {
  RepositorioMemoria({DateTime Function()? relogio, bool demonstracao = true})
    : _relogio = relogio ?? DateTime.now {
    if (demonstracao) _semear();
  }

  final DateTime Function() _relogio;
  final _rng = Random();
  int _seq = 0;

  final Map<String, _Conta> _contas = {};
  _Conta? _logada;
  final Map<String, _Recuperacao> _recuperacoes = {};

  DateTime get _agora => _relogio();
  DateTime get _hoje => Fmt.somenteData(_agora);

  String _novoId(String prefixo) => '$prefixo-${++_seq}';
  DateTime _carimbo() => _agora.add(Duration(microseconds: ++_seq));

  _Dados get _d {
    final c = _logada;
    if (c == null) throw const ErroApp('Sua sessão expirou. Entre novamente.');
    return c.dados;
  }

  static String _normalizaEmail(String e) => e.trim().toLowerCase();

  // =================================================================== Conta
  @override
  Usuario? get usuario => _logada?.usuario;

  @override
  Future<Usuario> entrar(String email, String senha) async {
    final c = _contas[_normalizaEmail(email)];
    if (c == null || c.senha != senha) {
      throw const ErroApp('E-mail ou senha incorretos.');
    }
    _logada = c;
    return c.usuario;
  }

  @override
  Future<Usuario> registrar({
    required String nome,
    required String email,
    required String senha,
    required DateTime nascimento,
  }) async {
    final chave = _normalizaEmail(email);
    if (_contas.containsKey(chave)) {
      throw const ErroApp('Este e-mail já está cadastrado.', campo: 'email');
    }
    final u = Usuario(
      id: _novoId('u'),
      nome: nome.trim(),
      email: chave,
      nascimento: nascimento,
    );
    final c = _Conta(u, senha);
    _contas[chave] = c;
    _logada = c;
    return u;
  }

  @override
  void sair() => _logada = null;

  @override
  Future<String?> solicitarCodigo(String email) async {
    final chave = _normalizaEmail(email);
    final c = _contas[chave];
    if (c == null) {
      throw const ErroApp('Não foi possível encontrar seu email.');
    }
    final codigo = List.generate(
      8,
      (_) => _rng.nextInt(10),
    ).join(); // pode começar com 0
    _recuperacoes[chave] = _Recuperacao(
      codigo,
      _agora.add(const Duration(minutes: 10)),
    );
    return codigo; // modo demonstração: não há envio real de e-mail
  }

  @override
  Future<String> verificarCodigo(String email, String codigo) async {
    const invalido = ErroApp(
      'O código de verificação que você inseriu não é válido. '
      'Verifique o código e tente novamente.',
    );
    final r = _recuperacoes[_normalizaEmail(email)];
    if (r == null || _agora.isAfter(r.expiraEm) || r.tentativas >= 5) {
      throw invalido;
    }
    if (r.codigo != codigo) {
      r.tentativas++;
      throw invalido;
    }
    r.token = 'tok-${_rng.nextInt(1 << 31)}-${++_seq}';
    return r.token!;
  }

  @override
  Future<void> redefinirSenha({
    required String email,
    required String token,
    required String novaSenha,
  }) async {
    final chave = _normalizaEmail(email);
    final r = _recuperacoes[chave];
    if (r == null || r.token != token || _agora.isAfter(r.expiraEm)) {
      throw const ErroApp('Sua solicitação expirou. Peça um novo código.');
    }
    if (novaSenha.length < 8) {
      throw const ErroApp(
        'A senha informada não atende os requisitos necessários de 8 caracteres',
      );
    }
    _contas[chave]!.senha = novaSenha;
    _recuperacoes.remove(chave); // token de uso único
  }

  // =========================================================== Recorrências
  static int _ultimoDia(int ano, int mes) => DateTime(ano, mes + 1, 0).day;

  /// Gera as datas de uma série. Mensal/anual preservam o dia original,
  /// usando o último dia do mês quando o dia não existe.
  List<DateTime> _datasDaSerie(
    DateTime inicio,
    Periodicidade p,
    DateTime? fim,
  ) {
    if (p == Periodicidade.nenhuma) return [inicio];
    final limite = switch (p) {
      Periodicidade.diaria => 90,
      Periodicidade.semanal => 52,
      Periodicidade.mensal => 24,
      _ => 10,
    };
    final datas = <DateTime>[];
    for (var k = 0; k < limite; k++) {
      final DateTime d = switch (p) {
        Periodicidade.diaria => DateTime(
          inicio.year,
          inicio.month,
          inicio.day + k,
        ),
        Periodicidade.semanal => DateTime(
          inicio.year,
          inicio.month,
          inicio.day + 7 * k,
        ),
        Periodicidade.mensal => () {
          final m0 = inicio.month - 1 + k;
          final ano = inicio.year + m0 ~/ 12;
          final mes = m0 % 12 + 1;
          return DateTime(ano, mes, min(inicio.day, _ultimoDia(ano, mes)));
        }(),
        _ => () {
          final ano = inicio.year + k;
          return DateTime(
            ano,
            inicio.month,
            min(inicio.day, _ultimoDia(ano, inicio.month)),
          );
        }(),
      };
      if (fim != null && d.isAfter(fim)) break;
      datas.add(d);
    }
    return datas;
  }

  // ============================================================== Atividades
  @override
  Future<ConsultaAtividades> consultarAtividades(
    FiltroAtividades f, {
    int deslocamento = 0,
    int limite = 10,
  }) async {
    final busca = f.busca.trim().toLowerCase();
    final lista = _d.atividades.where((a) {
      if (a.excluida || !Fmt.mesmoDia(a.data, f.data)) return false;
      if (f.categoria != null && a.categoria != f.categoria) return false;
      if (f.prioridade != null && a.prioridade != f.prioridade) return false;
      if (f.situacao == SituacaoFiltro.pendentes && a.concluida) return false;
      if (f.situacao == SituacaoFiltro.concluidas && !a.concluida) return false;
      if (busca.isNotEmpty && !a.nome.toLowerCase().contains(busca)) {
        return false;
      }
      return true;
    }).toList();

    final indice = {
      for (var i = 0; i < _d.atividades.length; i++) _d.atividades[i].id: i,
    };
    int porIndice(Atividade a, Atividade b) =>
        indice[a.id]!.compareTo(indice[b.id]!);
    lista.sort((a, b) {
      int c;
      switch (f.ordem) {
        case OrdemAtividade.horario:
          c = a.inicio.compareTo(b.inicio);
        case OrdemAtividade.prioridade:
          c = b.prioridade.index.compareTo(a.prioridade.index);
          if (c == 0) c = a.inicio.compareTo(b.inicio);
        case OrdemAtividade.recentes:
          c = b.criadoEm.compareTo(a.criadoEm);
      }
      return c != 0 ? c : porIndice(a, b);
    });

    final concluidas = lista.where((a) => a.concluida).length;
    final minutos = lista.fold<int>(0, (s, a) => s + a.duracaoMin);
    final fim = min(lista.length, deslocamento + limite);
    final pagina = lista.sublist(min(deslocamento, lista.length), fim);
    return ConsultaAtividades(
      itens: pagina.map((a) => a.copia()).toList(),
      total: lista.length,
      concluidas: concluidas,
      pendentes: lista.length - concluidas,
      minutos: minutos,
    );
  }

  @override
  Future<PendenciasAnteriores> pendenciasAnteriores() async {
    final antigas = _d.atividades
        .where((a) => !a.excluida && !a.concluida && a.data.isBefore(_hoje))
        .toList();
    if (antigas.isEmpty) return const PendenciasAnteriores(quantidade: 0);
    final menor = antigas
        .map((a) => a.data)
        .reduce((a, b) => a.isBefore(b) ? a : b);
    return PendenciasAnteriores(quantidade: antigas.length, maisAntiga: menor);
  }

  Atividade _atv(String id) {
    final a = _d.atividades.where((a) => a.id == id && !a.excluida).firstOrNull;
    if (a == null) throw const ErroApp('Atividade não encontrada.');
    return a;
  }

  @override
  Future<Atividade> obterAtividade(String id) async => _atv(id).copia();

  @override
  Future<List<Atividade>> sobreposicoes(
    DateTime data,
    int inicio,
    int fim, {
    String? ignorarId,
  }) async {
    return _d.atividades
        .where(
          (a) =>
              !a.excluida &&
              a.id != ignorarId &&
              Fmt.mesmoDia(a.data, data) &&
              a.inicio < fim &&
              inicio < a.fim,
        )
        .map((a) => a.copia())
        .toList();
  }

  @override
  Future<Atividade> criarAtividade(AtividadeForm f) async {
    final datas = _datasDaSerie(f.data, f.periodicidade, f.dataFinal);
    final serie = f.periodicidade == Periodicidade.nenhuma
        ? null
        : _novoId('sa');
    Atividade? primeira;
    for (var i = 0; i < datas.length; i++) {
      final a = Atividade(
        id: _novoId('a'),
        nome: f.nome.trim(),
        categoria: f.categoria,
        prioridade: f.prioridade,
        data: datas[i],
        inicio: f.inicio,
        fim: f.fim,
        criadoEm: _carimbo(),
        descricao: f.descricao.trim(),
        serieId: serie,
        numero: serie == null ? null : i + 1,
        periodicidade: f.periodicidade,
      );
      _d.atividades.add(a);
      primeira ??= a;
    }
    return primeira!.copia();
  }

  /// Ocorrências afetadas por uma edição/exclusão conforme o alcance.
  List<Atividade> _alvosAtividade(Atividade alvo, EscopoSerie escopo) {
    if (alvo.serieId == null ||
        escopo == EscopoSerie.somenteEsta ||
        alvo.concluida) {
      return [alvo];
    }
    return _d.atividades
        .where(
          (a) =>
              !a.excluida &&
              a.serieId == alvo.serieId &&
              !a.concluida &&
              a.numero! >= alvo.numero!,
        )
        .toList();
  }

  @override
  Future<void> editarAtividade(
    String id,
    AtividadeForm f,
    EscopoSerie escopo,
  ) async {
    final alvo = _atv(id);
    final delta = Fmt.diasEntre(alvo.data, f.data);
    for (final a in _alvosAtividade(alvo, escopo)) {
      a.nome = f.nome.trim();
      a.categoria = f.categoria;
      a.prioridade = f.prioridade;
      a.inicio = f.inicio;
      a.fim = f.fim;
      a.descricao = f.descricao.trim();
      a.data = DateTime(a.data.year, a.data.month, a.data.day + delta);
    }
  }

  @override
  Future<void> excluirAtividade(String id, EscopoSerie escopo) async {
    final alvo = _atv(id);
    for (final a in _alvosAtividade(alvo, escopo)) {
      a.excluida = true;
    }
  }

  @override
  Future<Atividade> alterarConclusaoAtividade(String id, bool concluida) async {
    final a = _atv(id);
    if (concluida) {
      a.concluidaEm ??= _agora;
    } else {
      a.concluidaEm = null;
    }
    return a.copia();
  }

  // ========================================================== Importâncias
  Importancia _imp(String id) {
    final i = _d.importancias
        .where((i) => i.id == id && !i.excluida)
        .firstOrNull;
    if (i == null) {
      throw const ErroApp('Esta importância não está mais disponível.');
    }
    return i;
  }

  static int _cmpPendentes(Importancia a, Importancia b) {
    final c = a.data.compareTo(b.data);
    if (c != 0) return c;
    if (a.horario == null && b.horario == null) return 0;
    if (a.horario == null) return 1;
    if (b.horario == null) return -1;
    return a.horario!.compareTo(b.horario!);
  }

  @override
  Future<List<Importancia>> consultarImportancias(
    FiltroImportancia filtro, {
    required int ano,
    required int mes,
    String busca = '',
  }) async {
    final hoje = _hoje;
    final b = busca.trim().toLowerCase();
    final lista = _d.importancias.where((i) {
      if (i.excluida) return false;
      if (b.isNotEmpty && !i.nome.toLowerCase().contains(b)) return false;
      switch (filtro) {
        case FiltroImportancia.todos:
          return true;
        case FiltroImportancia.hoje:
          return !i.concluida && Fmt.mesmoDia(i.data, hoje);
        case FiltroImportancia.mes:
          return i.data.year == ano && i.data.month == mes;
        case FiltroImportancia.proximos:
          return !i.concluida && i.data.isAfter(hoje);
        case FiltroImportancia.concluidos:
          return i.concluida;
        case FiltroImportancia.atrasados:
          return !i.concluida && i.data.isBefore(hoje);
      }
    }).toList();
    final pend = lista.where((i) => !i.concluida).toList()..sort(_cmpPendentes);
    final conc = lista.where((i) => i.concluida).toList()
      ..sort((a, b) => b.concluidaEm!.compareTo(a.concluidaEm!));
    return [...pend, ...conc].map(_comPagamento).toList();
  }

  @override
  Future<List<Importancia>> proximasImportancias({int limite = 3}) async {
    final hoje = _hoje;
    final l =
        _d.importancias
            .where((i) => !i.excluida && !i.concluida && !i.data.isBefore(hoje))
            .toList()
          ..sort(_cmpPendentes);
    return l.take(limite).map(_comPagamento).toList();
  }

  @override
  Future<int> totalAtrasadas() async => _d.importancias
      .where((i) => !i.excluida && !i.concluida && i.data.isBefore(_hoje))
      .length;

  @override
  Future<int> totalPendentesDoMes(int ano, int mes) async => _d.importancias
      .where(
        (i) =>
            !i.excluida &&
            !i.concluida &&
            i.data.year == ano &&
            i.data.month == mes,
      )
      .length;

  @override
  Future<Importancia> obterImportancia(String id) async =>
      _comPagamento(_imp(id));

  /// Cópia da importância com o valor e a data do pagamento vinculado.
  Importancia _comPagamento(Importancia i) {
    final c = i.copia();
    final mid = i.movimentacaoId;
    if (mid != null) {
      final m = _d.movs.where((m) => m.id == mid).firstOrNull;
      c.valorPago = m?.valor;
      c.dataPagamento = m?.data;
    }
    return c;
  }

  @override
  Future<Importancia> criarImportancia(ImportanciaForm f) async {
    final datas = _datasDaSerie(f.data, f.periodicidade, f.dataFinal);
    final serie = f.periodicidade == Periodicidade.nenhuma
        ? null
        : _novoId('si');
    Importancia? primeira;
    for (var i = 0; i < datas.length; i++) {
      final imp = Importancia(
        id: _novoId('i'),
        nome: f.nome.trim(),
        categoria: f.categoria,
        data: datas[i],
        criadoEm: _carimbo(),
        horario: f.horario,
        temDespesa: f.temDespesa,
        valorPrevisto: f.temDespesa ? f.valorPrevisto : 0,
        descricao: f.descricao.trim(),
        serieId: serie,
        numero: serie == null ? null : i + 1,
        periodicidade: f.periodicidade,
        lembrete: f.lembrete,
      );
      _d.importancias.add(imp);
      primeira ??= imp;
    }
    return primeira!.copia();
  }

  List<Importancia> _alvosImportancia(Importancia alvo, EscopoSerie escopo) {
    if (alvo.serieId == null ||
        escopo == EscopoSerie.somenteEsta ||
        alvo.concluida) {
      return [alvo];
    }
    return _d.importancias
        .where(
          (i) =>
              !i.excluida &&
              i.serieId == alvo.serieId &&
              !i.concluida &&
              i.numero! >= alvo.numero!,
        )
        .toList();
  }

  @override
  Future<void> editarImportancia(
    String id,
    ImportanciaForm f,
    EscopoSerie escopo,
  ) async {
    final alvo = _imp(id);
    if (alvo.paga && !f.temDespesa) {
      throw const ErroApp(
        'Esta importância já possui pagamento vinculado. Use “Ver despesa” para alterá-lo.',
      );
    }
    final delta = Fmt.diasEntre(alvo.data, f.data);
    for (final i in _alvosImportancia(alvo, escopo)) {
      i.nome = f.nome.trim();
      i.categoria = f.categoria;
      i.descricao = f.descricao.trim();
      i.horario = f.horario;
      i.lembrete = f.lembrete;
      i.temDespesa = f.temDespesa;
      i.valorPrevisto = f.temDespesa ? f.valorPrevisto : 0;
      i.data = DateTime(i.data.year, i.data.month, i.data.day + delta);
    }
  }

  @override
  Future<void> excluirImportancia(String id, EscopoSerie escopo) async {
    final alvo = _imp(id);
    for (final i in _alvosImportancia(alvo, escopo)) {
      i.excluida = true;
      // A despesa já registrada é preservada, apenas sem vínculo ativo.
      final mid = i.movimentacaoId;
      if (mid != null) {
        _d.movs.where((m) => m.id == mid).firstOrNull?.importanciaId = null;
        i.movimentacaoId = null;
      }
    }
  }

  @override
  Future<Importancia> alterarConclusaoImportancia(
    String id,
    bool concluida,
  ) async {
    final i = _imp(id);
    if (i.temDespesa) {
      throw const ErroApp(
        'Importâncias com despesa são concluídas ao registrar o pagamento.',
      );
    }
    if (concluida) {
      i.concluidaEm ??= _agora;
    } else {
      i.concluidaEm = null;
    }
    return i.copia();
  }

  @override
  Future<List<Movimentacao>> despesasSemVinculo({String busca = ''}) async {
    final b = busca.trim().toLowerCase();
    final l =
        _d.movs
            .where(
              (m) =>
                  m.tipo == TipoMov.despesa &&
                  m.importanciaId == null &&
                  (b.isEmpty || m.nome.toLowerCase().contains(b)),
            )
            .toList()
          ..sort((a, b) => b.data.compareTo(a.data));
    return l;
  }

  @override
  Future<void> vincularDespesa(
    String importanciaId,
    String movimentacaoId,
  ) async {
    final i = _imp(importanciaId);
    final m = _d.movs.where((m) => m.id == movimentacaoId).firstOrNull;
    if (m == null || m.tipo != TipoMov.despesa) {
      throw const ErroApp('Despesa não encontrada.');
    }
    if (i.paga || m.importanciaId != null || i.concluida || !i.temDespesa) {
      throw const ErroApp('Esta importância já possui um pagamento registrado');
    }
    i.movimentacaoId = m.id;
    i.concluidaEm = _agora;
    m.importanciaId = i.id;
  }

  // ============================================================ Financeiro
  List<Movimentacao> _movsDoPeriodo(DateTime ini, DateTime fim) => _d.movs
      .where((m) => !m.data.isBefore(ini) && !m.data.isAfter(fim))
      .toList();

  static int _soma(Iterable<Movimentacao> l, TipoMov t) =>
      l.where((m) => m.tipo == t).fold(0, (s, m) => s + m.valor);

  Comparacao _comparar(int atual, int anterior, String intervalo) {
    if (anterior > 0) {
      final v = ((atual - anterior) / anterior) * 100;
      return Comparacao(
        percentual: (v * 10).round() / 10,
        intervalo: intervalo,
      );
    }
    if (atual > 0) {
      return Comparacao(
        mensagem: 'Sem base de comparação',
        intervalo: intervalo,
      );
    }
    return Comparacao(
      mensagem: 'Sem movimentação nos dois períodos',
      intervalo: intervalo,
    );
  }

  @override
  Future<ResumoFinanceiro> resumoMes(int ano, int mes) async {
    final ini = DateTime(ano, mes, 1);
    final ultimo = _ultimoDia(ano, mes);
    final fim = DateTime(ano, mes, ultimo);
    final doMes = _movsDoPeriodo(ini, fim);
    final receitas = _soma(doMes, TipoMov.receita);
    final despesas = _soma(doMes, TipoMov.despesa);

    // Período de comparação (9.2.6).
    final hoje = _hoje;
    final atualEhMesCorrente = hoje.year == ano && hoje.month == mes;
    final futuro = DateTime(ano, mes).isAfter(DateTime(hoje.year, hoje.month));
    final ant = DateTime(ano, mes - 1, 1);
    final ultAnt = _ultimoDia(ant.year, ant.month);
    var diaFimAtual = ultimo;
    var diaFimAnt = ultAnt;
    if (atualEhMesCorrente) {
      diaFimAtual = hoje.day;
      diaFimAnt = min(hoje.day, ultAnt);
    }
    Comparacao cReceitas = const Comparacao();
    Comparacao cDespesas = const Comparacao();
    if (!futuro) {
      final atualP = _movsDoPeriodo(ini, DateTime(ano, mes, diaFimAtual));
      final antP = _movsDoPeriodo(
        ant,
        DateTime(ant.year, ant.month, diaFimAnt),
      );
      final intervalo =
          '01–${diaFimAnt.toString().padLeft(2, '0')}/${ant.month.toString().padLeft(2, '0')}';
      cReceitas = _comparar(
        _soma(atualP, TipoMov.receita),
        _soma(antP, TipoMov.receita),
        intervalo,
      );
      cDespesas = _comparar(
        _soma(atualP, TipoMov.despesa),
        _soma(antP, TipoMov.despesa),
        intervalo,
      );
    }

    final dias = List.generate(ultimo, (i) {
      final d = i + 1;
      final doDia = doMes.where((m) => m.data.day == d);
      return DiaFinanceiro(
        d,
        _soma(doDia, TipoMov.receita),
        _soma(doDia, TipoMov.despesa),
      );
    });

    final porCategoria = <String, int>{};
    for (final m in doMes.where((m) => m.tipo == TipoMov.despesa)) {
      porCategoria[m.categoria] = (porCategoria[m.categoria] ?? 0) + m.valor;
    }
    final cats =
        porCategoria.entries.map((e) => CategoriaTotal(e.key, e.value)).toList()
          ..sort((a, b) => b.total.compareTo(a.total));

    return ResumoFinanceiro(
      ano: ano,
      mes: mes,
      receitas: receitas,
      despesas: despesas,
      compReceitas: cReceitas,
      compDespesas: cDespesas,
      dias: dias,
      categorias: cats,
    );
  }

  @override
  Future<ResumoDia> resumoDia(DateTime dia) async {
    final l = _movsDoPeriodo(dia, dia);
    return ResumoDia(
      receitas: _soma(l, TipoMov.receita),
      despesas: _soma(l, TipoMov.despesa),
    );
  }

  @override
  Future<ConsultaMov> consultarMovimentacoes(
    FiltroMov f, {
    int deslocamento = 0,
    int limite = 10,
  }) async {
    final busca = f.busca.trim().toLowerCase();
    final l =
        _d.movs.where((m) {
          if (m.data.year != f.ano || m.data.month != f.mes) return false;
          if (f.tipo != null && m.tipo != f.tipo) return false;
          if (f.categoria != null && m.categoria != f.categoria) return false;
          if (busca.isNotEmpty && !m.nome.toLowerCase().contains(busca)) {
            return false;
          }
          return true;
        }).toList()..sort((a, b) {
          final c = b.data.compareTo(a.data);
          return c != 0 ? c : b.criadoEm.compareTo(a.criadoEm);
        });
    final ini = min(deslocamento, l.length);
    return ConsultaMov(
      itens: l.sublist(ini, min(l.length, ini + limite)),
      total: l.length,
    );
  }

  @override
  Future<Movimentacao> obterMovimentacao(String id) async {
    final m = _d.movs.where((m) => m.id == id).firstOrNull;
    if (m == null) throw const ErroApp('Lançamento não encontrado.');
    return m;
  }

  void _validaDataMov(MovimentacaoForm f) {
    if (f.data.isAfter(_hoje)) {
      throw ErroApp(
        f.tipo == TipoMov.receita
            ? 'A data do recebimento não pode ser futura'
            : 'A data do pagamento não pode ser futura. Cadastre o compromisso em Importâncias',
        campo: 'data',
      );
    }
  }

  @override
  Future<Movimentacao> criarMovimentacao(MovimentacaoForm f) async {
    _validaDataMov(f);
    Importancia? imp;
    if (f.importanciaId != null) {
      imp = _imp(f.importanciaId!);
      if (imp.paga || imp.concluida || !imp.temDespesa) {
        throw const ErroApp(
          'Esta importância já possui um pagamento registrado',
        );
      }
    }
    final m = Movimentacao(
      id: _novoId('m'),
      tipo: f.tipo,
      nome: f.nome.trim(),
      valor: f.valor,
      categoria: f.categoria,
      data: f.data,
      criadoEm: _carimbo(),
      descricao: f.descricao.trim(),
      contraparte: f.contraparte.trim(),
      forma: f.forma,
      importanciaId: imp?.id,
    );
    _d.movs.add(m);
    if (imp != null) {
      imp.movimentacaoId = m.id;
      imp.concluidaEm = _agora;
    }
    return m;
  }

  @override
  Future<void> editarMovimentacao(String id, MovimentacaoForm f) async {
    final m = await obterMovimentacao(id);
    _validaDataMov(f);
    m
      ..nome = f.nome.trim()
      ..valor = f.valor
      ..categoria = f.categoria
      ..data = f.data
      ..descricao = f.descricao.trim()
      ..contraparte = f.contraparte.trim()
      ..forma = f.forma;
  }

  @override
  Future<void> excluirMovimentacao(String id) async {
    final m = await obterMovimentacao(id);
    final iid = m.importanciaId;
    if (iid != null) {
      final imp = _d.importancias.where((i) => i.id == iid).firstOrNull;
      if (imp != null) {
        imp.movimentacaoId = null;
        imp.concluidaEm = null;
      }
    }
    _d.movs.remove(m);
  }

  // ========================================================== Notificações
  DateTime _momentoLembrete(Importancia i) {
    final l = i.lembrete!;
    final dia = DateTime(i.data.year, i.data.month, i.data.day - l.diasAntes);
    return DateTime(
      dia.year,
      dia.month,
      dia.day,
      l.horario ~/ 60,
      l.horario % 60,
    );
  }

  @override
  Future<List<Notificacao>> listarNotificacoes() async {
    final agora = _agora;
    final l = <Notificacao>[];
    for (final i in _d.importancias) {
      if (i.excluida || i.concluida || i.lembrete == null) continue;
      final quando = _momentoLembrete(i);
      if (quando.isAfter(agora)) continue;
      final dias = Fmt.diasEntre(_hoje, i.data);
      final prazo = dias == 0
          ? 'vence hoje'
          : dias == 1
          ? 'vence amanhã'
          : dias > 1
          ? 'vence em $dias dias'
          : 'está atrasada há ${-dias} dias';
      l.add(
        Notificacao(
          id: 'n-${i.id}',
          importanciaId: i.id,
          titulo: i.nome,
          mensagem: 'Lembrete: $prazo (${Fmt.data(i.data)}).',
          geradaEm: quando,
          lida: _d.lidas.contains('n-${i.id}'),
        ),
      );
    }
    l.sort((a, b) => b.geradaEm.compareTo(a.geradaEm));
    return l;
  }

  @override
  Future<int> totalNaoLidas() async =>
      (await listarNotificacoes()).where((n) => !n.lida).length;

  @override
  Future<void> marcarNotificacaoLida(String id) async => _d.lidas.add(id);

  // =============================================================== Demonstração
  void _semear() {
    final hoje = _hoje;
    final conta = _Conta(
      Usuario(
        id: 'u-demo',
        nome: 'Júlio Cesar',
        email: 'julio@email.com',
        nascimento: DateTime(1990, 5, 15),
      ),
      'Senha@123',
    );
    _contas[conta.usuario.email] = conta;
    final d = conta.dados;
    DateTime dia(int atras) =>
        DateTime(hoje.year, hoje.month, hoje.day - atras);
    // Datas de lançamentos financeiros ficam sempre dentro do mês corrente.
    DateTime noMes(int atras) {
      final x = dia(atras);
      return x.month == hoje.month ? x : DateTime(hoje.year, hoje.month, 1);
    }

    // ---- Atividades de hoje (6) + pendências de dias anteriores (2)
    Atividade atv(
      String nome,
      String cat,
      Prioridade p,
      DateTime data,
      int ini,
      int fim, {
      String desc = '',
      bool concluida = false,
      Periodicidade per = Periodicidade.nenhuma,
    }) {
      final a = Atividade(
        id: _novoId('a'),
        nome: nome,
        categoria: cat,
        prioridade: p,
        data: data,
        inicio: ini * 60,
        fim: fim * 60,
        criadoEm: _carimbo(),
        descricao: desc,
        periodicidade: per,
        concluidaEm: concluida ? _agora : null,
      );
      d.atividades.add(a);
      return a;
    }

    atv(
      'Estudar para a prova',
      'Estudo',
      Prioridade.alta,
      hoje,
      8,
      10,
      desc: 'Revisar capítulos 3 a 5 do livro',
      concluida: true,
    );
    _atvSerie(
      d,
      'Almoço',
      'Pessoal',
      Prioridade.baixa,
      hoje,
      12 * 60,
      13 * 60,
      Periodicidade.diaria,
      concluirPrimeira: true,
    );
    atv(
      'Trabalho (projeto)',
      'Trabalho',
      Prioridade.alta,
      hoje,
      13,
      16,
      desc: 'Finalizar módulo de relatórios',
      concluida: true,
    );
    _atvSerie(
      d,
      'Treino na academia',
      'Saúde',
      Prioridade.media,
      hoje,
      17 * 60,
      18 * 60 + 30,
      Periodicidade.semanal,
      concluirPrimeira: true,
    );
    atv(
      'Ler um livro',
      'Lazer',
      Prioridade.baixa,
      hoje,
      20,
      21,
      desc: 'Capítulo 4 do livro de ficção científica',
    ).fim = 21 * 60 + 30;
    atv('Jogar um pouco', 'Lazer', Prioridade.baixa, hoje, 22, 23).fim =
        23 * 60 + 30;
    atv(
      'Fechar planilha de gastos',
      'Pessoal',
      Prioridade.media,
      dia(1),
      9,
      10,
    );
    atv(
      'Enviar relatório semanal',
      'Trabalho',
      Prioridade.alta,
      dia(2),
      14,
      15,
    );

    // ---- Movimentações do mês corrente
    Movimentacao mov(
      TipoMov t,
      String nome,
      int cents,
      String cat,
      DateTime data, {
      String contra = '',
      String? forma,
    }) {
      final m = Movimentacao(
        id: _novoId('m'),
        tipo: t,
        nome: nome,
        valor: cents,
        categoria: cat,
        data: data,
        criadoEm: _carimbo(),
        contraparte: contra,
        forma: forma,
      );
      d.movs.add(m);
      return m;
    }

    mov(
      TipoMov.despesa,
      'Aluguel',
      60000,
      'Moradia',
      noMes(20),
      contra: 'Imobiliária Central',
      forma: 'Boleto',
    );
    final luz = mov(
      TipoMov.despesa,
      'Conta de luz',
      15234,
      'Contas',
      noMes(19),
      contra: 'Energisa',
      forma: 'Pix',
    );
    mov(
      TipoMov.despesa,
      'Farmácia',
      8990,
      'Saúde',
      noMes(15),
      contra: 'Drogaria Bem Estar',
      forma: 'Cartão de débito',
    );
    mov(
      TipoMov.despesa,
      'Padaria',
      2046,
      'Alimentação',
      noMes(9),
      contra: 'Padaria Pão Quente',
    );
    mov(TipoMov.despesa, 'Uber', 3250, 'Transporte', noMes(3), forma: 'Pix');
    mov(TipoMov.despesa, 'Restaurante', 8990, 'Alimentação', noMes(2));
    mov(
      TipoMov.despesa,
      'Mercado',
      24530,
      'Alimentação',
      noMes(1),
      contra: 'Mercado Central',
    );
    mov(
      TipoMov.receita,
      'Salário',
      245075,
      'Salário',
      hoje,
      contra: 'Empresa XYZ',
      forma: 'Transferência',
    );

    // ---- Mês anterior (base da comparação: +12,0% receitas / +8,0% despesas)
    final ant = DateTime(hoje.year, hoje.month - 1, 1);
    DateTime noAnt(int diaMes) => DateTime(
      ant.year,
      ant.month,
      min(diaMes, _ultimoDia(ant.year, ant.month)),
    );
    mov(TipoMov.receita, 'Salário', 218817, 'Salário', noAnt(1));
    mov(TipoMov.despesa, 'Aluguel', 60000, 'Moradia', noAnt(1));
    mov(TipoMov.despesa, 'Mercado', 53926, 'Alimentação', noAnt(2));

    // ---- Importâncias
    Importancia imp(
      String nome,
      String cat,
      DateTime data, {
      int? horario,
      int? valor,
      String desc = '',
      Periodicidade per = Periodicidade.nenhuma,
      Lembrete? lembrete,
      bool concluida = false,
    }) {
      final i = Importancia(
        id: _novoId('i'),
        nome: nome,
        categoria: cat,
        data: data,
        criadoEm: _carimbo(),
        horario: horario,
        temDespesa: valor != null,
        valorPrevisto: valor ?? 0,
        descricao: desc,
        periodicidade: per,
        lembrete: lembrete,
        concluidaEm: concluida ? _agora : null,
        serieId: per == Periodicidade.nenhuma ? null : _novoId('si'),
        numero: per == Periodicidade.nenhuma ? null : 1,
      );
      d.importancias.add(i);
      return i;
    }

    imp(
      'Fatura do cartão',
      'Contas',
      dia(4),
      valor: 48000,
      desc: 'Cartão de crédito',
    );
    imp(
      'Pagamento da internet',
      'Contas',
      hoje,
      horario: 8 * 60,
      valor: 9990,
      desc: 'Vivo Fibra',
      lembrete: const Lembrete(diasAntes: 1, horario: 9 * 60),
    );
    imp('Compra do mês', 'Compras', dia(-6), valor: 24530, desc: 'Mercado');
    imp('Aniversário da mãe', 'Pessoal', dia(-13), per: Periodicidade.anual);
    imp(
      'Licenciamento do veículo',
      'Veículo',
      dia(-16),
      valor: 12000,
      desc: 'Detran',
    );
    imp(
      'Assinatura do streaming',
      'Lazer',
      dia(-21),
      valor: 3990,
      desc: 'Netflix',
      per: Periodicidade.mensal,
    );
    final pago = imp(
      'Conta de luz',
      'Contas',
      noMes(19),
      valor: 15234,
      desc: 'Energisa',
      per: Periodicidade.mensal,
      concluida: true,
    );
    pago.movimentacaoId = luz.id;
    luz.importanciaId = pago.id;
    imp('Mensalidade da academia', 'Saúde', dia(12), concluida: true);
  }

  void _atvSerie(
    _Dados d,
    String nome,
    String cat,
    Prioridade p,
    DateTime ini,
    int hIni,
    int hFim,
    Periodicidade per, {
    bool concluirPrimeira = false,
  }) {
    final serie = _novoId('sa');
    final datas = _datasDaSerie(ini, per, null).take(8).toList();
    for (var k = 0; k < datas.length; k++) {
      d.atividades.add(
        Atividade(
          id: _novoId('a'),
          nome: nome,
          categoria: cat,
          prioridade: p,
          data: datas[k],
          inicio: hIni,
          fim: hFim,
          criadoEm: _carimbo(),
          serieId: serie,
          numero: k + 1,
          periodicidade: per,
          concluidaEm: concluirPrimeira && k == 0 ? _agora : null,
        ),
      );
    }
  }
}

class _Conta {
  _Conta(this.usuario, this.senha);
  final Usuario usuario;
  String senha;
  final dados = _Dados();
}

class _Dados {
  final atividades = <Atividade>[];
  final importancias = <Importancia>[];
  final movs = <Movimentacao>[];
  final lidas = <String>{};
}

class _Recuperacao {
  _Recuperacao(this.codigo, this.expiraEm);
  final String codigo;
  final DateTime expiraEm;
  int tentativas = 0;
  String? token;
}
