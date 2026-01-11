# datumagro/apps/inteligencia/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AlertaViewSet, AlertasIAView, MetricasDesempenhoView, webhook_ia

app_name = 'inteligencia'

router = DefaultRouter()
router.register(r'alertas', AlertaViewSet, basename='alerta')

urlpatterns = [
    path('alertas-ia/', AlertasIAView.as_view(), name='ia-alertas'),
    path('metricas-desempenho/', MetricasDesempenhoView.as_view(), name='ia-metricas'),
    path('webhook/', webhook_ia, name='ia-webhook'),
] + router.urls