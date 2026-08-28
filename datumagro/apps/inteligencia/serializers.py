# datumagro/apps/inteligencia/serializers.py

from rest_framework import serializers
from .models import Alerta


class AlertaSerializer(serializers.ModelSerializer):
    animal_brinco = serializers.CharField(source='animal.brinco', read_only=True, default=None)

    class Meta:
        model = Alerta
        fields = [
            'id',
            'tipo_alerta',
            'mensagem',
            'status',
            'data_criacao',
            'animal',
            'animal_brinco',
        ]
        read_only_fields = ['id', 'data_criacao', 'animal_brinco', 'status']