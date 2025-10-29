# datumagro/apps/inteligencia/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Alerta
from .serializers import AlertaSerializer

class AlertaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para visualizar e gerenciar os alertas gerados pela IA.
    O usuário pode listar seus alertas e marcá-los como resolvidos.
    """
    serializer_class = AlertaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Retorna apenas os alertas do cliente do usuário logado. """
        perfil = getattr(self.request.user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None) if perfil else None
        if not cliente:
            return Alerta.objects.none()
        return Alerta.objects.filter(cliente=cliente)

    @action(detail=True, methods=['post'])
    def marcar_como_resolvido(self, request, pk=None):
        """
        Ação customizada para marcar um alerta como 'RESOLVIDO'.
        URL: /api/inteligencia/alertas/{id}/marcar_como_resolvido/
        """
        # Defensive: ensure user has cliente linked before attempting to modify
        perfil = getattr(request.user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None) if perfil else None
        if not cliente:
            return Response({'detail': 'Usuário sem cliente vinculado.'}, status=status.HTTP_400_BAD_REQUEST)

        alerta = self.get_object()
        alerta.status = 'RESOLVIDO'
        alerta.save()
        return Response({'status': 'Alerta marcado como resolvido'}, status=status.HTTP_200_OK)