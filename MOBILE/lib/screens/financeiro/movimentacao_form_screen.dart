import 'package:flutter/material.dart';

import '../../core/categorias.dart';
import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../core/validadores.dart';
import '../../models/modelos.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import '../../widgets/formulario.dart';

/// Telas 10 (Cadastrar receita) e 11 (Cadastrar despesa), com edição.
class MovimentacaoFormScreen extends StatefulWidget {
  const MovimentacaoFormScreen({
    super.key,
    required this.tipo,
    this.editar,
    this.importancia,
  });
  final TipoMov tipo;
  final Movimentacao? editar;

  /// Importância de origem ("Registrar pagamento"), somente para despesas.
  final Importancia? importancia;

  @override
  State<MovimentacaoFormScreen> createState() => _MovimentacaoFormScreenState();
}

class _MovimentacaoFormScreenState extends State<MovimentacaoFormScreen> {
  final _nome = TextEditingController();
  final _valor = TextEditingController();
  final _data = TextEditingController();
  final _descricao = TextEditingController();
  final _contraparte = TextEditingController();

  String? _categoria;
  String? _forma;
  Importancia? _importancia;

  final _erros = <String, String?>{};
  String? _erroGeral;
  bool _salvando = false;
  bool _iniciado = false;
  late String _assinaturaInicial;

