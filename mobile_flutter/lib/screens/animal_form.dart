import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:provider/provider.dart';
import 'package:datumagro_mobile/data/database.dart';
import 'package:drift/drift.dart' show Value;

import '../services/api.dart';

// ─── Opções com labels do backend ────────────────────────────────────────────

const _racas = [
  ('NELORE', 'Nelore'), ('ANGUS', 'Angus'), ('BRAHMAN', 'Brahman'),
  ('BRANGUS', 'Brangus'), ('SENEPOL', 'Senepol'), ('GUZERA', 'Guzerá'),
  ('TABAPUA', 'Tabapuã'), ('GIR', 'Gir Leiteiro'), ('GIROLANDO', 'Girolando'),
  ('HEREFORD', 'Hereford'), ('BRAFORD', 'Braford'), ('CARACU', 'Caracu'),
  ('OUTRA', 'Outra/Mestiço'),
];

const _categorias = [
  ('BEZERRO', 'Bezerro(a)'), ('NOVILHA', 'Novilha'), ('GARROTE', 'Garrote'),
  ('TOURO', 'Touro'), ('MATRIZ', 'Matriz (Vaca)'), ('BOI', 'Boi (Engorda)'),
];

const _temperamentos = [
  ('MANSO', 'Manso'), ('NORMAL', 'Normal'), ('BRABO', 'Brabo'), ('AGRESSIVO', 'Agressivo'),
];

