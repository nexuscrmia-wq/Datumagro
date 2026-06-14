import 'dart:convert';
import 'api.dart';
import '../config.dart';

class ItemRomaneio {
  final String brinco;
  final String raca;
  final String categoria;
  final double pesoKg;
  final double arrobas;
  final double valorRs;

  ItemRomaneio({
    required this.brinco,
    required this.raca,
    required this.categoria,
    required this.pesoKg,
    required this.arrobas,
    required this.valorRs,
  });

  factory ItemRomaneio.fromJson(Map<String, dynamic> j) => ItemRomaneio(
        brinco: j['brinco'] ?? '',
        raca: j['raca'] ?? '',
        categoria: j['categoria'] ?? '',
        pesoKg: (j['peso_kg'] as num?)?.toDouble() ?? 0,
        arrobas: (j['arrobas'] as num?)?.toDouble() ?? 0,
        valorRs: (j['valor_rs'] as num?)?.toDouble() ?? 0,
      );
}

class ResumoRomaneio {
  final int totalAnimais;
  final double totalPesoKg;
  final double totalArrobas;
  final double totalValorRs;
  final double precoArroba;
  final String nomeFazenda;
  final String vendedor;
  final String comprador;
  final String dataHora;

  ResumoRomaneio({
    required this.totalAnimais,
    required this.totalPesoKg,
    required this.totalArrobas,
    required this.totalValorRs,
    required this.precoArroba,
    required this.nomeFazenda,
    required this.vendedor,
    required this.comprador,
    required this.dataHora,
  });

  factory ResumoRomaneio.fromJson(Map<String, dynamic> j) => ResumoRomaneio(
        totalAnimais: (j['total_animais'] as num?)?.toInt() ?? 0,
        totalPesoKg: (j['total_peso_kg'] as num?)?.toDouble() ?? 0,
        totalArrobas: (j['total_arrobas'] as num?)?.toDouble() ?? 0,
        totalValorRs: (j['total_valor_rs'] as num?)?.toDouble() ?? 0,
        precoArroba: (j['preco_arroba'] as num?)?.toDouble() ?? 0,
        nomeFazenda: j['nome_fazenda'] ?? '',
        vendedor: j['vendedor'] ?? '',
        comprador: j['comprador'] ?? '',
        dataHora: j['data_hora'] ?? '',
      );
}

class ResultadoRomaneio {
  final List<ItemRomaneio> itens;
  final ResumoRomaneio resumo;
  final String? pdfBase64;

  ResultadoRomaneio({
    required this.itens,
    required this.resumo,
    this.pdfBase64,
  });
}

class RomaneioService {
  final ApiService _api = ApiService();

  Future<ResultadoRomaneio> calcular({
    required double precoArroba,
    required List<Map<String, dynamic>> animais,
    String nomeFazenda = '',
    String vendedor = '',
    String comprador = '',
    bool gerarPdf = false,
  }) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/cadastros/romaneio/calcular/');
    final resp = await _api.authenticatedPost(url, {
      'preco_arroba': precoArroba,
      'animais': animais,
      'nome_fazenda': nomeFazenda,
      'vendedor': vendedor,
      'comprador': comprador,
      'gerar_pdf': gerarPdf,
    });

    if (resp.statusCode == 200) {
      final body = json.decode(resp.body) as Map<String, dynamic>;
      return ResultadoRomaneio(
        itens: (body['itens'] as List)
            .map((e) => ItemRomaneio.fromJson(e as Map<String, dynamic>))
            .toList(),
        resumo: ResumoRomaneio.fromJson(body['resumo'] as Map<String, dynamic>),
        pdfBase64: body['pdf_base64'] as String?,
      );
    }

    throw Exception('Erro ao calcular romaneio: ${resp.statusCode} ${resp.body}');
  }
}
