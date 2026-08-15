import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api.dart';
import '../config.dart';

class LogisticaScreen extends StatefulWidget {
  const LogisticaScreen({super.key});

  @override
  State<LogisticaScreen> createState() => _LogisticaScreenState();
}

class _LogisticaScreenState extends State<LogisticaScreen> {
  static const _cinza = Color(0xFF37474F);
  final _api = ApiService();

  List<Map<String, dynamic>> _embarques = [];
  bool _loading = true;
  String? _erro;
  String _filtroStatus = 'TODOS';

  static const _statusOpts = [
    ('TODOS', 'Todos'),
    ('PLA', 'Planejado'),
    ('PRE', 'Pré-Embarque'),
    ('NAV', 'Em Trânsito'),
    ('POR', 'No Porto'),
    ('FIN', 'Finalizado'),
    ('CAN', 'Cancelado'),
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _erro = null; });
    try {
      final resp = await _api.authenticatedGet(
        Uri.parse('$kApiBaseUrlEmulator/api/logistica/embarques/'),
      );
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body);
        final list = data is List ? data : (data['results'] ?? []);
        setState(() {
          _embarques = List<Map<String, dynamic>>.from(list);
          _loading = false;
        });
      } else {
        setState(() { _erro = 'Erro ${resp.statusCode}'; _loading = false; });
      }
    } catch (_) {
      setState(() { _erro = 'Sem conexão'; _loading = false; });
    }
  }

  List<Map<String, dynamic>> get _filtered {
    if (_filtroStatus == 'TODOS') return _embarques;
    return _embarques.where((e) => e['status'] == _filtroStatus).toList();
  }

  Future<void> _showNovoEmbarque() async {
    final numeroCtrl = TextEditingController(
        text: 'EMB-${DateTime.now().year}-${(_embarques.length + 1).toString().padLeft(3, '0')}');
    final destinoCtrl = TextEditingController();
    final paisCtrl = TextEditingController();
    final origemCtrl = TextEditingController(text: 'Porto do Açu');
    final navioCtrl = TextEditingController();
    String tipo = 'EXP';
    DateTime dataEmbarque = DateTime.now().add(const Duration(days: 7));
    DateTime dataChegada = DateTime.now().add(const Duration(days: 30));

    final confirmed = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModal) => Padding(
          padding: EdgeInsets.only(
              left: 20, right: 20, top: 20,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 20),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    const Expanded(
                        child: Text('Novo Embarque',
                            style: TextStyle(
                                fontSize: 18, fontWeight: FontWeight.bold))),
                    IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.pop(ctx, false)),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: numeroCtrl,
                  decoration: const InputDecoration(
                      labelText: 'Número do Embarque *',
                      border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: tipo,
                  decoration: const InputDecoration(
                      labelText: 'Tipo *', border: OutlineInputBorder()),
                  items: const [
                    DropdownMenuItem(
                        value: 'EXP', child: Text('Exportação (Saída)')),
                    DropdownMenuItem(
                        value: 'IMP', child: Text('Importação (Entrada)')),
                  ],
                  onChanged: (v) => setModal(() => tipo = v!),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: paisCtrl,
                  decoration: const InputDecoration(
                      labelText: 'País Parceiro *',
                      hintText: 'Ex: Turquia, Egito...',
                      border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: destinoCtrl,
                  decoration: const InputDecoration(
                      labelText: 'Porto de Destino *',
                      hintText: 'Ex: Porto de Istambul',
                      border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: origemCtrl,
                  decoration: const InputDecoration(
                      labelText: 'Porto de Origem',
                      border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: navioCtrl,
                  decoration: const InputDecoration(
                      labelText: 'Navio (opcional)',
                      border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: InkWell(
                        onTap: () async {
                          final d = await showDatePicker(
                            context: ctx,
                            initialDate: dataEmbarque,
                            firstDate: DateTime(2024),
                            lastDate: DateTime(2030),
                          );
                          if (d != null) setModal(() => dataEmbarque = d);
                        },
                        child: InputDecorator(
                          decoration: const InputDecoration(
                              labelText: 'Data Embarque *',
                              border: OutlineInputBorder()),
                          child: Text(
                              '${dataEmbarque.day.toString().padLeft(2, '0')}/${dataEmbarque.month.toString().padLeft(2, '0')}/${dataEmbarque.year}'),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: InkWell(
                        onTap: () async {
                          final d = await showDatePicker(
                            context: ctx,
                            initialDate: dataChegada,
                            firstDate: DateTime(2024),
                            lastDate: DateTime(2030),
                          );
                          if (d != null) setModal(() => dataChegada = d);
                        },
                        child: InputDecorator(
                          decoration: const InputDecoration(
                              labelText: 'Data Chegada *',
                              border: OutlineInputBorder()),
                          child: Text(
                              '${dataChegada.day.toString().padLeft(2, '0')}/${dataChegada.month.toString().padLeft(2, '0')}/${dataChegada.year}'),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    style: FilledButton.styleFrom(
                        backgroundColor: _cinza,
                        padding: const EdgeInsets.symmetric(vertical: 14)),
                    onPressed: () => Navigator.pop(ctx, true),
                    child: const Text('Criar Embarque',
                        style: TextStyle(fontSize: 15)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    if (confirmed != true || !mounted) return;

    if (destinoCtrl.text.trim().isEmpty || paisCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Preencha os campos obrigatórios.')));
      return;
    }

    try {
      final resp = await _api.authenticatedPost(
        Uri.parse('$kApiBaseUrlEmulator/api/logistica/embarques/'),
        {
          'numero_embarque': numeroCtrl.text.trim(),
          'tipo': tipo,
          'porto_destino': destinoCtrl.text.trim(),
          'pais_parceiro': paisCtrl.text.trim(),
          'porto_origem': origemCtrl.text.trim(),
          if (navioCtrl.text.trim().isNotEmpty) 'navio': navioCtrl.text.trim(),
          'data_prevista_embarque':
              '${dataEmbarque.year}-${dataEmbarque.month.toString().padLeft(2, '0')}-${dataEmbarque.day.toString().padLeft(2, '0')}',
          'data_prevista_chegada':
              '${dataChegada.year}-${dataChegada.month.toString().padLeft(2, '0')}-${dataChegada.day.toString().padLeft(2, '0')}',
        },
      );
      if (!mounted) return;
      if (resp.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Embarque criado com sucesso!')));
        _load();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro: ${resp.statusCode}')));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Erro: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Logística'),
        backgroundColor: _cinza,
        foregroundColor: Colors.white,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: _cinza,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('Novo Embarque'),
        onPressed: _showNovoEmbarque,
      ),
      body: Column(
        children: [
          _buildFilterBar(),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _erro != null
                    ? _buildError()
                    : _filtered.isEmpty
                        ? _buildEmpty()
                        : _buildList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterBar() {
    return Container(
      height: 48,
      color: _cinza.withValues(alpha: 0.05),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        children: _statusOpts.map((opt) {
          final selected = _filtroStatus == opt.$1;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(opt.$2, style: const TextStyle(fontSize: 12)),
              selected: selected,
              selectedColor: _cinza,
              labelStyle: TextStyle(color: selected ? Colors.white : Colors.grey.shade700),
              onSelected: (_) => setState(() => _filtroStatus = opt.$1),
            ),
          );
        }).toList(),
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

  Widget _buildEmpty() => Center(
    child: Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 80, height: 80,
            decoration: BoxDecoration(
              color: _cinza.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.local_shipping_outlined, size: 40, color: _cinza),
          ),
          const SizedBox(height: 20),
          Text('Nenhum embarque encontrado',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.grey.shade800)),
          const SizedBox(height: 8),
          Text('Os embarques de gado e insumos aparecerão aqui.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: Colors.grey.shade600, height: 1.5)),
        ],
      ),
    ),
  );

  Widget _buildList() => ListView.separated(
    padding: const EdgeInsets.all(16),
    itemCount: _filtered.length,
    separatorBuilder: (_, __) => const SizedBox(height: 10),
    itemBuilder: (_, i) => _EmbarqueCard(embarque: _filtered[i]),
  );
}

class _EmbarqueCard extends StatelessWidget {
  final Map<String, dynamic> embarque;
  const _EmbarqueCard({required this.embarque});

  static const _statusInfo = {
    'PLA': ('Planejado',      Color(0xFF78909C), Icons.schedule),
    'PRE': ('Pré-Embarque',   Color(0xFF1976D2), Icons.inventory_2_outlined),
    'NAV': ('Em Trânsito',    Color(0xFF00838F), Icons.directions_boat_outlined),
    'POR': ('No Porto',       Color(0xFFE65100), Icons.anchor),
    'FIN': ('Finalizado',     Color(0xFF2E7D32), Icons.check_circle_outline),
    'CAN': ('Cancelado',      Color(0xFFD32F2F), Icons.cancel_outlined),
  };

  static const _tipoInfo = {
    'EXP': ('Exportação', Color(0xFF2E7D32), Icons.arrow_upward),
    'IMP': ('Importação', Color(0xFF1565C0), Icons.arrow_downward),
  };

  @override
  Widget build(BuildContext context) {
    final numero = embarque['numero_embarque'] as String? ?? '—';
    final tipo = embarque['tipo'] as String? ?? '';
    final status = embarque['status'] as String? ?? '';
    final destino = embarque['porto_destino'] as String? ?? '—';
    final origem = embarque['porto_origem'] as String? ?? '—';
    final pais = embarque['pais_parceiro'] as String? ?? '—';
    final prevEmbarque = embarque['data_prevista_embarque'] as String? ?? '';
    final navio = embarque['navio'] as String?;
    final valorTotal = embarque['valor_total'];

    final (statusLabel, statusColor, statusIcon) =
        _statusInfo[status] ?? ('?', Colors.grey, Icons.help_outline);
    final (tipoLabel, tipoColor, tipoIcon) =
        _tipoInfo[tipo] ?? ('?', Colors.grey, Icons.swap_horiz);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: statusColor.withValues(alpha: 0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(tipoIcon, size: 16, color: tipoColor),
                const SizedBox(width: 6),
                Text(numero,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                const Spacer(),
                _StatusChip(label: statusLabel, color: statusColor, icon: statusIcon),
              ],
            ),
            const Divider(height: 16),
            _InfoRow(Icons.flag_outlined, '$tipoLabel — $pais'),
            const SizedBox(height: 4),
            _InfoRow(Icons.anchor, '$origem → $destino'),
            if (navio != null && navio.isNotEmpty) ...[
              const SizedBox(height: 4),
              _InfoRow(Icons.directions_boat_outlined, navio),
            ],
            if (prevEmbarque.isNotEmpty) ...[
              const SizedBox(height: 4),
              _InfoRow(Icons.calendar_today_outlined,
                'Embarque: ${prevEmbarque.length >= 10 ? prevEmbarque.substring(0, 10) : prevEmbarque}'),
            ],
            if (valorTotal != null && valorTotal != '0.00' && valorTotal != 0) ...[
              const SizedBox(height: 4),
              _InfoRow(Icons.attach_money,
                'USD ${valorTotal.toString()}', color: const Color(0xFF2E7D32)),
            ],
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final String label;
  final Color color;
  final IconData icon;
  const _StatusChip({required this.label, required this.color, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color? color;
  const _InfoRow(this.icon, this.text, {this.color});

  @override
  Widget build(BuildContext context) {
    final c = color ?? Colors.grey.shade700;
    return Row(
      children: [
        Icon(icon, size: 14, color: c),
        const SizedBox(width: 8),
        Expanded(child: Text(text, style: TextStyle(fontSize: 13, color: c))),
      ],
    );
  }
}
