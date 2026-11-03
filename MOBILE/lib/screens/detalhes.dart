import 'package:flutter/material.dart';

import '../core/formatadores.dart';
import '../core/theme.dart';
import '../models/modelos.dart';
import '../shell/rotas.dart';
import '../state/app_scope.dart';
import '../widgets/comuns.dart';
import '../widgets/linhas.dart';

/// Folha inferior padrão para detalhes de um registro.
Future<void> _abrirFolha(
  BuildContext context,
  Widget Function(BuildContext) construir,
) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (ctx) => DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.82,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      builder: (ctx, rolagem) => Column(
        children: [
          const SizedBox(height: 10),
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Cores.borda,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          Expanded(
            child: ListView(
              controller: rolagem,
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
              children: [construir(ctx)],
            ),
          ),
        ],
      ),
    ),
  );
}

class _Campo extends StatelessWidget {
  const _Campo(this.rotulo, this.valor, {this.cor});
  final String rotulo;
  final String valor;
  final Color? cor;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 7),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 118,
          child: Text(rotulo, style: Txt.rotulo.copyWith(fontSize: 13.5)),
        ),
        Expanded(
          child: Text(
            valor,
            style: Txt.corpo.copyWith(
              fontSize: 14.5,
              fontWeight: FontWeight.w600,
              color: cor ?? Cores.texto,
            ),
          ),
        ),
      ],
    ),
  );
}

class _Acao extends StatelessWidget {
  const _Acao(
    this.texto,
    this.onTap, {
    this.perigo = false,
    this.principal = false,
  });
  final String texto;
  final VoidCallback onTap;
  final bool perigo;
  final bool principal;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: principal
          ? BotaoPrimario(texto: texto, onPressed: onTap, altura: 48)
          : SizedBox(
              width: double.infinity,
              height: 46,
              child: OutlinedButton(
                onPressed: onTap,
                style: OutlinedButton.styleFrom(
                  side: BorderSide(
                    color: perigo
                        ? Cores.perigo.withValues(alpha: 0.6)
                        : Cores.borda,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Text(
                  texto,
                  style: Txt.corpoNegrito.copyWith(
                    color: perigo ? Cores.perigo : Cores.texto,
                    fontSize: 14.5,
                  ),
                ),
              ),
            ),
    );
  }
}

// ---------------------------------------------------------------- Atividade
Future<void> abrirDetalheAtividade(BuildContext context, String id) {
  return _abrirFolha(
    context,
    (ctx) => BlocoAsync<Atividade>(
      alturaCarregando: 200,
      mensagemErro: 'Não foi possível carregar a atividade. Tente novamente',
      carregar: () => AppScope.of(ctx).repositorio.obterAtividade(id),
      construir: (c, a) => _DetalheAtividade(a),
    ),
  );
}

class _DetalheAtividade extends StatelessWidget {
  const _DetalheAtividade(this.a);
  final Atividade a;

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final nav = Navigator.of(context);
    Future<void> alternar() async {
      try {
        await escopo.repositorio.alterarConclusaoAtividade(a.id, !a.concluida);
        escopo.dados.mudou();
        if (context.mounted) {
          mostrarMensagem(
            context,
            a.concluida ? 'Atividade reaberta' : 'Atividade concluída',
          );
        }
      } on ErroApp catch (e) {
        if (context.mounted) mostrarMensagem(context, e.mensagem, erro: true);
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(a.nome, style: Txt.tituloForm),
        const SizedBox(height: 4),
        TextoSituacao(
          a.concluida ? 'Concluída' : 'Pendente',
          a.concluida ? Cores.sucesso : Cores.alerta,
          tamanho: 14,
        ),
        const SizedBox(height: 12),
        _Campo('Categoria', a.categoria),
        _Campo('Prioridade', a.prioridade.rotulo, cor: a.prioridade.cor),
        _Campo('Data', Fmt.dataCompleta(a.data)),
        _Campo('Horário', '${Fmt.hora(a.inicio)} – ${Fmt.hora(a.fim)}'),
        _Campo('Duração', Fmt.duracao(a.duracaoMin)),
        if (a.concluida)
          _Campo(
            'Concluída em',
            '${Fmt.data(a.concluidaEm!)} às ${Fmt.hora(a.concluidaEm!.hour * 60 + a.concluidaEm!.minute)}',
            cor: Cores.sucesso,
          ),
        _Campo(
          'Repetição',
          a.periodicidade == Periodicidade.nenhuma
              ? 'Não repete'
              : a.periodicidade.rotulo,
        ),
        if (a.descricao.isNotEmpty) _Campo('Descrição', a.descricao),
        const SizedBox(height: 6),
        _Acao(
          a.concluida ? 'Reabrir atividade' : 'Concluir atividade',
          () async {
            await alternar();
            if (nav.mounted) nav.pop();
          },
          principal: true,
        ),
        _Acao('Editar', () {
          nav.pop();
          abrirFormAtividade(context, editar: a);
        }),
        _Acao('Excluir', () async {
          final escopoSerie = await confirmarExclusaoAtividade(context, a);
          if (escopoSerie == null) return;
          try {
            await escopo.repositorio.excluirAtividade(a.id, escopoSerie);
            escopo.dados.mudou();
            if (nav.mounted) nav.pop();
            if (context.mounted) mostrarMensagem(context, 'Atividade excluída');
          } on ErroApp catch (e) {
            if (context.mounted) {
              mostrarMensagem(context, e.mensagem, erro: true);
            }
          }
        }, perigo: true),
      ],
    );
  }
}

