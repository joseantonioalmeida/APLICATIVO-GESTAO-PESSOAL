import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../core/formatadores.dart';
import '../core/theme.dart';
import '../state/app_scope.dart';

// ---------------------------------------------------------------------------
// Campos de formulário
// ---------------------------------------------------------------------------

/// Rótulo acima de um campo.
class Rotulo extends StatelessWidget {
  const Rotulo(
    this.texto, {
    super.key,
    this.contador,
    this.obrigatorio = false,
  });
  final String texto;
  final String? contador;
  final bool obrigatorio;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(obrigatorio ? '$texto *' : texto, style: Txt.rotulo),
          ),
          if (contador != null) Text(contador!, style: Txt.rotulo),
        ],
      ),
    );
  }
}

/// Mensagem de erro/ajuda exibida logo abaixo de um campo.
class TextoAjuda extends StatelessWidget {
  const TextoAjuda(this.texto, {super.key, this.erro = false});
  final String texto;
  final bool erro;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Text(
        texto,
        style: Txt.pequeno.copyWith(
          color: erro ? Cores.perigo : Cores.textoSuave,
        ),
      ),
    );
  }
}

/// Caixa de campo (fundo, raio e borda de erro) reutilizada por todos os campos.
class CaixaCampo extends StatelessWidget {
  const CaixaCampo({
    super.key,
    required this.child,
    this.erro = false,
    this.onTap,
    this.altura = 52,
    this.padding = const EdgeInsets.symmetric(horizontal: 16),
    this.alturaLivre = false,
  });
  final Widget child;
  final bool erro;
  final VoidCallback? onTap;
  final double altura;
  final EdgeInsets padding;
  final bool alturaLivre;

  @override
  Widget build(BuildContext context) {
    final conteudo = Container(
      constraints: alturaLivre ? null : BoxConstraints(minHeight: altura),
      padding: padding,
      decoration: BoxDecoration(
        color: Cores.cartao,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: erro ? Cores.perigo : Colors.transparent,
          width: 1.2,
        ),
      ),
      alignment: alturaLivre ? null : Alignment.centerLeft,
      child: child,
    );
    if (onTap == null) return conteudo;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: conteudo,
    );
  }
}

class CampoTexto extends StatelessWidget {
  const CampoTexto({
    super.key,
    this.rotulo,
    this.dica,
    this.controller,
    this.icone,
    this.sufixo,
    this.obscuro = false,
    this.teclado,
    this.erro,
    this.onChanged,
    this.linhas = 1,
    this.maxCaracteres,
    this.formatadores,
    this.acao,
    this.onSubmitted,
    this.contador,
    this.obrigatorio = false,
    this.focusNode,
    this.autofillHints,
    this.capitalizacao = TextCapitalization.none,
    this.alturaCampo = 52,
  });

  final String? rotulo;
  final String? dica;
  final TextEditingController? controller;
  final IconData? icone;
  final Widget? sufixo;
  final bool obscuro;
  final TextInputType? teclado;
  final String? erro;
  final ValueChanged<String>? onChanged;
  final int linhas;
  final int? maxCaracteres;
  final List<TextInputFormatter>? formatadores;
  final TextInputAction? acao;
  final ValueChanged<String>? onSubmitted;
  final String? contador;
  final bool obrigatorio;
  final FocusNode? focusNode;
  final Iterable<String>? autofillHints;
  final TextCapitalization capitalizacao;
  final double alturaCampo;

