import 'dart:io';
import 'package:flutter/material.dart';
import '../services/api.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _fade;

  static const _verdeDark = Color(0xFF1B5E20);
  static const _verdeMain = Color(0xFF2E7D32);

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _fade = CurvedAnimation(parent: _ctrl, curve: Curves.easeIn);
    _ctrl.forward();
    _checkAuth();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(milliseconds: 1400));
    if (!mounted) return;

    // Timeout global de 12s — garante que o app nunca trava na splash
    // (flutter_secure_storage pode lançar PlatformException em instalações frescas)
    try {
      await _doCheckAuth().timeout(const Duration(seconds: 12));
    } catch (_) {
      if (mounted) Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  Future<void> _doCheckAuth() async {
    final api = ApiService();
    Map<String, dynamic>? user;
    try {
      user = await api.getStoredUser();
    } catch (_) {
      // PlatformException do flutter_secure_storage em alguns Android 11
      user = null;
    }

    if (!mounted) return;

    if (user != null) {
      // Tenta renovar token — falha silenciosa se estiver offline
      bool offline = false;
      try {
        await api.refreshAccessToken();
      } on SocketException {
        offline = true;
      } catch (_) {
        offline = true;
      }

      if (!mounted) return;

      // Modo offline: se tem token salvo, entra direto no dashboard
      if (offline) {
        String? token;
        try {
          final header = await api.getAuthHeader();
          token = header['Authorization'];
        } catch (_) {}
        if (!mounted) return;
        if (token != null && token.isNotEmpty) {
          Navigator.of(context).pushReplacementNamed('/dashboard');
          return;
        }
      }

      String status = 'PENDENTE';
      try {
        status = await api.getStatusAssinatura();
      } catch (_) {}

      if (!mounted) return;
      switch (status) {
        case 'ATIVO':
          Navigator.of(context).pushReplacementNamed('/dashboard');
        case 'BLOQUEADO':
          Navigator.of(context).pushReplacementNamed('/pending', arguments: true);
        default:
          Navigator.of(context).pushReplacementNamed('/pending');
      }
    } else {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [_verdeDark, _verdeMain],
          ),
        ),
        child: Center(
          child: FadeTransition(
            opacity: _fade,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 130,
                  height: 130,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(22),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.25),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(22),
                    child: Image.asset(
                      'assets/images/banner_datumagro.jpeg',
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
                const SizedBox(height: 28),
                const Text(
                  'DatumAgro',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 34,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Pecuária de precisão',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.8),
                    fontSize: 15,
                    letterSpacing: 0.4,
                  ),
                ),
                const SizedBox(height: 56),
                const SizedBox(
                  width: 26,
                  height: 26,
                  child: CircularProgressIndicator(
                    color: Colors.white,
                    strokeWidth: 2.5,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
