# datumagro/apps/integracoes/serializers.py

from rest_framework import serializers

class DadosRfidPesagemSerializer(serializers.Serializer):
    """
    Valida os dados de entrada para a integração de pesagem automática.
    """
    brinco = serializers.CharField(max_length=50)
    peso_kg = serializers.DecimalField(max_digits=7, decimal_places=2)
    data_pesagem = serializers.DateField(required=False, help_text="Formato AAAA-MM-DD. Se não informado, usa a data atual.")
    # No futuro, podemos adicionar outros campos como 'temperatura_corporal', etc.