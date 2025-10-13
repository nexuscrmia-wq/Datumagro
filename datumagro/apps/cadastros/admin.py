# datumagro/apps/cadastros/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Propriedade, Animal, RegistroPesagem


class PropriedadeInline(admin.TabularInline):
    model = Propriedade
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_empresa', 'cpf_cnpj', 'email_contato', 'data_cadastro')
    search_fields = ('nome_empresa', 'cpf_cnpj')
    inlines = [PropriedadeInline]


class AnimalInline(admin.TabularInline):
    model = Animal
    extra = 0
    fields = ('brinco', 'sexo', 'raca', 'data_nascimento', 'ativo')
    show_change_link = True


@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ('nome_propriedade', 'cliente', 'cidade', 'estado', 'objetivo_producao')
    list_filter = ('estado', 'objetivo_producao', 'tipo_solo')
    search_fields = ('nome_propriedade', 'cliente__nome_empresa')
    inlines = [AnimalInline]


class RegistroPesagemInline(admin.TabularInline):
    model = RegistroPesagem
    extra = 1
    ordering = ('-data_pesagem',)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        'brinco', 'propriedade', 'raca', 'sexo', 'categoria',
        'aptidao', 'is_reprodutor', 'status_reprodutivo', 'ativo', 'ver_foto'
    )
    list_filter = (
        'propriedade', 'sexo', 'raca', 'categoria', 'aptidao',
        'status_reprodutivo', 'ativo', 'temperamento', 'is_reprodutor'
    )
    search_fields = ('brinco', 'propriedade__nome_propriedade')
    autocomplete_fields = ('propriedade', 'pai', 'mae')
    inlines = [RegistroPesagemInline]

    fieldsets = (
        ('Identificação Principal', {
            'fields': ('propriedade', 'brinco', 'foto_perfil', 'ativo')
        }),
        ('Dados Zootécnicos', {
            'fields': ('raca', 'sexo', 'data_nascimento', 'categoria', 'aptidao')
        }),
        ('Controle Reprodutivo', {
            'fields': ('status_reprodutivo', 'is_reprodutor')
        }),
        ('Comportamento', {
            'fields': ('temperamento', 'caracteristicas_adicionais')
        }),
        ('Genealogia', {
            'fields': ('pai', 'mae')
        }),
    )

    class Media:
        js = ('admin/js/animal_admin.js',)

    def ver_foto(self, obj):
        if obj.foto_perfil:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                               obj.foto_perfil.url)
        return "Sem foto"

    ver_foto.short_description = 'Foto'


@admin.register(RegistroPesagem)
class RegistroPesagemAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data_pesagem', 'peso_kg')
    search_fields = ('animal__brinco',)
    autocomplete_fields = ('animal',)