  @override
  Widget build(BuildContext context) {
    final multilinha = linhas > 1;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (rotulo != null)
          Rotulo(rotulo!, contador: contador, obrigatorio: obrigatorio),
        CaixaCampo(
          erro: erro != null,
          altura: alturaCampo,
          alturaLivre: multilinha,
          padding: EdgeInsets.symmetric(
            horizontal: 16,
            vertical: multilinha ? 6 : 0,
          ),
          child: Row(
            crossAxisAlignment: multilinha
                ? CrossAxisAlignment.start
                : CrossAxisAlignment.center,
            children: [
              if (icone != null) ...[
                Padding(
                  padding: EdgeInsets.only(top: multilinha ? 12 : 0),
                  child: Icon(icone, size: 20, color: Cores.textoSuave),
                ),
                const SizedBox(width: 12),
              ],
              Expanded(
                child: TextField(
                  controller: controller,
                  focusNode: focusNode,
                  obscureText: obscuro,
                  keyboardType: multilinha ? TextInputType.multiline : teclado,
                  textInputAction: acao,
                  onChanged: onChanged,
                  onSubmitted: onSubmitted,
                  minLines: linhas,
                  maxLines: multilinha ? linhas + 2 : 1,
                  maxLength: maxCaracteres,
                  inputFormatters: formatadores,
                  autofillHints: autofillHints,
                  textCapitalization: capitalizacao,
                  style: Txt.corpo.copyWith(fontSize: 16),
                  cursorColor: Cores.primaria,
                  decoration: InputDecoration(
                    hintText: dica,
                    hintStyle: Txt.corpo.copyWith(
                      fontSize: 16,
                      color: Cores.dica,
                      fontWeight: FontWeight.w500,
                    ),
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    counterText: '',
                    isDense: true,
                    filled: false,
                    contentPadding: EdgeInsets.symmetric(
                      vertical: multilinha ? 10 : 14,
                    ),
                  ),
                ),
              ),
              ?sufixo,
            ],
          ),
        ),
        if (erro != null) TextoAjuda(erro!, erro: true),
      ],
    );
  }
}

class CampoSenha extends StatefulWidget {
  const CampoSenha({
    super.key,
    required this.rotulo,
    required this.dica,
    required this.controller,
    this.icone,
    this.erro,
    this.onChanged,
    this.acao,
    this.onSubmitted,
  });
  final String rotulo;
  final String dica;
  final TextEditingController controller;
  final IconData? icone;
  final String? erro;
  final ValueChanged<String>? onChanged;
  final TextInputAction? acao;
  final ValueChanged<String>? onSubmitted;

  @override
  State<CampoSenha> createState() => _CampoSenhaState();
}

class _CampoSenhaState extends State<CampoSenha> {
  bool _visivel = false;

  @override
  Widget build(BuildContext context) {
    return CampoTexto(
      rotulo: widget.rotulo,
      dica: widget.dica,
      controller: widget.controller,
      icone: widget.icone,
      obscuro: !_visivel,
      erro: widget.erro,
      onChanged: widget.onChanged,
      acao: widget.acao,
      onSubmitted: widget.onSubmitted,
      autofillHints: const [AutofillHints.password],
      sufixo: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => setState(() => _visivel = !_visivel),
        child: Padding(
          padding: const EdgeInsets.only(left: 12),
          child: Text(_visivel ? 'Ocultar' : 'Mostrar', style: Txt.link),
        ),
      ),
    );
  }
}

/// Campo de seleção única com lista em folha inferior.
class CampoSelecao<T> extends StatelessWidget {
  const CampoSelecao({
    super.key,
    this.rotulo,
    required this.valor,
    required this.opcoes,
    required this.rotuloDe,
    required this.aoEscolher,
    this.dica = 'Selecione',
    this.erro,
    this.obrigatorio = false,
    this.titulo,
    this.aoLimpar,
  });
  final String? rotulo;
  final T? valor;
  final List<T> opcoes;
  final String Function(T) rotuloDe;
  final ValueChanged<T> aoEscolher;
  final String dica;
  final String? erro;
  final bool obrigatorio;
  final String? titulo;
  final VoidCallback? aoLimpar;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (rotulo != null) Rotulo(rotulo!, obrigatorio: obrigatorio),
        CaixaCampo(
          erro: erro != null,
          onTap: () async {
            FocusScope.of(context).unfocus();
            final r = await escolherOpcao<T>(
              context,
              titulo: titulo ?? rotulo ?? dica,
              opcoes: opcoes,
              rotuloDe: rotuloDe,
              atual: valor,
            );
            if (r != null) aoEscolher(r);
          },
          child: Row(
            children: [
              Expanded(
                child: Text(
                  valor == null ? dica : rotuloDe(valor as T),
                  style: Txt.corpo.copyWith(
                    fontSize: 16,
                    fontWeight: valor == null
                        ? FontWeight.w700
                        : FontWeight.w600,
                    color: Cores.texto,
                  ),
                ),
              ),
              const Icon(
                Icons.keyboard_arrow_down,
                size: 20,
                color: Cores.textoSuave,
              ),
            ],
          ),
        ),
        if (erro != null) TextoAjuda(erro!, erro: true),
      ],
    );
  }
}