  bool get _receita => widget.tipo == TipoMov.receita;
  bool get _edicao => widget.editar != null;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_iniciado) return;
    _iniciado = true;
    final escopo = AppScope.of(context);
    final e = widget.editar;
    if (e != null) {
      _nome.text = e.nome;
      _valor.text = Fmt.valorSemSimbolo(e.valor);
      _categoria = e.categoria;
      _data.text = Fmt.data(e.data);
      _descricao.text = e.descricao;
      _contraparte.text = e.contraparte;
      _forma = e.forma;
      if (e.importanciaId != null) _carregarVinculada(e.importanciaId!);
    } else {
      _data.text = Fmt.data(escopo.hoje);
      final i = widget.importancia;
      if (i != null) _aplicarImportancia(i, inicial: true);
    }
    _assinaturaInicial = _assinatura();
  }

  Future<void> _carregarVinculada(String id) async {
    try {
      final i = await AppScope.of(context).repositorio.obterImportancia(id);
      if (mounted) setState(() => _importancia = i);
    } catch (_) {
      // Importância excluída: o vínculo já não está ativo.
    }
  }

  /// Preenche nome, valor previsto e categoria a partir da importância (11.5.1).
  void _aplicarImportancia(Importancia i, {bool inicial = false}) {
    _importancia = i;
    if (_nome.text.trim().isEmpty || inicial) _nome.text = i.nome;
    if (_valor.text.trim().isEmpty || inicial) {
      _valor.text = Fmt.valorSemSimbolo(i.valorPrevisto);
    }
    if (Categorias.despesas.contains(i.categoria) && _categoria == null) {
      _categoria = i.categoria;
    }
    if (_contraparte.text.trim().isEmpty && i.descricao.isNotEmpty) {
      _contraparte.text = i.descricao;
    }
  }

  @override
  void dispose() {
    for (final c in [_nome, _valor, _data, _descricao, _contraparte]) {
      c.dispose();
    }
    super.dispose();
  }

  String _assinatura() => [
    _nome.text,
    _valor.text,
    _categoria,
    _data.text,
    _descricao.text,
    _contraparte.text,
    _forma,
    _importancia?.id,
  ].join('|');

  bool get _alterado => _assinatura() != _assinaturaInicial;

  void _limpa(String campo) {
    if (_erros[campo] != null) setState(() => _erros[campo] = null);
  }

  MovimentacaoForm? _validar() {
    final hoje = AppScope.of(context).hoje;
    final erros = <String, String?>{};
    erros['nome'] = Valida.nome(
      _nome.text,
      _receita ? 'Informe o nome da receita' : 'Informe o nome da despesa',
    );
    final (centavos, erroValor) = Valida.valor(
      _valor.text,
      mensagemInvalido: _receita
          ? 'Informe um valor recebido maior que zero'
          : 'Informe um valor pago maior que zero',
    );
    erros['valor'] = erroValor;
    erros['categoria'] = _categoria == null ? 'Selecione uma categoria' : null;
    final data = Conv.data(_data.text);
    if (data == null) {
      erros['data'] = 'Informe uma data válida';
    } else if (data.isAfter(hoje)) {
      erros['data'] = _receita ? 'A data do recebimento não pode ser futura' : 'A data do pagamento não pode ser futura. Cadastre o compromisso em Importâncias';
    }
    setState(() {
      _erros
        ..clear()
        ..addAll(erros);
      _erroGeral = null;
    });
    if (erros.values.any((e) => e != null)) return null;
    return MovimentacaoForm(
      tipo: widget.tipo,
      nome: _nome.text.trim(),
      valor: centavos!,
      categoria: _categoria!,
      data: data!,
      descricao: _descricao.text.trim(),
      contraparte: _contraparte.text.trim(),
      forma: _forma,
      importanciaId: _edicao ? widget.editar!.importanciaId : _importancia?.id,
    );
  }

  Future<void> _salvar() async {
    if (_salvando) return;
    final form = _validar();
    if (form == null) return;
    final escopo = AppScope.of(context);
    final repo = escopo.repositorio;
    final e = widget.editar;
    final veioDeImportancia = widget.importancia != null;

    setState(() {
      _salvando = true;
      _erroGeral = null;
    });
    try {
      if (e == null) {
        await repo.criarMovimentacao(form);
      } else {
        await repo.editarMovimentacao(e.id, form);
      }
      if (!mounted) return;
      escopo.dados.mudou();
      ProtecaoSaida.de(context)?.liberar();
      final msg = e != null
          ? (_receita
                ? 'Receita atualizada com sucesso'
                : 'Despesa atualizada com sucesso')
          : (_receita
                ? 'Receita cadastrada com sucesso'
                : (veioDeImportancia
                      ? 'Pagamento registrado com sucesso'
                      : 'Despesa cadastrada com sucesso'));
      if (!veioDeImportancia) {
        escopo.navegacao.ir(
          IntencaoAba(
            Aba.financeiro,
            ano: form.data.year,
            mes: form.data.month,
          ),
        );
      }
      Navigator.of(context).pop(true);
      mostrarMensagem(context, msg);
    } on ErroApp catch (er) {
      if (mounted) {
        setState(() {
          if (er.campo != null) {
            _erros[er.campo!] = er.mensagem;
          } else {
            _erroGeral = er.mensagem;
          }
        });
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => _erroGeral = _receita
              ? 'Não foi possível confirmar o cadastro da receita. Tente novamente'
              : 'Não foi possível confirmar o cadastro da despesa. Tente novamente',
        );
      }
    } finally {
      if (mounted) setState(() => _salvando = false);
    }
  }

  Future<void> _escolherImportancia() async {
    final repo = AppScope.of(context).repositorio;
    final lista = (await repo.consultarImportancias(
      FiltroImportancia.todos,
      ano: DateTime.now().year,
      mes: DateTime.now().month,
    )).where((i) => !i.concluida && i.temDespesa && !i.paga).toList();
    if (!mounted) return;
    if (lista.isEmpty) {
      mostrarMensagem(
        context,
        'Nenhuma importância pendente com despesa para vincular',
        erro: true,
      );
      return;
    }
    final r = await escolherOpcao<Importancia>(
      context,
      titulo: 'Importância vinculada',
      opcoes: lista,
      rotuloDe: (i) =>
          '${i.nome} · vence ${Fmt.data(i.data)} · ${Fmt.moeda(i.valorPrevisto)}',
    );
    if (r != null) {
      setState(() => _aplicarImportancia(r));
    }
  }

  @override
  Widget build(BuildContext context) {
    final vinculada = _importancia != null;
    final cor = _receita ? Cores.sucesso : Cores.perigo;
    final titulo = _edicao
        ? (_receita ? 'Editar receita' : 'Editar despesa')
        : (_receita ? 'Cadastrar receita' : 'Cadastrar despesa');
    final textoSalvar = _edicao
        ? 'Salvar alterações'
        : (_receita
              ? 'Salvar receita'
              : (vinculada
                    ? 'Salvar despesa e registrar pagamento'
                    : 'Salvar despesa'));

    return ProtecaoSaida(
      alterado: () => _alterado,
      pergunta: _receita
          ? 'Deseja sair sem salvar a receita?'
          : 'Deseja sair sem salvar a despesa?',
      bloqueado: _salvando,
      child: FormularioScaffold(
        titulo: titulo,
        subtitulo: _receita
            ? 'Registre um valor que você já recebeu.'
            : 'Registre um pagamento que você já fez.',
        textoSalvar: textoSalvar,
        salvando: _salvando,
        onSalvar: _salvar,
        erroGeral: _erroGeral,
        cabecalho: _receita
            ? null
            : _CartaoImportancia(
                importancia: _importancia,
                editando: _edicao,
                aoTrocar: _escolherImportancia,
                aoRemover: () => setState(() => _importancia = null),
              ),
        children: [
          CampoTexto(
            rotulo: _receita ? 'Nome da receita' : 'Nome da despesa',
            obrigatorio: true,
            dica: _receita ? 'Ex.: Salário' : 'Ex.: Compra no mercado',
            controller: _nome,
            maxCaracteres: 100,
            capitalizacao: TextCapitalization.sentences,
            erro: _erros['nome'],
            onChanged: (_) {
              _limpa('nome');
              setState(() {});
            },
          ),
          const SizedBox(height: 14),
          CampoValor(
            rotulo: _receita ? 'Valor recebido' : 'Valor pago',
            obrigatorio: true,
            destaque: true,
            corValor: cor,
            controller: _valor,
            erro: _erros['valor'],
            onChanged: (_) {
              _limpa('valor');
              setState(() {});
            },
          ),
          if (!_receita && vinculada && _erros['valor'] == null)
            const TextoAjuda(
              'Confirme o valor realmente pago. Ele pode ser diferente do previsto.',
            ),
          const SizedBox(height: 14),
          CampoSelecao<String>(
            rotulo: 'Categoria',
            obrigatorio: true,
            dica: 'Selecione uma categoria',
            valor: _categoria,
            opcoes: _receita ? Categorias.receitas : Categorias.despesas,
            rotuloDe: (c) => c,
            erro: _erros['categoria'],
            aoEscolher: (c) => setState(() {
              _categoria = c;
              _erros['categoria'] = null;
            }),
          ),
          const SizedBox(height: 14),
          CampoData(
            rotulo: _receita ? 'Data do recebimento' : 'Data do pagamento',
            obrigatorio: true,
            controller: _data,
            erro: _erros['data'],
            ultima: AppScope.of(context).hoje,
            onChanged: (_) {
              _limpa('data');
              setState(() {});
            },
          ),
          if (_erros['data'] == null)
            TextoAjuda(
              _receita
                  ? 'Datas passadas são permitidas. Datas futuras, não.'
                  : 'Pode ser diferente do vencimento. Datas futuras, não.',
            ),
          const SizedBox(height: 18),
          Text(
            'Informações opcionais',
            style: Txt.corpoNegrito.copyWith(fontSize: 14),
          ),
          const SizedBox(height: 10),
          CampoTexto(
            rotulo: 'Descrição ou observação',
            dica: _receita
                ? 'Ex.: Pagamento referente ao serviço entregue em setembro'
                : 'Ex.: Pagamento com juros por atraso',
            controller: _descricao,
            linhas: 2,
            maxCaracteres: 200,
            contador: '${_descricao.text.length}/200',
            capitalizacao: TextCapitalization.sentences,
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 14),
          CampoTexto(
            rotulo: _receita
                ? 'Origem ou pagador'
                : 'Destinatário ou estabelecimento',
            dica: _receita
                ? 'Nome da empresa ou da pessoa'
                : 'Ex.: Mercado Central',
            controller: _contraparte,
            maxCaracteres: 100,
            capitalizacao: TextCapitalization.words,
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 14),
          CampoSelecao<String>(
            rotulo: _receita ? 'Forma de recebimento' : 'Forma de pagamento',
            dica: 'Selecione',
            valor: _forma,
            opcoes: _receita
                ? Categorias.formasRecebimento
                : Categorias.formasPagamento,
            rotuloDe: (c) => c,
            aoEscolher: (f) => setState(() => _forma = f),
          ),
        ],
      ),
    );
  }
}

