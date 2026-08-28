import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api.dart';
import '../config.dart';

class AlertasScreen extends StatefulWidget {
  const AlertasScreen({super.key});

  @override
  State<AlertasScreen> createState() => _AlertasScreenState();
}

class _AlertasScreenState extends State<AlertasScreen>
    with SingleTickerProviderStateMixin {
  static const _vermelho = Color(0xFFE65100);
  final _api = ApiService();

  List<Map<String, dynamic>> _alertas = [];
  bool _loading = true;
  String? _erro;
  late TabController _tabs;

  static const _tipos = ['Todos', 'Sanitário', 'Reprodutivo', 'Desempenho', 'Manejo', 'Genético'];

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
    setState(() {
      _loading = true;
      _erro = null;
    });
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
        setState(() {
          _erro = 'Erro ${resp.statusCode}';
          _loading = false;
        });
      }
    } catch (_) {
      setState(() {
        _erro = 'Sem conexão';
        _loading = false;
      });
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
          const SnackBar(
              content: Text('Alerta resolvido'),
              backgroundColor: Colors.green),
        );
        _load();
      }
    } catch (_) {}
  }

  Future<void> _deletar(int id) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Excluir alerta'),
        content: const Text('Deseja remover este alerta permanentemente?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancelar')),
          TextButton(
              onPressed: () => Navigator.pop(ctx, true),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Excluir')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      final resp = await _api.authenticatedDelete(
        Uri.parse('$kApiBaseUrlEmulator/api/inteligencia/alertas/$id/'),
      );
      if (mounted && (resp.statusCode == 204 || resp.statusCode == 200)) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Alerta excluído')),
        );
        _load();
      }
    } catch (_) {}
  }

  void _abrirFormulario() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _NovoAlertaSheet(
        api: _api,
        onSalvo: () {
          Navigator.pop(ctx);
          _load();
        },
      ),
    );
  }

  List<Map<String, dynamic>> _filtered(int tabIndex) {
    if (tabIndex == 0) return _alertas;
    const map = {
      1: 'SANITARIO',
      2: 'REPRODUTIVO',
      3: 'DESEMPENHO',
      4: 'MANEJO',
      5: 'GENETICO',
    };
    final key = map[tabIndex] ?? '';
    return _alertas.where((a) => (a['tipo_alerta'] ?? '') == key).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Alertas'),
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
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _abrirFormulario,
        backgroundColor: _vermelho,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_alert),
        label: const Text('Novo alerta'),
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
            FilledButton(
                onPressed: _load, child: const Text('Tentar novamente')),
          ],
        ),
      );

  Widget _buildList(List<Map<String, dynamic>> items) {
    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.check_circle_outline,
                size: 56, color: Colors.green.shade300),
            const SizedBox(height: 16),
            Text('Nenhum alerta',
                style: TextStyle(fontSize: 16, color: Colors.grey.shade600)),
            const SizedBox(height: 6),
            Text('Tudo sob controle por aqui.',
                style: TextStyle(fontSize: 13, color: Colors.grey.shade500)),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _abrirFormulario,
              icon: const Icon(Icons.add_alert),
              label: const Text('Criar alerta'),
              style: FilledButton.styleFrom(backgroundColor: _vermelho),
            ),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      itemCount: items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (_, i) => _AlertCard(
        alerta: items[i],
        onResolver: _resolver,
        onDeletar: _deletar,
      ),
    );
  }
}

// ─── Formulário de novo alerta ───────────────────────────────────────────────

class _NovoAlertaSheet extends StatefulWidget {
  final ApiService api;
  final VoidCallback onSalvo;

  const _NovoAlertaSheet({required this.api, required this.onSalvo});

  @override
  State<_NovoAlertaSheet> createState() => _NovoAlertaSheetState();
}

class _NovoAlertaSheetState extends State<_NovoAlertaSheet> {
  static const _vermelho = Color(0xFFE65100);
  final _formKey = GlobalKey<FormState>();
  final _mensagem = TextEditingController();

  String _tipo = 'SANITARIO';
  bool _saving = false;

  static const _tiposOpcoes = [
    ('SANITARIO', 'Sanitário', Icons.vaccines, Color(0xFFD32F2F)),
    ('REPRODUTIVO', 'Reprodutivo', Icons.favorite, Color(0xFFAD1457)),
    ('DESEMPENHO', 'Desempenho', Icons.speed, Color(0xFFE65100)),
    ('MANEJO', 'Manejo', Icons.handyman, Color(0xFF1565C0)),
    ('GENETICO', 'Genético', Icons.biotech, Color(0xFF6A1B9A)),
  ];

  @override
  void dispose() {
    _mensagem.dispose();
    super.dispose();
  }

