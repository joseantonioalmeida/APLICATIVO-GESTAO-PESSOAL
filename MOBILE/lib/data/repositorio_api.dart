import 'dart:math';

import '../models/modelos.dart';
import 'cliente_api.dart';
import 'repositorio.dart';

/// Implementação de [Repositorio] sobre a API MinhaVida (`/api/v1`).
///
/// Convenções:
/// - dinheiro trafega como texto decimal ("1220.35") e vira centavos (int);
/// - categorias são identificadas por nome na interface e por UUID na API
///   (catálogos carregados sob demanda);
/// - listas paginadas por cursor são expostas com `deslocamento/limite`,
///   guardando os cursores já conhecidos.
class RepositorioApi implements Repositorio {
  RepositorioApi({
    required this.cliente,
    String? fusoHorario,
    DateTime Function()? relogio,
  }) : _fuso = fusoHorario,
       _relogio = relogio ?? DateTime.now {
    cliente.aoSessaoExpirada = _sessaoExpirou;
  }

  final ClienteApi cliente;
  final String? _fuso;
  final DateTime Function() _relogio;

  Usuario? _usuario;
  _Catalogos? _catalogos;
  final Map<String, Map<int, String>> _cursores = {};
  Future<Map<String, dynamic>>? _painelImp;

  @override
  void Function()? aoSessaoExpirada;

  void _sessaoExpirou() {
    _limpar();
    aoSessaoExpirada?.call();
  }

  void _limpar() {
    _usuario = null;
    _catalogos = null;
    _cursores.clear();
    _painelImp = null;
    cliente.token = null;
  }

  /// Chamado após qualquer gravação: descarta caches de leitura.
  void _mudou() {
    _cursores.clear();
    _painelImp = null;
  }

