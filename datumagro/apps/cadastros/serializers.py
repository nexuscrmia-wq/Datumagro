# datumagro/apps/cadastros/serializers.py

from rest_framework import serializers
from .models import Cliente, Propriedade, Animal, RegistroPesagem

class PropriedadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propriedade
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    propriedades = PropriedadeSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'

class RegistroPesagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroPesagem
        fields = '__all__'

class AnimalSerializer(serializers.ModelSerializer):
    # Campos para facilitar a exibição da genealogia no front-end
    pai_brinco = serializers.CharField(source='pai.brinco', read_only=True, default=None)
    mae_brinco = serializers.CharField(source='mae.brinco', read_only=True, default=None)
    idade_meses = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = '__all__'
        read_only_fields = ('id',)

    def get_idade_meses(self, obj):
        from .services import calcular_idade_em_meses
        return calcular_idade_em_meses(obj.data_nascimento)