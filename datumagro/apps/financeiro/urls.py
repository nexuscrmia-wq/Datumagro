# datumagro/apps/financeiro/urls.py

from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, TransacaoViewSet
from .views import FormaPagamentoViewSet

app_name = 'financeiro' # <-- A LINHA CORRIGIDA

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'transacoes', TransacaoViewSet, basename='transacao')
router.register(r'formas-pagamento', FormaPagamentoViewSet, basename='forma-pagamento')

urlpatterns = router.urls