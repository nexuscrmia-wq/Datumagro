import 'package:flutter/material.dart';
import '../services/api.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  static const _verde = Color(0xFF2E7D32);

  final _pageCtrl = PageController();
  int _passo = 0;
  bool _loading = false;

  // Passo 1 — conta
  final _formKey = GlobalKey<FormState>();
  final _nomeCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _pass2Ctrl = TextEditingController();
  bool _obscure1 = true;
  bool _obscure2 = true;

  // Passo 2 — atividade
  String _tipoEspecie = 'BOVINOS_CORTE';
  String _faixaRebanho = '1-50';
  String _tipoOperacao = 'CORTE';

  // Passo 3 — localização + desafio
  String _estado = 'SP';
  final _cidadeCtrl = TextEditingController();
  final _propNomeCtrl = TextEditingController();
  String _desafio = 'Controle de pesagem e GMD';

  @override
  void dispose() {
    _pageCtrl.dispose();
    _nomeCtrl.dispose();
    _emailCtrl.dispose();
    _passCtrl.dispose();
    _pass2Ctrl.dispose();
    _cidadeCtrl.dispose();
    _propNomeCtrl.dispose();
    super.dispose();
  }

  // ── Passo 1: criar conta ─────────────────────────────────────────────────

  Future<void> _criarConta() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);

    final result = await ApiService().register(
      email: _emailCtrl.text.trim(),
      password: _passCtrl.text,
      password2: _pass2Ctrl.text,
      nomeCompleto: _nomeCtrl.text.trim(),
    );

    setState(() => _loading = false);

    if (!mounted) return;
    if (result['success'] == true) {
      _irParaPasso(1);
    } else {
      final err = result['error'];
      String msg = 'Erro ao criar conta.';
      if (err is Map) {
        final first = err.values.firstOrNull;
        if (first is List && first.isNotEmpty) msg = first.first.toString();
        if (first is String) msg = first;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(msg),
        backgroundColor: Colors.red.shade700,
      ));
    }
  }

  // ── Passo 3: salvar questionário e finalizar ─────────────────────────────

  Future<void> _finalizar() async {
    setState(() => _loading = true);
    try {
      final api = ApiService();
      // Salva atividade (etapa 3)
      await api.patchOnboarding({
        'etapa': 3,
        'tipo_especie': _tipoEspecie,
        'faixa_rebanho': _faixaRebanho,
        'tipo_operacao': _tipoOperacao,
      });
      // Salva localização (etapa 2)
      await api.patchOnboarding({
        'etapa': 2,
        'propriedade_estado': _estado,
        'propriedade_cidade': _cidadeCtrl.text.trim(),
        'nome_empresa': _propNomeCtrl.text.trim().isNotEmpty
            ? _propNomeCtrl.text.trim()
            : null,
      });
      // Finaliza onboarding (etapa 4)
      await api.patchOnboarding({
        'etapa': 4,
        'principal_desafio': _desafio,
      });
    } catch (_) {
      // Falha silenciosa: questionário é opcional; aprovação já está pendente
    } finally {
      setState(() => _loading = false);
    }
    if (!mounted) return;
    Navigator.of(context).pushReplacementNamed('/pending');
  }

  void _irParaPasso(int passo) {
    setState(() => _passo = passo);
    _pageCtrl.animateToPage(
      passo,
      duration: const Duration(milliseconds: 350),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: Text(
          ['Criar Conta', 'Sua Atividade', 'Sua Fazenda'][_passo],
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        leading: _passo > 0
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => _irParaPasso(_passo - 1),
              )
            : null,
      ),
      body: Column(
        children: [
          // Indicador de progresso
          _StepIndicator(passo: _passo, total: 3),

          Expanded(
            child: PageView(
              controller: _pageCtrl,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildPasso1(),
                _buildPasso2(),
                _buildPasso3(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── PASSO 1: Conta ────────────────────────────────────────────────────────

  Widget _buildPasso1() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 8),
          const Icon(Icons.agriculture, size: 56, color: _verde),
          const SizedBox(height: 12),
          const Text(
            'Bem-vindo ao DatumAgro',
            textAlign: TextAlign.center,
            style: TextStyle(
                fontSize: 20, fontWeight: FontWeight.bold, color: _verde),
          ),
          const SizedBox(height: 4),
          const Text(
            'Crie sua conta de proprietário',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.black54, fontSize: 13),
          ),
          const SizedBox(height: 28),
          Form(
            key: _formKey,
            child: Column(
              children: [
                _campo(
                  controller: _nomeCtrl,
                  label: 'Nome completo',
                  icon: Icons.person_outline,
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Informe seu nome' : null,
                ),
                const SizedBox(height: 14),
                _campo(
                  controller: _emailCtrl,
                  label: 'E-mail',
                  icon: Icons.email_outlined,
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Informe o e-mail';
                    if (!v.contains('@')) return 'E-mail inválido';
                    return null;
                  },
                ),
                const SizedBox(height: 14),
                _campo(
                  controller: _passCtrl,
                  label: 'Senha',
                  icon: Icons.lock_outline,
                  obscure: _obscure1,
                  suffixIcon: IconButton(
                    icon: Icon(_obscure1
                        ? Icons.visibility_off
                        : Icons.visibility),
                    onPressed: () => setState(() => _obscure1 = !_obscure1),
                  ),
                  validator: (v) =>
                      (v == null || v.length < 6) ? 'Mínimo 6 caracteres' : null,
                ),
                const SizedBox(height: 14),
                _campo(
                  controller: _pass2Ctrl,
                  label: 'Confirmar senha',
                  icon: Icons.lock_outline,
                  obscure: _obscure2,
                  suffixIcon: IconButton(
                    icon: Icon(_obscure2
                        ? Icons.visibility_off
                        : Icons.visibility),
                    onPressed: () => setState(() => _obscure2 = !_obscure2),
                  ),
                  validator: (v) =>
                      v != _passCtrl.text ? 'As senhas não coincidem' : null,
                ),
                const SizedBox(height: 28),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _verde,
                    foregroundColor: Colors.white,
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: _loading ? null : _criarConta,
                  child: _loading
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2))
                      : const Text('Próximo →',
                          style: TextStyle(
                              fontSize: 16, fontWeight: FontWeight.bold)),
                ),
                const SizedBox(height: 16),
                TextButton(
                  onPressed: () =>
                      Navigator.of(context).pushReplacementNamed('/login'),
                  child: const Text('Já tenho conta — Entrar',
                      style: TextStyle(
                          color: _verde, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── PASSO 2: Atividade ────────────────────────────────────────────────────

  Widget _buildPasso2() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Qual é sua atividade principal?',
              style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Color(0xFF1B5E20))),
          const SizedBox(height: 12),
          _ChipGroup<String>(
            opcoes: const {
              'BOVINOS_CORTE': '🐄 Pecuária de Corte',
              'BOVINOS_LEITE': '🥛 Pecuária de Leite',
              'SUINOS': '🐖 Suinocultura',
              'EQUINOS': '🐎 Equinocultura',
              'OVINOS_CAPRINOS': '🐑 Ovinos / Caprinos',
            },
            selecionado: _tipoEspecie,
            onChanged: (v) => setState(() => _tipoEspecie = v),
          ),

          const SizedBox(height: 24),
          const Text('Porte do rebanho / plantel',
              style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Color(0xFF1B5E20))),
          const SizedBox(height: 12),
          _ChipGroup<String>(
            opcoes: const {
              '1-50': '1 – 50 cabeças',
              '51-200': '51 – 200',
              '201-500': '201 – 500',
              '501-1000': '501 – 1000',
              '1000+': 'Acima de 1000',
            },
            selecionado: _faixaRebanho,
            onChanged: (v) => setState(() => _faixaRebanho = v),
          ),

          const SizedBox(height: 24),
          const Text('Tipo de operação',
              style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Color(0xFF1B5E20))),
          const SizedBox(height: 12),
          _ChipGroup<String>(
            opcoes: const {
              'CORTE': '🥩 Corte',
              'LEITE': '🥛 Leite',
              'MISTO': '🔄 Misto (Corte + Leite)',
            },
            selecionado: _tipoOperacao,
            onChanged: (v) => setState(() => _tipoOperacao = v),
          ),

          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: _verde,
                foregroundColor: Colors.white,
                minimumSize: const Size.fromHeight(50),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: () => _irParaPasso(2),
              child: const Text('Próximo →',
                  style:
                      TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  // ── PASSO 3: Fazenda ──────────────────────────────────────────────────────

  Widget _buildPasso3() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Onde fica sua fazenda?',
              style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Color(0xFF1B5E20))),
          const SizedBox(height: 14),

          // Estado
          DropdownButtonFormField<String>(
            initialValue: _estado,
            decoration: InputDecoration(
              labelText: 'Estado (UF)',
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Colors.white,
            ),
            items: _estados
                .map((e) =>
                    DropdownMenuItem(value: e, child: Text(e)))
                .toList(),
            onChanged: (v) => setState(() => _estado = v!),
          ),
          const SizedBox(height: 14),

          _campo(
            controller: _cidadeCtrl,
            label: 'Cidade',
            icon: Icons.location_city,
          ),
          const SizedBox(height: 14),

          _campo(
            controller: _propNomeCtrl,
            label: 'Nome da fazenda / propriedade',
            icon: Icons.home_work_outlined,
            hint: 'Ex: Fazenda São João',
          ),

          const SizedBox(height: 24),
          const Text('Qual seu maior desafio hoje?',
              style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Color(0xFF1B5E20))),
          const SizedBox(height: 12),
          _ChipGroup<String>(
            opcoes: const {
              'Controle de pesagem e GMD': '⚖️ Controle de pesagem e GMD',
              'Gestão financeira': '💰 Gestão financeira',
              'Rastreabilidade': '🏷️ Rastreabilidade',
              'Manejos sanitários': '💉 Manejos sanitários',
              'Gestão de equipe': '👥 Gestão de equipe',
              'Mapear a propriedade': '🗺️ Mapear a propriedade',
            },
            selecionado: _desafio,
            onChanged: (v) => setState(() => _desafio = v),
          ),

          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: _verde,
                minimumSize: const Size.fromHeight(52),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: _loading ? null : _finalizar,
              child: _loading
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                          color: Colors.white, strokeWidth: 2))
                  : const Text('Finalizar e aguardar aprovação',
                      style: TextStyle(
                          fontSize: 15, fontWeight: FontWeight.bold)),
            ),
          ),

          const SizedBox(height: 12),
          Center(
            child: Text(
              'Você receberá uma confirmação quando\nsua conta for aprovada.',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: Colors.grey.shade500, fontSize: 12, height: 1.5),
            ),
          ),
        ],
      ),
    );
  }

  Widget _campo({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType keyboardType = TextInputType.text,
    bool obscure = false,
    Widget? suffixIcon,
    String? hint,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscure,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon, color: _verde),
        suffixIcon: suffixIcon,
        border:
            OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: _verde, width: 2),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
    );
  }
}

