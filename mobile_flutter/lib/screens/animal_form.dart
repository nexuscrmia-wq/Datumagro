import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:provider/provider.dart';
import 'package:datumagro_mobile/data/database.dart';
import 'package:drift/drift.dart' show Value;

import '../services/api.dart';
import 'animal_detail_screen.dart';

// ─── Configurações por espécie ────────────────────────────────────────────────

class _EspecieConfig {
  final String label;           // nome amigável da espécie
  final String idLabel;         // rótulo do campo identificação
  final String idHint;          // hint do campo identificação
  final List<(String, String)> racas;
  final List<(String, String)> categorias;
  final List<(String, String)> aptidoes;
  final bool temStatus;         // tem status_reprodutivo para fêmeas
  final bool temReprodutor;     // tem campo "é reprodutor" para machos

  const _EspecieConfig({
    required this.label,
    required this.idLabel,
    required this.idHint,
    required this.racas,
    required this.categorias,
    required this.aptidoes,
    this.temStatus = true,
    this.temReprodutor = true,
  });
}

const _configs = <String, _EspecieConfig>{
  'BOVINOS_CORTE': _EspecieConfig(
    label: 'Bovinos de Corte',
    idLabel: 'Número do brinco / ID',
    idHint: 'Ex: 0042 ou BR-001',
    racas: [
      ('NELORE', 'Nelore'), ('ANGUS', 'Angus'), ('BRAHMAN', 'Brahman'),
      ('BRANGUS', 'Brangus'), ('SENEPOL', 'Senepol'), ('GUZERA', 'Guzerá'),
      ('TABAPUA', 'Tabapuã'), ('GIR', 'Gir'), ('BRAFORD', 'Braford'),
      ('HEREFORD', 'Hereford'), ('CARACU', 'Caracu'), ('OUTRA', 'Outra/Mestiço'),
    ],
    categorias: [
      ('BEZERRO', 'Bezerro(a)'), ('NOVILHA', 'Novilha'), ('GARROTE', 'Garrote'),
      ('TOURO', 'Touro'), ('MATRIZ', 'Matriz (Vaca)'), ('BOI', 'Boi (Engorda)'),
    ],
    aptidoes: [('CORTE', 'Corte'), ('DUPLA', 'Dupla Aptidão')],
  ),
  'BOVINOS_LEITE': _EspecieConfig(
    label: 'Bovinos de Leite',
    idLabel: 'Número do brinco / ID',
    idHint: 'Ex: 0042 ou BR-001',
    racas: [
      ('GIROLANDO', 'Girolando'), ('HOLANDES', 'Holandês (PB)'),
      ('JERSEY', 'Jersey'), ('PARDO_SUICO', 'Pardo Suíço'),
      ('GIR', 'Gir Leiteiro'), ('GUZERA', 'Guzerá'), ('CARACU', 'Caracu'),
      ('OUTRA', 'Outra/Mestiço'),
    ],
    categorias: [
      ('BEZERRO', 'Bezerro(a)'), ('NOVILHA', 'Novilha'), ('GARROTE', 'Garrote'),
      ('TOURO', 'Touro'), ('MATRIZ', 'Matriz (Vaca)'), ('BOI', 'Descarte'),
    ],
    aptidoes: [('LEITE', 'Leite'), ('DUPLA', 'Dupla Aptidão')],
  ),
  'EQUINOS': _EspecieConfig(
    label: 'Equinos',
    idLabel: 'Nome / Registro',
    idHint: 'Ex: Relâmpago ou ABQM-12345',
    racas: [
      ('QUARTO_MILHA', 'Quarto de Milha'), ('CRIOULO', 'Crioulo'),
      ('PAINT_HORSE', 'Paint Horse'), ('MANGALARGA', 'Mangalarga Marchador'),
      ('ARABE', 'Árabe'), ('PSI', 'PSI (Puro Sangue Inglês)'),
      ('LUSITANO', 'Lusitano'), ('APPALOOSA', 'Appaloosa'),
      ('CAMPOLINA', 'Campolina'), ('SELA_BR', 'Sela Brasileira'),
      ('OUTRA', 'Outra/Mestiço'),
    ],
    categorias: [
      ('POTRO', 'Potro / Potranca'), ('CAPAO', 'Capão'),
      ('EGUA', 'Égua'), ('GARANHAO', 'Garanhão'),
    ],
    aptidoes: [
      ('TRABALHO', 'Trabalho'), ('ESPORTE', 'Esporte / Lazer'),
      ('REPRODUCAO', 'Reprodução'), ('CORTE', 'Carne'),
    ],
    temStatus: true,
    temReprodutor: true,
  ),
  'SUINOS': _EspecieConfig(
    label: 'Suínos',
    idLabel: 'Tatuagem / Brinco',
    idHint: 'Ex: SUB-001',
    racas: [
      ('LANDRACE', 'Landrace'), ('LARGE_WHITE', 'Large White'),
      ('PIETRAIN', 'Pietrain'), ('DUROC', 'Duroc'),
      ('HAMPSHIRE', 'Hampshire'), ('MOURA', 'Moura'), ('PIAU', 'Piau'),
      ('OUTRA', 'Outra/Mestiço'),
    ],
    categorias: [
      ('LEITAO', 'Leitão'), ('SUINO_CRESC', 'Em Crescimento'),
      ('SUINO_TERM', 'Em Terminação'), ('PORCA', 'Porca'), ('VARRAO', 'Varrão'),
    ],
    aptidoes: [('CARNE', 'Carne'), ('REPRODUCAO', 'Reprodução')],
  ),
  'OVINOS_CAPRINOS': _EspecieConfig(
    label: 'Ovinos e Caprinos',
    idLabel: 'Brinco / ID',
    idHint: 'Ex: OV-001',
    racas: [
      // Ovinos
      ('DORPER', 'Dorper'), ('SANTA_INES', 'Santa Inês'),
      ('TEXEL', 'Texel'), ('ILE_FRANCE', 'Ile de France'),
      ('SUFFOLK', 'Suffolk'), ('BERGAMASCA', 'Bergamasca'),
      // Caprinos
      ('BOER', 'Boer'), ('ANGLO_NUB', 'Anglo-Nubiano'),
      ('SAANEN', 'Saanen'), ('TOGGENBURG', 'Toggenburg'),
      ('ALPINA_BR', 'Alpina Brasileira'),
      ('OUTRA', 'Outra/Mestiço'),
    ],
    categorias: [
      ('CORDEIRO', 'Cordeiro / Cabrito'), ('OVELHA', 'Ovelha / Cabra'),
      ('CARNEIRO', 'Carneiro / Bode'),
    ],
    aptidoes: [
      ('CARNE', 'Carne'), ('LEITE', 'Leite'), ('LA', 'Lã'),
      ('DUPLA', 'Dupla Aptidão'),
    ],
  ),
};

