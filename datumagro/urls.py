## datumagro/datumagro/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.views.static import serve
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from datumagro.apps.usuarios.views import CustomTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from datumagro.apps.core.views import (
    health, create_cliente_for_user, dashboard_resumo, politica_privacidade,
    onboarding_etapa, home, versao_app, redefinir_senha, download_apk, upload_apk,
    painel_usuarios, painel_aprovar_usuario, painel_suspender_usuario, painel_atribuir_plano,
)
from datumagro.apps.usuarios.views import (
    equipe_membros, equipe_convidar, equipe_aceitar,
    equipe_remover, equipe_permissoes, excluir_conta,
    entrar_equipe_landing, logout_view,
)

urlpatterns = [
    path('', home, name='home'),
    # Admin em path não-padrão — bots varrem /admin/ automaticamente
    path('datumagro-gestao/', admin.site.urls),
    path('ping/', lambda _: HttpResponse('pong'), name='ping'),

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
    path('api/assinaturas/', include('datumagro.apps.assinaturas.urls', namespace='assinaturas')),
    path('api/notificacoes/', include('datumagro.apps.notificacoes.urls', namespace='notificacoes')),
    path('api/rastreabilidade/', include('datumagro.apps.rastreabilidade.urls', namespace='rastreabilidade')),

    # Equipe / convites
    path('api/equipe/membros/', equipe_membros, name='equipe-membros'),
    path('api/equipe/convidar/', equipe_convidar, name='equipe-convidar'),
    path('api/equipe/aceitar/', equipe_aceitar, name='equipe-aceitar'),
    path('api/equipe/membros/<int:pk>/remover/', equipe_remover, name='equipe-remover'),
    path('api/equipe/membros/<int:pk>/permissoes/', equipe_permissoes, name='equipe-permissoes'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/usuarios/excluir-conta/', excluir_conta, name='excluir-conta'),

    # Recuperação de senha via browser (link enviado por email)
    path('redefinir-senha/<str:token>/', redefinir_senha, name='redefinir-senha'),

    # Landing page do convite de equipe (link enviado por e-mail)
    path('entrar-equipe/', entrar_equipe_landing, name='entrar-equipe'),

    # Central de Ajuda / Base de Conhecimento
    path('api/ajuda/', include('datumagro.apps.ajuda.urls', namespace='ajuda')),

    # Painel de gestão de usuários (superuser only)
    path('painel/', painel_usuarios, name='painel-usuarios'),
    path('painel/usuarios/<int:cliente_id>/aprovar/', painel_aprovar_usuario, name='painel-aprovar'),
    path('painel/usuarios/<int:cliente_id>/suspender/', painel_suspender_usuario, name='painel-suspender'),
    path('painel/usuarios/<int:cliente_id>/plano/', painel_atribuir_plano, name='painel-plano'),

    # APK: download público + upload restrito a admin (salva no Railway Volume)
    path('baixar/apk/', download_apk, name='download-apk'),
    path('api/admin/upload-apk/', upload_apk, name='upload-apk'),

    # Utilitários
    path('api/health/', health, name='health'),
    path('api/versao/', versao_app, name='versao-app'),
    path('api/dashboard/resumo/', dashboard_resumo, name='dashboard-resumo'),
    path('api/onboarding/criar-conta/', create_cliente_for_user, name='onboarding-create-cliente'),
    path('api/onboarding/etapa/', onboarding_etapa, name='onboarding-etapa'),

    # OpenAPI / Swagger — acessível a qualquer usuário autenticado
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[IsAuthenticated]), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[IsAuthenticated]), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema', permission_classes=[IsAuthenticated]), name='redoc'),

    # Media files (fotos de perfil, uploads) — Railway usa filesystem local
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]