/// Folha inferior com opções; devolve a escolhida (ou null ao fechar).
Future<T?> escolherOpcao<T>(
  BuildContext context, {
  required String titulo,
  required List<T> opcoes,
  required String Function(T) rotuloDe,
  T? atual,
}) {
  return showModalBottomSheet<T>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Cores.cartao,
    builder: (ctx) {
      return SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.of(ctx).size.height * 0.7,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
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
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 18, 24, 8),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Text(titulo, style: Txt.secao),
                ),
              ),
              Flexible(
                child: ListView(
                  shrinkWrap: true,
                  children: [
                    for (final o in opcoes)
                      ListTile(
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 24,
                        ),
                        title: Text(
                          rotuloDe(o),
                          style: Txt.corpo.copyWith(
                            fontWeight: o == atual
                                ? FontWeight.w800
                                : FontWeight.w500,
                            color: o == atual ? Cores.primaria : Cores.texto,
                          ),
                        ),
                        trailing: o == atual
                            ? const Icon(Icons.check, color: Cores.primaria)
                            : null,
                        onTap: () => Navigator.pop(ctx, o),
                      ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
    },
  );
}

/// Máscara monetária: o usuário digita só números e o campo mostra
/// "1.621,00" (os dois últimos dígitos são os centavos). Aceita até
/// 15 dígitos (trilhões de reais) sem estourar o limite de inteiros.
class MascaraMoeda extends TextInputFormatter {
  static const maxDigitos = 15;

  static String formatar(String digitos) {
    var d = digitos.replaceFirst(RegExp(r'^0+'), '');
    if (d.isEmpty) return '';
    d = d.padLeft(3, '0');
    final inteiro = d.substring(0, d.length - 2);
    final centavos = d.substring(d.length - 2);
    final b = StringBuffer();
    for (var i = 0; i < inteiro.length; i++) {
      if (i > 0 && (inteiro.length - i) % 3 == 0) b.write('.');
      b.write(inteiro[i]);
    }
    return '$b,$centavos';
  }

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue antigo,
    TextEditingValue novo,
  ) {
    var d = novo.text.replaceAll(RegExp(r'\D'), '');
    if (d.length > maxDigitos) d = d.substring(0, maxDigitos);
    final t = formatar(d);
    return TextEditingValue(
      text: t,
      selection: TextSelection.collapsed(offset: t.length),
    );
  }
}

/// Máscara DD/MM/AAAA.
class MascaraData extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue antigo,
    TextEditingValue novo,
  ) {
    final d = novo.text.replaceAll(RegExp(r'\D'), '');
    final b = StringBuffer();
    for (var i = 0; i < d.length && i < 8; i++) {
      if (i == 2 || i == 4) b.write('/');
      b.write(d[i]);
    }
    final t = b.toString();
    return TextEditingValue(
      text: t,
      selection: TextSelection.collapsed(offset: t.length),
    );
  }
}

/// Campo de data em DD/MM/AAAA, com digitação ou calendário.
class CampoData extends StatelessWidget {
  const CampoData({
    super.key,
    this.rotulo,
    required this.controller,
    this.erro,
    this.onChanged,
    this.primeira,
    this.ultima,
    this.dica = 'DD/MM/AAAA',
    this.obrigatorio = false,
    this.comIcone = true,
    this.somenteLeitura = false,
  });
  final String? rotulo;
  final TextEditingController controller;
  final String? erro;
  final ValueChanged<DateTime?>? onChanged;
  final DateTime? primeira;
  final DateTime? ultima;
  final String dica;
  final bool obrigatorio;
  final bool comIcone;
  final bool somenteLeitura;

  Future<void> _abrir(BuildContext context) async {
    FocusScope.of(context).unfocus();
    final atual = Conv.data(controller.text) ?? DateTime.now();
    final r = await showDatePicker(
      context: context,
      initialDate: atual,
      firstDate: primeira ?? DateTime(2000),
      lastDate: ultima ?? DateTime(2100),
      locale: const Locale('pt', 'BR'),
      helpText: rotulo,
    );
    if (r != null) {
      controller.text = Fmt.data(r);
      onChanged?.call(r);
    }
  }

