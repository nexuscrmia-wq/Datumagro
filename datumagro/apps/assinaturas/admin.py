# datumagro/apps/assinaturas/admin.py

from django.contrib import admin
from .models import Plano, Assinatura

@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_base_mensal', 'limite_animais', 'hardware_incluso', 'suporte_especialista', 'ativo')
    list_filter = ('ativo', 'hardware_incluso', 'suporte_especialista')
    search_fields = ('nome', 'descricao')
    ordering = ('valor_base_mensal',)

@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'plano', 'status', 'data_inicio', 'data_vencimento', 'is_ativa')
    list_filter = ('status', 'plano')
    search_fields = ('cliente__nome_empresa', 'plano__nome')
    autocomplete_fields = ('cliente', 'plano')
    ordering = ('-data_inicio',)
    readonly_fields = ('data_inicio', 'data_vencimento')