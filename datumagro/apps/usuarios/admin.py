# datumagro/apps/usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario, TipoUsuario
from .forms import CustomUserCreationForm, CustomUserChangeForm


class PerfilUsuarioInline(admin.StackedInline):
    """Permite editar o Perfil diretamente na página do Usuário."""
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'usuario'
    fields = ('bio', 'endereco', 'cidade', 'estado', 'cargo', 'setor', 'data_admissao', 'ativo')


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Usuario
    list_display = ['email', 'nome_completo', 'tipo_usuario', 'is_staff', 'is_active']
    list_filter = ['tipo_usuario', 'is_staff', 'is_active', 'groups']
    search_fields = ['email', 'nome_completo']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome_completo', 'first_name', 'last_name', 'telefone', 'data_nascimento', 'foto_perfil')}),
        ('Tipo de Usuário', {
            'fields': ('tipo_usuario', 'propriedades'),
            'description': 'Define o nível de acesso e as propriedades que o usuário pode gerenciar.'
        }),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    inlines = (PerfilUsuarioInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Admin para gerenciar perfis de usuários."""
    list_display = ['usuario', 'cargo', 'setor', 'data_admissao', 'ativo']
    list_filter = ['setor', 'ativo', 'data_admissao']
    search_fields = ['usuario__email', 'usuario__nome_completo', 'cargo']
    fields = ('usuario', 'bio', 'endereco', 'cidade', 'estado', 'cargo', 'setor', 'data_admissao', 'ativo')
    readonly_fields = ('usuario',)


admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(PerfilUsuario, PerfilUsuarioAdmin)