  @override
  Widget build(BuildContext context) {
    return CampoTexto(
      rotulo: rotulo,
      dica: dica,
      controller: controller,
      erro: erro,
      obrigatorio: obrigatorio,
      teclado: TextInputType.number,
      formatadores: [MascaraData()],
      onChanged: (t) => onChanged?.call(Conv.data(t)),
      sufixo: comIcone
          ? GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () => _abrir(context),
              child: const Padding(
                padding: EdgeInsets.only(left: 12),
                child: Icon(
                  Icons.calendar_today_outlined,
                  size: 18,
                  color: Cores.textoSuave,
                ),
              ),
            )
          : null,
    );
  }
}

/// Campo de horário (HH:MM) que abre o seletor de hora ao tocar.
class CampoHora extends StatelessWidget {
  const CampoHora({
    super.key,
    this.rotulo,
    required this.valor,
    required this.aoEscolher,
    this.erro,
    this.dica = '--:--',
    this.obrigatorio = false,
    this.aoLimpar,
  });
  final String? rotulo;
  final int? valor;
  final ValueChanged<int> aoEscolher;
  final String? erro;
  final String dica;
  final bool obrigatorio;
  final VoidCallback? aoLimpar;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (rotulo != null) Rotulo(rotulo!, obrigatorio: obrigatorio),
        CaixaCampo(
          erro: erro != null,
          onTap: () async {
            FocusScope.of(context).unfocus();
            final inicial = valor ?? 8 * 60;
            final r = await showTimePicker(
              context: context,
              initialTime: TimeOfDay(hour: inicial ~/ 60, minute: inicial % 60),
              builder: (ctx, child) => MediaQuery(
                data: MediaQuery.of(ctx).copyWith(alwaysUse24HourFormat: true),
                child: child!,
              ),
            );
            if (r != null) aoEscolher(r.hour * 60 + r.minute);
          },
          child: Row(
            children: [
              Expanded(
                child: Text(
                  valor == null ? dica : Fmt.hora(valor!),
                  style: Txt.corpo.copyWith(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: valor == null ? Cores.dica : Cores.texto,
                  ),
                ),
              ),
              if (valor != null && aoLimpar != null)
                GestureDetector(
                  onTap: aoLimpar,
                  child: const Icon(Icons.close, size: 18, color: Cores.dica),
                ),
            ],
          ),
        ),
        if (erro != null) TextoAjuda(erro!, erro: true),
      ],
    );
  }
}

/// Campo de valor em reais ("R$ 0,00"), com cor opcional para o valor digitado.
class CampoValor extends StatelessWidget {
  const CampoValor({
    super.key,
    this.rotulo,
    required this.controller,
    this.erro,
    this.onChanged,
    this.destaque = false,
    this.corValor,
    this.obrigatorio = false,
  });
  final String? rotulo;
  final TextEditingController controller;
  final String? erro;
  final ValueChanged<String>? onChanged;
  final bool destaque;
  final Color? corValor;
  final bool obrigatorio;

