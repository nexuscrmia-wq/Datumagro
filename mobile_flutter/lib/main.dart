import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'data/database.dart';
import 'screens/splash_screen.dart';
import 'screens/login.dart';
import 'screens/register_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/animals_list.dart';
import 'screens/profile_screen.dart';
import 'screens/romaneio_screen.dart';
import 'screens/module_placeholder_screen.dart';

void main() {
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
        '/dashboard': (context) => const DashboardScreen(),
        '/animals': (context) => const AnimalsListScreen(),
        '/profile': (context) => const ProfileScreen(),
        '/romaneio': (context) => const RomaneioScreen(),
        '/financeiro': (context) => const ModulePlaceholderScreen(
              title: 'Financeiro',
              icon: Icons.account_balance_wallet,
              description:
                  'Controle de receitas, despesas e fluxo de caixa da fazenda. Em breve disponível.',
              color: Colors.green,
            ),
        '/equipe': (context) => const ModulePlaceholderScreen(
              title: 'Equipe',
              icon: Icons.group,
              description:
                  'Gerencie funcionários, convites e permissões de acesso. Em breve disponível.',
              color: Colors.blue,
            ),
        '/logistica': (context) => const ModulePlaceholderScreen(
              title: 'Logística',
              icon: Icons.local_shipping,
              description:
                  'Controle de embarques, transporte e rastreabilidade internacional. Em breve disponível.',
              color: Colors.orange,
            ),
        '/alertas': (context) => const ModulePlaceholderScreen(
              title: 'Alertas e IA',
              icon: Icons.notifications_active,
              description:
                  'Central de alertas sanitários, reprodutivos e diagnósticos gerados por IA. Em breve disponível.',
              color: Colors.red,
            ),
      },
    );
  }
}
