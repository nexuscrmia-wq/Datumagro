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
        from datumagro.apps.cadastros.models import Cliente
        user = self.request.user
        perfil = getattr(user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None) if perfil else None
        if not cliente:
            cliente = Cliente.objects.filter(email_contato=user.email).first()
        if not cliente:
            return LogNotificacao.objects.none()
        return LogNotificacao.objects.filter(cliente=cliente)