  @override
  Widget build(BuildContext context) {
    final tam = destaque ? 24.0 : 16.0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (rotulo != null) Rotulo(rotulo!, obrigatorio: obrigatorio),
        CaixaCampo(
          erro: erro != null,
          altura: destaque ? 62 : 52,
          child: Row(
            children: [
              Text(
                'R\$',
                style: Txt.corpo.copyWith(
                  fontSize: destaque ? 20 : 16,
                  fontWeight: FontWeight.w700,
                  color: destaque ? Cores.dica : Cores.textoSuave,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextField(
                  controller: controller,
                  onChanged: onChanged,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  inputFormatters: [MascaraMoeda()],
                  cursorColor: Cores.primaria,
                  style: Txt.corpo.copyWith(
                    fontSize: tam,
                    fontWeight: destaque ? FontWeight.w800 : FontWeight.w700,
                    color: corValor ?? Cores.texto,
                  ),
                  decoration: InputDecoration(
                    hintText: '0,00',
                    hintStyle: Txt.corpo.copyWith(
                      fontSize: tam,
                      fontWeight: destaque ? FontWeight.w800 : FontWeight.w700,
                      color: Cores.dica,
                    ),
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    isDense: true,
                    filled: false,
                    contentPadding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ),
        ),
        if (erro != null) TextoAjuda(erro!, erro: true),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Botões e links
// ---------------------------------------------------------------------------

class BotaoPrimario extends StatelessWidget {
  const BotaoPrimario({
    super.key,
    required this.texto,
    required this.onPressed,
    this.carregando = false,
    this.altura = 54,
  });
  final String texto;
  final VoidCallback? onPressed;
  final bool carregando;
  final double altura;

  @override
  Widget build(BuildContext context) {
    final ativo = onPressed != null && !carregando;
    return SizedBox(
      width: double.infinity,
      height: altura,
      child: Material(
        color: ativo ? Cores.primaria : Cores.primaria.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: ativo ? onPressed : null,
          child: Center(
            child: carregando
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.4,
                      color: Cores.sobrePrimaria,
                    ),
                  )
                : Text(
                    texto,
                    style: const TextStyle(
                      fontFamily: AppTema.fonte,
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                      color: Cores.sobrePrimaria,
                    ),
                  ),
          ),
        ),
      ),
    );
  }
}

/// "Texto comum  Link" centralizado no rodapé das telas de autenticação.
class RodapeLink extends StatelessWidget {
  const RodapeLink({
    super.key,
    required this.texto,
    required this.link,
    required this.onTap,
  });
  final String texto;
  final String link;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Wrap(
        crossAxisAlignment: WrapCrossAlignment.center,
        alignment: WrapAlignment.center,
        children: [
          Text(
            '$texto ',
            style: Txt.corpo.copyWith(
              color: Cores.textoSuave,
              fontWeight: FontWeight.w400,
              fontSize: 15,
            ),
          ),
          GestureDetector(
            onTap: onTap,
            child: Text(
              link,
              style: Txt.link.copyWith(
                fontSize: 15,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class BotaoVoltar extends StatelessWidget {
  const BotaoVoltar({super.key, this.onTap});
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap ?? () => Navigator.maybePop(context),
      child: const SizedBox(
        width: 40,
        height: 40,
        child: Align(
          alignment: Alignment.centerLeft,
          child: Icon(Icons.chevron_left, size: 28, color: Cores.texto),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Cartões, selos e estados
// ---------------------------------------------------------------------------

class Cartao extends StatelessWidget {
  const Cartao({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
    this.cor,
    this.raio = 20,
    this.borda,
  });
  final Widget child;
  final EdgeInsets padding;
  final VoidCallback? onTap;
  final Color? cor;
  final double raio;
  final Color? borda;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: cor ?? Cores.cartao,
      borderRadius: BorderRadius.circular(raio),
      child: InkWell(
        borderRadius: BorderRadius.circular(raio),
        onTap: onTap,
        child: Container(
          padding: padding,
          decoration: borda == null
              ? null
              : BoxDecoration(
                  borderRadius: BorderRadius.circular(raio),
                  border: Border.all(color: borda!),
                ),
          child: child,
        ),
      ),
    );
  }
}

class IconeQuadrado extends StatelessWidget {
  const IconeQuadrado(
    this.icone, {
    super.key,
    this.cor = Cores.textoSuave,
    this.tamanho = 40,
  });
  final IconData icone;
  final Color cor;
  final double tamanho;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: tamanho,
      height: tamanho,
      decoration: BoxDecoration(
        color: Cores.fundo.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(icone, size: tamanho * 0.45, color: cor),
    );
  }
}

class EstadoCarregando extends StatelessWidget {
  const EstadoCarregando({super.key, this.altura = 120});
  final double altura;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: altura,
      child: const Center(
        child: SizedBox(
          width: 26,
          height: 26,
          child: CircularProgressIndicator(
            strokeWidth: 2.6,
            color: Cores.primaria,
          ),
        ),
      ),
    );
  }
}

class EstadoErro extends StatelessWidget {
  const EstadoErro({super.key, required this.mensagem, required this.onTentar});
  final String mensagem;
  final VoidCallback onTentar;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 8),
      child: Column(
        children: [
          const Icon(Icons.error_outline, color: Cores.perigo, size: 28),
          const SizedBox(height: 8),
          Text(
            mensagem,
            textAlign: TextAlign.center,
            style: Txt.corpo.copyWith(color: Cores.textoSuave),
          ),
          const SizedBox(height: 10),
          TextButton(
            onPressed: onTentar,
            child: Text('Tentar novamente', style: Txt.link),
          ),
        ],
      ),
    );
  }
}

class EstadoVazio extends StatelessWidget {
  const EstadoVazio({
    super.key,
    required this.mensagem,
    this.acao,
    this.onAcao,
    this.icone = Icons.inbox_outlined,
  });
  final String mensagem;
  final String? acao;
  final VoidCallback? onAcao;
  final IconData icone;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 12),
      child: Column(
        children: [
          Icon(icone, color: Cores.dica, size: 30),
          const SizedBox(height: 10),
          Text(
            mensagem,
            textAlign: TextAlign.center,
            style: Txt.corpo.copyWith(color: Cores.textoSuave),
          ),
          if (acao != null) ...[
            const SizedBox(height: 8),
            TextButton(
              onPressed: onAcao,
              child: Text(acao!, style: Txt.link),
            ),
          ],
        ],
      ),
    );
  }
}

/// Carrega dados de forma assíncrona com carregamento, erro e nova tentativa.
/// Recarrega automaticamente quando os dados do aplicativo mudam.
class BlocoAsync<T> extends StatefulWidget {
  const BlocoAsync({
    super.key,
    required this.carregar,
    required this.construir,
    this.mensagemErro = 'Não foi possível carregar. Tente novamente',
    this.alturaCarregando = 100,
    this.chave,
  });
  final Future<T> Function() carregar;
  final Widget Function(BuildContext, T) construir;
  final String mensagemErro;
  final double alturaCarregando;

  /// Mudar este valor força um novo carregamento.
  final Object? chave;

  @override
  State<BlocoAsync<T>> createState() => _BlocoAsyncState<T>();
}

class _BlocoAsyncState<T> extends State<BlocoAsync<T>> {
  T? _dados;
  bool _temDados = false;
  Object? _erro;
  int _geracao = 0;
  BarramentoDados? _barramento;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final b = AppScope.of(context).dados;
    if (_barramento != b) {
      _barramento?.removeListener(_recarregar);
      _barramento = b..addListener(_recarregar);
      _recarregar();
    }
  }

  @override
  void didUpdateWidget(BlocoAsync<T> old) {
    super.didUpdateWidget(old);
    if (old.chave != widget.chave) _recarregar();
  }

  @override
  void dispose() {
    _barramento?.removeListener(_recarregar);
    super.dispose();
  }

  Future<void> _recarregar() async {
    final g = ++_geracao;
    if (mounted) {
      setState(() {
        _erro = null;
      });
    }
    try {
      final r = await widget.carregar();
      if (!mounted || g != _geracao) return;
      setState(() {
        _dados = r;
        _temDados = true;
      });
    } catch (e) {
      if (!mounted || g != _geracao) return;
      setState(() {
        _erro = e;
        _temDados = false;
        _dados = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_erro != null) {
      return EstadoErro(mensagem: widget.mensagemErro, onTentar: _recarregar);
    }
    if (!_temDados) return EstadoCarregando(altura: widget.alturaCarregando);
    return widget.construir(context, _dados as T);
  }
}

// ---------------------------------------------------------------------------
// Diálogos e mensagens
// ---------------------------------------------------------------------------

void mostrarMensagem(BuildContext context, String texto, {bool erro = false}) {
  final m = ScaffoldMessenger.of(context);
  m.hideCurrentSnackBar();
  m.showSnackBar(
    SnackBar(
      content: Row(
        children: [
          Icon(
            erro ? Icons.error_outline : Icons.check_circle_outline,
            color: erro ? Cores.perigo : Cores.sucesso,
            size: 20,
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(texto)),
        ],
      ),
      duration: const Duration(seconds: 3),
    ),
  );
}

/// Diálogo de confirmação. Devolve true se o usuário confirmou.
Future<bool> confirmar(
  BuildContext context, {
  required String titulo,
  String? mensagem,
  required String confirmarTexto,
  String cancelarTexto = 'Cancelar',
  bool perigo = false,
}) async {
  final r = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(titulo),
      content: mensagem == null ? null : Text(mensagem),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(ctx, false),
          child: Text(
            cancelarTexto,
            style: Txt.corpoNegrito.copyWith(color: Cores.textoSuave),
          ),
        ),
        TextButton(
          onPressed: () => Navigator.pop(ctx, true),
          child: Text(
            confirmarTexto,
            style: Txt.corpoNegrito.copyWith(
              color: perigo ? Cores.perigo : Cores.primaria,
            ),
          ),
        ),
      ],
    ),
  );
  return r ?? false;
}

