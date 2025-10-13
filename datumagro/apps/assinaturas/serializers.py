# datumagro/apps/assinaturas/serializers.py

from rest_framework import serializers
from .models import Plano, Assinatura

class PlanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plano
        fields = [
            'id',
            'nome',
            'descricao',
            'valor_base_mensal',
            'limite_animais',
            'hardware_incluso',
            'suporte_especialista',
        ]

class AssinaturaSerializer(serializers.ModelSerializer):
    plano = PlanoSerializer(read_only=True)
    cliente_nome = serializers.CharField(source='cliente.nome_empresa', read_only=True)

    class Meta:
        model = Assinatura
        fields = [
            'id',
            'cliente_nome',
            'plano',
            'status',
            'data_inicio',
            'data_vencimento',
            'is_ativa',
        ]