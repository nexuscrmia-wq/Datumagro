import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config.dart';

class ApiService {
  final _storage = const FlutterSecureStorage();

  final List<String> _refreshPaths = [
    '/api/token/refresh/',
    '/api/usuarios/token/refresh/',
    '/api/usuarios/refresh/',
  ];

  // ─── Token helpers ────────────────────────────────────────────────────────

  Future<String?> _getAccessToken() => _storage.read(key: 'access_token');

  /// Central dispatcher: executa [requestFn] com o token atual e, em caso de
  /// 401, tenta refresh transparente e refaz a requisição uma única vez.
  Future<http.Response> _authenticatedRequest(
    Future<http.Response> Function(String token) requestFn,
  ) async {
    String token = await _getAccessToken() ?? '';
    var response = await requestFn(token);

    if (response.statusCode == 401) {
      final refreshed = await refreshAccessToken();
      if (refreshed) {
        token = await _getAccessToken() ?? '';
        response = await requestFn(token);
      }
    }

    return response;
  }

  Map<String, String> _authHeaders(String token,
      {bool json = true, Map<String, String>? extra}) {
    final h = <String, String>{};
    if (json) h['Content-Type'] = 'application/json';
    if (token.isNotEmpty) h['Authorization'] = 'Bearer $token';
    if (extra != null) h.addAll(extra);
    return h;
  }

  // ─── Verbos HTTP autenticados ─────────────────────────────────────────────

  Future<http.Response> authenticatedGet(Uri url,
      {Map<String, String>? extraHeaders}) {
    return _authenticatedRequest((token) => http
        .get(url, headers: _authHeaders(token, json: false, extra: extraHeaders))
        .timeout(const Duration(seconds: 15)));
  }

  Future<http.Response> authenticatedPost(Uri url, Map<String, dynamic> body,
      {Map<String, String>? extraHeaders}) {
    return _authenticatedRequest((token) => http
        .post(url,
            headers: _authHeaders(token, extra: extraHeaders),
            body: json.encode(body))
        .timeout(const Duration(seconds: 15)));
  }

  Future<http.Response> authenticatedPatch(Uri url, Map<String, dynamic> body,
      {Map<String, String>? extraHeaders}) {
    return _authenticatedRequest((token) => http
        .patch(url,
            headers: _authHeaders(token, extra: extraHeaders),
            body: json.encode(body))
        .timeout(const Duration(seconds: 15)));
  }

  Future<http.Response> authenticatedPut(Uri url, Map<String, dynamic> body,
      {Map<String, String>? extraHeaders}) {
    return _authenticatedRequest((token) => http
        .put(url,
            headers: _authHeaders(token, extra: extraHeaders),
            body: json.encode(body))
        .timeout(const Duration(seconds: 15)));
  }

  Future<http.Response> authenticatedDelete(Uri url,
      {Map<String, String>? extraHeaders}) {
    return _authenticatedRequest((token) => http
        .delete(url, headers: _authHeaders(token, extra: extraHeaders))
        .timeout(const Duration(seconds: 15)));
  }

  // ─── Auth ────────────────────────────────────────────────────────────────

