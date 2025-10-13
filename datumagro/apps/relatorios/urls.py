# datumagro/apps/relatorios/urls.py

from rest_framework.routers import DefaultRouter
from .views import RelatorioViewSet

app_name = 'relatorios'

router = DefaultRouter()
router.register(r'historico', RelatorioViewSet, basename='historico-relatorios')

urlpatterns = router.urls