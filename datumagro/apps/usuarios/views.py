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

from .models import Usuario
from .serializers import UsuarioSerializer, ResetPasswordSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action in ['registrar', 'login', 'reset_password', 'confirm_reset_password']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def registrar(self, request):
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

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'E-mail e senha são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user:
            if not user.is_active:
                return Response({'error': 'Usuário inativo.'}, status=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UsuarioSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

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
            # Em ambiente de desenvolvimento o SMTP pode falhar (credenciais incorretas).
            # Evitamos 500 retornando um 202 e, em DEBUG, incluímos o token no corpo para facilitar testes.
            if getattr(settings, 'DEBUG', False):
                return Response({'message': 'Falha ao enviar email via SMTP (dev). Token gerado (apenas dev):', 'token': token}, status=status.HTTP_202_ACCEPTED)
            else:
                # Em produção, registrar o erro e retornar sucesso genérico para não expor detalhes
                return Response({'message': 'Email de recuperação enfileirado.'}, status=status.HTTP_202_ACCEPTED)

        return Response({'message': 'Email de recuperação enviado.'})

    @action(detail=False, methods=['post'])
    def confirm_reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            user = Usuario.objects.get(password_reset_token=token)
        except Usuario.DoesNotExist:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)

        # opcional: checar expiração (24h)
        if user.token_created_at and (timezone.now() - user.token_created_at).total_seconds() > 86400:
            return Response({'error': 'Token expirado'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.password_reset_token = None
        user.token_created_at = None
        user.save()
        return Response({'message': 'Senha alterada com sucesso'})

    @action(detail=False, methods=['post'])
    def create_cliente(self, request):
        """Utility action to create a Cliente and associate it to the user's PerfilUsuario.
        This is convenient for smoke tests and local development. Expects optional fields:
        - nome_empresa, cpf_cnpj, telefone, email_contato
        If not provided, sensible defaults will be used.
        """
        from datumagro.apps.cadastros.models import Cliente
        user = request.user
        perfil = getattr(user, 'perfilusuario', None)

        nome = request.data.get('nome_empresa') or f"Cliente de {user.email}"
        cpf_cnpj = request.data.get('cpf_cnpj') or f"00000000000{user.id}"
        telefone = request.data.get('telefone') or ''
        email_contato = request.data.get('email_contato') or user.email

        # Create or get existing client by email
        cliente, created = Cliente.objects.get_or_create(email_contato=email_contato, defaults={
            'nome_empresa': nome,
            'cpf_cnpj': cpf_cnpj,
            'telefone': telefone,
        })

        if perfil is None:
            # try to create perfil if signals didn't run for some reason
            from .models import PerfilUsuario
            perfil = PerfilUsuario.objects.create(usuario=user)

        perfil.cliente = cliente
        perfil.save()

        return Response({'cliente_id': cliente.id, 'created': created})

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
            return Response({'detail': 'Perfil do usuário não encontrado.'}, status=400)

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

        return Response({'id': cliente.id, 'nome_empresa': cliente.nome_empresa}, status=201)



class PerfilUsuarioView(RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user