import 'package:flutter/material.dart';

import '../data/repositorio.dart';
import '../models/modelos.dart';

/// Abas da navegação inferior (ordem fixa exigida pelos requisitos).
enum Aba { inicio, atividades, financeiro, importancias, perfil }

/// Intenção de navegação entre abas, com parâmetros opcionais.
class IntencaoAba {
  const IntencaoAba(
    this.aba, {
    this.data,
    this.situacao,
    this.limparFiltros = false,
    this.filtroImportancia,
    this.ano,
    this.mes,
    this.tipoMov,
    this.categoriaMov,
    this.destaqueId,
    this.abrirMovimentacoes = false,
  });

  final Aba aba;
  final DateTime? data;
  final SituacaoFiltro? situacao;
  final bool limparFiltros;
  final FiltroImportancia? filtroImportancia;
  final int? ano;
  final int? mes;
  final TipoMov? tipoMov;
  final String? categoriaMov;
  final String? destaqueId;
  final bool abrirMovimentacoes;
}

/// Controla a aba atual e entrega parâmetros às telas das abas.
class Navegacao extends ChangeNotifier {
  Aba _aba = Aba.inicio;
  Aba get aba => _aba;

  IntencaoAba? _pendente;

  /// Consome a intenção pendente para [aba] (uma única vez).
  IntencaoAba? consumir(Aba aba) {
    final p = _pendente;
    if (p != null && p.aba == aba) {
      _pendente = null;
      return p;
    }
    return null;
  }

  void ir(IntencaoAba intencao) {
    _aba = intencao.aba;
    _pendente = intencao;
    notifyListeners();
  }

  void irPara(Aba aba) => ir(IntencaoAba(aba));
}

/// Avisa as telas quando dados foram alterados (para recarregarem).
class BarramentoDados extends ChangeNotifier {
  int versao = 0;
  void mudou() {
    versao++;
    notifyListeners();
  }
}

/// Dependências compartilhadas por toda a árvore de widgets.
class AppScope extends InheritedWidget {
  const AppScope({
    super.key,
    required this.repositorio,
    required this.navegacao,
    required this.dados,
    required this.relogio,
    required this.aoEntrar,
    required this.aoSair,
    required super.child,
  });

  final Repositorio repositorio;
  final Navegacao navegacao;
  final BarramentoDados dados;
  final DateTime Function() relogio;
  final VoidCallback aoEntrar;
  final VoidCallback aoSair;

  static AppScope of(BuildContext context) {
    final s = context.dependOnInheritedWidgetOfExactType<AppScope>();
    assert(s != null, 'AppScope não encontrado');
    return s!;
  }

  DateTime get agora => relogio();
  DateTime get hoje => DateTime(agora.year, agora.month, agora.day);

  @override
  bool updateShouldNotify(AppScope old) =>
      repositorio != old.repositorio || relogio != old.relogio;
}
