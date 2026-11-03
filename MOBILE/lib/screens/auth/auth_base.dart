import 'package:flutter/material.dart';

import '../../core/theme.dart';
import '../../widgets/comuns.dart';

/// Estrutura comum das telas de autenticação: conteúdo rolável + rodapé fixo.
class AuthScaffold extends StatelessWidget {
  const AuthScaffold({
    super.key,
    required this.children,
    required this.rodape,
    this.voltar = false,
    this.passo,
    this.topo = 0,
  });
  final List<Widget> children;
  final Widget rodape;
  final bool voltar;
  final int? passo;
  final double topo;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                keyboardDismissBehavior:
                    ScrollViewKeyboardDismissBehavior.onDrag,
                padding: const EdgeInsets.fromLTRB(24, 26, 24, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (voltar) const BotaoVoltar() else SizedBox(height: topo),
                    if (passo != null) ...[
                      const SizedBox(height: 14),
                      IndicadorPassos(passo: passo!),
                      const SizedBox(height: 28),
                    ],
                    ...children,
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 28, top: 8),
              child: rodape,
            ),
          ],
        ),
      ),
    );
  }
}

/// "Passo 1 de 3" com três barras de progresso.
class IndicadorPassos extends StatelessWidget {
  const IndicadorPassos({super.key, required this.passo, this.total = 3});
  final int passo;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 4),
        Row(
          children: [
            for (var i = 1; i <= total; i++) ...[
              Expanded(
                child: Container(
                  height: 4,
                  decoration: BoxDecoration(
                    color: i <= passo ? Cores.primaria : Cores.borda,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
              if (i < total) const SizedBox(width: 6),
            ],
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Passo $passo de $total',
          style: Txt.rotulo.copyWith(fontSize: 14),
        ),
      ],
    );
  }
}

/// Logotipo "MinhaVida" com o ícone de barras.
class Logotipo extends StatelessWidget {
  const Logotipo({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            color: Cores.primaria,
            borderRadius: BorderRadius.circular(18),
          ),
          child: CustomPaint(painter: _BarrasPainter()),
        ),
        const SizedBox(height: 14),
        RichText(
          text: const TextSpan(
            style: TextStyle(
              fontFamily: AppTema.fonte,
              fontSize: 26,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.5,
            ),
            children: [
              TextSpan(
                text: 'Minha',
                style: TextStyle(color: Cores.texto),
              ),
              TextSpan(
                text: 'Vida',
                style: TextStyle(color: Cores.primaria),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _BarrasPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = Cores.sobrePrimaria
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;
    final c = size.center(Offset.zero);
    const alturas = [10.0, 18.0, 13.0];
    for (var i = 0; i < 3; i++) {
      final x = c.dx - 9 + i * 9;
      canvas.drawLine(
        Offset(x, c.dy + alturas[i] / 2),
        Offset(x, c.dy - alturas[i] / 2),
        p,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}
