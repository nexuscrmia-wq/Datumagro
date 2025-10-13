# datumagro/apps/inteligencia/urls.py

from rest_framework.routers import DefaultRouter
from .views import AlertaViewSet

app_name = 'inteligencia' # <-- A LINHA CORRIGIDA

router = DefaultRouter()
router.register(r'alertas', AlertaViewSet, basename='alerta')

urlpatterns = router.urls