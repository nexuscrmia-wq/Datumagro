import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:provider/provider.dart';
import 'package:datumagro_mobile/data/database.dart';
import 'package:datumagro_mobile/services/sync_service.dart';
import '../services/api.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:async';
import '../config.dart';
import 'animal_form.dart';
import 'romaneio_screen.dart';

class AnimalsListScreen extends StatefulWidget {
  const AnimalsListScreen({super.key});

  @override
  State<AnimalsListScreen> createState() => _AnimalsListScreenState();
}

class _AnimalsListScreenState extends State<AnimalsListScreen> {
  late final AppDatabase db;
  String token = '';
  bool canEditAnimals = true;
  StreamSubscription<ConnectivityResult>? _connectivitySub;
  DateTime? _lastSyncAttempt;

  final _secureStorage = const FlutterSecureStorage();

  @override
  void initState() {
    super.initState();
    db = Provider.of<AppDatabase>(context, listen: false);
    // load token first
    _secureStorage.read(key: 'access_token').then((v) {
      setState(() {
        token = v ?? '';
      });
    });

    // load stored user and permissions
    _secureStorage.read(key: 'user').then((s) {
      if (s == null) return;
      try {
        final data = json.decode(s) as Map<String, dynamic>;
        final permissoes = data['permissoes'] as Map<String, dynamic>?;
        setState(() {
          canEditAnimals = permissoes == null
              ? true
              : (permissoes['can_edit_animais'] == true);
        });
      } catch (_) {}
    });

    // Listen to connectivity changes and trigger sync when online
    _connectivitySub =
        Connectivity().onConnectivityChanged.listen((result) async {
      if (result != ConnectivityResult.none) {
        final now = DateTime.now();
        if (_lastSyncAttempt == null ||
            now.difference(_lastSyncAttempt!).inSeconds > 10) {
          _lastSyncAttempt = now;
          final t = await _secureStorage.read(key: 'access_token');
          if ((t ?? token).isNotEmpty) {
            if (!mounted) return;
            final messenger = ScaffoldMessenger.of(context);
            final sync = SyncService(
                db: db,
                baseUrl: '$kApiBaseUrlEmulator/api/cadastros',
                api: ApiService());
            try {
              await sync.sync();
              messenger.showSnackBar(const SnackBar(
                  content: Text('Sincronização automática concluída')));
            } catch (e) {
              // ignore errors for now; user can manual sync
            }
          }
        }
      }
    });
  }

  @override
  void dispose() {
    _connectivitySub?.cancel();
    try {
      db.close();
    } catch (_) {}
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Animais', key: Key('animals_title')),
        actions: [
          IconButton(
            icon: const Icon(Icons.scale),
            tooltip: 'Romaneio de Pesagem',
            onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const RomaneioScreen())),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: StreamBuilder<List<Animal>>(
              stream: db.watchAllAnimals(),
              builder: (context, snapshot) {
                final animals = snapshot.data ?? [];
                if (animals.isEmpty) {
                  return const Center(child: Text('Nenhum animal (offline)'));
                }
                return ListView.builder(
                  itemCount: animals.length,
                  itemBuilder: (context, index) {
                    final a = animals[index];
                    return ListTile(
                      title: Text(a.brinco),
                      subtitle: Text(a.raca ?? ''),
                    );
                  },
                );
              },
            ),
          ),
          Row(
            children: [
              ElevatedButton(
                onPressed: () async {
                  final messenger = ScaffoldMessenger.of(context);
                  final sync = SyncService(
                      db: db,
                      baseUrl: '$kApiBaseUrlEmulator/api/cadastros',
                      api: ApiService());
                  try {
                    await sync.sync();
                    messenger.showSnackBar(const SnackBar(
                        content: Text('Sincronização concluída')));
                  } catch (e) {
                    messenger.showSnackBar(
                        SnackBar(content: Text('Erro de sync: $e')));
                  }
                },
                child: const Text('Sincronizar'),
              ),
            ],
          )
        ],
      ),
      floatingActionButton: canEditAnimals
          ? FloatingActionButton(
              onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const AnimalFormScreen())),
              child: const Icon(Icons.add),
            )
          : null,
    );
  }
}