// ─── Indicador de etapas ──────────────────────────────────────────────────────

class _StepIndicator extends StatelessWidget {
  final int passo;
  final int total;
  const _StepIndicator({required this.passo, required this.total});

  static const _corBarra = Color(0xFF2E7D32);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: _corBarra,
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 12),
      child: Row(
        children: List.generate(total, (i) {
          final done = i < passo;
          final active = i == passo;
          return Expanded(
            child: Padding(
              padding: EdgeInsets.only(right: i < total - 1 ? 6 : 0),
              child: Column(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    height: 4,
                    decoration: BoxDecoration(
                      color: (done || active)
                          ? Colors.white
                          : Colors.white.withValues(alpha: 0.3),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    ['Conta', 'Atividade', 'Fazenda'][i],
                    style: TextStyle(
                      color: (done || active)
                          ? Colors.white
                          : Colors.white.withValues(alpha: 0.5),
                      fontSize: 9,
                      fontWeight: active
                          ? FontWeight.bold
                          : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
      ),
    );
  }
}

// ─── Chip group de seleção única ──────────────────────────────────────────────

class _ChipGroup<T> extends StatelessWidget {
  final Map<T, String> opcoes;
  final T selecionado;
  final void Function(T) onChanged;

  const _ChipGroup({
    required this.opcoes,
    required this.selecionado,
    required this.onChanged,
  });

  static const _verde = Color(0xFF2E7D32);

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: opcoes.entries.map((e) {
        final selected = e.key == selecionado;
        return GestureDetector(
          onTap: () => onChanged(e.key),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            padding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: selected
                  ? _verde
                  : Colors.white,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: selected
                    ? _verde
                    : Colors.grey.shade300,
                width: selected ? 1.5 : 1,
              ),
              boxShadow: selected
                  ? [
                      const BoxShadow(
                          color: Color(0x302E7D32),
                          blurRadius: 6,
                          offset: Offset(0, 2))
                    ]
                  : null,
            ),
            child: Text(
              e.value,
              style: TextStyle(
                color: selected ? Colors.white : Colors.grey.shade700,
                fontWeight: selected
                    ? FontWeight.bold
                    : FontWeight.normal,
                fontSize: 13,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}

// ─── Estados brasileiros ──────────────────────────────────────────────────────

const _estados = [
  'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN',
  'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO',
];
