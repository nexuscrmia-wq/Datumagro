import 'dart:async';
import 'dart:convert';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'scale_service.dart';
import 'weight_parser.dart';

class ClassicScaleService implements BaseScaleService {
  final _weightCtrl = StreamController<double>.broadcast();
  final _connCtrl = StreamController<bool>.broadcast();

  BluetoothConnection? _conn;
  String _buffer = '';

  @override
  Stream<double> get weightStream => _weightCtrl.stream;

  @override
  Stream<bool> get connectionStatus => _connCtrl.stream;

  /// Retorna dispositivos já pareados (bonded) no sistema Android.
  /// Não requer scan — aparecem instantaneamente.
  @override
  Future<List<DiscoveredScale>> scan({Duration timeout = const Duration(seconds: 8)}) async {
    final bonded = await FlutterBluetoothSerial.instance.getBondedDevices();
    return bonded.map((d) => DiscoveredScale(
          id: d.address,
          name: d.name ?? d.address,
          type: BluetoothType.classic,
          nativeDevice: d,
        )).toList();
  }

  @override
  Future<void> connect(DiscoveredScale scale) async {
    final device = scale.nativeDevice as BluetoothDevice;
    _conn = await BluetoothConnection.toAddress(device.address);
    _connCtrl.add(true);

    _conn!.input!.listen(
      (bytes) => _processBytes(bytes),
      onDone: () => _connCtrl.add(false),
    );
  }

  void _processBytes(List<int> bytes) {
    _buffer += utf8.decode(bytes, allowMalformed: true);
    final lines = _buffer.split(RegExp(r'[\r\n\x03\x04]'));
    for (int i = 0; i < lines.length - 1; i++) {
      final parsed = UniversalWeightParser.parse(lines[i]);
      if (parsed != null) _weightCtrl.add(parsed.weight);
    }
    _buffer = lines.last;
  }

  @override
  Future<void> disconnect() async {
    await _conn?.close();
    _conn = null;
    _connCtrl.add(false);
    _buffer = '';
  }

  @override
  void dispose() {
    disconnect();
    _weightCtrl.close();
    _connCtrl.close();
  }
}
