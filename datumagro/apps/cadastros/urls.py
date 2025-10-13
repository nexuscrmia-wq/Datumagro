# datumagro/apps/cadastros/urls.py

from rest_framework.routers import DefaultRouter
from .views import PropriedadeViewSet, AnimalViewSet, RegistroPesagemViewSet

app_name = 'cadastros' # <-- A LINHA CORRIGIDA

router = DefaultRouter()
router.register(r'propriedades', PropriedadeViewSet, basename='propriedade')
router.register(r'animais', AnimalViewSet, basename='animal')
router.register(r'pesagens', RegistroPesagemViewSet, basename='pesagem')

urlpatterns = router.urls