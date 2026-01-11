# datumagro/apps/core/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
# O import do 'ObjectDoesNotExist' foi REMOVIDO, pois não é mais necessário.
from datumagro.apps.cadastros.models import Animal, Propriedade
from datumagro.apps.assinaturas.models import Assinatura
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import uuid
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datumagro.apps.cadastros.models import Cliente


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    View principal do sistema, o Dashboard.
    Agora com a lógica simplificada para carregar os dados.
    """
    template_name = 'core/dashboard.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nome_usuario'] = self.request.user.get_full_name() or self.request.user.email

        # Inicializa as variáveis do dashboard com valores padrão
        context['is_admin_sem_cliente'] = True
        context['assinatura'] = None
        context['total_propriedades'] = 0
        context['total_animais_ativos'] = 0

        # A verificação agora é mais simples e segura
        if hasattr(self.request.user, 'perfilusuario') and self.request.user.perfilusuario.cliente:
            cliente = self.request.user.perfilusuario.cliente
            context['is_admin_sem_cliente'] = False

            # Se o cliente existe, buscamos os dados dele com segurança
            context['assinatura'] = getattr(cliente, 'assinatura', None)
            context['total_propriedades'] = Propriedade.objects.filter(cliente=cliente).count()
            context['total_animais_ativos'] = Animal.objects.filter(
                propriedade__cliente=cliente,
                ativo=True
            ).count()

        return context


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """
    Simple health endpoint for frontend probes.
    Returns JSON with status and optional version from settings.VERSION.
    """
    version = getattr(settings, "VERSION", "unknown")
    return Response({"status": "ok", "version": version})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cliente_for_user(request):
    """
    Debug helper (development only): cria um Cliente e associa ao PerfilUsuario do usuário autenticado.
    Útil para testes locais/integração (não recomendado em produção).
    """
    user = request.user
    perfil = getattr(user, 'perfilusuario', None)
    if not perfil:
        return Response({'detail': 'Perfil do usuário não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

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

    return Response({'id': cliente.id, 'nome_empresa': cliente.nome_empresa}, status=status.HTTP_201_CREATED)