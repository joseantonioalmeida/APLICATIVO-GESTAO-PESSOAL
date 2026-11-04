import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'core/theme.dart';
import 'data/repositorio.dart';
import 'screens/auth/login_screen.dart';
import 'shell/main_shell.dart';
import 'state/app_scope.dart';

/// Raiz do aplicativo MinhaVida.
class MinhaVidaApp extends StatefulWidget {
  const MinhaVidaApp({super.key, required this.repositorio, this.relogio});

  final Repositorio repositorio;

  /// Fonte de data/hora (permite fixar o "agora" em testes).
  final DateTime Function()? relogio;

  @override
  State<MinhaVidaApp> createState() => _MinhaVidaAppState();
}

class _MinhaVidaAppState extends State<MinhaVidaApp> {
  final _navigatorKey = GlobalKey<NavigatorState>();
  final _navegacao = Navegacao();
  final _dados = BarramentoDados();
  late bool _logado = widget.repositorio.usuario != null;

  @override
  void initState() {
    super.initState();
    // Token recusado pelo servidor: volta ao login.
    widget.repositorio.aoSessaoExpirada = () {
      if (mounted && _logado) _sair();
    };
  }

  void _entrar() {
    _navigatorKey.currentState?.popUntil((r) => r.isFirst);
    _navegacao.irPara(Aba.inicio);
    setState(() => _logado = true);
  }

  void _sair() {
    _navigatorKey.currentState?.popUntil((r) => r.isFirst);
    _dados.mudou();
    setState(() => _logado = false);
  }

  @override
  Widget build(BuildContext context) {
    return AppScope(
      repositorio: widget.repositorio,
      navegacao: _navegacao,
      dados: _dados,
      relogio: widget.relogio ?? DateTime.now,
      aoEntrar: _entrar,
      aoSair: _sair,
      child: MaterialApp(
        title: 'MinhaVida',
        debugShowCheckedModeBanner: false,
        navigatorKey: _navigatorKey,
        theme: AppTema.escuro(),
        darkTheme: AppTema.escuro(),
        themeMode: ThemeMode.dark,
        locale: const Locale('pt', 'BR'),
        supportedLocales: const [Locale('pt', 'BR')],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        home: _logado
            ? MainShell(key: ValueKey(widget.repositorio.usuario?.id))
            : const LoginScreen(),
      ),
    );
  }
}
