import 'package:flutter/material.dart';

import '../../core/categorias.dart';
import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../core/validadores.dart';
import '../../models/modelos.dart';
import '../../shell/rotas.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import '../../widgets/formulario.dart';

/// Tela 8 - Cadastrar importância (e edição).
class ImportanciaFormScreen extends StatefulWidget {
  const ImportanciaFormScreen({super.key, this.editar});
  final Importancia? editar;

  @override
  State<ImportanciaFormScreen> createState() => _ImportanciaFormScreenState();
}

class _ImportanciaFormScreenState extends State<ImportanciaFormScreen> {
  final _nome = TextEditingController();
  final _data = TextEditingController();
  final _valor = TextEditingController();
  final _descricao = TextEditingController();
  final _dataFinal = TextEditingController();

  String? _categoria;
  bool _temDespesa = false;
  int? _horario;
  Periodicidade _repetir = Periodicidade.nenhuma;
  bool _ateData = false;
  bool _lembrar = false;
  int _diasAntes = 1;
  int _horaLembrete = 9 * 60;

  final _erros = <String, String?>{};
  String? _erroGeral;
  bool _salvando = false;
  bool _iniciado = false;
  late String _assinaturaInicial;

  bool get _edicao => widget.editar != null;
  bool get _paga => widget.editar?.paga ?? false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_iniciado) return;
    _iniciado = true;
    final e = widget.editar;
    if (e != null) {
      _nome.text = e.nome;
      _categoria = e.categoria;
      _data.text = Fmt.data(e.data);
      _temDespesa = e.temDespesa;
      if (e.temDespesa) _valor.text = Fmt.valorSemSimbolo(e.valorPrevisto);
      _horario = e.horario;
      _descricao.text = e.descricao;
      final l = e.lembrete;
      if (l != null) {
        _lembrar = true;
        _diasAntes = l.diasAntes;
        _horaLembrete = l.horario;
      }
    }
    _assinaturaInicial = _assinatura();
  }

  @override
  void dispose() {
    for (final c in [_nome, _data, _valor, _descricao, _dataFinal]) {
      c.dispose();
    }
    super.dispose();
  }

  String _assinatura() => [
    _nome.text,
    _categoria,
    _data.text,
    _temDespesa,
    _valor.text,
    _horario,
    _repetir.name,
    _ateData,
    _dataFinal.text,
    _descricao.text,
    _lembrar,
    _diasAntes,
    _horaLembrete,
  ].join('|');

  bool get _alterado => _assinatura() != _assinaturaInicial;

  void _limpa(String campo) {
    if (_erros[campo] != null) setState(() => _erros[campo] = null);
  }

  Future<void> _mudarDespesa(bool v) async {
    if (v == _temDespesa) return;
    if (!v && _valor.text.trim().isNotEmpty) {
      final ok = await confirmar(
        context,
        titulo: 'Remover o valor previsto?',
        mensagem: 'Ao escolher “Não”, o valor digitado será removido.',
        confirmarTexto: 'Remover valor',
        perigo: true,
      );
      if (!ok || !mounted) return;
      _valor.clear();
    }
    setState(() {
      _temDespesa = v;
      _erros['valor'] = null;
    });
  }

  ImportanciaForm? _validar() {
    final hoje = AppScope.of(context).hoje;
    final erros = <String, String?>{};
    erros['nome'] = Valida.nome(_nome.text, 'Informe o nome da importância');
    erros['categoria'] = _categoria == null ? 'Selecione uma categoria' : null;
    final data = Conv.data(_data.text);
    erros['data'] = data == null ? 'Informe uma data válida' : null;

    var valor = 0;
    if (_temDespesa) {
      final (c, e) = Valida.valor(
        _valor.text,
        mensagemInvalido: 'Informe um valor previsto maior que zero',
      );
      erros['valor'] = e;
      valor = c ?? 0;
    }

    DateTime? dataFinal;
    if (_repetir != Periodicidade.nenhuma && _ateData) {
      dataFinal = Conv.data(_dataFinal.text);
      if (dataFinal == null) {
        erros['dataFinal'] = 'Informe uma data válida';
      } else if (data != null && dataFinal.isBefore(data)) {
        erros['dataFinal'] =
            'A data final não pode ser anterior à primeira ocorrência';
      }
    }

    Lembrete? lembrete;
    if (_lembrar) {
      lembrete = Lembrete(diasAntes: _diasAntes, horario: _horaLembrete);
      if (data != null) {
        final quando = DateTime(
          data.year,
          data.month,
          data.day - _diasAntes,
          _horaLembrete ~/ 60,
          _horaLembrete % 60,
        );
        if (!quando.isAfter(AppScope.of(context).agora)) {
          erros['lembrete'] = 'O lembrete ficaria no passado. Ajuste o lembrete ou desative-o para salvar';
        }
      }
    }
    // Data passada não impede o cadastro (apenas é informada na tela).
    if (data != null && data.isBefore(hoje)) {
      // sem erro
    }

    setState(() {
      _erros
        ..clear()
        ..addAll(erros);
      _erroGeral = null;
    });
    if (erros.values.any((e) => e != null)) return null;
    return ImportanciaForm(
      nome: _nome.text.trim(),
      categoria: _categoria!,
      data: data!,
      temDespesa: _temDespesa,
      valorPrevisto: valor,
      horario: _horario,
      periodicidade: _repetir,
      dataFinal: dataFinal,
      descricao: _descricao.text.trim(),
      lembrete: lembrete,
    );
  }

  Future<void> _salvar() async {
    if (_salvando) return;
    final form = _validar();
    if (form == null) return;
    final escopo = AppScope.of(context);
    final repo = escopo.repositorio;

    var alcance = EscopoSerie.somenteEsta;
    final e = widget.editar;
    if (e != null && e.serieId != null && !e.concluida) {
      final r = await perguntarEscopo(
        context,
        titulo: 'Editar importância recorrente',
        confirmar: 'Salvar alterações',
      );
      if (r == null || !mounted) return;
      alcance = r;
    }

    setState(() {
      _salvando = true;
      _erroGeral = null;
    });
    try {
      Importancia salva;
      if (e == null) {
        salva = await repo.criarImportancia(form);
      } else {
        await repo.editarImportancia(e.id, form, alcance);
        salva = e;
      }
      if (!mounted) return;
      escopo.dados.mudou();
      ProtecaoSaida.de(context)?.liberar();
      escopo.navegacao.ir(
        IntencaoAba(
          Aba.importancias,
          filtroImportancia: FiltroImportancia.todos,
          destaqueId: salva.id,
        ),
      );
      Navigator.of(context).pop();
      mostrarMensagem(
        context,
        e == null
            ? 'Importância cadastrada com sucesso'
            : 'Importância atualizada com sucesso',
      );
    } on ErroApp catch (er) {
      if (mounted) setState(() => _erroGeral = er.mensagem);
    } catch (_) {
      if (mounted) {
        setState(
          () => _erroGeral =
              'Não foi possível salvar a importância. Tente novamente',
        );
      }
    } finally {
      if (mounted) setState(() => _salvando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final hoje = AppScope.of(context).hoje;
    final dataDigitada = Conv.data(_data.text);
    final dataPassada = dataDigitada != null && dataDigitada.isBefore(hoje);

    return ProtecaoSaida(
      alterado: () => _alterado,
      pergunta: 'Deseja sair sem salvar a importância?',
      bloqueado: _salvando,
      child: FormularioScaffold(
        titulo: _edicao ? 'Editar importância' : 'Cadastrar importância',
        textoSalvar: _edicao ? 'Salvar alterações' : 'Salvar importância',
        salvando: _salvando,
        onSalvar: _salvar,
        erroGeral: _erroGeral,
        children: [
          CampoTexto(
            rotulo: 'Nome da importância',
            obrigatorio: true,
            dica: 'Ex.: Pagamento da internet',
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
          CampoSelecao<String>(
            rotulo: 'Categoria',
            obrigatorio: true,
            dica: 'Selecione uma categoria',
            valor: _categoria,
            opcoes: Categorias.importancias,
            rotuloDe: (c) => c,
            erro: _erros['categoria'],
            aoEscolher: (c) => setState(() {
              _categoria = c;
              _erros['categoria'] = null;
            }),
          ),
          const SizedBox(height: 14),
          CampoData(
            rotulo: 'Data do compromisso ou vencimento',
            obrigatorio: true,
            controller: _data,
            erro: _erros['data'],
            onChanged: (_) {
              _limpa('data');
              _limpa('lembrete');
              setState(() {});
            },
          ),
          if (dataPassada && _erros['data'] == null)
            const TextoAjuda(
              'Esta data já passou: a importância aparecerá como atrasada.',
            ),
          const SizedBox(height: 14),
          const Rotulo('Possui despesa?', obrigatorio: true),
          Row(
            children: [
              Expanded(
                child: _OpcaoSimNao(
                  texto: 'Sim',
                  selecionada: _temDespesa,
                  onTap: _paga ? null : () => _mudarDespesa(true),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _OpcaoSimNao(
                  texto: 'Não',
                  selecionada: !_temDespesa,
                  onTap: _paga ? null : () => _mudarDespesa(false),
                ),
              ),
            ],
          ),
          if (_paga)
            const TextoAjuda(
              'Esta importância já foi paga. Altere o pagamento em “Ver despesa”.',
            ),
          if (_temDespesa) ...[
            const SizedBox(height: 14),
            CampoValor(
              rotulo: 'Valor previsto',
              obrigatorio: true,
              controller: _valor,
              erro: _erros['valor'],
              onChanged: (_) => _limpa('valor'),
            ),
            if (_erros['valor'] == null)
              const TextoAjuda('Maior que zero, com até duas casas decimais.'),
          ],
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: CampoHora(
                  rotulo: 'Horário\n(opcional)',
                  valor: _horario,
                  dica: '--:--',
                  aoLimpar: () => setState(() => _horario = null),
                  aoEscolher: (v) => setState(() => _horario = v),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: CampoSelecao<Periodicidade>(
                  rotulo: 'Repetir\n(opcional)',
                  valor: _repetir,
                  opcoes: Periodicidade.values,
                  rotuloDe: (p) => p.rotulo,
                  aoEscolher: _edicao
                      ? (_) {}
                      : (p) => setState(() => _repetir = p),
                ),
              ),
            ],
          ),
          if (_repetir != Periodicidade.nenhuma && !_edicao) ...[
            const SizedBox(height: 14),
            TerminoRepeticao(
              ateData: _ateData,
              controller: _dataFinal,
              erro: _erros['dataFinal'],
              aoMudar: (v) => setState(() => _ateData = v),
              aoDigitar: () => _limpa('dataFinal'),
            ),
          ],
          const SizedBox(height: 14),
          CampoTexto(
            rotulo: 'Descrição ou referência (opcional)',
            dica: 'Ex.: Vivo Fibra',
            controller: _descricao,
            linhas: 2,
            maxCaracteres: 200,
            contador: '${_descricao.text.length}/200',
            capitalizacao: TextCapitalization.sentences,
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 16),
          _CartaoLembrete(
            ativo: _lembrar,
            dias: _diasAntes,
            horario: _horaLembrete,
            erro: _erros['lembrete'],
            aoAtivar: (v) => setState(() {
              _lembrar = v;
              _erros['lembrete'] = null;
            }),
            aoEscolherDias: (d) => setState(() {
              _diasAntes = d;
              _erros['lembrete'] = null;
            }),
            aoEscolherHorario: (h) => setState(() {
              _horaLembrete = h;
              _erros['lembrete'] = null;
            }),
          ),
        ],
      ),
    );
  }
}

class _OpcaoSimNao extends StatelessWidget {
  const _OpcaoSimNao({
    required this.texto,
    required this.selecionada,
    required this.onTap,
  });
  final String texto;
  final bool selecionada;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selecionada,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          height: 44,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: selecionada ? Cores.borda : Cores.cartao,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: selecionada
                  ? Cores.primaria.withValues(alpha: 0.7)
                  : Colors.transparent,
            ),
          ),
          child: Text(
            texto,
            style: Txt.corpoNegrito.copyWith(
              fontSize: 15,
              color: selecionada ? Cores.texto : Cores.textoSuave,
            ),
          ),
        ),
      ),
    );
  }
}

