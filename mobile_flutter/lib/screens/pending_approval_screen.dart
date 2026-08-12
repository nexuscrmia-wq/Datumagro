import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api.dart';

class PendingApprovalScreen extends StatefulWidget {
  final bool bloqueado;
  const PendingApprovalScreen({super.key, this.bloqueado = false});

  @override
  State<PendingApprovalScreen> createState() => _PendingApprovalScreenState();
}

class _PendingApprovalScreenState extends State<PendingApprovalScreen> {
  static const _verde = Color(0xFF2E7D32);
  static const _whatsapp = Color(0xFF25D366);
  static const _laranja = Color(0xFFE65100);
  static const _vermelho = Color(0xFFB71C1C);

  final _api = ApiService();
  bool _verificando = false;
  String? _email;

  @override
  void initState() {
    super.initState();
    _loadEmail();
  }

  Future<void> _loadEmail() async {
    final user = await _api.getStoredUser();
    if (mounted && user != null) {
      setState(() => _email = user['email'] as String?);
    }
  }

  Future<void> _verificarLiberacao() async {
    setState(() => _verificando = true);
    try {
      final status = await _api.verificarStatusAssinatura();
      if (!mounted) return;
      setState(() => _verificando = false);

      if (status == 'ATIVO') {
        Navigator.of(context).pushReplacementNamed('/dashboard');
      } else if (status == 'BLOQUEADO') {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
              builder: (_) => const PendingApprovalScreen(bloqueado: true)),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Conta ainda em análise. Aguarde a aprovação.'),
          behavior: SnackBarBehavior.floating,
        ));
      }
    } catch (_) {
      if (mounted) setState(() => _verificando = false);
    }
  }

  Future<void> _abrirWhatsApp() async {
    final msg = Uri.encodeComponent(
        'Olá! Acabei de fazer meu cadastro no DatumAgro com o e-mail $_email e gostaria de liberar meu acesso.');
    final url = Uri.parse('https://wa.me/5522988330445?text=$msg');
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  Future<void> _logout() async {
    await _api.logout();
    if (!mounted) return;
    Navigator.of(context).pushReplacementNamed('/login');
  }

  @override
  Widget build(BuildContext context) {
    final bloqueado = widget.bloqueado;
    final corPrincipal = bloqueado ? _vermelho : _laranja;
    final icone = bloqueado ? Icons.block : Icons.lock_clock;
    final titulo = bloqueado
        ? 'Acesso Bloqueado'
        : 'Aguardando Liberação';
    final subtitulo = bloqueado
        ? 'Sua conta foi bloqueada. Entre em contato com nossa equipe para mais informações.'
        : 'Sua conta está em análise. Para ativar o acesso completo, fale com nossa equipe no WhatsApp e finalize a escolha do seu plano.';

    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            children: [
              const Spacer(),

              // Ícone animado
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: corPrincipal.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: corPrincipal.withValues(alpha: 0.3), width: 2),
                ),
                child: Icon(icone, color: corPrincipal, size: 48),
              ),

              const SizedBox(height: 28),

              Text(
                titulo,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B2A22),
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 14),

              Text(
                subtitulo,
                style: const TextStyle(
                  fontSize: 14,
                  color: Color(0xFF546E5A),
                  height: 1.6,
                ),
                textAlign: TextAlign.center,
              ),

              if (_email != null) ...[
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFFCDE8D4)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.email_outlined, size: 16, color: _verde),
                      const SizedBox(width: 8),
                      Text(
                        _email!,
                        style: const TextStyle(
                          color: _verde,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              const Spacer(),

              // Botão WhatsApp
              if (!bloqueado) ...[
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _whatsapp,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      elevation: 0,
                    ),
                    onPressed: _abrirWhatsApp,
                    icon: const Icon(Icons.chat, size: 20),
                    label: const Text(
                      'Falar com Suporte no WhatsApp',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ),
                ),

                const SizedBox(height: 12),

                // Botão Verificar Liberação
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _verde,
                      side: const BorderSide(color: _verde),
                      padding: const EdgeInsets.symmetric(vertical: 15),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: _verificando ? null : _verificarLiberacao,
                    icon: _verificando
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: _verde))
                        : const Icon(Icons.refresh, size: 20),
                    label: Text(
                      _verificando ? 'Verificando...' : 'Verificar Liberação',
                      style: const TextStyle(
                          fontWeight: FontWeight.w600, fontSize: 15),
                    ),
                  ),
                ),
              ],

              if (bloqueado) ...[
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _whatsapp,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      elevation: 0,
                    ),
                    onPressed: _abrirWhatsApp,
                    icon: const Icon(Icons.chat, size: 20),
                    label: const Text(
                      'Contatar Suporte',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ),
                ),
              ],

              const SizedBox(height: 12),

              TextButton(
                onPressed: _logout,
                child: const Text(
                  'Sair da conta',
                  style: TextStyle(color: Colors.grey, fontSize: 13),
                ),
              ),

              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}
