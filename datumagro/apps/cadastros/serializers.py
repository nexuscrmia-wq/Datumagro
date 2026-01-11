# datumagro/apps/cadastros/serializers.py

from rest_framework import serializers
from .models import (Cliente, Propriedade, Animal, RegistroPesagem,
                     Piquete, Vacina, AplicacaoVacina, InformacaoGenetica, FichaTecnicaAnimal)

class PropriedadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propriedade
        fields = '__all__'
        # cliente será definido pelo servidor a partir do usuário autenticado
        # e não deve ser enviado pelo cliente (flutter/mobile)
        read_only_fields = ('cliente',)

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
        read_only_fields = ('id', 'updated_at')

    def get_idade_meses(self, obj: Animal) -> int:
        from .services import calcular_idade_em_meses
        return calcular_idade_em_meses(obj.data_nascimento)


class PiqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piquete
        fields = '__all__'
        read_only_fields = ('propriedade',)


class VacinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacina
        fields = '__all__'


class AplicacaoVacinaSerializer(serializers.ModelSerializer):
    vacina_nome = serializers.CharField(source='vacina.nome', read_only=True)

    class Meta:
        model = AplicacaoVacina
        fields = '__all__'


class InformacaoGeneticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacaoGenetica
        fields = '__all__'


class FichaTecnicaAnimalSerializer(serializers.ModelSerializer):
    # Campos relacionados para facilitar a visualização
    animal_brinco = serializers.CharField(source='animal.brinco', read_only=True)
    animal_raca = serializers.CharField(source='animal.raca', read_only=True)
    animal_sexo = serializers.CharField(source='animal.sexo', read_only=True)
    piquete_nome = serializers.CharField(source='piquete_atual.nome', read_only=True)

    # Informações calculadas
    idade_meses = serializers.SerializerMethodField()
    vacinas_pendentes = serializers.SerializerMethodField()
    ultima_pesagem_info = serializers.SerializerMethodField()

    class Meta:
        model = FichaTecnicaAnimal
        fields = '__all__'
        read_only_fields = ('animal', 'gmd_diario', 'gmd_semanal', 'gmd_quinzenal',
                           'gmd_mensal', 'gmd_anual', 'peso_atual_kg', 'data_ultima_pesagem',
                           'vacinas_em_dia', 'proxima_vacina')

    def get_idade_meses(self, obj):
        from .services import calcular_idade_em_meses
        return calcular_idade_em_meses(obj.animal.data_nascimento)

    def get_vacinas_pendentes(self, obj):
        from django.utils import timezone
        hoje = timezone.now().date()
        return obj.animal.aplicacoes_vacina.filter(
            proxima_dose__isnull=False,
            proxima_dose__lt=hoje
        ).count()

    def get_ultima_pesagem_info(self, obj):
        ultima = obj.animal.pesagens.order_by('-data_pesagem').first()
        if ultima:
            return {
                'peso': ultima.peso_kg,
                'data': ultima.data_pesagem,
                'observacao': ultima.observacao
            }
        return None