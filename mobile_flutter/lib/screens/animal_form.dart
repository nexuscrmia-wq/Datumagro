import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:datumagro_mobile/data/database.dart';
import 'package:drift/drift.dart' show Value;

class AnimalFormScreen extends StatefulWidget {
  final Animal? animal; // null = create, non-null = edit

  const AnimalFormScreen({super.key, this.animal});

  @override
  State<AnimalFormScreen> createState() => _AnimalFormScreenState();
}

class _AnimalFormScreenState extends State<AnimalFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _brinco = TextEditingController();
  final _raca = TextEditingController();
  final _sexo = TextEditingController();
  final _dataNasc = TextEditingController();
  final _categoria = TextEditingController();
  final _temperamento = TextEditingController();
  final _aptidao = TextEditingController();
  final _statusReprod = TextEditingController();
  bool _isReprodutor = false;
  String _registroGenetico = 'COM';
  final _caracteristicas = TextEditingController();
  final _pai = TextEditingController();
  final _mae = TextEditingController();

  late final AppDatabase db;

  @override
  void initState() {
    super.initState();
    final a = widget.animal;
    if (a != null) {
      _brinco.text = a.brinco;
      _raca.text = a.raca ?? '';
      _sexo.text = a.sexo ?? '';
      _dataNasc.text = a.dataNascimento?.toIso8601String().split('T').first ?? '';
      _categoria.text = a.categoria ?? '';
      _temperamento.text = a.temperamento ?? '';
      _aptidao.text = a.aptidao ?? '';
      _statusReprod.text = a.statusReprodutivo ?? '';
      _isReprodutor = a.isReprodutor;
      _caracteristicas.text = a.caracteristicas ?? '';
      _pai.text = a.paiId?.toString() ?? '';
      _mae.text = a.maeId?.toString() ?? '';
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    db = Provider.of<AppDatabase>(context, listen: false);
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    DateTime? parsedDate;
    try {
      parsedDate = DateTime.parse(_dataNasc.text);
    } catch (_) {
      parsedDate = DateTime.now();
    }

    final isEdit = widget.animal != null;
    final now = DateTime.now();

    if (isEdit) {
      final updated = widget.animal!.copyWith(
        brinco: _brinco.text,
        raca: Value(_raca.text),
        sexo: Value(_sexo.text.isNotEmpty ? _sexo.text : 'M'),
        dataNascimento: Value(parsedDate),
        categoria: Value(_categoria.text),
        temperamento: Value(_temperamento.text),
        aptidao: Value(_aptidao.text),
        statusReprodutivo: Value(_statusReprod.text),
        isReprodutor: _isReprodutor,
        caracteristicas: Value(_caracteristicas.text),
        paiId: Value(_pai.text.isNotEmpty ? int.tryParse(_pai.text) : null),
        maeId: Value(_mae.text.isNotEmpty ? int.tryParse(_mae.text) : null),
        updatedAt: Value(now),
      );
      await db.updateAnimalEntry(updated);
      final payload = json.encode({
        'id': widget.animal!.serverId ?? widget.animal!.id,
        'brinco': _brinco.text,
        'raca': _raca.text,
        'sexo': _sexo.text,
        'data_nascimento': parsedDate.toIso8601String(),
        'categoria': _categoria.text,
        'temperamento': _temperamento.text,
        'aptidao': _aptidao.text,
        'status_reprodutivo': _statusReprod.text,
        'is_reprodut': _isReprodutor,
        'registro_genetico': _registroGenetico,
        'caracteristicas_adicionais': _caracteristicas.text,
      });
      await db.enqueue('update', 'animal', payload,
          clientId: 'upd-${widget.animal!.id}-${now.millisecondsSinceEpoch}');
    } else {
      final entry = AnimalsCompanion.insert(
        propriedadeId: 1,
        brinco: _brinco.text,
        raca: Value(_raca.text),
        sexo: Value(_sexo.text.isNotEmpty ? _sexo.text : 'M'),
        dataNascimento: Value(parsedDate),
        categoria: Value(_categoria.text),
        temperamento: Value(_temperamento.text),
        aptidao: Value(_aptidao.text),
        statusReprodutivo: Value(_statusReprod.text),
        isReprodutor: Value(_isReprodutor),
        caracteristicas: Value(_caracteristicas.text),
        paiId: Value(_pai.text.isNotEmpty ? int.tryParse(_pai.text) : null),
        maeId: Value(_mae.text.isNotEmpty ? int.tryParse(_mae.text) : null),
        fotoPerfil: const Value(''),
        ativo: const Value(true),
        updatedAt: Value(now),
      );
      final id = await db.insertAnimal(entry);
      final payload = json.encode({
        'id': id,
        'propriedade': 1,
        'brinco': _brinco.text,
        'raca': _raca.text,
        'sexo': _sexo.text,
        'data_nascimento': parsedDate.toIso8601String(),
        'categoria': _categoria.text,
        'temperamento': _temperamento.text,
        'aptidao': _aptidao.text,
        'status_reprodutivo': _statusReprod.text,
        'is_reprodut': _isReprodutor,
        'registro_genetico': _registroGenetico,
        'caracteristicas_adicionais': _caracteristicas.text,
        'pai': _pai.text.isNotEmpty ? int.tryParse(_pai.text) : null,
        'mae': _mae.text.isNotEmpty ? int.tryParse(_mae.text) : null,
        'foto_perfil': '',
        'ativo': true,
        'updated_at': now.toIso8601String(),
      });
      await db.enqueue('create', 'animal', payload,
          clientId: 'tmp-${now.millisecondsSinceEpoch}');
    }

    if (mounted) Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.animal != null;
    return Scaffold(
      appBar: AppBar(title: Text(isEdit ? 'Editar Animal' : 'Novo Animal')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(controller: _brinco, decoration: const InputDecoration(labelText: 'Brinco')),
              TextFormField(controller: _raca, decoration: const InputDecoration(labelText: 'Raça')),
              TextFormField(controller: _sexo, decoration: const InputDecoration(labelText: 'Sexo (M/F)')),
              TextFormField(controller: _dataNasc, decoration: const InputDecoration(labelText: 'Data Nascimento (YYYY-MM-DD)')),
              TextFormField(controller: _categoria, decoration: const InputDecoration(labelText: 'Categoria')),
              TextFormField(controller: _temperamento, decoration: const InputDecoration(labelText: 'Temperamento')),
              TextFormField(controller: _aptidao, decoration: const InputDecoration(labelText: 'Aptidão')),
              TextFormField(controller: _statusReprod, decoration: const InputDecoration(labelText: 'Status Reprodutivo')),
              Row(children: [
                const Text('É reprodutor?'),
                Checkbox(value: _isReprodutor, onChanged: (v) => setState(() => _isReprodutor = v ?? false)),
              ]),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _registroGenetico,
                decoration: const InputDecoration(labelText: 'Registro Genético'),
                items: const [
                  DropdownMenuItem(value: 'COM', child: Text('Comercial (sem registro)')),
                  DropdownMenuItem(value: 'PO',  child: Text('🟢 Puro de Origem (PO)')),
                  DropdownMenuItem(value: 'PC',  child: Text('🟡 Puro por Cruza (PC)')),
                  DropdownMenuItem(value: 'PA',  child: Text('🔵 Puro por Absorção (PA)')),
                ],
                onChanged: (v) => setState(() => _registroGenetico = v ?? 'COM'),
              ),
              const SizedBox(height: 8),
              TextFormField(controller: _caracteristicas, decoration: const InputDecoration(labelText: 'Características adicionais')),
              TextFormField(controller: _pai, decoration: const InputDecoration(labelText: 'ID do Pai (opcional)'), keyboardType: TextInputType.number),
              TextFormField(controller: _mae, decoration: const InputDecoration(labelText: 'ID da Mãe (opcional)'), keyboardType: TextInputType.number),
              const SizedBox(height: 20),
              ElevatedButton(onPressed: _save, child: const Text('Salvar (offline)')),
            ],
          ),
        ),
      ),
    );
  }
}
