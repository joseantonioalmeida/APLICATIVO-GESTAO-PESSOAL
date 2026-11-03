import 'package:flutter/material.dart';

/// Erro de negócio com mensagem pronta para exibir ao usuário.
class ErroApp implements Exception {
  const ErroApp(this.mensagem, {this.campo});
  final String mensagem;
  final String? campo;
  @override
  String toString() => mensagem;
}

enum Prioridade {
  baixa('Baixa', Color(0xFF34D399)),
  media('Média', Color(0xFFFCC431)),
  alta('Alta', Color(0xFFFF7E96));

  const Prioridade(this.rotulo, this.cor);
  final String rotulo;
  final Color cor;
}

enum Periodicidade {
  nenhuma('Não repetir'),
  diaria('Diariamente'),
  semanal('Semanalmente'),
  mensal('Mensalmente'),
  anual('Anualmente');

  const Periodicidade(this.rotulo);
  final String rotulo;

  /// "Repete diariamente", "Repete anualmente"...
  String get textoRepete {
    switch (this) {
      case Periodicidade.nenhuma:
        return '';
      case Periodicidade.diaria:
        return 'Repete diariamente';
      case Periodicidade.semanal:
        return 'Repete semanalmente';
      case Periodicidade.mensal:
        return 'Repete mensalmente';
      case Periodicidade.anual:
        return 'Repete anualmente';
    }
  }
}

enum TipoMov {
  receita('Receita'),
  despesa('Despesa');

  const TipoMov(this.rotulo);
  final String rotulo;
}

enum EscopoSerie { somenteEsta, estaEProximas }

class Usuario {
  const Usuario({
    required this.id,
    required this.nome,
    required this.email,
    required this.nascimento,
  });
  final String id;
  final String nome;
  final String email;
  final DateTime nascimento;

  String get primeiroNome => nome.trim().split(RegExp(r'\s+')).first;

  String get iniciais {
    final p = nome.trim().split(RegExp(r'\s+'));
    if (p.length == 1) return p.first.substring(0, 1).toUpperCase();
    return (p.first[0] + p.last[0]).toUpperCase();
  }
}

class Atividade {
  Atividade({
    required this.id,
    required this.nome,
    required this.categoria,
    required this.prioridade,
    required this.data,
    required this.inicio,
    required this.fim,
    required this.criadoEm,
    this.descricao = '',
    this.serieId,
    this.numero,
    this.periodicidade = Periodicidade.nenhuma,
    this.concluidaEm,
    this.excluida = false,
  });

  final String id;
  String nome;
  String categoria;
  Prioridade prioridade;
  DateTime data;
  int inicio; // minutos desde 00:00
  int fim;
  final DateTime criadoEm;
  String descricao;
  final String? serieId;
  final int? numero;
  Periodicidade periodicidade;
  DateTime? concluidaEm;
  bool excluida;

  bool get concluida => concluidaEm != null;
  int get duracaoMin => fim - inicio;

  /// Prévia da descrição: até 30 caracteres, com reticências.
  String get previa =>
      descricao.length <= 30 ? descricao : '${descricao.substring(0, 30)}…';

  Atividade copia() => Atividade(
    id: id,
    nome: nome,
    categoria: categoria,
    prioridade: prioridade,
    data: data,
    inicio: inicio,
    fim: fim,
    criadoEm: criadoEm,
    descricao: descricao,
    serieId: serieId,
    numero: numero,
    periodicidade: periodicidade,
    concluidaEm: concluidaEm,
    excluida: excluida,
  );
}

class Lembrete {
  const Lembrete({required this.diasAntes, required this.horario});
  final int diasAntes; // 0, 1, 3 ou 7
  final int horario; // minutos desde 00:00
}

class Importancia {
  Importancia({
    required this.id,
    required this.nome,
    required this.categoria,
    required this.data,
    required this.criadoEm,
    this.horario,
    this.temDespesa = false,
    this.valorPrevisto = 0,
    this.descricao = '',
    this.serieId,
    this.numero,
    this.periodicidade = Periodicidade.nenhuma,
    this.lembrete,
    this.concluidaEm,
    this.movimentacaoId,
    this.excluida = false,
  });

