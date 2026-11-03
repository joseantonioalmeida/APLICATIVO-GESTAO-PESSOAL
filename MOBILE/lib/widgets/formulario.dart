import 'package:flutter/material.dart';

import '../core/theme.dart';
import 'comuns.dart';

/// Estrutura das telas de cadastro: título com voltar, formulário rolável e
/// botões "Salvar" e "Cancelar" fixos na base.
class FormularioScaffold extends StatelessWidget {
  const FormularioScaffold({
    super.key,
    required this.titulo,
    required this.children,
    required this.textoSalvar,
    required this.onSalvar,
    this.salvando = false,
    this.subtitulo,
    this.erroGeral,
    this.cabecalho,
  });
  final String titulo;
  final String? subtitulo;
  final List<Widget> children;
  final String textoSalvar;
  final VoidCallback onSalvar;
  final bool salvando;
  final String? erroGeral;
  final Widget? cabecalho;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
              child: Row(
                children: [
                  BotaoVoltar(
                    onTap: () =>
                        ProtecaoSaida.de(context)?.tentarSair() ??
                        Navigator.maybePop(context),
                  ),
                  const SizedBox(width: 4),
                  Expanded(child: Text(titulo, style: Txt.tituloForm)),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                keyboardDismissBehavior:
                    ScrollViewKeyboardDismissBehavior.onDrag,
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (subtitulo != null) ...[
                      Text(
                        subtitulo!,
                        style: Txt.rotulo.copyWith(fontSize: 14),
                      ),
                      const SizedBox(height: 14),
                    ],
                    if (cabecalho != null) ...[
                      cabecalho!,
                      const SizedBox(height: 14),
                    ],
                    ...children,
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 10),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (erroGeral != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        erroGeral!,
                        textAlign: TextAlign.center,
                        style: Txt.pequeno.copyWith(
                          color: Cores.perigo,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  BotaoPrimario(
                    texto: salvando ? 'Salvando...' : textoSalvar,
                    onPressed: onSalvar,
                    carregando: salvando,
                    altura: 48,
                  ),
                  TextButton(
                    onPressed: salvando
                        ? null
                        : () =>
                              ProtecaoSaida.de(context)?.tentarSair() ??
                              Navigator.maybePop(context),
                    child: Text(
                      'Cancelar',
                      style: Txt.corpo.copyWith(
                        color: Cores.textoSuave,
                        fontWeight: FontWeight.w500,
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

/// "Término da repetição": Sem data final / Até uma data.
class TerminoRepeticao extends StatelessWidget {
  const TerminoRepeticao({
    super.key,
    required this.ateData,
    required this.controller,
    required this.aoMudar,
    required this.aoDigitar,
    this.erro,
  });
  final bool ateData;
  final TextEditingController controller;
  final ValueChanged<bool> aoMudar;
  final VoidCallback aoDigitar;
  final String? erro;

  @override
  Widget build(BuildContext context) {
    Widget opcao(String texto, bool valor) => Expanded(
      child: GestureDetector(
        onTap: () => aoMudar(valor),
        child: Container(
          height: 44,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: ateData == valor ? Cores.selecionado : Cores.cartao,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: ateData == valor ? Cores.primaria : Colors.transparent,
              width: 1.2,
            ),
          ),
          child: Text(texto, style: Txt.corpoNegrito.copyWith(fontSize: 14)),
        ),
      ),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Rotulo('Término da repetição'),
        Row(
          children: [
            opcao('Sem data final', false),
            const SizedBox(width: 8),
            opcao('Até uma data', true),
          ],
        ),
        if (ateData) ...[
          const SizedBox(height: 12),
          CampoData(
            rotulo: 'Data final',
            obrigatorio: true,
            controller: controller,
            erro: erro,
            onChanged: (_) => aoDigitar(),
          ),
        ],
      ],
    );
  }
}
