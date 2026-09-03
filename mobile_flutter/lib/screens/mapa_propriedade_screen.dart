import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../services/api.dart';

// ── Tipos de infraestrutura disponíveis ──────────────────────────────────────
const _kInfraTypes = [
  {'id': 'bebedouro', 'label': 'Bebedouro', 'emoji': '💧'},
  {'id': 'cocho', 'label': 'Cocho', 'emoji': '🧂'},
  {'id': 'porteira', 'label': 'Porteira', 'emoji': '🚪'},
  {'id': 'curral', 'label': 'Curral / Baia', 'emoji': '🐄'},
  {'id': 'sede', 'label': 'Sede', 'emoji': '🏠'},
  {'id': 'silo', 'label': 'Silo / Tulha', 'emoji': '🌾'},
  {'id': 'bomba', 'label': 'Bomba / Poço', 'emoji': '⛽'},
];

enum _DrawMode { none, piquete, infraestrutura }

// ── Modelos locais ───────────────────────────────────────────────────────────
class _Piquete {
  final String nome;
  final double areaHa;
  final List<LatLng> pontos;
  _Piquete({required this.nome, required this.areaHa, required this.pontos});
}

class _InfraPoint {
  final String tipo;
  final LatLng posicao;
  _InfraPoint({required this.tipo, required this.posicao});

  String get emoji =>
      _kInfraTypes.firstWhere((t) => t['id'] == tipo,
          orElse: () => {'emoji': '📍'})['emoji']!;
}

// ── Fórmula Shoelace esférica (igual ao backend Python) ─────────────────────
double _areaHa(List<LatLng> coords) {
  if (coords.length < 3) return 0.0;
  const r = 6371000.0;
  final n = coords.length;
  double total = 0.0;
  for (int i = 0; i < n; i++) {
    final j = (i + 1) % n;
    final lon1 = coords[i].longitude * pi / 180;
    final lat1 = coords[i].latitude * pi / 180;
    final lon2 = coords[j].longitude * pi / 180;
    final lat2 = coords[j].latitude * pi / 180;
    total += (lon2 - lon1) * (2 + sin(lat1) + sin(lat2));
  }
  return double.parse(
      (total.abs() * r * r / 2 / 10000).toStringAsFixed(2));
}

// ── Parseia FeatureCollection de polígonos → lista de anéis ─────────────────
List<List<LatLng>> _parsePolygons(Map<String, dynamic>? fc) {
  if (fc == null) return [];
  final result = <List<LatLng>>[];
  final features = fc['features'] as List? ?? [];
  for (final feat in features) {
    final geom = feat['geometry'] as Map<String, dynamic>?;
    if (geom == null) continue;
    final type = geom['type'] as String?;
    final coords = geom['coordinates'] as List?;
    if (coords == null) continue;
    if (type == 'Polygon') {
      final ring = _ringToLatLng(coords[0] as List);
      if (ring.isNotEmpty) result.add(ring);
    } else if (type == 'MultiPolygon') {
      for (final poly in coords) {
        final ring = _ringToLatLng((poly as List)[0] as List);
        if (ring.isNotEmpty) result.add(ring);
      }
    }
  }
  return result;
}

List<LatLng> _ringToLatLng(List ring) => ring
    .whereType<List>()
    .where((c) => c.length >= 2)
    .map((c) => LatLng((c[1] as num).toDouble(), (c[0] as num).toDouble()))
    .toList();

// ── Parseia piquetes salvos ──────────────────────────────────────────────────
List<_Piquete> _parsePiquetes(Map<String, dynamic>? fc) {
  if (fc == null) return [];
  final result = <_Piquete>[];
  final features = fc['features'] as List? ?? [];
  for (final feat in features) {
    final props = feat['properties'] as Map<String, dynamic>? ?? {};
    final geom = feat['geometry'] as Map<String, dynamic>?;
    if (geom == null) continue;
    final coords = geom['coordinates'] as List?;
    if (coords == null || coords.isEmpty) continue;
    final ring = _ringToLatLng(coords[0] as List);
    if (ring.isEmpty) continue;
    result.add(_Piquete(
      nome: props['name'] as String? ?? 'Piquete',
      areaHa: (props['area_ha'] as num?)?.toDouble() ?? _areaHa(ring),
      pontos: ring,
    ));
  }
  return result;
}

