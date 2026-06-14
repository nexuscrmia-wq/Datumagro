"""
Permissões customizadas para controlar acesso aos endpoints baseado no tipo de usuário.
"""
from rest_framework.permissions import BasePermission
from .models import TipoUsuario


class IsProprietario(BasePermission):
    """Apenas proprietários podem acessar."""
    message = "Apenas proprietários podem acessar este recurso."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_proprietario()


class IsGerente(BasePermission):
    """Apenas gerentes e proprietários podem acessar."""
    message = "Apenas gerentes e proprietários podem acessar este recurso."

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            (request.user.is_gerente() or request.user.is_proprietario())
        )


class IsFuncionario(BasePermission):
    """Apenas funcionários, gerentes e proprietários podem acessar."""
    message = "Acesso restrito."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class PermissaoAnimais(BasePermission):
    """Controla acesso aos endpoints de animais."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in ['GET']:
            # Todos podem ver animais
            return request.user.get_permissoes().get('can_view_animais', False)
        
        # Para editar/criar/deletar, apenas proprietários e gerentes
        return request.user.get_permissoes().get('can_edit_animais', False)


class PermissaoPropriedades(BasePermission):
    """Controla acesso aos endpoints de propriedades."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        permissoes = request.user.get_permissoes()
        
        if request.method in ['GET']:
            return permissoes.get('can_view_propriedades', False)
        
        # Apenas proprietários podem editar propriedades
        return request.user.is_proprietario()


class PermissaoFinanceiro(BasePermission):
    """Controla acesso aos endpoints de financeiro."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        permissoes = request.user.get_permissoes()
        
        if request.method in ['GET']:
            return permissoes.get('can_view_financeiro', False)
        
        # Apenas proprietários podem editar financeiro
        return permissoes.get('can_edit_financeiro', False)


class PermissaoAlertas(BasePermission):
    """Controla acesso aos endpoints de alertas."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Todos autenticados podem ver alertas
        return request.user.get_permissoes().get('can_view_alertas', False)


class PermissaoVacinas(BasePermission):
    """Controla acesso aos endpoints de vacinas."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        permissoes = request.user.get_permissoes()
        
        if request.method in ['GET']:
            return permissoes.get('can_view_vacinas', False)
        
        # Apenas gerentes e proprietários podem editar vacinas
        return permissoes.get('can_edit_vacinas', False)


class PermissaoLotes(BasePermission):
    """Controla acesso aos endpoints de lotes."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Funcionários não podem gerenciar lotes
        if request.user.is_funcionario():
            return False
        
        return request.user.get_permissoes().get('can_manage_lotes', False)


class PermissaoRelatorios(BasePermission):
    """Controla acesso aos endpoints de relatórios."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Apenas proprietários e gerentes podem ver relatórios
        return request.user.get_permissoes().get('can_view_relatorios', False)


class PermissaoGerenciarUsuarios(BasePermission):
    """Controla acesso para gerenciar usuários (criar funcionários)."""
    message = "Apenas proprietários podem gerenciar usuários."
    
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            request.user.is_proprietario()
        )


class CanDeleteData(BasePermission):
    """Apenas proprietários podem deletar dados."""
    message = "Você não tem permissão para deletar dados."
    
    def has_permission(self, request, view):
        if request.method not in ['DELETE']:
            return True
        
        return (
            request.user and request.user.is_authenticated and
            request.user.get_permissoes().get('can_delete_dados', False)
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Permite acesso apenas para donos ou leitura apenas.
    Útil para que usuários vejam apenas seus dados.
    """
    def has_object_permission(self, request, view, obj):
        # Leitura permitida para qualquer usuário autenticado
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        
        # Escrita permitida apenas para proprietários
        return request.user.is_proprietario()


class IsImportacaoInternacional(BasePermission):
    """Permissão que permite acesso somente a clientes cujo plano libera importação internacional."""
    message = "Acesso negado: seu plano não permite importação internacional."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        from datumagro.apps.cadastros.models import Cliente
        prop = request.user.propriedades.select_related('cliente').first()
        cliente = prop.cliente if prop else Cliente.objects.filter(email_contato=request.user.email).first()
        if not cliente:
            return False

        assinatura = getattr(cliente, 'assinatura', None)
        plano = getattr(assinatura, 'plano', None) if assinatura else None
        if not plano:
            return False

        return bool(getattr(plano, 'acesso_importacao_internacional', False))
