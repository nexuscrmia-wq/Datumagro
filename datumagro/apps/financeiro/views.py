# datumagro/apps/financeiro/views.py
"""
Views otimizadas para o módulo financeiro com cache e logging profissional.
"""

import logging
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Sum, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import date, timedelta

from .models import Transacao, Categoria, FormaPagamento
from .serializers import (
    TransacaoSerializer, CategoriaSerializer,
    FormaPagamentoSerializer
)
from datumagro.apps.cadastros.models import Cliente
from datumagro.apps.usuarios.permissions import PermissaoFinanceiro, CanDeleteData

logger = logging.getLogger(__name__)


def _resolver_cliente_financeiro(user):
    """Resolve o cliente do usuário sem nenhum fallback de segurança."""
    try:
        prop = user.propriedades.select_related('cliente').first()
        if prop and prop.cliente:
            return prop.cliente
    except Exception:
        pass
    try:
        if user.email:
            cliente = Cliente.objects.filter(email_contato=user.email).first()
            if cliente:
                return cliente
    except Exception:
        pass
    return None


class CategoriaViewSet(viewsets.ModelViewSet):
    """ViewSet otimizado para categorias financeiras com cache"""
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated, PermissaoFinanceiro, CanDeleteData]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['tipo']
    search_fields = ['nome']

    def get_queryset(self):
        cliente = _resolver_cliente_financeiro(self.request.user)
        if cliente is None:
            return Categoria.objects.none()
        return Categoria.objects.filter(cliente=cliente)

    def perform_create(self, serializer):
        cliente = _resolver_cliente_financeiro(self.request.user)
        if cliente is None:
            raise serializers.ValidationError({'detail': 'Usuário sem cliente vinculado.'})
        instance = serializer.save(cliente=cliente)
        # 🚀 Invalida cache de relatórios (usando delete ao invés de delete_pattern)
        try:
            cache.delete(f"user_{self.request.user.id}_financeiro_categorias")
            cache.delete(f"user_{self.request.user.id}_financeiro_relatorios")
        except AttributeError:
            # LocMemCache não suporta delete_pattern, então apenas log
            pass
        logger.info("Categoria criada", extra={
            'user_id': self.request.user.id,
            'categoria_id': instance.id,
            'categoria_nome': instance.nome
        })

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # 🚀 Invalida cache de relatórios
        try:
            cache.delete(f"user_{self.request.user.id}_financeiro_categorias")
            cache.delete(f"user_{self.request.user.id}_financeiro_transacoes")
            cache.delete(f"user_{self.request.user.id}_financeiro_relatorios")
        except AttributeError:
            pass

    def perform_destroy(self, instance):
        instance_id = instance.id
        super().perform_destroy(instance)
        # 🚀 Invalida cache de relatórios
        try:
            cache.delete(f"user_{self.request.user.id}_financeiro_categorias")
            cache.delete(f"user_{self.request.user.id}_financeiro_relatorios")
        except AttributeError:
            pass
        logger.info("Categoria deletada", extra={
            'user_id': self.request.user.id,
            'categoria_id': instance_id
        })


