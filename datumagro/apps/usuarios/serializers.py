# datumagro/apps/usuarios/serializers.py

from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    """ Serializer para o modelo de Usuário. """
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome_completo']