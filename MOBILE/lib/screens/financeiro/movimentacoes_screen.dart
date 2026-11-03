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

/// Consulta completa de movimentações do mês (9.1.6).
class MovimentacoesScreen extends StatefulWidget {
  const MovimentacoesScreen({
    super.key,
    required this.ano,
    required this.mes,
    this.tipo,
    this.categoria,
  });
  final int ano;
  final int mes;
  final TipoMov? tipo;
  final String? categoria;

  @override
  State<MovimentacoesScreen> createState() => _MovimentacoesScreenState();
}

class _MovimentacoesScreenState extends State<MovimentacoesScreen> {
  static const _pagina = 10;
  late TipoMov? _tipo = widget.tipo;
  late String? _categoria = widget.categoria;
  String _termo = '';
  final _busca = TextEditingController();
  Timer? _debounce;

  List<Movimentacao> _itens = [];
  int _total = 0;
  bool _carregando = true;
  bool _carregandoMais = false;
  bool _erro = false;
  int _geracao = 0;
  AppScope? _escopo;
  bool _iniciado = false;

  FiltroMov get _filtro => FiltroMov(
    ano: widget.ano,
    mes: widget.mes,
    busca: _termo,
    tipo: _tipo,
    categoria: _categoria,
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final e = AppScope.of(context);
    if (_escopo != e) {
      _escopo?.dados.removeListener(_aoMudar);
      _escopo = e;
      e.dados.addListener(_aoMudar);
    }
    if (!_iniciado) {
      _iniciado = true;
      _carregar();
    }
  }

  @override
  void dispose() {
    _escopo?.dados.removeListener(_aoMudar);
    _debounce?.cancel();
    _busca.dispose();
    super.dispose();
  }

  void _aoMudar() => _carregar(preservar: true);

  Future<void> _carregar({bool preservar = false}) async {
    final e = _escopo;
    if (e == null || !mounted) return;
    final g = ++_geracao;
    final qtd = preservar ? _itens.length : 0;
    setState(() {
      _carregando = !preservar || _itens.isEmpty;
      _erro = false;
    });
    try {
      final c = await e.repositorio.consultarMovimentacoes(
        _filtro,
        limite: qtd > _pagina ? qtd : _pagina,
      );
      if (!mounted || g != _geracao) return;
      setState(() {
        _itens = c.itens;
        _total = c.total;
        _carregando = false;
      });
    } catch (_) {
      if (!mounted || g != _geracao) return;
      setState(() {
        _erro = true;
        _carregando = false;
      });
    }
  }

  Future<void> _carregarMais() async {
    final e = _escopo;
    if (e == null || _carregandoMais) return;
    setState(() => _carregandoMais = true);
    try {
      final c = await e.repositorio.consultarMovimentacoes(
        _filtro,
        deslocamento: _itens.length,
        limite: _pagina,
      );
      if (!mounted) return;
      final ids = _itens.map((m) => m.id).toSet();
      setState(() {
        _itens = [..._itens, ...c.itens.where((m) => !ids.contains(m.id))];
        _total = c.total;
      });
    } catch (_) {
      if (mounted) {
        mostrarMensagem(
          context,
          'Não foi possível carregar mais lançamentos',
          erro: true,
        );
      }
    } finally {
      if (mounted) setState(() => _carregandoMais = false);
    }
  }

  void _limpar() {
    _busca.clear();
    setState(() {
      _termo = '';
      _tipo = null;
      _categoria = null;
    });
    _carregar();
  }

  void _escolherTipo(TipoMov? t) {
    setState(() {
      _tipo = t;
      // Limpa filtros incompatíveis: categoria de despesa x tipo receita.
      if (t == TipoMov.receita &&
          _categoria != null &&
          !Categorias.receitas.contains(_categoria)) {
        _categoria = null;
      }
      if (t == TipoMov.despesa &&
          _categoria != null &&
          !Categorias.despesas.contains(_categoria)) {
        _categoria = null;
      }
    });
    _carregar();
  }

  Future<void> _escolherCategoria() async {
    final lista = switch (_tipo) {
      TipoMov.receita => Categorias.receitas,
      TipoMov.despesa => Categorias.despesas,
      null => {...Categorias.despesas, ...Categorias.receitas}.toList()..sort(),
    };
    final r = await escolherOpcao<String>(
      context,
      titulo: 'Categoria',
      opcoes: ['Todas', ...lista],
      rotuloDe: (c) => c,
      atual: _categoria ?? 'Todas',
    );
    if (r == null) return;
    setState(() => _categoria = r == 'Todas' ? null : r);
    _carregar();
  }

