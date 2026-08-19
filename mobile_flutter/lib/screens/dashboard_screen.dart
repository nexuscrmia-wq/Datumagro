import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api.dart';
import '../config.dart';
import '../ajuda/ajuda_bottom_sheet.dart';
import '../ajuda/ajuda_service.dart';
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
  bool _offline = false;

  static bool _versionChecked = false;
  static const _verde = Color(0xFF2E7D32);

  final _ajudaService = AjudaService(ApiService());

  @override
  void initState() {
    super.initState();
    _load();
    if (!_versionChecked) {
      _versionChecked = true;
      // Aguarda o frame estar pronto antes de exibir qualquer dialog
      WidgetsBinding.instance.addPostFrameCallback((_) => _checkVersion());
    }
  }

  // ─── Verificação de atualização ──────────────────────────────────────────

  Future<void> _checkVersion() async {
    try {
      final info = await ApiService().fetchVersaoApp();
      if (!mounted) return;
      final serverVersion = info['versao'] as String? ?? '';
      final obrigatorio = info['obrigatorio'] as bool? ?? false;
      final novidades = info['novidades'] as String? ?? '';
      final urlDownload = info['url_download'] as String? ?? '';
      if (_isNewerVersion(serverVersion, kAppVersion)) {
        _showUpdateDialog(
          versao: serverVersion,
          obrigatorio: obrigatorio,
          novidades: novidades,
          urlDownload: urlDownload,
        );
      }
    } catch (_) {
      // Falha silenciosa — conectividade não impede o dashboard de funcionar
    }
  }

  List<int> _parseVersion(String v) =>
      v.split('.').map((p) => int.tryParse(p) ?? 0).toList();

  bool _isNewerVersion(String server, String current) {
    final s = _parseVersion(server);
    final c = _parseVersion(current);
    for (int i = 0; i < 3; i++) {
      final sv = i < s.length ? s[i] : 0;
      final cv = i < c.length ? c[i] : 0;
      if (sv > cv) return true;
      if (sv < cv) return false;
    }
    return false;
  }

  void _showUpdateDialog({
    required String versao,
    required bool obrigatorio,
    required String novidades,
    required String urlDownload,
  }) {
    showDialog<void>(
      context: context,
      barrierDismissible: !obrigatorio,
      builder: (ctx) => PopScope(
        canPop: !obrigatorio,
        child: AlertDialog(
          icon: Icon(
            obrigatorio ? Icons.system_update : Icons.system_update_alt,
            color: _verde,
            size: 40,
          ),
          title: Text(
            obrigatorio ? 'Atualização obrigatória' : 'Nova versão disponível',
            textAlign: TextAlign.center,
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Versão $versao disponível.\nVocê está usando $kAppVersion.',
                style: const TextStyle(fontSize: 14),
              ),
              if (novidades.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Text(
                    novidades,
                    style: const TextStyle(fontSize: 13, height: 1.5),
                  ),
                ),
              ],
              if (obrigatorio) ...[
                const SizedBox(height: 12),
                const Text(
                  'Esta versão não é mais suportada. Atualize para continuar usando o DatumAgro.',
                  style: TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
              ],
            ],
          ),
          actions: [
            if (!obrigatorio)
              TextButton(
                onPressed: () => Navigator.of(ctx).pop(),
                child: const Text('Agora não'),
              ),
            FilledButton.icon(
              icon: const Icon(Icons.download_rounded, size: 18),
              label: const Text('Baixar atualização'),
              style: FilledButton.styleFrom(backgroundColor: _verde),
              onPressed: () async {
                final uri = Uri.parse(urlDownload);
                if (await canLaunchUrl(uri)) {
                  await launchUrl(uri, mode: LaunchMode.externalApplication);
                }
                if (!obrigatorio && ctx.mounted) {
                  Navigator.of(ctx).pop();
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _erro = null;
    });
    try {
      final api = ApiService();
      final offline = await api.isOffline();
      final kpis = await api.fetchDashboard();
      final user = await api.fetchMe();
      if (!mounted) return;
      setState(() {
        _kpis = kpis;
        _user = user;
        _offline = offline;
        _loading = false;
        // Se não tem dados nem online nem cache, mostra erro
        _erro = (kpis.isEmpty && user == null) ? 'sem_internet' : null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _erro = 'sem_internet';
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
            icon: const Icon(Icons.help_outline),
            tooltip: 'Ajuda',
            onPressed: () => mostrarAjuda(context,
                service: _ajudaService, moduloSlug: 'dashboard'),
          ),
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
                : Column(
                    children: [
                      if (_offline)
                        Container(
                          width: double.infinity,
                          color: Colors.orange.shade700,
                          padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
                          child: const Row(
                            children: [
                              Icon(Icons.wifi_off, color: Colors.white, size: 16),
                              SizedBox(width: 8),
                              Text('Modo offline — exibindo dados salvos',
                                  style: TextStyle(color: Colors.white, fontSize: 13)),
                            ],
                          ),
                        ),
                      Expanded(child: _buildContent(nome, tipo)),
                    ],
                  ),
      ),
    );
  }

  Widget _buildError() {
    final semInternet = _erro == 'sem_internet';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(semInternet ? Icons.wifi_off : Icons.cloud_off,
                size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              semInternet ? 'Sem conexão com a internet' : 'Sem conexão com o servidor',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.black87),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              semInternet
                  ? 'O DatumAgro precisa de internet para funcionar.\nConecte-se ao Wi-Fi ou ative os dados móveis e tente novamente.'
                  : 'Verifique sua conexão e tente novamente.',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32)),
              onPressed: _load,
              icon: const Icon(Icons.refresh, color: Colors.white),
              label: const Text('Tentar novamente', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
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

        const SizedBox(height: 16),

        // Card GMD em destaque
        _GmdCard(gmdMedioHoje: kpis['gmd_medio_hoje'] as double?),

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
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                label: 'Mapa',
                icon: Icons.map_outlined,
                color: const Color(0xFF1565C0),
                onTap: () => Navigator.of(context).pushNamed('/mapa'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                label: 'Planos',
                icon: Icons.star_outline,
                color: const Color(0xFFF9A825),
                onTap: () => Navigator.of(context).pushNamed('/planos'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _ActionButton(
                label: 'Financeiro',
                icon: Icons.account_balance_wallet_outlined,
                color: const Color(0xFF00695C),
                onTap: () => Navigator.of(context).pushNamed('/financeiro'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                label: 'Equipe',
                icon: Icons.group_outlined,
                color: const Color(0xFF6A1B9A),
                onTap: () => Navigator.of(context).pushNamed('/equipe'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                label: 'Alertas',
                icon: Icons.notifications_outlined,
                color: const Color(0xFFE65100),
                onTap: () => Navigator.of(context).pushNamed('/alertas'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _ActionButton(
                label: 'Logística',
                icon: Icons.local_shipping_outlined,
                color: const Color(0xFF37474F),
                onTap: () => Navigator.of(context).pushNamed('/logistica'),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _GmdCard extends StatelessWidget {
  final double? gmdMedioHoje;

  const _GmdCard({this.gmdMedioHoje});

  @override
  Widget build(BuildContext context) {
    final hasData = gmdMedioHoje != null;
    final isPositive = (gmdMedioHoje ?? 0) >= 0;
    final color = hasData
        ? (isPositive ? const Color(0xFF2E7D32) : const Color(0xFFB71C1C))
        : const Color(0xFF546E7A);
    final sign = hasData && isPositive ? '+' : '';
    final valueText = hasData
        ? '$sign${gmdMedioHoje!.toStringAsFixed(2)} kg/dia'
        : '—';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withAlpha(80)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withAlpha(30),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.trending_up, color: color, size: 26),
          ),
          const SizedBox(width: 14),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'GMD Médio Hoje',
                style: TextStyle(
                    fontSize: 12,
                    color: color,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.3),
              ),
              Text(
                valueText,
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: color),
              ),
            ],
          ),
          const Spacer(),
          if (!hasData)
            Text('Sem pesagens\nhoje',
                style: TextStyle(fontSize: 11, color: color),
                textAlign: TextAlign.right),
        ],
      ),
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
  const _ActionButton(
      {required this.label,
      required this.icon,
      required this.onTap,
      this.color});

  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final c = color ?? const Color(0xFF2E7D32);
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: c.withValues(alpha: 0.4)),
        ),
        child: Column(
          children: [
            Icon(icon, color: c, size: 28),
            const SizedBox(height: 6),
            Text(label,
                style: TextStyle(fontWeight: FontWeight.w600, color: c)),
          ],
        ),
      ),
    );
  }
}