/// "Deseja sair sem salvar...?" com Continuar preenchendo / Descartar alterações.
Future<bool> confirmarDescarte(BuildContext context, String titulo) {
  return confirmar(
    context,
    titulo: titulo,
    confirmarTexto: 'Descartar alterações',
    cancelarTexto: 'Continuar preenchendo',
    perigo: true,
  );
}

/// Envolve um formulário e pergunta antes de sair quando há alterações.
class ProtecaoSaida extends StatefulWidget {
  const ProtecaoSaida({
    super.key,
    required this.alterado,
    required this.pergunta,
    required this.child,
    this.bloqueado = false,
  });
  final bool Function() alterado;
  final String pergunta;
  final Widget child;
  final bool bloqueado;

  @override
  State<ProtecaoSaida> createState() => ProtecaoSaidaState();

  static ProtecaoSaidaState? de(BuildContext context) =>
      context.findAncestorStateOfType<ProtecaoSaidaState>();
}

class ProtecaoSaidaState extends State<ProtecaoSaida> {
  bool _liberado = false;

  /// Sai da tela depois de salvar, sem perguntar.
  void liberar() => _liberado = true;

  /// Tenta sair (botão Cancelar/voltar): pergunta se houver alterações.
  Future<void> tentarSair() async {
    if (widget.bloqueado) return;
    if (!widget.alterado() || _liberado) {
      Navigator.of(context).pop();
      return;
    }
    final descartar = await confirmarDescarte(context, widget.pergunta);
    if (descartar && mounted) {
      _liberado = true;
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) tentarSair();
      },
      child: widget.child,
    );
  }
}

