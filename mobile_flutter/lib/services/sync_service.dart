import 'dart:convert';

import 'package:datumagro_mobile/data/database.dart';
import 'package:drift/drift.dart' show Value;
import '../config.dart';
import 'api.dart';

class SyncService {
  final AppDatabase db;
  final String baseUrl; // ex: https://your-api.example.com/api/cadastros/
  final ApiService api;

  SyncService({required this.db, required this.baseUrl, required this.api});

  Future<void> sync() async {
    final queue = await db.getPendingQueue();
    final changes = queue.map((q) {
      final payload = json.decode(q.payload);
      return {
        'op': q.op,
        'model': q.model,
        'client_id': q.clientId,
        'data': payload,
      };
    }).toList();

    const lastSync = null; // In future save last sync timestamp

    final effectiveBase =
        baseUrl.isEmpty ? '$kApiBaseUrlEmulator/api/cadastros' : baseUrl;
    final url = Uri.parse('$effectiveBase/sync/');
    final resp = await api.authenticatedPost(
        url, {'last_server_sync': lastSync, 'changes': changes});

    if (resp.statusCode == 200) {
      final body = json.decode(resp.body);
      final applied = body['applied'] as List<dynamic>? ?? [];

      // Remove applied items from queue
      for (var item in applied) {
        final clientId = item['client_id'];
        if (clientId != null) {
          final matches = queue.where((q) => q.clientId == clientId).toList();
          if (matches.isNotEmpty) {
            await db.removeQueueItem(matches.first.id);
          }
        }
      }

      // Apply server changes: map server 'animal' to local DB and upsert by serverId
      final serverChanges = body['server_changes'] as List<dynamic>? ?? [];
      for (var sc in serverChanges) {
        if (sc['model'] == 'animal') {
          final data = sc['data'] as Map<String, dynamic>;
          final serverId = int.tryParse('${data['id']}');
          DateTime? parseDate(String? s) {
            if (s == null) return null;
            try {
              return DateTime.parse(s);
            } catch (_) {
              return null;
            }
          }

          final updatedAt = parseDate(sc['updated_at'] as String?);
          final dataNascimento = parseDate(data['data_nascimento'] as String?);

          final companion = AnimalsCompanion(
            serverId: Value(serverId),
            propriedadeId: Value(data['propriedade'] ?? 0),
            brinco: Value(data['brinco'] ?? ''),
            raca: Value(data['raca'] ?? ''),
            sexo: Value(data['sexo'] ?? ''),
            dataNascimento: Value(dataNascimento),
            categoria: Value(data['categoria'] ?? ''),
            temperamento: Value(data['temperamento'] ?? ''),
            aptidao: Value(data['aptidao'] ?? ''),
            statusReprodutivo: Value(data['status_reprodutivo'] ?? ''),
            isReprodutor: Value(data['is_reprodut'] ?? false),
            caracteristicas: Value(data['caracteristicas_adicionais'] ?? ''),
            paiId: Value(data['pai'] as int?),
            maeId: Value(data['mae'] as int?),
            fotoPerfil: Value(data['foto_perfil'] ?? ''),
            ativo: Value(data['ativo'] ?? true),
            updatedAt: Value(updatedAt),
          );

          await db.upsertByServerId(serverId, companion);
        }
      }
    } else {
      throw Exception('Sync failed: ${resp.statusCode} ${resp.body}');
    }
  }
}
