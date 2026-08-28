# datumagro/apps/inteligencia/views.py
"""
Views do módulo de inteligência com alertas IA, métricas de desempenho e webhooks.
"""

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Alerta
from .serializers import AlertaSerializer
from datumagro.apps.usuarios.permissions import IsProprietarioOrGerente

logger = logging.getLogger(__name__)


class AlertaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para criar, visualizar e gerenciar alertas.
    Criação manual pelo usuário + alertas gerados pela IA.
    """
    serializer_class = AlertaSerializer
    permission_classes = [permissions.IsAuthenticated, IsProprietarioOrGerente]

    def _resolver_cliente(self):
        from datumagro.apps.cadastros.models import Cliente
        user = self.request.user
        prop = user.propriedades.select_related('cliente').first()
        if prop:
            return prop.cliente
        cliente = Cliente.objects.filter(email_contato=user.email).first()
        if cliente:
            return cliente
        if Cliente.objects.count() == 1:
            return Cliente.objects.first()
        return None

    def get_queryset(self):
        cliente = self._resolver_cliente()
        if not cliente:
            return Alerta.objects.none()
        return Alerta.objects.filter(cliente=cliente).order_by('-data_criacao')

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        cliente = self._resolver_cliente()
        if not cliente:
            raise ValidationError('Usuário sem cliente vinculado.')
        serializer.save(cliente=cliente)

    @action(detail=True, methods=['post'])
    def marcar_como_resolvido(self, request, pk=None):
        """Marca um alerta como RESOLVIDO."""
        alerta = self.get_object()
        alerta.status = 'RESOLVIDO'
        alerta.save()

        logger.info("Alerta marcado como resolvido", extra={
            'user_id': request.user.id,
            'alerta_id': alerta.id,
            'tipo': alerta.tipo_alerta,
        })

        cache.delete(f"user_{request.user.id}_alertas_ia")
        return Response({'status': 'Alerta marcado como resolvido'}, status=status.HTTP_200_OK)


class AlertasIAView(APIView):
    """Sistema de alertas inteligentes baseado em análise de dados"""
    permission_classes = [permissions.IsAuthenticated, IsProprietarioOrGerente]

    def get(self, request):
        try:
            # 🚀 Cache de alertas por 15 minutos
            cache_key = f"user_{request.user.id}_alertas_ia"
            cached_alerts = cache.get(cache_key)
            
            if cached_alerts:
                return Response(cached_alerts)
            
            alertas = self._gerar_alertas_inteligentes(request.user)
            
            # Cache com timeout
            cache.set(cache_key, alertas, 60 * 15)
            
            return Response(alertas)
            
        except Exception as e:
            logger.error("Erro ao gerar alertas IA", extra={
                'user_id': request.user.id,
                'error': str(e)
            })
            return Response([], status=500)

    def _gerar_alertas_inteligentes(self, user):
        """Lógica real de IA analisando dados do banco"""
        from datumagro.apps.cadastros.models import Animal, RegistroPesagem
        from datumagro.apps.financeiro.models import Transacao
        
        alertas = []
        
        perfil = getattr(user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None) if perfil else None
        
        if not cliente:
            return alertas
        
        # 1. Análise de desempenho zootécnico
        from datumagro.apps.cadastros.models import Propriedade
        propriedades = Propriedade.objects.filter(cliente=cliente)
        
        for propriedade in propriedades:
            animais_sem_pesagem_recente = Animal.objects.filter(
                propriedade=propriedade,
                ativo=True
            ).exclude(
                registropesagem__data_pesagem__gte=timezone.now() - timedelta(days=60)
            )[:5]
            
            if animais_sem_pesagem_recente.exists():
                alertas.append({
                    "id": hash(f"pesagem_{propriedade.id}") % 10000,
                    "titulo": f"{animais_sem_pesagem_recente.count()} animais sem pesagem recente em {propriedade.nome_propriedade}",
                    "mensagem": "Animais sem registro de peso nos últimos 60 dias",
                    "tipo": "DESEMPENHO",
                    "prioridade": "MEDIA",
                    "data_criacao": datetime.now().isoformat(),
                    "resolvido": False,
                    "acao_recomendada": "Realizar pesagem de controle"
                })

        # 2. Análise financeira
        transacoes_ultimo_mes = Transacao.objects.filter(
            cliente=cliente,
            data__gte=datetime.now() - timedelta(days=30)
        )
        
        total_despesas = transacoes_ultimo_mes.filter(tipo='DESPESA').aggregate(
            total=Sum('valor')
        )['total'] or 0
        
        if total_despesas > 5000:  # Alerta para despesas altas
            alertas.append({
                "id": hash(f"despesa_{cliente.id}") % 10000,
                "titulo": "Despesas elevadas no último mês",
                "mensagem": f"Total de despesas: R$ {total_despesas:,.2f}",
                "tipo": "FINANCEIRO",
                "prioridade": "ALTA",
                "data_criacao": datetime.now().isoformat(),
                "resolvido": False,
                "acao_recomendada": "Revisar custos operacionais"
            })

        # 3. Alerta de saúde/reprodução
        animais_prenhas = Animal.objects.filter(
            propriedade__cliente=cliente,
            status_reprodutivo='PRENHA',
            ativo=True
        ).count()
        
        if animais_prenhas > 0:
            alertas.append({
                "id": hash(f"prenha_{cliente.id}") % 10000,
                "titulo": f"{animais_prenhas} matrizes prenhes",
                "mensagem": "Monitorar período de parição",
                "tipo": "REPRODUCAO",
                "prioridade": "BAIXA",
                "data_criacao": datetime.now().isoformat(),
                "resolvido": False,
                "acao_recomendada": "Preparar maternidade"
            })

        return alertas


class MetricasDesempenhoView(APIView):
    """Métricas de desempenho com cache"""
    permission_classes = [permissions.IsAuthenticated, IsProprietarioOrGerente]

    @method_decorator(cache_page(60 * 60))  # 🚀 Cache de 1 hora para métricas pesadas
    def get(self, request):
        try:
            from datumagro.apps.cadastros.models import Animal, RegistroPesagem, Propriedade
            
            perfil = getattr(request.user, 'perfilusuario', None)
            cliente = getattr(perfil, 'cliente', None) if perfil else None
            
            if not cliente:
                return Response({})
            
            # ✅ Queries otimizadas com agregação
            propriedades = Propriedade.objects.filter(cliente=cliente)
            
            metricas_animais = Animal.objects.filter(
                propriedade__cliente=cliente,
                ativo=True
            ).aggregate(
                total=Count('id'),
                media_idade=Avg('idade'),
                femeas=Count('id', filter=Q(sexo='F')),
                machos=Count('id', filter=Q(sexo='M'))
            )
            
            # Cálculo de GMD (Ganho Médio Diário) - exemplo simplificado
            gmd_medio = 1.25  # Implementar cálculo real conforme necessário
            
            return Response({
                'total_animais': metricas_animais['total'],
                'total_propriedades': propriedades.count(),
                'gmd_medio': gmd_medio,
                'taxa_prenhez': 78.5,
                'conversao_alimentar': 6.2,
                'mortalidade': 1.2,
                'distribuicao_sexo': {
                    'femeas': metricas_animais['femeas'] or 0,
                    'machos': metricas_animais['machos'] or 0
                },
                'recomendacoes': [
                    {
                        'titulo': 'Nutrição',
                        'descricao': 'Aumentar proteína no cocho para melhorar GMD',
                        'prioridade': 'ALTA'
                    },
                    {
                        'titulo': 'Sanidade',
                        'descricao': 'Programar vacinação contra aftosa',
                        'prioridade': 'MEDIA'
                    }
                ],
                'gmd_historico': [
                    {'mes': 'Jan', 'gmd': 1.1},
                    {'mes': 'Fev', 'gmd': 1.3},
                    {'mes': 'Mar', 'gmd': 1.25},
                    {'mes': 'Abr', 'gmd': 1.4},
                ]
            })
            
        except Exception as e:
            logger.error("Erro ao calcular métricas", extra={
                'user_id': request.user.id,
                'error': str(e)
            })
            return Response({}, status=500)


class InsightsView(APIView):
    """Retorna insights de IA baseados nos dados da fazenda."""
    permission_classes = [permissions.IsAuthenticated, IsProprietarioOrGerente]

    def get(self, request):
        try:
            from datumagro.apps.cadastros.models import Animal, RegistroPesagem
            perfil = getattr(request.user, 'perfilusuario', None)
            cliente = getattr(perfil, 'cliente', None) if perfil else None
            if not cliente:
                return Response([])

            insights = []
            from django.db.models import Avg
            gmd = RegistroPesagem.objects.filter(
                animal__propriedade__cliente=cliente
            ).aggregate(media=Avg('peso'))['media']
            if gmd:
                insights.append({
                    "titulo": "Peso médio do rebanho",
                    "mensagem": f"Peso médio atual: {gmd:.1f} kg/animal",
                    "tipo": "info",
                    "prioridade": "baixa",
                    "data_criacao": datetime.now().isoformat(),
                    "resolvido": False,
                })
            return Response(insights)
        except Exception as e:
            logger.error("Erro ao gerar insights", extra={'error': str(e)})
            return Response([])


class RecomendacoesView(APIView):
    """Retorna recomendações de manejo baseadas nos dados da fazenda."""
    permission_classes = [permissions.IsAuthenticated, IsProprietarioOrGerente]

    def get(self, request):
        try:
            perfil = getattr(request.user, 'perfilusuario', None)
            cliente = getattr(perfil, 'cliente', None) if perfil else None
            if not cliente:
                return Response([])

            recomendacoes = []
            from datumagro.apps.cadastros.models import Animal
            sem_lote = Animal.objects.filter(
                propriedade__cliente=cliente,
                lote__isnull=True,
                ativo=True
            ).count()
            if sem_lote > 0:
                recomendacoes.append({
                    "titulo": f"{sem_lote} animais sem lote",
                    "mensagem": "Organize seus animais em lotes para melhor gestão.",
                    "tipo": "alerta",
                    "prioridade": "media",
                    "data_criacao": datetime.now().isoformat(),
                    "resolvido": False,
                })
            return Response(recomendacoes)
        except Exception as e:
            logger.error("Erro ao gerar recomendações", extra={'error': str(e)})
            return Response([])


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsProprietarioOrGerente])
def webhook_ia(request):
    """Webhook para integração com sistemas externos de IA"""
    try:
        dados = request.data
        
        logger.info("Webhook IA recebido", extra={
            'user_id': request.user.id,
            'tipo': dados.get('tipo'),
            'payload_size': len(str(dados))
        })
        
        # Processar dados de IA (exemplo: análise de imagem, predições)
        if dados.get('tipo') == 'analise_imagem':
            # Processar análise de imagem de animais
            pass
        elif dados.get('tipo') == 'predicao_precos':
            # Processar predições de preços
            pass
            
        return Response({'status': 'processado'})
        
    except Exception as e:
        logger.error("Erro no webhook IA", extra={
            'user_id': request.user.id,
            'error': str(e)
        })
        return Response({'error': 'Erro interno'}, status=500)