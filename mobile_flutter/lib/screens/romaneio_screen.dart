import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/romaneio_service.dart';
import '../ajuda/ajuda_bottom_sheet.dart';
import '../ajuda/ajuda_service.dart';
import '../services/api.dart';

class _AnimalEntry {
  final TextEditingController brinco = TextEditingController();
  final TextEditingController peso = TextEditingController();
  _AnimalEntry({String brincoVal = ''}) {
    brinco.text = brincoVal;
  }
  void dispose() {
    brinco.dispose();
    peso.dispose();
  }
}

class RomaneioScreen extends StatefulWidget {
  const RomaneioScreen({super.key});

  @override
  State<RomaneioScreen> createState() => _RomaneioScreenState();
}

class _RomaneioScreenState extends State<RomaneioScreen> {
  final _ajudaService = AjudaService(ApiService());
  final _precoCtrl = TextEditingController(text: '280.00');
  final _fazendaCtrl = TextEditingController();
  final _vendedorCtrl = TextEditingController();
  final _compradorCtrl = TextEditingController();

  final List<_AnimalEntry> _entradas = [_AnimalEntry()];

  bool _loading = false;
  ResultadoRomaneio? _resultado;
  String? _erro;

  static const _verde = Color(0xFF2E7D32);

  @override
  void dispose() {
    _precoCtrl.dispose();
    _fazendaCtrl.dispose();
    _vendedorCtrl.dispose();
    _compradorCtrl.dispose();
    for (final e in _entradas) {
      e.dispose();
    }
    super.dispose();
  }

  // Cálculo local em tempo real (sem chamar o backend)
  double get _precoArroba => double.tryParse(_precoCtrl.text.replaceAll(',', '.')) ?? 0;

  double get _totalPesoLocal {
    double t = 0;
    for (final e in _entradas) {
      t += double.tryParse(e.peso.text.replaceAll(',', '.')) ?? 0;
    }
    return t;
  }

  double get _totalArrobasLocal => _totalPesoLocal / 30.0;
  double get _totalValorLocal => _totalArrobasLocal * _precoArroba;

  void _addAnimal() {
    setState(() => _entradas.add(_AnimalEntry()));
  }

  void _removeAnimal(int idx) {
    if (_entradas.length == 1) return;
    setState(() {
      _entradas[idx].dispose();
      _entradas.removeAt(idx);
    });
  }