  final String id;
  String nome;
  String categoria;
  DateTime data;
  final DateTime criadoEm;
  int? horario;
  bool temDespesa;
  int valorPrevisto; // centavos
  String descricao;
  final String? serieId;
  final int? numero;
  Periodicidade periodicidade;
  Lembrete? lembrete;
  DateTime? concluidaEm;
  String? movimentacaoId;
  bool excluida;

  /// Preenchidos pelo repositório quando há despesa vinculada.
  int? valorPago; // centavos
  DateTime? dataPagamento;

  bool get concluida => concluidaEm != null;
  bool get paga => movimentacaoId != null;

  Importancia copia() => Importancia(
    id: id,
    nome: nome,
    categoria: categoria,
    data: data,
    criadoEm: criadoEm,
    horario: horario,
    temDespesa: temDespesa,
    valorPrevisto: valorPrevisto,
    descricao: descricao,
    serieId: serieId,
    numero: numero,
    periodicidade: periodicidade,
    lembrete: lembrete,
    concluidaEm: concluidaEm,
    movimentacaoId: movimentacaoId,
    excluida: excluida,
  );
}

class Movimentacao {
  Movimentacao({
    required this.id,
    required this.tipo,
    required this.nome,
    required this.valor,
    required this.categoria,
    required this.data,
    required this.criadoEm,
    this.descricao = '',
    this.contraparte = '',
    this.forma,
    this.importanciaId,
  });

  final String id;
  final TipoMov tipo;
  String nome;
  int valor; // centavos, sempre positivo
  String categoria;
  DateTime data;
  final DateTime criadoEm;
  String descricao;
  String contraparte; // origem/pagador ou destinatário/estabelecimento
  String? forma;
  String? importanciaId;

  bool get receita => tipo == TipoMov.receita;
}

class Notificacao {
  const Notificacao({
    required this.id,
    required this.importanciaId,
    required this.titulo,
    required this.mensagem,
    required this.geradaEm,
    required this.lida,
  });
  final String id;
  final String importanciaId;
  final String titulo;
  final String mensagem;
  final DateTime geradaEm;
  final bool lida;
}

// ---------------------------------------------------------------------------
// Formulários (dados enviados ao repositório)
// ---------------------------------------------------------------------------

class AtividadeForm {
  const AtividadeForm({
    required this.nome,
    required this.categoria,
    required this.prioridade,
    required this.data,
    required this.inicio,
    required this.fim,
    this.descricao = '',
    this.periodicidade = Periodicidade.nenhuma,
    this.dataFinal,
  });
  final String nome;
  final String categoria;
  final Prioridade prioridade;
  final DateTime data;
  final int inicio;
  final int fim;
  final String descricao;
  final Periodicidade periodicidade;
  final DateTime? dataFinal;
}

class ImportanciaForm {
  const ImportanciaForm({
    required this.nome,
    required this.categoria,
    required this.data,
    this.temDespesa = false,
    this.valorPrevisto = 0,
    this.horario,
    this.periodicidade = Periodicidade.nenhuma,
    this.dataFinal,
    this.descricao = '',
    this.lembrete,
  });
  final String nome;
  final String categoria;
  final DateTime data;
  final bool temDespesa;
  final int valorPrevisto;
  final int? horario;
  final Periodicidade periodicidade;
  final DateTime? dataFinal;
  final String descricao;
  final Lembrete? lembrete;
}

class MovimentacaoForm {
  const MovimentacaoForm({
    required this.tipo,
    required this.nome,
    required this.valor,
    required this.categoria,
    required this.data,
    this.descricao = '',
    this.contraparte = '',
    this.forma,
    this.importanciaId,
  });
  final TipoMov tipo;
  final String nome;
  final int valor;
  final String categoria;
  final DateTime data;
  final String descricao;
  final String contraparte;
  final String? forma;
  final String? importanciaId;
}

// ---------------------------------------------------------------------------
// Consultas e resumos
// ---------------------------------------------------------------------------

enum SituacaoFiltro {
  todas('Todas'),
  pendentes('Pendentes'),
  concluidas('Concluídas');

  const SituacaoFiltro(this.rotulo);
  final String rotulo;
}

enum OrdemAtividade {
  horario('Horário inicial'),
  prioridade('Prioridade'),
  recentes('Mais recentes');