// -------------------------------------------------------------- Importância
Future<void> abrirDetalheImportancia(BuildContext context, String id) async {
  final escopo = AppScope.of(context);
  // Se a importância foi excluída, informa em vez de abrir uma folha vazia.
  try {
    await escopo.repositorio.obterImportancia(id);
  } on ErroApp catch (e) {
    if (context.mounted) mostrarMensagem(context, e.mensagem, erro: true);
    return;
  }
  if (!context.mounted) return;
  await _abrirFolha(
    context,
    (ctx) => BlocoAsync<Importancia>(
      alturaCarregando: 200,
      mensagemErro: 'Não foi possível carregar a importância. Tente novamente',
      carregar: () => AppScope.of(ctx).repositorio.obterImportancia(id),
      construir: (c, i) => _DetalheImportancia(i),
    ),
  );
}

class _DetalheImportancia extends StatelessWidget {
  const _DetalheImportancia(this.i);
  final Importancia i;

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final nav = Navigator.of(context);
    final prazo = PrazoImportancia.de(i, escopo.hoje);
    final situacao = i.paga
        ? 'Concluída · Pago'
        : (i.concluida ? 'Concluída' : 'Pendente');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(i.nome, style: Txt.tituloForm),
        const SizedBox(height: 4),
        Row(
          children: [
            TextoSituacao(
              situacao,
              i.concluida ? Cores.sucesso : Cores.alerta,
              tamanho: 14,
            ),
            if (prazo != null) ...[
              const SizedBox(width: 10),
              TextoSituacao(prazo.texto, prazo.cor, tamanho: 14),
            ],
          ],
        ),
        const SizedBox(height: 12),
        _Campo('Categoria', i.categoria),
        _Campo(
          'Data',
          '${Fmt.dataCompleta(i.data)}${i.horario != null ? ' · ${Fmt.hora(i.horario!)}' : ''}',
        ),
        if (i.descricao.isNotEmpty) _Campo('Referência', i.descricao),
        if (i.temDespesa)
          _Campo('Valor previsto', Fmt.moeda(i.valorPrevisto))
        else
          _Campo('Despesa', 'Sem despesa'),
        if (i.paga) ...[
          _Campo('Valor pago', Fmt.moeda(i.valorPago ?? 0), cor: Cores.sucesso),
          if (i.dataPagamento != null)
            _Campo('Data do pagamento', Fmt.data(i.dataPagamento!)),
        ],
        _Campo(
          'Repetição',
          i.periodicidade == Periodicidade.nenhuma
              ? 'Não repete'
              : i.periodicidade.rotulo,
        ),
        if (i.lembrete != null)
          _Campo(
            'Lembrete',
            '${i.lembrete!.diasAntes == 0 ? 'No dia' : '${i.lembrete!.diasAntes} dia${i.lembrete!.diasAntes == 1 ? '' : 's'} antes'} às ${Fmt.hora(i.lembrete!.horario)}',
          ),
        const SizedBox(height: 6),
        if (i.temDespesa && !i.paga && !i.concluida)
          _Acao('Registrar pagamento', () {
            nav.pop();
            registrarPagamento(context, i);
          }, principal: true),
        if (i.paga)
          _Acao('Ver despesa', () async {
            nav.pop();
            if (i.movimentacaoId != null) {
              abrirDetalheMovimentacao(context, i.movimentacaoId!);
            }
          }, principal: true),
        if (!i.temDespesa)
          _Acao(i.concluida ? 'Reabrir' : 'Marcar como concluída', () async {
            try {
              await escopo.repositorio.alterarConclusaoImportancia(
                i.id,
                !i.concluida,
              );
              escopo.dados.mudou();
              if (nav.mounted) nav.pop();
            } on ErroApp catch (e) {
              if (context.mounted) {
                mostrarMensagem(context, e.mensagem, erro: true);
              }
            }
          }, principal: true),
        _Acao('Editar', () {
          nav.pop();
          abrirFormImportancia(context, editar: i);
        }),
        _Acao('Excluir', () async {
          final alcance = await confirmarExclusaoImportancia(context, i);
          if (alcance == null) return;
          try {
            await escopo.repositorio.excluirImportancia(i.id, alcance);
            escopo.dados.mudou();
            if (nav.mounted) nav.pop();
            if (context.mounted) {
              mostrarMensagem(context, 'Importância excluída');
            }
          } on ErroApp catch (e) {
            if (context.mounted) {
              mostrarMensagem(context, e.mensagem, erro: true);
            }
          }
        }, perigo: true),
      ],
    );
  }
}

