from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuário customizado usado pelo projeto."""
    email = models.EmailField('E-mail', unique=True)
    username = models.CharField('Username', max_length=150, blank=True)
    nome_completo = models.CharField('Nome Completo', max_length=255, blank=True)
    first_name = models.CharField('Nome', max_length=150, blank=True)
    last_name = models.CharField('Sobrenome', max_length=150, blank=True)
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True)
    data_nascimento = models.DateField('Data de Nascimento', blank=True, null=True)
    foto_perfil = models.ImageField('Foto de Perfil', upload_to='perfis/', blank=True, null=True)

    # Controle
    is_active = models.BooleanField('Ativo', default=True)
    is_staff = models.BooleanField('Staff', default=False)
    date_joined = models.DateTimeField('Data de Registro', default=timezone.now)

    # Campos para reset de senha
    password_reset_token = models.CharField(max_length=128, blank=True, null=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.email}"


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfilusuario')

    def __str__(self):
        return f"Perfil de {self.usuario.email}"