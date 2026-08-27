import 'dart:async';

enum BluetoothType { ble, classic }

class DiscoveredScale {
  final String id;
  final String name;
  final BluetoothType type;
  final dynamic nativeDevice;

  const DiscoveredScale({
    required this.id,
    required this.name,
    required this.type,
    required this.nativeDevice,
  });
}

abstract class BaseScaleService {
  Stream<double> get weightStream;
  Stream<bool> get connectionStatus;

  Future<List<DiscoveredScale>> scan({Duration timeout});
  Future<void> connect(DiscoveredScale scale);
  Future<void> disconnect();
  void dispose();
}
