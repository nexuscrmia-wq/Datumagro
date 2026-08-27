import 'dart:async';
import 'dart:convert';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'scale_service.dart';
import 'weight_parser.dart';

/// Serviço BLE universal para balanças de curral e industriais.
/// Detecta automaticamente a característica de dados via Notify/Indicate.
/// Compatível com Nordic UART Service, HM-10, Toledo, Tru-Test BLE.
class BleScaleService implements BaseScaleService {
  final _weightCtrl = StreamController<double>.broadcast();
  final _connCtrl = StreamController<bool>.broadcast();

  BluetoothDevice? _device;
  StreamSubscription? _notifySub;
  StreamSubscription? _connSub;
  String _buffer = '';

  @override
  Stream<double> get weightStream => _weightCtrl.stream;

  @override
  Stream<bool> get connectionStatus => _connCtrl.stream;

  @override
  Future<List<DiscoveredScale>> scan({Duration timeout = const Duration(seconds: 8)}) async {
    final found = <DiscoveredScale>[];
    final completer = Completer<void>();

    await FlutterBluePlus.startScan(timeout: timeout);

    final sub = FlutterBluePlus.scanResults.listen((results) {
      for (final r in results) {
        final name = r.device.platformName.isNotEmpty
            ? r.device.platformName
            : r.advertisementData.localName;
        if (name.isEmpty) continue;
        // Inclui qualquer dispositivo com nome — o usuário escolhe qual é a balança
        final already = found.any((s) => s.id == r.device.remoteId.str);
        if (!already) {
          found.add(DiscoveredScale(
            id: r.device.remoteId.str,
            name: name,
            type: BluetoothType.ble,
            nativeDevice: r.device,
          ));
        }
      }
    });

    await Future.delayed(timeout);
    await FlutterBluePlus.stopScan();
    await sub.cancel();
    completer.complete();

    return found;
  }

  @override
  Future<void> connect(DiscoveredScale scale) async {
    _device = scale.nativeDevice as BluetoothDevice;

    await _device!.connect(autoConnect: false, timeout: const Duration(seconds: 10));

    _connSub = _device!.connectionState.listen((state) {
      _connCtrl.add(state == BluetoothConnectionState.connected);
    });
    _connCtrl.add(true);

    final services = await _device!.discoverServices();

    for (final service in services) {
      for (final char in service.characteristics) {
        if (char.properties.notify || char.properties.indicate) {
          await char.setNotifyValue(true);
          _notifySub = char.lastValueStream.listen(_processBytes);
          return; // Usa a primeira característica de notificação encontrada
        }
      }
    }
  }

  void _processBytes(List<int> bytes) {
    _buffer += utf8.decode(bytes, allowMalformed: true);

    // Quebra nos delimitadores comuns de balanças
    final lines = _buffer.split(RegExp(r'[\r\n\x03\x04]'));
    for (int i = 0; i < lines.length - 1; i++) {
      final parsed = UniversalWeightParser.parse(lines[i]);
      if (parsed != null) {
        _weightCtrl.add(parsed.weight);
      }
    }
    _buffer = lines.last; // Mantém fragmento incompleto para o próximo pacote
  }

  @override
  Future<void> disconnect() async {
    await _notifySub?.cancel();
    await _connSub?.cancel();
    await _device?.disconnect();
    _connCtrl.add(false);
    _buffer = '';
    _device = null;
  }

  @override
  void dispose() {
    disconnect();
    _weightCtrl.close();
    _connCtrl.close();
  }
}
