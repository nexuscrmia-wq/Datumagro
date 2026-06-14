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

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    final messenger = ScaffoldMessenger.of(context);
    final navigator = Navigator.of(context);
    setState(() => _loading = true);
    try {
      await ApiService().login(_emailCtrl.text.trim(), _passCtrl.text);
      setState(() => _loading = false);
      navigator.pushReplacementNamed('/dashboard');
    } catch (e) {
      setState(() => _loading = false);
      messenger.showSnackBar(SnackBar(content: Text('Falha no login: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                  key: const Key('login_email'),
                  controller: _emailCtrl,
                  decoration: const InputDecoration(labelText: 'Email')),
              TextFormField(
                  key: const Key('login_password'),
                  controller: _passCtrl,
                  decoration: const InputDecoration(labelText: 'Senha'),
                  obscureText: true),
              const SizedBox(height: 20),
              ElevatedButton(
                  key: const Key('login_button'),
                  onPressed: _loading ? null : _login,
                  child: _loading
                      ? const CircularProgressIndicator()
                      : const Text('Entrar')),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () =>
                    Navigator.of(context).pushNamed('/register'),
                child: const Text('Não tem conta? Criar agora'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
