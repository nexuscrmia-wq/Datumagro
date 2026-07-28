import 'package:flutter/material.dart';
import 'package:datumagro_mobile/data/database.dart';
import '../services/api.dart';
import 'animal_form.dart';

class AnimalDetailScreen extends StatefulWidget {
  final Animal animal;

  const AnimalDetailScreen({super.key, required this.animal});

  @override
  State<AnimalDetailScreen> createState() => _AnimalDetailScreenState();
}

class _AnimalDetailScreenState extends State<AnimalDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;
  late Animal _animal;
  List<Map<String, dynamic>> _pesagens = [];
  bool _loadingPesagens = false;
  String _registroGenetico = 'COM';

  @override
  void initState() {
    super.initState();
    _animal = widget.animal;
    _tabs = TabController(length: 5, vsync: this);
    _tabs.addListener(() {
      if (_tabs.index == 1 && _pesagens.isEmpty && !_loadingPesagens) {
        _fetchPesagens();
      }
    });
    // Busca dados extras do servidor (registro genético) se já sincronizado
    if (_animal.serverId != null) {
      _fetchAnimalDetails();
    }
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _fetchAnimalDetails() async {
    try {
      final data = await ApiService().fetchAnimalDetail(_animal.serverId!);
      if (mounted && data != null) {
        setState(() {
          _registroGenetico = (data['registro_genetico'] as String?) ?? 'COM';
        });
      }
    } catch (_) {}
  }

  Future<void> _fetchPesagens() async {
    setState(() => _loadingPesagens = true);
    try {
      final serverId = _animal.serverId;
      if (serverId == null) {
        setState(() => _loadingPesagens = false);
        return;
      }
      final result = await ApiService().fetchPesagens(serverId);
      setState(() => _pesagens = result);
    } catch (_) {
    } finally {
      setState(() => _loadingPesagens = false);
    }
  }

  Future<void> _openEdit() async {
    final updated = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => AnimalFormScreen(animal: _animal)),
    );
    if (updated == true && mounted) {
      // Reload from DB not needed — the form updated the record in Drift.
      // For simplicity we just pop back; the list's StreamBuilder will refresh.
      Navigator.of(context).pop(true);
    }
  }

  Future<void> _showAddPesagem() async {
    final pesoCtrl = TextEditingController();
    final dataCtrl = TextEditingController(
        text: DateTime.now().toIso8601String().split('T').first);
    final obsCtrl = TextEditingController();

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Nova Pesagem'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: pesoCtrl,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                  labelText: 'Peso (kg)', hintText: '385.0'),
            ),
            TextField(
              controller: dataCtrl,
              decoration:
                  const InputDecoration(labelText: 'Data (YYYY-MM-DD)'),
            ),
            TextField(
              controller: obsCtrl,
              decoration: const InputDecoration(labelText: 'Observações'),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancelar')),
          ElevatedButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Salvar')),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    final peso = double.tryParse(pesoCtrl.text.replaceAll(',', '.'));
    if (peso == null) return;

    final messenger = ScaffoldMessenger.of(context);
    try {
      await ApiService().registrarPesagem(
        animalId: _animal.serverId!,
        pesoKg: peso,
        data: dataCtrl.text,
        observacoes: obsCtrl.text,
      );
      await _fetchPesagens();
      messenger.showSnackBar(const SnackBar(content: Text('Pesagem salva!')));
    } catch (e) {
      messenger.showSnackBar(SnackBar(content: Text('Erro: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final sexoLabel = _animal.sexo == 'M' ? 'Macho' : 'Fêmea';
    final nascimento = _animal.dataNascimento;
    final idade = nascimento != null
        ? '${DateTime.now().difference(nascimento).inDays ~/ 30} meses'
        : '—';

    return Scaffold(
      appBar: AppBar(
        title: Text(_animal.brinco),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            tooltip: 'Editar',
            onPressed: _openEdit,
          ),
        ],
        bottom: TabBar(
          controller: _tabs,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Informações'),
            Tab(text: 'Pesagens'),
            Tab(text: 'Fotos'),
            Tab(text: 'Saúde'),
            Tab(text: 'Reprodução'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabs,
        children: [
          // ── Tab 1: Informações ──────────────────────────────
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Badge de registro genético
              _GeneticoBadge(registroGenetico: _registroGenetico),
              const SizedBox(height: 12),
              _InfoCard(children: [
                _InfoRow('Brinco', _animal.brinco),
                _InfoRow('Raça', _animal.raca ?? '—'),
                _InfoRow('Sexo', sexoLabel),
                _InfoRow('Idade', idade),
                _InfoRow(
                    'Nascimento',
                    nascimento != null
                        ? nascimento.toIso8601String().split('T').first
                        : '—'),
              ]),
              const SizedBox(height: 12),
              _InfoCard(title: 'Produção', children: [
                _InfoRow('Categoria', _animal.categoria ?? '—'),
                _InfoRow('Aptidão', _animal.aptidao ?? '—'),
                _InfoRow('Temperamento', _animal.temperamento ?? '—'),
                _InfoRow('Status reprodutivo', _animal.statusReprodutivo ?? '—'),
                _InfoRow('É reprodutor', _animal.isReprodutor ? 'Sim' : 'Não'),
              ]),
              if ((_animal.caracteristicas ?? '').isNotEmpty) ...[
                const SizedBox(height: 12),
                _InfoCard(title: 'Observações', children: [
                  Text(_animal.caracteristicas ?? ''),
                ]),
              ],
            ],
          ),

          // ── Tab 2: Pesagens ─────────────────────────────────
          _buildPesagensTab(),

          // ── Tab 3: Fotos ────────────────────────────────────
          const _PlaceholderTab(
            icon: Icons.photo_camera,
            title: 'Fotos',
            subtitle: 'Adicione fotos do animal pela câmera ou galeria.',
          ),

          // ── Tab 4: Saúde ────────────────────────────────────
          const _PlaceholderTab(
            icon: Icons.vaccines,
            title: 'Saúde',
            subtitle:
                'Histórico de vacinas, vermifugações e tratamentos veterinários.',
          ),

          // ── Tab 5: Reprodução ───────────────────────────────
          const _PlaceholderTab(
            icon: Icons.favorite,
            title: 'Reprodução',
            subtitle: 'Coberturas, prenhezes e histórico de partos.',
          ),
        ],
      ),
    );
  }

  Widget _buildPesagensTab() {
    if (_loadingPesagens) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        Expanded(
          child: _pesagens.isEmpty
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.scale, size: 48, color: Colors.grey),
                      const SizedBox(height: 12),
                      Text(
                        _animal.serverId == null
                            ? 'Sincronize o animal para registrar pesagens'
                            : 'Nenhuma pesagem registrada',
                        style: const TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _fetchPesagens,
                  child: CustomScrollView(
                    slivers: [
                      SliverToBoxAdapter(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: _WeightChart(pesagens: _pesagens),
                        ),
                      ),
                      SliverList(
                        delegate: SliverChildBuilderDelegate(
                          (context, i) {
                            final p = _pesagens[i];
                            final peso = p['peso_kg']?.toString() ?? '—';
                            final data = (p['data_pesagem'] ?? '').toString();
                            final gmd = p['gmd_calculado'] ?? p['gmd'];
                            final origem = p['origem'] as String? ?? 'MANUAL';
                            return ListTile(
                              leading: Icon(
                                origem == 'RFID' ? Icons.bluetooth : Icons.scale,
                                color: origem == 'RFID' ? Colors.blue : null,
                              ),
                              title: Text('$peso kg'),
                              subtitle: Text(data),
                              trailing: gmd != null
                                  ? Column(
                                      mainAxisSize: MainAxisSize.min,
                                      crossAxisAlignment: CrossAxisAlignment.end,
                                      children: [
                                        Text('GMD: $gmd kg/dia',
                                            style: const TextStyle(fontSize: 12)),
                                        if (origem == 'RFID')
                                          const Text('RFID',
                                              style: TextStyle(
                                                  fontSize: 10, color: Colors.blue)),
                                      ],
                                    )
                                  : null,
                            );
                          },
                          childCount: _pesagens.length,
                        ),
                      ),
                    ],
                  ),
                ),
        ),
        if (_animal.serverId != null)
          Padding(
            padding: const EdgeInsets.all(12),
            child: ElevatedButton.icon(
              icon: const Icon(Icons.add),
              label: const Text('Registrar Pesagem'),
              onPressed: _showAddPesagem,
            ),
          ),
      ],
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String? title;
  final List<Widget> children;

  const _InfoCard({this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null) ...[
              Text(title!,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: Theme.of(context).colorScheme.primary)),
              const Divider(),
            ],
            ...children,
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(label,
                style: const TextStyle(
                    fontWeight: FontWeight.w500, color: Colors.grey)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

class _PlaceholderTab extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _PlaceholderTab(
      {required this.icon, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(title,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(subtitle,
                style: TextStyle(color: Colors.grey.shade600),
                textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

// ─── Badge de Registro Genético ──────────────────────────────────────────────

class _GeneticoBadge extends StatelessWidget {
  final String registroGenetico;

  const _GeneticoBadge({required this.registroGenetico});

  static const _labels = {
    'PO': 'Puro de Origem (PO)',
    'PC': 'Puro por Cruza (PC)',
    'PA': 'Puro por Absorção (PA)',
    'COM': 'Comercial',
  };

  static const _colors = {
    'PO': Color(0xFF2E7D32),
    'PC': Color(0xFFF9A825),
    'PA': Color(0xFF1565C0),
    'COM': Color(0xFF757575),
  };

  static const _emojis = {
    'PO': '🟢',
    'PC': '🟡',
    'PA': '🔵',
    'COM': '⚪',
  };

  @override
  Widget build(BuildContext context) {
    final code = registroGenetico.toUpperCase();
    final color = _colors[code] ?? _colors['COM']!;
    final label = _labels[code] ?? code;
    final emoji = _emojis[code] ?? '⚪';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withAlpha(80)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Registro Genético',
                  style: TextStyle(
                      fontSize: 11,
                      color: color,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5)),
              Text(label,
                  style: TextStyle(
                      fontSize: 14,
                      color: color,
                      fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }
}

// ─── Gráfico de Curva de Peso ────────────────────────────────────────────────

class _WeightChart extends StatelessWidget {
  final List<Map<String, dynamic>> pesagens;

  const _WeightChart({required this.pesagens});

  @override
  Widget build(BuildContext context) {
    // Ordena cronologicamente para o gráfico (pesagens vêm ordenadas por -data)
    final ordered = pesagens.reversed.toList();
    if (ordered.length < 2) {
      return const SizedBox.shrink();
    }

    final points = ordered.map((p) {
      final peso = double.tryParse(p['peso_kg']?.toString() ?? '') ?? 0.0;
      final data = p['data_pesagem'] as String? ?? '';
      return _WeightPoint(data: data, pesoKg: peso);
    }).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Curva de Peso',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: Theme.of(context).colorScheme.primary)),
            const SizedBox(height: 8),
            SizedBox(
              height: 160,
              child: CustomPaint(
                size: const Size(double.infinity, 160),
                painter: _WeightChartPainter(
                  points: points,
                  lineColor: Theme.of(context).colorScheme.primary,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(points.first.data,
                    style: const TextStyle(fontSize: 10, color: Colors.grey)),
                Text(points.last.data,
                    style: const TextStyle(fontSize: 10, color: Colors.grey)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _WeightPoint {
  final String data;
  final double pesoKg;
  const _WeightPoint({required this.data, required this.pesoKg});
}

class _WeightChartPainter extends CustomPainter {
  final List<_WeightPoint> points;
  final Color lineColor;

  const _WeightChartPainter({required this.points, required this.lineColor});

  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;

    final minY = points.map((p) => p.pesoKg).reduce((a, b) => a < b ? a : b);
    final maxY = points.map((p) => p.pesoKg).reduce((a, b) => a > b ? a : b);
    final rangeY = (maxY - minY).clamp(1.0, double.infinity);

    double toX(int i) => size.width * i / (points.length - 1);
    double toY(double v) =>
        size.height - (size.height * 0.1) - ((v - minY) / rangeY) * (size.height * 0.8);

    // Grid lines
    final gridPaint = Paint()
      ..color = Colors.grey.withAlpha(40)
      ..strokeWidth = 1;
    for (int i = 0; i <= 4; i++) {
      final y = size.height * 0.1 + (size.height * 0.8) * i / 4;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
      final weight = maxY - (rangeY * i / 4);
      final tp = TextPainter(
        text: TextSpan(
          text: '${weight.toStringAsFixed(0)} kg',
          style: TextStyle(
              fontSize: 9, color: Colors.grey.shade500),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(2, y - 10));
    }

    // Area fill
    final fillPath = Path();
    fillPath.moveTo(toX(0), size.height);
    for (int i = 0; i < points.length; i++) {
      fillPath.lineTo(toX(i), toY(points[i].pesoKg));
    }
    fillPath.lineTo(toX(points.length - 1), size.height);
    fillPath.close();
    canvas.drawPath(
      fillPath,
      Paint()..color = lineColor.withAlpha(30),
    );

    // Line
    final linePaint = Paint()
      ..color = lineColor
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    path.moveTo(toX(0), toY(points[0].pesoKg));
    for (int i = 1; i < points.length; i++) {
      path.lineTo(toX(i), toY(points[i].pesoKg));
    }
    canvas.drawPath(path, linePaint);

    // Dots
    final dotPaint = Paint()..color = lineColor;
    final dotBg = Paint()..color = Colors.white;
    for (int i = 0; i < points.length; i++) {
      final dx = toX(i);
      final dy = toY(points[i].pesoKg);
      canvas.drawCircle(Offset(dx, dy), 5, dotBg);
      canvas.drawCircle(Offset(dx, dy), 4, dotPaint);
    }
  }

  @override
  bool shouldRepaint(_WeightChartPainter old) =>
      old.points != points || old.lineColor != lineColor;
}
