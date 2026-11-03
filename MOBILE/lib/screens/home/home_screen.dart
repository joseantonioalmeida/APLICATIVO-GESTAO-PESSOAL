import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../models/modelos.dart';
import '../../shell/rotas.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import '../../widgets/linhas.dart';

/// Tela 4 - Início.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Timer? _timer;
  DateTime? _hojeVisto;
  final _processando = <String>{};

  @override
  void initState() {
    super.initState();
    // Acompanha a virada do dia com a tela aberta.
    _timer = Timer.periodic(
      const Duration(seconds: 20),
      (_) => _verificarDia(),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _verificarDia() {
    if (!mounted) return;
    final hoje = AppScope.of(context).hoje;
    if (_hojeVisto != null && !Fmt.mesmoDia(_hojeVisto!, hoje)) {
      setState(() => _hojeVisto = hoje);
      AppScope.of(context).dados.mudou();
    }
  }

  Future<void> _alternar(Atividade a) async {
    if (_processando.contains(a.id)) return;
    final escopo = AppScope.of(context);
    setState(() => _processando.add(a.id));
    try {
      await escopo.repositorio.alterarConclusaoAtividade(a.id, !a.concluida);
      escopo.dados.mudou();
      if (mounted) {
        mostrarMensagem(
          context,
          a.concluida ? 'Atividade reaberta' : 'Atividade concluída',
        );
      }
    } on ErroApp catch (e) {
      if (mounted) mostrarMensagem(context, e.mensagem, erro: true);
    } finally {
      if (mounted) setState(() => _processando.remove(a.id));
    }
  }

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final hoje = escopo.hoje;
    _hojeVisto ??= hoje;
    final chaveDia = '${hoje.year}-${hoje.month}-${hoje.day}';
    final nav = escopo.navegacao;
    final repo = escopo.repositorio;

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
            _Cabecalho(hoje: hoje, chave: chaveDia),
            const SizedBox(height: 14),
            Text(
              Fmt.mesAno(hoje.year, hoje.month),
              style: Txt.corpo.copyWith(
                fontWeight: FontWeight.w600,
                color: Cores.textoSuave,
              ),
            ),
            const SizedBox(height: 10),
            BlocoAsync<ResumoFinanceiro>(
              chave: chaveDia,
              carregar: () => repo.resumoMes(hoje.year, hoje.month),
              mensagemErro: 'Não foi possível carregar seus dados financeiros. Tente novamente',
              construir: (ctx, r) => _IndicadoresMes(resumo: r, hoje: hoje),
            ),
            const SizedBox(height: 12),
            BlocoAsync<int>(
              chave: chaveDia,
              alturaCarregando: 40,
              carregar: repo.totalAtrasadas,
              construir: (ctx, n) => n == 0
                  ? const SizedBox.shrink()
                  : Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _AvisoAtrasadas(quantidade: n),
                    ),
            ),
            BlocoAsync<_DadosHoje>(
              chave: chaveDia,
              mensagemErro:
                  'Não foi possível carregar suas atividades. Tente novamente',
              carregar: () async {
                final c = await repo.consultarAtividades(
                  FiltroAtividades(data: hoje),
                  limite: 1000,
                );
                final p = await repo.pendenciasAnteriores();
                return _DadosHoje(c, p);
              },
              construir: (ctx, d) => _CartaoHoje(
                hoje: hoje,
                dados: d,
                processando: _processando,
                aoAlternar: _alternar,
              ),
            ),
            const SizedBox(height: 14),
            BlocoAsync<ResumoDia>(
              chave: chaveDia,
              carregar: () => repo.resumoDia(hoje),
              mensagemErro: 'Não foi possível carregar seus dados financeiros. Tente novamente',
              construir: (ctx, r) => _ResumoDia(resumo: r),
            ),
            const SizedBox(height: 14),
            _AcessosRapidos(hoje: hoje),
            const SizedBox(height: 22),
            _TituloSecao(
              'Movimentações recentes',
              acao: 'Ver todas',
              onAcao: () => nav.ir(
                IntencaoAba(
                  Aba.financeiro,
                  ano: hoje.year,
                  mes: hoje.month,
                  abrirMovimentacoes: true,
                ),
              ),
            ),
            const SizedBox(height: 10),
            BlocoAsync<ConsultaMov>(
              chave: chaveDia,
              mensagemErro: 'Não foi possível carregar suas movimentações. Tente novamente',
              carregar: () => repo.consultarMovimentacoes(
                FiltroMov(ano: hoje.year, mes: hoje.month),
                limite: 5,
              ),
              construir: (ctx, c) => _MovimentacoesRecentes(consulta: c),
            ),
            const SizedBox(height: 22),
            _TituloSecao(
              'Próximas importâncias',
              acao: 'Ver todas',
              onAcao: () => nav.ir(
                const IntencaoAba(
                  Aba.importancias,
                  filtroImportancia: FiltroImportancia.todos,
                ),
              ),
            ),
            const SizedBox(height: 10),
            BlocoAsync<List<Importancia>>(
              chave: chaveDia,
              mensagemErro: 'Não foi possível carregar suas importâncias. Tente novamente',
              carregar: () => repo.proximasImportancias(limite: 3),
              construir: (ctx, l) =>
                  _ProximasImportancias(itens: l, hoje: hoje),
            ),
          ],
        ),
      ),
    );
  }
}

