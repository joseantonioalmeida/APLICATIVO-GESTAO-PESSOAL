import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/categorias.dart';
import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../models/modelos.dart';
import '../../shell/rotas.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import '../home/home_screen.dart' show ControleConclusao;

/// Tela 5 - Atividades (lista de tarefas).
class AtividadesScreen extends StatefulWidget {
  const AtividadesScreen({super.key});

  @override
  State<AtividadesScreen> createState() => _AtividadesScreenState();
}

class _AtividadesScreenState extends State<AtividadesScreen> {
  static const _tamanhoPagina = 10;

  late FiltroAtividades _filtro;
  bool _iniciado = false;
  bool _seguindoHoje = true;

  final _busca = TextEditingController();
  Timer? _debounce;
  Timer? _relogio;

  List<Atividade> _itens = [];
  ConsultaAtividades? _consulta;
  PendenciasAnteriores _pendencias = const PendenciasAnteriores(quantidade: 0);
  bool _carregando = true;
  bool _carregandoMais = false;
  bool _erro = false;
  int _geracao = 0;
  final _processando = <String>{};

  AppScope? _escopo;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final e = AppScope.of(context);
    if (_escopo != e) {
      _escopo?.navegacao.removeListener(_aoNavegar);
      _escopo?.dados.removeListener(_aoMudarDados);
      _escopo = e;
      e.navegacao.addListener(_aoNavegar);
      e.dados.addListener(_aoMudarDados);
    }
    if (!_iniciado) {
      _iniciado = true;
      _filtro = FiltroAtividades(data: e.hoje);
      _relogio = Timer.periodic(
        const Duration(seconds: 20),
        (_) => _verificarDia(),
      );
      _aoNavegar();
      _carregar();
    }
  }

  @override
  void dispose() {
    _escopo?.navegacao.removeListener(_aoNavegar);
    _escopo?.dados.removeListener(_aoMudarDados);
    _debounce?.cancel();
    _relogio?.cancel();
    _busca.dispose();
    super.dispose();
  }

  void _aoMudarDados() => _carregar(preservar: true);

  void _aoNavegar() {
    final e = _escopo;
    if (e == null) return;
    final it = e.navegacao.consumir(Aba.atividades);
    if (it == null) return;
    setState(() {
      var f = _filtro;
      if (it.limparFiltros) {
        f = f.limpo();
        _busca.clear();
      }
      if (it.situacao != null) f = f.copiar(situacao: it.situacao);
      if (it.data != null) {
        f = f.copiar(data: Fmt.somenteData(it.data!));
        _seguindoHoje = Fmt.mesmoDia(it.data!, e.hoje);
      }
      _filtro = f;
    });
    _carregar();
  }

  void _verificarDia() {
    final e = _escopo;
    if (e == null || !mounted) return;
    if (_seguindoHoje && !Fmt.mesmoDia(_filtro.data, e.hoje)) {
      setState(() => _filtro = _filtro.copiar(data: e.hoje));
      _carregar();
    }
  }

  Future<void> _carregar({bool preservar = false}) async {
    final e = _escopo;
    if (e == null) return;
    final g = ++_geracao;
    final quantidade = preservar ? _itens.length : 0;
    setState(() {
      _carregando = !preservar || _consulta == null;
      _erro = false;
    });
    try {
      final c = await e.repositorio.consultarAtividades(
        _filtro,
        limite: quantidade > _tamanhoPagina ? quantidade : _tamanhoPagina,
      );
      final p = await e.repositorio.pendenciasAnteriores();
      if (!mounted || g != _geracao) return;
      setState(() {
        _consulta = c;
        _itens = c.itens;
        _pendencias = p;
        _carregando = false;
      });
    } catch (_) {
      if (!mounted || g != _geracao) return;
      setState(() {
        _erro = true;
        _carregando = false;
        _consulta = null;
        _itens = [];
      });
    }
  }

  Future<void> _carregarMais() async {
    final e = _escopo;
    if (e == null || _carregandoMais || _consulta == null) return;
    setState(() => _carregandoMais = true);
    try {
      final c = await e.repositorio.consultarAtividades(
        _filtro,
        deslocamento: _itens.length,
        limite: _tamanhoPagina,
      );
      if (!mounted) return;
      final ids = _itens.map((a) => a.id).toSet();
      setState(() {
        _itens = [..._itens, ...c.itens.where((a) => !ids.contains(a.id))];
        _consulta = ConsultaAtividades(
          itens: _itens,
          total: c.total,
          concluidas: c.concluidas,
          pendentes: c.pendentes,
          minutos: c.minutos,
        );
      });
    } catch (_) {
      if (mounted) {
        mostrarMensagem(
          context,
          'Não foi possível carregar mais atividades',
          erro: true,
        );
      }
    } finally {
      if (mounted) setState(() => _carregandoMais = false);
    }
  }

  void _mudar(FiltroAtividades f, {bool? seguirHoje}) {
    setState(() {
      _filtro = f;
      if (seguirHoje != null) _seguindoHoje = seguirHoje;
    });
    _carregar();
  }

  void _irParaData(DateTime d) {
    final dia = Fmt.somenteData(d);
    _mudar(_filtro.copiar(data: dia), seguirHoje: false);
  }

  Future<void> _escolherData() async {
    final r = await showDatePicker(
      context: context,
      initialDate: _filtro.data,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
      locale: const Locale('pt', 'BR'),
    );
    if (r != null) _irParaData(r);
  }

  Future<void> _alternar(Atividade a) async {
    if (_processando.contains(a.id)) return;
    final e = _escopo!;
    setState(() => _processando.add(a.id));
    try {
      await e.repositorio.alterarConclusaoAtividade(a.id, !a.concluida);
      e.dados.mudou();
      if (mounted) {
        mostrarMensagem(
          context,
          a.concluida ? 'Atividade reaberta' : 'Atividade concluída',
        );
      }
    } on ErroApp catch (er) {
      if (mounted) mostrarMensagem(context, er.mensagem, erro: true);
    } catch (_) {
      if (mounted) {
        mostrarMensagem(
          context,
          'Não foi possível confirmar a alteração. Verifique e tente novamente',
          erro: true,
        );
      }
    } finally {
      if (mounted) setState(() => _processando.remove(a.id));
    }
  }

  Future<void> _excluir(Atividade a) async {
    final escopo = await confirmarExclusaoAtividade(context, a);
    if (escopo == null || !mounted) return;
    final e = _escopo!;
    try {
      await e.repositorio.excluirAtividade(a.id, escopo);
      e.dados.mudou();
      if (mounted) mostrarMensagem(context, 'Atividade excluída');
    } on ErroApp catch (er) {
      if (mounted) mostrarMensagem(context, er.mensagem, erro: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final f = _filtro;
    final c = _consulta;
    final ehHoje = Fmt.mesmoDia(f.data, escopo.hoje);

    return SafeArea(
      bottom: false,
      child: RefreshIndicator(
        color: Cores.primaria,
        backgroundColor: Cores.cartao,
        onRefresh: () => _carregar(preservar: true),
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text('Atividades', style: Txt.tituloTela),
                ),
                _BotaoNovo(
                  texto: 'Nova atividade',
                  onTap: () => abrirFormAtividade(context, data: f.data),
                ),
              ],
            ),
            const SizedBox(height: 14),
            _SeletorData(
              data: f.data,
              ehHoje: ehHoje,
              onAnterior: () => _irParaData(
                DateTime(f.data.year, f.data.month, f.data.day - 1),
              ),
              onProxima: () => _irParaData(
                DateTime(f.data.year, f.data.month, f.data.day + 1),
              ),
              onHoje: () =>
                  _mudar(_filtro.copiar(data: escopo.hoje), seguirHoje: true),
              onEscolher: _escolherData,
            ),
            const SizedBox(height: 12),
            _CampoBusca(
              controller: _busca,
              dica: 'Buscar atividade',
              categoriaAtiva: f.categoria != null,
              onChanged: (t) {
                _debounce?.cancel();
                _debounce = Timer(const Duration(milliseconds: 300), () {
                  if (mounted) _mudar(_filtro.copiar(busca: t));
                });
              },
              onFiltroCategoria: () async {
                final r = await escolherOpcao<_Opc<String?>>(
                  context,
                  titulo: 'Categoria',
                  opcoes: [
                    const _Opc<String?>(null),
                    for (final c in Categorias.atividades) _Opc<String?>(c),
                  ],
                  rotuloDe: (v) => v.valor ?? 'Todas',
                  atual: _Opc<String?>(f.categoria),
                );
                if (r != null && mounted) {
                  _mudar(_filtro.copiar(categoria: r.valor));
                }
              },
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: _CaixaFiltro<SituacaoFiltro>(
                    rotulo: 'Situação',
                    valor: f.situacao,
                    opcoes: SituacaoFiltro.values,
                    rotuloDe: (v) => v.rotulo,
                    aoEscolher: (v) => _mudar(_filtro.copiar(situacao: v)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _CaixaFiltro<Prioridade?>(
                    rotulo: 'Prioridade',
                    valor: f.prioridade,
                    opcoes: [null, ...Prioridade.values],
                    rotuloDe: (v) => v?.rotulo ?? 'Todas',
                    aoEscolher: (v) => _mudar(_filtro.copiar(prioridade: v)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _CaixaFiltro<OrdemAtividade>(
                    rotulo: 'Ordenar por',
                    valor: f.ordem,
                    opcoes: OrdemAtividade.values,
                    rotuloDe: (v) => v.rotulo,
                    aoEscolher: (v) => _mudar(_filtro.copiar(ordem: v)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _Indicadores(consulta: c),
            if (_pendencias.quantidade > 0) ...[
              const SizedBox(height: 12),
              _AvisoPendencias(
                quantidade: _pendencias.quantidade,
                onVer: () {
                  _busca.clear();
                  _mudar(
                    FiltroAtividades(
                      data: _pendencias.maisAntiga!,
                      situacao: SituacaoFiltro.pendentes,
                      ordem: f.ordem,
                    ),
                    seguirHoje: false,
                  );
                },
              ),
            ],
            const SizedBox(height: 18),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(ehHoje ? 'Hoje' : Fmt.diaSemana(f.data), style: Txt.secao),
                const SizedBox(width: 8),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 1),
                    child: Text(
                      '${Fmt.dataCurta(f.data)}/${f.data.year} · ${f.filtrado ? 'com filtros' : 'sem filtros'}',
                      style: Txt.rotulo.copyWith(fontSize: 13),
                    ),
                  ),
                ),
                if (f.filtrado)
                  GestureDetector(
                    onTap: () {
                      _busca.clear();
                      _mudar(_filtro.limpo());
                    },
                    child: Text(
                      'Limpar filtros',
                      style: Txt.link.copyWith(fontSize: 13),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            if (_carregando)
              const EstadoCarregando(altura: 160)
            else if (_erro)
              EstadoErro(
                mensagem: 'Não foi possível carregar suas atividades. Tente novamente',
                onTentar: _carregar,
              )
            else if (c != null && c.total == 0)
              Cartao(
                child: f.filtrado
                    ? EstadoVazio(
                        mensagem: 'Nenhuma atividade encontrada para os filtros selecionados',
                        acao: 'Limpar filtros',
                        onAcao: () {
                          _busca.clear();
                          _mudar(_filtro.limpo());
                        },
                      )
                    : EstadoVazio(
                        mensagem: 'Nenhuma atividade cadastrada para esta data',
                        acao: 'Nova atividade',
                        onAcao: () => abrirFormAtividade(context, data: f.data),
                        icone: Icons.event_available_outlined,
                      ),
              )
            else
              Cartao(
                raio: 22,
                padding: const EdgeInsets.fromLTRB(14, 4, 6, 4),
                child: Column(
                  children: [
                    for (var i = 0; i < _itens.length; i++) ...[
                      if (i > 0) const Divider(height: 1, color: Cores.borda),
                      _ItemAtividade(
                        atividade: _itens[i],
                        ocupado: _processando.contains(_itens[i].id),
                        aoAlternar: () => _alternar(_itens[i]),
                        aoAbrir: () =>
                            abrirDetalheAtividade(context, _itens[i].id),
                        aoEditar: () =>
                            abrirFormAtividade(context, editar: _itens[i]),
                        aoExcluir: () => _excluir(_itens[i]),
                      ),
                    ],
                    if (c != null && c.temMais)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: _carregandoMais
                            ? const EstadoCarregando(altura: 40)
                            : TextButton(
                                onPressed: _carregarMais,
                                child: Text(
                                  'Carregar mais atividades (${c.total - _itens.length})',
                                  style: Txt.link,
                                ),
                              ),
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _BotaoNovo extends StatelessWidget {
  const _BotaoNovo({required this.texto, required this.onTap});
  final String texto;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Cores.primaria,
      borderRadius: BorderRadius.circular(22),
      child: InkWell(
        borderRadius: BorderRadius.circular(22),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.add, size: 18, color: Cores.sobrePrimaria),
              const SizedBox(width: 6),
              Text(
                texto,
                style: Txt.corpoNegrito.copyWith(
                  color: Cores.sobrePrimaria,
                  fontSize: 14.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SeletorData extends StatelessWidget {
  const _SeletorData({
    required this.data,
    required this.ehHoje,
    required this.onAnterior,
    required this.onProxima,
    required this.onHoje,
    required this.onEscolher,
  });
  final DateTime data;
  final bool ehHoje;
  final VoidCallback onAnterior;
  final VoidCallback onProxima;
  final VoidCallback onHoje;
  final VoidCallback onEscolher;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        IconButton(
          tooltip: 'Dia anterior',
          onPressed: onAnterior,
          icon: const Icon(Icons.chevron_left, color: Cores.texto),
          visualDensity: VisualDensity.compact,
        ),
        Expanded(
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onEscolher,
            child: Column(
              children: [
                Text(
                  Fmt.diaSemana(data),
                  style: Txt.rotulo.copyWith(fontSize: 13),
                ),
                Text(
                  Fmt.dataExtensa(data),
                  textAlign: TextAlign.center,
                  style: Txt.corpoNegrito.copyWith(fontSize: 16.5, height: 1.2),
                ),
              ],
            ),
          ),
        ),
        IconButton(
          tooltip: 'Próximo dia',
          onPressed: onProxima,
          icon: const Icon(Icons.chevron_right, color: Cores.texto),
          visualDensity: VisualDensity.compact,
        ),
        GestureDetector(
          onTap: onHoje,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: Cores.selecionado,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Text(
              'Hoje',
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

class _CampoBusca extends StatelessWidget {
  const _CampoBusca({
    required this.controller,
    required this.dica,
    required this.onChanged,
    this.onFiltroCategoria,
    this.categoriaAtiva = false,
  });
  final TextEditingController controller;
  final String dica;
  final ValueChanged<String> onChanged;
  final VoidCallback? onFiltroCategoria;
  final bool categoriaAtiva;

  @override
  Widget build(BuildContext context) {
    return CaixaCampo(
      altura: 44,
      child: Row(
        children: [
          const Icon(Icons.search, size: 19, color: Cores.textoSuave),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              controller: controller,
              onChanged: onChanged,
              style: Txt.corpo.copyWith(fontSize: 15),
              cursorColor: Cores.primaria,
              decoration: InputDecoration(
                hintText: dica,
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
                contentPadding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
          if (onFiltroCategoria != null)
            GestureDetector(
              onTap: onFiltroCategoria,
              child: Semantics(
                label: 'Filtrar por categoria',
                child: Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Icon(
                    Icons.tune,
                    size: 19,
                    color: categoriaAtiva ? Cores.primaria : Cores.textoSuave,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _CaixaFiltro<T> extends StatelessWidget {
  const _CaixaFiltro({
    required this.rotulo,
    required this.valor,
    required this.opcoes,
    required this.rotuloDe,
    required this.aoEscolher,
  });
  final String rotulo;
  final T valor;
  final List<T> opcoes;
  final String Function(T) rotuloDe;
  final ValueChanged<T> aoEscolher;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Cores.cartao,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () async {
          // Opções nulas ("Todas") não podem ser distinguidas de "fechou";
          // por isso usamos um invólucro.
          final r = await escolherOpcao<_Opc<T>>(
            context,
            titulo: rotulo,
            opcoes: [for (final o in opcoes) _Opc(o)],
            rotuloDe: (o) => rotuloDe(o.valor),
            atual: _Opc(valor),
          );
          if (r != null) aoEscolher(r.valor);
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(rotulo, style: Txt.pequeno.copyWith(fontSize: 11.5)),
              const SizedBox(height: 2),
              Text(
                rotuloDe(valor),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Txt.corpoNegrito.copyWith(fontSize: 14, height: 1.15),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Opc<T> {
  const _Opc(this.valor);
  final T valor;
  @override
  bool operator ==(Object other) => other is _Opc<T> && other.valor == valor;
  @override
  int get hashCode => valor.hashCode;
}

class _Indicadores extends StatelessWidget {
  const _Indicadores({required this.consulta});
  final ConsultaAtividades? consulta;

  @override
  Widget build(BuildContext context) {
    final c = consulta;
    Widget item(String valor, String rotulo, Color cor) => Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            valor,
            style: Txt.titulo.copyWith(
              fontSize: 22,
              color: cor,
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 2),
          Text(rotulo, style: Txt.pequeno.copyWith(fontSize: 12)),
        ],
      ),
    );
    return Cartao(
      raio: 18,
      padding: const EdgeInsets.fromLTRB(14, 14, 8, 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          item(c == null ? '–' : '${c.total}', 'Total', Cores.texto),
          item(
            c == null ? '–' : '${c.concluidas}',
            'Concluídas',
            Cores.sucesso,
          ),
          item(c == null ? '–' : '${c.pendentes}', 'Pendentes', Cores.alerta),
          Expanded(
            flex: 1,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  c == null ? '–' : Fmt.duracaoCompacta(c.minutos),
                  style: Txt.titulo.copyWith(fontSize: 22, letterSpacing: -0.3),
                ),
                const SizedBox(height: 2),
                Text(
                  'Tempo\nplanejado',
                  style: Txt.pequeno.copyWith(fontSize: 12, height: 1.15),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AvisoPendencias extends StatelessWidget {
  const _AvisoPendencias({required this.quantidade, required this.onVer});
  final int quantidade;
  final VoidCallback onVer;

  @override
  Widget build(BuildContext context) {
    return Cartao(
      raio: 18,
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      child: Row(
        children: [
          const Icon(Icons.schedule, color: Cores.alerta, size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              quantidade == 1
                  ? '1 pendência de dias anteriores'
                  : '$quantidade pendências de dias anteriores',
              style: Txt.corpo.copyWith(
                fontWeight: FontWeight.w600,
                fontSize: 14.5,
              ),
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: onVer,
            child: Text(
              'Ver pendências',
              style: Txt.link.copyWith(fontSize: 13.5),
            ),
          ),
        ],
      ),
    );
  }
}

class _ItemAtividade extends StatelessWidget {
  const _ItemAtividade({
    required this.atividade,
    required this.ocupado,
    required this.aoAlternar,
    required this.aoAbrir,
    required this.aoEditar,
    required this.aoExcluir,
  });
  final Atividade atividade;
  final bool ocupado;
  final VoidCallback aoAlternar;
  final VoidCallback aoAbrir;
  final VoidCallback aoEditar;
  final VoidCallback aoExcluir;

  @override
  Widget build(BuildContext context) {
    final a = atividade;
    final subtitulo = a.descricao.isEmpty
        ? a.categoria
        : '${a.categoria} · ${a.previa}';
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 1),
            child: ControleConclusao(
              concluida: a.concluida,
              ocupado: ocupado,
              onTap: aoAlternar,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: aoAbrir,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    a.nome,
                    style: Txt.corpoNegrito.copyWith(
                      fontSize: 16.5,
                      color: a.concluida ? Cores.textoSuave : Cores.texto,
                      decoration: a.concluida
                          ? TextDecoration.lineThrough
                          : null,
                      decorationColor: Cores.textoSuave,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(subtitulo, style: Txt.pequeno.copyWith(fontSize: 13)),
                  const SizedBox(height: 2),
                  Text.rich(
                    TextSpan(
                      style: Txt.pequeno.copyWith(fontSize: 13),
                      children: [
                        TextSpan(
                          text:
                              '${Fmt.hora(a.inicio)} – ${Fmt.hora(a.fim)} · Prioridade ${a.prioridade.rotulo.toLowerCase()} · ',
                        ),
                        TextSpan(
                          text: a.concluida ? 'Concluída' : 'Pendente',
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            color: a.concluida ? Cores.sucesso : Cores.alerta,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (a.periodicidade != Periodicidade.nenhuma)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        a.periodicidade.textoRepete,
                        style: Txt.pequeno.copyWith(
                          color: Cores.primaria,
                          fontSize: 12.5,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          PopupMenuButton<String>(
            padding: EdgeInsets.zero,
            tooltip: 'Mais opções',
            icon: const Icon(
              Icons.more_horiz,
              size: 20,
              color: Cores.textoSuave,
            ),
            onSelected: (v) => v == 'editar' ? aoEditar() : aoExcluir(),
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'editar', child: Text('Editar')),
              PopupMenuItem(value: 'excluir', child: Text('Excluir')),
            ],
          ),
        ],
      ),
    );
  }
}
