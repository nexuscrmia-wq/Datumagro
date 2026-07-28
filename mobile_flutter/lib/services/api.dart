import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config.dart';

class ApiService {
  final _storage = const FlutterSecureStorage();
  // Candidate refresh endpoints (try in order). Adjust if your backend uses a different path.
  final List<String> _refreshPaths = [
    '/api/token/refresh/',
    '/api/usuarios/token/refresh/',
    '/api/usuarios/refresh/',
  ];

  /// Login using new backend endpoint. Stores access, refresh and user payload.
  Future<void> login(String email, String password) async {
    // Backend exposes the ViewSet under /api/usuarios/usuarios/ so the login
    // action is available at /api/usuarios/usuarios/login/
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
  }

  Future<Map<String, String>> getAuthHeader() async {
    final token = await _storage.read(key: 'access_token');
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

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'user');
  }

  /// Try to refresh access token using stored refresh_token.
  /// Returns true if a new access token was saved.
  Future<bool> refreshAccessToken() async {
    final refresh = await _storage.read(key: 'refresh_token');
    if (refresh == null || refresh.isEmpty) return false;

    for (final path in _refreshPaths) {
      try {
        final url = Uri.parse('$kApiBaseUrlEmulator$path');
        // Common payload expected by SimpleJWT: {"refresh": "..."}
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
        // else try next candidate
      } catch (_) {
        // Try next candidate
      }
    }

    return false;
  }

  /// Perform POST with Authorization header and automatic refresh-on-401 (single retry).
  Future<http.Response> authenticatedPost(Uri url, Map<String, dynamic> body,
      {Map<String, String>? extraHeaders}) async {
    final token = await _storage.read(key: 'access_token');
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null && token.isNotEmpty)
      headers['Authorization'] = 'Bearer $token';
    if (extraHeaders != null) headers.addAll(extraHeaders);

    var resp = await http
        .post(url, headers: headers, body: json.encode(body))
        .timeout(const Duration(seconds: 15));
    if (resp.statusCode == 401) {
      final refreshed = await refreshAccessToken();
      if (refreshed) {
        final newToken = await _storage.read(key: 'access_token');
        final retryHeaders = <String, String>{
          'Content-Type': 'application/json'
        };
        if (newToken != null && newToken.isNotEmpty)
          retryHeaders['Authorization'] = 'Bearer $newToken';
        if (extraHeaders != null) retryHeaders.addAll(extraHeaders);
        resp = await http
            .post(url, headers: retryHeaders, body: json.encode(body))
            .timeout(const Duration(seconds: 15));
      }
    }
    return resp;
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String password2,
    required String nomeCompleto,
  }) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/usuarios/registrar/');
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
      await _storage.write(key: 'refresh_token', value: body['refresh'] as String);
      await _storage.write(key: 'user', value: json.encode(body['user']));
      return {'success': true};
    }
    return {'success': false, 'error': body};
  }

  Future<Map<String, dynamic>> fetchDashboard() async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/dashboard/resumo/');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) return json.decode(resp.body) as Map<String, dynamic>;
    return {};
  }

  Future<Map<String, dynamic>?> fetchMe() async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/usuarios/me/');
    final resp = await authenticatedGet(url);
    if (resp.statusCode == 200) return json.decode(resp.body) as Map<String, dynamic>;
    return null;
  }

  Future<bool> deleteAccount(String password) async {
    final refresh = await _storage.read(key: 'refresh_token');
    final url = Uri.parse('$kApiBaseUrlEmulator/api/usuarios/excluir-conta/');
    final body = <String, dynamic>{'password': password};
    if (refresh != null && refresh.isNotEmpty) body['refresh'] = refresh;
    final resp = await authenticatedPost(url, body);
    return resp.statusCode == 200;
  }

  Future<Map<String, dynamic>?> fetchAnimalDetail(int animalId) async {
    final url = Uri.parse('$kApiBaseUrlEmulator/api/cadastros/animais/$animalId/');
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

  /// Perform GET with Authorization header and automatic refresh-on-401 (single retry).
  Future<http.Response> authenticatedGet(Uri url,
      {Map<String, String>? extraHeaders}) async {
    final token = await _storage.read(key: 'access_token');
    final headers = <String, String>{};
    if (token != null && token.isNotEmpty)
      headers['Authorization'] = 'Bearer $token';
    if (extraHeaders != null) headers.addAll(extraHeaders);

    var resp = await http
        .get(url, headers: headers)
        .timeout(const Duration(seconds: 15));
    if (resp.statusCode == 401) {
      final refreshed = await refreshAccessToken();
      if (refreshed) {
        final newToken = await _storage.read(key: 'access_token');
        final retryHeaders = <String, String>{};
        if (newToken != null && newToken.isNotEmpty)
          retryHeaders['Authorization'] = 'Bearer $newToken';
        if (extraHeaders != null) retryHeaders.addAll(extraHeaders);
        resp = await http
            .get(url, headers: retryHeaders)
            .timeout(const Duration(seconds: 15));
      }
    }
    return resp;
  }
}
