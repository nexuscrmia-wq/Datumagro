# datumagro/apps/financeiro/admin.py

from django.contrib import admin
from .models import Categoria, Transacao

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'tipo')
    list_filter = ('tipo', 'cliente')
    search_fields = ('nome',)

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'cliente', 'categoria', 'valor', 'data')
    list_filter = ('data', 'categoria', 'cliente')
    search_fields = ('descricao', 'categoria__nome')
    autocomplete_fields = ('cliente', 'categoria', 'animal')
    date_hierarchy = 'data'