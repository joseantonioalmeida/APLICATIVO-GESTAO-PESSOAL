import 'package:flutter/material.dart';

/// Listas fixas de categorias e opções definidas nos requisitos.
class Categorias {
  static const atividades = [
    'Trabalho',
    'Estudo',
    'Saúde',
    'Pessoal',
    'Lazer',
    'Outros',
  ];

  static const importancias = [
    'Contas',
    'Compras',
    'Veículo',
    'Lazer',
    'Saúde',
    'Educação',
    'Pessoal',
    'Outros',
  ];

  static const receitas = [
    'Salário',
    'Trabalho autônomo',
    'Vendas',
    'Rendimentos',
    'Reembolsos',
    'Outros',
  ];

  static const despesas = [
    'Alimentação',
    'Transporte',
    'Moradia',
    'Contas',
    'Compras',
    'Saúde',
    'Educação',
    'Lazer',
    'Veículo',
    'Outros',
  ];

  static const formasRecebimento = [
    'Pix',
    'Dinheiro',
    'Transferência',
    'Depósito',
    'Outros',
  ];

  static const formasPagamento = [
    'Pix',
    'Dinheiro',
    'Cartão de débito',
    'Transferência',
    'Boleto',
    'Outros',
  ];

  /// Ícone de cada categoria (despesas e importâncias).
  static IconData icone(String categoria) {
    switch (categoria) {
      case 'Moradia':
        return Icons.home_outlined;
      case 'Alimentação':
        return Icons.restaurant_outlined;
      case 'Contas':
        return Icons.credit_card_outlined;
      case 'Saúde':
        return Icons.favorite_border;
      case 'Transporte':
        return Icons.directions_bus_outlined;
      case 'Compras':
        return Icons.shopping_bag_outlined;
      case 'Educação':
        return Icons.school_outlined;
      case 'Lazer':
        return Icons.sports_esports_outlined;
      case 'Veículo':
        return Icons.directions_car_outlined;
      case 'Pessoal':
        return Icons.favorite_border;
      case 'Salário':
        return Icons.south_west;
      case 'Trabalho autônomo':
        return Icons.work_outline;
      case 'Vendas':
        return Icons.sell_outlined;
      case 'Rendimentos':
        return Icons.trending_up;
      case 'Reembolsos':
        return Icons.replay;
      default:
        return Icons.more_horiz;
    }
  }
}
