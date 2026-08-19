import 'dart:io';
import 'package:flutter/material.dart';
import '../services/api.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _loading = false;
  bool _showPass = false;

  static const _verdeDark = Color(0xFF1B5E20);
  static const _verdeMain = Color(0xFF2E7D32);
  static const _verdeLight = Color(0xFFE8F5E9);

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    final messenger = ScaffoldMessenger.of(context);
    final navigator = Navigator.of(context);
    setState(() => _loading = true);
    try {
      final api = ApiService();
      await api.login(_emailCtrl.text.trim(), _passCtrl.text);
      if (!mounted) return;
      setState(() => _loading = false);
      final status = await api.getStatusAssinatura();
      if (!mounted) return;
      switch (status) {
        case 'ATIVO':
          navigator.pushReplacementNamed('/dashboard');
        case 'BLOQUEADO':
          navigator.pushReplacementNamed('/pending', arguments: true);
        default: // PENDENTE
          navigator.pushReplacementNamed('/pending');
      }
    } on SocketException {
      setState(() => _loading = false);
      // Tenta entrar com sessão salva (modo offline)
      final api = ApiService();
      final user = await api.getStoredUser();
      final header = await api.getAuthHeader();
      if (!mounted) return;
      if (user != null && header.isNotEmpty) {
        navigator.pushReplacementNamed('/dashboard');
        return;
      }
      messenger.showSnackBar(SnackBar(
        content: const Text('Sem conexão com a internet. Conecte-se para fazer login pela primeira vez.'),
        backgroundColor: Colors.orange.shade800,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 5),
      ));
    } catch (e) {
      setState(() => _loading = false);
      messenger.showSnackBar(SnackBar(
        content: const Text('Email ou senha incorretos'),
        backgroundColor: Colors.red.shade700,
        behavior: SnackBarBehavior.floating,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _verdeLight,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [
              // Header verde com logo
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 40),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [_verdeDark, _verdeMain],
                  ),
                  borderRadius: BorderRadius.only(
                    bottomLeft: Radius.circular(32),
                    bottomRight: Radius.circular(32),
                  ),
                ),
                child: Column(
                  children: [
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.2),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(18),
                        child: Image.asset(
                          'assets/images/banner_datumagro.jpeg',
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'DatumAgro',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 26,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Pecuária de precisão',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.8),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),

              // Formulário
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Entrar na sua conta',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: _verdeDark,
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Campo email
                      TextFormField(
                        key: const Key('login_email'),
                        controller: _emailCtrl,
                        keyboardType: TextInputType.emailAddress,
                        decoration: InputDecoration(
                          labelText: 'Email',
                          prefixIcon: const Icon(Icons.email_outlined, color: _verdeMain),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(color: _verdeMain, width: 2),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                        validator: (v) =>
                            (v == null || !v.contains('@')) ? 'Email inválido' : null,
                      ),

                      const SizedBox(height: 16),

                      // Campo senha
                      TextFormField(
                        key: const Key('login_password'),
                        controller: _passCtrl,
                        obscureText: !_showPass,
                        decoration: InputDecoration(
                          labelText: 'Senha',
                          prefixIcon: const Icon(Icons.lock_outline, color: _verdeMain),
                          suffixIcon: IconButton(
                            icon: Icon(
                              _showPass ? Icons.visibility_off : Icons.visibility,
                              color: Colors.grey,
                            ),
                            onPressed: () => setState(() => _showPass = !_showPass),
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(color: _verdeMain, width: 2),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                        validator: (v) =>
                            (v == null || v.length < 4) ? 'Senha obrigatória' : null,
                      ),

                      const SizedBox(height: 28),

                      // Botão entrar
                      SizedBox(
                        height: 52,
                        child: ElevatedButton(
                          key: const Key('login_button'),
                          onPressed: _loading ? null : _login,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _verdeMain,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            elevation: 2,
                          ),
                          child: _loading
                              ? const SizedBox(
                                  width: 22,
                                  height: 22,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2.5,
                                  ),
                                )
                              : const Text(
                                  'Entrar',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                        ),
                      ),

                      const SizedBox(height: 16),

                      // Link criar conta
                      TextButton(
                        onPressed: () => Navigator.of(context).pushNamed('/register'),
                        child: const Text(
                          'Não tem conta? Criar agora',
                          style: TextStyle(color: _verdeDark, fontWeight: FontWeight.w600),
                        ),
                      ),

                      const SizedBox(height: 32),

                      // Rodapé
                      Text(
                        'Desenvolvido por Nexus AI Tech',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.grey.shade500,
                          letterSpacing: 0.3,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
