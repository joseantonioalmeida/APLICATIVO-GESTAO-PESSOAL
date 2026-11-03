import 'package:flutter/material.dart';

import '../core/categorias.dart';
import '../core/formatadores.dart';
import '../core/theme.dart';
import '../models/modelos.dart';

/// Linha de movimentação (receita/despesa) usada na Início e no Financeiro.
class LinhaMovimentacao extends StatelessWidget {
  const LinhaMovimentacao({
    super.key,
    required this.mov,
    required this.onTap,
    this.detalhada = false,
    this.destaque = false,
    this.onMenu,
  });
  final Movimentacao mov;
  final VoidCallback onTap;

  /// Financeiro: "Despesa · Alimentação · 28/09/2025". Início: "28/09/2025 · Despesa".
  final bool detalhada;
  final bool destaque;
  final ValueChanged<String>? onMenu;

  @override
  Widget build(BuildContext context) {
    final cor = mov.receita ? Cores.sucesso : Cores.perigo;
    final icone = mov.receita
        ? Icons.file_download_outlined
        : Categorias.icone(mov.categoria);
    final subtitulo = detalhada
        ? '${mov.tipo.rotulo} · ${mov.categoria} · ${Fmt.data(mov.data)}'
        : '${Fmt.data(mov.data)} · ${mov.tipo.rotulo}';
    return InkWell(
      onTap: onTap,
      child: Container(
        color: destaque ? Cores.selecionado.withValues(alpha: 0.5) : null,
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: Cores.fundo.withValues(alpha: 0.55),
                borderRadius: BorderRadius.circular(11),
              ),
              child: Icon(icone, size: 18, color: cor),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    mov.nome,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Txt.corpo.copyWith(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitulo,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Txt.pequeno.copyWith(fontSize: 12.5),
                  ),
                  if (mov.importanciaId != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        'Vinculada a uma importância',
                        style: Txt.pequeno.copyWith(
                          color: Cores.primaria,
                          fontSize: 12,
                        ),
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Text(
              Fmt.moedaComSinal(mov.valor, entrada: mov.receita),
              style: Txt.corpoNegrito.copyWith(color: cor, fontSize: 15),
            ),
            if (onMenu != null)
              PopupMenuButton<String>(
                padding: EdgeInsets.zero,
                icon: const Icon(
                  Icons.more_vert,
                  size: 18,
                  color: Cores.textoSuave,
                ),
                onSelected: onMenu,
                itemBuilder: (_) => const [
                  PopupMenuItem(value: 'editar', child: Text('Editar')),
                  PopupMenuItem(value: 'excluir', child: Text('Excluir')),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

/// Divisor fino entre linhas de uma lista dentro de um cartão.
class DivisorFino extends StatelessWidget {
  const DivisorFino({super.key});
  @override
  Widget build(BuildContext context) =>
      const Divider(height: 1, thickness: 1, color: Cores.borda);
}

/// Texto "Hoje", "Amanhã", "Em X dias", "Atrasada há X dias".
class PrazoImportancia {
  const PrazoImportancia(this.texto, this.cor);
  final String texto;
  final Color cor;

  static PrazoImportancia? de(Importancia i, DateTime hoje) {
    if (i.concluida) return null;
    final d = Fmt.diasEntre(hoje, i.data);
    if (d < 0) {
      final n = -d;
      return PrazoImportancia(
        'Atrasada há $n dia${n == 1 ? '' : 's'}',
        Cores.perigo,
      );
    }
    if (d == 0) return const PrazoImportancia('Hoje', Cores.alerta);
    if (d == 1) return const PrazoImportancia('Amanhã', Cores.textoSuave);
    return PrazoImportancia('Em $d dias', Cores.textoSuave);
  }
}
