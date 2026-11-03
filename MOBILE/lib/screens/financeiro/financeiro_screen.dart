import 'package:flutter/material.dart';

import '../../core/categorias.dart';
import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../models/modelos.dart';
import '../../shell/rotas.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import '../../widgets/linhas.dart';
import '../home/home_screen.dart' show textoComparacao;
import 'grafico_mes.dart';

/// Tela 9 - Financeiro.
class FinanceiroScreen extends StatefulWidget {
  const FinanceiroScreen({super.key});

  @override
  State<FinanceiroScreen> createState() => _FinanceiroScreenState();
}

class _FinanceiroScreenState extends State<FinanceiroScreen> {
  late int _ano;
  late int _mes;
  bool _iniciado = false;
  int? _diaSelecionado;
  AppScope? _escopo;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final e = AppScope.of(context);
    if (_escopo != e) {
      _escopo?.navegacao.removeListener(_aoNavegar);
      _escopo = e;
      e.navegacao.addListener(_aoNavegar);
    }
    if (!_iniciado) {
      _iniciado = true;
      _ano = e.hoje.year;
      _mes = e.hoje.month;
      WidgetsBinding.instance.addPostFrameCallback((_) => _aoNavegar());
    }
  }

  @override
  void dispose() {
    _escopo?.navegacao.removeListener(_aoNavegar);
    super.dispose();
  }

  void _aoNavegar() {
    final e = _escopo;
    if (e == null || !mounted) return;
    final it = e.navegacao.consumir(Aba.financeiro);
    if (it == null) return;
    setState(() {
      if (it.ano != null && it.mes != null) {
        _ano = it.ano!;
        _mes = it.mes!;
        _diaSelecionado = null;
      }
    });
    if (it.abrirMovimentacoes) {
      abrirMovimentacoes(
        context,
        ano: _ano,
        mes: _mes,
        tipo: it.tipoMov,
        categoria: it.categoriaMov,
      );
    }
  }

  void _mudarMes(int delta) {
    final d = DateTime(_ano, _mes + delta);
    setState(() {
      _ano = d.year;
      _mes = d.month;
      _diaSelecionado = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final repo = escopo.repositorio;
    final chave = '$_ano-$_mes';

    return SafeArea(
      bottom: false,
      child: RefreshIndicator(
        color: Cores.primaria,
        backgroundColor: Cores.cartao,
        onRefresh: () async => escopo.dados.mudou(),
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
          children: [
            const Text('Financeiro', style: Txt.tituloTela),
            const SizedBox(height: 10),
            Row(
              children: [
                IconButton(
                  tooltip: 'Mês anterior',
                  onPressed: () => _mudarMes(-1),
                  icon: const Icon(Icons.chevron_left, color: Cores.texto),
                  visualDensity: VisualDensity.compact,
                ),
                Expanded(
                  child: Text(
                    Fmt.mesAno(_ano, _mes),
                    textAlign: TextAlign.center,
                    style: Txt.corpoNegrito.copyWith(fontSize: 17),
                  ),
                ),
                IconButton(
                  tooltip: 'Próximo mês',
                  onPressed: () => _mudarMes(1),
                  icon: const Icon(Icons.chevron_right, color: Cores.texto),
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
            const SizedBox(height: 6),
            BlocoAsync<ResumoFinanceiro>(
              chave: chave,
              alturaCarregando: 380,
              mensagemErro: 'Não foi possível carregar seus dados financeiros. Tente novamente',
              carregar: () => repo.resumoMes(_ano, _mes),
              construir: (ctx, r) => Column(
                children: [
                  _CartaoSaldo(resumo: r),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _BotaoCadastro(
                          texto: 'Cadastrar receita',
                          cor: Cores.sucesso,
                          onTap: () => abrirFormReceita(context),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _BotaoCadastro(
                          texto: 'Cadastrar despesa',
                          cor: Cores.perigo,
                          onTap: () => abrirFormDespesa(context),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  _CartaoGrafico(
                    resumo: r,
                    selecionado: _diaSelecionado ?? _diaPadrao(r, escopo.hoje),
                    aoSelecionar: (d) => setState(() => _diaSelecionado = d),
                  ),
                  const SizedBox(height: 22),
                  _CategoriasDespesas(resumo: r),
                ],
              ),
            ),
            const SizedBox(height: 22),
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Últimas movimentações',
                    style: Txt.secao.copyWith(fontSize: 18.5),
                  ),
                ),
                GestureDetector(
                  onTap: () =>
                      abrirMovimentacoes(context, ano: _ano, mes: _mes),
                  child: Text(
                    'Ver todas',
                    style: Txt.link.copyWith(fontSize: 13.5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            BlocoAsync<ConsultaMov>(
              chave: chave,
              mensagemErro: 'Não foi possível carregar seus dados financeiros. Tente novamente',
              carregar: () => repo.consultarMovimentacoes(
                FiltroMov(ano: _ano, mes: _mes),
                limite: 5,
              ),
              construir: (ctx, c) => c.itens.isEmpty
                  ? Cartao(
                      child: EstadoVazio(
                        mensagem: 'Nenhuma movimentação cadastrada neste mês',
                        icone: Icons.receipt_long_outlined,
                        acao: 'Cadastrar receita',
                        onAcao: () => abrirFormReceita(context),
                      ),
                    )
                  : Cartao(
                      raio: 22,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 4,
                      ),
                      child: Column(
                        children: [
                          for (var i = 0; i < c.itens.length; i++) ...[
                            if (i > 0) const DivisorFino(),
                            LinhaMovimentacao(
                              mov: c.itens[i],
                              detalhada: true,
                              onTap: () => abrirDetalheMovimentacao(
                                context,
                                c.itens[i].id,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  int _diaPadrao(ResumoFinanceiro r, DateTime hoje) {
    if (r.ano == hoje.year && r.mes == hoje.month) return hoje.day;
    final comMov = r.dias.where((d) => d.receitas > 0 || d.despesas > 0);
    return comMov.isEmpty ? 1 : comMov.last.dia;
  }
}

class _CartaoSaldo extends StatelessWidget {
  const _CartaoSaldo({required this.resumo});
  final ResumoFinanceiro resumo;

  @override
  Widget build(BuildContext context) {
    Widget coluna(
      String rotulo,
      int valor,
      Color cor,
      Comparacao c,
      bool gasto,
    ) {
      return Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(rotulo, style: Txt.rotulo.copyWith(fontSize: 13)),
            const SizedBox(height: 3),
            Text(
              Fmt.moeda(valor),
              style: Txt.titulo.copyWith(
                fontSize: 19,
                color: cor,
                letterSpacing: -0.3,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              textoComparacao(c, gasto: gasto),
              style: Txt.pequeno.copyWith(fontSize: 11.5, height: 1.3),
            ),
          ],
        ),
      );
    }

    return Cartao(
      raio: 22,
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Saldo do mês',
                  style: Txt.rotulo.copyWith(fontSize: 14),
                ),
              ),
              GestureDetector(
                onTap: () => _detalhes(context),
                child: Text(
                  'Ver detalhes',
                  style: Txt.link.copyWith(fontSize: 13.5),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            resumo.saldo < 0
                ? '− ${Fmt.moeda(-resumo.saldo)}'
                : Fmt.moeda(resumo.saldo),
            style: Txt.titulo.copyWith(
              fontSize: 36,
              color: resumo.saldo < 0 ? Cores.perigo : Cores.texto,
            ),
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              coluna(
                'Receitas',
                resumo.receitas,
                Cores.sucesso,
                resumo.compReceitas,
                false,
              ),
              const SizedBox(width: 12),
              coluna(
                'Despesas',
                resumo.despesas,
                Cores.perigo,
                resumo.compDespesas,
                true,
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _detalhes(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Detalhes do saldo', style: Txt.secao),
              const SizedBox(height: 4),
              Text(Fmt.mesAno(resumo.ano, resumo.mes), style: Txt.rotulo),
              const SizedBox(height: 16),
              _LinhaDetalhe(
                'Total de receitas',
                Fmt.moeda(resumo.receitas),
                Cores.sucesso,
              ),
              _LinhaDetalhe(
                'Total de despesas',
                '− ${Fmt.moeda(resumo.despesas)}',
                Cores.perigo,
              ),
              const Divider(color: Cores.borda),
              _LinhaDetalhe(
                'Saldo do mês',
                resumo.saldo < 0
                    ? '− ${Fmt.moeda(-resumo.saldo)}'
                    : Fmt.moeda(resumo.saldo),
                resumo.saldo < 0 ? Cores.perigo : Cores.texto,
              ),
              const SizedBox(height: 10),
              Text(
                'Saldo do mês = receitas − despesas. Considera apenas recebimentos e '
                'pagamentos já registrados, não os valores previstos em Importâncias.',
                style: Txt.pequeno.copyWith(height: 1.4),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LinhaDetalhe extends StatelessWidget {
  const _LinhaDetalhe(this.rotulo, this.valor, this.cor);
  final String rotulo;
  final String valor;
  final Color cor;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Row(
      children: [
        Expanded(child: Text(rotulo, style: Txt.corpo)),
        Text(valor, style: Txt.corpoNegrito.copyWith(color: cor)),
      ],
    ),
  );
}

class _BotaoCadastro extends StatelessWidget {
  const _BotaoCadastro({
    required this.texto,
    required this.cor,
    required this.onTap,
  });
  final String texto;
  final Color cor;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Cores.cartao,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: SizedBox(
          height: 46,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.add, size: 16, color: cor),
              const SizedBox(width: 4),
              Flexible(
                child: Text(
                  texto,
                  overflow: TextOverflow.ellipsis,
                  style: Txt.corpoNegrito.copyWith(color: cor, fontSize: 13.5),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CartaoGrafico extends StatelessWidget {
  const _CartaoGrafico({
    required this.resumo,
    required this.selecionado,
    required this.aoSelecionar,
  });
  final ResumoFinanceiro resumo;
  final int selecionado;
  final ValueChanged<int> aoSelecionar;

  @override
  Widget build(BuildContext context) {
    final dia = resumo.dias[(selecionado - 1).clamp(0, resumo.dias.length - 1)];
    final dd = dia.dia.toString().padLeft(2, '0');
    final mm = resumo.mes.toString().padLeft(2, '0');
    return Cartao(
      raio: 22,
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  'Resumo do\nmês',
                  style: Txt.secao.copyWith(fontSize: 18.5, height: 1.15),
                ),
              ),
              const _Legenda('Receitas', Cores.sucesso),
              const SizedBox(width: 10),
              const _Legenda('Despesas', Cores.perigo),
            ],
          ),
          const SizedBox(height: 14),
          GraficoMes(
            resumo: resumo,
            selecionado: selecionado,
            aoSelecionar: aoSelecionar,
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Cores.fundo.withValues(alpha: 0.7),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Dia $dd/$mm',
                  style: Txt.corpoNegrito.copyWith(fontSize: 14),
                ),
                const SizedBox(height: 2),
                Text.rich(
                  TextSpan(
                    style: Txt.pequeno.copyWith(fontSize: 12.5),
                    children: [
                      const TextSpan(text: 'Receitas '),
                      TextSpan(
                        text: Fmt.moeda(dia.receitas),
                        style: const TextStyle(
                          color: Cores.sucesso,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const TextSpan(text: ' · Despesas '),
                      TextSpan(
                        text: Fmt.moeda(dia.despesas),
                        style: const TextStyle(
                          color: Cores.perigo,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 4),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: () => _valoresEmTexto(context),
              style: TextButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                minimumSize: const Size(0, 30),
              ),
              child: Text(
                'Ver valores por dia',
                style: Txt.link.copyWith(fontSize: 13),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _valoresEmTexto(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.of(ctx).size.height * 0.75,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 20, 24, 8),
                child: Text(
                  'Resumo do mês · ${Fmt.mesAno(resumo.ano, resumo.mes)}',
                  style: Txt.secao,
                ),
              ),
              Flexible(
                child: ListView(
                  shrinkWrap: true,
                  padding: const EdgeInsets.fromLTRB(24, 0, 24, 16),
                  children: [
                    for (final d in resumo.dias)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 5),
                        child: Row(
                          children: [
                            SizedBox(
                              width: 56,
                              child: Text(
                                '${d.dia.toString().padLeft(2, '0')}/${resumo.mes.toString().padLeft(2, '0')}',
                                style: Txt.rotulo,
                              ),
                            ),
                            Expanded(
                              child: Text(
                                'Receitas ${Fmt.moeda(d.receitas)}',
                                style: Txt.pequeno.copyWith(
                                  color: d.receitas > 0
                                      ? Cores.sucesso
                                      : Cores.textoSuave,
                                ),
                              ),
                            ),
                            Text(
                              'Despesas ${Fmt.moeda(d.despesas)}',
                              style: Txt.pequeno.copyWith(
                                color: d.despesas > 0
                                    ? Cores.perigo
                                    : Cores.textoSuave,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Legenda extends StatelessWidget {
  const _Legenda(this.texto, this.cor);
  final String texto;
  final Color cor;

  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: 8,
        height: 8,
        decoration: BoxDecoration(color: cor, shape: BoxShape.circle),
      ),
      const SizedBox(width: 5),
      Text(texto, style: Txt.pequeno.copyWith(fontSize: 12)),
    ],
  );
}

class _CategoriasDespesas extends StatelessWidget {
  const _CategoriasDespesas({required this.resumo});
  final ResumoFinanceiro resumo;

  @override
  Widget build(BuildContext context) {
    final cats = resumo.categorias;
    final previa = cats.take(5).toList();
    final maior = cats.isEmpty ? 1 : cats.first.total;

    Widget linha(CategoriaTotal c, {bool paraFolha = false}) => InkWell(
      onTap: () {
        if (paraFolha) Navigator.pop(context);
        abrirMovimentacoes(
          context,
          ano: resumo.ano,
          mes: resumo.mes,
          tipo: TipoMov.despesa,
          categoria: c.categoria,
        );
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            IconeQuadrado(
              Categorias.icone(c.categoria),
              cor: Cores.primaria,
              tamanho: 34,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          c.categoria,
                          style: Txt.corpoNegrito.copyWith(fontSize: 15.5),
                        ),
                      ),
                      Text(
                        Fmt.moeda(c.total),
                        style: Txt.corpo.copyWith(
                          fontSize: 14.5,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 7),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: resumo.despesas == 0 ? 0 : c.total / maior,
                      minHeight: 4,
                      backgroundColor: Cores.borda,
                      valueColor: const AlwaysStoppedAnimation(Cores.primaria),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                'Categorias de despesas',
                style: Txt.secao.copyWith(fontSize: 18.5),
              ),
            ),
            if (cats.length > 5)
              GestureDetector(
                onTap: () => showModalBottomSheet<void>(
                  context: context,
                  isScrollControlled: true,
                  builder: (ctx) => SafeArea(
                    child: ConstrainedBox(
                      constraints: BoxConstraints(
                        maxHeight: MediaQuery.of(ctx).size.height * 0.75,
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.fromLTRB(24, 20, 24, 8),
                            child: Text(
                              'Categorias de despesas',
                              style: Txt.secao,
                            ),
                          ),
                          Flexible(
                            child: ListView(
                              shrinkWrap: true,
                              padding: const EdgeInsets.fromLTRB(24, 0, 24, 16),
                              children: [
                                for (final c in cats) linha(c, paraFolha: true),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                child: Text(
                  'Ver todas',
                  style: Txt.link.copyWith(fontSize: 13.5),
                ),
              ),
          ],
        ),
        const SizedBox(height: 10),
        Cartao(
          raio: 22,
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
          child: cats.isEmpty
              ? const EstadoVazio(
                  mensagem: 'Nenhuma despesa registrada neste mês',
                  icone: Icons.pie_chart_outline,
                )
              : Column(children: [for (final c in previa) linha(c)]),
        ),
      ],
    );
  }
}
