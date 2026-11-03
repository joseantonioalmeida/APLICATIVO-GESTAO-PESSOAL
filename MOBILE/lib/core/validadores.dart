import 'formatadores.dart';

/// Regras de validação compartilhadas pelos formulários.
class Valida {
  static final _email = RegExp(
    r"^[A-Za-z0-9._%+\-']+@[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?)+$",
  );

  static bool emailValido(String v) => _email.hasMatch(v.trim());

  /// Nome (3 a 100 caracteres, sem contar espaços nas extremidades).
  static String? nome(String v, String mensagemVazio) {
    final t = v.trim();
    if (t.isEmpty) return mensagemVazio;
    if (t.length < 3) return 'O nome deve ter no mínimo 3 caracteres';
    if (t.length > 100) return 'O nome deve ter no máximo 100 caracteres';
    return null;
  }

  static const mensagemSenhaCurta =
      'A senha informada não atende os requisitos necessários de 8 caracteres';

  static String? senha(String v) {
    if (v.isEmpty) return 'Informe sua senha';
    if (v.length < 8) return mensagemSenhaCurta;
    return null;
  }

  /// Valor monetário > 0 com até 2 casas. Devolve (centavos, erro).
  static (int?, String?) valor(
    String v, {
    required String mensagemInvalido,
    String mensagemCasas = 'Informe um valor com até duas casas decimais',
  }) {
    try {
      final c = Conv.centavos(v);
      if (c == null || c <= 0) return (null, mensagemInvalido);
      return (c, null);
    } on FormatException {
      return (null, mensagemCasas);
    }
  }
}