_EspecieConfig _cfgFor(String esp) =>
    _configs[esp] ?? _configs['BOVINOS_CORTE']!;

// ─── Opções comuns ────────────────────────────────────────────────────────────

const _temperamentos = [
  ('MANSO', 'Manso'), ('NORMAL', 'Normal'), ('BRABO', 'Brabo'), ('AGRESSIVO', 'Agressivo'),
];

const _statusReprod = [
  ('VAZIA', 'Vazia'), ('PRENHA', 'Prenha'), ('LACTANTE', 'Em Lactação'), ('SECA', 'Seca'),
];

const _registros = [
  ('COM', 'Comercial (sem registro)'), ('PO', 'Puro de Origem (PO)'),
  ('PC', 'Puro por Cruza (PC)'), ('PA', 'Puro por Absorção (PA)'),
];

// ─── Tela ─────────────────────────────────────────────────────────────────────

class AnimalFormScreen extends StatefulWidget {
  final Animal? animal;
  const AnimalFormScreen({super.key, this.animal});

  @override
  State<AnimalFormScreen> createState() => _AnimalFormScreenState();
}

class _AnimalFormScreenState extends State<AnimalFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _brinco = TextEditingController();
  final _caracteristicas = TextEditingController();

  String? _raca;
  String _sexo = 'M';
  DateTime? _dataNasc;
  String? _categoria;
  String? _temperamento;
  String? _aptidao;
  String? _statusReprodutivo;
  bool _isReprodutor = false;
  String _registroGenetico = 'COM';

  bool _saving = false;
  int _propriedadeId = 1;
  String _tipoEspecie = 'BOVINOS_CORTE';

  static const _verde = Color(0xFF2E7D32);
  static const _storage = FlutterSecureStorage();

  @override
  void initState() {
    super.initState();
    _loadContext();
    final a = widget.animal;
    if (a != null) {
      _brinco.text = a.brinco;
      _raca = a.raca;
      _sexo = a.sexo ?? 'M';
      _dataNasc = a.dataNascimento;
      _categoria = a.categoria;
      _temperamento = a.temperamento;
      _aptidao = a.aptidao;
      _statusReprodutivo = a.statusReprodutivo;
      _isReprodutor = a.isReprodutor;
      _caracteristicas.text = a.caracteristicas ?? '';
    }
  }

  Future<void> _loadContext() async {
    try {
      final s = await _storage.read(key: 'user');
      if (s != null) {
        final data = json.decode(s) as Map<String, dynamic>;
        final especie = data['tipo_especie'] as String? ?? 'BOVINOS_CORTE';
        final props = data['propriedades'] as List<dynamic>?;
        setState(() {
          _tipoEspecie = especie;
          // Ao trocar espécie, garante que os campos escolhidos ainda são válidos
          final cfg = _cfgFor(especie);
          if (_raca != null && !cfg.racas.any((r) => r.$1 == _raca)) _raca = null;
          if (_categoria != null && !cfg.categorias.any((c) => c.$1 == _categoria)) {
            _categoria = null;
          }
          if (_aptidao != null && !cfg.aptidoes.any((a) => a.$1 == _aptidao)) {
            _aptidao = null;
          }
          if (props != null && props.isNotEmpty) {
            _propriedadeId = (props.first as Map)['id'] as int? ?? 1;
          }
        });
        return;
      }
    } catch (_) {}
    // Fallback: primeira propriedade da API
    try {
      final list = await ApiService().fetchPropriedades();
      if (list.isNotEmpty && mounted) {
        setState(() => _propriedadeId = list.first['id'] as int? ?? 1);
      }
    } catch (_) {}
  }

  @override
  void dispose() {
    _brinco.dispose();
    _caracteristicas.dispose();
    super.dispose();
  }

  // ── DatePicker ───────────────────────────────────────────────────────────

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _dataNasc ?? DateTime.now(),
      firstDate: DateTime(1990),
      lastDate: DateTime.now(),
      helpText: 'Data de nascimento',
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: Theme.of(ctx).colorScheme.copyWith(primary: _verde),
        ),
        child: child!,
      ),
    );
    if (picked != null) setState(() => _dataNasc = picked);
  }

  // ── Salvar ───────────────────────────────────────────────────────────────

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    final db = Provider.of<AppDatabase>(context, listen: false);
    final now = DateTime.now();
    final isEdit = widget.animal != null;
    final cfg = _cfgFor(_tipoEspecie);

    final statusFinal = (cfg.temStatus && _sexo == 'F') ? _statusReprodutivo : null;
    final reprodutorFinal = (cfg.temReprodutor && _sexo == 'M') ? _isReprodutor : false;

    try {
      if (isEdit) {
        await db.updateAnimalEntry(widget.animal!.copyWith(
          brinco: _brinco.text.trim(),
          raca: Value(_raca),
          sexo: Value(_sexo),
          dataNascimento: Value(_dataNasc),
          categoria: Value(_categoria),
          temperamento: Value(_temperamento),
          aptidao: Value(_aptidao),
          statusReprodutivo: Value(statusFinal),
          isReprodutor: reprodutorFinal,
          caracteristicas: Value(_caracteristicas.text.trim()),
          updatedAt: Value(now),
        ));
        await db.enqueue(
          'update', 'animal',
          json.encode({
            'id': widget.animal!.serverId ?? widget.animal!.id,
            'brinco': _brinco.text.trim(),
            'raca': _raca,
            'sexo': _sexo,
            'data_nascimento': _dataNasc?.toIso8601String(),
            'categoria': _categoria,
            'temperamento': _temperamento,
            'aptidao': _aptidao,
            'status_reprodutivo': statusFinal,
            'is_reprodut': reprodutorFinal,
            'registro_genetico': _registroGenetico,
            'caracteristicas_adicionais': _caracteristicas.text.trim(),
          }),
          clientId: 'upd-${widget.animal!.id}-${now.millisecondsSinceEpoch}',
        );
      } else {
        final id = await db.insertAnimal(AnimalsCompanion.insert(
          propriedadeId: _propriedadeId,
          brinco: _brinco.text.trim(),
          raca: Value(_raca),
          sexo: Value(_sexo),
          dataNascimento: Value(_dataNasc),
          categoria: Value(_categoria),
          temperamento: Value(_temperamento),
          aptidao: Value(_aptidao),
          statusReprodutivo: Value(statusFinal),
          isReprodutor: Value(reprodutorFinal),
          caracteristicas: Value(_caracteristicas.text.trim()),
          fotoPerfil: const Value(''),
          ativo: const Value(true),
          updatedAt: Value(now),
        ));
        await db.enqueue(
          'create', 'animal',
          json.encode({
            'id': id,
            'propriedade': _propriedadeId,
            'brinco': _brinco.text.trim(),
            'raca': _raca,
            'sexo': _sexo,
            'data_nascimento': _dataNasc?.toIso8601String(),
            'categoria': _categoria,
            'temperamento': _temperamento,
            'aptidao': _aptidao,
            'status_reprodutivo': statusFinal,
            'is_reprodut': reprodutorFinal,
            'registro_genetico': _registroGenetico,
            'caracteristicas_adicionais': _caracteristicas.text.trim(),
            'foto_perfil': '',
            'ativo': true,
            'updated_at': now.toIso8601String(),
          }),
          clientId: 'tmp-${now.millisecondsSinceEpoch}',
        );

        // Após criar, abre o detalhe do animal para o usuário adicionar
        // pesagens, saúde e reprodução nas abas correspondentes
        final criado = await db.getById(id);
        if (!mounted) return;
        if (criado != null) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Animal cadastrado! Use as abas para adicionar pesagens, saúde e reprodução.'),
            duration: Duration(seconds: 4),
          ));
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => AnimalDetailScreen(animal: criado)),
          );
        } else {
          Navigator.of(context).pop(true);
        }
        return;
      }

      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (!mounted) return;
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Erro ao salvar: $e'),
        backgroundColor: Colors.red,
      ));
    }
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.animal != null;
    final cfg = _cfgFor(_tipoEspecie);

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: Text(isEdit ? 'Editar ${cfg.label}' : 'Novo ${cfg.label}',
            style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        actions: [
          if (_saving)
            const Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(width: 20, height: 20,
                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
            )
          else
            TextButton.icon(
              onPressed: _save,
              icon: const Icon(Icons.check, color: Colors.white),
              label: const Text('Salvar',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [

            // ── Identificação ─────────────────────────────────────────
            _Section(title: 'Identificação', children: [
              _Field(
                child: TextFormField(
                  controller: _brinco,
                  decoration: _dec(cfg.idLabel, Icons.tag, hint: cfg.idHint),
                  textCapitalization: TextCapitalization.characters,
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Campo obrigatório' : null,
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _raca,
                  decoration: _dec('Raça / Linhagem', Icons.biotech_outlined),
                  isExpanded: true,
                  items: cfg.racas
                      .map((r) => DropdownMenuItem(value: r.$1, child: Text(r.$2)))
                      .toList(),
                  onChanged: (v) => setState(() => _raca = v),
                  validator: (v) => v == null ? 'Selecione a raça' : null,
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _registroGenetico,
                  decoration:
                      _dec('Registro genético', Icons.workspace_premium_outlined),
                  isExpanded: true,
                  items: _registros
                      .map((r) => DropdownMenuItem(value: r.$1, child: Text(r.$2)))
                      .toList(),
                  onChanged: (v) => setState(() => _registroGenetico = v ?? 'COM'),
                ),
              ),
            ]),

            const SizedBox(height: 12),

            // ── Dados básicos ─────────────────────────────────────────
            _Section(title: 'Dados básicos', children: [
              _Field(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Sexo',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                    const SizedBox(height: 6),
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(
                            value: 'M',
                            label: Text('Macho'),
                            icon: Icon(Icons.male)),
                        ButtonSegment(
                            value: 'F',
                            label: Text('Fêmea'),
                            icon: Icon(Icons.female)),
                      ],
                      selected: {_sexo},
                      onSelectionChanged: (s) => setState(() {
                        _sexo = s.first;
                        if (_sexo == 'M') _statusReprodutivo = null;
                        if (_sexo == 'F') _isReprodutor = false;
                      }),
                      style: ButtonStyle(
                        foregroundColor: WidgetStateProperty.resolveWith((s) =>
                            s.contains(WidgetState.selected)
                                ? Colors.white
                                : _verde),
                        backgroundColor: WidgetStateProperty.resolveWith((s) =>
                            s.contains(WidgetState.selected)
                                ? _verde
                                : Colors.transparent),
                      ),
                    ),
                  ],
                ),
              ),
              _Field(
                child: InkWell(
                  onTap: _pickDate,
                  borderRadius: BorderRadius.circular(8),
                  child: InputDecorator(
                    decoration: _dec('Data de nascimento', Icons.cake_outlined),
                    child: Text(
                      _dataNasc != null
                          ? '${_dataNasc!.day.toString().padLeft(2, '0')}/'
                            '${_dataNasc!.month.toString().padLeft(2, '0')}/'
                            '${_dataNasc!.year}'
                          : 'Toque para selecionar',
                      style: TextStyle(
                        fontSize: 16,
                        color: _dataNasc != null
                            ? Colors.black87
                            : Colors.grey.shade500,
                      ),
                    ),
                  ),
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _categoria,
                  decoration: _dec('Categoria', Icons.category_outlined),
                  isExpanded: true,
                  items: cfg.categorias
                      .map((c) => DropdownMenuItem(value: c.$1, child: Text(c.$2)))
                      .toList(),
                  onChanged: (v) => setState(() => _categoria = v),
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _aptidao,
                  decoration: _dec('Aptidão / Finalidade', Icons.agriculture_outlined),
                  isExpanded: true,
                  items: cfg.aptidoes
                      .map((a) => DropdownMenuItem(value: a.$1, child: Text(a.$2)))
                      .toList(),
                  onChanged: (v) => setState(() => _aptidao = v),
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _temperamento,
                  decoration: _dec('Temperamento', Icons.mood_outlined),
                  isExpanded: true,
                  items: _temperamentos
                      .map((t) => DropdownMenuItem(value: t.$1, child: Text(t.$2)))
                      .toList(),
                  onChanged: (v) => setState(() => _temperamento = v),
                ),
              ),
            ]),

            const SizedBox(height: 12),

            // ── Reprodução (condicional) ──────────────────────────────
            _Section(title: 'Reprodução', children: [
              if (cfg.temStatus && _sexo == 'F')
                _Field(
                  child: DropdownButtonFormField<String>(
                    value: _statusReprodutivo,
                    decoration:
                        _dec('Status reprodutivo', Icons.child_friendly_outlined),
                    isExpanded: true,
                    items: _statusReprod
                        .map((s) => DropdownMenuItem(value: s.$1, child: Text(s.$2)))
                        .toList(),
                    onChanged: (v) => setState(() => _statusReprodutivo = v),
                  ),
                ),
              if (cfg.temReprodutor && _sexo == 'M')
                _Field(
                  child: SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _isReprodutor,
                    onChanged: (v) => setState(() => _isReprodutor = v),
                    title: Text(_tipoEspecie == 'EQUINOS'
                        ? 'É garanhão (reprodutor)'
                        : _tipoEspecie == 'SUINOS'
                            ? 'É varrão (reprodutor)'
                            : 'É reprodutor (touro/carneiro/bode)'),
                    activeThumbColor: _verde,
                  ),
                ),
              if (!cfg.temStatus && !cfg.temReprodutor)
                const _Field(
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 4),
                    child: Text(
                      'Sem campos reprodutivos específicos para esta espécie.',
                      style: TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ),
                ),
            ]),

            const SizedBox(height: 12),

            // ── Observações ──────────────────────────────────────────
            _Section(title: 'Observações', children: [
              _Field(
                child: TextFormField(
                  controller: _caracteristicas,
                  decoration:
                      _dec('Características adicionais', Icons.notes_outlined),
                  maxLines: 3,
                  minLines: 2,
                  textCapitalization: TextCapitalization.sentences,
                ),
              ),
            ]),

            const SizedBox(height: 24),

            FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: _verde,
                minimumSize: const Size.fromHeight(52),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: _saving ? null : _save,
              icon: _saving
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check),
              label: Text(
                isEdit ? 'Salvar alterações' : 'Cadastrar ${cfg.label.toLowerCase()}',
                style:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  InputDecoration _dec(String label, IconData icon, {String? hint}) =>
      InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon, color: _verde),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        filled: true,
        fillColor: Colors.white,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      );
}

// ── Widgets auxiliares ────────────────────────────────────────────────────────

class _Section extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const _Section({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 8),
          child: Text(title,
              style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  color: Color(0xFF2E7D32))),
        ),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: const [
              BoxShadow(
                  color: Colors.black12, blurRadius: 4, offset: Offset(0, 2))
            ],
          ),
          child: Column(children: children),
        ),
      ],
    );
  }
}

class _Field extends StatelessWidget {
  final Widget child;
  const _Field({required this.child});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      child: child,
    );
  }
}
