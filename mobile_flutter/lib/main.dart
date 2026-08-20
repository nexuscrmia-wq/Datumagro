import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'data/database.dart';
import 'screens/splash_screen.dart';
import 'screens/login.dart';
import 'screens/register_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/romaneio_screen.dart';
import 'screens/financeiro_screen.dart';
import 'screens/mapa_propriedade_screen.dart';
import 'screens/planos_screen.dart';
import 'screens/pending_approval_screen.dart';
import 'screens/equipe_screen.dart';
import 'screens/alertas_screen.dart';
import 'screens/logistica_screen.dart';
import 'screens/home_screen.dart';
import 'services/api.dart';
import 'services/notificacao_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Verifica vacinas vencendo em segundo plano após iniciar o app
  NotificacaoService.verificarVacinasVencendo(ApiService());
  final db = AppDatabase();
  runApp(Provider<AppDatabase>.value(
    value: db,
    child: const DatumAgroApp(),
  ));
}

class DatumAgroApp extends StatelessWidget {
  const DatumAgroApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DatumAgro',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2E7D32)),
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/dashboard': (context) => const HomeScreen(),
        '/home': (context) => const HomeScreen(),
        '/animals': (context) => const HomeScreen(initialIndex: 1),
        '/profile': (context) => const ProfileScreen(),
        '/romaneio': (context) => const RomaneioScreen(),
        '/financeiro': (context) => const FinanceiroScreen(),
        '/equipe': (context) => const EquipeScreen(),
        '/logistica': (context) => const LogisticaScreen(),
        '/mapa': (context) => const MapaPropriedadeScreen(),
        '/planos': (context) => const PlanosScreen(),
        '/pending': (context) {
          final bloqueado =
              ModalRoute.of(context)?.settings.arguments == true;
          return PendingApprovalScreen(bloqueado: bloqueado);
        },
        '/alertas': (context) => const AlertasScreen(),
      },
    );
  }
}