class _DadosHoje {
  _DadosHoje(this.consulta, this.pendencias);
  final ConsultaAtividades consulta;
  final PendenciasAnteriores pendencias;
}

// ---------------------------------------------------------------- Cabeçalho
class _Cabecalho extends StatelessWidget {
  const _Cabecalho({required this.hoje, required this.chave});
  final DateTime hoje;
  final String chave;

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final u = escopo.repositorio.usuario;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Olá, ${u?.primeiroNome ?? ''}!',
                style: Txt.tituloTela.copyWith(fontSize: 24),
              ),
              const SizedBox(height: 4),
              Text(
                Fmt.dataCompleta(hoje),
                style: Txt.rotulo.copyWith(fontSize: 14, height: 1.3),
              ),
            ],
          ),
        ),
        const SizedBox(width: 10),
        BlocoAsync<int>(
          chave: chave,
          alturaCarregando: 44,
          carregar: escopo.repositorio.totalNaoLidas,
          mensagemErro: '',
          construir: (ctx, n) => _Sino(naoLidas: n),
        ),
        const SizedBox(width: 10),
        GestureDetector(
          onTap: () => escopo.navegacao.irPara(Aba.perfil),
          child: Container(
            width: 44,
            height: 44,
            alignment: Alignment.center,
            decoration: const BoxDecoration(
              color: Cores.selecionado,
              shape: BoxShape.circle,
            ),
            child: Text(
              u?.iniciais ?? '',
              style: Txt.corpoNegrito.copyWith(
                color: Cores.primaria,
                fontSize: 14,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _Sino extends StatelessWidget {
  const _Sino({required this.naoLidas});
  final int naoLidas;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => abrirNotificacoes(context),
      child: Semantics(
        label: naoLidas > 0
            ? 'Notificações, $naoLidas não lidas'
            : 'Notificações',
        child: Container(
          width: 44,
          height: 44,
          decoration: const BoxDecoration(
            color: Cores.cartao,
            shape: BoxShape.circle,
          ),
          child: Stack(
            alignment: Alignment.center,
            children: [
              const Icon(
                Icons.notifications_none,
                size: 20,
                color: Cores.texto,
              ),
              if (naoLidas > 0)
                Positioned(
                  top: 11,
                  right: 12,
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Cores.perigo,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// -------------------------------------------------------------- Indicadores
class _IndicadoresMes extends StatelessWidget {
  const _IndicadoresMes({required this.resumo, required this.hoje});
  final ResumoFinanceiro resumo;
  final DateTime hoje;

  @override
  Widget build(BuildContext context) {
    final nav = AppScope.of(context).navegacao;
    final repo = AppScope.of(context).repositorio;
    final c = resumo.compDespesas;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Cartao(
          raio: 22,
          padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
          onTap: () => nav.ir(
            IntencaoAba(Aba.financeiro, ano: hoje.year, mes: hoje.month),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Saldo do mês', style: Txt.rotulo.copyWith(fontSize: 14)),
              const SizedBox(height: 8),
              Text(
                Fmt.moeda(resumo.saldo),
                style: Txt.titulo.copyWith(
                  fontSize: 36,
                  color: resumo.saldo < 0 ? Cores.perigo : Cores.texto,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Receitas ${Fmt.moeda(resumo.receitas)} – Despesas ${Fmt.moeda(resumo.despesas)}',
                style: Txt.pequeno.copyWith(fontSize: 12.5),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: Cartao(
                  raio: 22,
                  padding: const EdgeInsets.all(16),
                  onTap: () => nav.ir(
                    IntencaoAba(
                      Aba.financeiro,
                      ano: hoje.year,
                      mes: hoje.month,
                      tipoMov: TipoMov.despesa,
                      abrirMovimentacoes: true,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Text(
                              'Despesas do mês',
                              style: Txt.rotulo.copyWith(fontSize: 13),
                            ),
                          ),
                          const Icon(
                            Icons.north_east,
                            size: 11,
                            color: Cores.perigo,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            'Saída',
                            style: Txt.pequeno.copyWith(
                              color: Cores.perigo,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        Fmt.moeda(resumo.despesas),
                        style: Txt.titulo.copyWith(fontSize: 21),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        textoComparacao(c, gasto: true),
                        style: Txt.pequeno.copyWith(fontSize: 12.5),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: BlocoAsync<int>(
                  chave: '${hoje.year}-${hoje.month}',
                  carregar: () =>
                      repo.totalPendentesDoMes(hoje.year, hoje.month),
                  construir: (ctx, n) => Cartao(
                    raio: 22,
                    padding: const EdgeInsets.all(16),
                    onTap: () => nav.ir(
                      const IntencaoAba(
                        Aba.importancias,
                        filtroImportancia: FiltroImportancia.mes,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Importâncias pendentes',
                          style: Txt.rotulo.copyWith(fontSize: 13),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          n == 1 ? '1 pendente' : '$n pendentes',
                          style: Txt.titulo.copyWith(fontSize: 21),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Em ${Fmt.mesAno(hoje.year, hoje.month).toLowerCase()}, incluindo atrasadas',
                          style: Txt.pequeno.copyWith(fontSize: 12.5),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// "Aumento de gastos de 8,0% vs. 01–29/08", "Sem base de comparação"...
String textoComparacao(Comparacao c, {required bool gasto}) {
  if (c.mensagem != null) return c.mensagem!;
  final p = c.percentual;
  if (p == null) return '';
  final vs = ' vs. ${c.intervalo}';
  if (p == 0) return 'Estável$vs';
  if (p > 0) {
    return '${gasto ? 'Aumento de gastos de' : 'Aumento de'} ${Fmt.percentual(p)}$vs';
  }
  return '${gasto ? 'Redução de gastos de' : 'Redução de'} ${Fmt.percentual(p)}$vs';
}

class _AvisoAtrasadas extends StatelessWidget {
  const _AvisoAtrasadas({required this.quantidade});
  final int quantidade;

  @override
  Widget build(BuildContext context) {
    final nav = AppScope.of(context).navegacao;
    return Cartao(
      raio: 18,
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      child: Row(
        children: [
          const Icon(
            Icons.warning_amber_rounded,
            color: Cores.perigo,
            size: 22,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              quantidade == 1
                  ? 'Você tem 1 importância atrasada'
                  : 'Você tem $quantidade importâncias atrasadas',
              style: Txt.corpo.copyWith(
                fontWeight: FontWeight.w600,
                fontSize: 14.5,
              ),
            ),
          ),
          GestureDetector(
            onTap: () => nav.ir(
              const IntencaoAba(
                Aba.importancias,
                filtroImportancia: FiltroImportancia.atrasados,
              ),
            ),
            child: Text(
              'Ver atrasadas',
              style: Txt.link.copyWith(fontSize: 13.5),
            ),
          ),
        ],
      ),
    );
  }
}

// --------------------------------------------------------------------- Hoje
class _CartaoHoje extends StatelessWidget {
  const _CartaoHoje({
    required this.hoje,
    required this.dados,
    required this.processando,
    required this.aoAlternar,
  });
  final DateTime hoje;
  final _DadosHoje dados;
  final Set<String> processando;
  final ValueChanged<Atividade> aoAlternar;

  @override
  Widget build(BuildContext context) {
    final nav = AppScope.of(context).navegacao;
    final c = dados.consulta;
    final todas = [...c.itens];
    // Pendentes primeiro; depois concluídas; por horário inicial.
    todas.sort((a, b) {
      if (a.concluida != b.concluida) return a.concluida ? 1 : -1;
      return a.inicio.compareTo(b.inicio);
    });
    final previa = todas.take(3).toList();
    final progresso = c.total == 0 ? 0.0 : c.concluidas / c.total;
    final p = dados.pendencias;

    return Cartao(
      raio: 22,
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Hoje', style: Txt.secao.copyWith(fontSize: 20)),
                    const SizedBox(height: 2),
                    Text(
                      Fmt.dataCompleta(hoje),
                      style: Txt.rotulo.copyWith(fontSize: 13.5, height: 1.3),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              GestureDetector(
                onTap: () => nav.ir(
                  IntencaoAba(Aba.atividades, data: hoje, limparFiltros: true),
                ),
                child: Text(
                  'Ver\ncalendário',
                  textAlign: TextAlign.left,
                  style: Txt.link.copyWith(fontSize: 13.5, height: 1.25),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (c.total == 0) ...[
            EstadoVazio(
              mensagem: 'Nenhuma atividade cadastrada para hoje',
              acao: 'Nova atividade',
              onAcao: () => abrirFormAtividade(context, data: hoje),
              icone: Icons.event_available_outlined,
            ),
          ] else ...[
            Row(
              children: [
                Expanded(
                  child: Text(
                    '${c.concluidas} de ${c.total} atividades concluídas',
                    style: Txt.corpo.copyWith(
                      fontWeight: FontWeight.w600,
                      fontSize: 14.5,
                    ),
                  ),
                ),
                Text(
                  c.pendentes == 1 ? '1 pendente' : '${c.pendentes} pendentes',
                  style: Txt.rotulo.copyWith(fontSize: 14),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: progresso,
                minHeight: 5,
                backgroundColor: Cores.borda,
                valueColor: const AlwaysStoppedAnimation(Cores.primaria),
              ),
            ),
            const SizedBox(height: 8),
            if (c.pendentes == 0)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Text(
                  'Todas as atividades de hoje foram concluídas',
                  style: Txt.corpo.copyWith(color: Cores.sucesso, fontSize: 14),
                ),
              ),
            for (final a in previa) ...[
              const DivisorFino(),
              _LinhaAtividadeHome(
                atividade: a,
                ocupado: processando.contains(a.id),
                aoAlternar: () => aoAlternar(a),
              ),
            ],
          ],
          if (p.quantidade > 0) ...[
            const DivisorFino(),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Text(
                    p.quantidade == 1
                        ? '1 pendência de dias anteriores'
                        : '${p.quantidade} pendências de dias anteriores',
                    style: Txt.rotulo.copyWith(fontSize: 14),
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: () => nav.ir(
                    IntencaoAba(
                      Aba.atividades,
                      data: p.maisAntiga,
                      situacao: SituacaoFiltro.pendentes,
                      limparFiltros: true,
                    ),
                  ),
                  child: Text(
                    'Ver\npendências',
                    style: Txt.link.copyWith(fontSize: 13.5, height: 1.25),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 12),
          Material(
            color: Cores.borda.withValues(alpha: 0.8),
            borderRadius: BorderRadius.circular(12),
            child: InkWell(
              borderRadius: BorderRadius.circular(12),
              onTap: () => nav.ir(
                IntencaoAba(Aba.atividades, data: hoje, limparFiltros: true),
              ),
              child: SizedBox(
                height: 44,
                child: Center(
                  child: Text(
                    'Ver todas as atividades',
                    style: Txt.corpo.copyWith(
                      fontWeight: FontWeight.w600,
                      fontSize: 14.5,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LinhaAtividadeHome extends StatelessWidget {
  const _LinhaAtividadeHome({
    required this.atividade,
    required this.aoAlternar,
    required this.ocupado,
  });
  final Atividade atividade;
  final VoidCallback aoAlternar;
  final bool ocupado;

  @override
  Widget build(BuildContext context) {
    final a = atividade;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 11),
      child: Row(
        children: [
          ControleConclusao(
            concluida: a.concluida,
            ocupado: ocupado,
            onTap: aoAlternar,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () => abrirDetalheAtividade(context, a.id),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    a.nome,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Txt.corpo.copyWith(
                      fontSize: 16.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    '${a.categoria} · ${Fmt.hora(a.inicio)} - ${Fmt.hora(a.fim)}',
                    style: Txt.pequeno.copyWith(fontSize: 12.5),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          TextoSituacao(
            a.concluida ? 'Concluída' : 'Pendente',
            a.concluida ? Cores.sucesso : Cores.alerta,
          ),
        ],
      ),
    );
  }
}

/// Círculo para concluir/reabrir uma atividade.
class ControleConclusao extends StatelessWidget {
  const ControleConclusao({
    super.key,
    required this.concluida,
    required this.onTap,
    this.ocupado = false,
  });
  final bool concluida;
  final VoidCallback onTap;
  final bool ocupado;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: concluida ? 'Reabrir atividade' : 'Concluir atividade',
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: ocupado ? null : onTap,
        child: SizedBox(
          width: 28,
          height: 28,
          child: Center(
            child: ocupado
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Cores.primaria,
                    ),
                  )
                : AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: concluida ? Cores.sucesso : Colors.transparent,
                      border: Border.all(
                        color: concluida
                            ? Cores.sucesso
                            : const Color(0xFF3A4256),
                        width: 2,
                      ),
                    ),
                    child: concluida
                        ? const Icon(Icons.check, size: 15, color: Cores.fundo)
                        : null,
                  ),
          ),
        ),
      ),
    );
  }
}

// ------------------------------------------------------------ Resumo do dia
class _ResumoDia extends StatelessWidget {
  const _ResumoDia({required this.resumo});
  final ResumoDia resumo;

  @override
  Widget build(BuildContext context) {
    Widget linha(String rotulo, Widget valor, {bool ultimo = false}) => Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 13),
          child: Row(
            children: [
              Expanded(
                child: Text(rotulo, style: Txt.rotulo.copyWith(fontSize: 15.5)),
              ),
              valor,
            ],
          ),
        ),
        if (!ultimo) const DivisorFino(),
      ],
    );
    final saldo = resumo.saldo;
    return Cartao(
      raio: 22,
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resumo financeiro do dia',
            style: Txt.secao.copyWith(fontSize: 18.5),
          ),
          const SizedBox(height: 6),
          linha(
            'Receitas de hoje',
            Text(
              '+ ${Fmt.moeda(resumo.receitas)}',
              style: Txt.corpoNegrito.copyWith(
                color: resumo.receitas > 0 ? Cores.sucesso : Cores.texto,
                fontSize: 16,
              ),
            ),
          ),
          linha(
            'Despesas de hoje',
            Text(
              Fmt.moeda(resumo.despesas),
              style: Txt.corpoNegrito.copyWith(fontSize: 16),
            ),
          ),
          linha(
            'Saldo do dia',
            Text(
              saldo < 0 ? '− ${Fmt.moeda(-saldo)}' : Fmt.moeda(saldo),
              style: Txt.corpoNegrito.copyWith(
                fontSize: 17.5,
                color: saldo < 0 ? Cores.perigo : Cores.texto,
              ),
            ),
            ultimo: true,
          ),
          const SizedBox(height: 4),
          Text(
            'Importâncias que vencem hoje e ainda não foram pagas não entram nas despesas.',
            style: Txt.pequeno.copyWith(fontSize: 12.5, height: 1.4),
          ),
        ],
      ),
    );
  }
}

// --------------------------------------------------------- Acessos rápidos
class _AcessosRapidos extends StatelessWidget {
  const _AcessosRapidos({required this.hoje});
  final DateTime hoje;

  @override
  Widget build(BuildContext context) {
    final nav = AppScope.of(context).navegacao;
    Widget item(IconData icone, String texto, VoidCallback onTap) => Expanded(
      child: Material(
        color: Cores.cartao,
        borderRadius: BorderRadius.circular(18),
        child: InkWell(
          borderRadius: BorderRadius.circular(18),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 12),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icone, size: 19, color: Cores.primaria),
                const SizedBox(height: 7),
                Text(
                  texto,
                  textAlign: TextAlign.center,
                  style: Txt.corpo.copyWith(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    height: 1.2,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          item(
            Icons.add,
            'Nova\natividade',
            () => abrirFormAtividade(context, data: hoje),
          ),
          const SizedBox(width: 8),
          item(
            Icons.account_balance_wallet_outlined,
            'Receita ou\ndespesa',
            () => escolherReceitaOuDespesa(context),
          ),
          const SizedBox(width: 8),
          item(
            Icons.calendar_today_outlined,
            'Importância',
            () => abrirFormImportancia(context),
          ),
          const SizedBox(width: 8),
          item(Icons.bar_chart, 'Resumo\nfinanceiro', () {
            nav.ir(
              IntencaoAba(Aba.financeiro, ano: hoje.year, mes: hoje.month),
            );
          }),
        ],
      ),
    );
  }
}

class _TituloSecao extends StatelessWidget {
  const _TituloSecao(this.titulo, {this.acao, this.onAcao});
  final String titulo;
  final String? acao;
  final VoidCallback? onAcao;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(titulo, style: Txt.secao.copyWith(fontSize: 18.5)),
        ),
        if (acao != null)
          GestureDetector(
            onTap: onAcao,
            child: Text(acao!, style: Txt.link.copyWith(fontSize: 13.5)),
          ),
      ],
    );
  }
}

class _MovimentacoesRecentes extends StatelessWidget {
  const _MovimentacoesRecentes({required this.consulta});
  final ConsultaMov consulta;

  @override
  Widget build(BuildContext context) {
    if (consulta.itens.isEmpty) {
      return const Cartao(
        child: EstadoVazio(
          mensagem: 'Nenhuma movimentação cadastrada neste mês',
          icone: Icons.receipt_long_outlined,
        ),
      );
    }
    return Cartao(
      raio: 22,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Column(
        children: [
          for (var i = 0; i < consulta.itens.length; i++) ...[
            if (i > 0) const DivisorFino(),
            LinhaMovimentacao(
              mov: consulta.itens[i],
              onTap: () =>
                  abrirDetalheMovimentacao(context, consulta.itens[i].id),
            ),
          ],
        ],
      ),
    );
  }
}

class _ProximasImportancias extends StatelessWidget {
  const _ProximasImportancias({required this.itens, required this.hoje});
  final List<Importancia> itens;
  final DateTime hoje;

  @override
  Widget build(BuildContext context) {
    if (itens.isEmpty) {
      return const Cartao(
        child: EstadoVazio(
          mensagem:
              'Nenhuma importância pendente para hoje ou para os próximos dias',
          icone: Icons.event_outlined,
        ),
      );
    }
    return Cartao(
      raio: 22,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Column(
        children: [
          for (var i = 0; i < itens.length; i++) ...[
            if (i > 0) const DivisorFino(),
            _LinhaProxima(imp: itens[i], hoje: hoje),
          ],
        ],
      ),
    );
  }
}

class _LinhaProxima extends StatelessWidget {
  const _LinhaProxima({required this.imp, required this.hoje});
  final Importancia imp;
  final DateTime hoje;

  @override
  Widget build(BuildContext context) {
    final prazo = PrazoImportancia.de(imp, hoje)!;
    final quando = imp.horario == null
        ? Fmt.data(imp.data)
        : '${Fmt.data(imp.data)} · ${Fmt.hora(imp.horario!)}';
    return InkWell(
      onTap: () => abrirDetalheImportancia(context, imp.id),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 11),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    imp.nome,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Txt.corpo.copyWith(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(quando, style: Txt.pequeno.copyWith(fontSize: 12.5)),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  imp.temDespesa ? Fmt.moeda(imp.valorPrevisto) : 'Sem despesa',
                  style: imp.temDespesa
                      ? Txt.corpoNegrito.copyWith(fontSize: 15)
                      : Txt.pequeno.copyWith(fontSize: 13),
                ),
                const SizedBox(height: 2),
                TextoSituacao(prazo.texto, prazo.cor, tamanho: 12.5),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
