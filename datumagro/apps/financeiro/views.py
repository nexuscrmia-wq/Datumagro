# datumagro/apps/financeiro/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta
from .models import Categoria, Transacao
from .serializers import CategoriaSerializer, TransacaoSerializer
from .services import get_fluxo_caixa


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar as Categorias Financeiras do cliente logado.
    """
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Categoria.objects.filter(cliente=self.request.user.perfilusuario.cliente)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user.perfilusuario.cliente)


class TransacaoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar as Transações Financeiras do cliente logado.
    """
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transacao.objects.filter(cliente=self.request.user.perfilusuario.cliente)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user.perfilusuario.cliente)

    @action(detail=False, methods=['get'])
    def fluxo_caixa_mensal(self, request):
        """
        Retorna o fluxo de caixa do mês atual para o cliente.
        URL: /api/financeiro/transacoes/fluxo_caixa_mensal/
        """
        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)

        cliente = request.user.perfilusuario.cliente
        dados = get_fluxo_caixa(cliente, primeiro_dia_mes, hoje)

        return Response(dados)