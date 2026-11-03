import 'package:flutter/material.dart';

import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../models/modelos.dart';
import '../../shell/rotas.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';

/// Lista de lembretes gerados para Importâncias (4.1.9).
class NotificacoesScreen extends StatelessWidget {
  const NotificacoesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 10, 16, 0),
              child: Row(
                children: [
                  BotaoVoltar(),
                  SizedBox(width: 4),
                  Expanded(child: Text('Notificações', style: Txt.tituloForm)),
                ],
              ),
            ),
            Expanded(
              child: BlocoAsync<List<Notificacao>>(
                alturaCarregando: 300,
                mensagemErro: 'Não foi possível carregar suas notificações. Tente novamente',
                carregar: escopo.repositorio.listarNotificacoes,
                construir: (ctx, lista) {
                  if (lista.isEmpty) {
                    return const Center(
                      child: EstadoVazio(
                        mensagem: 'Você não tem notificações',
                        icone: Icons.notifications_none,
                      ),
                    );
                  }
                  return ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
                    itemCount: lista.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 10),
                    itemBuilder: (ctx, i) {
                      final n = lista[i];
                      return Cartao(
                        raio: 18,
                        onTap: () async {
                          await escopo.repositorio.marcarNotificacaoLida(n.id);
                          escopo.dados.mudou();
                          if (!ctx.mounted) return;
                          // Ler não conclui nem paga o compromisso.
                          await abrirDetalheImportancia(ctx, n.importanciaId);
                        },
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const IconeQuadrado(
                              Icons.notifications_none,
                              cor: Cores.primaria,
                              tamanho: 38,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    n.titulo,
                                    style: Txt.corpoNegrito.copyWith(
                                      fontWeight: n.lida
                                          ? FontWeight.w600
                                          : FontWeight.w800,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    n.mensagem,
                                    style: Txt.pequeno.copyWith(fontSize: 13),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '${Fmt.data(n.geradaEm)} às ${Fmt.hora(n.geradaEm.hour * 60 + n.geradaEm.minute)}',
                                    style: Txt.pequeno.copyWith(
                                      fontSize: 11.5,
                                      color: Cores.dica,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            if (!n.lida)
                              Container(
                                margin: const EdgeInsets.only(top: 6),
                                width: 9,
                                height: 9,
                                decoration: const BoxDecoration(
                                  color: Cores.perigo,
                                  shape: BoxShape.circle,
                                ),
                              ),
                          ],
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
