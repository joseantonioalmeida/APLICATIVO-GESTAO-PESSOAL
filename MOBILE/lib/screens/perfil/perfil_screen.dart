import 'package:flutter/material.dart';

import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';

/// Área de Perfil (destino do avatar e da navegação inferior).
class PerfilScreen extends StatelessWidget {
  const PerfilScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final escopo = AppScope.of(context);
    final u = escopo.repositorio.usuario;
    return SafeArea(
      bottom: false,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
        children: [
          const Text('Perfil', style: Txt.tituloTela),
          const SizedBox(height: 20),
          Center(
            child: Container(
              width: 84,
              height: 84,
              alignment: Alignment.center,
              decoration: const BoxDecoration(
                color: Cores.selecionado,
                shape: BoxShape.circle,
              ),
              child: Text(
                u?.iniciais ?? '',
                style: Txt.titulo.copyWith(fontSize: 30, color: Cores.primaria),
              ),
            ),
          ),
          const SizedBox(height: 14),
          Center(child: Text(u?.nome ?? '', style: Txt.tituloForm)),
          const SizedBox(height: 2),
          Center(
            child: Text(
              u?.email ?? '',
              style: Txt.rotulo.copyWith(fontSize: 14),
            ),
          ),
          const SizedBox(height: 24),
          Cartao(
            raio: 20,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 6),
            child: Column(
              children: [
                _Linha('Nome completo', u?.nome ?? '-'),
                const Divider(height: 1, color: Cores.borda),
                _Linha('E-mail', u?.email ?? '-'),
                const Divider(height: 1, color: Cores.borda),
                _Linha(
                  'Data de nascimento',
                  u == null ? '-' : Fmt.data(u.nascimento),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            height: 50,
            child: OutlinedButton.icon(
              onPressed: () async {
                final sair = await confirmar(
                  context,
                  titulo: 'Deseja sair da sua conta?',
                  confirmarTexto: 'Sair',
                  perigo: true,
                );
                if (sair) {
                  escopo.repositorio.sair();
                  escopo.aoSair();
                }
              },
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Cores.perigo.withValues(alpha: 0.6)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              icon: const Icon(Icons.logout, size: 18, color: Cores.perigo),
              label: Text(
                'Sair',
                style: Txt.corpoNegrito.copyWith(
                  color: Cores.perigo,
                  fontSize: 15,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Linha extends StatelessWidget {
  const _Linha(this.rotulo, this.valor);
  final String rotulo;
  final String valor;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 14),
    child: Row(
      children: [
        Expanded(child: Text(rotulo, style: Txt.rotulo.copyWith(fontSize: 14))),
        Flexible(
          child: Text(
            valor,
            textAlign: TextAlign.right,
            overflow: TextOverflow.ellipsis,
            style: Txt.corpo.copyWith(
              fontWeight: FontWeight.w600,
              fontSize: 14.5,
            ),
          ),
        ),
      ],
    ),
  );
}
