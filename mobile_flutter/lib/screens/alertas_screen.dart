import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api.dart';
import '../config.dart';

class AlertasScreen extends StatefulWidget {
  const AlertasScreen({super.key});

  @override
  State<AlertasScreen> createState() => _AlertasScreenState();
}

class _AlertasScreenState extends State<AlertasScreen> with SingleTickerProviderStateMixin {
  static const _vermelho = Color(0xFFE65100);
  final _api = ApiService();

  List<Map<String, dynamic>> _alertas = [];
  bool _loading = true;
  String? _erro;
  late TabController _tabs;

  static const _tipos = ['Todos', 'Sanitário', 'Reprodutivo', 'Desempenho', 'Manejo'];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: _tipos.length, vsync: this);
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _erro = null; });
    try {
      final resp = await _api.authenticatedGet(
        Uri.parse('$kApiBaseUrlEmulator/api/inteligencia/alertas/'),
      );
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body);
        final list = data is List ? data : (data['results'] ?? []);
        setState(() {
          _alertas = List<Map<String, dynamic>>.from(list);
          _loading = false;
        });
      } else {
        setState(() { _erro = 'Erro ${resp.statusCode}'; _loading = false; });
      }
    } catch (_) {
      setState(() { _erro = 'Sem conexão'; _loading = false; });
    }
  }

  Future<void> _resolver(int id) async {
    try {
      final resp = await _api.authenticatedPost(
        Uri.parse('$kApiBaseUrlEmulator/api/inteligencia/alertas/$id/marcar_como_resolvido/'),
        {},
      );
      if (mounted && resp.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Alerta resolvido'), backgroundColor: Colors.green),
        );
        _load();
      }
    } catch (_) {}
  }

  List<Map<String, dynamic>> _filtered(int tabIndex) {
    if (tabIndex == 0) return _alertas;
    final map = {1: 'SANITARIO', 2: 'REPRODUTIVO', 3: 'DESEMPENHO', 4: 'MANEJO'};
    final key = map[tabIndex] ?? '';
    return _alertas.where((a) => (a['tipo_alerta'] ?? '') == key).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Alertas e IA'),
        backgroundColor: _vermelho,
        foregroundColor: Colors.white,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
        bottom: TabBar(
          controller: _tabs,
          isScrollable: true,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.white,
          tabs: _tipos.map((t) => Tab(text: t)).toList(),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _erro != null
              ? _buildError()
              : TabBarView(
                  controller: _tabs,
                  children: List.generate(
                    _tipos.length,
                    (i) => _buildList(_filtered(i)),
                  ),
                ),
    );
  }

  Widget _buildError() => Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.wifi_off, size: 48, color: Colors.grey.shade400),
        const SizedBox(height: 12),
        Text(_erro!, style: TextStyle(color: Colors.grey.shade600)),
        const SizedBox(height: 16),
        FilledButton(onPressed: _load, child: const Text('Tentar novamente')),
      ],
    ),
  );

  Widget _buildList(List<Map<String, dynamic>> items) {
    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.check_circle_outline, size: 56, color: Colors.green.shade300),
            const SizedBox(height: 16),
            Text('Nenhum alerta', style: TextStyle(fontSize: 16, color: Colors.grey.shade600)),
            const SizedBox(height: 6),
            Text('Tudo sob controle por aqui.',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade500)),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (_, i) => _AlertCard(alerta: items[i], onResolver: _resolver),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final Map<String, dynamic> alerta;
  final Future<void> Function(int) onResolver;

  const _AlertCard({required this.alerta, required this.onResolver});

  static const _tipoInfo = {
    'SANITARIO':    ('Sanitário',    Color(0xFFD32F2F), Icons.vaccines),
    'REPRODUTIVO':  ('Reprodutivo',  Color(0xFFAD1457), Icons.favorite),
    'DESEMPENHO':   ('Desempenho',   Color(0xFFE65100), Icons.speed),
    'MANEJO':       ('Manejo',       Color(0xFF1565C0), Icons.handyman),
    'GENETICO':     ('Genético',     Color(0xFF6A1B9A), Icons.biotech),
  };

  static const _statusInfo = {
    'PENDENTE':     ('Pendente',    Color(0xFFE65100)),
    'VISUALIZADO':  ('Visto',       Color(0xFF1976D2)),
    'RESOLVIDO':    ('Resolvido',   Color(0xFF2E7D32)),
  };

  @override
  Widget build(BuildContext context) {
    final tipo = alerta['tipo_alerta'] as String? ?? '';
    final status = alerta['status'] as String? ?? '';
    final mensagem = alerta['mensagem'] as String? ?? '';
    final criacao = alerta['data_criacao'] as String? ?? '';
    final id = alerta['id'] as int? ?? 0;
    final resolvido = status == 'RESOLVIDO';

    final (tipoLabel, tipoColor, tipoIcon) = _tipoInfo[tipo] ?? ('Alerta', const Color(0xFF757575), Icons.warning_amber);
    final (statusLabel, statusColor) = _statusInfo[status] ?? ('?', Colors.grey);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: tipoColor.withValues(alpha: 0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: tipoColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(tipoIcon, size: 18, color: tipoColor),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(tipoLabel,
                    style: TextStyle(fontWeight: FontWeight.bold, color: tipoColor, fontSize: 14)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: statusColor.withValues(alpha: 0.4)),
                  ),
                  child: Text(statusLabel,
                    style: TextStyle(fontSize: 11, color: statusColor, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(mensagem,
              style: TextStyle(
                fontSize: 14,
                height: 1.4,
                color: resolvido ? Colors.grey.shade500 : Colors.grey.shade800,
                decoration: resolvido ? TextDecoration.lineThrough : null,
              )),
            const SizedBox(height: 10),
            Row(
              children: [
                Icon(Icons.access_time, size: 12, color: Colors.grey.shade400),
                const SizedBox(width: 4),
                Text(
                  criacao.length >= 10 ? criacao.substring(0, 10) : criacao,
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                ),
                const Spacer(),
                if (!resolvido)
                  TextButton.icon(
                    onPressed: () => onResolver(id),
                    icon: const Icon(Icons.check_circle_outline, size: 16),
                    label: const Text('Resolver', style: TextStyle(fontSize: 13)),
                    style: TextButton.styleFrom(foregroundColor: Colors.green.shade700),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
