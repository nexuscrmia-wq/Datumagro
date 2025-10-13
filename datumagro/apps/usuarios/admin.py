# datumagro/apps/usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario
from .forms import CustomUserCreationForm, CustomUserChangeForm


class PerfilUsuarioInline(admin.StackedInline):
    """ Permite editar o Perfil diretamente na página do Usuário. """
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'usuario'


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Usuario
    list_display = ['email', 'nome_completo', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'groups']
    search_fields = ['email', 'nome_completo']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome_completo',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    inlines = (PerfilUsuarioInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


admin.site.register(Usuario, CustomUserAdmin)