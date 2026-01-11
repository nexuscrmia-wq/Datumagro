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
        from datumagro.apps.cadastros.models import Cliente
        
        user = self.context['request'].user
        cliente = None
        
        # Fallback: tente achar cliente por email do usuário
        try:
            if user and getattr(user, 'email', None):
                cliente = Cliente.objects.filter(email_contato=user.email).first()
            if cliente is None:
                # Se não encontrar por email, pega o primeiro cliente (dev only)
                cliente = Cliente.objects.first()
        except Exception:
            cliente = None

        if value.cliente != cliente:
            raise serializers.ValidationError("Esta categoria não pertence ao seu usuário.")
        return value


from .models import FormaPagamento


class FormaPagamentoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = FormaPagamento
        fields = [
            'id', 'tipo', 'tipo_display', 'titular', 'numero_cartao',
            'validade', 'bandeira', 'chave_pix', 'principal', 'ativo',
            'data_cadastro', 'ultima_atualizacao'
        ]
        read_only_fields = ['data_cadastro', 'ultima_atualizacao']

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        numero_cartao = attrs.get('numero_cartao')
        validade = attrs.get('validade')
        chave_pix = attrs.get('chave_pix')

        if tipo in ['CC', 'CD']:
            if not numero_cartao:
                raise serializers.ValidationError({'numero_cartao': 'Número do cartão é obrigatório para cartões'})
            if not validade:
                raise serializers.ValidationError({'validade': 'Data de validade é obrigatória para cartões'})

        if tipo == 'PX' and not chave_pix:
            raise serializers.ValidationError({'chave_pix': 'Chave PIX é obrigatória para pagamento via PIX'})

        return attrs

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)