/// "Registrar pagamento": nova despesa ou vincular uma existente (11.5.5).
Future<void> registrarPagamento(BuildContext context, Importancia i) async {
  final escolha = await escolherOpcao<String>(
    context,
    titulo: 'Registrar pagamento',
    opcoes: const ['nova', 'existente'],
    rotuloDe: (v) =>
        v == 'nova' ? 'Registrar nova despesa' : 'Vincular despesa existente',
  );
  if (escolha == null || !context.mounted) return;
  if (escolha == 'nova') {
    final salvo = await abrirFormDespesa(context, importancia: i);
    if (salvo == true && context.mounted) {
      abrirDetalheImportancia(context, i.id);
    }
    return;
  }
  final escopo = AppScope.of(context);
  final lista = await escopo.repositorio.despesasSemVinculo();
  if (!context.mounted) return;
  if (lista.isEmpty) {
    mostrarMensagem(
      context,
      'Você não tem despesas sem vínculo para associar',
      erro: true,
    );
    return;
  }
  final m = await escolherOpcao<Movimentacao>(
    context,
    titulo: 'Escolha a despesa',
    opcoes: lista,
    rotuloDe: (m) => '${m.nome} · ${Fmt.data(m.data)} · ${Fmt.moeda(m.valor)}',
  );
  if (m == null || !context.mounted) return;
  final ok = await confirmar(
    context,
    titulo: 'Vincular esta despesa?',
    mensagem:
        '“${m.nome}” (${Fmt.moeda(m.valor)}) passará a quitar “${i.nome}”. '
        'O lançamento não será duplicado nem alterado.',
    confirmarTexto: 'Vincular',
  );
  if (!ok || !context.mounted) return;
  try {
    await escopo.repositorio.vincularDespesa(i.id, m.id);
    escopo.dados.mudou();
    if (context.mounted) {
      mostrarMensagem(context, 'Pagamento registrado com sucesso');
      abrirDetalheImportancia(context, i.id);
    }
  } on ErroApp catch (e) {
    if (context.mounted) mostrarMensagem(context, e.mensagem, erro: true);
  }
}

// ------------------------------------------------------------ Movimentação
Future<void> abrirDetalheMovimentacao(BuildContext context, String id) {
  return _abrirFolha(
    context,
    (ctx) => BlocoAsync<Movimentacao>(
      alturaCarregando: 200,
      mensagemErro: 'Não foi possível carregar o lançamento. Tente novamente',
      carregar: () => AppScope.of(ctx).repositorio.obterMovimentacao(id),
      construir: (c, m) => _DetalheMovimentacao(m),
    ),
  );
}

class _DetalheMovimentacao extends StatelessWidget {
  const _DetalheMovimentacao(this.m);
  final Movimentacao m;

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final nav = Navigator.of(context);
    final cor = m.receita ? Cores.sucesso : Cores.perigo;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(m.nome, style: Txt.tituloForm),
        const SizedBox(height: 4),
        Text(
          Fmt.moedaComSinal(m.valor, entrada: m.receita),
          style: Txt.titulo.copyWith(fontSize: 26, color: cor),
        ),
        const SizedBox(height: 12),
        _Campo('Tipo', m.tipo.rotulo, cor: cor),
        _Campo('Categoria', m.categoria),
        _Campo(m.receita ? 'Recebimento' : 'Pagamento', Fmt.data(m.data)),
        if (m.descricao.isNotEmpty) _Campo('Descrição', m.descricao),
        if (m.contraparte.isNotEmpty)
          _Campo(m.receita ? 'Origem' : 'Destinatário', m.contraparte),
        if (m.forma != null)
          _Campo(
            m.receita ? 'Forma de recebimento' : 'Forma de pagamento',
            m.forma!,
          ),
        if (m.importanciaId != null)
          _Campo(
            'Importância',
            'Vinculada a uma importância',
            cor: Cores.primaria,
          ),
        const SizedBox(height: 6),
        if (m.importanciaId != null)
          _Acao('Ver importância', () {
            nav.pop();
            abrirDetalheImportancia(context, m.importanciaId!);
          }, principal: true),
        _Acao('Editar', () {
          nav.pop();
          abrirFormMovimentacao(context, m);
        }),
        _Acao('Excluir', () async {
          final ok = await confirmarExclusaoMovimentacao(context, m);
          if (!ok) return;
          try {
            await escopo.repositorio.excluirMovimentacao(m.id);
            escopo.dados.mudou();
            if (nav.mounted) nav.pop();
            if (context.mounted) {
              mostrarMensagem(
                context,
                m.receita ? 'Receita excluída' : 'Despesa excluída',
              );
            }
          } on ErroApp catch (e) {
            if (context.mounted) {
              mostrarMensagem(context, e.mensagem, erro: true);
            }
          }
        }, perigo: true),
      ],
    );
  }
}

