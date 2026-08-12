import 'dart:convert';
import '../services/api.dart';
import '../config.dart';

class GuiaModulo {
  final String titulo;
  final String comoUsar;
  final String dicaAgro;

  const GuiaModulo({
    required this.titulo,
    required this.comoUsar,
    required this.dicaAgro,
  });

  factory GuiaModulo.fromJson(Map<String, dynamic> json) => GuiaModulo(
        titulo: json['titulo'] as String,
        comoUsar: json['como_usar_passo_a_passo'] as String,
        dicaAgro: json['dicas_agronomicas_zootecnicas'] as String,
      );
}

class AjudaService {
  final ApiService _api;

  const AjudaService(this._api);

  Future<GuiaModulo> buscarGuia(String moduloSlug) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/ajuda/$moduloSlug/');
    final resp = await _api.authenticatedGet(url);

    if (resp.statusCode == 200) {
      return GuiaModulo.fromJson(
          json.decode(resp.body) as Map<String, dynamic>);
    }
    if (resp.statusCode == 404) {
      throw Exception('Guia não encontrado para "$moduloSlug".');
    }
    throw Exception('Erro ao carregar ajuda (${resp.statusCode}).');
  }
}