  Future<void> _excluir(Movimentacao m) async {
    final ok = await confirmarExclusaoMovimentacao(context, m);
    if (!ok || !mounted) return;
    final e = _escopo!;
    try {
      await e.repositorio.excluirMovimentacao(m.id);
      e.dados.mudou();
      if (mounted) {
        mostrarMensagem(
          context,
          m.receita ? 'Receita excluída' : 'Despesa excluída',
        );
      }
    } on ErroApp catch (er) {
      if (mounted) mostrarMensagem(context, er.mensagem, erro: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final filtrado = _filtro.filtrado;
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
              child: Row(
                children: [
                  const BotaoVoltar(),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Movimentações', style: Txt.tituloForm),
                        Text(
                          Fmt.mesAno(widget.ano, widget.mes),
                          style: Txt.rotulo,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: RefreshIndicator(
                color: Cores.primaria,
                backgroundColor: Cores.cartao,
                onRefresh: _carregar,
                child: ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
                  children: [
                    CaixaCampo(
                      altura: 44,
                      child: Row(
                        children: [
                          const Icon(
                            Icons.search,
                            size: 19,
                            color: Cores.textoSuave,
                          ),
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
                                hintText: 'Buscar movimentação',
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
                    Row(
                      children: [
                        for (final (t, nome) in [
                          (null, 'Todas'),
                          (TipoMov.receita, 'Receitas'),
                          (TipoMov.despesa, 'Despesas'),
                        ]) ...[
                          GestureDetector(
                            onTap: () => _escolherTipo(t),
                            child: Container(
                              height: 36,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: _tipo == t
                                    ? Cores.selecionado
                                    : Cores.cartao,
                                borderRadius: BorderRadius.circular(18),
                                border: Border.all(
                                  color: _tipo == t
                                      ? Cores.primaria
                                      : Colors.transparent,
                                ),
                              ),
                              child: Text(
                                nome,
                                style: Txt.corpoNegrito.copyWith(
                                  fontSize: 13.5,
                                  color: _tipo == t
                                      ? Cores.primaria
                                      : Cores.textoSuave,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                        ],
                        const Spacer(),
                        GestureDetector(
                          onTap: _escolherCategoria,
                          child: Container(
                            height: 36,
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            decoration: BoxDecoration(
                              color: _categoria != null
                                  ? Cores.selecionado
                                  : Cores.cartao,
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(
                                color: _categoria != null
                                    ? Cores.primaria
                                    : Colors.transparent,
                              ),
                            ),
                            child: Row(
                              children: [
                                const Icon(
                                  Icons.tune,
                                  size: 16,
                                  color: Cores.textoSuave,
                                ),
                                const SizedBox(width: 5),
                                ConstrainedBox(
                                  constraints: const BoxConstraints(
                                    maxWidth: 84,
                                  ),
                                  child: Text(
                                    _categoria ?? 'Categoria',
                                    overflow: TextOverflow.ellipsis,
                                    style: Txt.corpoNegrito.copyWith(
                                      fontSize: 13,
                                      color: _categoria != null
                                          ? Cores.primaria
                                          : Cores.textoSuave,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            filtrado
                                ? '$_total encontrada(s) · com filtros'
                                : '$_total no mês · sem filtros',
                            style: Txt.rotulo.copyWith(fontSize: 13),
                          ),
                        ),
                        if (filtrado)
                          GestureDetector(
                            onTap: _limpar,
                            child: Text(
                              'Limpar filtros',
                              style: Txt.link.copyWith(fontSize: 13),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    if (_carregando)
                      const EstadoCarregando(altura: 200)
                    else if (_erro)
                      EstadoErro(
                        mensagem: 'Não foi possível carregar seus dados financeiros. Tente novamente',
                        onTentar: _carregar,
                      )
                    else if (_itens.isEmpty)
                      Cartao(
                        child: EstadoVazio(
                          mensagem: filtrado
                              ? 'Nenhuma movimentação encontrada para os filtros selecionados'
                              : 'Nenhuma movimentação cadastrada neste mês',
                          acao: filtrado
                              ? 'Limpar filtros'
                              : 'Cadastrar receita',
                          onAcao: filtrado
                              ? _limpar
                              : () => abrirFormReceita(context),
                          icone: Icons.receipt_long_outlined,
                        ),
                      )
                    else
                      Cartao(
                        raio: 22,
                        padding: const EdgeInsets.fromLTRB(16, 4, 4, 4),
                        child: Column(
                          children: [
                            for (var i = 0; i < _itens.length; i++) ...[
                              if (i > 0) const DivisorFino(),
                              LinhaMovimentacao(
                                mov: _itens[i],
                                detalhada: true,
                                onTap: () => abrirDetalheMovimentacao(
                                  context,
                                  _itens[i].id,
                                ),
                                onMenu: (v) => v == 'editar'
                                    ? abrirFormMovimentacao(context, _itens[i])
                                    : _excluir(_itens[i]),
                              ),
                            ],
                            if (_itens.length < _total)
                              Padding(
                                padding: const EdgeInsets.symmetric(
                                  vertical: 8,
                                ),
                                child: _carregandoMais
                                    ? const EstadoCarregando(altura: 40)
                                    : TextButton(
                                        onPressed: _carregarMais,
                                        child: Text(
                                          'Carregar mais (${_total - _itens.length})',
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
            ),
          ],
        ),
      ),
    );
  }
}
