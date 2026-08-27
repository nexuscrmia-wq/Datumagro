import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/ble_scale_service.dart';
import '../services/classic_scale_service.dart';
import '../services/scale_service.dart';

const _kLastScaleId = 'last_scale_id';
const _kLastScaleName = 'last_scale_name';
const _kLastScaleType = 'last_scale_type'; // 'ble' | 'classic'

/// Bottom sheet para conectar balança BLE ou Bluetooth Classic (SPP).
/// Retorna double do peso quando o usuário confirmar (ou automaticamente em modo rápido).
class BalancaSheet extends StatefulWidget {
  const BalancaSheet({super.key});

  @override
  State<BalancaSheet> createState() => _BalancaSheetState();
}

class _BalancaSheetState extends State<BalancaSheet> {
  static const _verde = Color(0xFF2E7D32);
  static const _amber = Color(0xFFF59E0B);
  static const _storage = FlutterSecureStorage();

  late BleScaleService _bleService;
  late ClassicScaleService _classicService;

  _Phase _phase = _Phase.idle;
  List<DiscoveredScale> _foundBle = [];
  List<DiscoveredScale> _foundClassic = [];
  DiscoveredScale? _selected;
  BaseScaleService? _activeService;

  // Leituras para cálculo de estabilidade
  final List<_Reading> _readings = [];
  double? _liveWeight;
  bool _isStable = false;

  // Modo rápido (auto-fill ao estabilizar)
  bool _modoRapido = false;
  Timer? _autoFillTimer;

  String? _erro;
  String? _cachedId;
  String? _cachedName;
  String? _cachedType;

  StreamSubscription? _weightSub;
  StreamSubscription? _connSub;

  @override
  void initState() {
    super.initState();
    _bleService = BleScaleService();
    _classicService = ClassicScaleService();
    _loadCache();
  }

  @override
  void dispose() {
    _autoFillTimer?.cancel();
    _weightSub?.cancel();
    _connSub?.cancel();
    _bleService.dispose();
    _classicService.dispose();
    super.dispose();
  }

  Future<void> _loadCache() async {
    _cachedId = await _storage.read(key: _kLastScaleId);
    _cachedName = await _storage.read(key: _kLastScaleName);
    _cachedType = await _storage.read(key: _kLastScaleType);
    if (mounted && _cachedId != null) setState(() {});
  }

  Future<void> _saveCache(DiscoveredScale scale) async {
    await _storage.write(key: _kLastScaleId, value: scale.id);
    await _storage.write(key: _kLastScaleName, value: scale.name);
    await _storage.write(key: _kLastScaleType,
        value: scale.type == BluetoothType.ble ? 'ble' : 'classic');
  }

  // ── Estabilidade ────────────────────────────────────────────────────────────

  void _addReading(double weight) {
    final now = DateTime.now();
    _readings.add(_Reading(weight: weight, time: now));
    // Mantém só leituras dos últimos 3 segundos
    _readings.removeWhere(
        (r) => now.difference(r.time).inMilliseconds > 3000);

    final stable = _computeStable();
    setState(() {
      _liveWeight = weight;
      _isStable = stable;
    });

    if (stable && _modoRapido) {
      _autoFillTimer?.cancel();
      _autoFillTimer = Timer(const Duration(milliseconds: 1500), () {
        if (mounted && _liveWeight != null) {
          HapticFeedback.mediumImpact();
          Navigator.of(context).pop(_liveWeight);
        }
      });
    } else {
      _autoFillTimer?.cancel();
    }
  }

  bool _computeStable() {
    if (_readings.length < 3) return false;
    final weights = _readings.map((r) => r.weight).toList();
    final mean = weights.reduce((a, b) => a + b) / weights.length;
    final variance =
        weights.map((w) => pow(w - mean, 2)).reduce((a, b) => a + b) /
            weights.length;
    final stdDev = sqrt(variance);
    return stdDev < 0.5; // ±0.5 kg de variação → estável
  }

  // ── Scan & Conexão ─────────────────────────────────────────────────────────

