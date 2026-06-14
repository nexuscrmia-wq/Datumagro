# datumagro/apps/operacional/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProdutoSanitario, ManejoSanitario, RegistroReprodutivo, Lote, Piquete
from .serializers import (
    ProdutoSanitarioSerializer, ManejoSanitarioSerializer, RegistroReprodutivoSerializer,
    LoteSerializer, PiqueteSerializer
)
from .services import recomendar_proximo_piquete
from datumagro.apps.usuarios.permissions import (
    PermissaoAnimais, PermissaoLotes, CanDeleteData
)


class BaseOperacionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet base com 2 camadas de segurança:
    1. Multi-tenant: filtra pelo cliente do usuário
    2. Role-based: Funcionário vê apenas suas propriedades designadas
    """
    permission_classes = [permissions.IsAuthenticated, PermissaoAnimais, CanDeleteData]

    def _get_cliente(self):
        from datumagro.apps.cadastros.models import Cliente
        user = self.request.user
        try:
            cliente = Cliente.objects.filter(email_contato=user.email).first()
            if cliente:
                return cliente
        except Exception:
            pass
        return Cliente.objects.first()

    def get_queryset(self):
        cliente = self._get_cliente()
        if not cliente:
            return self.serializer_class.Meta.model.objects.none()

        user = self.request.user
        model_class = self.serializer_class.Meta.model

        # Camada 1: filtro multi-tenant por cliente
        if hasattr(model_class, 'cliente'):
            qs = model_class.objects.filter(cliente=cliente)
        elif hasattr(model_class, 'propriedade'):
            qs = model_class.objects.filter(propriedade__cliente=cliente)
        elif hasattr(model_class, 'matriz'):
            qs = model_class.objects.filter(matriz__propriedade__cliente=cliente)
        elif hasattr(model_class, 'animal'):
            qs = model_class.objects.filter(animal__propriedade__cliente=cliente)
        else:
            return model_class.objects.none()

        # Camada 2: Funcionário só vê dados das suas propriedades designadas
        if user.is_funcionario():
            propriedades_do_user = user.propriedades.all()
            if hasattr(model_class, 'propriedade'):
                qs = qs.filter(propriedade__in=propriedades_do_user)
            elif hasattr(model_class, 'matriz'):
                qs = qs.filter(matriz__propriedade__in=propriedades_do_user)
            elif hasattr(model_class, 'animal'):
                qs = qs.filter(animal__propriedade__in=propriedades_do_user)

        return qs

    def perform_create(self, serializer):
        serializer.save()


# ViewSets para cada modelo
class ProdutoSanitarioViewSet(BaseOperacionalViewSet):
    serializer_class = ProdutoSanitarioSerializer


class ManejoSanitarioViewSet(BaseOperacionalViewSet):
    serializer_class = ManejoSanitarioSerializer


class RegistroReprodutivoViewSet(BaseOperacionalViewSet):
    serializer_class = RegistroReprodutivoSerializer


class LoteViewSet(BaseOperacionalViewSet):
    serializer_class = LoteSerializer
    permission_classes = [permissions.IsAuthenticated, PermissaoLotes, CanDeleteData]


class PiqueteViewSet(BaseOperacionalViewSet):
    serializer_class = PiqueteSerializer
    permission_classes = [permissions.IsAuthenticated, PermissaoLotes, CanDeleteData]

    @action(detail=False, methods=['get'])
    def recomendar(self, request):
        """
        Endpoint da IA de Manejo de Pasto.
        URL: /api/operacional/piquetes/recomendar/
        """
        cliente = self._get_cliente()
        if not cliente:
            return Response({"erro": "Nenhum cliente associado."}, status=400)
        propriedade = cliente.propriedades.first()
        if not propriedade:
            return Response({"erro": "Nenhuma propriedade cadastrada."}, status=400)

        piquete_recomendado = recomendar_proximo_piquete(propriedade)
        if piquete_recomendado:
            return Response(self.get_serializer(piquete_recomendado).data)
        return Response({"mensagem": "Nenhum piquete pronto para uso no momento."})
