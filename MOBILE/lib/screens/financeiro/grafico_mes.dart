import 'package:flutter/material.dart';

import '../../core/theme.dart';
import '../../models/modelos.dart';

/// Gráfico de barras agrupadas (receitas x despesas) por dia do mês.
class GraficoMes extends StatelessWidget {
  const GraficoMes({
    super.key,
    required this.resumo,
    required this.selecionado,
    required this.aoSelecionar,
  });
  final ResumoFinanceiro resumo;
  final int selecionado;
  final ValueChanged<int> aoSelecionar;

  static const double _alturaGrafico = 130;
  static const double _margemEsquerda = 34;
  static const double _alturaEixo = 18;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Gráfico de receitas e despesas por dia',
      child: LayoutBuilder(
        builder: (context, c) {
          final largura = c.maxWidth;
          return GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTapDown: (d) => _selecionar(d.localPosition.dx, largura),
            onHorizontalDragUpdate: (d) =>
                _selecionar(d.localPosition.dx, largura),
            child: SizedBox(
              height: _alturaGrafico + _alturaEixo,
              width: largura,
              child: CustomPaint(painter: _PintorGrafico(resumo, selecionado)),
            ),
          );
        },
      ),
    );
  }

  void _selecionar(double dx, double largura) {
    final area = largura - _margemEsquerda;
    final n = resumo.dias.length;
    final i = ((dx - _margemEsquerda) / (area / n)).floor();
    if (i >= 0 && i < n) aoSelecionar(i + 1);
  }
}

class _PintorGrafico extends CustomPainter {
  _PintorGrafico(this.r, this.selecionado);
  final ResumoFinanceiro r;
  final int selecionado;

  static String _rotuloEixo(int centavos) {
    if (centavos == 0) return '0';
    final v = centavos / 100;
    if (v >= 1000) {
      final k = v / 1000;
      return '${k.toStringAsFixed(k >= 10 ? 0 : 1).replaceAll('.', ',')}k';
    }
    return v.toStringAsFixed(0);
  }

  @override
  void paint(Canvas canvas, Size size) {
    const margem = GraficoMes._margemEsquerda;
    const altura = GraficoMes._alturaGrafico;
    final area = size.width - margem;
    final n = r.dias.length;
    final grupo = area / n;

    var maximo = 0;
    for (final d in r.dias) {
      if (d.receitas > maximo) maximo = d.receitas;
      if (d.despesas > maximo) maximo = d.despesas;
    }
    if (maximo == 0) maximo = 100;

    final grade = Paint()
      ..color = Cores.borda
      ..strokeWidth = 1;
    final estiloEixo = TextStyle(
      fontFamily: AppTema.fonte,
      fontSize: 10,
      color: Cores.textoSuave.withValues(alpha: 0.8),
    );

    void texto(
      String t,
      Offset o, {
      bool direita = false,
      bool centro = false,
    }) {
      final tp = TextPainter(
        text: TextSpan(text: t, style: estiloEixo),
        textDirection: TextDirection.ltr,
      )..layout();
      var dx = o.dx;
      if (direita) dx -= tp.width;
      if (centro) dx -= tp.width / 2;
      tp.paint(canvas, Offset(dx, o.dy - tp.height / 2));
    }

    // Linhas de grade e rótulos do eixo Y (0, 50% e 100%).
    for (final f in [0.0, 0.5, 1.0]) {
      final y = altura - altura * f;
      canvas.drawLine(Offset(margem, y), Offset(size.width, y), grade);
      texto(
        _rotuloEixo((maximo * f).round()),
        Offset(margem - 6, y),
        direita: true,
      );
    }

    // Faixa do dia selecionado.
    final sel = (selecionado - 1).clamp(0, n - 1);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(margem + sel * grupo, 0, grupo, altura),
        const Radius.circular(3),
      ),
      Paint()..color = Cores.primaria.withValues(alpha: 0.12),
    );

    final larguraBarra = (grupo * 0.36).clamp(1.5, 8.0);
    final pr = Paint()..color = Cores.sucesso;
    final pd = Paint()..color = Cores.perigo;
    for (var i = 0; i < n; i++) {
      final d = r.dias[i];
      final cx = margem + i * grupo + grupo / 2;
      if (d.receitas > 0) {
        final h = (d.receitas / maximo * altura).clamp(2.0, altura);
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(cx - larguraBarra, altura - h, larguraBarra, h),
            const Radius.circular(1.5),
          ),
          pr,
        );
      }
      if (d.despesas > 0) {
        final h = (d.despesas / maximo * altura).clamp(2.0, altura);
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(cx, altura - h, larguraBarra, h),
            const Radius.circular(1.5),
          ),
          pd,
        );
      }
    }

    // Rótulos do eixo X: 1, 5, 10, ... e o último dia.
    for (var d = 1; d <= n; d++) {
      if (d == 1 || d % 5 == 0 || d == n) {
        if (n - d < 3 && d != n) continue; // evita sobreposição com o último
        texto(
          '$d',
          Offset(margem + (d - 1) * grupo + grupo / 2, altura + 11),
          centro: true,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _PintorGrafico old) =>
      old.r != r || old.selecionado != selecionado;
}
