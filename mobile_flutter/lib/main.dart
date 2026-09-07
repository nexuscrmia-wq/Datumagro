import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:app_links/app_links.dart';
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
import 'screens/aceitar_convite_screen.dart';
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

class DatumAgroApp extends StatefulWidget {
  const DatumAgroApp({super.key});

  @override
  State<DatumAgroApp> createState() => _DatumAgroAppState();
}

class _DatumAgroAppState extends State<DatumAgroApp> {
  final _navigatorKey = GlobalKey<NavigatorState>();

  @override
  void initState() {
    super.initState();
    _initDeepLinks();
  }

  void _initDeepLinks() {
    final appLinks = AppLinks();
    // Link que abriu o app quando estava fechado
    appLinks.getInitialLink().then((uri) {
      if (uri != null) _handleLink(uri);
    });
    // Links recebidos com o app aberto
    appLinks.uriLinkStream.listen(_handleLink, onError: (_) {});
  }

  void _handleLink(Uri uri) {
    if (uri.scheme == 'datumagro' && uri.host == 'entrar-equipe') {
      final token = uri.queryParameters['t'] ?? '';
      if (token.isNotEmpty) {
        _navigatorKey.currentState?.pushNamed('/aceitar-convite', arguments: token);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: _navigatorKey,
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
        '/aceitar-convite': (context) {
          final token =
              ModalRoute.of(context)?.settings.arguments as String? ?? '';
          return AceitarConviteScreen(token: token);
        },
      },
    );
  }
}
