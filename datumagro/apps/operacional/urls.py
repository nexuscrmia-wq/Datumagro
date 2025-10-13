# datumagro/apps/operacional/urls.py

from rest_framework.routers import DefaultRouter
from .views import (
    ProdutoSanitarioViewSet, ManejoSanitarioViewSet, RegistroReprodutivoViewSet,
    LoteViewSet, PiqueteViewSet
)

app_name = 'operacional' # <-- A LINHA CORRIGIDA

router = DefaultRouter()
router.register(r'produtos-sanitarios', ProdutoSanitarioViewSet, basename='produtosanitario')
router.register(r'manejos-sanitarios', ManejoSanitarioViewSet, basename='manejosanitario')
router.register(r'registros-reprodutivos', RegistroReprodutivoViewSet, basename='registroreprodutivo')
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(r'piquetes', PiqueteViewSet, basename='piquete')

urlpatterns = router.urls