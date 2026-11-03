import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../core/theme.dart';
import '../../core/validadores.dart';
import '../../models/modelos.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import 'auth_base.dart';

void _avisoCodigo(BuildContext context, String? codigo) {
  // Sem envio real de e-mail (modo demonstração), o código é exibido na tela.
  if (codigo != null) {
    mostrarMensagem(context, 'Modo demonstração - código enviado: $codigo');
  }
}

/// Tela 3.1 - Esqueceu a senha (informar e-mail).
class EsqueceuSenhaScreen extends StatefulWidget {
  const EsqueceuSenhaScreen({super.key});

  @override
  State<EsqueceuSenhaScreen> createState() => _EsqueceuSenhaScreenState();
}

class _EsqueceuSenhaScreenState extends State<EsqueceuSenhaScreen> {
  final _email = TextEditingController();
  String? _erro;
  bool _enviando = false;

  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (_enviando) return;
    final email = _email.text.trim();
    if (email.isEmpty) {
      setState(() => _erro = 'Informe seu e-mail');
      return;
    }
    if (!Valida.emailValido(email)) {
      setState(() => _erro = 'Informe um e-mail válido');
      return;
    }
    final escopo = AppScope.of(context);
    setState(() => _enviando = true);
    try {
      final codigo = await escopo.repositorio.solicitarCodigo(email);
      if (!mounted) return;
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => CodigoScreen(email: email, codigoDemo: codigo),
        ),
      );
    } on ErroApp catch (e) {
      if (mounted) setState(() => _erro = e.mensagem);
    } catch (_) {
      if (mounted) {
        setState(
          () => _erro = 'Não foi possível enviar o código. Tente novamente',
        );
      }
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AuthScaffold(
      voltar: true,
      passo: 1,
      rodape: RodapeLink(
        texto: 'Lembrou a senha?',
        link: 'Voltar ao login',
        onTap: () => Navigator.popUntil(context, (r) => r.isFirst),
      ),
      children: [
        const Text('Esqueceu a senha?', style: Txt.titulo),
        const SizedBox(height: 10),
        Text(
          'Informe o e-mail da sua conta e enviaremos um código de 8 dígitos para redefinir a senha.',
          style: Txt.subtitulo.copyWith(fontSize: 17),
        ),
        const SizedBox(height: 22),
        CampoTexto(
          rotulo: 'E-mail',
          dica: 'voce@email.com',
          controller: _email,
          icone: Icons.mail_outline,
          teclado: TextInputType.emailAddress,
          acao: TextInputAction.done,
          erro: _erro,
          onSubmitted: (_) => _enviar(),
          onChanged: (_) => setState(() => _erro = null),
        ),
        if (_erro == null)
          const TextoAjuda('O código chega no e-mail cadastrado na sua conta.'),
        const SizedBox(height: 18),
        BotaoPrimario(
          texto: 'Enviar',
          carregando: _enviando,
          onPressed: _enviar,
        ),
      ],
    );
  }
}

/// Tela 3.2 - Digite o código de 8 dígitos.
class CodigoScreen extends StatefulWidget {
  const CodigoScreen({super.key, required this.email, this.codigoDemo});
  final String email;
  final String? codigoDemo;

  @override
  State<CodigoScreen> createState() => _CodigoScreenState();
}

class _CodigoScreenState extends State<CodigoScreen> {
  static const _digitos = 8;
  final _controller = TextEditingController();
  final _foco = FocusNode();
  String? _erro;
  bool _enviando = false;

