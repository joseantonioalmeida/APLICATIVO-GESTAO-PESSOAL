import 'package:flutter/material.dart';

/// Paleta extraída dos protótipos das 13 telas.
class Cores {
  static const fundo = Color(0xFF0A0E17);
  static const cartao = Color(0xFF111828);
  static const borda = Color(0xFF1B2234);
  static const primaria = Color(0xFF8DB4FF);
  static const sobrePrimaria = Color(0xFF0A0E17);
  static const texto = Color(0xFFFFFFFF);
  static const textoSuave = Color(0xFFA9AFBD);
  static const dica = Color(0xFF6B7385);
  static const sucesso = Color(0xFF34D399);
  static const perigo = Color(0xFFFF7E96);
  static const alerta = Color(0xFFFCC431);
  static const selecionado = Color(0xFF1B2741);
}

class AppTema {
  static const fonte = 'PlusJakartaSans';

  static ThemeData escuro() {
    final base = ThemeData(
      brightness: Brightness.dark,
      useMaterial3: true,
      fontFamily: fonte,
      scaffoldBackgroundColor: Cores.fundo,
      canvasColor: Cores.fundo,
      colorScheme: const ColorScheme.dark(
        primary: Cores.primaria,
        onPrimary: Cores.sobrePrimaria,
        secondary: Cores.primaria,
        surface: Cores.cartao,
        onSurface: Cores.texto,
        error: Cores.perigo,
      ),
    );
    return base.copyWith(
      appBarTheme: const AppBarTheme(
        backgroundColor: Cores.fundo,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      dividerColor: Cores.borda,
      textSelectionTheme: const TextSelectionThemeData(
        cursorColor: Cores.primaria,
        selectionColor: Color(0x558DB4FF),
        selectionHandleColor: Cores.primaria,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: const Color(0xFF1B2741),
        contentTextStyle: const TextStyle(
          fontFamily: fonte,
          color: Cores.texto,
          fontWeight: FontWeight.w600,
          fontSize: 14,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: Cores.cartao,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        titleTextStyle: const TextStyle(
          fontFamily: fonte,
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: Cores.texto,
        ),
        contentTextStyle: const TextStyle(
          fontFamily: fonte,
          fontSize: 14,
          color: Cores.textoSuave,
          height: 1.4,
        ),
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: Cores.cartao,
        modalBackgroundColor: Cores.cartao,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
      ),
      popupMenuTheme: PopupMenuThemeData(
        color: const Color(0xFF161E30),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        textStyle: const TextStyle(
          fontFamily: fonte,
          color: Cores.texto,
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

/// Estilos de texto reutilizados nas telas.
class Txt {
  static const _f = AppTema.fonte;

  static const titulo = TextStyle(
    fontFamily: _f,
    fontSize: 30,
    fontWeight: FontWeight.w800,
    color: Cores.texto,
    height: 1.15,
    letterSpacing: -0.5,
  );
  static const tituloTela = TextStyle(
    fontFamily: _f,
    fontSize: 26,
    fontWeight: FontWeight.w800,
    color: Cores.texto,
    letterSpacing: -0.4,
  );
  static const tituloForm = TextStyle(
    fontFamily: _f,
    fontSize: 22,
    fontWeight: FontWeight.w800,
    color: Cores.texto,
    letterSpacing: -0.3,
  );
  static const secao = TextStyle(
    fontFamily: _f,
    fontSize: 18,
    fontWeight: FontWeight.w800,
    color: Cores.texto,
  );
  static const subtitulo = TextStyle(
    fontFamily: _f,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: Cores.textoSuave,
    height: 1.35,
  );
  static const rotulo = TextStyle(
    fontFamily: _f,
    fontSize: 13,
    fontWeight: FontWeight.w500,
    color: Cores.textoSuave,
  );
  static const corpo = TextStyle(
    fontFamily: _f,
    fontSize: 15,
    fontWeight: FontWeight.w500,
    color: Cores.texto,
  );
  static const corpoNegrito = TextStyle(
    fontFamily: _f,
    fontSize: 15,
    fontWeight: FontWeight.w700,
    color: Cores.texto,
  );
  static const pequeno = TextStyle(
    fontFamily: _f,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    color: Cores.textoSuave,
    height: 1.3,
  );
  static const link = TextStyle(
    fontFamily: _f,
    fontSize: 14,
    fontWeight: FontWeight.w700,
    color: Cores.primaria,
  );
}
