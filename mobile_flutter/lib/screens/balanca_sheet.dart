import 'dart:async';
import 'package:flutter/material.dart';
import '../services/ble_scale_service.dart';
import '../services/scale_service.dart';

/// Bottom sheet para conectar balança BLE e capturar peso.
/// Retorna o double do peso quando o usuário confirmar.
class BalancaSheet extends StatefulWidget {
  const BalancaSheet({super.key});

  @override
  State<BalancaSheet> createState() => _BalancaSheetState();
}

class _BalancaSheetState extends State<BalancaSheet> {
  static const _verde = Color(0xFF2E7D32);

  final _service = BleScaleService();

  _Phase _phase = _Phase.idle;
  List<DiscoveredScale> _found = [];
  DiscoveredScale? _selected;
  double? _liveWeight;
  String? _erro;

  StreamSubscription? _weightSub;
  StreamSubscription? _connSub;

  @override
  void dispose() {
    _weightSub?.cancel();
    _connSub?.cancel();
    _service.dispose();
    super.dispose();
  }

  Future<void> _scan() async {
    setState(() {
      _phase = _Phase.scanning;
      _found = [];
      _erro = null;
    });
    try {
      final scales = await _service.scan(timeout: const Duration(seconds: 8));
      if (!mounted) return;
      if (scales.isEmpty) {
        setState(() {
          _phase = _Phase.idle;
          _erro = 'Nenhuma balança encontrada.\nVerifique se o Bluetooth está ativado e a balança está ligada.';
        });
      } else {
        setState(() {
          _found = scales;
          _phase = _Phase.picking;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _phase = _Phase.idle;
        _erro = 'Erro ao escanear: $e';
      });
    }
  }

  Future<void> _connect(DiscoveredScale scale) async {
    setState(() {
      _selected = scale;
      _phase = _Phase.connecting;
      _erro = null;
    });
    try {
      await _service.connect(scale);
      if (!mounted) return;
      setState(() => _phase = _Phase.reading);

      _weightSub = _service.weightStream.listen((w) {
        if (mounted) setState(() => _liveWeight = w);
      });

      _connSub = _service.connectionStatus.listen((connected) {
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
        _erro = 'Falha ao conectar: verifique se a balança está pareada nas configurações do Android.';
      });
    }
  }

  void _confirmar() {
    if (_liveWeight != null) {
      Navigator.of(context).pop(_liveWeight);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Handle
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
                Text('Conectar Balança',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold)),
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
          children: [
            if (_erro != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(_erro!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red, fontSize: 13)),
              ),
            Text(
              'Ligue a balança e certifique-se que o Bluetooth está ativado.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
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
            ),
          ],
        );

      case _Phase.scanning:
        return const Padding(
          padding: EdgeInsets.symmetric(vertical: 24),
          child: Column(
            children: [
              CircularProgressIndicator(color: _verde),
              SizedBox(height: 16),
              Text('Buscando dispositivos Bluetooth…',
                  style: TextStyle(color: Colors.grey)),
            ],
          ),
        );

      case _Phase.picking:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${_found.length} dispositivo(s) encontrado(s):',
                style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            ..._found.map((s) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.bluetooth, color: _verde),
                  title: Text(s.name),
                  subtitle: Text(s.id, style: const TextStyle(fontSize: 11)),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _connect(s),
                )),
            const SizedBox(height: 8),
            TextButton(
              onPressed: _scan,
              child: const Text('Buscar novamente'),
            ),
          ],
        );

      case _Phase.connecting:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 24),
          child: Column(
            children: [
              const CircularProgressIndicator(color: _verde),
              const SizedBox(height: 16),
              Text('Conectando em "${_selected?.name}"…',
                  style: const TextStyle(color: Colors.grey)),
            ],
          ),
        );

      case _Phase.reading:
        return Column(
          children: [
            // Peso em tempo real
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 24),
              decoration: BoxDecoration(
                color: _verde.withAlpha(12),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: _verde.withAlpha(60)),
              ),
              child: Column(
                children: [
                  Text(
                    _liveWeight != null
                        ? '${_liveWeight!.toStringAsFixed(1)} kg'
                        : '—',
                    style: TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: _liveWeight != null ? _verde : Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.bluetooth_connected,
                          size: 14, color: Colors.green.shade600),
                      const SizedBox(width: 4),
                      Text(
                        _selected?.name ?? 'Balança conectada',
                        style: TextStyle(
                            fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      _service.disconnect();
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
              ],
            ),
          ],
        );
    }
  }
}

enum _Phase { idle, scanning, picking, connecting, reading }
