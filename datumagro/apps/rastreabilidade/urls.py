# datumagro/apps/rastreabilidade/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilPublicoAPIViewSet, PublicPerfilDetailView

app_name = 'rastreabilidade'

# URLs da API para o produtor gerenciar os perfis
router = DefaultRouter()
router.register(r'gerenciar-perfis', PerfilPublicoAPIViewSet, basename='gerenciar-perfil')

# URLs públicas que serão acessadas pelo QR Code
public_urls = [
    path('perfil/<slug:slug>/', PublicPerfilDetailView.as_view(), name='perfil-publico-animal'),
]

urlpatterns = [
    # Ex: /api/rastreabilidade/gerenciar-perfis/
    path('api/', include(router.urls)),
    # Ex: /rastreabilidade/perfil/brinco-01-123/
    path('', include(public_urls)),
]