  Future<void> _scan() async {
    setState(() {
      _phase = _Phase.scanning;
      _foundBle = [];
      _foundClassic = [];
      _erro = null;
    });

    // Scan BLE e Classic em paralelo
    final results = await Future.wait([
      _bleService.scan(timeout: const Duration(seconds: 8)).catchError((_) => <DiscoveredScale>[]),
      _classicService.scan().catchError((_) => <DiscoveredScale>[]),
    ]);

    if (!mounted) return;

    final ble = results[0];
    final classic = results[1];

    if (ble.isEmpty && classic.isEmpty) {
      setState(() {
        _phase = _Phase.idle;
        _erro = 'Nenhuma balança encontrada.\nVerifique se o Bluetooth está ativado e a balança está ligada e pareada.';
      });
      return;
    }

    setState(() {
      _foundBle = ble;
      _foundClassic = classic;
      _phase = _Phase.picking;
    });
  }

  Future<void> _connect(DiscoveredScale scale) async {
    setState(() {
      _selected = scale;
      _phase = _Phase.connecting;
      _erro = null;
    });

    final service =
        scale.type == BluetoothType.ble ? _bleService : _classicService;

    try {
      await service.connect(scale);
      if (!mounted) return;

      _activeService = service;
      await _saveCache(scale);

      setState(() => _phase = _Phase.reading);

      _weightSub = service.weightStream.listen(_addReading);
      _connSub = service.connectionStatus.listen((connected) {
        if (!connected && mounted) {
          setState(() {
            _phase = _Phase.idle;
            _erro = 'Conexão encerrada pela balança.';
          });
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _phase = _Phase.idle;
        _erro = 'Falha ao conectar.\nVerifique se a balança está ligada e pareada nas configurações do Android.';
      });
    }
  }

  Future<void> _reconectarUltimaBalanca() async {
    setState(() {
      _phase = _Phase.scanning;
      _erro = null;
    });

    final isBle = _cachedType == 'ble';
    final service = isBle ? _bleService : _classicService;

    try {
      final scales = await service.scan(timeout: const Duration(seconds: 6));
      if (!mounted) return;

      final match = scales.where((s) => s.id == _cachedId).firstOrNull;
      if (match != null) {
        await _connect(match);
      } else {
        setState(() {
          _phase = _Phase.idle;
          _erro = '"$_cachedName" não encontrada. Tente buscar novamente.';
        });
      }
    } catch (_) {
      if (mounted) setState(() => _phase = _Phase.idle);
    }
  }

  void _confirmar() {
    if (_liveWeight != null) {
      HapticFeedback.mediumImpact();
      Navigator.of(context).pop(_liveWeight);
    }
  }

  // ── UI ─────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 36, height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.scale, color: _verde),
                const SizedBox(width: 8),
                Expanded(
                  child: Text('Conectar Balança',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold)),
                ),
                if (_phase == _Phase.reading)
                  _StabilityBadge(isStable: _isStable),
              ],
            ),
            const SizedBox(height: 20),
            _buildBody(),
          ],
        ),
      ),
    );
  }

  Widget _buildBody() {
    switch (_phase) {
      case _Phase.idle:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_erro != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(_erro!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red, fontSize: 13)),
              ),
            // Reconectar à última balança usada
            if (_cachedId != null && _cachedName != null)
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: _verde,
                  side: const BorderSide(color: _verde),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                icon: const Icon(Icons.bluetooth_connected, size: 18),
                label: Text('Reconectar: $_cachedName'),
                onPressed: _reconectarUltimaBalanca,
              ),
            const SizedBox(height: 10),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: _verde,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.bluetooth_searching),
              label: const Text('Buscar Balanças'),
              onPressed: _scan,
            ),
            const SizedBox(height: 10),
            Text(
              'Busca BLE + dispositivos Classic pareados no sistema.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
            ),
          ],
        );

      case _Phase.scanning:
        return const Padding(
          padding: EdgeInsets.symmetric(vertical: 28),
          child: Column(children: [
            CircularProgressIndicator(color: _verde),
            SizedBox(height: 14),
            Text('Buscando balanças BLE e Bluetooth Classic…',
                style: TextStyle(color: Colors.grey, fontSize: 13)),
          ]),
        );

      case _Phase.picking:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_foundBle.isNotEmpty) ...[
              _SectionLabel(label: 'Bluetooth LE', icon: Icons.sensors),
              ..._foundBle.map((s) => _DeviceTile(scale: s, onTap: () => _connect(s))),
            ],
            if (_foundClassic.isNotEmpty) ...[
              _SectionLabel(label: 'Bluetooth Classic (SPP)', icon: Icons.bluetooth),
              ..._foundClassic.map((s) => _DeviceTile(scale: s, onTap: () => _connect(s))),
            ],
            const SizedBox(height: 8),
            TextButton.icon(
              onPressed: _scan,
              icon: const Icon(Icons.refresh, size: 16),
              label: const Text('Buscar novamente'),
            ),
          ],
        );

      case _Phase.connecting:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 28),
          child: Column(children: [
            const CircularProgressIndicator(color: _verde),
            const SizedBox(height: 14),
            Text('Conectando em "${_selected?.name}"…',
                style: const TextStyle(color: Colors.grey, fontSize: 13)),
          ]),
        );

      case _Phase.reading:
        final weightText = _liveWeight != null
            ? '${_liveWeight!.toStringAsFixed(1)} kg'
            : '—';

        return Column(
          children: [
            // Display de peso
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 20),
              decoration: BoxDecoration(
                color: (_isStable ? _verde : _amber).withAlpha(14),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: (_isStable ? _verde : _amber).withAlpha(80),
                ),
              ),
              child: Column(children: [
                Text(
                  weightText,
                  style: TextStyle(
                    fontSize: 52,
                    fontWeight: FontWeight.bold,
                    color: _liveWeight != null
                        ? (_isStable ? _verde : _amber)
                        : Colors.grey,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.bluetooth_connected,
                        size: 13,
                        color: Colors.green.shade600),
                    const SizedBox(width: 4),
                    Text(
                      _selected?.name ?? '',
                      style: TextStyle(
                          fontSize: 12, color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ]),
            ),
            const SizedBox(height: 12),

            // Toggle modo rápido
            Row(
              children: [
                Switch(
                  value: _modoRapido,
                  activeColor: _verde,
                  onChanged: (v) => setState(() {
                    _modoRapido = v;
                    if (!v) _autoFillTimer?.cancel();
                  }),
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Modo Rápido',
                          style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                      Text('Preenche sozinho ao estabilizar por 1,5s',
                          style: TextStyle(
                              fontSize: 11, color: Colors.grey.shade500)),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),
            Row(children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () {
                    _activeService?.disconnect();
                    Navigator.of(context).pop();
                  },
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Cancelar'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                flex: 2,
                child: ElevatedButton(
                  onPressed: _liveWeight != null ? _confirmar : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _verde,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  child: Text(
                    _liveWeight != null
                        ? 'Usar ${_liveWeight!.toStringAsFixed(1)} kg'
                        : 'Aguardando…',
                  ),
                ),
              ),
            ]),
          ],
        );
    }
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

