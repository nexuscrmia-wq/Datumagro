## datumagro/datumagro/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as authtoken_views # <-- ADICIONE ESTA LINHA DE IMPORT

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL PARA AUTENTICAÇÃO E GERAÇÃO DE TOKEN
    path('api/api-token-auth/', authtoken_views.obtain_auth_token), # <-- ADICIONE ESTA LINHA

    # URLs da API, organizadas por app
    path('api/usuarios/', include('datumagro.apps.usuarios.urls', namespace='usuarios')),
    path('api/cadastros/', include('datumagro.apps.cadastros.urls', namespace='cadastros')),
    # ... (o resto do seu arquivo continua igual)
]

# ... (o resto do seu arquivo continua igual)