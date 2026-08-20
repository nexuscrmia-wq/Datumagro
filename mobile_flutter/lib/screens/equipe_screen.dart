import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api.dart';
import '../config.dart';

class EquipeScreen extends StatefulWidget {
  const EquipeScreen({super.key});

  @override
  State<EquipeScreen> createState() => _EquipeScreenState();
}

class _EquipeScreenState extends State<EquipeScreen> {
  static const _verde = Color(0xFF6A1B9A);
  final _api = ApiService();

  List<Map<String, dynamic>> _membros = [];
  bool _loading = true;
  String? _erro;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _erro = null; });
    try {
      final resp = await _api.authenticatedGet(
        Uri.parse('$kApiBaseUrlEmulator/api/equipe/membros/'),
      );
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body);
        setState(() {
          _membros = List<Map<String, dynamic>>.from(data is List ? data : []);
          _loading = false;
        });
      } else {
        setState(() { _erro = 'Erro ${resp.statusCode}'; _loading = false; });
      }
    } catch (e) {
      setState(() { _erro = 'Sem conexão'; _loading = false; });
    }
  }

  Future<void> _convidar() async {
    final emailCtrl = TextEditingController();
    String cargo = 'OPERADOR';

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Convidar membro'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: emailCtrl,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'E-mail do funcionário',
                  prefixIcon: Icon(Icons.email_outlined),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: cargo,
                decoration: const InputDecoration(
                  labelText: 'Cargo / Função',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'OPERADOR', child: Text('Operador')),
                  DropdownMenuItem(value: 'GERENTE', child: Text('Gerente')),
                  DropdownMenuItem(value: 'VETERINARIO', child: Text('Veterinário')),
                ],
                onChanged: (v) => setSt(() => cargo = v ?? 'OPERADOR'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: _verde),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Enviar convite'),
            ),
          ],
        ),
      ),
    );

    if (result != true) return;
    final email = emailCtrl.text.trim();
    if (email.isEmpty) return;

    try {
      final resp = await _api.authenticatedPost(
        Uri.parse('$kApiBaseUrlEmulator/api/equipe/convidar/'),
        {'email': email, 'cargo': cargo},
      );
      if (mounted) {
        if (resp.statusCode == 201) {
          final data = json.decode(resp.body);
          final codigo = data['invite']?['codigo'] ?? '';
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Convite enviado! Código: $codigo'),
              backgroundColor: Colors.green,
            ),
          );
          _load();
        } else {
          final body = json.decode(resp.body);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(body['detail'] ?? 'Erro ao convidar'), backgroundColor: Colors.red),
          );
        }
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Sem conexão'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _remover(int id, String nome) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Remover membro'),
        content: Text('Remover $nome da equipe?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Remover'),
          ),
        ],
      ),
    );
    if (confirm != true) return;

    try {
      final resp = await _api.authenticatedDelete(
        Uri.parse('$kApiBaseUrlEmulator/api/equipe/membros/$id/remover/'),
      );
      if (mounted) {
        if (resp.statusCode == 200 || resp.statusCode == 204) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Membro removido'), backgroundColor: Colors.green),
          );
          _load();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Erro ao remover'), backgroundColor: Colors.red),
          );
        }
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Equipe'),
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _load,
            tooltip: 'Atualizar',
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _convidar,
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.person_add_outlined),
        label: const Text('Convidar'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _erro != null
              ? _buildError()
              : _membros.isEmpty
                  ? _buildEmpty()
                  : _buildList(),
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
              color: _verde.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.group_outlined, size: 40, color: _verde),
          ),
          const SizedBox(height: 20),
          Text('Nenhum membro na equipe',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.grey.shade800)),
          const SizedBox(height: 8),
          Text('Convide funcionários para gerenciar sua propriedade juntos.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: Colors.grey.shade600, height: 1.5)),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: _convidar,
            style: FilledButton.styleFrom(backgroundColor: _verde),
            icon: const Icon(Icons.person_add_outlined),
            label: const Text('Convidar primeiro membro'),
          ),
        ],
      ),
    ),
  );

  Widget _buildList() => ListView.separated(
    padding: const EdgeInsets.all(16),
    itemCount: _membros.length,
    separatorBuilder: (_, __) => const SizedBox(height: 8),
    itemBuilder: (_, i) {
      final m = _membros[i];
      final user = m['user'] as Map<String, dynamic>? ?? m;
      final nome = user['nome'] as String? ?? user['nome_completo'] as String? ?? 'Membro';
      final email = user['email'] as String? ?? '';
      final cargo = m['cargo'] as String? ?? 'OPERADOR';
      final id = m['id'] as int? ?? 0;
      final ingresso = m['data_ingresso'] as String?;

      return Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Colors.grey.shade200),
        ),
        child: ListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          leading: CircleAvatar(
            backgroundColor: _verde.withValues(alpha: 0.15),
            child: Text(
              nome.isNotEmpty ? nome[0].toUpperCase() : '?',
              style: TextStyle(color: _verde, fontWeight: FontWeight.bold),
            ),
          ),
          title: Text(nome, style: const TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (email.isNotEmpty) Text(email, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
              if (ingresso != null) ...[
                const SizedBox(height: 2),
                Text('Desde ${ingresso.split('T').first}',
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade500)),
              ],
            ],
          ),
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _CargoBadge(cargo: cargo),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.remove_circle_outline, color: Colors.red, size: 22),
                onPressed: () => _remover(id, nome),
                tooltip: 'Remover',
              ),
            ],
          ),
        ),
      );
    },
  );
}

class _CargoBadge extends StatelessWidget {
  final String cargo;
  const _CargoBadge({required this.cargo});

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (cargo.toUpperCase()) {
      'GERENTE' => ('Gerente', Colors.blue),
      'VETERINARIO' => ('Vet.', Colors.teal),
      'PROPRIETARIO' => ('Proprietário', const Color(0xFF2E7D32)),
      _ => ('Operador', Colors.orange),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600)),
    );
  }
}
