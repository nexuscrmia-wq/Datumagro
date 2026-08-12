from rest_framework import serializers
from .models import GuiaModulo


class GuiaModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuiaModulo
        fields = [
            "modulo_slug",
            "titulo",
            "especie",
            "como_usar_passo_a_passo",
            "dicas_agronomicas_zootecnicas",
        ]
