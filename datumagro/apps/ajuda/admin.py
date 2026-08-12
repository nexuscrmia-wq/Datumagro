from django.contrib import admin
from .models import GuiaModulo


@admin.register(GuiaModulo)
class GuiaModuloAdmin(admin.ModelAdmin):
    list_display = ("modulo_slug", "especie", "titulo", "ativo", "atualizado_em")
    list_filter = ("modulo_slug", "especie", "ativo")
    search_fields = ("titulo", "como_usar_passo_a_passo", "dicas_agronomicas_zootecnicas")
    ordering = ("modulo_slug", "especie")