class TransacaoViewSet(viewsets.ModelViewSet):
    """ViewSet otimizado para transações financeiras com cache inteligente"""
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated, PermissaoFinanceiro, CanDeleteData]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'data']
    search_fields = ['descricao', 'observacao']
    ordering_fields = ['data', 'valor']
    ordering = ['-data']

    def get_queryset(self):
        cliente = _resolver_cliente_financeiro(self.request.user)
        if cliente is None:
            return Transacao.objects.none()
        return Transacao.objects.select_related('categoria').filter(
            cliente=cliente
        ).order_by('-data')

    def perform_create(self, serializer):
        cliente = _resolver_cliente_financeiro(self.request.user)
        if cliente is None:
            raise serializers.ValidationError({'detail': 'Usuário sem cliente vinculado.'})
        instance = serializer.save(cliente=cliente)
        # 🚀 Invalida cache de relatórios
        try:
            cache.delete(f"user_{self.request.user.id}_financeiro_transacoes")
            cache.delete(f"user_{self.request.user.id}_financeiro_relatorios")
        except AttributeError:
            pass
        logger.info("Transação criada", extra={
            'user_id': self.request.user.id,
            'transacao_id': instance.id,
            'valor': str(instance.valor),
            'tipo': instance.categoria.tipo if instance.categoria_id else 'N/A',
        })

    def perform_update(self, serializer):
        super().perform_update(serializer)
        # 🚀 Invalida cache de relatórios
        try:
            cache.delete(f"user_{self.request.user.id}_financeiro_categorias")
            cache.delete(f"user_{self.request.user.id}_financeiro_transacoes")
            cache.delete(f"user_{self.request.user.id}_financeiro_relatorios")
        except AttributeError:
            pass

    def perform_destroy(self, instance):
        instance_id = instance.id
        super().perform_destroy(instance)
        # 🚀 Invalida cache de relatórios
        try:
            cache.delete(f"user_{self.request.user.id}_financeiro_categorias")
            cache.delete(f"user_{self.request.user.id}_financeiro_transacoes")
            cache.delete(f"user_{self.request.user.id}_financeiro_relatorios")
        except AttributeError:
            pass
        logger.info("Transação deletada", extra={
            'user_id': self.request.user.id,
            'transacao_id': instance_id
        })

    @action(detail=False, methods=['get'])
    def fluxo_caixa(self, request):
        """Retorna o resumo financeiro cacheado por 5 minutos"""
        cache_key = f"user_{request.user.id}_financeiro_fluxo_caixa"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        qs = self.get_queryset()
        
        # ✅ OTIMIZAÇÃO: Single query para ambos os aggregates
        aggregates = qs.aggregate(
            total_receitas=Sum('valor', filter=Q(tipo='RECEITA')),
            total_despesas=Sum('valor', filter=Q(tipo='DESPESA'))
        )
        
        receitas = aggregates['total_receitas'] or 0
        despesas = aggregates['total_despesas'] or 0
        
        result = {
            'total_receitas': receitas,
            'total_despesas': despesas,
            'saldo': receitas - despesas,
            'total_transacoes': qs.count()
        }
        
        # 🚀 Cache por 5 minutos
        cache.set(cache_key, result, 60 * 5)
        
        return Response(result)

    @action(detail=False, methods=['get'])
    def fluxo_caixa_mensal(self, request):
        """Retorna o fluxo de caixa do mês atual (compatível com versão anterior)"""
        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        
        qs = self.get_queryset().filter(
            data__gte=primeiro_dia_mes,
            data__lte=hoje
        )
        
        aggregates = qs.aggregate(
            total_receitas=Sum('valor', filter=Q(tipo='RECEITA')),
            total_despesas=Sum('valor', filter=Q(tipo='DESPESA'))
        )
        
        receitas = aggregates['total_receitas'] or 0
        despesas = aggregates['total_despesas'] or 0
        
        return Response({
            'periodo': f"{primeiro_dia_mes.strftime('%m/%Y')}",
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas,
            'transacoes': TransacaoSerializer(qs, many=True).data
        })

    @action(detail=False, methods=['get'])
    def relatorio_mensal(self, request):
        """Relatório mensal detalhado com cache inteligente"""
        cache_key = f"user_{request.user.id}_financeiro_relatorio_mensal"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # ✅ Query otimizada com agregações
        from django.db.models.functions import TruncMonth
        relatorio = (
            self.get_queryset()
            .annotate(mes=TruncMonth('data'))
            .values('mes', 'tipo')
            .annotate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            .order_by('-mes')
        )
        
        result = {
            'relatorio_mensal': list(relatorio),
            'gerado_em': date.today().isoformat()
        }
        
        # 🚀 Cache por 10 minutos
        cache.set(cache_key, result, 60 * 10)
        
        return Response(result)


class FormaPagamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para formas de pagamento"""
    serializer_class = FormaPagamentoSerializer
    permission_classes = [permissions.IsAuthenticated, PermissaoFinanceiro, CanDeleteData]

    def get_queryset(self):
        return FormaPagamento.objects.filter(usuario=self.request.user, ativo=True)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def definir_principal(self, request, pk=None):
        """Define a forma de pagamento como principal"""
        forma = self.get_object()
        # Remover principal de todas as outras formas
        FormaPagamento.objects.filter(cliente=forma.cliente, principal=True).update(principal=False)
        forma.principal = True
        forma.save()
        return Response(self.get_serializer(forma).data)

    def perform_destroy(self, instance):
        """Soft delete: marca como inativa"""
        instance.ativo = False
        instance.save()
        logger.info("Forma de pagamento desativada", extra={
            'user_id': self.request.user.id,
            'forma_pagamento_id': instance.id
        })