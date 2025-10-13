# datumagro/apps/usuarios/models.py (COLE ESTE CÓDIGO FINAL)

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


class PerfilUsuario(models.Model):
    """
    Modelo de perfil que estende o usuário. A conexão com o Cliente
    será feita de forma reversa, a partir do modelo Cliente.
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfilusuario')

    # O CAMPO 'cliente' FOI REMOVIDO DAQUI PARA RESOLVER A AMBIGUIDADE.

    def __str__(self):
        return f"Perfil de {self.usuario.email}"