# datumagro/apps/usuarios/views.py

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import UsuarioSerializer

class PerfilUsuarioView(RetrieveUpdateAPIView):
    """
    View para o usuário logado ver e editar seus próprios dados.
    Acessível em /api/usuarios/me/
    """
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user