  Future<void> _calcular({bool gerarPdf = false}) async {
    final preco = _precoArroba;
    if (preco <= 0) {
      _showSnack('Informe o preço da @ válido.');
      return;
    }

    final animais = <Map<String, dynamic>>[];
    for (final e in _entradas) {
      final brinco = e.brinco.text.trim();
      final peso = double.tryParse(e.peso.text.replaceAll(',', '.')) ?? 0;
      if (brinco.isEmpty || peso <= 0) continue;
      animais.add({'brinco': brinco, 'peso_kg': peso});
    }
    if (animais.isEmpty) {
      _showSnack('Adicione pelo menos um animal com brinco e peso.');
      return;
    }

    setState(() {
      _loading = true;
      _erro = null;
      _resultado = null;
    });

    try {
      final res = await RomaneioService().calcular(
        precoArroba: preco,
        animais: animais,
        nomeFazenda: _fazendaCtrl.text.trim(),
        vendedor: _vendedorCtrl.text.trim(),
        comprador: _compradorCtrl.text.trim(),
        gerarPdf: gerarPdf,
      );
      setState(() => _resultado = res);
    } catch (e) {
      setState(() => _erro = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  void _showSnack(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: const Text('Romaneio de Pesagem',
            style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            tooltip: 'Ajuda',
            onPressed: () => mostrarAjuda(context, service: _ajudaService, moduloSlug: 'romaneio'),
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf),
            tooltip: 'Calcular + Gerar PDF',
            onPressed: _loading ? null : () => _calcular(gerarPdf: true),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Preço da arroba + info fazenda
            _SectionCard(
              title: 'Configuração',
              child: Column(
                children: [
                  _buildField(
                    controller: _precoCtrl,
                    label: 'Preço da Arroba (@) — R\$',
                    hint: 'Ex: 280.00',
                    icon: Icons.attach_money,
                    numeric: true,
                    onChanged: (_) => setState(() {}),
                  ),
                  const SizedBox(height: 10),
                  _buildField(
                      controller: _fazendaCtrl,
                      label: 'Fazenda',
                      hint: 'Nome da fazenda (opcional)',
                      icon: Icons.terrain),
                  const SizedBox(height: 10),
                  Row(children: [
                    Expanded(
                      child: _buildField(
                          controller: _vendedorCtrl,
                          label: 'Vendedor',
                          hint: 'Nome',
                          icon: Icons.person),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _buildField(
                          controller: _compradorCtrl,
                          label: 'Comprador',
                          hint: 'Nome',
                          icon: Icons.handshake),
                    ),
                  ]),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // Painel de totais em tempo real
            _TotaisCard(
              totalAnimais: _entradas
                  .where((e) =>
                      e.brinco.text.trim().isNotEmpty &&
                      (double.tryParse(e.peso.text.replaceAll(',', '.')) ?? 0) > 0)
                  .length,
              totalPeso: _totalPesoLocal,
              totalArrobas: _totalArrobasLocal,
              totalValor: _totalValorLocal,
            ),

            const SizedBox(height: 12),

            // Lista de animais
            _SectionCard(
              title: 'Animais',
              trailing: TextButton.icon(
                onPressed: _addAnimal,
                icon: const Icon(Icons.add, color: _verde),
                label: const Text('Adicionar', style: TextStyle(color: _verde)),
              ),
              child: Column(
                children: List.generate(
                  _entradas.length,
                  (i) => _AnimalRow(
                    entry: _entradas[i],
                    index: i,
                    onRemove: () => _removeAnimal(i),
                    onChanged: () => setState(() {}),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Botão calcular
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: _verde,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: _loading ? null : () => _calcular(),
              icon: _loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.calculate),
              label: Text(_loading ? 'Calculando...' : 'Calcular Romaneio',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),

            if (_erro != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200)),
                child: Text(_erro!, style: TextStyle(color: Colors.red.shade700)),
              ),
            ],

            // Resultado do backend
            if (_resultado != null) ...[
              const SizedBox(height: 16),
              _ResultadoPanel(resultado: _resultado!),
            ],

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    bool numeric = false,
    void Function(String)? onChanged,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: numeric
          ? const TextInputType.numberWithOptions(decimal: true)
          : TextInputType.text,
      inputFormatters: numeric
          ? [FilteringTextInputFormatter.allow(RegExp(r'[0-9.,]'))]
          : null,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon, color: _verde),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: _verde, width: 2)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      ),
    );
  }
}

class _AnimalRow extends StatelessWidget {
  const _AnimalRow({
    required this.entry,
    required this.index,
    required this.onRemove,
    required this.onChanged,
  });

  final _AnimalEntry entry;
  final int index;
  final VoidCallback onRemove;
  final VoidCallback onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          // Número do animal
          Container(
            width: 28,
            height: 28,
            alignment: Alignment.center,
            decoration: const BoxDecoration(
                color: Color(0xFF2E7D32), shape: BoxShape.circle),
            child: Text('${index + 1}',
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 8),
          // Brinco
          Expanded(
            flex: 2,
            child: TextFormField(
              controller: entry.brinco,
              onChanged: (_) => onChanged(),
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(
                labelText: 'Brinco',
                hintText: 'Ex: B-001',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              ),
            ),
          ),
          const SizedBox(width: 8),
          // Peso
          Expanded(
            flex: 2,
            child: TextFormField(
              controller: entry.peso,
              onChanged: (_) => onChanged(),
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[0-9.,]'))
              ],
              decoration: InputDecoration(
                labelText: 'Peso (kg)',
                hintText: '450.0',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              ),
            ),
          ),
          const SizedBox(width: 4),
          // Arrobas calculadas ao vivo
          SizedBox(
            width: 58,
            child: Column(
              children: [
                Text(
                  '${((double.tryParse(entry.peso.text.replaceAll(',', '.')) ?? 0) / 30).toStringAsFixed(1)}@',
                  style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2E7D32)),
                ),
                const Text('arrobas', style: TextStyle(fontSize: 9, color: Colors.grey)),
              ],
            ),
          ),
          // Remover
          IconButton(
            icon: const Icon(Icons.remove_circle_outline, color: Colors.red),
            onPressed: onRemove,
            padding: EdgeInsets.zero,
          ),
        ],
      ),
    );
  }
}

class _TotaisCard extends StatelessWidget {
  const _TotaisCard({
    required this.totalAnimais,
    required this.totalPeso,
    required this.totalArrobas,
    required this.totalValor,
  });

  final int totalAnimais;
  final double totalPeso;
  final double totalArrobas;
  final double totalValor;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF2E7D32),
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _Tot(label: 'Animais', value: '$totalAnimais', unit: 'cabeças'),
          _Tot(label: 'Peso Total', value: totalPeso.toStringAsFixed(0), unit: 'kg'),
          _Tot(label: 'Total @', value: totalArrobas.toStringAsFixed(1), unit: 'arrobas'),
          _Tot(
            label: 'Valor Total',
            value: 'R\$ ${totalValor.toStringAsFixed(0)}',
            unit: '',
            big: true,
          ),
        ],
      ),
    );
  }
}

