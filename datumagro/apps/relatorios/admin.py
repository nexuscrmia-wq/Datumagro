# datumagro/apps/relatorios/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Relatorio


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('data_geracao', 'cliente', 'tipo_relatorio', 'status', 'link_download')
    list_filter = ('status', 'tipo_relatorio', 'data_geracao')
    search_fields = ('cliente__nome_empresa',)
    readonly_fields = ('data_geracao', 'cliente', 'tipo_relatorio', 'status', 'parametros', 'arquivo')

    def link_download(self, obj):
        if obj.arquivo:
            return format_html('<a href="{}" download>Baixar</a>', obj.arquivo.url)
        return "N/A"

    link_download.short_description = 'Download'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False