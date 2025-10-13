# datumagro/apps/financeiro/urls.py

from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, TransacaoViewSet

app_name = 'financeiro' # <-- A LINHA CORRIGIDA

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'transacoes', TransacaoViewSet, basename='transacao')

urlpatterns = router.urls