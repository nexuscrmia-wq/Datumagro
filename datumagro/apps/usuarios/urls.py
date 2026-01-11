from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, PerfilUsuarioView

app_name = 'usuarios'

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', PerfilUsuarioView.as_view(), name='meu-perfil'),
]