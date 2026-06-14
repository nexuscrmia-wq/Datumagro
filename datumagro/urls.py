## datumagro/datumagro/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from datumagro.apps.usuarios.views import CustomTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from datumagro.apps.core.views import (
    health, create_cliente_for_user, dashboard_resumo, politica_privacidade
)
from datumagro.apps.usuarios.views import (
    equipe_membros, equipe_convidar, equipe_aceitar,
    equipe_remover, equipe_permissoes, excluir_conta,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página pública (obrigatória para aprovação nas lojas)
    path('privacidade/', politica_privacidade, name='politica-privacidade'),

    # Autenticação JWT
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # APIs por app
    path('api/usuarios/', include('datumagro.apps.usuarios.urls', namespace='usuarios')),
    path('api/cadastros/', include('datumagro.apps.cadastros.urls', namespace='cadastros')),
    path('api/financeiro/', include('datumagro.apps.financeiro.urls', namespace='financeiro')),
    path('api/inteligencia/', include('datumagro.apps.inteligencia.urls', namespace='inteligencia')),
    path('api/logistica/', include('datumagro.apps.logistica.urls')),
    path('api/operacional/', include('datumagro.apps.operacional.urls')),
    path('api/relatorios/', include('datumagro.apps.relatorios.urls', namespace='relatorios')),

    # Equipe / convites
    path('api/equipe/membros/', equipe_membros, name='equipe-membros'),
    path('api/equipe/convidar/', equipe_convidar, name='equipe-convidar'),
    path('api/equipe/aceitar/', equipe_aceitar, name='equipe-aceitar'),
    path('api/equipe/membros/<int:pk>/remover/', equipe_remover, name='equipe-remover'),
    path('api/equipe/membros/<int:pk>/permissoes/', equipe_permissoes, name='equipe-permissoes'),
    path('api/usuarios/excluir-conta/', excluir_conta, name='excluir-conta'),

    # Utilitários
    path('api/health/', health, name='health'),
    path('api/dashboard/resumo/', dashboard_resumo, name='dashboard-resumo'),
    path('api/debug/create_cliente/', create_cliente_for_user, name='debug-create-cliente'),

    # OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