// ── Parseia infraestrutura salva ─────────────────────────────────────────────
List<_InfraPoint> _parseInfra(Map<String, dynamic>? fc) {
  if (fc == null) return [];
  final result = <_InfraPoint>[];
  final features = fc['features'] as List? ?? [];
  for (final feat in features) {
    final props = feat['properties'] as Map<String, dynamic>? ?? {};
    final geom = feat['geometry'] as Map<String, dynamic>?;
    if (geom == null || geom['type'] != 'Point') continue;
    final coords = geom['coordinates'] as List?;
    if (coords == null || coords.length < 2) continue;
    result.add(_InfraPoint(
      tipo: props['tipo'] as String? ?? 'ponto',
      posicao: LatLng((coords[1] as num).toDouble(), (coords[0] as num).toDouble()),
    ));
  }
  return result;
}

// ── Calcula centróide simples dos polígonos CAR ──────────────────────────────
LatLng? _centroid(List<List<LatLng>> polygons) {
  if (polygons.isEmpty) return null;
  double sumLat = 0, sumLng = 0;
  int count = 0;
  for (final ring in polygons) {
    for (final pt in ring) {
      sumLat += pt.latitude;
      sumLng += pt.longitude;
      count++;
    }
  }
  if (count == 0) return null;
  return LatLng(sumLat / count, sumLng / count);
}

// ── Serializa para GeoJSON ───────────────────────────────────────────────────
Map<String, dynamic> _piquetesToGeoJson(List<_Piquete> list) => {
      'type': 'FeatureCollection',
      'features': list
          .map((p) => {
                'type': 'Feature',
                'properties': {'name': p.nome, 'area_ha': p.areaHa},
                'geometry': {
                  'type': 'Polygon',
                  'coordinates': [
                    p.pontos
                        .map((pt) => [pt.longitude, pt.latitude])
                        .toList(),
                  ],
                },
              })
          .toList(),
    };

Map<String, dynamic> _infraToGeoJson(List<_InfraPoint> list) => {
      'type': 'FeatureCollection',
      'features': list
          .map((p) => {
                'type': 'Feature',
                'properties': {'tipo': p.tipo, 'emoji': p.emoji},
                'geometry': {
                  'type': 'Point',
                  'coordinates': [p.posicao.longitude, p.posicao.latitude],
                },
              })
          .toList(),
    };

// ══════════════════════════════════════════════════════════════════════════════
//  SCREEN
// ══════════════════════════════════════════════════════════════════════════════

class MapaPropriedadeScreen extends StatefulWidget {
  final Map<String, dynamic>? propriedadeInicial;
  const MapaPropriedadeScreen({super.key, this.propriedadeInicial});

  @override
  State<MapaPropriedadeScreen> createState() => _MapaPropriedadeScreenState();
}

class _MapaPropriedadeScreenState extends State<MapaPropriedadeScreen> {
  static const _verde = Color(0xFF2E7D32);
  static const _verdeClaro = Color(0xFF43A047);
  static const _amarelo = Color(0xFFF9A825);
  static const _laranja = Color(0xFFEF6C00);

  final _api = ApiService();
  final _mapController = MapController();

  // Seleção de propriedade
  List<Map<String, dynamic>> _propriedades = [];
  Map<String, dynamic>? _propriedade;
  bool _loadingList = false;

  // Camadas
  List<List<LatLng>> _carPolygons = [];
  List<_Piquete> _piquetes = [];
  List<_InfraPoint> _infra = [];

  // Visibilidade
  bool _showCar = true;
  bool _showPiquetes = true;
  bool _showInfra = true;

  // Desenho
  _DrawMode _drawMode = _DrawMode.none;
  String? _pendingInfraType;
  List<LatLng> _drawingPoints = [];

