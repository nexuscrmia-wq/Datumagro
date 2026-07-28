# datumagro/apps/financeiro/serializers.py

from rest_framework import serializers
from .models import Categoria, Transacao


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'tipo']


class TransacaoSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source='categoria.id', read_only=True)

    class Meta:
        model = Transacao
        fields = [
            'id',
            'tipo',
            'status',
            'descricao',
            'valor',
            'data',
            'observacao',
            'categoria',
            'categoria_id',
            'categoria_nome',
            'animal',
        ]
        read_only_fields = ['categoria_id']

    def to_internal_value(self, data):
        """
        Accept 'categoria' as either an integer PK or a string name.
        When it's a string, store it in categoria_nome and resolve/create
        the Categoria FK automatically.
        """
        data = dict(data)

        raw_cat = data.get('categoria')
        if raw_cat is not None and not isinstance(raw_cat, int):
            # String name supplied — stash it as categoria_nome and resolve FK
            cat_name = str(raw_cat)
            data['categoria_nome'] = cat_name
            # Remove 'categoria' so DRF doesn't try to coerce the string to a PK
            data.pop('categoria', None)

        return super().to_internal_value(data)

    def _get_cliente(self):
        from datumagro.apps.cadastros.models import Cliente
        user = self.context['request'].user
        cliente = Cliente.objects.filter(email_contato=user.email).first()
        if cliente is None:
            cliente = Cliente.objects.first()
        return cliente

    def _resolve_categoria(self, validated_data):
        """Auto-create Categoria from categoria_nome if FK not set."""
        cat_nome = validated_data.get('categoria_nome', '')
        if not validated_data.get('categoria') and cat_nome:
            cliente = self._get_cliente()
            tipo_transacao = validated_data.get('tipo', 'DESPESA')
            cat_tipo = 'RECEITA' if tipo_transacao == 'RECEITA' else 'CUSTO'
            if cliente:
                cat, _ = Categoria.objects.get_or_create(
                    cliente=cliente,
                    nome=cat_nome,
                    defaults={'tipo': cat_tipo},
                )
                validated_data['categoria'] = cat

    def create(self, validated_data):
        from datumagro.apps.cadastros.models import Cliente
        user = self.context['request'].user
        cliente = self._get_cliente()
        validated_data['cliente'] = cliente
        self._resolve_categoria(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._resolve_categoria(validated_data)
        return super().update(instance, validated_data)


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