  // ======================================================== Conversões
  static String _data(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-'
      '${d.month.toString().padLeft(2, '0')}-'
      '${d.day.toString().padLeft(2, '0')}';

  static DateTime _lerData(String s) {
    final p = s.split('-');
    return DateTime(int.parse(p[0]), int.parse(p[1]), int.parse(p[2]));
  }

  static String _hora(int minutos) =>
      '${(minutos ~/ 60).toString().padLeft(2, '0')}:'
      '${(minutos % 60).toString().padLeft(2, '0')}';

  static int _lerHora(String s) =>
      int.parse(s.substring(0, 2)) * 60 + int.parse(s.substring(3, 5));

  static String _dinheiro(int centavos) =>
      '${centavos ~/ 100}.${(centavos % 100).toString().padLeft(2, '0')}';

  static int _centavos(String s) {
    final p = s.split('.');
    final decimais = p.length > 1
        ? p[1].padRight(2, '0').substring(0, 2)
        : '00';
    return int.parse(p[0]) * 100 + int.parse(decimais);
  }

  static DateTime _instante(String s) => DateTime.parse(s).toLocal();

  static String? _textoOuNulo(String s) {
    final t = s.trim();
    return t.isEmpty ? null : t;
  }

  static Map<String, dynamic> _mapa(dynamic v) => v as Map<String, dynamic>;

  static String _mes(int ano, int mes) =>
      '${ano.toString().padLeft(4, '0')}-${mes.toString().padLeft(2, '0')}';

  static Periodicidade _periodicidade(dynamic v) => switch (v) {
    'DIARIA' => Periodicidade.diaria,
    'SEMANAL' => Periodicidade.semanal,
    'MENSAL' => Periodicidade.mensal,
    'ANUAL' => Periodicidade.anual,
    _ => Periodicidade.nenhuma,
  };

  static String _periodicidadeApi(Periodicidade p) => switch (p) {
    Periodicidade.nenhuma => 'NAO_REPETIR',
    Periodicidade.diaria => 'DIARIA',
    Periodicidade.semanal => 'SEMANAL',
    Periodicidade.mensal => 'MENSAL',
    Periodicidade.anual => 'ANUAL',
  };

  static Map<String, dynamic>? _repeticao(
    Periodicidade p,
    DateTime? dataFinal,
  ) {
    if (p == Periodicidade.nenhuma) return null;
    return {
      'periodicidade': _periodicidadeApi(p),
      'termino': dataFinal == null ? 'SEM_DATA_FINAL' : 'ATE_DATA',
      'data_final': dataFinal == null ? null : _data(dataFinal),
    };
  }

  static Prioridade _prioridade(String v) => switch (v) {
    'ALTA' => Prioridade.alta,
    'MEDIA' => Prioridade.media,
    _ => Prioridade.baixa,
  };

  static String _prioridadeApi(Prioridade p) => switch (p) {
    Prioridade.baixa => 'BAIXA',
    Prioridade.media => 'MEDIA',
    Prioridade.alta => 'ALTA',
  };

  static String _alcance(EscopoSerie e) =>
      e == EscopoSerie.somenteEsta ? 'SOMENTE_ESTA' : 'ESTA_E_PROXIMAS';

  static const _formas = {
    'PIX': 'Pix',
    'DINHEIRO': 'Dinheiro',
    'TRANSFERENCIA': 'Transferência',
    'DEPOSITO': 'Depósito',
    'CARTAO_DEBITO': 'Cartão de débito',
    'BOLETO': 'Boleto',
    'OUTROS': 'Outros',
  };

  static String? _formaApi(String? rotulo) {
    if (rotulo == null) return null;
    for (final e in _formas.entries) {
      if (e.value == rotulo) return e.key;
    }
    return 'OUTROS';
  }

  /// Fuso IANA enviado no cadastro. O Dart expõe só o deslocamento; usa os
  /// fusos brasileiros e permite sobrescrever por `--dart-define=FUSO_HORARIO`.
  String get _fusoHorario {
    final informado = _fuso;
    if (informado != null && informado.isNotEmpty) return informado;
    final horas = _relogio().timeZoneOffset.inHours;
    return switch (horas) {
      -2 => 'America/Noronha',
      -4 => 'America/Manaus',
      -5 => 'America/Rio_Branco',
      _ => 'America/Sao_Paulo',
    };
  }

  // ============================================================ Catálogos
  Future<_Catalogos> _cat() async {
    final existente = _catalogos;
    if (existente != null) return existente;
    final r = await Future.wait([
      cliente.get('/api/v1/categorias/atividades'),
      cliente.get('/api/v1/categorias/importancias'),
      cliente.get(
        '/api/v1/categorias/financeiras',
        consulta: {'tipo': 'RECEITA'},
      ),
      cliente.get(
        '/api/v1/categorias/financeiras',
        consulta: {'tipo': 'DESPESA'},
      ),
    ]);
    Map<String, String> ler(dynamic lista) => {
      for (final c in (lista as List)) c['nome'] as String: c['id'] as String,
    };
    return _catalogos = _Catalogos(
      atividades: ler(r[0]),
      importancias: ler(r[1]),
      receitas: ler(r[2]),
      despesas: ler(r[3]),
    );
  }

  static String _idDe(Map<String, String> catalogo, String nome) {
    final id = catalogo[nome];
    if (id == null) throw const ErroApp('Selecione uma categoria válida');
    return id;
  }

  // =============================================================== Conta
  @override
  Usuario? get usuario => _usuario;

  Usuario _lerUsuario(Map<String, dynamic> j) => Usuario(
    id: j['id'] as String,
    nome: j['nome_completo'] as String,
    email: j['email'] as String,
    nascimento: _lerData(j['data_nascimento'] as String),
  );

  @override
  Future<Usuario> entrar(String email, String senha) async {
    final t = _mapa(
      await cliente.post('/api/v1/auth/login', {
        'email': email.trim(),
        'senha': senha,
      }, autenticado: false),
    );
    cliente.token = t['access_token'] as String;
    try {
      final u = _lerUsuario(_mapa(await cliente.get('/api/v1/usuarios/me')));
      _catalogos = null;
      _mudou();
      return _usuario = u;
    } on Object {
      _limpar();
      rethrow;
    }
  }

  @override
  Future<Usuario> registrar({
    required String nome,
    required String email,
    required String senha,
    required DateTime nascimento,
  }) async {
    await cliente.post('/api/v1/auth/registro', {
      'nome_completo': nome.trim(),
      'email': email.trim(),
      'senha': senha,
      'confirmar_senha': senha,
      'data_nascimento': _data(nascimento),
      'fuso_horario': _fusoHorario,
    }, autenticado: false);
    return entrar(email, senha);
  }

  @override
  void sair() => _limpar();

  @override
  Future<String?> solicitarCodigo(String email) async {
    await cliente.post('/api/v1/auth/recuperacao/solicitar', {
      'email': email.trim(),
    }, autenticado: false);
    return null; // o código chega por e-mail
  }

  @override
  Future<String> verificarCodigo(String email, String codigo) async {
    final r = _mapa(
      await cliente.post('/api/v1/auth/recuperacao/verificar', {
        'email': email.trim(),
        'codigo': codigo,
      }, autenticado: false),
    );
    return r['token_redefinicao'] as String;
  }

  @override
  Future<void> redefinirSenha({
    required String email,
    required String token,
    required String novaSenha,
  }) async {
    await cliente.post('/api/v1/auth/recuperacao/redefinir', {
      'token_redefinicao': token,
      'nova_senha': novaSenha,
      'confirmar_senha': novaSenha,
    }, autenticado: false);
  }

  // ======================================================= Paginação
  /// Lê itens por cursor expondo `deslocamento/limite`.
  ///
  /// Devolve os itens pedidos e a última resposta (com totais e indicadores).
  Future<(List<dynamic>, Map<String, dynamic>)> _paginar(
    String caminho,
    Map<String, String?> params, {
    required int deslocamento,
    required int limite,
  }) async {
    final ordenado = (params.entries.toList()
      ..sort((a, b) => a.key.compareTo(b.key)));
    final chave =
        '$caminho?${ordenado.map((e) => '${e.key}=${e.value}').join('&')}';
    final memo = _cursores.putIfAbsent(chave, () => {});
    var pos = 0;
    String? cursor;
    if (deslocamento > 0 && memo.containsKey(deslocamento)) {
      pos = deslocamento;
      cursor = memo[deslocamento];
    } else if (deslocamento == 0) {
      memo.clear();
    }
    final itens = <dynamic>[];
    late Map<String, dynamic> ultima;
    while (true) {
      final descartar = max(0, deslocamento - pos);
      final falta = limite - itens.length;
      final pedir = min(50, max(1, descartar + falta));
      ultima = _mapa(
        await cliente.get(
          caminho,
          consulta: {...params, 'limite': '$pedir', 'cursor': cursor},
        ),
      );
      final pagina = (ultima['itens'] as List);
      var visto = 0;
      for (final item in pagina) {
        if (pos + visto >= deslocamento && itens.length < limite) {
          itens.add(item);
        }
        visto++;
      }
      pos += pagina.length;
      cursor = ultima['proximo_cursor'] as String?;
      if (cursor == null) break;
      memo[pos] = cursor;
      if (itens.length >= limite) break;
    }
    return (itens, ultima);
  }

  /// Todos os itens de uma consulta paginada (listas completas).
  Future<List<dynamic>> _todos(
    String caminho,
    Map<String, String?> params,
  ) async {
    final itens = <dynamic>[];
    String? cursor;
    for (var i = 0; i < 200; i++) {
      final r = _mapa(
        await cliente.get(
          caminho,
          consulta: {...params, 'limite': '50', 'cursor': cursor},
        ),
      );
      itens.addAll(r['itens'] as List);
      cursor = r['proximo_cursor'] as String?;
      if (cursor == null) break;
    }
    return itens;
  }

  // ========================================================== Atividades
  Atividade _atividade(Map<String, dynamic> j) {
    final serie = j['serie'] as Map<String, dynamic>?;
    final data = _lerData(j['data'] as String);
    final concluidaEm = j['concluida_em'] as String?;
    return Atividade(
      id: j['id'] as String,
      nome: j['nome'] as String,
      categoria: _mapa(j['categoria'])['nome'] as String,
      prioridade: _prioridade(j['prioridade'] as String),
      data: data,
      inicio: _lerHora(j['horario_inicial'] as String),
      fim: _lerHora(j['horario_final'] as String),
      criadoEm: j['criado_em'] != null
          ? _instante(j['criado_em'] as String)
          : data,
      // A lista traz só a prévia (30 caracteres + reticências); o detalhe
      // traz o texto completo.
      descricao:
          ((j.containsKey('descricao') ? j['descricao'] : j['descricao_previa'])
              as String?) ??
          '',
      serieId: (j['serie_id'] ?? serie?['id']) as String?,
      numero: j['numero_ocorrencia'] as int?,
      periodicidade: _periodicidade(j['periodicidade']),
      concluidaEm: concluidaEm == null ? null : _instante(concluidaEm),
    );
  }

  Map<String, dynamic> _corpoAtividade(AtividadeForm f, String categoriaId) => {
    'nome': f.nome.trim(),
    'categoria_id': categoriaId,
    'prioridade': _prioridadeApi(f.prioridade),
    'data': _data(f.data),
    'horario_inicial': _hora(f.inicio),
    'horario_final': _hora(f.fim),
    'descricao': _textoOuNulo(f.descricao),
    // A interface já perguntou ao usuário (Revisar horários / Salvar mesmo
    // assim) antes de chamar o repositório.
    'confirmar_sobreposicao': true,
  };

  @override
  Future<ConsultaAtividades> consultarAtividades(
    FiltroAtividades f, {
    int deslocamento = 0,
    int limite = 10,
  }) async {
    final cat = await _cat();
    final (itens, ultima) = await _paginar(
      '/api/v1/atividades',
      {
        'data': _data(f.data),
        'categoria_id': f.categoria == null
            ? null
            : _idDe(cat.atividades, f.categoria!),
        'situacao': switch (f.situacao) {
          SituacaoFiltro.todas => 'TODAS',
          SituacaoFiltro.pendentes => 'PENDENTE',
          SituacaoFiltro.concluidas => 'CONCLUIDA',
        },
        'prioridade': f.prioridade == null
            ? 'TODAS'
            : _prioridadeApi(f.prioridade!),
        'busca': f.busca.trim().isEmpty ? null : f.busca.trim(),
        'ordenacao': switch (f.ordem) {
          OrdemAtividade.horario => 'HORARIO',
          OrdemAtividade.prioridade => 'PRIORIDADE',
          OrdemAtividade.recentes => 'RECENTES',
        },
      },
      deslocamento: deslocamento,
      limite: limite,
    );
    final ind = _mapa(ultima['indicadores']);
    return ConsultaAtividades(
      itens: [for (final i in itens) _atividade(_mapa(i))],
      total: ind['total'] as int,
      concluidas: ind['concluidas'] as int,
      pendentes: ind['pendentes'] as int,
      minutos: ind['tempo_total_minutos'] as int,
    );
  }

  @override
  Future<PendenciasAnteriores> pendenciasAnteriores() async {
    final r = _mapa(
      await cliente.get('/api/v1/atividades/pendencias-anteriores'),
    );
    final antiga = r['data_mais_antiga'] as String?;
    return PendenciasAnteriores(
      quantidade: r['quantidade'] as int,
      maisAntiga: antiga == null ? null : _lerData(antiga),
    );
  }

  @override
  Future<Atividade> obterAtividade(String id) async {
    try {
      return _atividade(_mapa(await cliente.get('/api/v1/atividades/$id')));
    } on ErroApp catch (e) {
      if (e.status == 404) throw const ErroApp('Atividade não encontrada.');
      rethrow;
    }
  }

  @override
  Future<List<Atividade>> sobreposicoes(
    DateTime data,
    int inicio,
    int fim, {
    String? ignorarId,
  }) async {
    final dia = await _todos('/api/v1/atividades', {'data': _data(data)});
    return [
      for (final j in dia)
        if (_mapa(j)['id'] != ignorarId) _atividade(_mapa(j)),
    ].where((a) => a.inicio < fim && inicio < a.fim).toList();
  }

  @override
  Future<Atividade> criarAtividade(AtividadeForm form) async {
    final cat = await _cat();
    final corpo = _corpoAtividade(form, _idDe(cat.atividades, form.categoria));
    final rep = _repeticao(form.periodicidade, form.dataFinal);
    if (rep != null) corpo['repeticao'] = rep;
    final r = await cliente.postIdempotente('/api/v1/atividades', corpo);
    _mudou();
    return _atividade(_mapa(r));
  }

  @override
  Future<void> editarAtividade(
    String id,
    AtividadeForm form,
    EscopoSerie escopo,
  ) async {
    final cat = await _cat();
    final corpo = _corpoAtividade(form, _idDe(cat.atividades, form.categoria))
      ..['alcance'] = _alcance(escopo);
    await cliente.patch('/api/v1/atividades/$id', corpo);
    _mudou();
  }

  @override
  Future<void> excluirAtividade(String id, EscopoSerie escopo) async {
    await cliente.delete(
      '/api/v1/atividades/$id',
      consulta: {'alcance': _alcance(escopo)},
    );
    _mudou();
  }

  @override
  Future<Atividade> alterarConclusaoAtividade(String id, bool concluida) async {
    final r = await cliente.put('/api/v1/atividades/$id/situacao', {
      'situacao': concluida ? 'CONCLUIDA' : 'PENDENTE',
    });
    _mudou();
    return _atividade(_mapa(r));
  }

  // ======================================================== Importâncias
  Importancia _importancia(Map<String, dynamic> j) {
    final data = _lerData(j['data_compromisso'] as String);
    final pagamento = j['pagamento'] as Map<String, dynamic>?;
    final lembreteJson = j['lembrete'] as Map<String, dynamic>?;
    final concluida = j['situacao'] == 'CONCLUIDA';
    final momento = j['momento_conclusao'] as String?;
    final serie = j['serie'] as Map<String, dynamic>?;
    final valorPrevisto = j['valor_previsto'] as String?;
    final horario = j['horario'] as String?;
    final imp = Importancia(
      id: j['id'] as String,
      nome: j['nome'] as String,
      categoria: _mapa(j['categoria'])['nome'] as String,
      data: data,
      criadoEm: j['criado_em'] != null
          ? _instante(j['criado_em'] as String)
          : data,
      horario: horario == null ? null : _lerHora(horario),
      temDespesa: j['possui_despesa'] as bool,
      valorPrevisto: valorPrevisto == null ? 0 : _centavos(valorPrevisto),
      descricao: (j['descricao'] as String?) ?? '',
      serieId: (j['serie_id'] ?? serie?['id']) as String?,
      numero: j['numero_ocorrencia'] as int?,
      periodicidade: _periodicidade(j['periodicidade']),
      lembrete: lembreteJson == null || lembreteJson['situacao'] == 'DESATIVADO'
          ? null
          : Lembrete(
              diasAntes: lembreteJson['antecedencia_dias'] as int,
              horario: _lerHora(lembreteJson['horario'] as String),
            ),
      concluidaEm: concluida
          ? (momento == null ? _relogio() : _instante(momento))
          : null,
      movimentacaoId: pagamento?['movimentacao_id'] as String?,
    );
    if (pagamento != null) {
      imp
        ..valorPago = _centavos(pagamento['valor'] as String)
        ..dataPagamento = _lerData(pagamento['data_movimentacao'] as String);
    }
    return imp;
  }

  Map<String, dynamic> _corpoImportancia(
    ImportanciaForm f,
    String categoriaId,
  ) => {
    'nome': f.nome.trim(),
    'categoria_id': categoriaId,
    'data_compromisso': _data(f.data),
    'horario': f.horario == null ? null : _hora(f.horario!),
    'descricao': _textoOuNulo(f.descricao),
    'possui_despesa': f.temDespesa,
    'valor_previsto': f.temDespesa ? _dinheiro(f.valorPrevisto) : null,
    'lembrete': f.lembrete == null
        ? null
        : {
            'antecedencia_dias': f.lembrete!.diasAntes,
            'horario': _hora(f.lembrete!.horario),
          },
  };

  static String _filtroApi(FiltroImportancia f) => switch (f) {
    FiltroImportancia.todos => 'TODOS',
    FiltroImportancia.hoje => 'VENCENDO_HOJE',
    FiltroImportancia.mes => 'ESTE_MES',
    FiltroImportancia.proximos => 'PROXIMOS',
    FiltroImportancia.concluidos => 'CONCLUIDOS',
    FiltroImportancia.atrasados => 'ATRASADOS',
  };

  @override
  Future<List<Importancia>> consultarImportancias(
    FiltroImportancia filtro, {
    required int ano,
    required int mes,
    String busca = '',
  }) async {
    final itens = await _todos('/api/v1/importancias', {
      'filtro': _filtroApi(filtro),
      'mes': filtro == FiltroImportancia.mes ? _mes(ano, mes) : null,
      'busca': busca.trim().isEmpty ? null : busca.trim(),
    });
    return [for (final i in itens) _importancia(_mapa(i))];
  }

  Future<Map<String, dynamic>> _painelImportancias() => _painelImp ??= cliente
      .get('/api/v1/painel/importancias')
      .then(_mapa)
      .catchError((Object e) {
        _painelImp = null;
        throw e;
      });

  @override
  Future<List<Importancia>> proximasImportancias({int limite = 3}) async {
    final p = await _painelImportancias();
    return [for (final i in (p['proximas'] as List)) _importancia(_mapa(i))]
        .take(limite)
        .toList();
  }

  @override
  Future<int> totalAtrasadas() async =>
      (await _painelImportancias())['atrasadas_quantidade'] as int;

  @override
  Future<int> totalPendentesDoMes(int ano, int mes) async {
    final p = await _painelImportancias();
    if (p['mes_referencia'] == _mes(ano, mes)) {
      return p['pendentes_mes'] as int;
    }
    final lista = await consultarImportancias(
      FiltroImportancia.mes,
      ano: ano,
      mes: mes,
    );
    return lista.where((i) => !i.concluida).length;
  }

  @override
  Future<Importancia> obterImportancia(String id) async {
    try {
      return _importancia(_mapa(await cliente.get('/api/v1/importancias/$id')));
    } on ErroApp catch (e) {
      if (e.status == 404) {
        throw const ErroApp('Esta importância não está mais disponível.');
      }
      rethrow;
    }
  }

  @override
  Future<Importancia> criarImportancia(ImportanciaForm form) async {
    final cat = await _cat();
    final corpo = _corpoImportancia(
      form,
      _idDe(cat.importancias, form.categoria),
    );
    final rep = _repeticao(form.periodicidade, form.dataFinal);
    if (rep != null) corpo['repeticao'] = rep;
    final r = await cliente.postIdempotente('/api/v1/importancias', corpo);
    _mudou();
    return _importancia(_mapa(r));
  }

  @override
  Future<void> editarImportancia(
    String id,
    ImportanciaForm form,
    EscopoSerie escopo,
  ) async {
    final cat = await _cat();
    final corpo = _corpoImportancia(
      form,
      _idDe(cat.importancias, form.categoria),
    )..['alcance'] = _alcance(escopo);
    await cliente.patch('/api/v1/importancias/$id', corpo);
    _mudou();
  }

  @override
  Future<void> excluirImportancia(String id, EscopoSerie escopo) async {
    await cliente.delete(
      '/api/v1/importancias/$id',
      consulta: {'alcance': _alcance(escopo)},
    );
    _mudou();
  }

  @override
  Future<Importancia> alterarConclusaoImportancia(
    String id,
    bool concluida,
  ) async {
    final r = await cliente.put('/api/v1/importancias/$id/situacao', {
      'situacao': concluida ? 'CONCLUIDA' : 'PENDENTE',
    });
    _mudou();
    return _importancia(_mapa(r));
  }

  @override
  Future<List<Movimentacao>> despesasSemVinculo({String busca = ''}) async {
    final itens = await _todos(
      '/api/v1/financeiro/despesas/disponiveis-vinculo',
      {'busca': busca.trim().isEmpty ? null : busca.trim()},
    );
    return [
      for (final i in itens)
        Movimentacao(
          id: _mapa(i)['id'] as String,
          tipo: TipoMov.despesa,
          nome: _mapa(i)['nome'] as String,
          valor: _centavos(_mapa(i)['valor'] as String),
          categoria: '',
          data: _lerData(_mapa(i)['data_movimentacao'] as String),
          criadoEm: _lerData(_mapa(i)['data_movimentacao'] as String),
        ),
    ];
  }

  @override
  Future<void> vincularDespesa(
    String importanciaId,
    String movimentacaoId,
  ) async {
    await cliente.put('/api/v1/importancias/$importanciaId/pagamento', {
      'movimentacao_id': movimentacaoId,
    });
    _mudou();
  }

  // =========================================================== Financeiro
  Movimentacao _movimentacao(Map<String, dynamic> j) {
    final data = _lerData(j['data_movimentacao'] as String);
    final imp = j['importancia'] as Map<String, dynamic>?;
    return Movimentacao(
      id: j['id'] as String,
      tipo: j['tipo'] == 'RECEITA' ? TipoMov.receita : TipoMov.despesa,
      nome: j['nome'] as String,
      valor: _centavos(j['valor'] as String),
      categoria: _mapa(j['categoria'])['nome'] as String,
      data: data,
      criadoEm: j['criado_em'] != null
          ? _instante(j['criado_em'] as String)
          : data,
      descricao: (j['descricao'] as String?) ?? '',
      contraparte: (j['contraparte'] as String?) ?? '',
      forma: _formas[j['forma']],
      importanciaId: (imp != null && imp['disponivel'] == true)
          ? imp['id'] as String
          : null,
    );
  }

  Comparacao _comparacao(Map<String, dynamic> j) {
    final anterior = j['intervalo_anterior'] as Map<String, dynamic>?;
    var intervalo = '';
    if (anterior != null) {
      final ini = _lerData(anterior['inicio'] as String);
      final fim = _lerData(anterior['fim'] as String);
      intervalo =
          '${ini.day.toString().padLeft(2, '0')}–'
          '${fim.day.toString().padLeft(2, '0')}/'
          '${fim.month.toString().padLeft(2, '0')}';
    }
    final variacao = j['variacao_percentual'] as String?;
    return switch (j['tendencia']) {
      'SEM_BASE' => Comparacao(
        mensagem: 'Sem base de comparação',
        intervalo: intervalo,
      ),
      'SEM_MOVIMENTACAO' => Comparacao(
        mensagem: 'Sem movimentação nos dois períodos',
        intervalo: intervalo,
      ),
      'NAO_APLICAVEL' => const Comparacao(),
      _ => Comparacao(
        percentual: variacao == null ? null : double.parse(variacao),
        intervalo: intervalo,
      ),
    };
  }

  @override
  Future<ResumoFinanceiro> resumoMes(int ano, int mes) async {
    final j = _mapa(
      await cliente.get(
        '/api/v1/financeiro/resumo',
        consulta: {'mes': _mes(ano, mes)},
      ),
    );
    final comp = _mapa(j['comparacao']);
    return ResumoFinanceiro(
      ano: ano,
      mes: mes,
      receitas: _centavos(j['receitas'] as String),
      despesas: _centavos(j['despesas'] as String),
      compReceitas: _comparacao(_mapa(comp['receitas'])),
      compDespesas: _comparacao(_mapa(comp['despesas'])),
      dias: [
        for (final d in (j['grafico_diario'] as List))
          DiaFinanceiro(
            _lerData(_mapa(d)['data'] as String).day,
            _centavos(_mapa(d)['receitas'] as String),
            _centavos(_mapa(d)['despesas'] as String),
          ),
      ],
      categorias: [
        for (final c in (j['categorias_despesa'] as List))
          CategoriaTotal(
            _mapa(_mapa(c)['categoria'])['nome'] as String,
            _centavos(_mapa(c)['total'] as String),
          ),
      ],
    );
  }

  @override
  Future<ResumoDia> resumoDia(DateTime dia) async {
    final r = await resumoMes(dia.year, dia.month);
    final d = r.dias[dia.day - 1];
    return ResumoDia(receitas: d.receitas, despesas: d.despesas);
  }

  @override
  Future<ConsultaMov> consultarMovimentacoes(
    FiltroMov f, {
    int deslocamento = 0,
    int limite = 10,
  }) async {
    final cat = await _cat();
    final comum = <String, String?>{
      'mes': _mes(f.ano, f.mes),
      'busca': f.busca.trim().isEmpty ? null : f.busca.trim(),
    };
    final nome = f.categoria;
    // "Outros" existe nas duas listas; sem tipo escolhido, consulta ambas.
    final ambigua =
        nome != null &&
        f.tipo == null &&
        cat.receitas.containsKey(nome) &&
        cat.despesas.containsKey(nome);
    if (ambigua) {
      final a = await _todos('/api/v1/financeiro/movimentacoes', {
        ...comum,
        'tipo': 'RECEITA',
        'categoria_id': cat.receitas[nome],
      });
      final b = await _todos('/api/v1/financeiro/movimentacoes', {
        ...comum,
        'tipo': 'DESPESA',
        'categoria_id': cat.despesas[nome],
      });
      final todos =
          [
            for (final j in [...a, ...b]) _movimentacao(_mapa(j)),
          ]..sort((x, y) {
            final c = y.data.compareTo(x.data);
            return c != 0 ? c : y.id.compareTo(x.id);
          });
      final ini = min(deslocamento, todos.length);
      return ConsultaMov(
        itens: todos.sublist(ini, min(todos.length, ini + limite)),
        total: todos.length,
      );
    }
    String? categoriaId;
    var tipo = switch (f.tipo) {
      TipoMov.receita => 'RECEITA',
      TipoMov.despesa => 'DESPESA',
      null => 'TODAS',
    };
    if (nome != null) {
      if (cat.receitas.containsKey(nome) && f.tipo != TipoMov.despesa) {
        categoriaId = cat.receitas[nome];
        tipo = 'RECEITA';
      } else {
        categoriaId = _idDe(cat.despesas, nome);
        tipo = 'DESPESA';
      }
    }
    final (itens, ultima) = await _paginar(
      '/api/v1/financeiro/movimentacoes',
      {...comum, 'tipo': tipo, 'categoria_id': categoriaId},
      deslocamento: deslocamento,
      limite: limite,
    );
    return ConsultaMov(
      itens: [for (final j in itens) _movimentacao(_mapa(j))],
      total: ultima['total'] as int,
    );
  }

  @override
  Future<Movimentacao> obterMovimentacao(String id) async {
    try {
      return _movimentacao(
        _mapa(await cliente.get('/api/v1/financeiro/movimentacoes/$id')),
      );
    } on ErroApp catch (e) {
      if (e.status == 404) throw const ErroApp('Lançamento não encontrado.');
      rethrow;
    }
  }

  @override
  Future<Movimentacao> criarMovimentacao(MovimentacaoForm form) async {
    final cat = await _cat();
    final receita = form.tipo == TipoMov.receita;
    final corpo = <String, dynamic>{
      'nome': form.nome.trim(),
      'valor': _dinheiro(form.valor),
      'categoria_id': _idDe(
        receita ? cat.receitas : cat.despesas,
        form.categoria,
      ),
      'data_movimentacao': _data(form.data),
      'descricao': _textoOuNulo(form.descricao),
      'contraparte': _textoOuNulo(form.contraparte),
      'forma': _formaApi(form.forma),
      if (!receita && form.importanciaId != null)
        'importancia_id': form.importanciaId,
    };
    final r = await cliente.postIdempotente(
      '/api/v1/financeiro/${receita ? 'receitas' : 'despesas'}',
      corpo,
    );
    _mudou();
    return _movimentacao(_mapa(r));
  }

  @override
  Future<void> editarMovimentacao(String id, MovimentacaoForm form) async {
    final cat = await _cat();
    final receita = form.tipo == TipoMov.receita;
    await cliente.patch('/api/v1/financeiro/movimentacoes/$id', {
      'nome': form.nome.trim(),
      'valor': _dinheiro(form.valor),
      'categoria_id': _idDe(
        receita ? cat.receitas : cat.despesas,
        form.categoria,
      ),
      'data_movimentacao': _data(form.data),
      'descricao': _textoOuNulo(form.descricao),
      'contraparte': _textoOuNulo(form.contraparte),
      'forma': _formaApi(form.forma),
    });
    _mudou();
  }

  @override
  Future<void> excluirMovimentacao(String id) async {
    await cliente.delete('/api/v1/financeiro/movimentacoes/$id');
    _mudou();
  }

  // ======================================================== Notificações
  @override
  Future<List<Notificacao>> listarNotificacoes() async {
    final itens = await _todos('/api/v1/notificacoes', {});
    return [
      for (final j in itens)
        Notificacao(
          id: _mapa(j)['id'] as String,
          importanciaId: _mapa(_mapa(j)['importancia'])['id'] as String,
          titulo: _mapa(j)['titulo'] as String,
          mensagem: _mapa(j)['mensagem'] as String,
          geradaEm: _instante(_mapa(j)['criada_em'] as String),
          lida: _mapa(j)['lida'] as bool,
        ),
    ];
  }

  @override
  Future<int> totalNaoLidas() async =>
      _mapa(await cliente.get('/api/v1/notificacoes/nao-lidas'))['quantidade']
          as int;

  @override
  Future<void> marcarNotificacaoLida(String id) async {
    await cliente.post('/api/v1/notificacoes/$id/leitura', const {});
  }
}

class _Catalogos {
  const _Catalogos({
    required this.atividades,
    required this.importancias,
    required this.receitas,
    required this.despesas,
  });
  final Map<String, String> atividades;
  final Map<String, String> importancias;
  final Map<String, String> receitas;
  final Map<String, String> despesas;
}
