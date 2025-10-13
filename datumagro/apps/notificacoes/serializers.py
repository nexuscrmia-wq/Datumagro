# datumagro/apps/notificacoes/serializers.py

from rest_framework import serializers
from .models import LogNotificacao

class LogNotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogNotificacao
        fields = ['id', 'canal', 'destinatario', 'status', 'timestamp', 'detalhes_retorno']
        read_only_fields = fields