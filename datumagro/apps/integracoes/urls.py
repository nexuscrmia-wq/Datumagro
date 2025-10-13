# datumagro/apps/integracoes/urls.py

from django.urls import path
from .views import RegistroAutomaticoView

app_name = 'integracoes'

urlpatterns = [
    path('registrar-pesagem/', RegistroAutomaticoView.as_view(), name='registrar-pesagem-automatica'),
]