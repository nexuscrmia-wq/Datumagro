import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:provider/provider.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:datumagro_mobile/data/database.dart';
import 'package:datumagro_mobile/services/sync_service.dart';
import '../services/api.dart';
import '../config.dart';
import '../ajuda/ajuda_bottom_sheet.dart';
import '../ajuda/ajuda_service.dart';
import 'animal_form.dart';
import 'animal_detail_screen.dart';
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

  // Busca e filtros
  final _searchCtrl = TextEditingController();
  String _query = '';
  String? _filtroSexo;     // 'M', 'F', ou null
  String? _filtroCategoria;

  static const _verde = Color(0xFF2E7D32);
  static const _categorias = ['BEZERRO', 'NOVILHO', 'TOURO', 'VACA', 'NOVILHA', 'BOI'];

  final _secureStorage = const FlutterSecureStorage();
  final _ajudaService = AjudaService(ApiService());

  @override
  void initState() {
    super.initState();
    db = Provider.of<AppDatabase>(context, listen: false);
    _secureStorage.read(key: 'access_token').then((v) {
      setState(() => token = v ?? '');
      // Sincroniza ao abrir a tela para garantir dados atualizados em qualquer dispositivo
      if ((v ?? '').isNotEmpty) _runSync(silent: true);
    });
    _secureStorage.read(key: 'user').then((s) {
      if (s == null) return;
      try {
        final data = json.decode(s) as Map<String, dynamic>;
        final perm = data['permissoes'] as Map<String, dynamic>?;
        setState(() => canEditAnimals = perm == null ? true : perm['can_edit_animais'] == true);
      } catch (_) {}
    });

    _searchCtrl.addListener(() => setState(() => _query = _searchCtrl.text.toLowerCase().trim()));

    _connectivitySub = Connectivity().onConnectivityChanged.listen((result) async {
      if (result == ConnectivityResult.none) return;
      final now = DateTime.now();
      if (_lastSyncAttempt != null && now.difference(_lastSyncAttempt!).inSeconds < 10) return;
      _lastSyncAttempt = now;
      final t = await _secureStorage.read(key: 'access_token');
      if ((t ?? token).isEmpty || !mounted) return;
      await _runSync(silent: false);
    });
  }

  Future<void> _runSync({bool silent = false}) async {
    _lastSyncAttempt = DateTime.now();
    try {
      await SyncService(db: db, baseUrl: '$kApiBaseUrlEmulator/api/cadastros', api: ApiService()).sync();
      if (!silent && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Sincronizado ✓')));
      }
    } catch (_) {}
  }

  @override
  void dispose() {
    _connectivitySub?.cancel();
    _searchCtrl.dispose();
    try { db.close(); } catch (_) {}
    super.dispose();
  }

  List<Animal> _filtrar(List<Animal> todos) {
    return todos.where((a) {
      if (_query.isNotEmpty) {
        final brinco = a.brinco.toLowerCase();
        final raca = (a.raca ?? '').toLowerCase();
        if (!brinco.contains(_query) && !raca.contains(_query)) return false;
      }
      if (_filtroSexo != null && a.sexo != _filtroSexo) return false;
      if (_filtroCategoria != null && (a.categoria ?? '').toUpperCase() != _filtroCategoria) return false;
      return true;
    }).toList();
  }

  // ── QR Scanner ────────────────────────────────────────────────────────────
  Future<void> _abrirQRScanner(List<Animal> todos) async {
    final ctrl = MobileScannerController();
    final brinco = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      builder: (_) => SizedBox(
        height: 340,
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Aponte para o QR code ou brinco do animal',
                  style: TextStyle(fontWeight: FontWeight.bold)),
            ),
            Expanded(
              child: MobileScanner(
                controller: ctrl,
                onDetect: (capture) {
                  final code = capture.barcodes.firstOrNull?.rawValue;
                  if (code != null && code.isNotEmpty) {
                    ctrl.dispose();
                    Navigator.of(context).pop(code);
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
    if (brinco == null || !mounted) return;
    final animal = todos.where((a) => a.brinco.toLowerCase() == brinco.toLowerCase()).firstOrNull;
    if (animal != null) {
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => AnimalDetailScreen(animal: animal)));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Animal "$brinco" não encontrado.'), backgroundColor: Colors.orange),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Animais'),
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            tooltip: 'Ajuda',
            onPressed: () => mostrarAjuda(context, service: _ajudaService, moduloSlug: 'animals'),
          ),
          IconButton(
            icon: const Icon(Icons.scale),
            tooltip: 'Romaneio',
            onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RomaneioScreen())),
          ),
        ],
      ),
      body: StreamBuilder<List<Animal>>(
        stream: db.watchAllAnimals(),
        builder: (context, snapshot) {
          final todos = snapshot.data ?? [];
          final filtrados = _filtrar(todos);

          return Column(
            children: [
              // ── Barra de busca ──────────────────────────────────────────
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 12, 12, 4),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _searchCtrl,
                        decoration: InputDecoration(
                          hintText: 'Buscar por brinco ou raça...',
                          prefixIcon: const Icon(Icons.search, color: _verde),
                          suffixIcon: _query.isNotEmpty
                              ? IconButton(
                                  icon: const Icon(Icons.clear),
                                  onPressed: () => _searchCtrl.clear(),
                                )
                              : null,
                          filled: true,
                          fillColor: Colors.grey.shade100,
                          contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 12),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide.none,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Botão QR
                    Material(
                      color: _verde,
                      borderRadius: BorderRadius.circular(12),
                      child: InkWell(
                        borderRadius: BorderRadius.circular(12),
                        onTap: () => _abrirQRScanner(todos),
                        child: const Padding(
                          padding: EdgeInsets.all(10),
                          child: Icon(Icons.qr_code_scanner, color: Colors.white, size: 24),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // ── Chips de filtro ─────────────────────────────────────────
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.fromLTRB(12, 4, 12, 8),
                child: Row(
                  children: [
                    _FiltroChip(
                      label: 'Machos',
                      icon: Icons.male,
                      ativo: _filtroSexo == 'M',
                      cor: Colors.blue.shade700,
                      onTap: () => setState(() => _filtroSexo = _filtroSexo == 'M' ? null : 'M'),
                    ),
                    const SizedBox(width: 6),
                    _FiltroChip(
                      label: 'Fêmeas',
                      icon: Icons.female,
                      ativo: _filtroSexo == 'F',
                      cor: Colors.pink.shade600,
                      onTap: () => setState(() => _filtroSexo = _filtroSexo == 'F' ? null : 'F'),
                    ),
                    const SizedBox(width: 6),
                    ..._categorias.map((cat) => Padding(
                          padding: const EdgeInsets.only(right: 6),
                          child: _FiltroChip(
                            label: cat[0] + cat.substring(1).toLowerCase(),
                            ativo: _filtroCategoria == cat,
                            cor: _verde,
                            onTap: () => setState(() => _filtroCategoria = _filtroCategoria == cat ? null : cat),
                          ),
                        )),
                  ],
                ),
              ),

              // ── Contador ───────────────────────────────────────────────
              if (todos.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
                  child: Row(
                    children: [
                      Text(
                        '${filtrados.length} de ${todos.length} animal${todos.length != 1 ? 'is' : ''}',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                      const Spacer(),
                      if (_filtroSexo != null || _filtroCategoria != null || _query.isNotEmpty)
                        TextButton.icon(
                          onPressed: () => setState(() {
                            _filtroSexo = null;
                            _filtroCategoria = null;
                            _searchCtrl.clear();
                          }),
                          icon: const Icon(Icons.filter_alt_off, size: 14),
                          label: const Text('Limpar filtros', style: TextStyle(fontSize: 12)),
                          style: TextButton.styleFrom(foregroundColor: Colors.grey, visualDensity: VisualDensity.compact),
                        ),
                    ],
                  ),
                ),

              // ── Lista ──────────────────────────────────────────────────
              Expanded(
                child: filtrados.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(todos.isEmpty ? Icons.pets : Icons.search_off,
                                size: 56, color: Colors.grey.shade300),
                            const SizedBox(height: 12),
                            Text(
                              todos.isEmpty
                                  ? 'Nenhum animal cadastrado'
                                  : 'Nenhum animal encontrado',
                              style: TextStyle(color: Colors.grey.shade500),
                            ),
                            if (todos.isEmpty) ...[
                              const SizedBox(height: 8),
                              TextButton(
                                onPressed: () async {
                                  try {
                                    await SyncService(db: db, baseUrl: '$kApiBaseUrlEmulator/api/cadastros', api: ApiService()).sync();
                                  } catch (_) {}
                                },
                                child: const Text('Sincronizar agora'),
                              ),
                            ]
                          ],
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.only(bottom: 80),
                        itemCount: filtrados.length,
                        separatorBuilder: (_, __) => const Divider(height: 1, indent: 72),
                        itemBuilder: (context, i) {
                          final a = filtrados[i];
                          final isFemea = a.sexo == 'F';
                          return ListTile(
                            leading: CircleAvatar(
                              backgroundColor: isFemea ? Colors.pink.shade100 : Colors.blue.shade100,
                              child: Text(
                                a.sexo ?? '?',
                                style: TextStyle(
                                  color: isFemea ? Colors.pink.shade700 : Colors.blue.shade700,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            title: Text(a.brinco, style: const TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: Text([
                              if ((a.raca ?? '').isNotEmpty) a.raca!,
                              if ((a.categoria ?? '').isNotEmpty)
                                a.categoria![0] + a.categoria!.substring(1).toLowerCase(),
                            ].join(' · ')),
                            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute(builder: (_) => AnimalDetailScreen(animal: a)),
                            ),
                          );
                        },
                      ),
              ),
            ],
          );
        },
      ),
      floatingActionButton: canEditAnimals
          ? FloatingActionButton.extended(
              backgroundColor: _verde,
              foregroundColor: Colors.white,
              onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AnimalFormScreen())),
              icon: const Icon(Icons.add),
              label: const Text('Novo Animal'),
            )
          : null,
    );
  }
}

class _FiltroChip extends StatelessWidget {
  final String label;
  final IconData? icon;
  final bool ativo;
  final Color cor;
  final VoidCallback onTap;

  const _FiltroChip({
    required this.label,
    required this.ativo,
    required this.cor,
    required this.onTap,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: ativo ? cor : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: ativo ? cor : Colors.grey.shade300),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(icon, size: 14, color: ativo ? Colors.white : Colors.grey.shade600),
              const SizedBox(width: 4),
            ],
            Text(label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: ativo ? Colors.white : Colors.grey.shade700,
                )),
          ],
        ),
      ),
    );
  }
}