  const OrdemAtividade(this.rotulo);
  final String rotulo;
}

class FiltroAtividades {
  const FiltroAtividades({
    required this.data,
    this.categoria,
    this.situacao = SituacaoFiltro.todas,
    this.prioridade,
    this.busca = '',
    this.ordem = OrdemAtividade.horario,
  });
  final DateTime data;
  final String? categoria;
  final SituacaoFiltro situacao;
  final Prioridade? prioridade;
  final String busca;
  final OrdemAtividade ordem;

  /// Há algum filtro ativo além da data (a ordenação não conta).
  bool get filtrado =>
      categoria != null ||
      situacao != SituacaoFiltro.todas ||
      prioridade != null ||
      busca.trim().isNotEmpty;

  FiltroAtividades copiar({
    DateTime? data,
    Object? categoria = _n,
    SituacaoFiltro? situacao,
    Object? prioridade = _n,
    String? busca,
    OrdemAtividade? ordem,
  }) => FiltroAtividades(
    data: data ?? this.data,
    categoria: identical(categoria, _n) ? this.categoria : categoria as String?,
    situacao: situacao ?? this.situacao,
    prioridade: identical(prioridade, _n)
        ? this.prioridade
        : prioridade as Prioridade?,
    busca: busca ?? this.busca,
    ordem: ordem ?? this.ordem,
  );

  FiltroAtividades limpo() => FiltroAtividades(data: data, ordem: ordem);
}

const _n = Object();

class ConsultaAtividades {
  const ConsultaAtividades({
    required this.itens,
    required this.total,
    required this.concluidas,
    required this.pendentes,
    required this.minutos,
  });
  final List<Atividade> itens;
  final int total;
  final int concluidas;
  final int pendentes;
  final int minutos;

  bool get temMais => itens.length < total;
}

class PendenciasAnteriores {
  const PendenciasAnteriores({required this.quantidade, this.maisAntiga});
  final int quantidade;
  final DateTime? maisAntiga;
}

enum FiltroImportancia {
  todos('Todos'),
  hoje('Vencendo hoje'),
  mes('Este mês'),
  proximos('Próximos'),
  concluidos('Concluídos'),
  atrasados('Atrasados');

  const FiltroImportancia(this.rotulo);
  final String rotulo;
}

class ResumoDia {
  const ResumoDia({required this.receitas, required this.despesas});
  final int receitas;
  final int despesas;
  int get saldo => receitas - despesas;
}

class DiaFinanceiro {
  const DiaFinanceiro(this.dia, this.receitas, this.despesas);
  final int dia;
  final int receitas;
  final int despesas;
}

class CategoriaTotal {
  const CategoriaTotal(this.categoria, this.total);
  final String categoria;
  final int total;
}

class Comparacao {
  const Comparacao({this.percentual, this.mensagem, this.intervalo = ''});

  /// Variação em %; null quando não há base ou o mês é futuro.
  final double? percentual;

  /// Texto alternativo ("Sem base de comparação"...).
  final String? mensagem;

  /// Ex.: "01–29/08".
  final String intervalo;
}

class ResumoFinanceiro {
  const ResumoFinanceiro({
    required this.ano,
    required this.mes,
    required this.receitas,
    required this.despesas,
    required this.compReceitas,
    required this.compDespesas,
    required this.dias,
    required this.categorias,
  });
  final int ano;
  final int mes;
  final int receitas;
  final int despesas;
  final Comparacao compReceitas;
  final Comparacao compDespesas;
  final List<DiaFinanceiro> dias;
  final List<CategoriaTotal> categorias;
  int get saldo => receitas - despesas;
}

class FiltroMov {
  const FiltroMov({
    required this.ano,
    required this.mes,
    this.busca = '',
    this.tipo,
    this.categoria,
  });
  final int ano;
  final int mes;
  final String busca;
  final TipoMov? tipo;
  final String? categoria;

  bool get filtrado =>
      busca.trim().isNotEmpty || tipo != null || categoria != null;
}

class ConsultaMov {
  const ConsultaMov({required this.itens, required this.total});
  final List<Movimentacao> itens;
  final int total;
  bool get temMais => itens.length < total;
}
