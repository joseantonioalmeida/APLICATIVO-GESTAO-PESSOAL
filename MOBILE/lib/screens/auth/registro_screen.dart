import 'package:flutter/material.dart';

import '../../core/formatadores.dart';
import '../../core/theme.dart';
import '../../core/validadores.dart';
import '../../models/modelos.dart';
import '../../state/app_scope.dart';
import '../../widgets/comuns.dart';
import 'auth_base.dart';

/// Tela 2 - Criar conta.
class RegistroScreen extends StatefulWidget {
  const RegistroScreen({super.key});

  @override
  State<RegistroScreen> createState() => _RegistroScreenState();
}

class _RegistroScreenState extends State<RegistroScreen> {
  final _nome = TextEditingController();
  final _email = TextEditingController();
  final _senha = TextEditingController();
  final _confirmar = TextEditingController();
  final _nascimento = TextEditingController();
  final _erros = <String, String?>{};
  String? _erroGeral;
  bool _enviando = false;

  @override
  void dispose() {
    for (final c in [_nome, _email, _senha, _confirmar, _nascimento]) {
      c.dispose();
    }
    super.dispose();
  }

  bool _validar() {
    final erros = <String, String?>{};
    erros['nome'] = Valida.nome(_nome.text, 'Informe seu nome completo');
    erros['email'] = _email.text.trim().isEmpty
        ? 'Informe seu e-mail'
        : (!Valida.emailValido(_email.text)
              ? 'Informe um e-mail válido'
              : null);
    erros['senha'] = Valida.senha(_senha.text);
    erros['confirmar'] = _confirmar.text.isEmpty
        ? 'Confirme sua senha'
        : (_confirmar.text != _senha.text
              ? 'As senhas devem ser idênticas'
              : null);
    final nasc = Conv.data(_nascimento.text);
    erros['nascimento'] = _nascimento.text.isEmpty
        ? 'Informe sua data de nascimento'
        : (nasc == null
              ? 'Informe uma data válida'
              : (nasc.isAfter(AppScope.of(context).hoje)
                    ? 'A data de nascimento não pode ser futura'
                    : null));
    setState(() {
      _erros
        ..clear()
        ..addAll(erros);
      _erroGeral = null;
    });
    return erros.values.every((e) => e == null);
  }

  Future<void> _criar() async {
    if (_enviando || !_validar()) return;
    final escopo = AppScope.of(context);
    setState(() => _enviando = true);
    try {
      await escopo.repositorio.registrar(
        nome: _nome.text,
        email: _email.text,
        senha: _senha.text,
        nascimento: Conv.data(_nascimento.text)!,
      );
      if (!mounted) return;
      escopo.aoEntrar();
    } on ErroApp catch (e) {
      if (!mounted) return;
      setState(() {
        if (e.campo != null) {
          _erros[e.campo!] = e.mensagem;
        } else {
          _erroGeral = e.mensagem;
        }
      });
    } catch (_) {
      if (mounted) {
        setState(
          () => _erroGeral = 'Não foi possível criar a conta. Tente novamente',
        );
      }
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  void _limpa(String campo) {
    if (_erros[campo] != null) setState(() => _erros[campo] = null);
  }

  @override
  Widget build(BuildContext context) {
    return AuthScaffold(
      voltar: true,
      rodape: RodapeLink(
        texto: 'Já tem uma conta?',
        link: 'Fazer login',
        onTap: () => Navigator.pop(context),
      ),
      children: [
        const SizedBox(height: 17),
        const Text('Criar sua conta', style: Txt.titulo),
        const SizedBox(height: 10),
        Text(
          'Preencha os dados abaixo para se cadastrar.',
          style: Txt.subtitulo.copyWith(fontSize: 17),
        ),
        const SizedBox(height: 22),
        CampoTexto(
          rotulo: 'Nome completo',
          dica: 'Seu nome completo',
          controller: _nome,
          capitalizacao: TextCapitalization.words,
          acao: TextInputAction.next,
          erro: _erros['nome'],
          onChanged: (_) => _limpa('nome'),
        ),
        const SizedBox(height: 14),
        CampoTexto(
          rotulo: 'E-mail',
          dica: 'voce@email.com',
          controller: _email,
          teclado: TextInputType.emailAddress,
          acao: TextInputAction.next,
          erro: _erros['email'],
          onChanged: (_) => _limpa('email'),
        ),
        const SizedBox(height: 14),
        CampoSenha(
          rotulo: 'Senha',
          dica: 'Mínimo de 8 caracteres',
          controller: _senha,
          acao: TextInputAction.next,
          erro: _erros['senha'],
          onChanged: (_) => _limpa('senha'),
        ),
        const SizedBox(height: 14),
        CampoSenha(
          rotulo: 'Confirmar senha',
          dica: 'Repita a senha',
          controller: _confirmar,
          acao: TextInputAction.next,
          erro: _erros['confirmar'],
          onChanged: (_) => _limpa('confirmar'),
        ),
        const SizedBox(height: 14),
        CampoData(
          rotulo: 'Data de nascimento',
          controller: _nascimento,
          comIcone: false,
          erro: _erros['nascimento'],
          ultima: AppScope.of(context).hoje,
          onChanged: (_) => _limpa('nascimento'),
        ),
        if (_erroGeral != null) ...[
          const SizedBox(height: 12),
          Text(
            _erroGeral!,
            style: Txt.pequeno.copyWith(color: Cores.perigo, fontSize: 13),
          ),
        ],
        const SizedBox(height: 24),
        BotaoPrimario(
          texto: 'Criar conta',
          carregando: _enviando,
          onPressed: _criar,
        ),
      ],
    );
  }
}