// ---------------------------------------------------------------------------
// Navegação inferior
// ---------------------------------------------------------------------------

class BarraNavegacao extends StatelessWidget {
  const BarraNavegacao({super.key, required this.atual, required this.onTap});
  final Aba atual;
  final ValueChanged<Aba> onTap;

  static const _itens = [
    (Aba.inicio, 'Início', Icons.home_outlined, Icons.home_rounded),
    (
      Aba.atividades,
      'Atividades',
      Icons.format_list_bulleted,
      Icons.format_list_bulleted,
    ),
    (
      Aba.financeiro,
      'Financeiro',
      Icons.account_balance_wallet_outlined,
      Icons.account_balance_wallet,
    ),
    (
      Aba.importancias,
      'Importâncias',
      Icons.calendar_today_outlined,
      Icons.calendar_today,
    ),
    (Aba.perfil, 'Perfil', Icons.person_outline, Icons.person),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Cores.fundo,
        border: Border(top: BorderSide(color: Cores.borda)),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 60,
          child: Row(
            children: [
              for (final (aba, nome, icone, iconeSel) in _itens)
                Expanded(
                  child: InkWell(
                    onTap: () => onTap(aba),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          aba == atual ? iconeSel : icone,
                          size: 22,
                          color: aba == atual
                              ? Cores.primaria
                              : Cores.textoSuave,
                        ),
                        const SizedBox(height: 3),
                        Text(
                          nome,
                          style: TextStyle(
                            fontFamily: AppTema.fonte,
                            fontSize: 11,
                            fontWeight: aba == atual
                                ? FontWeight.w700
                                : FontWeight.w500,
                            color: aba == atual
                                ? Cores.primaria
                                : Cores.textoSuave,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Selo textual (ex.: "Pendente", "Concluída", "Hoje").
class TextoSituacao extends StatelessWidget {
  const TextoSituacao(this.texto, this.cor, {super.key, this.tamanho = 13});
  final String texto;
  final Color cor;
  final double tamanho;

  @override
  Widget build(BuildContext context) => Text(
    texto,
    style: TextStyle(
      fontFamily: AppTema.fonte,
      fontSize: tamanho,
      fontWeight: FontWeight.w700,
      color: cor,
    ),
  );
}
