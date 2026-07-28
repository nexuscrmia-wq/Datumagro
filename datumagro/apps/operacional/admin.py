# datumagro/apps/operacional/admin.py

from django.contrib import admin
from .models import ProdutoSanitario, ManejoSanitario, RegistroReprodutivo, Lote, Piquete

@admin.register(ProdutoSanitario)
class ProdutoSanitarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'tipo_produto', 'fabricante')
    list_filter = ('tipo_produto', 'cliente')
    search_fields = ('nome', 'fabricante')

@admin.register(ManejoSanitario)
class ManejoSanitarioAdmin(admin.ModelAdmin):
    list_display = ('animal', 'tipo', 'data', 'produto')
    list_filter = ('tipo', 'data')
    search_fields = ('animal__brinco', 'produto', 'descricao')
    autocomplete_fields = ('animal',)
    date_hierarchy = 'data'

@admin.register(RegistroReprodutivo)
class RegistroReprodutivoAdmin(admin.ModelAdmin):
    list_display = ('matriz', 'tipo_evento', 'data_evento', 'ordem_parto', 'touro', 'resultado_dg')
    list_filter = ('tipo_evento', 'resultado_dg', 'data_evento')
    search_fields = ('matriz__brinco', 'touro__brinco')
    autocomplete_fields = ('matriz', 'touro')
    date_hierarchy = 'data_evento'
    readonly_fields = ('ordem_parto',)

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'propriedade', 'contagem_animais')
    list_filter = ('propriedade',)
    search_fields = ('nome',)
    filter_horizontal = ('animais',)

    def contagem_animais(self, obj):
        return obj.animais.count()
    contagem_animais.short_description = 'Nº de Animais'

@admin.register(Piquete)
class PiqueteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'propriedade', 'status', 'tipo_capim', 'tamanho_hectares', 'lote_atual')
    list_filter = ('status', 'tipo_capim', 'propriedade')
    search_fields = ('nome',)