// -------------------------------------------------------------- Confirmações
/// Pergunta o alcance de uma edição/exclusão em série (5.4.4).
Future<EscopoSerie?> perguntarEscopo(
  BuildContext context, {
  required String titulo,
  required String confirmar,
  String? mensagem,
}) {
  var escolhido = EscopoSerie.somenteEsta;
  return showDialog<EscopoSerie>(
    context: context,
    builder: (ctx) => StatefulBuilder(
      builder: (ctx, setState) => AlertDialog(
        title: Text(titulo),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (mensagem != null) ...[
              Text(mensagem),
              const SizedBox(height: 8),
            ],
            RadioGroup<EscopoSerie>(
              groupValue: escolhido,
              onChanged: (v) => setState(() => escolhido = v ?? escolhido),
              child: const Column(
                children: [
                  RadioListTile<EscopoSerie>(
                    contentPadding: EdgeInsets.zero,
                    activeColor: Cores.primaria,
                    value: EscopoSerie.somenteEsta,
                    title: Text('Somente esta ocorrência'),
                  ),
                  RadioListTile<EscopoSerie>(
                    contentPadding: EdgeInsets.zero,
                    activeColor: Cores.primaria,
                    value: EscopoSerie.estaEProximas,
                    title: Text('Esta e as próximas pendentes'),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(
              'Cancelar',
              style: Txt.corpoNegrito.copyWith(color: Cores.textoSuave),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, escolhido),
            child: Text(
              confirmar,
              style: Txt.corpoNegrito.copyWith(color: Cores.primaria),
            ),
          ),
        ],
      ),
    ),
  );
}

/// Devolve o alcance escolhido, ou null se o usuário cancelou.
Future<EscopoSerie?> confirmarExclusaoAtividade(
  BuildContext context,
  Atividade a,
) async {
  if (a.serieId != null && !a.concluida) {
    return perguntarEscopo(
      context,
      titulo: 'Excluir atividade recorrente',
      mensagem: 'Deseja excluir a atividade ${a.nome}? Escolha o alcance:',
      confirmar: 'Excluir',
    );
  }
  final ok = await confirmar(
    context,
    titulo: 'Deseja excluir a atividade ${a.nome}?',
    confirmarTexto: 'Excluir',
    perigo: true,
  );
  return ok ? EscopoSerie.somenteEsta : null;
}

Future<EscopoSerie?> confirmarExclusaoImportancia(
  BuildContext context,
  Importancia i,
) async {
  final aviso = i.paga
      ? 'A despesa já registrada será mantida no Financeiro, sem vínculo.'
      : null;
  if (i.serieId != null && !i.concluida) {
    return perguntarEscopo(
      context,
      titulo: 'Deseja excluir esta importância?',
      mensagem: aviso,
      confirmar: 'Excluir',
    );
  }
  final ok = await confirmar(
    context,
    titulo: 'Deseja excluir esta importância?',
    mensagem: aviso,
    confirmarTexto: 'Excluir',
    perigo: true,
  );
  return ok ? EscopoSerie.somenteEsta : null;
}

Future<bool> confirmarExclusaoMovimentacao(
  BuildContext context,
  Movimentacao m,
) {
  final partes = <String>[
    '${m.nome} · ${Fmt.data(m.data)} · ${Fmt.moeda(m.valor)}',
    'A exclusão atualizará os totais.',
    if (m.importanciaId != null)
      'A importância vinculada voltará a ficar pendente.',
  ];
  return confirmar(
    context,
    titulo: m.receita
        ? 'Deseja excluir esta receita?'
        : 'Deseja excluir esta despesa?',
    mensagem: partes.join('\n'),
    confirmarTexto: 'Excluir',
    perigo: true,
  );
}
