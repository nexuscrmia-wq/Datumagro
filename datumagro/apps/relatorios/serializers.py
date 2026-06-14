from rest_framework import serializers
from .models import Relatorio


class RelatorioSerializer(serializers.ModelSerializer):
    # Campos renomeados para corresponder ao modelo Flutter
    tipo = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    data_criacao = serializers.DateTimeField(source='data_geracao')
    url_download = serializers.SerializerMethodField()
    tamanho_arquivo = serializers.SerializerMethodField()

    class Meta:
        model = Relatorio
        fields = [
            'id', 'tipo', 'nome', 'data_criacao',
            'status', 'url_download', 'tamanho_arquivo', 'parametros',
        ]

    def get_tipo(self, obj):
        # Mapeia tipos internos para os tipos que o Flutter entende
        mapa = {
            'PDF_DESEMPENHO_LOTE': 'DESEMPENHO',
            'EXCEL_LISTA_ANIMAIS': 'PRODUCAO',
            'FINANCEIRO': 'FINANCEIRO',
            'SANITARIO': 'SANITARIO',
            'REPRODUTIVO': 'REPRODUTIVO',
            'PRODUCAO': 'PRODUCAO',
        }
        return mapa.get(obj.tipo_relatorio, obj.tipo_relatorio)

    def get_nome(self, obj):
        return obj.get_tipo_relatorio_display()

    def get_url_download(self, obj):
        if obj.arquivo and obj.status == 'CONCLUIDO':
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.arquivo.url)
            return obj.arquivo.url
        return None

    def get_tamanho_arquivo(self, obj):
        if obj.arquivo:
            try:
                return obj.arquivo.size
            except Exception:
                pass
        return None
