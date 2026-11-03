import '../models/modelos.dart';

/// Contrato de dados do aplicativo.
///
/// Hoje é implementado por [RepositorioMemoria] (dados locais de demonstração).
/// Quando a API estiver pronta, basta criar uma implementação HTTP desta
/// interface e trocá-la em `main.dart`: nenhuma tela precisa mudar.
abstract class Repositorio {
  // ------------------------------------------------------------------ Conta
  Usuario? get usuario;

  /// Lança [ErroApp] com a mensagem exibida na tela quando inválido.
  Future<Usuario> entrar(String email, String senha);

  Future<Usuario> registrar({
    required String nome,
    required String email,
    required String senha,
    required DateTime nascimento,
  });

  void sair();

  /// Envia (ou reenvia) o código de 8 dígitos. Lança [ErroApp] se o e-mail não
  /// existir. Retorna o código somente em modo demonstração (sem envio real).
  Future<String?> solicitarCodigo(String email);

  /// Valida o código e devolve o token de redefinição.
  Future<String> verificarCodigo(String email, String codigo);

  Future<void> redefinirSenha({
    required String email,
    required String token,
    required String novaSenha,
  });

  // -------------------------------------------------------------- Atividades
  Future<ConsultaAtividades> consultarAtividades(
    FiltroAtividades filtro, {
    int deslocamento = 0,
    int limite = 10,
  });

  Future<PendenciasAnteriores> pendenciasAnteriores();

  Future<Atividade> obterAtividade(String id);

  Future<List<Atividade>> sobreposicoes(
    DateTime data,
    int inicio,
    int fim, {
    String? ignorarId,
  });

  Future<Atividade> criarAtividade(AtividadeForm form);

  Future<void> editarAtividade(
    String id,
    AtividadeForm form,
    EscopoSerie escopo,
  );

  Future<void> excluirAtividade(String id, EscopoSerie escopo);

  /// Idempotente: concluir uma atividade já concluída a mantém concluída.
  Future<Atividade> alterarConclusaoAtividade(String id, bool concluida);

  // ------------------------------------------------------------ Importâncias
  /// Devolve o resultado completo da consulta (já filtrado e ordenado).
  Future<List<Importancia>> consultarImportancias(
    FiltroImportancia filtro, {
    required int ano,
    required int mes,
    String busca = '',
  });

  /// Próximas importâncias pendentes (hoje ou depois), em ordem de data.
  Future<List<Importancia>> proximasImportancias({int limite = 3});

  Future<int> totalAtrasadas();

  Future<int> totalPendentesDoMes(int ano, int mes);

  Future<Importancia> obterImportancia(String id);

  Future<Importancia> criarImportancia(ImportanciaForm form);

  Future<void> editarImportancia(
    String id,
    ImportanciaForm form,
    EscopoSerie escopo,
  );

  Future<void> excluirImportancia(String id, EscopoSerie escopo);

  /// Para importâncias sem despesa.
  Future<Importancia> alterarConclusaoImportancia(String id, bool concluida);

  /// Despesas do usuário ainda sem importância vinculada.
  Future<List<Movimentacao>> despesasSemVinculo({String busca = ''});

  /// Vincula uma despesa existente, concluindo a importância (sem novo lançamento).
  Future<void> vincularDespesa(String importanciaId, String movimentacaoId);

  // -------------------------------------------------------------- Financeiro
  Future<ResumoFinanceiro> resumoMes(int ano, int mes);

  Future<ResumoDia> resumoDia(DateTime dia);

  Future<ConsultaMov> consultarMovimentacoes(
    FiltroMov filtro, {
    int deslocamento = 0,
    int limite = 10,
  });

  Future<Movimentacao> obterMovimentacao(String id);

  /// Se [MovimentacaoForm.importanciaId] vier preenchido, cria a despesa e
  /// conclui a importância na mesma operação.
  Future<Movimentacao> criarMovimentacao(MovimentacaoForm form);

  Future<void> editarMovimentacao(String id, MovimentacaoForm form);

  /// Reabre a importância vinculada, se houver.
  Future<void> excluirMovimentacao(String id);

  // ------------------------------------------------------------ Notificações
  Future<List<Notificacao>> listarNotificacoes();

  Future<int> totalNaoLidas();

  Future<void> marcarNotificacaoLida(String id);
}
