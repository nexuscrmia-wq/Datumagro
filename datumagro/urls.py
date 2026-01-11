## datumagro/datumagro/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from datumagro.apps.usuarios.views import CustomTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from datumagro.apps.core.views import health
from datumagro.apps.core.views import create_cliente_for_user

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs para autenticação JWT
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # URLs da API, organizadas por app
    path('api/usuarios/', include('datumagro.apps.usuarios.urls', namespace='usuarios')),
    path('api/cadastros/', include('datumagro.apps.cadastros.urls', namespace='cadastros')),
    path('api/financeiro/', include('datumagro.apps.financeiro.urls', namespace='financeiro')),
    path('api/inteligencia/', include('datumagro.apps.inteligencia.urls', namespace='inteligencia')),
    path('api/logistica/', include('datumagro.apps.logistica.urls')),  # ✅ Nova API de Logística
    path('api/health/', health, name='health'),
    # Debug helper to create a Cliente for the authenticated user (development only)
    path('api/debug/create_cliente/', create_cliente_for_user, name='debug-create-cliente'),
    # ... (o resto do seu arquivo continua igual)

    # OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# ... (o resto do seu arquivo continua igual)