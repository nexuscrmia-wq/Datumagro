# datumagro/apps/relatorios/serializers.py

from rest_framework import serializers
from .models import Relatorio


class RelatorioSerializer(serializers.ModelSerializer):
    tipo_relatorio = serializers.CharField(source='get_tipo_relatorio_display')

    class Meta:
        model = Relatorio
        fields = ['id', 'data_geracao', 'tipo_relatorio', 'status', 'arquivo', 'parametros']
        read_only_fields = fields