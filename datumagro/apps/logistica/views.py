from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from datumagro.apps.usuarios.permissions import IsImportacaoInternacional
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .models import Embarque, ItemEmbarque
from .serializers import EmbarqueSerializer, ItemEmbarqueSerializer


class EmbarqueViewSet(viewsets.ModelViewSet):
    """CRUD simples para embarques do Porto do Açu."""
    queryset = Embarque.objects.all().order_by('-data_prevista_embarque')
    serializer_class = EmbarqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'status', 'porto_destino']
    search_fields = ['numero_embarque', 'navio', 'porto_destino', 'agente_carga']
    ordering_fields = ['data_prevista_embarque', 'created_at']

    def perform_create(self, serializer):
        tipo = serializer.validated_data.get('tipo')
        # Tipo 'IMP' representa importação (entrada)
        if tipo == 'IMP':
            perm = IsImportacaoInternacional()
            if not perm.has_permission(self.request, self):
                raise PermissionDenied(getattr(perm, 'message', 'Acesso negado: seu plano não permite importação internacional.'))
        serializer.save()

    def perform_update(self, serializer):
        # Se alterar/definir tipo para importação, também checar permissão
        tipo = serializer.validated_data.get('tipo')
        if tipo == 'IMP':
            perm = IsImportacaoInternacional()
            if not perm.has_permission(self.request, self):
                raise PermissionDenied(getattr(perm, 'message', 'Acesso negado: seu plano não permite importação internacional.'))
        serializer.save()


class ItemEmbarqueViewSet(viewsets.ModelViewSet):
    """CRUD para itens de carga vinculados aos embarques."""
    queryset = ItemEmbarque.objects.all().order_by('-id')
    serializer_class = ItemEmbarqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['embarque', 'animal', 'tipo_produto']
    search_fields = ['descricao_produto', 'gta', 'sif']
    ordering_fields = ['peso_total_kg', 'valor_total']

    def perform_create(self, serializer):
        embarque = serializer.validated_data.get('embarque')
        if embarque and getattr(embarque, 'tipo', None) == 'IMP':
            perm = IsImportacaoInternacional()
            if not perm.has_permission(self.request, self):
                raise PermissionDenied(getattr(perm, 'message', 'Acesso negado: seu plano não permite importação internacional.'))
        serializer.save()

    def perform_update(self, serializer):
        embarque = serializer.validated_data.get('embarque')
        if embarque and getattr(embarque, 'tipo', None) == 'IMP':
            perm = IsImportacaoInternacional()
            if not perm.has_permission(self.request, self):
                raise PermissionDenied(getattr(perm, 'message', 'Acesso negado: seu plano não permite importação internacional.'))
        serializer.save()

