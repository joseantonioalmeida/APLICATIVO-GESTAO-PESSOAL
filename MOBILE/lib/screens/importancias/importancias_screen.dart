import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/categorias.dart';
import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../models/modelos.dart';
import '../../shell/rotas.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import '../../widgets/linhas.dart';

/// Tela 7 - Importâncias.
class ImportanciasScreen extends StatefulWidget {
  const ImportanciasScreen({super.key});

  @override
  State<ImportanciasScreen> createState() => _ImportanciasScreenState();
}

class _ImportanciasScreenState extends State<ImportanciasScreen> {
  FiltroImportancia _filtro = FiltroImportancia.todos;
  late int _ano;
  late int _mes;
  bool _iniciado = false;

  final _busca = TextEditingController();
  String _termo = '';
  Timer? _debounce;
  Timer? _relogio;
  Timer? _tempoDestaque;
  DateTime? _diaVisto;
  String? _destaqueId;

  List<Importancia>? _itens;
  bool _carregando = true;
  bool _erro = false;
  int _geracao = 0;
  AppScope? _escopo;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final e = AppScope.of(context);
    if (_escopo != e) {
      _escopo?.navegacao.removeListener(_aoNavegar);
      _escopo?.dados.removeListener(_carregar);
      _escopo = e;
      e.navegacao.addListener(_aoNavegar);
      e.dados.addListener(_carregar);
    }
    if (!_iniciado) {
      _iniciado = true;
      _ano = e.hoje.year;
      _mes = e.hoje.month;
      _diaVisto = e.hoje;
      _relogio = Timer.periodic(const Duration(seconds: 20), (_) {
        final es = _escopo;
        if (es == null || !mounted) return;
        if (_diaVisto != null && !Fmt.mesmoDia(_diaVisto!, es.hoje)) {
          setState(() => _diaVisto = es.hoje);
          _carregar();
        }
      });
      _aoNavegar();
      _carregar();
    }
  }

  @override
  void dispose() {
    _escopo?.navegacao.removeListener(_aoNavegar);
    _escopo?.dados.removeListener(_carregar);
    _debounce?.cancel();
    _relogio?.cancel();
    _tempoDestaque?.cancel();
    _busca.dispose();
    super.dispose();
  }

  void _aoNavegar() {
    final e = _escopo;
    if (e == null) return;
    final it = e.navegacao.consumir(Aba.importancias);
    if (it == null) return;
    setState(() {
      if (it.filtroImportancia != null) {
        _filtro = it.filtroImportancia!;
        _busca.clear();
        _termo = '';
        _ano = e.hoje.year;
        _mes = e.hoje.month;
      }
      _destaqueId = it.destaqueId;
    });
    _tempoDestaque?.cancel();
    if (it.destaqueId != null) {
      _tempoDestaque = Timer(const Duration(seconds: 5), () {
        if (mounted) setState(() => _destaqueId = null);
      });
    }
    _carregar();
  }

  Future<void> _carregar() async {
    final e = _escopo;
    if (e == null || !mounted) return;
    final g = ++_geracao;
    setState(() {
      _carregando = _itens == null;
      _erro = false;
    });
    try {
      final r = await e.repositorio.consultarImportancias(
        _filtro,
        ano: _ano,
        mes: _mes,
        busca: _termo,
      );
      if (!mounted || g != _geracao) return;
      setState(() {
        _itens = r;
        _carregando = false;
      });
    } catch (_) {
      if (!mounted || g != _geracao) return;
      setState(() {
        _erro = true;
        _itens = null;
        _carregando = false;
      });
    }
  }

  void _mudarFiltro(FiltroImportancia f) {
    setState(() {
      _filtro = f;
      _itens = null;
    });
    _carregar();
  }

  void _mudarMes(int delta) {
    final d = DateTime(_ano, _mes + delta);
    setState(() {
      _ano = d.year;
      _mes = d.month;
    });
    _carregar();
  }

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final hoje = escopo.hoje;
    final mesAtual = _ano == hoje.year && _mes == hoje.month;
    final itens = _itens;

    return SafeArea(
      bottom: false,
      child: RefreshIndicator(
        color: Cores.primaria,
        backgroundColor: Cores.cartao,
        onRefresh: _carregar,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Importâncias', style: Txt.tituloTela),
                      SizedBox(height: 4),
                      Text(
                        'Compromissos e datas\nimportantes',
                        style: Txt.rotulo,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Material(
                  color: Cores.primaria,
                  borderRadius: BorderRadius.circular(22),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(22),
                    onTap: () => abrirFormImportancia(context),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 10,
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.add,
                            size: 16,
                            color: Cores.sobrePrimaria,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'Nova\nimportância',
                            style: Txt.corpoNegrito.copyWith(
                              color: Cores.sobrePrimaria,
                              fontSize: 14,
                              height: 1.15,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            CaixaCampo(
              altura: 44,
              child: Row(
                children: [
                  const Icon(Icons.search, size: 19, color: Cores.textoSuave),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: _busca,
                      onChanged: (t) {
                        _debounce?.cancel();
                        _debounce = Timer(
                          const Duration(milliseconds: 300),
                          () {
                            if (!mounted) return;
                            setState(() => _termo = t);
                            _carregar();
                          },
                        );
                      },
                      style: Txt.corpo.copyWith(fontSize: 15),
                      cursorColor: Cores.primaria,
                      decoration: InputDecoration(
                        hintText: 'Buscar importância',
                        hintStyle: Txt.corpo.copyWith(
                          fontSize: 15,
                          color: Cores.dica,
                          fontWeight: FontWeight.w500,
                        ),
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                        filled: false,
                        isDense: true,
                        contentPadding: const EdgeInsets.symmetric(
                          vertical: 12,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 36,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: [
                  for (final f in FiltroImportancia.values) ...[
                    _FichaFiltro(
                      texto: f == FiltroImportancia.mes && !mesAtual
                          ? 'Mês selecionado'
                          : f.rotulo,
                      selecionada: f == _filtro,
                      onTap: () => _mudarFiltro(f),
                    ),
                    const SizedBox(width: 8),
                  ],
                ],
              ),
            ),
            if (_filtro == FiltroImportancia.mes) ...[
              const SizedBox(height: 10),
              Row(
                children: [
                  IconButton(
                    tooltip: 'Mês anterior',
                    onPressed: () => _mudarMes(-1),
                    icon: const Icon(Icons.chevron_left, color: Cores.texto),
                  ),
                  Expanded(
                    child: Text(
                      Fmt.mesAno(_ano, _mes),
                      textAlign: TextAlign.center,
                      style: Txt.corpoNegrito.copyWith(fontSize: 16),
                    ),
                  ),
                  IconButton(
                    tooltip: 'Próximo mês',
                    onPressed: () => _mudarMes(1),
                    icon: const Icon(Icons.chevron_right, color: Cores.texto),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 14),
            if (_carregando)
              const EstadoCarregando(altura: 200)
            else if (_erro)
              EstadoErro(
                mensagem: 'Não foi possível carregar suas importâncias. Tente novamente',
                onTentar: _carregar,
              )
            else if (itens != null && itens.isEmpty)
              Cartao(
                child:
                    (_termo.trim().isEmpty &&
                        _filtro == FiltroImportancia.todos)
                    ? EstadoVazio(
                        mensagem:
                            'Você ainda não cadastrou nenhuma importância',
                        acao: 'Nova importância',
                        onAcao: () => abrirFormImportancia(context),
                        icone: Icons.event_outlined,
                      )
                    : const EstadoVazio(
                        mensagem: 'Nenhuma importância encontrada para os filtros selecionados',
                        icone: Icons.search_off,
                      ),
              )
            else if (itens != null)
              ..._grupos(itens, hoje),
          ],
        ),
      ),
    );
  }

  List<Widget> _grupos(List<Importancia> itens, DateTime hoje) {
    final atrasadas = itens
        .where((i) => !i.concluida && i.data.isBefore(hoje))
        .toList();
    final doDia = itens
        .where((i) => !i.concluida && Fmt.mesmoDia(i.data, hoje))
        .toList();
    final proximas = itens
        .where((i) => !i.concluida && i.data.isAfter(hoje))
        .toList();
    final concluidas = itens.where((i) => i.concluida).toList();

    final w = <Widget>[];
    void grupo(
      String titulo,
      Color cor,
      List<Importancia> l, {
      String? sufixo,
    }) {
      if (l.isEmpty) return;
      w.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(titulo, style: Txt.secao.copyWith(color: cor, fontSize: 19)),
              const Spacer(),
              Text(
                sufixo ?? Fmt.pluralImportancias(l.length),
                style: Txt.rotulo.copyWith(fontSize: 13),
              ),
            ],
          ),
        ),
      );
      w.add(_CartaoLista(itens: l, hoje: hoje, destaqueId: _destaqueId));
      w.add(const SizedBox(height: 20));
    }

    grupo('Atrasadas', Cores.perigo, atrasadas);
    grupo('Hoje', Cores.texto, doDia);

    if (proximas.isNotEmpty) {
      // Próximas, subdivididas por mês.
      final porMes = <String, List<Importancia>>{};
      for (final i in proximas) {
        porMes.putIfAbsent('${i.data.year}-${i.data.month}', () => []).add(i);
      }
      var primeiro = true;
      for (final l in porMes.values) {
        final rotulo =
            '${Fmt.mesAnoData(l.first.data)} · ${Fmt.pluralImportancias(l.length)}';
        if (primeiro) {
          w.add(
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('Próximas', style: Txt.secao.copyWith(fontSize: 19)),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      rotulo,
                      textAlign: TextAlign.right,
                      style: Txt.rotulo.copyWith(fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          );
          primeiro = false;
        } else {
          w.add(
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Align(
                alignment: Alignment.centerRight,
                child: Text(rotulo, style: Txt.rotulo.copyWith(fontSize: 13)),
              ),
            ),
          );
        }
        w.add(_CartaoLista(itens: l, hoje: hoje, destaqueId: _destaqueId));
        w.add(const SizedBox(height: 16));
      }
      w.add(const SizedBox(height: 4));
    }

    grupo('Concluídas', Cores.texto, concluidas);
    return w;
  }
}

class _FichaFiltro extends StatelessWidget {
  const _FichaFiltro({
    required this.texto,
    required this.selecionada,
    required this.onTap,
  });
  final String texto;
  final bool selecionada;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selecionada,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: selecionada ? Cores.selecionado : Cores.cartao,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: selecionada ? Cores.primaria : Colors.transparent,
            ),
          ),
          child: Text(
            texto,
            style: Txt.corpoNegrito.copyWith(
              fontSize: 13.5,
              color: selecionada ? Cores.primaria : Cores.textoSuave,
            ),
          ),
        ),
      ),
    );
  }
}