  Future<void> login(String email, String password) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/usuarios/login/');
    final resp = await http
        .post(url,
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'email': email, 'password': password}))
        .timeout(const Duration(seconds: 10));

    if (resp.statusCode != 200) {
      throw Exception('Login failed: ${resp.statusCode}');
    }

    final body = json.decode(resp.body) as Map<String, dynamic>;
    final access = body['access'] as String?;
    final refresh = body['refresh'] as String?;
    final user = body['user'];

    if (access == null || refresh == null || user == null) {
      throw Exception('Invalid login response');
    }

    await _storage.write(key: 'access_token', value: access);
    await _storage.write(key: 'refresh_token', value: refresh);
    await _storage.write(key: 'user', value: json.encode(user));
    await _storage.write(
        key: 'status_assinatura',
        value: body['status_assinatura'] as String? ?? 'PENDENTE');
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String password2,
    required String nomeCompleto,
  }) async {
    final url =
        Uri.parse('$kApiBaseUrlEmulator/api/usuarios/usuarios/registrar/');
    final resp = await http.post(url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'password2': password2,
          'username': email.split('@').first,
          'nome_completo': nomeCompleto,
          'tipo_usuario': 'proprietario',
        }));
    final body = json.decode(resp.body) as Map<String, dynamic>;
    if (resp.statusCode == 201) {
      await _storage.write(key: 'access_token', value: body['access'] as String);
      await _storage.write(
          key: 'refresh_token', value: body['refresh'] as String);
      await _storage.write(key: 'user', value: json.encode(body['user']));
      await _storage.write(
          key: 'status_assinatura',
          value: body['status_assinatura'] as String? ?? 'PENDENTE');
      return {'success': true};
    }
    return {'success': false, 'error': body};
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'user');
  }

  /// Tenta renovar o access token usando o refresh token armazenado.
  Future<bool> refreshAccessToken() async {
    final refresh = await _storage.read(key: 'refresh_token');
    if (refresh == null || refresh.isEmpty) return false;

    for (final path in _refreshPaths) {
      try {
        final url = Uri.parse('$kApiBaseUrlEmulator$path');
        final resp = await http
            .post(url,
                headers: {'Content-Type': 'application/json'},
                body: json.encode({'refresh': refresh}))
            .timeout(const Duration(seconds: 10));

        if (resp.statusCode == 200) {
          final body = json.decode(resp.body) as Map<String, dynamic>;
          final newAccess =
              body['access'] as String? ?? body['access_token'] as String?;
          if (newAccess != null && newAccess.isNotEmpty) {
            await _storage.write(key: 'access_token', value: newAccess);
            return true;
          }
        }
      } catch (_) {
        // tenta próximo path
      }
    }

    return false;
  }

  // ─── Subscription status ──────────────────────────────────────────────────

  Future<String> getStatusAssinatura() async =>
      await _storage.read(key: 'status_assinatura') ?? 'PENDENTE';

  Future<String> verificarStatusAssinatura() async {
    final resp = await authenticatedGet(
        Uri.parse('$kApiBaseUrlEmulator/api/usuarios/me/'));
    if (resp.statusCode == 200) {
      final body = json.decode(resp.body) as Map<String, dynamic>;
      final status = body['status_assinatura'] as String? ?? 'PENDENTE';
      await _storage.write(key: 'status_assinatura', value: status);
      return status;
    }
    return await getStatusAssinatura();
  }

  // ─── User / profile ───────────────────────────────────────────────────────

  Future<Map<String, String>> getAuthHeader() async {
    final token = await _getAccessToken();
    if (token == null || token.isEmpty) return {};
    return {'Authorization': 'Bearer $token'};
  }

  Future<Map<String, dynamic>?> getStoredUser() async {
    final s = await _storage.read(key: 'user');
    if (s == null) return null;
    try {
      return json.decode(s) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> fetchMe() async {
    try {
      final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/usuarios/me/');
      final resp = await authenticatedGet(url);
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body) as Map<String, dynamic>;
        await _storage.write(key: 'user', value: json.encode(data));
        return data;
      }
    } on SocketException {
      // offline: return cached user
    }
    return getStoredUser();
  }

  Future<Map<String, dynamic>?> uploadFotoPerfil(String filePath) async {
    final token = await _getAccessToken() ?? '';
    final uri = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/me/');
    final request = http.MultipartRequest('PATCH', uri)
      ..headers['Authorization'] = 'Bearer $token'
      ..files.add(await http.MultipartFile.fromPath('foto_perfil', filePath));
    final streamed = await request.send().timeout(const Duration(seconds: 30));
    final resp = await http.Response.fromStream(streamed);
    if (resp.statusCode == 200) {
      final data = json.decode(resp.body) as Map<String, dynamic>;
      await _storage.write(key: 'user', value: json.encode(data));
      return data;
    }
    return null;
  }

  Future<Map<String, dynamic>?> updateMe(Map<String, dynamic> fields) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/me/');
    final resp = await authenticatedPatch(url, fields);
    if (resp.statusCode == 200) {
      final data = json.decode(resp.body) as Map<String, dynamic>;
      await _storage.write(key: 'user', value: json.encode(data));
      return data;
    }
    return null;
  }

  Future<bool> changePassword(String senhaAtual, String novaSenha) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/usuarios/change_password/');
    final resp = await authenticatedPost(url, {
      'old_password': senhaAtual,
      'new_password': novaSenha,
    });
    return resp.statusCode == 200;
  }

  Future<bool> deleteAccount(String password) async {
    final refresh = await _storage.read(key: 'refresh_token');
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/excluir-conta/');
    final body = <String, dynamic>{'password': password};
    if (refresh != null && refresh.isNotEmpty) body['refresh'] = refresh;
    final resp = await authenticatedPost(url, body);
    return resp.statusCode == 200;
  }

  // ─── Convite de equipe ───────────────────────────────────────────────────

  /// Aceita um convite de equipe via token (deep link) ou código manual.
  /// Retorna `(userData, accessToken, refreshToken)` em caso de sucesso ou lança exceção.
  Future<Map<String, dynamic>> aceitarConvite({
    required String token,
    required String nome,
    required String email,
    required String password,
  }) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/equipe/aceitar/');
    final resp = await http.post(url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'token': token,
          'nome': nome,
          'email': email,
          'password': password,
          'password2': password,
        }));
    if (resp.statusCode == 201) {
      final data = json.decode(resp.body) as Map<String, dynamic>;
      await _storage.write(key: 'access_token', value: data['access'] as String);
      await _storage.write(key: 'refresh_token', value: data['refresh'] as String);
      await _storage.write(key: 'user', value: json.encode(data['user']));
      return data;
    }
    final body = json.decode(resp.body);
    final detail = (body is Map ? body['detail'] : null) ?? 'Erro ao aceitar convite.';
    throw Exception(detail.toString());
  }

  // ─── Dashboard ────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> fetchDashboard({bool forceOnline = false}) async {
    try {
      final url = Uri.parse('$kApiBaseUrlEmulator/api/dashboard/resumo/');
      final resp = await authenticatedGet(url);
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body) as Map<String, dynamic>;
        await _storage.write(key: 'cache_dashboard', value: json.encode(data));
        return data;
      }
    } on SocketException {
      // offline: return cached dashboard
    }
    final cached = await _storage.read(key: 'cache_dashboard');
    if (cached != null) return json.decode(cached) as Map<String, dynamic>;
    return {};
  }

  Future<bool> isOffline() async {
    try {
      final url = Uri.parse('$kApiBaseUrlEmulator/api/health/');
      await http.get(url).timeout(const Duration(seconds: 4));
      return false;
    } catch (_) {
      return true;
    }
  }

  // ─── Propriedades / GIS ───────────────────────────────────────────────────

  Future<List<Map<String, dynamic>>> fetchPropriedades() async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/cadastros/propriedades/');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) {
      final body = json.decode(resp.body);
      final results = body is Map ? body['results'] ?? body : body;
      return (results as List).cast<Map<String, dynamic>>();
    }
    return [];
  }

  Future<(Map<String, dynamic>?, String?)> criarPropriedade(Map<String, dynamic> dados) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/cadastros/propriedades/');
    final resp = await authenticatedPost(url, dados);
    if (resp.statusCode == 201) {
      return (json.decode(resp.body) as Map<String, dynamic>, null);
    }
    String erro = 'Erro ${resp.statusCode}';
    try {
      final body = json.decode(resp.body);
      if (body is Map) {
        final detail = body['detail'] ?? body.values.firstOrNull?.toString();
        if (detail != null) erro = detail.toString();
      }
    } catch (_) {}
    return (null, erro);
  }

  Future<void> atualizarCamadas(
    int propriedadeId, {
    Map<String, dynamic>? piquetes,
    Map<String, dynamic>? infraestrutura,
  }) async {
    final url = Uri.parse(
        '$kApiBaseUrlEmulator/api/cadastros/propriedades/$propriedadeId/camadas/');
    final body = <String, dynamic>{};
    if (piquetes != null) body['geojson_piquetes_talhoes'] = piquetes;
    if (infraestrutura != null) body['geojson_infraestrutura'] = infraestrutura;
    final resp = await authenticatedPatch(url, body);
    if (resp.statusCode != 200) {
      throw Exception('Erro ao salvar camadas: ${resp.statusCode}');
    }
  }

  // ─── Animais / Pesagens ───────────────────────────────────────────────────

  Future<Map<String, dynamic>?> fetchAnimalDetail(int animalId) async {
    final url =
        Uri.parse('$kApiBaseUrlEmulator/api/cadastros/animais/$animalId/');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) return json.decode(resp.body) as Map<String, dynamic>;
    return null;
  }

  Future<List<Map<String, dynamic>>> fetchPesagens(int animalId) async {
    final url = Uri.parse(
        '$kApiBaseUrlEmulator/api/cadastros/pesagens/?animal=$animalId&ordering=-data_pesagem');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) {
      final body = json.decode(resp.body);
      final results = body is Map ? body['results'] ?? body : body;
      return (results as List).cast<Map<String, dynamic>>();
    }
    return [];
  }

  Future<void> registrarPesagem({
    required int animalId,
    required double pesoKg,
    required String data,
    String observacoes = '',
  }) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/cadastros/pesagens/');
    final resp = await authenticatedPost(url, {
      'animal': animalId,
      'peso_kg': pesoKg,
      'data_pesagem': data,
      'observacoes': observacoes,
    });
    if (resp.statusCode != 201) {
      throw Exception('Erro ao salvar pesagem: ${resp.statusCode}');
    }
  }

  /// Verifica a versão mais recente disponível no servidor.
  /// Endpoint público — não requer autenticação.
  Future<Map<String, dynamic>> fetchVersaoApp() async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/versao/');
    final resp = await http
        .get(url)
        .timeout(const Duration(seconds: 8));
    if (resp.statusCode == 200) {
      return json.decode(utf8.decode(resp.bodyBytes)) as Map<String, dynamic>;
    }
    throw Exception('Versão indisponível (${resp.statusCode})');
  }

  // ─── Onboarding / questionário ───────────────────────────────────────────

  Future<void> patchOnboarding(Map<String, dynamic> data) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/onboarding/etapa/');
    final resp = await authenticatedPatch(url, data);
    if (resp.statusCode != 200) {
      throw Exception('Erro ao salvar questionário (${resp.statusCode})');
    }
  }

  // ─── Planos de assinatura (público, sem preço) ────────────────────────────

  Future<List<Map<String, dynamic>>> fetchPlanos() async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/assinaturas/planos/');
    final resp = await http.get(url).timeout(const Duration(seconds: 10));
    if (resp.statusCode == 200) {
      final body = json.decode(utf8.decode(resp.bodyBytes));
      final results = body is List ? body : (body['results'] ?? body);
      return (results as List).cast<Map<String, dynamic>>();
    }
    return [];
  }

  // ─── Financeiro ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> fetchFluxoCaixa() async {
    final url = Uri.parse(
        '$kApiBaseUrlEmulator/api/financeiro/transacoes/fluxo_caixa_mensal/');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) {
      return json.decode(utf8.decode(resp.bodyBytes)) as Map<String, dynamic>;
    }
    return {};
  }

  Future<List<Map<String, dynamic>>> fetchTransacoes({String? tipo}) async {
    var query = 'ordering=-data&page_size=50';
    if (tipo != null) query += '&tipo=$tipo';
    final url =
        Uri.parse('$kApiBaseUrlEmulator/api/financeiro/transacoes/?$query');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) {
      final body = json.decode(utf8.decode(resp.bodyBytes));
      final results = body is Map ? body['results'] ?? body : body;
      return (results as List).cast<Map<String, dynamic>>();
    }
    return [];
  }

  Future<void> criarTransacao({
    required String tipo,
    required double valor,
    required String data,
    required String descricao,
    String? categoriaNome,
  }) async {
    final url =
        Uri.parse('$kApiBaseUrlEmulator/api/financeiro/transacoes/');
    final body = <String, dynamic>{
      'tipo': tipo,
      'valor': valor,
      'data': data,
      'descricao': descricao,
      if (categoriaNome != null && categoriaNome.isNotEmpty)
        'categoria': categoriaNome,
    };
    final resp = await authenticatedPost(url, body);
    if (resp.statusCode != 201) {
      final err = json.decode(resp.body);
      throw Exception('Erro ao salvar: $err');
    }
  }

  // Retorna manejos sanitários com data_prevista nos próximos 7 dias
  Future<List<Map<String, dynamic>>> fetchManejosVencendo() async {
    final hoje = DateTime.now();
    final limite = hoje.add(const Duration(days: 7));
    final limiteStr = limite.toIso8601String().split('T').first;
    final url = Uri.parse(
        '$kApiBaseUrlEmulator/api/operacional/manejos-sanitarios/?data_prevista__lte=$limiteStr&status=PENDENTE');
    final resp = await _authenticatedRequest(
      (token) => http.get(url, headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      }),
    );
    if (resp.statusCode == 200) {
      final body = json.decode(resp.body);
      final results = body is Map ? body['results'] ?? body : body;
      return (results as List).cast<Map<String, dynamic>>();
    }
    return [];
  }
}
