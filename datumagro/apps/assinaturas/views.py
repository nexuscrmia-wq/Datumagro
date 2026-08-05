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

    def _get_cliente(self, request):
        from datumagro.apps.cadastros.models import Cliente
        user = request.user
        perfil = getattr(user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None) if perfil else None
        if not cliente:
            cliente = Cliente.objects.filter(email_contato=user.email).first()
        return cliente

    def get_queryset(self):
        cliente = self._get_cliente(self.request)
        if not cliente:
            return Assinatura.objects.none()
        return Assinatura.objects.filter(cliente=cliente)

    def list(self, request, *args, **kwargs):
        """ Retorna a assinatura do cliente logado. """
        cliente = self._get_cliente(request)
        if not cliente:
            return Response({"detail": "Cliente não encontrado."}, status=404)
        try:
            assinatura = Assinatura.objects.get(cliente=cliente)
            serializer = self.get_serializer(assinatura)
            return Response(serializer.data)
        except Assinatura.DoesNotExist:
            return Response({"detail": "Nenhuma assinatura encontrada."}, status=404)