  @override
  void initState() {
    super.initState();
    _foco.addListener(() {
      if (mounted) setState(() {});
    });
    if (widget.codigoDemo != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _avisoCodigo(context, widget.codigoDemo);
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _foco.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (_enviando) return;
    if (_controller.text.length != _digitos) {
      setState(() => _erro = 'Digite os 8 dígitos do código');
      return;
    }
    final escopo = AppScope.of(context);
    setState(() => _enviando = true);
    try {
      final token = await escopo.repositorio.verificarCodigo(
        widget.email,
        _controller.text,
      );
      if (!mounted) return;
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => NovaSenhaScreen(email: widget.email, token: token),
        ),
      );
    } on ErroApp catch (e) {
      if (mounted) setState(() => _erro = e.mensagem);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _reenviar() async {
    try {
      final codigo = await AppScope.of(context).repositorio
          .solicitarCodigo(widget.email);
      if (!mounted) return;
      _controller.clear();
      setState(() => _erro = null);
      mostrarMensagem(
        context,
        'Enviamos um novo código. O anterior não vale mais.',
      );
      _avisoCodigoDepois(codigo);
    } on ErroApp catch (e) {
      if (mounted) mostrarMensagem(context, e.mensagem, erro: true);
    }
  }

  void _avisoCodigoDepois(String? codigo) {
    if (codigo == null) return;
    Future.delayed(const Duration(milliseconds: 600), () {
      if (mounted) _avisoCodigo(context, codigo);
    });
  }

  @override
  Widget build(BuildContext context) {
    final texto = _controller.text;
    return AuthScaffold(
      voltar: true,
      passo: 2,
      rodape: RodapeLink(
        texto: 'Não recebeu o código?',
        link: 'Reenviar código',
        onTap: _reenviar,
      ),
      children: [
        const Text('Digite o código', style: Txt.titulo),
        const SizedBox(height: 10),
        RichText(
          text: TextSpan(
            style: Txt.subtitulo.copyWith(fontSize: 17),
            children: [
              const TextSpan(text: 'Enviamos um código de 8 dígitos para '),
              TextSpan(
                text: widget.email,
                style: const TextStyle(
                  color: Cores.texto,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const TextSpan(text: '.'),
            ],
          ),
        ),
        const SizedBox(height: 22),
        const Rotulo('Código de verificação'),
        GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () => _foco.requestFocus(),
          child: Stack(
            children: [
              Row(
                children: [
                  for (var i = 0; i < _digitos; i++) ...[
                    Expanded(
                      child: Container(
                        height: 56,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: Cores.cartao,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _erro != null
                                ? Cores.perigo
                                : (i == texto.length && _foco.hasFocus
                                      ? Cores.primaria
                                      : Colors.transparent),
                            width: 1.4,
                          ),
                        ),
                        child: Text(
                          i < texto.length ? texto[i] : '',
                          style: Txt.titulo.copyWith(fontSize: 22),
                        ),
                      ),
                    ),
                    if (i < _digitos - 1) const SizedBox(width: 6),
                  ],
                ],
              ),
              // Campo real, invisível, que recebe a digitação.
              Positioned.fill(
                child: Opacity(
                  opacity: 0,
                  child: TextField(
                    controller: _controller,
                    focusNode: _foco,
                    keyboardType: TextInputType.number,
                    autofocus: true,
                    maxLength: _digitos,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    onChanged: (_) => setState(() => _erro = null),
                    onSubmitted: (_) => _enviar(),
                    decoration: const InputDecoration(counterText: ''),
                  ),
                ),
              ),
            ],
          ),
        ),
        if (_erro != null)
          TextoAjuda(_erro!, erro: true)
        else
          const TextoAjuda('O código vale por 10 minutos.'),
        const SizedBox(height: 18),
        BotaoPrimario(
          texto: 'Enviar',
          carregando: _enviando,
          onPressed: _enviar,
        ),
      ],
    );
  }
}

/// Tela 3.3 - Crie uma nova senha.
class NovaSenhaScreen extends StatefulWidget {
  const NovaSenhaScreen({super.key, required this.email, required this.token});
  final String email;
  final String token;

  @override
  State<NovaSenhaScreen> createState() => _NovaSenhaScreenState();
}

class _NovaSenhaScreenState extends State<NovaSenhaScreen> {
  final _senha = TextEditingController();
  final _confirmar = TextEditingController();
  String? _erroSenha;
  String? _erroConfirmar;
  bool _enviando = false;

  @override
  void dispose() {
    _senha.dispose();
    _confirmar.dispose();
    super.dispose();
  }

  Future<void> _redefinir() async {
    if (_enviando) return;
    setState(() {
      _erroSenha = _senha.text.length < 8 ? Valida.mensagemSenhaCurta : null;
      _erroConfirmar = _confirmar.text != _senha.text
          ? 'As senhas devem ser idênticas'
          : null;
    });
    if (_erroSenha != null || _erroConfirmar != null) return;
    final escopo = AppScope.of(context);
    final navegador = Navigator.of(context);
    final mensageiro = ScaffoldMessenger.of(context);
    setState(() => _enviando = true);
    try {
      await escopo.repositorio.redefinirSenha(
        email: widget.email,
        token: widget.token,
        novaSenha: _senha.text,
      );
      navegador.popUntil((r) => r.isFirst);
      mensageiro.showSnackBar(
        const SnackBar(
          content: Text('Redefinição de senha concluída com sucesso'),
        ),
      );
    } on ErroApp catch (e) {
      if (mounted) setState(() => _erroSenha = e.mensagem);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AuthScaffold(
      voltar: true,
      passo: 3,
      rodape: const SizedBox(height: 0),
      children: [
        const Text('Crie uma nova senha', style: Txt.titulo),
        const SizedBox(height: 10),
        Text(
          'Código confirmado. Agora escolha a nova senha da sua conta.',
          style: Txt.subtitulo.copyWith(fontSize: 17),
        ),
        const SizedBox(height: 22),
        CampoSenha(
          rotulo: 'Nova senha',
          dica: 'Nova senha',
          controller: _senha,
          acao: TextInputAction.next,
          erro: _erroSenha,
          onChanged: (_) => setState(() => _erroSenha = null),
        ),
        const SizedBox(height: 14),
        CampoSenha(
          rotulo: 'Confirmar a nova senha',
          dica: 'Repita a nova senha',
          controller: _confirmar,
          acao: TextInputAction.done,
          erro: _erroConfirmar,
          onSubmitted: (_) => _redefinir(),
          onChanged: (_) => setState(() => _erroConfirmar = null),
        ),
        const SizedBox(height: 14),
        Text(
          'A senha deve ter pelo menos 8 caracteres. Para torná-la mais forte, '
          'use letras maiúsculas e minúsculas, números e símbolos como ! @ # \$ % & * =',
          style: Txt.pequeno.copyWith(fontSize: 13, height: 1.45),
        ),
        const SizedBox(height: 18),
        BotaoPrimario(
          texto: 'Redefinir senha',
          carregando: _enviando,
          onPressed: _redefinir,
        ),
      ],
    );
  }
}
