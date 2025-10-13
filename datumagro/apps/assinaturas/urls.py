# datumagro/apps/assinaturas/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'assinaturas' # <-- A LINHA CORRIGIDA

router = DefaultRouter()
router.register(r'planos', views.PlanoViewSet, basename='plano')

minha_assinatura_urls = [
    path('', views.MinhaAssinaturaViewSet.as_view({'get': 'list'}), name='minha-assinatura-detalhe'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('minha-assinatura/', include(minha_assinatura_urls)),
]