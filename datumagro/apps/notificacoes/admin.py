# datumagro/apps/notificacoes/admin.py

from django.contrib import admin
from .models import LogNotificacao

@admin.register(LogNotificacao)
class LogNotificacaoAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'cliente', 'canal', 'status', 'alerta_origem')
    list_filter = ('status', 'canal', 'timestamp')
    search_fields = ('cliente__nome_empresa', 'destinatario')
    readonly_fields = ('timestamp', 'cliente', 'canal', 'destinatario', 'status', 'alerta_origem', 'detalhes_retorno')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False