class _Reading {
  final double weight;
  final DateTime time;
  const _Reading({required this.weight, required this.time});
}

class _StabilityBadge extends StatelessWidget {
  final bool isStable;
  const _StabilityBadge({required this.isStable});

  @override
  Widget build(BuildContext context) {
    final color = isStable ? const Color(0xFF2E7D32) : const Color(0xFFF59E0B);
    final label = isStable ? 'Estável' : 'Oscilando';
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withAlpha(24),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withAlpha(100)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Icon(isStable ? Icons.check_circle : Icons.sync, size: 13, color: color),
        const SizedBox(width: 4),
        Text(label,
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
      ]),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  final IconData icon;
  const _SectionLabel({required this.label, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 4),
      child: Row(children: [
        Icon(icon, size: 14, color: Colors.grey.shade500),
        const SizedBox(width: 6),
        Text(label,
            style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Colors.grey.shade500,
                letterSpacing: 0.5)),
      ]),
    );
  }
}

class _DeviceTile extends StatelessWidget {
  final DiscoveredScale scale;
  final VoidCallback onTap;
  const _DeviceTile({required this.scale, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.scale, color: Color(0xFF2E7D32)),
      title: Text(scale.name, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(scale.id, style: const TextStyle(fontSize: 11)),
      trailing: const Icon(Icons.chevron_right, color: Colors.grey),
      onTap: onTap,
    );
  }
}

enum _Phase { idle, scanning, picking, connecting, reading }
