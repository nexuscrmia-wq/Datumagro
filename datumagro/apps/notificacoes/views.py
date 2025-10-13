# datumagro/apps/notificacoes/views.py

from rest_framework import viewsets, permissions
from .models import LogNotificacao
from .serializers import LogNotificacaoSerializer


class HistoricoNotificacoesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ao cliente logado visualizar o histórico
    de todas as notificações que já foram enviadas para ele.

    É 'ReadOnly' porque o cliente não pode criar ou apagar um log de notificação.
    """
    serializer_class = LogNotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Esta função é a garantia de segurança: ela filtra o histórico para mostrar
        APENAS as notificações que pertencem ao cliente do usuário que fez a requisição.
        """
        cliente = self.request.user.perfilusuario.cliente
        return LogNotificacao.objects.filter(cliente=cliente)