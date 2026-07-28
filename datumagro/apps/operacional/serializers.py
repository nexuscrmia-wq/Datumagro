# datumagro/apps/operacional/serializers.py

from rest_framework import serializers
from .models import ProdutoSanitario, ManejoSanitario, RegistroReprodutivo, Lote, Piquete


class ProdutoSanitarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoSanitario
        fields = '__all__'


class ManejoSanitarioSerializer(serializers.ModelSerializer):
    animal_nome = serializers.CharField(source='animal.brinco', read_only=True, default=None)

    class Meta:
        model = ManejoSanitario
        fields = '__all__'


class RegistroReprodutivoSerializer(serializers.ModelSerializer):
    matriz_brinco = serializers.CharField(source='matriz.brinco', read_only=True, default=None)
    touro_brinco = serializers.CharField(source='touro.brinco', read_only=True, default=None)

    class Meta:
        model = RegistroReprodutivo
        fields = '__all__'


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = '__all__'


class PiqueteSerializer(serializers.ModelSerializer):
    lote_atual_nome = serializers.CharField(source='lote_atual.nome', read_only=True, default=None)

    class Meta:
        model = Piquete
        fields = '__all__'