const _aptidoes = [
  ('CORTE', 'Corte'), ('LEITE', 'Leite'), ('DUPLA', 'Dupla Aptidão'),
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

  static const _verde = Color(0xFF2E7D32);
  static const _storage = FlutterSecureStorage();

  @override
  void initState() {
    super.initState();
    _loadPropriedade();
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
      // registroGenetico não está no modelo Drift local — mantém COM
    }
  }

  Future<void> _loadPropriedade() async {
    // Tenta ler o ID da propriedade do usuário armazenado
    try {
      final s = await _storage.read(key: 'user');
      if (s != null) {
        final data = json.decode(s) as Map<String, dynamic>;
        final props = data['propriedades'] as List<dynamic>?;
        if (props != null && props.isNotEmpty) {
          final id = (props.first as Map)['id'];
          if (id != null && mounted) setState(() => _propriedadeId = id as int);
          return;
        }
      }
    } catch (_) {}

    // Fallback: buscar primeira propriedade da API
    try {
      final api = ApiService();
      final list = await api.fetchPropriedades();
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
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
      helpText: 'Data de nascimento',
      locale: const Locale('pt', 'BR'),
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

    try {
      if (isEdit) {
        final updated = widget.animal!.copyWith(
          brinco: _brinco.text.trim(),
          raca: Value(_raca),
          sexo: Value(_sexo),
          dataNascimento: Value(_dataNasc),
          categoria: Value(_categoria),
          temperamento: Value(_temperamento),
          aptidao: Value(_aptidao),
          statusReprodutivo: Value(_sexo == 'F' ? _statusReprodutivo : null),
          isReprodutor: _sexo == 'M' ? _isReprodutor : false,
          caracteristicas: Value(_caracteristicas.text.trim()),
          updatedAt: Value(now),
        );
        await db.updateAnimalEntry(updated);
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
            'status_reprodutivo': _sexo == 'F' ? _statusReprodutivo : null,
            'is_reprodut': _sexo == 'M' ? _isReprodutor : false,
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
          statusReprodutivo: Value(_sexo == 'F' ? _statusReprodutivo : null),
          isReprodutor: Value(_sexo == 'M' ? _isReprodutor : false),
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
            'status_reprodutivo': _sexo == 'F' ? _statusReprodutivo : null,
            'is_reprodut': _sexo == 'M' ? _isReprodutor : false,
            'registro_genetico': _registroGenetico,
            'caracteristicas_adicionais': _caracteristicas.text.trim(),
            'foto_perfil': '',
            'ativo': true,
            'updated_at': now.toIso8601String(),
          }),
          clientId: 'tmp-${now.millisecondsSinceEpoch}',
        );
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
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: Text(isEdit ? 'Editar Animal' : 'Novo Animal',
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
              label: const Text('Salvar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // ── Identificação ───────────────────────────────────────────
            _Section(title: 'Identificação', children: [
              _Field(
                child: TextFormField(
                  controller: _brinco,
                  decoration: _dec('Número do brinco / ID', Icons.tag),
                  textCapitalization: TextCapitalization.characters,
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Brinco é obrigatório' : null,
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _raca,
                  decoration: _dec('Raça', Icons.biotech_outlined),
                  isExpanded: true,
                  items: _racas.map((r) => DropdownMenuItem(value: r.$1, child: Text(r.$2))).toList(),
                  onChanged: (v) => setState(() => _raca = v),
                  validator: (v) => v == null ? 'Selecione a raça' : null,
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _registroGenetico,
                  decoration: _dec('Registro genético', Icons.workspace_premium_outlined),
                  isExpanded: true,
                  items: _registros.map((r) => DropdownMenuItem(value: r.$1, child: Text(r.$2))).toList(),
                  onChanged: (v) => setState(() => _registroGenetico = v ?? 'COM'),
                ),
              ),
            ]),

            const SizedBox(height: 12),

            // ── Dados básicos ───────────────────────────────────────────
            _Section(title: 'Dados básicos', children: [
              _Field(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Sexo', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                    const SizedBox(height: 6),
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'M', label: Text('Macho'), icon: Icon(Icons.male)),
                        ButtonSegment(value: 'F', label: Text('Fêmea'), icon: Icon(Icons.female)),
                      ],
                      selected: {_sexo},
                      onSelectionChanged: (s) => setState(() {
                        _sexo = s.first;
                        // Limpa campos condicionais ao trocar sexo
                        if (_sexo == 'M') _statusReprodutivo = null;
                        if (_sexo == 'F') _isReprodutor = false;
                      }),
                      style: ButtonStyle(
                        foregroundColor: WidgetStateProperty.resolveWith((s) =>
                            s.contains(WidgetState.selected) ? Colors.white : _verde),
                        backgroundColor: WidgetStateProperty.resolveWith((s) =>
                            s.contains(WidgetState.selected) ? _verde : Colors.transparent),
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
                          ? '${_dataNasc!.day.toString().padLeft(2, '0')}/${_dataNasc!.month.toString().padLeft(2, '0')}/${_dataNasc!.year}'
                          : 'Toque para selecionar',
                      style: TextStyle(
                        fontSize: 16,
                        color: _dataNasc != null ? Colors.black87 : Colors.grey.shade500,
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
                  items: _categorias.map((c) => DropdownMenuItem(value: c.$1, child: Text(c.$2))).toList(),
                  onChanged: (v) => setState(() => _categoria = v),
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _aptidao,
                  decoration: _dec('Aptidão', Icons.agriculture_outlined),
                  isExpanded: true,
                  items: _aptidoes.map((a) => DropdownMenuItem(value: a.$1, child: Text(a.$2))).toList(),
                  onChanged: (v) => setState(() => _aptidao = v),
                ),
              ),
              _Field(
                child: DropdownButtonFormField<String>(
                  value: _temperamento,
                  decoration: _dec('Temperamento', Icons.mood_outlined),
                  isExpanded: true,
                  items: _temperamentos.map((t) => DropdownMenuItem(value: t.$1, child: Text(t.$2))).toList(),
                  onChanged: (v) => setState(() => _temperamento = v),
                ),
              ),
            ]),

            const SizedBox(height: 12),

            // ── Reprodução (condicional) ─────────────────────────────────
            _Section(title: 'Reprodução', children: [
              if (_sexo == 'F') ...[
                _Field(
                  child: DropdownButtonFormField<String>(
                    value: _statusReprodutivo,
                    decoration: _dec('Status reprodutivo', Icons.child_friendly_outlined),
                    isExpanded: true,
                    items: _statusReprod.map((s) => DropdownMenuItem(value: s.$1, child: Text(s.$2))).toList(),
                    onChanged: (v) => setState(() => _statusReprodutivo = v),
                  ),
                ),
              ],
              if (_sexo == 'M') ...[
                _Field(
                  child: SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    value: _isReprodutor,
                    onChanged: (v) => setState(() => _isReprodutor = v),
                    title: const Text('É reprodutor (touro)'),
                    subtitle: const Text('Ative se este macho é usado como reprodutor'),
                    activeThumbColor: _verde,
                  ),
                ),
              ],
              if (_sexo == 'F' && _statusReprodutivo == null && _sexo == 'F')
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                  child: Text(
                    'Selecione o status reprodutivo para fêmeas em idade adulta.',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                  ),
                ),
            ]),

            const SizedBox(height: 12),

            // ── Observações ─────────────────────────────────────────────
            _Section(title: 'Observações', children: [
              _Field(
                child: TextFormField(
                  controller: _caracteristicas,
                  decoration: _dec('Características adicionais', Icons.notes_outlined),
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
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: _saving ? null : _save,
              icon: _saving
                  ? const SizedBox(width: 18, height: 18,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check),
              label: Text(isEdit ? 'Salvar alterações' : 'Cadastrar animal',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  InputDecoration _dec(String label, IconData icon) => InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: _verde),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
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
              BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2))
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
