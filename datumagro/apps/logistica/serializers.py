from rest_framework import serializers
from .models import Embarque, ItemEmbarque, RastreamentoEmbarque
from datumagro.apps.cadastros.serializers import AnimalSerializer


class ItemEmbarqueSerializer(serializers.ModelSerializer):
    animal_details = AnimalSerializer(source='animal', read_only=True)

    class Meta:
        model = ItemEmbarque
        fields = '__all__'


class RastreamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RastreamentoEmbarque
        fields = '__all__'


class EmbarqueSerializer(serializers.ModelSerializer):
    itens = ItemEmbarqueSerializer(many=True, read_only=True)
    rastreamento = RastreamentoSerializer(many=True, read_only=True)

    total_peso = serializers.SerializerMethodField()
    total_valor = serializers.SerializerMethodField()
    quantidade_itens = serializers.SerializerMethodField()

    class Meta:
        model = Embarque
        fields = '__all__'
        read_only_fields = ['responsavel']

    def get_total_peso(self, obj: Embarque) -> float:
        return float(sum(item.peso_total_kg for item in obj.itens.all()))

    def get_total_valor(self, obj: Embarque) -> float:
        return float(sum(item.valor_total for item in obj.itens.all()))
        
    def get_quantidade_itens(self, obj: Embarque) -> int:
        return obj.itens.count()

