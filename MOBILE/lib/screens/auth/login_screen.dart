import 'package:flutter/material.dart';

import '../../core/theme.dart';
import '../../core/validadores.dart';
import '../../models/modelos.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import 'auth_base.dart';
import 'recuperacao_screens.dart';
import 'registro_screen.dart';

/// Tela 1 - Login.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, this.mensagemInicial});
  final String? mensagemInicial;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _senha = TextEditingController();
  String? _erroEmail;
  String? _erroSenha;
  String? _erroGeral;
  bool _enviando = false;

  @override
  void dispose() {
    _email.dispose();
    _senha.dispose();
    super.dispose();
  }

  Future<void> _entrar() async {
    if (_enviando) return;
    setState(() {
      _erroGeral = null;
      _erroEmail = _email.text.trim().isEmpty
          ? 'Informe seu e-mail'
          : (!Valida.emailValido(_email.text)
                ? 'Informe um e-mail válido'
                : null);
      _erroSenha = _senha.text.isEmpty ? 'Informe sua senha' : null;
    });
    if (_erroEmail != null || _erroSenha != null) return;

    final escopo = AppScope.of(context);
    setState(() => _enviando = true);
    try {
      await escopo.repositorio.entrar(_email.text, _senha.text);
      if (!mounted) return;
      escopo.aoEntrar();
    } on ErroApp catch (e) {
      if (mounted) setState(() => _erroGeral = e.mensagem);
    } catch (_) {
      if (mounted) {
        setState(() => _erroGeral = 'Não foi possível entrar. Tente novamente');
      }
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AuthScaffold(
      topo: 76,
      rodape: RodapeLink(
        texto: 'Não tem uma conta?',
        link: 'Registrar-se',
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const RegistroScreen()),
        ),
      ),
      children: [
        const Center(child: Logotipo()),
        const SizedBox(height: 44),
        const Text('Bem-vindo de volta', style: Txt.titulo),
        const SizedBox(height: 10),
        Text(
          'Entre para continuar organizando seu dia.',
          style: Txt.subtitulo.copyWith(fontSize: 17),
        ),
        const SizedBox(height: 28),
        CampoTexto(
          rotulo: 'E-mail',
          dica: 'voce@email.com',
          controller: _email,
          icone: Icons.mail_outline,
          teclado: TextInputType.emailAddress,
          acao: TextInputAction.next,
          erro: _erroEmail,
          autofillHints: const [AutofillHints.email],
          onChanged: (_) => setState(() => _erroEmail = null),
        ),
        const SizedBox(height: 16),
        CampoSenha(
          rotulo: 'Senha',
          dica: 'Sua senha',
          controller: _senha,
          icone: Icons.lock_outline,
          erro: _erroSenha,
          acao: TextInputAction.done,
          onSubmitted: (_) => _entrar(),
          onChanged: (_) => setState(() => _erroSenha = null),
        ),
        const SizedBox(height: 14),
        Align(
          alignment: Alignment.centerRight,
          child: GestureDetector(
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const EsqueceuSenhaScreen()),
            ),
            child: Text('Esqueceu a senha?', style: Txt.link),
          ),
        ),
        if (_erroGeral != null) ...[
          const SizedBox(height: 14),
          Text(
            _erroGeral!,
            style: Txt.pequeno.copyWith(color: Cores.perigo, fontSize: 13),
          ),
        ],
        const SizedBox(height: 16),
        BotaoPrimario(
          texto: 'Entrar',
          carregando: _enviando,
          onPressed: _entrar,
        ),
      ],
    );
  }
}
