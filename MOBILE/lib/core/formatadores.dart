import 'package:intl/intl.dart';

/// Funções de formatação e conversão no padrão brasileiro.
/// Valores monetários trafegam como inteiros em centavos (sem erro de ponto flutuante).
class Fmt {
  static final _moeda = NumberFormat.currency(
    locale: 'pt_BR',
    symbol: 'R\$',
    decimalDigits: 2,
  );

  /// 122035 -> "R$ 1.220,35" (usa espaço comum).
  static String moeda(int centavos) =>
      _moeda.format(centavos / 100).replaceAll(' ', ' ');

  /// Sem o símbolo: 9990 -> "99,90".
  static String valorSemSimbolo(int centavos) =>
      NumberFormat.decimalPatternDigits(
        locale: 'pt_BR',
        decimalDigits: 2,
      ).format(centavos / 100);

  /// "+ R$ 2.450,75" / "− R$ 245,30".
  static String moedaComSinal(int centavos, {required bool entrada}) =>
      '${entrada ? '+' : '−'} ${moeda(centavos)}';

  static String data(DateTime d) => DateFormat('dd/MM/yyyy').format(d);
  static String dataCurta(DateTime d) => DateFormat('dd/MM').format(d);

  static String diaSemana(DateTime d) {
    final s = DateFormat('EEEE', 'pt_BR').format(d);
    return s[0].toUpperCase() + s.substring(1);
  }

  /// "29 de setembro de 2025"
  static String dataExtensa(DateTime d) =>
      DateFormat("d 'de' MMMM 'de' y", 'pt_BR').format(d);

  /// "Segunda-feira, 29 de setembro de 2025"
  static String dataCompleta(DateTime d) =>
      '${diaSemana(d)}, ${dataExtensa(d)}';

  /// "Setembro de 2025"
  static String mesAno(int ano, int mes) {
    final s = DateFormat("MMMM 'de' y", 'pt_BR').format(DateTime(ano, mes));
    return s[0].toUpperCase() + s.substring(1);
  }

  /// "Outubro de 2025"
  static String mesAnoData(DateTime d) => mesAno(d.year, d.month);

  /// Minutos desde 00:00 -> "08:00".
  static String hora(int minutos) {
    final h = (minutos ~/ 60).toString().padLeft(2, '0');
    final m = (minutos % 60).toString().padLeft(2, '0');
    return '$h:$m';
  }

  /// 210 -> "3h 30min"; 120 -> "2h"; 45 -> "45min"; 630 -> "10h30" no resumo.
  static String duracao(int minutos) {
    final h = minutos ~/ 60;
    final m = minutos % 60;
    if (h == 0) return '${m}min';
    if (m == 0) return '${h}h';
    return '${h}h ${m}min';
  }

  /// Versão compacta usada no indicador "Tempo planejado": 630 -> "10h30".
  static String duracaoCompacta(int minutos) {
    final h = minutos ~/ 60;
    final m = minutos % 60;
    if (m == 0) return '${h}h';
    return '${h}h${m.toString().padLeft(2, '0')}';
  }

  /// Percentual com uma casa decimal: 12.0 -> "12,0%".
  static String percentual(double v) =>
      '${NumberFormat('0.0', 'pt_BR').format(v.abs())}%';

  static DateTime somenteData(DateTime d) => DateTime(d.year, d.month, d.day);

  static bool mesmoDia(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  /// Diferença em dias de calendário (b - a).
  static int diasEntre(DateTime a, DateTime b) {
    final ua = DateTime.utc(a.year, a.month, a.day);
    final ub = DateTime.utc(b.year, b.month, b.day);
    return ub.difference(ua).inDays;
  }

  static String pluralImportancias(int n) =>
      n == 1 ? '1 importância' : '$n importâncias';
}

/// Conversões de texto digitado.
class Conv {
  /// Converte texto monetário BR ("99,90", "1.234,5", "100") em centavos.
  /// Retorna null se inválido; lança [FormatException] se tiver mais de 2 casas.
  static int? centavos(String texto) {
    var t = texto.trim().replaceAll('R\$', '').replaceAll(' ', '');
    if (t.isEmpty) return null;
    if (t.startsWith('-')) return null;
    if (t.contains(',')) {
      t = t.replaceAll('.', '').replaceAll(',', '.');
    } else if ('.'.allMatches(t).length > 1) {
      t = t.replaceAll('.', '');
    } else if (t.contains('.')) {
      // "1.234" => milhar; "1.5" / "1.50" => decimal
      final partes = t.split('.');
      if (partes[1].length == 3) t = partes.join();
    }
    if (!RegExp(r'^\d+(\.\d+)?$').hasMatch(t)) return null;
    final partes = t.split('.');
    final dec = partes.length > 1 ? partes[1] : '';
    if (dec.length > 2) throw const FormatException('casas');
    final inteiro = int.tryParse(partes[0]);
    if (inteiro == null) return null;
    final c = int.tryParse(dec.padRight(2, '0')) ?? 0;
    return inteiro * 100 + c;
  }

  /// "DD/MM/AAAA" -> data (null se inexistente).
  static DateTime? data(String texto) {
    final m = RegExp(r'^(\d{2})/(\d{2})/(\d{4})$').firstMatch(texto.trim());
    if (m == null) return null;
    final d = int.parse(m.group(1)!);
    final mes = int.parse(m.group(2)!);
    final a = int.parse(m.group(3)!);
    if (a < 1900 || a > 2200) return null;
    final dt = DateTime(a, mes, d);
    if (dt.year != a || dt.month != mes || dt.day != d) return null;
    return dt;
  }

  /// "HH:MM" -> minutos (null se inválido).
  static int? hora(String texto) {
    final m = RegExp(r'^(\d{1,2}):(\d{2})$').firstMatch(texto.trim());
    if (m == null) return null;
    final h = int.parse(m.group(1)!);
    final min = int.parse(m.group(2)!);
    if (h > 23 || min > 59) return null;
    return h * 60 + min;
  }
}