class _Tot extends StatelessWidget {
  const _Tot(
      {required this.label,
      required this.value,
      required this.unit,
      this.big = false});
  final String label;
  final String value;
  final String unit;
  final bool big;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label,
            style: const TextStyle(color: Colors.white70, fontSize: 10)),
        Text(value,
            style: TextStyle(
                color: Colors.white,
                fontSize: big ? 18 : 15,
                fontWeight: FontWeight.bold)),
        if (unit.isNotEmpty)
          Text(unit, style: const TextStyle(color: Colors.white70, fontSize: 9)),
      ],
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child, this.trailing});
  final String title;
  final Widget child;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 8, 0),
            child: Row(
              children: [
                Text(title,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: Color(0xFF2E7D32))),
                const Spacer(),
                if (trailing != null) trailing!,
              ],
            ),
          ),
          const Divider(height: 12),
          Padding(padding: const EdgeInsets.fromLTRB(12, 0, 12, 12), child: child),
        ],
      ),
    );
  }
}

class _ResultadoPanel extends StatelessWidget {
  const _ResultadoPanel({required this.resultado});
  final ResultadoRomaneio resultado;

  @override
  Widget build(BuildContext context) {
    final r = resultado.resumo;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFE8F5E9),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFF81C784)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Resumo do Romaneio',
                  style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: Color(0xFF1B5E20))),
              const SizedBox(height: 8),
              _Row('Data / Hora', r.dataHora),
              _Row('Animais', '${r.totalAnimais} cabeças'),
              _Row('Peso Total', '${r.totalPesoKg.toStringAsFixed(1)} kg'),
              _Row('Total em Arrobas', '${r.totalArrobas.toStringAsFixed(2)} @'),
              _Row('Preço da @', 'R\$ ${r.precoArroba.toStringAsFixed(2)}'),
              const Divider(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('VALOR TOTAL DA NEGOCIAÇÃO',
                      style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                          color: Color(0xFF1B5E20))),
                  Text('R\$ ${r.totalValorRs.toStringAsFixed(2)}',
                      style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                          color: Color(0xFF2E7D32))),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        // Tabela dos itens
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: Colors.green.shade100),
          ),
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                decoration: const BoxDecoration(
                  color: Color(0xFF2E7D32),
                  borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(10),
                      topRight: Radius.circular(10)),
                ),
                child: const Row(
                  children: [
                    Expanded(flex: 2, child: _Th('Brinco')),
                    Expanded(flex: 2, child: _Th('Raça')),
                    Expanded(flex: 1, child: _Th('Kg', right: true)),
                    Expanded(flex: 1, child: _Th('@', right: true)),
                    Expanded(flex: 2, child: _Th('R\$', right: true)),
                  ],
                ),
              ),
              // Linhas
              ...resultado.itens.asMap().entries.map((entry) {
                final i = entry.key;
                final item = entry.value;
                return Container(
                  color: i.isEven ? const Color(0xFFF9FBE7) : Colors.white,
                  padding:
                      const EdgeInsets.symmetric(vertical: 7, horizontal: 12),
                  child: Row(
                    children: [
                      Expanded(
                          flex: 2,
                          child: Text(item.brinco,
                              style: const TextStyle(fontWeight: FontWeight.bold))),
                      Expanded(
                          flex: 2,
                          child: Text(item.raca.isEmpty ? '—' : item.raca,
                              style: const TextStyle(fontSize: 12))),
                      Expanded(
                          flex: 1,
                          child: Text(item.pesoKg.toStringAsFixed(0),
                              textAlign: TextAlign.right,
                              style: const TextStyle(fontSize: 12))),
                      Expanded(
                          flex: 1,
                          child: Text(item.arrobas.toStringAsFixed(1),
                              textAlign: TextAlign.right,
                              style: const TextStyle(fontSize: 12))),
                      Expanded(
                          flex: 2,
                          child: Text(
                              'R\$ ${item.valorRs.toStringAsFixed(0)}',
                              textAlign: TextAlign.right,
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF2E7D32)))),
                    ],
                  ),
                );
              }),
            ],
          ),
        ),
        if (resultado.pdfBase64 != null) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: Row(
              children: [
                Icon(Icons.picture_as_pdf, color: Colors.blue.shade700),
                const SizedBox(width: 8),
                Expanded(
                  child: Text('PDF gerado com sucesso!',
                      style: TextStyle(
                          color: Colors.blue.shade700,
                          fontWeight: FontWeight.bold)),
                ),
                TextButton(
                  onPressed: () {
                    // Copiar base64 para área de transferência (para debug/demo)
                    Clipboard.setData(
                        ClipboardData(text: resultado.pdfBase64!));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text('PDF base64 copiado para clipboard')),
                    );
                  },
                  child: const Text('Copiar'),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _Row extends StatelessWidget {
  const _Row(this.label, this.value);
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.black54, fontSize: 12)),
          Text(value,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
        ],
      ),
    );
  }
}

class _Th extends StatelessWidget {
  const _Th(this.text, {this.right = false});
  final String text;
  final bool right;

  @override
  Widget build(BuildContext context) {
    return Text(text,
        textAlign: right ? TextAlign.right : TextAlign.left,
        style: const TextStyle(
            color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold));
  }
}
