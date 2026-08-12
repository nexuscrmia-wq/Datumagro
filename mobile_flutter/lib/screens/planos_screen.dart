import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api.dart';

// Planos padrão usados como fallback se a API não responder
const _fallback = [
  {
    'nome': 'Starter',
    'cap_descricao': 'Até 100 cabeças',
    'highlight': false,
    'recursos': [
      'Mapeamento via CAR (KML/GeoJSON)',
      'Pesagem com cálculo de GMD',
      'Passaporte sanitário digital',
      'Gestão multi-espécie',
      'Suporte por WhatsApp',
    ],
    'whatsapp_msg':
        'Ol%C3%A1%21%20Tenho%20interesse%20no%20plano%20Starter%20do%20DatumAgro.',
  },
  {
    'nome': 'Profissional',
    'cap_descricao': 'Até 500 cabeças',
    'highlight': true,
    'recursos': [
      'Tudo do Starter',
      'Alertas de manejo em tempo real',
      'Gestão financeira por lote',
      'Gestão de equipe e permissões (RBAC)',
      'Mapa interativo (piquetes + infraestrutura)',
      'Suporte prioritário',
    ],
    'whatsapp_msg':
        'Ol%C3%A1%21%20Tenho%20interesse%20no%20plano%20Profissional%20do%20DatumAgro.',
  },
  {
    'nome': 'Cooperativa',
    'cap_descricao': 'Ilimitado · multi-fazenda',
    'highlight': false,
    'recursos': [
      'Tudo do Profissional',
      'Múltiplas propriedades',
      'Relatórios consolidados',
      'API de integração',
      'Suporte dedicado',
    ],
    'whatsapp_msg':
        'Ol%C3%A1%21%20Tenho%20interesse%20no%20plano%20Cooperativa%20do%20DatumAgro.',
  },
];

class PlanosScreen extends StatefulWidget {
  const PlanosScreen({super.key});

  @override
  State<PlanosScreen> createState() => _PlanosScreenState();
}

class _PlanosScreenState extends State<PlanosScreen> {
  static const _verde = Color(0xFF2E7D32);
  static const _whatsappColor = Color(0xFF25D366);

  List<Map<String, dynamic>> _planos = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _carregarPlanos();
  }

  Future<void> _carregarPlanos() async {
    try {
      final lista = await ApiService().fetchPlanos();
      if (!mounted) return;
      setState(() {
        _planos = lista.isNotEmpty
            ? lista
            : List<Map<String, dynamic>>.from(_fallback);
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _planos = List<Map<String, dynamic>>.from(_fallback);
        _loading = false;
      });
    }
  }

  Future<void> _openWhatsApp(String msg) async {
    final url = Uri.parse('https://wa.me/5522988330445?text=$msg');
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      appBar: AppBar(
        backgroundColor: _verde,
        foregroundColor: Colors.white,
        title: const Text('Planos',
            style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _verde))
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 32),
              children: [
                // Header
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: _verde,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Column(
                    children: [
                      Text('Escolha o plano ideal',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold)),
                      SizedBox(height: 6),
                      Text(
                        'Preços personalizados conforme o tamanho da sua operação. '
                        'Converse com nossa equipe e receba uma proposta.',
                        textAlign: TextAlign.center,
                        style:
                            TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                ..._planos.map((p) => _PlanCard(
                      plan: p,
                      onConsultar: () {
                        final msg = (p['whatsapp_msg'] as String?)
                                ?.isNotEmpty ==
                            true
                            ? p['whatsapp_msg'] as String
                            : 'Ol%C3%A1%21%20Tenho%20interesse%20no%20plano%20${Uri.encodeComponent(p['nome'] as String? ?? '')}%20do%20DatumAgro.';
                        _openWhatsApp(msg);
                      },
                    )),

                const SizedBox(height: 8),

                GestureDetector(
                  onTap: () => _openWhatsApp(
                      'Ol%C3%A1%21%20Gostaria%20de%20saber%20mais%20sobre%20os%20planos%20do%20DatumAgro.'),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                        vertical: 18, horizontal: 20),
                    decoration: BoxDecoration(
                      color: _whatsappColor,
                      borderRadius: BorderRadius.circular(14),
                      boxShadow: const [
                        BoxShadow(
                            color: Color(0x4025D366),
                            blurRadius: 12,
                            offset: Offset(0, 4)),
                      ],
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('📱', style: TextStyle(fontSize: 22)),
                        SizedBox(width: 10),
                        Flexible(
                          child: Text(
                            'Falar com a equipe no WhatsApp',
                            style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 15),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),
                const Center(
                  child: Text(
                    'Sem contrato de fidelidade. Mude de plano conforme o rebanho cresce.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
              ],
            ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  final Map<String, dynamic> plan;
  final VoidCallback onConsultar;

  const _PlanCard({required this.plan, required this.onConsultar});

  static const _verde = Color(0xFF2E7D32);
  static const _gold = Color(0xFFF9A825);

  @override
  Widget build(BuildContext context) {
    final isHighlight = plan['highlight'] as bool? ?? false;
    final recursos = plan['recursos'];
    final items = recursos is List
        ? recursos.cast<String>()
        : <String>[];

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isHighlight ? _gold : Colors.transparent,
          width: isHighlight ? 2 : 0,
        ),
        boxShadow: [
          BoxShadow(
              color: Colors.black
                  .withValues(alpha: isHighlight ? 0.12 : 0.06),
              blurRadius: isHighlight ? 16 : 8,
              offset: const Offset(0, 3)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 14),
            decoration: BoxDecoration(
              color: isHighlight
                  ? _gold.withValues(alpha: 0.1)
                  : _verde.withValues(alpha: 0.05),
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(13)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (isHighlight)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          margin: const EdgeInsets.only(bottom: 6),
                          decoration: BoxDecoration(
                            color: _gold,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text('MAIS POPULAR',
                              style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                  letterSpacing: 0.8)),
                        ),
                      Text(plan['nome'] as String? ?? '',
                          style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: isHighlight ? _gold : _verde)),
                      Text(plan['cap_descricao'] as String? ?? '',
                          style: const TextStyle(
                              fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: (isHighlight ? _gold : _verde)
                        .withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text('Consultar',
                      style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: isHighlight ? _gold : _verde,
                          letterSpacing: 0.3)),
                ),
              ],
            ),
          ),

          // Recursos
          if (items.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(18, 12, 18, 4),
              child: Column(
                children: items
                    .map((item) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 5),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('✓ ',
                                  style: TextStyle(
                                      color: _verde,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13)),
                              Expanded(
                                child: Text(item,
                                    style: const TextStyle(
                                        fontSize: 13,
                                        color: Color(0xFF37474F))),
                              ),
                            ],
                          ),
                        ))
                    .toList(),
              ),
            ),

          // Botão
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 8, 18, 16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: isHighlight ? _gold : _verde,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 13),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                  elevation: 0,
                ),
                onPressed: onConsultar,
                child: const Text('Consultar via WhatsApp',
                    style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
