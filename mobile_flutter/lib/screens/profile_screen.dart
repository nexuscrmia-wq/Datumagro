import 'package:flutter/material.dart';
import '../services/api.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  bool _loading = true;

  static const _verde = Color(0xFF2E7D32);

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    final user = await ApiService().fetchMe();
    if (!mounted) return;
    setState(() {
      _user = user;
      _loading = false;
    });
  }

  Future<void> _logout() async {
    await ApiService().logout();
    if (!mounted) return;
    Navigator.of(context).pushReplacementNamed('/login');
  }

  void _showDeleteDialog() {
    final passCtrl = TextEditingController();
    bool deleting = false;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setInner) => AlertDialog(
          title: const Text('Excluir Conta',
              style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Esta ação é irreversível. Seus dados serão anonimizados '
                'conforme a LGPD e sua conta será desativada permanentemente.',
                style: TextStyle(fontSize: 13),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: passCtrl,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Confirme sua senha',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock_outline),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: deleting ? null : () => Navigator.of(ctx).pop(),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              onPressed: deleting
                  ? null
                  : () async {
                      if (passCtrl.text.isEmpty) return;
                      final messenger = ScaffoldMessenger.of(context);
                      final navigator = Navigator.of(context);
                      setInner(() => deleting = true);
                      final ok = await ApiService().deleteAccount(passCtrl.text);
                      if (!ctx.mounted) return;
                      Navigator.of(ctx).pop();
                      if (ok) {
                        await ApiService().logout();
                        navigator.pushReplacementNamed('/login');
                        messenger.showSnackBar(
                          const SnackBar(
                              content: Text('Conta excluída com sucesso.'),
                              backgroundColor: Colors.green),
                        );
                      } else {
                        messenger.showSnackBar(
                          const SnackBar(
                              content: Text('Senha incorreta. Tente novamente.'),
                              backgroundColor: Colors.red),
                        );
                      }
                    },
              child: deleting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          color: Colors.white, strokeWidth: 2))
                  : const Text('Excluir',
                      style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: const Text('Meu Perfil', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _verde))
          : ListView(
              padding: const EdgeInsets.all(20),
              children: [
                // Avatar e nome
                Center(
                  child: Column(
                    children: [
                      Container(
                        width: 80,
                        height: 80,
                        decoration: const BoxDecoration(
                          color: _verde,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.person, size: 44, color: Colors.white),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _user?['nome_completo'] as String? ??
                            (_user?['email'] as String?)?.split('@').first ??
                            'Usuário',
                        style: const TextStyle(
                            fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      _TypeBadge(_user?['tipo_usuario'] as String? ?? ''),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // Informações
                _SectionCard(
                  children: [
                    _InfoRow(Icons.email_outlined, 'E-mail',
                        _user?['email'] as String? ?? '—'),
                    const Divider(height: 1),
                    _InfoRow(Icons.phone_outlined, 'Telefone',
                        _user?['telefone'] as String? ?? 'Não informado'),
                  ],
                ),

                const SizedBox(height: 16),

                // Permissões
                if (_user?['permissoes'] is Map) ...[
                  _SectionCard(
                    title: 'Permissões',
                    children: [
                      for (final entry
                          in (_user!['permissoes'] as Map).entries)
                        _PermRow(entry.key as String, entry.value == true),
                    ],
                  ),
                  const SizedBox(height: 16),
                ],

                // Ações
                _SectionCard(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.logout, color: _verde),
                      title: const Text('Sair da conta'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: _logout,
                    ),
                    const Divider(height: 1),
                    ListTile(
                      leading: const Icon(Icons.delete_forever, color: Colors.red),
                      title: const Text('Excluir minha conta',
                          style: TextStyle(color: Colors.red)),
                      subtitle: const Text('Ação irreversível · LGPD',
                          style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.chevron_right, color: Colors.red),
                      onTap: _showDeleteDialog,
                    ),
                  ],
                ),

                const SizedBox(height: 24),
                const Center(
                  child: Text('DatumAgro v1.0',
                      style: TextStyle(color: Colors.black38, fontSize: 12)),
                ),
              ],
            ),
    );
  }
}

class _TypeBadge extends StatelessWidget {
  const _TypeBadge(this.tipo);
  final String tipo;

  @override
  Widget build(BuildContext context) {
    final label = tipo == 'proprietario'
        ? 'Proprietário'
        : tipo == 'gerente'
            ? 'Gerente'
            : 'Funcionário';
    final color = tipo == 'proprietario'
        ? const Color(0xFF2E7D32)
        : tipo == 'gerente'
            ? const Color(0xFF1565C0)
            : const Color(0xFF6A1B9A);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(label,
          style: TextStyle(
              color: color, fontWeight: FontWeight.w600, fontSize: 13)),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.children, this.title});
  final List<Widget> children;
  final String? title;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (title != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              child: Text(title!,
                  style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2E7D32),
                      fontSize: 13)),
            ),
          ...children,
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow(this.icon, this.label, this.value);
  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: const Color(0xFF2E7D32)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: const TextStyle(fontSize: 11, color: Colors.black54)),
                Text(value,
                    style: const TextStyle(
                        fontSize: 14, fontWeight: FontWeight.w500)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PermRow extends StatelessWidget {
  const _PermRow(this.key_, this.enabled);
  final String key_;
  final bool enabled;

  static const _labels = {
    'can_view_animais': 'Ver animais',
    'can_edit_animais': 'Editar animais',
    'can_view_financeiro': 'Ver financeiro',
    'can_edit_financeiro': 'Editar financeiro',
    'can_view_relatorios': 'Ver relatórios',
    'can_manage_usuarios': 'Gerenciar equipe',
    'can_delete_dados': 'Excluir dados',
    'can_manage_lotes': 'Gerenciar lotes',
    'can_view_vacinas': 'Ver vacinas',
    'can_edit_vacinas': 'Editar vacinas',
    'can_view_alertas': 'Ver alertas',
    'can_view_propriedades': 'Ver propriedades',
  };

  @override
  Widget build(BuildContext context) {
    final label = _labels[key_] ?? key_;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Row(
        children: [
          Icon(
            enabled ? Icons.check_circle : Icons.cancel_outlined,
            size: 18,
            color: enabled ? const Color(0xFF2E7D32) : Colors.red.shade300,
          ),
          const SizedBox(width: 10),
          Text(label, style: const TextStyle(fontSize: 13)),
        ],
      ),
    );
  }
}
