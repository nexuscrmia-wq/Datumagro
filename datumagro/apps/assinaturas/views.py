# datumagro/apps/assinaturas/views.py

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Plano, Assinatura
from .serializers import PlanoSerializer, AssinaturaSerializer

class PlanoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite que os planos sejam visualizados.
    Acessível por qualquer um para ver os planos disponíveis.
    """
    queryset = Plano.objects.filter(ativo=True)
    serializer_class = PlanoSerializer
    permission_classes = [permissions.AllowAny]


class MinhaAssinaturaViewSet(viewsets.GenericViewSet):
    """
    API endpoint para um cliente logado ver e gerenciar sua própria assinatura.
    - GET /api/minha-assinatura/ -> Retorna os detalhes da assinatura do usuário logado.
    """
    serializer_class = AssinaturaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Garante que o usuário só possa ver sua própria assinatura
        return Assinatura.objects.filter(cliente=self.request.user.perfilusuario.cliente)

    def list(self, request, *args, **kwargs):
        """ Retorna a assinatura do cliente logado. """
        try:
            assinatura = request.user.perfilusuario.cliente.assinatura
            serializer = self.get_serializer(assinatura)
            return Response(serializer.data)
        except Assinatura.DoesNotExist:
            return Response({"detail": "Nenhuma assinatura encontrada."}, status=404)