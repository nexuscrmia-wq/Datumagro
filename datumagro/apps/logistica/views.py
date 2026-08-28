from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from datumagro.apps.usuarios.permissions import IsImportacaoInternacional, IsProprietarioOrGerente
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .models import Embarque, ItemEmbarque
from .serializers import EmbarqueSerializer, ItemEmbarqueSerializer


def _resolver_cliente_logistica(user):
    """Resolve o cliente do usuário com fallback para sistema mono-cliente."""
    from datumagro.apps.cadastros.models import Cliente
    prop = user.propriedades.select_related('cliente').first()
    if prop:
        return prop.cliente
    cliente = Cliente.objects.filter(email_contato=user.email).first()
    if cliente:
        return cliente
    if Cliente.objects.count() == 1:
        return Cliente.objects.first()
    return None


class EmbarqueViewSet(viewsets.ModelViewSet):
    """
    Embarques e GTA: peão pode consultar a agenda de saída mas não criar/editar.
    Leitura: todos autenticados. Escrita: Proprietário + Gerente.
    """
    serializer_class = EmbarqueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'status', 'porto_destino']
    search_fields = ['numero_embarque', 'navio', 'porto_destino', 'agente_carga']
    ordering_fields = ['data_prevista_embarque', 'created_at']

    def get_queryset(self):
        cliente = _resolver_cliente_logistica(self.request.user)
        if not cliente:
            return Embarque.objects.none()
        return Embarque.objects.filter(responsavel=cliente).order_by('-data_prevista_embarque')

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsProprietarioOrGerente()]

    def _check_importacao(self):
        perm = IsImportacaoInternacional()
        if not perm.has_permission(self.request, self):
            raise PermissionDenied(getattr(perm, 'message', 'Acesso negado: seu plano não permite importação internacional.'))

    def _get_responsavel(self):
        from rest_framework.exceptions import ValidationError
        cliente = _resolver_cliente_logistica(self.request.user)
        if not cliente:
            raise ValidationError({'responsavel': 'Usuário sem cliente vinculado.'})
        return cliente

    def perform_create(self, serializer):
        tipo = serializer.validated_data.get('tipo')
        if tipo == 'IMP':
            self._check_importacao()
        serializer.save(responsavel=self._get_responsavel())

    def perform_update(self, serializer):
        tipo = serializer.validated_data.get('tipo')
        if tipo == 'IMP':
            self._check_importacao()
        serializer.save()


class ItemEmbarqueViewSet(viewsets.ModelViewSet):
    """Itens de embarque: leitura para todos, escrita só Proprietário + Gerente."""
    queryset = ItemEmbarque.objects.all().order_by('-id')
    serializer_class = ItemEmbarqueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['embarque', 'animal', 'tipo_produto']
    search_fields = ['descricao_produto', 'gta', 'sif']
    ordering_fields = ['peso_total_kg', 'valor_total']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsProprietarioOrGerente()]

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