class _CartaoLembrete extends StatelessWidget {
  const _CartaoLembrete({
    required this.ativo,
    required this.dias,
    required this.horario,
    required this.aoAtivar,
    required this.aoEscolherDias,
    required this.aoEscolherHorario,
    this.erro,
  });
  final bool ativo;
  final int dias;
  final int horario;
  final String? erro;
  final ValueChanged<bool> aoAtivar;
  final ValueChanged<int> aoEscolherDias;
  final ValueChanged<int> aoEscolherHorario;

  static const _opcoes = [
    (0, 'No dia'),
    (1, '1 dia antes'),
    (3, '3 dias antes'),
    (7, '7 dias antes'),
  ];

  @override
  Widget build(BuildContext context) {
    Widget ficha(int d, String texto) {
      final sel = d == dias;
      return GestureDetector(
        onTap: () => aoEscolherDias(d),
        child: Container(
          height: 42,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: sel ? Cores.selecionado : Cores.fundo.withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: sel
                  ? Cores.primaria.withValues(alpha: 0.6)
                  : Colors.transparent,
            ),
          ),
          child: Text(
            texto,
            style: Txt.corpoNegrito.copyWith(
              fontSize: 14,
              color: sel ? Cores.primaria : Cores.textoSuave,
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Cores.cartao,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: erro != null ? Cores.perigo : Colors.transparent,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Lembrar-me',
                      style: Txt.corpoNegrito.copyWith(fontSize: 15.5),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Gera uma notificação no aplicativo',
                      style: Txt.pequeno.copyWith(fontSize: 12.5),
                    ),
                  ],
                ),
              ),
              Switch(
                value: ativo,
                onChanged: aoAtivar,
                activeThumbColor: Cores.fundo,
                activeTrackColor: Cores.primaria,
                inactiveThumbColor: Cores.textoSuave,
                inactiveTrackColor: Cores.borda,
              ),
            ],
          ),
          if (ativo) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: ficha(_opcoes[0].$1, _opcoes[0].$2)),
                const SizedBox(width: 8),
                Expanded(child: ficha(_opcoes[1].$1, _opcoes[1].$2)),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(child: ficha(_opcoes[2].$1, _opcoes[2].$2)),
                const SizedBox(width: 8),
                Expanded(child: ficha(_opcoes[3].$1, _opcoes[3].$2)),
              ],
            ),
            const SizedBox(height: 14),
            CampoHora(
              rotulo: 'Horário do lembrete',
              obrigatorio: true,
              valor: horario,
              aoEscolher: aoEscolherHorario,
            ),
            const TextoAjuda(
              'O lembrete ficará disponível nas notificações do aplicativo.',
            ),
          ],
          if (erro != null) TextoAjuda(erro!, erro: true),
        ],
      ),
    );
  }
}
