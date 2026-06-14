# datumagro/apps/core/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from datumagro.apps.cadastros.models import Animal, Propriedade
from datumagro.apps.assinaturas.models import Assinatura
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import uuid
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


from django.shortcuts import render

def politica_privacidade(request):
    """Política de Privacidade pública — obrigatória para aprovação nas lojas."""
    return render(request, 'privacidade.html')


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


def _get_cliente_for_user(user):
    """Resolve the Cliente for a given user, with fallbacks."""
    try:
        if hasattr(user, 'perfilusuario') and user.perfilusuario.cliente:
            return user.perfilusuario.cliente
    except Exception:
        pass
    cliente = Cliente.objects.filter(email_contato=user.email).first()
    if cliente:
        return cliente
    return Cliente.objects.first()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_resumo(request):
    """
    Returns all dashboard KPIs in a single query set.
    GET /api/dashboard/resumo/
    """
    from datumagro.apps.inteligencia.models import Alerta
    from datumagro.apps.operacional.models import ManejoSanitario, RegistroReprodutivo
    from datumagro.apps.logistica.models import Embarque

    cliente = _get_cliente_for_user(request.user)
    hoje = timezone.now().date()
    sete_dias = hoje + timedelta(days=7)

    if cliente:
        total_animais = Animal.objects.filter(
            propriedade__cliente=cliente, ativo=True
        ).count()

        alertas_criticos = Alerta.objects.filter(
            cliente=cliente, status='PENDENTE'
        ).count()

        proximos_manejos = ManejoSanitario.objects.filter(
            animal__propriedade__cliente=cliente,
            data_aplicacao__gte=hoje,
            data_aplicacao__lte=sete_dias,
        ).count()

        nascimentos_mes = RegistroReprodutivo.objects.filter(
            matriz__propriedade__cliente=cliente,
            tipo_evento='PARTO',
            data_evento__year=hoje.year,
            data_evento__month=hoje.month,
        ).count()

        embarques_ativos = Embarque.objects.filter(
            status__in=['PLA', 'PRE', 'NAV', 'POR']
        ).count()

        pesagens_hoje = Animal.objects.filter(
            propriedade__cliente=cliente,
            pesagens__data_pesagem=hoje,
        ).distinct().count()
    else:
        total_animais = alertas_criticos = proximos_manejos = 0
        nascimentos_mes = embarques_ativos = pesagens_hoje = 0

    return Response({
        'total_animais': total_animais,
        'alertas_criticos': alertas_criticos,
        'proximos_manejos_7_dias': proximos_manejos,
        'nascimentos_mes': nascimentos_mes,
        'embarques_ativos': embarques_ativos,
        'pesagens_hoje': pesagens_hoje,
    })