from django.contrib import admin
from .models import Embarque, ItemEmbarque, RastreamentoEmbarque


class RastreamentoInline(admin.TabularInline):
    model = RastreamentoEmbarque
    extra = 0
    readonly_fields = ('data_evento',)


class ItemEmbarqueInline(admin.TabularInline):
    model = ItemEmbarque
    extra = 1


class EmbarqueAdmin(admin.ModelAdmin):
    list_display = ('numero_embarque', 'navio', 'tipo', 'status', 'porto_destino', 'data_prevista_embarque')
    search_fields = ('numero_embarque', 'navio', 'porto_destino')
    list_filter = ('tipo', 'status', 'porto_destino')
    inlines = [ItemEmbarqueInline, RastreamentoInline]
    readonly_fields = ('numero_embarque', 'created_at', 'updated_at')


class ItemEmbarqueAdmin(admin.ModelAdmin):
    list_display = ('embarque', 'tipo_produto', 'descricao_produto', 'peso_total_kg', 'valor_total', 'animal')
    search_fields = ('descricao_produto', 'gta', 'sif')
    list_filter = ('embarque', 'tipo_produto')


# Register safely to avoid AlreadyRegistered on reloads
try:
    admin.site.register(Embarque, EmbarqueAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(ItemEmbarque, ItemEmbarqueAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(RastreamentoEmbarque)
except admin.sites.AlreadyRegistered:
    pass

