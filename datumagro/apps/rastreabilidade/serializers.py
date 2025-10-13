# datumagro/apps/rastreabilidade/serializers.py

from rest_framework import serializers
from .models import PerfilPublicoAnimal
from datumagro.apps.cadastros.serializers import AnimalSerializer, PropriedadeSerializer
from datumagro.apps.operacional.serializers import ManejoSanitarioSerializer

class PerfilPublicoManagementSerializer(serializers.ModelSerializer):
    """ Serializer para o produtor gerenciar as configurações do perfil. """
    class Meta:
        model = PerfilPublicoAnimal
        fields = ['id', 'animal', 'is_publico', 'titulo_perfil', 'historia_destacada', 'slug', 'qr_code']
        read_only_fields = ('animal', 'slug', 'qr_code')

class DadosRastreabilidadeSerializer(serializers.ModelSerializer):
    """
    Serializer especial que agrega dados de vários apps para a página pública.
    """
    animal = AnimalSerializer(read_only=True)
    propriedade = PropriedadeSerializer(source='animal.propriedade', read_only=True)
    manejos_sanitarios = ManejoSanitarioSerializer(source='animal.manejos_sanitarios', many=True, read_only=True)
    # Adicionar outros dados agregados aqui no futuro (ex: alimentação, desempenho)

    class Meta:
        model = PerfilPublicoAnimal
        fields = [
            'titulo_perfil',
            'historia_destacada',
            'animal',
            'propriedade',
            'manejos_sanitarios',
        ]