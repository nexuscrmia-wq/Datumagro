import secrets
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from .managers import UsuarioManager


class TipoUsuario(models.TextChoices):
    """Tipos de usuários no sistema com permissões diferentes."""
    PROPRIETARIO = 'proprietario', 'Proprietário'
    GERENTE = 'gerente', 'Gerente'
    FUNCIONARIO = 'funcionario', 'Funcionário'


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuário customizado usado pelo projeto."""
    email = models.EmailField('E-mail', unique=True)
    username = models.CharField('Username', max_length=150, blank=True)
    nome_completo = models.CharField('Nome Completo', max_length=255, blank=True)
    first_name = models.CharField('Nome', max_length=150, blank=True)
    last_name = models.CharField('Sobrenome', max_length=150, blank=True)
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True)
    data_nascimento = models.DateField('Data de Nascimento', blank=True, null=True)
    foto_perfil = models.ImageField('Foto de Perfil', upload_to='perfis/', blank=True, null=True)

    # Tipo de usuário e permissões
    tipo_usuario = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PROPRIETARIO,
        help_text='Define nível de acesso e permissões no sistema'
    )
    propriedades = models.ManyToManyField(
        'cadastros.Propriedade',
        blank=True,
        related_name='usuarios_acesso',
        help_text='Propriedades a que o funcionário tem acesso'
    )

    # Controle
    is_active = models.BooleanField('Ativo', default=True)
    is_staff = models.BooleanField('Staff', default=False)
    date_joined = models.DateTimeField('Data de Registro', default=timezone.now)

    # Campos para reset de senha
    password_reset_token = models.CharField(max_length=128, blank=True, null=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tipo_usuario']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.email}"

    # Métodos para verificar tipo de usuário
    def is_proprietario(self):
        """Verifica se é proprietário (acesso total)."""
        return self.tipo_usuario == TipoUsuario.PROPRIETARIO

    def is_gerente(self):
        """Verifica se é gerente (acesso parcial)."""
        return self.tipo_usuario == TipoUsuario.GERENTE

    def is_funcionario(self):
        """Verifica se é funcionário (acesso limitado)."""
        return self.tipo_usuario == TipoUsuario.FUNCIONARIO

    def get_permissoes(self):
        """Retorna as permissões disponíveis baseado no tipo de usuário."""
        permissoes_por_tipo = {
            TipoUsuario.PROPRIETARIO: {
                'can_view_animais': True,
                'can_edit_animais': True,
                'can_view_propriedades': True,
                'can_edit_propriedades': True,
                'can_view_financeiro': True,
                'can_edit_financeiro': True,
                'can_view_alertas': True,
                'can_view_vacinas': True,
                'can_edit_vacinas': True,
                'can_view_relatorios': True,
                'can_manage_usuarios': True,
                'can_manage_lotes': True,
                'can_delete_dados': True,
            },
            TipoUsuario.GERENTE: {
                'can_view_animais': True,
                'can_edit_animais': True,
                'can_view_propriedades': True,
                'can_edit_propriedades': False,
                'can_view_financeiro': True,
                'can_edit_financeiro': False,
                'can_view_alertas': True,
                'can_view_vacinas': True,
                'can_edit_vacinas': True,
                'can_view_relatorios': True,
                'can_manage_usuarios': False,
                'can_manage_lotes': True,
                'can_delete_dados': False,
            },
            TipoUsuario.FUNCIONARIO: {
                'can_view_animais': True,
                'can_edit_animais': False,
                'can_view_propriedades': True,  # vê apenas as suas (filtrado no get_queryset)
                'can_edit_propriedades': False,
                'can_view_financeiro': False,
                'can_edit_financeiro': False,
                'can_view_alertas': True,
                'can_view_vacinas': True,
                'can_edit_vacinas': False,
                'can_view_relatorios': False,
                'can_manage_usuarios': False,
                'can_manage_lotes': False,
                'can_delete_dados': False,
            },
        }
        return permissoes_por_tipo.get(self.tipo_usuario, {})


class PerfilUsuario(models.Model):
    """Perfil adicional do usuário com informações complementares."""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfilusuario')
    bio = models.TextField('Biografia', blank=True, default='')
    endereco = models.CharField('Endereço', max_length=255, blank=True, default='')
    cidade = models.CharField('Cidade', max_length=100, blank=True, default='')
    estado = models.CharField('Estado', max_length=2, blank=True, default='')
    cargo = models.CharField(
        'Cargo',
        max_length=100,
        blank=True,
        help_text='Cargo/posição do funcionário na propriedade'
    )
    setor = models.CharField(
        'Setor',
        max_length=100,
        blank=True,
        choices=[
            ('producao', 'Produção'),
            ('reprodução', 'Reprodução'),
            ('sanidade', 'Sanidade'),
            ('alimentos', 'Alimentos'),
            ('administrativo', 'Administrativo'),
            ('outro', 'Outro'),
        ],
        help_text='Setor de trabalho do funcionário'
    )
    data_admissao = models.DateField('Data de Admissão', blank=True, null=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuário'

    def __str__(self):
        return f"Perfil de {self.usuario.email}"


def _gerar_codigo():
    """6 dígitos alfanuméricos maiúsculos, sem caracteres ambíguos (0/O, 1/I)."""
    alfabeto = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(alfabeto) for _ in range(6))


def _gerar_token():
    return secrets.token_urlsafe(48)


def _expira_em():
    return timezone.now() + timedelta(hours=48)


class ConviteEquipe(models.Model):
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_ACEITO = 'ACEITO'
    STATUS_EXPIRADO = 'EXPIRADO'
    STATUS_CANCELADO = 'CANCELADO'
    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_ACEITO, 'Aceito'),
        (STATUS_EXPIRADO, 'Expirado'),
        (STATUS_CANCELADO, 'Cancelado'),
    ]

    token = models.CharField(max_length=72, unique=True, default=_gerar_token)
    codigo = models.CharField(max_length=6, unique=True, default=_gerar_codigo)
    email = models.EmailField(blank=True, default='')
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.FUNCIONARIO,
    )
    criado_por = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='convites_criados'
    )
    cliente = models.ForeignKey(
        'cadastros.Cliente', on_delete=models.CASCADE, related_name='convites'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField(default=_expira_em)
    aceito_por = models.OneToOneField(
        Usuario, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='convite_aceito'
    )

    class Meta:
        verbose_name = 'Convite de Equipe'
        verbose_name_plural = 'Convites de Equipe'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Convite {self.codigo} → {self.email or 'aberto'} ({self.status})"

    @property
    def is_valid(self):
        return self.status == self.STATUS_PENDENTE and timezone.now() < self.expira_em