/// Cartão "Importância vinculada" do cadastro de despesas.
class _CartaoImportancia extends StatelessWidget {
  const _CartaoImportancia({
    required this.importancia,
    required this.editando,
    required this.aoTrocar,
    required this.aoRemover,
  });
  final Importancia? importancia;
  final bool editando;
  final VoidCallback aoTrocar;
  final VoidCallback aoRemover;

  @override
  Widget build(BuildContext context) {
    final i = importancia;
    if (i == null) {
      if (editando) return const SizedBox.shrink();
      return Cartao(
        raio: 16,
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
        onTap: aoTrocar,
        child: Row(
          children: [
            const IconeQuadrado(Icons.link, cor: Cores.primaria, tamanho: 36),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Vincular a uma importância (opcional)',
                style: Txt.corpo.copyWith(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            Text('Escolher', style: Txt.link.copyWith(fontSize: 13)),
          ],
        ),
      );
    }
    return Cartao(
      raio: 16,
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Row(
        children: [
          const IconeQuadrado(
            Icons.calendar_today_outlined,
            cor: Cores.alerta,
            tamanho: 36,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Importância vinculada',
                  style: Txt.pequeno.copyWith(fontSize: 11.5),
                ),
                Text(i.nome, style: Txt.corpoNegrito.copyWith(fontSize: 15)),
                Text(
                  'Vence em ${Fmt.data(i.data)} · Previsto ${Fmt.moeda(i.valorPrevisto)}',
                  style: Txt.pequeno.copyWith(fontSize: 11.5),
                ),
              ],
            ),
          ),
          if (!editando)
            GestureDetector(
              onTap: aoTrocar,
              child: Text('Trocar', style: Txt.link.copyWith(fontSize: 13)),
            ),
        ],
      ),
    );
  }
}