  bool _hasChanges = false;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    if (widget.propriedadeInicial != null) {
      _loadProp(widget.propriedadeInicial!);
    } else {
      _fetchPropriedades();
    }
  }

  Future<void> _fetchPropriedades() async {
    setState(() => _loadingList = true);
    try {
      final list = await _api.fetchPropriedades();
      if (!mounted) return;
      if (list.length == 1) {
        _loadProp(list.first);
      } else {
        setState(() {
          _propriedades = list;
          _loadingList = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loadingList = false);
    }
  }

  void _loadProp(Map<String, dynamic> prop) {
    _propriedade = prop;
    _carPolygons = _parsePolygons(prop['geojson_car'] as Map<String, dynamic>?);
    _piquetes = _parsePiquetes(
        prop['geojson_piquetes_talhoes'] as Map<String, dynamic>?);
    _infra = _parseInfra(
        prop['geojson_infraestrutura'] as Map<String, dynamic>?);
    _hasChanges = false;

    setState(() => _loadingList = false);

    // Centraliza no mapa após o frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final center = _centroid(_carPolygons);
      if (center != null) {
        _mapController.move(center, 14.0);
      }
    });
  }

  // ── Interação no mapa ──────────────────────────────────────────────────────

  void _handleTap(TapPosition _, LatLng pt) {
    if (_drawMode == _DrawMode.piquete) {
      setState(() => _drawingPoints.add(pt));
    } else if (_drawMode == _DrawMode.infraestrutura &&
        _pendingInfraType != null) {
      setState(() {
        _infra.add(_InfraPoint(tipo: _pendingInfraType!, posicao: pt));
        _drawMode = _DrawMode.none;
        _pendingInfraType = null;
        _hasChanges = true;
      });
    }
  }

  Future<void> _closePiquete() async {
    if (_drawingPoints.length < 3) {
      _showSnack('Adicione pelo menos 3 pontos para fechar o piquete.');
      return;
    }
    final area = _areaHa(_drawingPoints);
    final nome = await _showNomeDialog(area);
    if (nome == null) return; // cancelado
    setState(() {
      _piquetes.add(_Piquete(
        nome: nome,
        areaHa: area,
        pontos: List.from(_drawingPoints),
      ));
      _drawingPoints = [];
      _drawMode = _DrawMode.none;
      _hasChanges = true;
    });
  }

  void _cancelDraw() {
    setState(() {
      _drawingPoints = [];
      _drawMode = _DrawMode.none;
      _pendingInfraType = null;
    });
  }

  void _undoLastPoint() {
    if (_drawingPoints.isEmpty) return;
    setState(() => _drawingPoints.removeLast());
  }

  void _removePiquete(int index) {
    setState(() {
      _piquetes.removeAt(index);
      _hasChanges = true;
    });
  }

  void _removeInfra(int index) {
    setState(() {
      _infra.removeAt(index);
      _hasChanges = true;
    });
  }

  Future<void> _save() async {
    final prop = _propriedade;
    if (prop == null) return;
    final id = prop['id'] as int?;
    if (id == null) return;
    setState(() => _saving = true);
    try {
      await _api.atualizarCamadas(
        id,
        piquetes: _piquetesToGeoJson(_piquetes),
        infraestrutura: _infraToGeoJson(_infra),
      );
      if (!mounted) return;
      setState(() {
        _hasChanges = false;
        _saving = false;
      });
      _showSnack('Mapa salvo com sucesso!', color: _verde);
    } catch (e) {
      if (!mounted) return;
      setState(() => _saving = false);
      _showSnack('Erro ao salvar: $e');
    }
  }

  // ── Diálogos ───────────────────────────────────────────────────────────────

  Future<String?> _showNomeDialog(double area) async {
    final ctrl = TextEditingController(text: 'Piquete ${_piquetes.length + 1}');
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Nomear piquete'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Área calculada: ${area.toStringAsFixed(2)} ha',
                style: const TextStyle(color: _verde, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Nome do piquete / talhão',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (v) => Navigator.pop(ctx, v.trim()),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: _verde),
            onPressed: () => Navigator.pop(ctx, ctrl.text.trim()),
            child: const Text('Salvar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Future<void> _showInfraTypePicker() async {
    final type = await showModalBottomSheet<String>(
      context: context,
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Selecione o tipo de infraestrutura',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const Divider(height: 0),
            ..._kInfraTypes.map((t) => ListTile(
                  leading: Text(t['emoji']!, style: const TextStyle(fontSize: 24)),
                  title: Text(t['label']!),
                  onTap: () => Navigator.pop(context, t['id']),
                )),
          ],
        ),
      ),
    );
    if (type == null) return;
    setState(() {
      _pendingInfraType = type;
      _drawMode = _DrawMode.infraestrutura;
    });
  }

  Future<void> _showPiquetesList() async {
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.5,
        builder: (_, scroll) => Column(
          children: [
            const SizedBox(height: 12),
            Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  const Text('Piquetes / Talhões',
                      style:
                          TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const Spacer(),
                  Text('${_piquetes.length} item(s)',
                      style: const TextStyle(color: Colors.grey)),
                ],
              ),
            ),
            const Divider(height: 0),
            Expanded(
              child: _piquetes.isEmpty
                  ? const Center(
                      child: Text('Nenhum piquete desenhado ainda.',
                          style: TextStyle(color: Colors.grey)))
                  : ListView.builder(
                      controller: scroll,
                      itemCount: _piquetes.length,
                      itemBuilder: (_, i) {
                        final p = _piquetes[i];
                        return ListTile(
                          leading: const Icon(Icons.crop_square,
                              color: _amarelo),
                          title: Text(p.nome),
                          subtitle: Text(
                              '${p.areaHa.toStringAsFixed(2)} ha'),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete_outline,
                                color: Colors.red),
                            onPressed: () {
                              Navigator.pop(context);
                              _removePiquete(i);
                            },
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSnack(String msg, {Color? color}) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: color ?? Colors.red[700],
      behavior: SnackBarBehavior.floating,
    ));
  }

  // ── Build ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    // Tela de seleção de propriedade
    if (_propriedade == null) {
      return _buildPicker();
    }
    return _buildMap();
  }

  Widget _buildVazio() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 90, height: 90,
              decoration: BoxDecoration(
                color: _verde.withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.terrain, size: 44, color: _verde),
            ),
            const SizedBox(height: 20),
            const Text('Nenhuma propriedade cadastrada',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center),
            const SizedBox(height: 8),
            const Text(
              'Cadastre sua fazenda ou propriedade para usar o mapa, desenhar piquetes e marcar infraestrutura.',
              style: TextStyle(color: Colors.black54, fontSize: 14),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),
            FilledButton.icon(
              style: FilledButton.styleFrom(backgroundColor: _verde),
              onPressed: _showCadastrarPropriedade,
              icon: const Icon(Icons.add_location_alt),
              label: const Text('Cadastrar propriedade'),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: _fetchPropriedades,
              child: const Text('Atualizar lista'),
            ),
          ],
        ),
      ),
    );
  }

  static const _ufs = [
    'AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT',
    'PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO',
  ];

  Future<void> _showCadastrarPropriedade() async {
    final nomeCtrl = TextEditingController();
    final cidadeCtrl = TextEditingController();
    final haCtrl = TextEditingController();
    String uf = 'MG';
    String objetivo = 'ENGORDA';
    bool saving = false;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setInner) => Padding(
          padding: EdgeInsets.only(
              left: 20, right: 20, top: 20,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Nova Propriedade',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 20),
                TextField(
                  controller: nomeCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Nome da propriedade *',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.home_outlined),
                    hintText: 'Ex: Fazenda Santa Maria',
                  ),
                  textCapitalization: TextCapitalization.words,
                ),
                const SizedBox(height: 14),
                Row(children: [
                  Expanded(
                    child: TextField(
                      controller: cidadeCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Cidade *',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.location_city),
                      ),
                      textCapitalization: TextCapitalization.words,
                    ),
                  ),
                  const SizedBox(width: 10),
                  SizedBox(
                    width: 100,
                    child: DropdownButtonFormField<String>(
                      value: uf,
                      decoration: const InputDecoration(
                        labelText: 'UF',
                        border: OutlineInputBorder(),
                      ),
                      items: _ufs.map((u) =>
                        DropdownMenuItem(value: u, child: Text(u))).toList(),
                      onChanged: (v) => setInner(() => uf = v ?? uf),
                    ),
                  ),
                ]),
                const SizedBox(height: 14),
                Row(children: [
                  Expanded(
                    child: TextField(
                      controller: haCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Área (hectares)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.landscape),
                        hintText: 'Ex: 150.5',
                      ),
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: objetivo,
                      decoration: const InputDecoration(
                        labelText: 'Objetivo',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'CRIA', child: Text('Cria')),
                        DropdownMenuItem(value: 'RECRIA', child: Text('Recria')),
                        DropdownMenuItem(value: 'ENGORDA', child: Text('Engorda')),
                      ],
                      onChanged: (v) => setInner(() => objetivo = v ?? objetivo),
                    ),
                  ),
                ]),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    style: FilledButton.styleFrom(
                        backgroundColor: _verde,
                        padding: const EdgeInsets.symmetric(vertical: 14)),
                    onPressed: saving
                        ? null
                        : () async {
                            if (nomeCtrl.text.trim().isEmpty ||
                                cidadeCtrl.text.trim().isEmpty) {
                              ScaffoldMessenger.of(ctx).showSnackBar(
                                const SnackBar(
                                    content: Text('Preencha nome e cidade.')),
                              );
                              return;
                            }
                            setInner(() => saving = true);
                            final messenger = ScaffoldMessenger.of(ctx);
                            final dados = <String, dynamic>{
                              'nome_propriedade': nomeCtrl.text.trim(),
                              'cidade': cidadeCtrl.text.trim(),
                              'estado': uf,
                              'objetivo_producao': objetivo,
                              if (haCtrl.text.isNotEmpty)
                                'hectares': double.tryParse(
                                    haCtrl.text.replaceAll(',', '.')),
                            };
                            final (nova, erro) = await _api.criarPropriedade(dados);
                            if (!ctx.mounted) return;
                            Navigator.of(ctx).pop();
                            if (nova != null) {
                              setState(() {
                                _propriedades.add(nova);
                                _loadProp(nova);
                              });
                              messenger.showSnackBar(
                                const SnackBar(
                                    content: Text('Propriedade cadastrada!'),
                                    backgroundColor: _verde),
                              );
                            } else {
                              messenger.showSnackBar(
                                SnackBar(
                                    content: Text(erro ?? 'Erro ao cadastrar.'),
                                    backgroundColor: Colors.red),
                              );
                            }
                          },
                    child: saving
                        ? const SizedBox(
                            width: 20, height: 20,
                            child: CircularProgressIndicator(
                                color: Colors.white, strokeWidth: 2))
                        : const Text('Salvar propriedade',
                            style: TextStyle(fontSize: 16)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPicker() {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: const Text('Selecionar Propriedade'),
      ),
      body: _loadingList
          ? const Center(child: CircularProgressIndicator(color: _verde))
          : _propriedades.isEmpty
              ? _buildVazio()

              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _propriedades.length,
                  itemBuilder: (_, i) {
                    final p = _propriedades[i];
                    final ha = p['area_total_ha'] ?? p['hectares'];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: _verde.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.terrain, color: _verde),
                        ),
                        title: Text(p['nome_propriedade'] as String? ?? '—',
                            style:
                                const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(
                            '${p['cidade'] ?? ''} — ${ha != null ? '$ha ha' : 'Área não informada'}'),
                        trailing:
                            const Icon(Icons.map_outlined, color: _verde),
                        onTap: () => setState(() => _loadProp(p)),
                      ),
                    );
                  },
                ),
    );
  }

  Widget _buildMap() {
    final prop = _propriedade!;
    final nomeProp = prop['nome_propriedade'] as String? ?? 'Mapa';
    final hasCarPolygons = _carPolygons.isNotEmpty;
    final initialCenter = _centroid(_carPolygons) ??
        const LatLng(-15.7801, -47.9292); // centro do Brasil como fallback

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: Text(nomeProp,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
        actions: [
          if (_hasChanges)
            _saving
                ? const Padding(
                    padding: EdgeInsets.all(16),
                    child: SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                            color: Colors.white, strokeWidth: 2)))
                : TextButton.icon(
                    onPressed: _save,
                    icon: const Icon(Icons.save_alt, color: Colors.white),
                    label: const Text('Salvar',
                        style: TextStyle(color: Colors.white)),
                  ),
        ],
      ),
      body: Stack(
        children: [
          // ── Mapa ──────────────────────────────────────────────────────────
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: initialCenter,
              initialZoom: hasCarPolygons ? 13.5 : 10.0,
              onTap: _handleTap,
            ),
            children: [
              TileLayer(
                urlTemplate:
                    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'br.com.datumagro',
              ),

              // Camada CAR (base oficial, imutável)
              if (_showCar && _carPolygons.isNotEmpty)
                PolygonLayer(
                  polygons: _carPolygons
                      .map((pts) => Polygon(
                            points: pts,
                            color: const Color(0x3343A047),
                            borderColor: _verdeClaro,
                            borderStrokeWidth: 2.5,
                          ))
                      .toList(),
                ),

              // Camada piquetes / talhões salvos
              if (_showPiquetes && _piquetes.isNotEmpty)
                PolygonLayer(
                  polygons: _piquetes
                      .map((p) => Polygon(
                            points: p.pontos,
                            color: const Color(0x55F9A825),
                            borderColor: _amarelo,
                            borderStrokeWidth: 2,
                            label: '${p.nome}\n${p.areaHa.toStringAsFixed(1)} ha',
                            labelStyle: const TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold),
                          ))
                      .toList(),
                ),

              // Polígono sendo desenhado agora
              if (_drawingPoints.isNotEmpty) ...[
                PolylineLayer(
                  polylines: [
                    Polyline(
                      points: [
                        ..._drawingPoints,
                        _drawingPoints.first, // fecha visualmente
                      ],
                      color: _laranja,
                      strokeWidth: 2.5,
                    ),
                  ],
                ),
                MarkerLayer(
                  markers: _drawingPoints
                      .map((pt) => Marker(
                            point: pt,
                            width: 12,
                            height: 12,
                            child: Container(
                              decoration: BoxDecoration(
                                color: _laranja,
                                shape: BoxShape.circle,
                                border: Border.all(
                                    color: Colors.white, width: 2),
                              ),
                            ),
                          ))
                      .toList(),
                ),
              ],

              // Camada infraestrutura (marcadores)
              if (_showInfra && _infra.isNotEmpty)
                MarkerLayer(
                  markers: _infra
                      .asMap()
                      .entries
                      .map((e) => Marker(
                            point: e.value.posicao,
                            width: 40,
                            height: 40,
                            child: GestureDetector(
                              onLongPress: () => _removeInfra(e.key),
                              child: Container(
                                decoration: const BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                        color: Colors.black26,
                                        blurRadius: 4)
                                  ],
                                ),
                                child: Center(
                                  child: Text(e.value.emoji,
                                      style:
                                          const TextStyle(fontSize: 20)),
                                ),
                              ),
                            ),
                          ))
                      .toList(),
                ),
            ],
          ),

          // ── Toolbar de camadas (topo) ─────────────────────────────────────
          Positioned(
            top: 12,
            left: 12,
            child: Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _LayerToggle(
                      emoji: '🌿',
                      label: 'CAR',
                      active: _showCar,
                      onTap: () => setState(() => _showCar = !_showCar),
                    ),
                    _LayerToggle(
                      emoji: '🟨',
                      label: 'Piquetes',
                      active: _showPiquetes,
                      onTap: () =>
                          setState(() => _showPiquetes = !_showPiquetes),
                    ),
                    _LayerToggle(
                      emoji: '📍',
                      label: 'Infra',
                      active: _showInfra,
                      onTap: () =>
                          setState(() => _showInfra = !_showInfra),
                    ),
                    const SizedBox(width: 4),
                    InkWell(
                      borderRadius: BorderRadius.circular(8),
                      onTap: _showPiquetesList,
                      child: const Padding(
                        padding: EdgeInsets.all(8),
                        child: Icon(Icons.list_alt, size: 20, color: _verde),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ── Hint de modo de desenho ───────────────────────────────────────
          if (_drawMode != _DrawMode.none)
            Positioned(
              top: 70,
              left: 12,
              right: 12,
              child: Card(
                color: _laranja,
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  child: Row(
                    children: [
                      const Icon(Icons.touch_app,
                          color: Colors.white, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _drawMode == _DrawMode.piquete
                              ? 'Toque no mapa para adicionar vértices do piquete'
                              : 'Toque no local para posicionar o marcador',
                          style: const TextStyle(
                              color: Colors.white, fontSize: 13),
                        ),
                      ),
                      TextButton(
                        onPressed: _cancelDraw,
                        child: const Text('Cancelar',
                            style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                ),
              ),
            ),

          // ── Toolbar de desenho (rodapé) ───────────────────────────────────
          Positioned(
            bottom: 20,
            left: 16,
            right: 16,
            child: Row(
              children: [
                // Botões de desenho
                if (_drawMode == _DrawMode.none) ...[
                  _MapFab(
                    icon: Icons.crop_square,
                    label: 'Piquete',
                    color: _amarelo,
                    onTap: () =>
                        setState(() => _drawMode = _DrawMode.piquete),
                  ),
                  const SizedBox(width: 12),
                  _MapFab(
                    emoji: '📍',
                    label: 'Infra',
                    color: _laranja,
                    onTap: _showInfraTypePicker,
                  ),
                ] else if (_drawMode == _DrawMode.piquete) ...[
                  _MapFab(
                    icon: Icons.undo,
                    label: 'Desfazer',
                    color: Colors.grey[700]!,
                    onTap: _undoLastPoint,
                    small: true,
                  ),
                  const SizedBox(width: 12),
                  _MapFab(
                    icon: Icons.check_circle,
                    label: 'Fechar\nPiquete',
                    color: _verde,
                    onTap: _drawingPoints.length >= 3 ? _closePiquete : null,
                  ),
                ],
                const Spacer(),
                // Légenda das camadas
                if (!hasCarPolygons)
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black87,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'Sem CAR importado\nImporte via Propriedade → Importar CAR',
                      style: TextStyle(color: Colors.white60, fontSize: 11),
                      textAlign: TextAlign.center,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Widgets auxiliares ────────────────────────────────────────────────────────

class _LayerToggle extends StatelessWidget {
  final String emoji;
  final String label;
  final bool active;
  final VoidCallback onTap;
  const _LayerToggle(
      {required this.emoji,
      required this.label,
      required this.active,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        child: Opacity(
          opacity: active ? 1.0 : 0.35,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(emoji, style: const TextStyle(fontSize: 18)),
              Text(label,
                  style: const TextStyle(
                      fontSize: 9, fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}

class _MapFab extends StatelessWidget {
  final IconData? icon;
  final String? emoji;
  final String label;
  final Color color;
  final VoidCallback? onTap;
  final bool small;

  const _MapFab({
    this.icon,
    this.emoji,
    required this.label,
    required this.color,
    required this.onTap,
    this.small = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Opacity(
        opacity: onTap == null ? 0.4 : 1.0,
        child: Container(
          padding: EdgeInsets.symmetric(
              horizontal: small ? 12 : 16, vertical: small ? 8 : 12),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(14),
            boxShadow: const [
              BoxShadow(color: Colors.black26, blurRadius: 6, offset: Offset(0, 2))
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (emoji != null)
                Text(emoji!, style: TextStyle(fontSize: small ? 18 : 22))
              else if (icon != null)
                Icon(icon, color: Colors.white, size: small ? 18 : 22),
              const SizedBox(height: 2),
              Text(label,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: small ? 9 : 11,
                      fontWeight: FontWeight.bold,
                      height: 1.2)),
            ],
          ),
        ),
      ),
    );
  }
}
