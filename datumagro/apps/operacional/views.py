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


class BaseOperacionalViewSet(viewsets.ModelViewSet):
    """ ViewSet base que filtra os dados pelo cliente do usuário logado. """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cliente = self.request.user.perfilusuario.cliente
        model_class = self.serializer_class.Meta.model

        # Filtra os objetos que pertencem diretamente ao cliente ou a uma propriedade do cliente
        if hasattr(model_class, 'cliente'):
            return model_class.objects.filter(cliente=cliente)
        if hasattr(model_class, 'propriedade'):
            return model_class.objects.filter(propriedade__cliente=cliente)
        # Adicionar mais lógicas de filtro conforme necessário
        return model_class.objects.none()

    def perform_create(self, serializer):
        # A lógica de associação ao cliente/propriedade pode ser mais complexa e
        # deve ser tratada no serializer ou na view de cada um
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


class PiqueteViewSet(BaseOperacionalViewSet):
    serializer_class = PiqueteSerializer

    @action(detail=False, methods=['get'])
    def recomendar(self, request):
        """
        Endpoint da IA de Manejo de Pasto.
        URL: /api/operacional/piquetes/recomendar/
        """
        cliente = request.user.perfilusuario.cliente
        # Assumindo que queremos a recomendação para a primeira propriedade do cliente
        propriedade = cliente.propriedades.first()
        if not propriedade:
            return Response({"erro": "Nenhuma propriedade cadastrada."}, status=400)

        piquete_recomendado = recomendar_proximo_piquete(propriedade)

        if piquete_recomendado:
            serializer = self.get_serializer(piquete_recomendado)
            return Response(serializer.data)
        else:
            return Response({"mensagem": "Nenhum piquete pronto para uso no momento."})