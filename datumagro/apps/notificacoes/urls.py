# datumagro/apps/notificacoes/urls.py

from rest_framework.routers import DefaultRouter
from .views import HistoricoNotificacoesViewSet

app_name = 'notificacoes'

router = DefaultRouter()
router.register(r'historico', HistoricoNotificacoesViewSet, basename='historico-notificacoes')

urlpatterns = router.urls