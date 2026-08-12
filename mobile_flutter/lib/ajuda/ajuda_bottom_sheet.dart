import 'package:flutter/material.dart';
import 'ajuda_service.dart';

const _verde = Color(0xFF2E7D32);

/// Abre o modal de ajuda contextual de uma tela.
///
/// ```dart
/// mostrarAjuda(context, service: ajudaService, moduloSlug: 'mapa');
/// ```
Future<void> mostrarAjuda(
  BuildContext context, {
  required AjudaService service,
  required String moduloSlug,
}) {
  return showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => _AjudaSheet(service: service, moduloSlug: moduloSlug),
  );
}

class _AjudaSheet extends StatefulWidget {
  final AjudaService service;
  final String moduloSlug;

  const _AjudaSheet({required this.service, required this.moduloSlug});

  @override
  State<_AjudaSheet> createState() => _AjudaSheetState();
}

class _AjudaSheetState extends State<_AjudaSheet>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs;
  late final Future<GuiaModulo> _guiaFuture;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
    _guiaFuture = widget.service.buscarGuia(widget.moduloSlug);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.62,
      minChildSize: 0.4,
      maxChildSize: 0.92,
      expand: false,
      builder: (context, scrollCtrl) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            // ── handle ──
            Container(
              margin: const EdgeInsets.only(top: 10, bottom: 4),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // ── conteúdo ──
            Expanded(
              child: FutureBuilder<GuiaModulo>(
                future: _guiaFuture,
                builder: (context, snap) {
                  if (snap.connectionState != ConnectionState.done) {
                    return const Center(child: CircularProgressIndicator(color: _verde));
                  }

                  if (snap.hasError) {
                    return Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.wifi_off_rounded,
                              size: 48, color: Colors.grey.shade400),
                          const SizedBox(height: 16),
                          Text(
                            'Não foi possível carregar a ajuda desta tela.\n'
                            'Verifique sua conexão e tente novamente.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey.shade600),
                          ),
                        ],
                      ),
                    );
                  }

                  final guia = snap.data!;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // título
                      Padding(
                        padding:
                            const EdgeInsets.fromLTRB(20, 12, 20, 0),
                        child: Text(
                          guia.titulo,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: _verde,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),

                      // tabs
                      TabBar(
                        controller: _tabs,
                        labelColor: _verde,
                        unselectedLabelColor: Colors.grey,
                        indicatorColor: _verde,
                        tabs: const [
                          Tab(
                            icon: Icon(Icons.menu_book_outlined),
                            text: 'Como usar',
                          ),
                          Tab(
                            icon: Icon(Icons.eco_outlined),
                            text: 'Dica do campo',
                          ),
                        ],
                      ),

                      // conteúdo das tabs
                      Expanded(
                        child: TabBarView(
                          controller: _tabs,
                          children: [
                            _Conteudo(
                              scrollCtrl: scrollCtrl,
                              texto: guia.comoUsar,
                              icone: Icons.checklist_rounded,
                            ),
                            _Conteudo(
                              scrollCtrl: scrollCtrl,
                              texto: guia.dicaAgro,
                              icone: Icons.agriculture_rounded,
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Conteudo extends StatelessWidget {
  final ScrollController scrollCtrl;
  final String texto;
  final IconData icone;

  const _Conteudo({
    required this.scrollCtrl,
    required this.texto,
    required this.icone,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      controller: scrollCtrl,
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icone, color: _verde, size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              texto,
              style: const TextStyle(height: 1.6, fontSize: 15),
            ),
          ),
        ],
      ),
    );
  }
}