  Future<void> _salvar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    try {
      final resp = await widget.api.authenticatedPost(
        Uri.parse('$kApiBaseUrlEmulator/api/inteligencia/alertas/'),
        {'tipo_alerta': _tipo, 'mensagem': _mensagem.text.trim()},
      );
      if (!mounted) return;
      if (resp.statusCode == 201) {
        widget.onSalvo();
      } else {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Erro ${resp.statusCode}: ${resp.body}'),
          backgroundColor: Colors.red,
        ));
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Sem conexão: $e'),
        backgroundColor: Colors.red,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottom = MediaQuery.of(context).viewInsets.bottom;
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: EdgeInsets.fromLTRB(20, 16, 20, 20 + bottom),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle
            Center(
              child: Container(
                width: 40, height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Icon(Icons.add_alert, color: _vermelho),
                const SizedBox(width: 10),
                const Text('Novo Alerta',
                    style: TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 20),

            // Tipo — chips scrolláveis
            const Text('Tipo de alerta',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
                    color: Colors.black54)),
            const SizedBox(height: 8),
            SizedBox(
              height: 44,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: _tiposOpcoes.map((opt) {
                  final (value, label, icon, cor) = opt;
                  final selected = _tipo == value;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      avatar: Icon(icon,
                          size: 16,
                          color: selected ? Colors.white : cor),
                      label: Text(label),
                      selected: selected,
                      onSelected: (_) => setState(() => _tipo = value),
                      selectedColor: cor,
                      labelStyle: TextStyle(
                        color: selected ? Colors.white : Colors.black87,
                        fontWeight: selected
                            ? FontWeight.bold
                            : FontWeight.normal,
                      ),
                      showCheckmark: false,
                    ),
                  );
                }).toList(),
              ),
            ),

            const SizedBox(height: 16),

            // Mensagem
            TextFormField(
              controller: _mensagem,
              decoration: InputDecoration(
                labelText: 'Descrição do alerta',
                hintText: 'Ex: Animal #042 com sintomas de tristeza parasitária',
                prefixIcon: Icon(Icons.notes_outlined, color: _vermelho),
                border:
                    OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                filled: true,
                fillColor: const Color(0xFFF5F5F5),
              ),
              maxLines: 3,
              minLines: 2,
              textCapitalization: TextCapitalization.sentences,
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Descreva o alerta' : null,
            ),

            const SizedBox(height: 20),

            FilledButton.icon(
              onPressed: _saving ? null : _salvar,
              style: FilledButton.styleFrom(
                backgroundColor: _vermelho,
                minimumSize: const Size.fromHeight(50),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              icon: _saving
                  ? const SizedBox(
                      width: 18, height: 18,
                      child: CircularProgressIndicator(
                          color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check),
              label: Text(_saving ? 'Salvando...' : 'Criar alerta',
                  style: const TextStyle(
                      fontSize: 15, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Card de alerta ──────────────────────────────────────────────────────────

class _AlertCard extends StatelessWidget {
  final Map<String, dynamic> alerta;
  final Future<void> Function(int) onResolver;
  final Future<void> Function(int) onDeletar;

  const _AlertCard({
    required this.alerta,
    required this.onResolver,
    required this.onDeletar,
  });

  static const _tipoInfo = {
    'SANITARIO':   ('Sanitário',   Color(0xFFD32F2F), Icons.vaccines),
    'REPRODUTIVO': ('Reprodutivo', Color(0xFFAD1457), Icons.favorite),
    'DESEMPENHO':  ('Desempenho',  Color(0xFFE65100), Icons.speed),
    'MANEJO':      ('Manejo',      Color(0xFF1565C0), Icons.handyman),
    'GENETICO':    ('Genético',    Color(0xFF6A1B9A), Icons.biotech),
  };

  static const _statusInfo = {
    'PENDENTE':    ('Pendente',  Color(0xFFE65100)),
    'VISUALIZADO': ('Visto',     Color(0xFF1976D2)),
    'RESOLVIDO':   ('Resolvido', Color(0xFF2E7D32)),
  };

  @override
  Widget build(BuildContext context) {
    final tipo = alerta['tipo_alerta'] as String? ?? '';
    final st = alerta['status'] as String? ?? '';
    final mensagem = alerta['mensagem'] as String? ?? '';
    final criacao = alerta['data_criacao'] as String? ?? '';
    final animalBrinco = alerta['animal_brinco'] as String?;
    final id = alerta['id'] as int? ?? 0;
    final resolvido = st == 'RESOLVIDO';

    final (tipoLabel, tipoColor, tipoIcon) =
        _tipoInfo[tipo] ?? ('Alerta', const Color(0xFF757575), Icons.warning_amber);
    final (statusLabel, statusColor) =
        _statusInfo[st] ?? ('?', Colors.grey);

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
            // Cabeçalho
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
                      style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: tipoColor,
                          fontSize: 14)),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                        color: statusColor.withValues(alpha: 0.4)),
                  ),
                  child: Text(statusLabel,
                      style: TextStyle(
                          fontSize: 11,
                          color: statusColor,
                          fontWeight: FontWeight.w600)),
                ),
              ],
            ),

            // Animal vinculado
            if (animalBrinco != null && animalBrinco.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(children: [
                  Icon(Icons.pets, size: 13, color: Colors.grey.shade500),
                  const SizedBox(width: 4),
                  Text('Animal: $animalBrinco',
                      style: TextStyle(
                          fontSize: 12, color: Colors.grey.shade600)),
                ]),
              ),

            const SizedBox(height: 10),

            // Mensagem
            Text(
              mensagem,
              style: TextStyle(
                fontSize: 14,
                height: 1.4,
                color: resolvido
                    ? Colors.grey.shade500
                    : Colors.grey.shade800,
                decoration: resolvido ? TextDecoration.lineThrough : null,
              ),
            ),

            const SizedBox(height: 10),

            // Rodapé: data + ações
            Row(
              children: [
                Icon(Icons.access_time,
                    size: 12, color: Colors.grey.shade400),
                const SizedBox(width: 4),
                Text(
                  criacao.length >= 10
                      ? criacao.substring(0, 10)
                      : criacao,
                  style: TextStyle(
                      fontSize: 11, color: Colors.grey.shade500),
                ),
                const Spacer(),
                if (!resolvido)
                  TextButton.icon(
                    onPressed: () => onResolver(id),
                    icon: const Icon(Icons.check_circle_outline, size: 16),
                    label: const Text('Resolver',
                        style: TextStyle(fontSize: 13)),
                    style: TextButton.styleFrom(
                        foregroundColor: Colors.green.shade700),
                  ),
                IconButton(
                  icon: Icon(Icons.delete_outline,
                      size: 18, color: Colors.red.shade300),
                  tooltip: 'Excluir',
                  onPressed: () => onDeletar(id),
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
