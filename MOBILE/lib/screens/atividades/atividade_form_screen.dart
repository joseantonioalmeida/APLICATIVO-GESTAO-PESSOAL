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

/// Telas 6 - Cadastrar atividade (e edição, reutilizando o formulário).
class AtividadeFormScreen extends StatefulWidget {
  const AtividadeFormScreen({super.key, this.dataInicial, this.editar});
  final DateTime? dataInicial;
  final Atividade? editar;

  @override
  State<AtividadeFormScreen> createState() => _AtividadeFormScreenState();
}

class _AtividadeFormScreenState extends State<AtividadeFormScreen> {
  final _nome = TextEditingController();
  final _data = TextEditingController();
  final _descricao = TextEditingController();
  final _dataFinal = TextEditingController();

  String? _categoria;
  Prioridade _prioridade = Prioridade.baixa;
  int? _inicio;
  int? _fim;
  Periodicidade _repetir = Periodicidade.nenhuma;
  bool _ateData = false;

  final _erros = <String, String?>{};
  String? _erroGeral;
  bool _salvando = false;
  bool _iniciado = false;
  late String _assinaturaInicial;

  bool get _edicao => widget.editar != null;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_iniciado) return;
    _iniciado = true;
    final e = widget.editar;
    if (e != null) {
      _nome.text = e.nome;
      _categoria = e.categoria;
      _prioridade = e.prioridade;
      _data.text = Fmt.data(e.data);
      _inicio = e.inicio;
      _fim = e.fim;
      _descricao.text = e.descricao;
    } else {
      final base = widget.dataInicial ?? AppScope.of(context).hoje;
      _data.text = Fmt.data(base);
    }
    _assinaturaInicial = _assinatura();
  }

  @override
  void dispose() {
    for (final c in [_nome, _data, _descricao, _dataFinal]) {
      c.dispose();
    }
    super.dispose();
  }

  String _assinatura() => [
    _nome.text,
    _categoria,
    _prioridade.name,
    _data.text,
    _inicio,
    _fim,
    _descricao.text,
    _repetir.name,
    _ateData,
    _dataFinal.text,
  ].join('|');

  bool get _alterado => _assinatura() != _assinaturaInicial;

  int? get _duracao {
    if (_inicio == null || _fim == null || _fim! <= _inicio!) return null;
    return _fim! - _inicio!;
  }

  void _limpa(String campo) {
    if (_erros[campo] != null) setState(() => _erros[campo] = null);
  }

  /// Valida o formulário; devolve o formulário pronto ou null se houver erros.
  AtividadeForm? _validar() {
    final erros = <String, String?>{};
    erros['nome'] = Valida.nome(_nome.text, 'Informe o nome da atividade');
    erros['categoria'] = _categoria == null ? 'Selecione uma categoria' : null;
    final data = Conv.data(_data.text);
    erros['data'] = data == null ? 'Informe uma data válida' : null;
    erros['inicio'] = _inicio == null ? 'Informe o horário inicial' : null;
    erros['fim'] = _fim == null
        ? 'Informe o horário final'
        : (_inicio != null && _fim! <= _inicio!
              ? 'O horário final deve ser posterior ao horário inicial'
              : null);
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
    setState(() {
      _erros
        ..clear()
        ..addAll(erros);
      _erroGeral = null;
    });
    if (erros.values.any((e) => e != null)) return null;
    return AtividadeForm(
      nome: _nome.text.trim(),
      categoria: _categoria!,
      prioridade: _prioridade,
      data: data!,
      inicio: _inicio!,
      fim: _fim!,
      descricao: _descricao.text.trim(),
      periodicidade: _repetir,
      dataFinal: dataFinal,
    );
  }

  Future<void> _salvar() async {
    if (_salvando) return;
    final form = _validar();
    if (form == null) return;
    final escopo = AppScope.of(context);
    final repo = escopo.repositorio;

    // Aviso de sobreposição de horários (6.4.4).
    final sobrepostas = await repo.sobreposicoes(
      form.data,
      form.inicio,
      form.fim,
      ignorarId: widget.editar?.id,
    );
    if (!mounted) return;
    if (sobrepostas.isNotEmpty) {
      final nomes = sobrepostas.map((a) => '“${a.nome}”').take(2).join(' e ');
      final salvarMesmoAssim = await confirmar(
        context,
        titulo: 'Horários sobrepostos',
        mensagem:
            'Este horário coincide com $nomes. '
            'As durações continuam sendo somadas no tempo planejado.',
        confirmarTexto: 'Salvar mesmo assim',
        cancelarTexto: 'Revisar horários',
      );
      if (!salvarMesmoAssim || !mounted) return;
    }

    // Alcance da edição em séries (5.4.4).
    var alcance = EscopoSerie.somenteEsta;
    final e = widget.editar;
    if (e != null && e.serieId != null && !e.concluida) {
      final r = await perguntarEscopo(
        context,
        titulo: 'Editar atividade recorrente',
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
      if (e == null) {
        await repo.criarAtividade(form);
      } else {
        await repo.editarAtividade(e.id, form, alcance);
      }
      if (!mounted) return;
      escopo.dados.mudou();
      ProtecaoSaida.de(context)?.liberar();
      escopo.navegacao.ir(
        IntencaoAba(Aba.atividades, data: form.data, limparFiltros: true),
      );
      Navigator.of(context).pop();
      mostrarMensagem(
        context,
        e == null
            ? 'Atividade cadastrada com sucesso'
            : 'Atividade atualizada com sucesso',
      );
    } on ErroApp catch (er) {
      if (mounted) setState(() => _erroGeral = er.mensagem);
    } catch (_) {
      if (mounted) {
        setState(
          () => _erroGeral =
              'Não foi possível salvar a atividade. Tente novamente',
        );
      }
    } finally {
      if (mounted) setState(() => _salvando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final duracao = _duracao;
    return ProtecaoSaida(
      alterado: () => _alterado,
      pergunta: 'Deseja sair sem salvar a atividade?',
      bloqueado: _salvando,
      child: FormularioScaffold(
        titulo: _edicao ? 'Editar atividade' : 'Cadastrar atividade',
        textoSalvar: _edicao ? 'Salvar alterações' : 'Salvar atividade',
        salvando: _salvando,
        onSalvar: _salvar,
        erroGeral: _erroGeral,
        children: [
          CampoTexto(
            rotulo: 'Título da atividade',
            obrigatorio: true,
            dica: 'Ex.: Estudar para a prova',
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
            opcoes: Categorias.atividades,
            rotuloDe: (c) => c,
            erro: _erros['categoria'],
            aoEscolher: (c) => setState(() {
              _categoria = c;
              _erros['categoria'] = null;
            }),
          ),
          const SizedBox(height: 14),
          const Rotulo('Prioridade', obrigatorio: true),
          Row(
            children: [
              for (final p in Prioridade.values) ...[
                Expanded(
                  child: _FichaPrioridade(
                    prioridade: p,
                    selecionada: p == _prioridade,
                    onTap: () => setState(() => _prioridade = p),
                  ),
                ),
                if (p != Prioridade.alta) const SizedBox(width: 8),
              ],
            ],
          ),
          const SizedBox(height: 14),
          CampoData(
            rotulo: 'Data',
            obrigatorio: true,
            controller: _data,
            erro: _erros['data'],
            onChanged: (_) {
              _limpa('data');
              setState(() {});
            },
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: CampoHora(
                  rotulo: 'Horário inicial',
                  obrigatorio: true,
                  valor: _inicio,
                  erro: _erros['inicio'],
                  aoEscolher: (v) => setState(() {
                    _inicio = v;
                    _erros['inicio'] = null;
                    _erros['fim'] = null;
                    // O final precisa ser maior que o inicial: se deixou de
                    // ser, limpa para o usuário escolher de novo.
                    if (_fim != null && _fim! <= v) {
                      _fim = null;
                      _erros['fim'] = 'Escolha novamente o horário final';
                    }
                  }),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: CampoHora(
                  rotulo: 'Horário final',
                  obrigatorio: true,
                  valor: _fim,
                  habilitado: _inicio != null,
                  minimoExclusivo: _inicio,
                  aoRecusar: (m) => setState(() => _erros['fim'] = m),
                  erro: _erros['fim'],
                  aoEscolher: (v) => setState(() {
                    _fim = v;
                    _erros['fim'] = null;
                  }),
                ),
              ),
            ],
          ),
          if (duracao != null)
            TextoAjuda('Duração calculada: ${Fmt.duracao(duracao)}'),
          const SizedBox(height: 14),
          CampoTexto(
            rotulo: 'Descrição (opcional)',
            dica: 'Adicione detalhes sobre a atividade',
            controller: _descricao,
            linhas: 3,
            maxCaracteres: 200,
            contador: '${_descricao.text.length}/200',
            capitalizacao: TextCapitalization.sentences,
            onChanged: (_) => setState(() {}),
          ),
          if (!_edicao) ...[
            const SizedBox(height: 14),
            CampoSelecao<Periodicidade>(
              rotulo: 'Repetir (opcional)',
              valor: _repetir,
              opcoes: const [
                Periodicidade.nenhuma,
                Periodicidade.diaria,
                Periodicidade.semanal,
                Periodicidade.mensal,
              ],
              rotuloDe: (p) => p.rotulo,
              aoEscolher: (p) => setState(() => _repetir = p),
            ),
            if (_repetir != Periodicidade.nenhuma) ...[
              const SizedBox(height: 14),
              TerminoRepeticao(
                ateData: _ateData,
                controller: _dataFinal,
                erro: _erros['dataFinal'],
                aoMudar: (v) => setState(() => _ateData = v),
                aoDigitar: () => _limpa('dataFinal'),
              ),
            ],
          ],
        ],
      ),
    );
  }
}

class _FichaPrioridade extends StatelessWidget {
  const _FichaPrioridade({
    required this.prioridade,
    required this.selecionada,
    required this.onTap,
  });
  final Prioridade prioridade;
  final bool selecionada;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selecionada,
      label: 'Prioridade ${prioridade.rotulo}',
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          height: 46,
          decoration: BoxDecoration(
            color: selecionada ? Cores.selecionado : Cores.cartao,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: selecionada ? Cores.primaria : Colors.transparent,
              width: 1.2,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: prioridade.cor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                prioridade.rotulo,
                style: Txt.corpoNegrito.copyWith(fontSize: 15),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
