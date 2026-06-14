from rest_framework.routers import DefaultRouter
from .views import RelatorioViewSet

app_name = 'relatorios'

router = DefaultRouter()
router.register(r'', RelatorioViewSet, basename='relatorios')

urlpatterns = router.urls
