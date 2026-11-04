import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:http/http.dart' as http;

import '../models/modelos.dart';

const mensagemSemConexao =
    'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente';
const mensagemSessaoExpirada = 'Sua sessão expirou. Entre novamente.';

/// Camada de transporte HTTP da API MinhaVida.
///
/// - Converte erros da API (`{codigo, mensagem, campos}`) em [ErroApp].
/// - Envia o token Bearer e avisa quando a sessão expira (401).
/// - Gera `Idempotency-Key` estável por envio: uma nova tentativa do MESMO
///   envio (após falha de rede ou 5xx) reutiliza a chave e não duplica o
///   registro; um novo envio com o mesmo conteúdo, depois de um sucesso,
///   recebe outra chave (lançamentos iguais legítimos não são barrados).
class ClienteApi {
  ClienteApi({
    required Uri base,
    http.Client? cliente,
    this.tempoLimite = const Duration(seconds: 20),
    Random? aleatorio,
  }) : _base = base, // ignore: prefer_initializing_formals
       _http = cliente ?? http.Client(),
       _rng = aleatorio ?? Random.secure();

  final Uri _base;
  final http.Client _http;
  final Duration tempoLimite;
  final Random _rng;

  String? token;

  /// Chamado quando a API recusa o token (401) numa rota autenticada.
  void Function()? aoSessaoExpirada;

  final Map<String, String> _chavesPendentes = {};

  Uri _uri(String caminho, Map<String, String?>? consulta) {
    final limpa = <String, String>{
      for (final e in (consulta ?? {}).entries)
        if (e.value != null) e.key: e.value!,
    };
    final raiz = _base.path.endsWith('/')
        ? _base.path.substring(0, _base.path.length - 1)
        : _base.path;
    return _base.replace(
      path: '$raiz$caminho',
      queryParameters: limpa.isEmpty ? null : limpa,
    );
  }

  String _novaChave() {
    const alfabeto = '0123456789abcdef';
    return List.generate(32, (_) => alfabeto[_rng.nextInt(16)]).join();
  }

  Future<dynamic> get(
    String caminho, {
    Map<String, String?>? consulta,
    bool autenticado = true,
  }) => _enviar('GET', caminho, consulta: consulta, autenticado: autenticado);

  Future<dynamic> put(String caminho, Object corpo) =>
      _enviar('PUT', caminho, corpo: corpo);

  Future<dynamic> patch(String caminho, Object corpo) =>
      _enviar('PATCH', caminho, corpo: corpo);

  Future<dynamic> delete(String caminho, {Map<String, String?>? consulta}) =>
      _enviar('DELETE', caminho, consulta: consulta);

  Future<dynamic> post(
    String caminho,
    Object corpo, {
    bool autenticado = true,
  }) => _enviar('POST', caminho, corpo: corpo, autenticado: autenticado);

  /// POST com `Idempotency-Key` (cadastros).
  Future<dynamic> postIdempotente(String caminho, Map<String, dynamic> corpo) {
    final assinatura = '$caminho|${jsonEncode(corpo)}';
    final chave = _chavesPendentes.putIfAbsent(assinatura, _novaChave);
    return _enviar(
      'POST',
      caminho,
      corpo: corpo,
      chaveIdempotencia: chave,
      aoConcluir: (resultadoDefinitivo) {
        if (resultadoDefinitivo) _chavesPendentes.remove(assinatura);
      },
    );
  }

  Future<dynamic> _enviar(
    String metodo,
    String caminho, {
    Map<String, String?>? consulta,
    Object? corpo,
    bool autenticado = true,
    String? chaveIdempotencia,
    void Function(bool resultadoDefinitivo)? aoConcluir,
  }) async {
    final requisicao = http.Request(metodo, _uri(caminho, consulta))
      ..headers['Accept'] = 'application/json';
    if (corpo != null) {
      requisicao.headers['Content-Type'] = 'application/json; charset=utf-8';
      requisicao.body = jsonEncode(corpo);
    }
    if (autenticado && token != null) {
      requisicao.headers['Authorization'] = 'Bearer $token';
    }
    if (chaveIdempotencia != null) {
      requisicao.headers['Idempotency-Key'] = chaveIdempotencia;
    }

    http.Response resposta;
    try {
      final stream = await _http.send(requisicao).timeout(tempoLimite);
      resposta = await http.Response.fromStream(stream).timeout(tempoLimite);
    } on Object {
      // Resultado desconhecido: a chave é mantida para a nova tentativa.
      aoConcluir?.call(false);
      throw const ErroApp(mensagemSemConexao);
    }

    final status = resposta.statusCode;
    // 5xx e 408 podem ter sido processados: mantém a chave.
    aoConcluir?.call(status < 500 && status != 408);
    if (status >= 200 && status < 300) {
      if (resposta.bodyBytes.isEmpty) return null;
      return jsonDecode(utf8.decode(resposta.bodyBytes));
    }
    throw _erroDe(resposta, autenticado: autenticado);
  }

  ErroApp _erroDe(http.Response r, {required bool autenticado}) {
    Map<String, dynamic>? corpo;
    try {
      final d = jsonDecode(utf8.decode(r.bodyBytes));
      if (d is Map<String, dynamic>) corpo = d;
    } on Object {
      corpo = null;
    }
    if (r.statusCode == 401 && autenticado) {
      token = null;
      aoSessaoExpirada?.call();
      return ErroApp(
        mensagemSessaoExpirada,
        codigo: corpo?['codigo'] as String?,
        status: 401,
      );
    }
    if (r.statusCode >= 500 || corpo == null) {
      return ErroApp(
        r.statusCode == 503
            ? 'Serviço temporariamente indisponível. Tente novamente'
            : 'Não foi possível concluir a operação. Tente novamente',
        status: r.statusCode,
      );
    }
    final campos = corpo['campos'];
    String? campo;
    var mensagem = (corpo['mensagem'] as String?) ?? 'Operação não concluída.';
    if (campos is List && campos.isNotEmpty && campos.first is Map) {
      final primeiro = campos.first as Map;
      campo = (primeiro['campo'] as String?)?.split('.').last;
      mensagem = (primeiro['mensagem'] as String?) ?? mensagem;
    }
    return ErroApp(
      mensagem,
      campo: campo,
      codigo: corpo['codigo'] as String?,
      status: r.statusCode,
    );
  }

  void fechar() => _http.close();
}
