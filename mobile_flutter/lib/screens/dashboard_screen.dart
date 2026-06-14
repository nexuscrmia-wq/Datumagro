import 'package:flutter/material.dart';
import '../services/api.dart';
import 'romaneio_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _kpis;
  Map<String, dynamic>? _user;
  bool _loading = true;
  String? _erro;

  static const _verde = Color(0xFF2E7D32);

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _erro = null;
    });
    try {
      final api = ApiService();
      final kpis = await api.fetchDashboard();
      final user = await api.fetchMe();
      if (!mounted) return;
      setState(() {
        _kpis = kpis;
        _user = user;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _erro = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _logout() async {
    await ApiService().logout();
    if (!mounted) return;
    Navigator.of(context).pushReplacementNamed('/login');
  }

  @override
  Widget build(BuildContext context) {
    final nome = _user?['nome_completo'] as String? ??
        (_user?['email'] as String?)?.split('@').first ??
        'Produtor';
    final tipo = _user?['tipo_usuario'] as String? ?? '';

    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: const Text('DatumAgro', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.scale),
            tooltip: 'Romaneio de Pesagem',
            onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const RomaneioScreen())),
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: 'Perfil',
            onPressed: () => Navigator.of(context).pushNamed('/profile'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sair',
            onPressed: _logout,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        color: _verde,
        child: _loading
            ? const Center(child: CircularProgressIndicator(color: _verde))
            : _erro != null
                ? _buildError()
                : _buildContent(nome, tipo),
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.wifi_off, size: 56, color: Colors.grey),
          const SizedBox(height: 12),
          const Text('Sem conexão com o servidor',
              style: TextStyle(fontSize: 16, color: Colors.grey)),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32)),
            onPressed: _load,
            icon: const Icon(Icons.refresh, color: Colors.white),
            label: const Text('Tentar novamente',
                style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Widget _buildContent(String nome, String tipo) {
    final kpis = _kpis ?? {};
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header de boas-vindas
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: _verde,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Row(
            children: [
              CircleAvatar(
                backgroundColor: Colors.white.withValues(alpha: 0.2),
                radius: 26,
                child: const Icon(Icons.person, color: Colors.white, size: 28),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Olá, $nome!',
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold)),
                    const SizedBox(height: 2),
                    Text(
                      tipo == 'proprietario'
                          ? 'Proprietário'
                          : tipo == 'gerente'
                              ? 'Gerente'
                              : 'Funcionário',
                      style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.8),
                          fontSize: 13),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),
        const Text('Visão Geral',
            style: TextStyle(
                fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
        const SizedBox(height: 12),

        // Grid de KPIs
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.4,
          children: [
            _KpiCard(
              label: 'Animais Ativos',
              value: '${kpis['total_animais'] ?? 0}',
              icon: Icons.pets,
              color: const Color(0xFF2E7D32),
            ),
            _KpiCard(
              label: 'Pesagens Hoje',
              value: '${kpis['pesagens_hoje'] ?? 0}',
              icon: Icons.monitor_weight,
              color: const Color(0xFF1565C0),
            ),
            _KpiCard(
              label: 'Alertas Críticos',
              value: '${kpis['alertas_criticos'] ?? 0}',
              icon: Icons.warning_amber,
              color: (kpis['alertas_criticos'] ?? 0) > 0
                  ? const Color(0xFFB71C1C)
                  : const Color(0xFF558B2F),
            ),
            _KpiCard(
              label: 'Nascimentos/Mês',
              value: '${kpis['nascimentos_mes'] ?? 0}',
              icon: Icons.child_care,
              color: const Color(0xFF6A1B9A),
            ),
            _KpiCard(
              label: 'Manejos (7 dias)',
              value: '${kpis['proximos_manejos_7_dias'] ?? 0}',
              icon: Icons.medical_services,
              color: const Color(0xFFE65100),
            ),
            _KpiCard(
              label: 'Embarques Ativos',
              value: '${kpis['embarques_ativos'] ?? 0}',
              icon: Icons.local_shipping,
              color: const Color(0xFF00695C),
            ),
          ],
        ),

        const SizedBox(height: 24),
        const Text('Ações Rápidas',
            style: TextStyle(
                fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
        const SizedBox(height: 12),

        Row(
          children: [
            Expanded(
              child: _ActionButton(
                label: 'Animais',
                icon: Icons.pets,
                onTap: () => Navigator.of(context).pushNamed('/animals'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                label: 'Romaneio',
                icon: Icons.scale,
                onTap: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const RomaneioScreen())),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color color;

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
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Icon(icon, color: color, size: 26),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(value,
                  style: TextStyle(
                      fontSize: 26, fontWeight: FontWeight.bold, color: color)),
              Text(label,
                  style: const TextStyle(fontSize: 11, color: Colors.black54),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis),
            ],
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  const _ActionButton({required this.label, required this.icon, required this.onTap});

  final String label;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFA5D6A7)),
        ),
        child: Column(
          children: [
            Icon(icon, color: const Color(0xFF2E7D32), size: 28),
            const SizedBox(height: 6),
            Text(label,
                style: const TextStyle(
                    fontWeight: FontWeight.w600, color: Color(0xFF2E7D32))),
          ],
        ),
      ),
    );
  }
}
