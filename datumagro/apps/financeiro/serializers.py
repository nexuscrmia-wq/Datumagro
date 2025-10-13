# datumagro/apps/financeiro/serializers.py

from rest_framework import serializers
from .models import Categoria, Transacao


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'tipo']


class TransacaoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    categoria_tipo = serializers.CharField(source='categoria.tipo', read_only=True)

    class Meta:
        model = Transacao
        fields = [
            'id',
            'descricao',
            'valor',
            'data',
            'observacao',
            'categoria',
            'categoria_nome',
            'categoria_tipo',
            'animal'
        ]

    def validate_categoria(self, value):
        """
        Validação para garantir que a categoria pertence ao mesmo cliente da transação.
        """
        cliente = self.context['request'].user.perfilusuario.cliente
        if value.cliente != cliente:
            raise serializers.ValidationError("Esta categoria não pertence ao seu usuário.")
        return value