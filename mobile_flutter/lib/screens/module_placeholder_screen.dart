import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class ModulePlaceholderScreen extends StatelessWidget {
  final String title;
  final IconData icon;
  final String description;
  final Color? color;

  const ModulePlaceholderScreen({
    super.key,
    required this.title,
    required this.icon,
    required this.description,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final accent = color ?? const Color(0xFF2E7D32);
    final dark = Color.fromARGB(
      255,
      ((accent.r * 255.0).round() * 0.6).round(),
      ((accent.g * 255.0).round() * 0.6).round(),
      ((accent.b * 255.0).round() * 0.6).round(),
    );

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            backgroundColor: accent,
            foregroundColor: Colors.white,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [dark, accent],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SizedBox(height: 40),
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(icon, size: 42, color: Colors.white),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Badge em breve
                  Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 6),
                      decoration: BoxDecoration(
                        color: accent.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                            color: accent.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.rocket_launch,
                              size: 14, color: accent),
                          const SizedBox(width: 6),
                          Text(
                            'Módulo em desenvolvimento',
                            style: TextStyle(
                                color: accent,
                                fontWeight: FontWeight.w600,
                                fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Descrição
                  Text(
                    description,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: Colors.grey.shade700,
                        fontSize: 15,
                        height: 1.5),
                  ),

                  const SizedBox(height: 32),

                  // O que vem por aí
                  Text(
                    'O que você vai encontrar aqui',
                    style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: Colors.grey.shade800),
                  ),
                  const SizedBox(height: 12),

                  ..._features(title).map(
                    (f) => Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Row(
                        children: [
                          Container(
                            width: 36,
                            height: 36,
                            decoration: BoxDecoration(
                              color: accent.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Icon(f.$2, color: accent, size: 18),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(f.$1,
                                style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey.shade700)),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Botão de notificação
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: accent,
                        side: BorderSide(color: accent),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      icon: const Icon(Icons.notifications_none),
                      label: const Text('Avisar quando disponível',
                          style: TextStyle(fontWeight: FontWeight.w600)),
                      onPressed: () async {
                        final uri = Uri.parse(
                          'https://wa.me/5522988330445?text=Ol%C3%A1%21%20Quero%20ser%20avisado%20quando%20o%20m%C3%B3dulo%20de%20${Uri.encodeComponent(title)}%20estiver%20dispon%C3%ADvel.',
                        );
                        if (await canLaunchUrl(uri)) {
                          await launchUrl(uri,
                              mode: LaunchMode.externalApplication);
                        }
                      },
                    ),
                  ),

                  const SizedBox(height: 12),

                  Center(
                    child: Text(
                      'Sua opinião acelera o desenvolvimento.',
                      style: TextStyle(
                          color: Colors.grey.shade500, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  static List<(String, IconData)> _features(String title) {
    switch (title.toLowerCase()) {
      case 'financeiro':
        return [
          ('Controle de receitas e despesas por lote', Icons.receipt_long),
          ('Fluxo de caixa mensal com gráficos', Icons.show_chart),
          ('Categorias personalizadas de custo', Icons.category),
          ('Exportação de relatórios em PDF/Excel', Icons.download),
        ];
      case 'equipe':
        return [
          ('Convite de funcionários por e-mail', Icons.person_add),
          ('Controle de permissões por módulo (RBAC)', Icons.security),
          ('Histórico de atividades por usuário', Icons.history),
          ('Gestão de turno e tarefas', Icons.task_alt),
        ];
      case 'logística':
        return [
          ('Controle de embarques e guias de trânsito', Icons.local_shipping),
          ('Rastreabilidade por SISBOV / RFID', Icons.qr_code_scanner),
          ('Integração com frigoríficos', Icons.warehouse),
          ('Histórico de movimentações', Icons.timeline),
        ];
      case 'alertas e ia':
        return [
          ('Alertas sanitários e de vacinação', Icons.vaccines),
          ('Diagnósticos gerados por IA', Icons.psychology),
          ('Notificações de cio e parto', Icons.favorite),
          ('Alertas de anomalia de peso (GMD)', Icons.scale),
        ];
      default:
        return [
          ('Ferramentas avançadas de gestão', Icons.build),
          ('Relatórios e análises', Icons.bar_chart),
          ('Integração com outros módulos', Icons.hub),
        ];
    }
  }
}
