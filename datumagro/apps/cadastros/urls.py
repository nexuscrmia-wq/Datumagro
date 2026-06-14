# datumagro/apps/cadastros/urls.py

from rest_framework.routers import DefaultRouter
from .views import (ClienteViewSet, 
                    PropriedadeViewSet, 
                    AnimalViewSet, 
                    RegistroPesagemViewSet, 
                    PiqueteViewSet, 
                    VacinaViewSet, 
                    AplicacaoVacinaViewSet, 
                    InformacaoGeneticaViewSet, 
                    FichaTecnicaAnimalViewSet)

app_name = 'cadastros'

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'propriedades', PropriedadeViewSet, basename='propriedade')
router.register(r'animais', AnimalViewSet, basename='animal')
router.register(r'pesagens', RegistroPesagemViewSet, basename='pesagem')
router.register(r'piquetes', PiqueteViewSet, basename='piquete')
router.register(r'vacinas', VacinaViewSet, basename='vacina')
router.register(r'aplicacoes-vacina', AplicacaoVacinaViewSet, basename='aplicacao-vacina')
router.register(r'informacoes-geneticas', InformacaoGeneticaViewSet, basename='informacao-genetica')
urlpatterns = router.urls
