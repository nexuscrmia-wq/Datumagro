# datumagro/apps/usuarios/urls.py

from django.urls import path
from .views import PerfilUsuarioView

app_name = 'usuarios'

urlpatterns = [
    path('me/', PerfilUsuarioView.as_view(), name='meu-perfil'),
]