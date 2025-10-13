# datumagro/apps/inteligencia/admin.py

from django.contrib import admin
from .models import Alerta

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('data_criacao', 'cliente', 'tipo_alerta', 'status', 'animal')
    list_filter = ('status', 'tipo_alerta', 'data_criacao', 'cliente')
    search_fields = ('cliente__nome_empresa', 'animal__brinco', 'mensagem')
    readonly_fields = ('data_criacao', 'cliente', 'animal', 'tipo_alerta', 'mensagem')
    list_per_page = 30