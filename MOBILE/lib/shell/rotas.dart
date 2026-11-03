import 'package:flutter/material.dart';

import '../core/theme.dart';
import '../models/modelos.dart';
import '../screens/atividades/atividade_form_screen.dart';
import '../screens/financeiro/movimentacao_form_screen.dart';
import '../screens/financeiro/movimentacoes_screen.dart';
import '../screens/importancias/importancia_form_screen.dart';
import '../screens/perfil/notificacoes_screen.dart';
import '../widgets/comuns.dart';

export '../screens/detalhes.dart';

/// Atalhos de navegação para as telas de cadastro e consultas.

Future<void> abrirFormAtividade(
  BuildContext context, {
  DateTime? data,
  Atividade? editar,
}) {
  return Navigator.of(context).push(
    MaterialPageRoute(
      builder: (_) => AtividadeFormScreen(dataInicial: data, editar: editar),
    ),
  );
}

Future<void> abrirFormImportancia(BuildContext context, {Importancia? editar}) {
  return Navigator.of(context).push(
    MaterialPageRoute(builder: (_) => ImportanciaFormScreen(editar: editar)),
  );
}

Future<bool?> abrirFormReceita(BuildContext context) {
  return Navigator.of(context).push<bool>(
    MaterialPageRoute(
      builder: (_) => const MovimentacaoFormScreen(tipo: TipoMov.receita),
    ),
  );
}

Future<bool?> abrirFormDespesa(
  BuildContext context, {
  Importancia? importancia,
}) {
  return Navigator.of(context).push<bool>(
    MaterialPageRoute(
      builder: (_) => MovimentacaoFormScreen(
        tipo: TipoMov.despesa,
        importancia: importancia,
      ),
    ),
  );
}

/// Edição de um lançamento existente (receita ou despesa).
Future<bool?> abrirFormMovimentacao(BuildContext context, Movimentacao m) {
  return Navigator.of(context).push<bool>(
    MaterialPageRoute(
      builder: (_) => MovimentacaoFormScreen(tipo: m.tipo, editar: m),
    ),
  );
}

Future<void> abrirMovimentacoes(
  BuildContext context, {
  required int ano,
  required int mes,
  TipoMov? tipo,
  String? categoria,
}) {
  return Navigator.of(context).push(
    MaterialPageRoute(
      builder: (_) => MovimentacoesScreen(
        ano: ano,
        mes: mes,
        tipo: tipo,
        categoria: categoria,
      ),
    ),
  );
}

Future<void> abrirNotificacoes(BuildContext context) {
  return Navigator.of(context)
      .push(MaterialPageRoute(builder: (_) => const NotificacoesScreen()));
}

/// Folha "Cadastrar receita / Cadastrar despesa" (acesso rápido da Início).
Future<void> escolherReceitaOuDespesa(BuildContext context) {
  return showModalBottomSheet<void>(
    context: context,
    builder: (ctx) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 20, 24, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Adicionar', style: Txt.secao),
            const SizedBox(height: 14),
            _OpcaoCadastro(
              icone: Icons.south_west,
              cor: Cores.sucesso,
              texto: 'Cadastrar receita',
              onTap: () {
                Navigator.pop(ctx);
                abrirFormReceita(context);
              },
            ),
            const SizedBox(height: 10),
            _OpcaoCadastro(
              icone: Icons.north_east,
              cor: Cores.perigo,
              texto: 'Cadastrar despesa',
              onTap: () {
                Navigator.pop(ctx);
                abrirFormDespesa(context);
              },
            ),
          ],
        ),
      ),
    ),
  );
}

class _OpcaoCadastro extends StatelessWidget {
  const _OpcaoCadastro({
    required this.icone,
    required this.cor,
    required this.texto,
    required this.onTap,
  });
  final IconData icone;
  final Color cor;
  final String texto;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Cartao(
      cor: Cores.fundo.withValues(alpha: 0.5),
      raio: 16,
      onTap: onTap,
      child: Row(
        children: [
          IconeQuadrado(icone, cor: cor, tamanho: 38),
          const SizedBox(width: 14),
          Expanded(child: Text(texto, style: Txt.corpoNegrito)),
          const Icon(Icons.chevron_right, color: Cores.textoSuave),
        ],
      ),
    );
  }
}
