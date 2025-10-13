# datumagro/apps/usuarios/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, PerfilUsuario

@receiver(post_save, sender=Usuario)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Signal para criar um PerfilUsuario toda vez que um Usuario é criado.
    """
    if created:
        PerfilUsuario.objects.create(usuario=instance)