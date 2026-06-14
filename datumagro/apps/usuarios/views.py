from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import uuid

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario, PerfilUsuario, TipoUsuario, ConviteEquipe
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UsuarioSerializer, 
    ResetPasswordSerializer,
    UsuarioLoginSerializer,
    FuncionarioRegistroSerializer,
    PerfilUsuarioSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsProprietario


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action in ['registrar', 'login', 'reset_password', 'confirm_reset_password']:
            return [AllowAny()]
        if self.action in ['registrar_funcionario']:
            return [IsProprietario()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def registrar(self, request):
        """Registrar novo usuário como proprietário."""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UsuarioSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': f'Erro interno do servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Login com retorno de tipo de usuário e permissões.
        
        Request:
        {
            "email": "usuario@example.com",
            "password": "senha123"
        }
        
        Response:
        {
            "user": {
                "id": 1,
                "email": "usuario@example.com",
                "nome_completo": "João Silva",
                "tipo_usuario": "funcionario",
                "tipo_usuario_display": "Funcionário",
                "foto_perfil": null,
                "telefone": "11999999999",
                "permissoes": {
                    "can_view_animais": true,
                    "can_view_alertas": true,
                    "can_view_vacinas": true,
                    ...
                },
                "propriedades": [...]
            },
            "refresh": "token_refresh",
            "access": "token_access"
        }
        """
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(
                {'error': 'E-mail e senha são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)
        if user:
            if not user.is_active:
                return Response(
                    {'error': 'Usuário inativo.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            refresh = RefreshToken.for_user(user)
            
            # Preparar dados para o serializer de login
            user_data = {
                'id': user.id,
                'email': user.email,
                'nome_completo': user.nome_completo or user.first_name,
                'tipo_usuario': user.tipo_usuario,
                'foto_perfil': user.foto_perfil.url if user.foto_perfil else None,
                'telefone': user.telefone,
                'usuario_obj': user,  # Passado para o serializer calcular permissões
            }
            
            serializer = UsuarioLoginSerializer(user_data)
            
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        
        return Response(
            {'error': 'Credenciais inválidas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=['post'], permission_classes=[IsProprietario])
    def registrar_funcionario(self, request):
        """
        Registrar novo funcionário (apenas proprietários podem).
        
        Request:
        {
            "email": "funcionario@example.com",
            "first_name": "João",
            "last_name": "Silva",
            "telefone": "11999999999",
            "password": "senha123",
            "password2": "senha123",
            "setor": "producao",
            "cargo": "Assistente de Produção"
        }
        """
        serializer = FuncionarioRegistroSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validação de limite de funcionários do plano do cliente
        owner = request.user
        owner_perfil = getattr(owner, 'perfilusuario', None)
        cliente = getattr(owner_perfil, 'cliente', None)
        if not cliente:
            return Response({'detail': 'Cliente não associado ao proprietário. Crie/associe um cliente primeiro.'}, status=400)

        assinatura = getattr(cliente, 'assinatura', None)
        if not assinatura or not getattr(assinatura, 'plano', None):
            return Response({'detail': 'Assinatura/plano não encontrado para o cliente.'}, status=403)

        plano = assinatura.plano
        max_func = getattr(plano, 'max_funcionarios', 0)

        # Conta funcionários já vinculados às propriedades do cliente
        current_count = Usuario.objects.filter(
            tipo_usuario=TipoUsuario.FUNCIONARIO,
            propriedades__cliente=cliente
        ).distinct().count()

        if current_count >= max_func:
            return Response(
                {'detail': f"Limite de funcionários atingido para o plano atual ({max_func})."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Cria o usuário e associa perfil/propriedades ao cliente do proprietário
        user = serializer.save()

        # Associa o perfil do novo usuário ao mesmo cliente (em memória)
        try:
            perfil = getattr(user, 'perfilusuario', None)
            if perfil:
                perfil.cliente = cliente
                perfil.save()
        except Exception:
            # Não é crítico — apenas logamos no debug se necessário
            pass

        # Copia acessos de propriedades do proprietário para o funcionário
        try:
            user.propriedades.set(owner.propriedades.all())
        except Exception:
            pass

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Funcionário registrado com sucesso',
            'user': UsuarioSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Solicitar reset de senha."""
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        token = get_random_string(48)
        user.password_reset_token = token
        user.token_created_at = timezone.now()
        user.save()

        reset_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password/{token}"
        context = {'user': user, 'reset_url': reset_url}
        message = render_to_string('usuarios/reset_password_email.html', context)

        try:
            send_mail(
                'Recuperação de Senha - DatumAgro',
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            if getattr(settings, 'DEBUG', False):
                return Response({
                    'message': 'Falha ao enviar email via SMTP (dev). Token gerado (apenas dev):', 
                    'token': token
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({
                    'message': 'Email de recuperação enfileirado.'
                }, status=status.HTTP_202_ACCEPTED)

        return Response({'message': 'Email de recuperação enviado.'})

    @action(detail=False, methods=['post'])
    def confirm_reset_password(self, request):
        """Confirmar reset de senha com token."""
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            user = Usuario.objects.get(password_reset_token=token)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Token inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar expiração (24h)
        if user.token_created_at and (timezone.now() - user.token_created_at).total_seconds() > 86400:
            return Response(
                {'error': 'Token expirado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.password_reset_token = None
        user.token_created_at = None
        user.save()
        
        return Response({'message': 'Senha alterada com sucesso'})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_cliente(self, request):
        """
        Dev helper: cria um Cliente e o associa ao PerfilUsuario do usuário atual.
        Útil para testes locais.
        """
        from datumagro.apps.cadastros.models import Cliente

        user = request.user
        perfil = getattr(user, 'perfilusuario', None)
        if not perfil:
            return Response(
                {'detail': 'Perfil do usuário não encontrado.'}, 
                status=400
            )

        nome_empresa = request.data.get('nome_empresa') or f'Empresa {user.email}'
        cpf_cnpj = request.data.get('cpf_cnpj') or str(uuid.uuid4())[:14]
        telefone = request.data.get('telefone') or ''

        cliente = Cliente.objects.create(
            perfil_usuario=perfil,
            nome_empresa=nome_empresa,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone,
            email_contato=user.email
        )

        perfil.cliente = cliente
        perfil.save()

        return Response({
            'id': cliente.id, 
            'nome_empresa': cliente.nome_empresa
        }, status=201)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna informações do usuário logado com permissões."""
        user = request.user
        user_data = {
            'id': user.id,
            'email': user.email,
            'nome_completo': user.nome_completo or user.first_name,
            'tipo_usuario': user.tipo_usuario,
            'tipo_usuario_display': user.get_tipo_usuario_display(),
            'foto_perfil': user.foto_perfil.url if user.foto_perfil else None,
            'telefone': user.telefone,
            'usuario_obj': user,
        }
        
        serializer = UsuarioLoginSerializer(user_data)
        return Response(serializer.data)


class PerfilUsuarioView(RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# Helpers de equipe
# ---------------------------------------------------------------------------

def _get_cliente_equipe(user):
    """Retorna o Cliente associado ao usuário (via perfil ou email)."""
    from datumagro.apps.cadastros.models import Cliente
    perfil = getattr(user, 'perfilusuario', None)
    cliente = getattr(perfil, 'cliente', None) if perfil else None
    if not cliente:
        cliente = Cliente.objects.filter(email_contato=user.email).first()
    return cliente


def _permissions_flutter(user):
    """Converte get_permissoes() do Django para as chaves esperadas pelo Flutter."""
    p = user.get_permissoes()
    return {
        'can_view_finance': p.get('can_view_financeiro', False),
        'can_edit_finance': p.get('can_edit_financeiro', False),
        'can_view_animals': p.get('can_view_animais', False),
        'can_edit_animals': p.get('can_edit_animais', False),
        'can_delete_animals': p.get('can_delete_dados', False),
        'can_register_manejo': p.get('can_edit_vacinas', False),
        'can_manage_lotes': p.get('can_manage_lotes', False),
        'can_manage_team': p.get('can_manage_usuarios', False),
    }


def _cargo_label(user):
    """Retorna o cargo no formato que o Flutter espera (ADMIN/VETERINARIO/OPERADOR)."""
    perfil = getattr(user, 'perfilusuario', None)
    stored = (getattr(perfil, 'cargo', '') or '').upper()
    if stored in ('ADMIN', 'VETERINARIO', 'OPERADOR'):
        return stored
    if user.tipo_usuario in (TipoUsuario.PROPRIETARIO, TipoUsuario.GERENTE):
        return 'ADMIN'
    return 'OPERADOR'


def _member_json(user):
    perfil = getattr(user, 'perfilusuario', None)
    data_ingresso = None
    if perfil and getattr(perfil, 'data_admissao', None):
        data_ingresso = perfil.data_admissao.isoformat()
    elif user.date_joined:
        data_ingresso = user.date_joined.date().isoformat()
    return {
        'id': user.id,
        'user': {
            'email': user.email,
            'nome': user.nome_completo or user.first_name or user.email.split('@')[0],
        },
        'cargo': _cargo_label(user),
        'permissions': _permissions_flutter(user),
        'data_ingresso': data_ingresso,
    }


def _cargo_to_tipo(cargo):
    """Mapeia cargo Flutter para tipo_usuario Django."""
    return TipoUsuario.GERENTE if cargo == 'ADMIN' else TipoUsuario.FUNCIONARIO


# ---------------------------------------------------------------------------
# Endpoints de equipe: /api/equipe/...
# ---------------------------------------------------------------------------

from rest_framework.decorators import api_view, permission_classes as pc


@api_view(['GET'])
@pc([IsAuthenticated])
def equipe_membros(request):
    """Lista todos os membros da equipe do mesmo cliente."""
    cliente = _get_cliente_equipe(request.user)
    if not cliente:
        return Response({'detail': 'Cliente não encontrado.'}, status=404)

    membros = Usuario.objects.filter(
        propriedades__cliente=cliente,
        is_active=True,
    ).exclude(id=request.user.id).distinct()

    return Response([_member_json(u) for u in membros])


@api_view(['POST'])
@pc([IsAuthenticated, IsProprietario])
def equipe_convidar(request):
    """Cria um ConviteEquipe (token + código) e retorna os detalhes."""
    cliente = _get_cliente_equipe(request.user)
    if not cliente:
        return Response({'detail': 'Cliente não encontrado. Crie um cliente primeiro.'}, status=400)

    email = request.data.get('email', '').strip()
    cargo = request.data.get('cargo', 'OPERADOR').upper()

    convite = ConviteEquipe.objects.create(
        criado_por=request.user,
        cliente=cliente,
        email=email,
        tipo_usuario=_cargo_to_tipo(cargo),
    )

    # Retorna no formato TeamMember para compatibilidade com o Flutter atual,
    # mais os campos extras do convite (código e link para compartilhar).
    base_url = request.build_absolute_uri('/')[:-1]
    return Response({
        'id': convite.id,
        'user': {'email': email or 'Convite aberto', 'nome': 'Aguardando aceite'},
        'cargo': cargo,
        'permissions': _permissions_flutter(request.user),  # placeholder
        'data_ingresso': None,
        # Campos extras exibidos opcionalmente na UI:
        'invite': {
            'codigo': convite.codigo,
            'token': convite.token,
            'link': f'{base_url}/entrar-equipe/?t={convite.token}',
            'expira_em': convite.expira_em.isoformat(),
        },
    }, status=201)


@api_view(['POST'])
@pc([AllowAny])
def equipe_aceitar(request):
    """
    Aceita convite por token (link) ou código manual e registra o novo usuário.

    Body: { "token": "..." | "codigo": "ABC123",
            "nome": "...", "email": "...", "password": "...", "password2": "..." }
    """
    token = request.data.get('token', '').strip()
    codigo = request.data.get('codigo', '').strip().upper()

    if not token and not codigo:
        return Response({'detail': 'Forneça token ou codigo.'}, status=400)

    try:
        if token:
            convite = ConviteEquipe.objects.get(token=token)
        else:
            convite = ConviteEquipe.objects.get(codigo=codigo)
    except ConviteEquipe.DoesNotExist:
        return Response({'detail': 'Convite não encontrado.'}, status=404)

    if not convite.is_valid:
        return Response({'detail': 'Convite expirado ou já utilizado.'}, status=400)

    email = request.data.get('email', convite.email).strip()
    nome = request.data.get('nome', '').strip()
    password = request.data.get('password', '')
    password2 = request.data.get('password2', '')

    if not email:
        return Response({'detail': 'Email é obrigatório.'}, status=400)
    if password != password2:
        return Response({'detail': 'As senhas não coincidem.'}, status=400)
    if len(password) < 6:
        return Response({'detail': 'Senha deve ter ao menos 6 caracteres.'}, status=400)
    if Usuario.objects.filter(email=email).exists():
        return Response({'detail': 'Este email já está cadastrado.'}, status=400)

    user = Usuario.objects.create_user(
        email=email,
        password=password,
        nome_completo=nome,
        tipo_usuario=convite.tipo_usuario,
    )

    # Associa às propriedades do cliente do convite
    from datumagro.apps.cadastros.models import Propriedade
    propriedades = Propriedade.objects.filter(cliente=convite.cliente)
    user.propriedades.set(propriedades)

    convite.status = ConviteEquipe.STATUS_ACEITO
    convite.aceito_por = user
    convite.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'user': {
            'id': user.id,
            'email': user.email,
            'nome_completo': user.nome_completo,
            'tipo_usuario': user.tipo_usuario,
            'permissoes': user.get_permissoes(),
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=201)


@api_view(['DELETE'])
@pc([IsAuthenticated, IsProprietario])
def equipe_remover(request, pk):
    """Remove um membro da equipe (desativa o usuário)."""
    cliente = _get_cliente_equipe(request.user)
    if not cliente:
        return Response(status=404)

    try:
        user = Usuario.objects.get(
            id=pk,
            propriedades__cliente=cliente,
            is_active=True,
        )
    except Usuario.DoesNotExist:
        return Response({'detail': 'Membro não encontrado.'}, status=404)

    if user.id == request.user.id:
        return Response({'detail': 'Você não pode remover a si mesmo.'}, status=400)

    user.is_active = False
    user.propriedades.clear()
    user.save()
    return Response(status=204)


@api_view(['GET', 'PUT'])
@pc([IsAuthenticated])
def equipe_permissoes(request, pk):
    """Obtém ou atualiza as permissões (tipo_usuario) de um membro."""
    cliente = _get_cliente_equipe(request.user)
    if not cliente:
        return Response(status=404)

    try:
        user = Usuario.objects.get(id=pk, propriedades__cliente=cliente, is_active=True)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Membro não encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(_permissions_flutter(user))

    # PUT — mapeamos can_manage_team → gerente, caso contrário funcionario
    can_manage = request.data.get('can_manage_team', False)
    user.tipo_usuario = TipoUsuario.GERENTE if can_manage else TipoUsuario.FUNCIONARIO
    user.save()
    return Response(_permissions_flutter(user))


# ---------------------------------------------------------------------------
# Exclusão de conta — obrigatório Apple App Store
# ---------------------------------------------------------------------------

@api_view(['POST'])
@pc([IsAuthenticated])
def excluir_conta(request):
    """
    Anonimiza e desativa a conta do usuário autenticado.
    Body: { "password": "senha_atual" }
    """
    password = request.data.get('password', '')
    if not request.user.check_password(password):
        return Response({'detail': 'Senha incorreta.'}, status=400)

    user = request.user
    # Anonimiza dados pessoais (LGPD art. 18)
    import hashlib
    anon_suffix = hashlib.sha256(user.email.encode()).hexdigest()[:12]
    user.email = f'excluido_{anon_suffix}@anonimizado.invalid'
    user.nome_completo = ''
    user.first_name = ''
    user.last_name = ''
    user.telefone = None
    user.foto_perfil = None
    user.is_active = False
    user.set_unusable_password()
    user.save()
    user.propriedades.clear()

    return Response({'detail': 'Conta excluída com sucesso.'}, status=200)