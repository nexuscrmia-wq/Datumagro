import 'package:flutter/material.dart';
import '../services/api.dart';
import '../ajuda/ajuda_bottom_sheet.dart';
import '../ajuda/ajuda_service.dart';

class FinanceiroScreen extends StatefulWidget {
  const FinanceiroScreen({super.key});

  @override
  State<FinanceiroScreen> createState() => _FinanceiroScreenState();
}

class _FinanceiroScreenState extends State<FinanceiroScreen>
    with SingleTickerProviderStateMixin {
  static const _verde = Color(0xFF2E7D32);
  static const _bg = Color(0xFFF1F8E9);

  late final TabController _tabs;
  final _api = ApiService();
  final _ajudaService = AjudaService(ApiService());

  Map<String, dynamic> _fluxo = {};
  List<Map<String, dynamic>> _transacoes = [];
  bool _loading = true;
  String? _erro;
  String _filtroTipo = 'TODOS';

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _tabs.addListener(() {
      if (!_tabs.indexIsChanging) {
        setState(() {
          _filtroTipo = ['TODOS', 'RECEITA', 'DESPESA'][_tabs.index];
        });
        _loadTransacoes();
      }
    });
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
      final results = await Future.wait([
        _api.fetchFluxoCaixa(),
        _api.fetchTransacoes(),
      ]);
      if (!mounted) return;
      setState(() {
        _fluxo = results[0] as Map<String, dynamic>;
        _transacoes = results[1] as List<Map<String, dynamic>>;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _erro = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _loadTransacoes() async {
    final tipo = _filtroTipo == 'TODOS' ? null : _filtroTipo;
    try {
      final list = await _api.fetchTransacoes(tipo: tipo);
      if (!mounted) return;
      setState(() => _transacoes = list);
    } catch (_) {}
  }

  void _abrirNovaTransacao() async {
    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _NovaTransacaoSheet(api: _api),
    );
    if (result == true) _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: const Text('Financeiro',
            style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            tooltip: 'Ajuda',
            onPressed: () =>
                mostrarAjuda(context, service: _ajudaService, moduloSlug: 'financeiro'),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Atualizar',
            onPressed: _load,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _abrirNovaTransacao,
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('Lançamento'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _verde))
          : _erro != null
              ? _buildErro()
              : _buildConteudo(),
    );
  }

  Widget _buildErro() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.wifi_off, size: 56, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('Sem conexão com o servidor',
                style: TextStyle(fontSize: 16, color: Colors.grey)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(backgroundColor: _verde),
              onPressed: _load,
              icon: const Icon(Icons.refresh, color: Colors.white),
              label: const Text('Tentar novamente',
                  style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConteudo() {
    final receitas = double.tryParse(_fluxo['receitas']?.toString() ?? '0') ?? 0;
    final despesas = double.tryParse(_fluxo['despesas']?.toString() ?? '0') ?? 0;
    final saldo = receitas - despesas;
    final periodo = _fluxo['periodo'] as String? ?? '';

    return RefreshIndicator(
      onRefresh: _load,
      color: _verde,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        children: [
          // ── Card de saldo ──────────────────────────────────────────────
          _SaldoCard(
            saldo: saldo,
            receitas: receitas,
            despesas: despesas,
            periodo: periodo,
          ),
          const SizedBox(height: 16),

          // ── Barra de progresso receita/despesa ─────────────────────────
          if (receitas > 0 || despesas > 0) ...[
            _BalanceBar(receitas: receitas, despesas: despesas),
            const SizedBox(height: 20),
          ],

          // ── Aba de filtro e lista ──────────────────────────────────────
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              boxShadow: const [
                BoxShadow(
                    color: Color(0x14000000),
                    blurRadius: 8,
                    offset: Offset(0, 2))
              ],
            ),
            child: Column(
              children: [
                TabBar(
                  controller: _tabs,
                  labelColor: _verde,
                  unselectedLabelColor: Colors.grey,
                  indicatorColor: _verde,
                  labelStyle: const TextStyle(fontWeight: FontWeight.w600),
                  tabs: const [
                    Tab(text: 'Todos'),
                    Tab(text: 'Receitas'),
                    Tab(text: 'Despesas'),
                  ],
                ),
                const Divider(height: 1),
                _transacoes.isEmpty
                    ? Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          children: [
                            Icon(Icons.receipt_long,
                                size: 48,
                                color: Colors.grey.shade300),
                            const SizedBox(height: 12),
                            Text(
                              'Nenhum lançamento encontrado.\nToque em + para adicionar.',
                              textAlign: TextAlign.center,
                              style: TextStyle(color: Colors.grey.shade500),
                            ),
                          ],
                        ),
                      )
                    : ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _transacoes.length,
                        separatorBuilder: (_, __) =>
                            const Divider(height: 1, indent: 56),
                        itemBuilder: (_, i) =>
                            _TransacaoTile(t: _transacoes[i]),
                      ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Card de Saldo ────────────────────────────────────────────────────────────

class _SaldoCard extends StatelessWidget {
  final double saldo;
  final double receitas;
  final double despesas;
  final String periodo;

  const _SaldoCard({
    required this.saldo,
    required this.receitas,
    required this.despesas,
    required this.periodo,
  });

  static const _verde = Color(0xFF2E7D32);
  static const _vermelho = Color(0xFFC62828);

  @override
  Widget build(BuildContext context) {
    final positive = saldo >= 0;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: positive
              ? [const Color(0xFF1B5E20), const Color(0xFF2E7D32)]
              : [const Color(0xFF7F0000), const Color(0xFFC62828)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: (positive ? _verde : _vermelho).withValues(alpha: 0.35),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.account_balance_wallet,
                  color: Colors.white70, size: 18),
              const SizedBox(width: 6),
              Text(
                'Saldo do mês${periodo.isNotEmpty ? ' · $periodo' : ''}',
                style:
                    const TextStyle(color: Colors.white70, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            _fmt(saldo),
            style: const TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
                fontFeatures: [FontFeature.tabularFigures()]),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _MiniStat(
                  icon: Icons.arrow_upward_rounded,
                  label: 'Receitas',
                  value: receitas,
                  cor: Colors.greenAccent.shade100,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _MiniStat(
                  icon: Icons.arrow_downward_rounded,
                  label: 'Despesas',
                  value: despesas,
                  cor: Colors.red.shade100,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _fmt(double v) {
    final abs = v.abs();
    final sign = v < 0 ? '-' : '';
    return '${sign}R\$ ${abs.toStringAsFixed(2).replaceAll('.', ',').replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+,)'), (m) => '${m[1]}.')}';
  }
}

class _MiniStat extends StatelessWidget {
  final IconData icon;
  final String label;
  final double value;
  final Color cor;

  const _MiniStat(
      {required this.icon,
      required this.label,
      required this.value,
      required this.cor});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Icon(icon, color: cor, size: 18),
          const SizedBox(width: 6),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style:
                        const TextStyle(color: Colors.white70, fontSize: 10)),
                Text(
                  'R\$ ${value.toStringAsFixed(2).replaceAll('.', ',')}',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      fontWeight: FontWeight.bold),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Barra de progresso ───────────────────────────────────────────────────────

class _BalanceBar extends StatelessWidget {
  final double receitas;
  final double despesas;

  const _BalanceBar({required this.receitas, required this.despesas});

  @override
  Widget build(BuildContext context) {
    final total = receitas + despesas;
    final fracR = total > 0 ? receitas / total : 0.5;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: const [
          BoxShadow(
              color: Color(0x14000000), blurRadius: 8, offset: Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Distribuição mensal',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Row(
              children: [
                Expanded(
                  flex: (fracR * 100).round(),
                  child: Container(height: 14, color: const Color(0xFF2E7D32)),
                ),
                Expanded(
                  flex: ((1 - fracR) * 100).round().clamp(1, 99),
                  child: Container(height: 14, color: const Color(0xFFC62828)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          const Row(
            children: [
              _Legenda(cor: Color(0xFF2E7D32), label: 'Receitas'),
              SizedBox(width: 16),
              _Legenda(cor: Color(0xFFC62828), label: 'Despesas'),
            ],
          ),
        ],
      ),
    );
  }
}

class _Legenda extends StatelessWidget {
  final Color cor;
  final String label;
  const _Legenda({required this.cor, required this.label});

  @override
  Widget build(BuildContext context) => Row(
        children: [
          Container(
              width: 10,
              height: 10,
              decoration:
                  BoxDecoration(color: cor, borderRadius: BorderRadius.circular(2))),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        ],
      );
}

// ─── Tile de transação ────────────────────────────────────────────────────────

class _TransacaoTile extends StatelessWidget {
  final Map<String, dynamic> t;
  const _TransacaoTile({required this.t});

  @override
  Widget build(BuildContext context) {
    final tipo = t['tipo'] as String? ?? 'DESPESA';
    final isReceita = tipo == 'RECEITA';
    final valor = double.tryParse(t['valor']?.toString() ?? '0') ?? 0;
    final descricao = t['descricao'] as String? ?? '—';
    final categoria = t['categoria_nome'] as String? ?? t['categoria']?.toString() ?? '';
    final data = (t['data'] as String? ?? '').replaceAll('-', '/');
    final status = t['status'] as String? ?? '';

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: isReceita
              ? const Color(0xFF2E7D32).withValues(alpha: 0.1)
              : const Color(0xFFC62828).withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(
          isReceita ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded,
          color: isReceita ? const Color(0xFF2E7D32) : const Color(0xFFC62828),
          size: 20,
        ),
      ),
      title: Text(descricao,
          style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14),
          overflow: TextOverflow.ellipsis),
      subtitle: Text(
        [if (categoria.isNotEmpty) categoria, data].join(' · '),
        style: const TextStyle(fontSize: 12, color: Colors.grey),
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '${isReceita ? '+' : '-'}R\$ ${valor.toStringAsFixed(2).replaceAll('.', ',')}',
            style: TextStyle(
              color: isReceita ? const Color(0xFF2E7D32) : const Color(0xFFC62828),
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          if (status == 'PENDENTE')
            Container(
              margin: const EdgeInsets.only(top: 2),
              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: Colors.orange.shade200),
              ),
              child: const Text('Pendente',
                  style: TextStyle(fontSize: 9, color: Colors.orange)),
            ),
        ],
      ),
    );
  }
}

// ─── Bottom Sheet: Nova Transação ─────────────────────────────────────────────

class _NovaTransacaoSheet extends StatefulWidget {
  final ApiService api;
  const _NovaTransacaoSheet({required this.api});

  @override
  State<_NovaTransacaoSheet> createState() => _NovaTransacaoSheetState();
}

class _NovaTransacaoSheetState extends State<_NovaTransacaoSheet> {
  static const _verde = Color(0xFF2E7D32);
  static const _vermelho = Color(0xFFC62828);

  String _tipo = 'DESPESA';
  final _descCtrl = TextEditingController();
  final _valorCtrl = TextEditingController();
  final _catCtrl = TextEditingController();
  final _dataCtrl = TextEditingController(
      text: DateTime.now().toIso8601String().split('T').first);
  bool _saving = false;
  String? _erro;

  @override
  void dispose() {
    _descCtrl.dispose();
    _valorCtrl.dispose();
    _catCtrl.dispose();
    _dataCtrl.dispose();
    super.dispose();
  }

  Future<void> _salvar() async {
    final desc = _descCtrl.text.trim();
    final valor = double.tryParse(_valorCtrl.text.replaceAll(',', '.'));
    if (desc.isEmpty || valor == null || valor <= 0) {
      setState(() => _erro = 'Preencha descrição e valor corretamente.');
      return;
    }
    setState(() {
      _saving = true;
      _erro = null;
    });
    try {
      await widget.api.criarTransacao(
        tipo: _tipo,
        valor: valor,
        data: _dataCtrl.text,
        descricao: desc,
        categoriaNome: _catCtrl.text.trim().isEmpty ? null : _catCtrl.text.trim(),
      );
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      setState(() {
        _erro = 'Erro ao salvar. Tente novamente.';
        _saving = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isReceita = _tipo == 'RECEITA';
    final cor = isReceita ? _verde : _vermelho;

    return Padding(
      padding:
          EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Novo Lançamento',
                style:
                    TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),

            // Tipo toggle
            Row(
              children: [
                Expanded(
                  child: _TipoBtn(
                    label: 'Despesa',
                    icon: Icons.arrow_downward_rounded,
                    cor: _vermelho,
                    selected: _tipo == 'DESPESA',
                    onTap: () => setState(() => _tipo = 'DESPESA'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _TipoBtn(
                    label: 'Receita',
                    icon: Icons.arrow_upward_rounded,
                    cor: _verde,
                    selected: _tipo == 'RECEITA',
                    onTap: () => setState(() => _tipo = 'RECEITA'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _descCtrl,
              decoration: InputDecoration(
                labelText: 'Descrição',
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10)),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide(color: cor, width: 2)),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _valorCtrl,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(
                      labelText: 'Valor (R\$)',
                      prefixText: 'R\$ ',
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10)),
                      focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: BorderSide(color: cor, width: 2)),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _dataCtrl,
                    decoration: InputDecoration(
                      labelText: 'Data',
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _catCtrl,
              decoration: InputDecoration(
                labelText: 'Categoria (opcional)',
                hintText: 'Ex: Nutrição, Sanidade',
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10)),
              ),
            ),

            if (_erro != null) ...[
              const SizedBox(height: 8),
              Text(_erro!,
                  style: const TextStyle(color: Colors.red, fontSize: 12)),
            ],
            const SizedBox(height: 20),

            SizedBox(
              width: double.infinity,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: cor,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: _saving ? null : _salvar,
                child: _saving
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            color: Colors.white, strokeWidth: 2))
                    : const Text('Salvar lançamento',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TipoBtn extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color cor;
  final bool selected;
  final VoidCallback onTap;

  const _TipoBtn(
      {required this.label,
      required this.icon,
      required this.cor,
      required this.selected,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: selected ? cor.withValues(alpha: 0.12) : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
              color: selected ? cor : Colors.transparent, width: 1.5),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: selected ? cor : Colors.grey, size: 18),
            const SizedBox(width: 6),
            Text(label,
                style: TextStyle(
                    color: selected ? cor : Colors.grey,
                    fontWeight: selected ? FontWeight.bold : FontWeight.normal)),
          ],
        ),
      ),
    );
  }
}
