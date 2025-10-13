# datumagro/apps/rastreabilidade/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import PerfilPublicoAnimal

@admin.register(PerfilPublicoAnimal)
class PerfilPublicoAnimalAdmin(admin.ModelAdmin):
    list_display = ('animal', 'is_publico', 'slug', 'link_para_perfil')
    list_filter = ('is_publico',)
    search_fields = ('animal__brinco',)
    prepopulated_fields = {'slug': ('titulo_perfil',)}
    readonly_fields = ('qr_code_imagem',)

    def link_para_perfil(self, obj):
        if obj.is_publico and obj.slug:
            url = reverse('rastreabilidade:perfil-publico-animal', kwargs={'slug': obj.slug})
            return format_html('<a href="{}" target="_blank">Ver Perfil</a>', url)
        return "Perfil não público"
    link_para_perfil.short_description = 'Link Público'

    def qr_code_imagem(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="150" height="150" />', obj.qr_code.url)
        return "QR Code ainda não gerado."
    qr_code_imagem.short_description = 'Imagem do QR Code'