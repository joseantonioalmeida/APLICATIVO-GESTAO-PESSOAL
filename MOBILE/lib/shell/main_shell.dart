import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../screens/atividades/atividades_screen.dart';
import '../screens/financeiro/financeiro_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/importancias/importancias_screen.dart';
import '../screens/perfil/perfil_screen.dart';
import '../state/app_scope.dart';
import '../widgets/comuns.dart';

/// Estrutura principal: cinco abas com navegação inferior fixa
/// (Início, Atividades, Financeiro, Importâncias e Perfil).
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  Navegacao? _nav;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final n = AppScope.of(context).navegacao;
    if (_nav != n) {
      _nav?.removeListener(_aoMudar);
      _nav = n..addListener(_aoMudar);
    }
  }

  @override
  void dispose() {
    _nav?.removeListener(_aoMudar);
    super.dispose();
  }

  void _aoMudar() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final nav = AppScope.of(context).navegacao;
    return PopScope(
      canPop: nav.aba == Aba.inicio,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) nav.irPara(Aba.inicio);
      },
      child: AnnotatedRegion<SystemUiOverlayStyle>(
        value: SystemUiOverlayStyle.light,
        child: Scaffold(
          body: IndexedStack(
            index: nav.aba.index,
            children: const [
              HomeScreen(),
              AtividadesScreen(),
              FinanceiroScreen(),
              ImportanciasScreen(),
              PerfilScreen(),
            ],
          ),
          bottomNavigationBar: BarraNavegacao(
            atual: nav.aba,
            onTap: nav.irPara,
          ),
        ),
      ),
    );
  }
}