class _CartaoLista extends StatelessWidget {
  const _CartaoLista({
    required this.itens,
    required this.hoje,
    this.destaqueId,
  });
  final List<Importancia> itens;
  final DateTime hoje;
  final String? destaqueId;

  @override
  Widget build(BuildContext context) {
    return Cartao(
      raio: 22,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
      child: Column(
        children: [
          for (var i = 0; i < itens.length; i++) ...[
            if (i > 0) const Divider(height: 1, color: Cores.borda),
            _ItemImportancia(
              imp: itens[i],
              hoje: hoje,
              destaque: itens[i].id == destaqueId,
            ),
          ],
        ],
      ),
    );
  }
}

class _ItemImportancia extends StatelessWidget {
  const _ItemImportancia({
    required this.imp,
    required this.hoje,
    this.destaque = false,
  });
  final Importancia imp;
  final DateTime hoje;
  final bool destaque;

  @override
  Widget build(BuildContext context) {
    final prazo = PrazoImportancia.de(imp, hoje);
    final partes = <String>[
      if (imp.descricao.isNotEmpty) imp.descricao,
      imp.categoria,
      Fmt.data(imp.data) +
          (imp.horario != null ? ' · ${Fmt.hora(imp.horario!)}' : ''),
      imp.concluida ? 'Concluída' : 'Pendente',
    ];
    final valor = imp.paga
        ? null
        : (imp.temDespesa ? Fmt.moeda(imp.valorPrevisto) : null);
    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      decoration: BoxDecoration(
        color: destaque
            ? Cores.selecionado.withValues(alpha: 0.6)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => abrirDetalheImportancia(context, imp.id),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 2),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              IconeQuadrado(
                imp.concluida
                    ? Icons.check
                    : (prazo != null && prazo.cor == Cores.perigo
                          ? Icons.credit_card_outlined
                          : (Fmt.mesmoDia(imp.data, hoje)
                                ? Icons.calendar_today_outlined
                                : Categorias.icone(imp.categoria))),
                cor: imp.concluida
                    ? Cores.sucesso
                    : (prazo != null && prazo.cor == Cores.perigo
                          ? Cores.perigo
                          : (Fmt.mesmoDia(imp.data, hoje)
                                ? Cores.alerta
                                : Cores.primaria)),
                tamanho: 38,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      imp.nome,
                      style: Txt.corpoNegrito.copyWith(
                        fontSize: 16.5,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text.rich(
                      TextSpan(
                        style: Txt.pequeno.copyWith(
                          fontSize: 12.5,
                          height: 1.35,
                        ),
                        children: [
                          TextSpan(
                            text:
                                '${partes.take(partes.length - 1).join(' · ')} · ',
                          ),
                          TextSpan(
                            text: partes.last,
                            style: TextStyle(
                              color: imp.concluida
                                  ? Cores.sucesso
                                  : Cores.textoSuave,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (imp.periodicidade != Periodicidade.nenhuma)
                      Padding(
                        padding: const EdgeInsets.only(top: 2),
                        child: Text(
                          imp.periodicidade.textoRepete,
                          style: Txt.pequeno.copyWith(
                            color: Cores.primaria,
                            fontSize: 12.5,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  if (imp.paga)
                    Text(
                      Fmt.moeda(imp.valorPago ?? imp.valorPrevisto),
                      style: Txt.corpoNegrito.copyWith(fontSize: 15.5),
                    )
                  else if (valor != null)
                    Text(
                      valor,
                      style: Txt.corpoNegrito.copyWith(fontSize: 15.5),
                    )
                  else
                    Text(
                      'Sem despesa',
                      style: Txt.pequeno.copyWith(fontSize: 13),
                    ),
                  const SizedBox(height: 3),
                  if (imp.paga)
                    const TextoSituacao('Pago', Cores.sucesso, tamanho: 12.5)
                  else if (prazo != null)
                    TextoSituacao(prazo.texto, prazo.cor, tamanho: 12.5),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
