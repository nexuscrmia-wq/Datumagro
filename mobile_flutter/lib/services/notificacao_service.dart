import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'api.dart';

class NotificacaoService {
  static final _plugin = FlutterLocalNotificationsPlugin();
  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized) return;
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    await _plugin.initialize(const InitializationSettings(android: android));
    _initialized = true;
  }

  static Future<void> verificarVacinasVencendo(ApiService api) async {
    await init();
    try {
      final manejos = await api.fetchManejosVencendo();
      if (manejos.isEmpty) return;

      for (int i = 0; i < manejos.length; i++) {
        final m = manejos[i];
        final brinco = m['animal_brinco'] ?? m['animal'] ?? 'Animal';
        final produto = m['produto'] ?? m['tipo'] ?? 'Vacina';
        final data = m['data_prevista'] ?? m['data'] ?? '';

        await _plugin.show(
          i,
          'Vacina vencendo — $brinco',
          '$produto · Aplicação prevista: $data',
          const NotificationDetails(
            android: AndroidNotificationDetails(
              'datumagro_vacinas',
              'Vacinas',
              channelDescription: 'Alertas de vacinas vencendo em 7 dias',
              importance: Importance.high,
              priority: Priority.high,
              icon: '@mipmap/ic_launcher',
            ),
          ),
        );
      }
    } catch (_) {}
  }
}
