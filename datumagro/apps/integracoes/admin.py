# datumagro/apps/integracoes/admin.py

from django.contrib import admin
from .models import LogIntegracao


@admin.register(LogIntegracao)
class LogIntegracaoAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'cliente', 'tipo_integracao', 'status')
    list_filter = ('status', 'tipo_integracao', 'timestamp')
    search_fields = ('cliente__nome_empresa', 'dados_recebidos')
    readonly_fields = ('timestamp', 'cliente', 'tipo_integracao', 'dados_recebidos', 'status', 'mensagem_retorno')

    def has_add_permission(self, request):
        return False  # Ninguém pode adicionar um log manualmente

    def has_change_permission(self, request, obj=None):
        return False  # Ninguém pode alterar um log