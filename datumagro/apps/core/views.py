# datumagro/apps/core/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
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
    Debug / onboarding helper: cria um Cliente + Propriedade padrão e associa ao usuário.
    Necessário para que novos Proprietários possam usar o sistema sem passar pelo admin.
    """
    from datumagro.apps.cadastros.models import Propriedade

    user = request.user

    # Idempotente: se já tem um cliente via propriedade, retorna ele
    existing = _get_cliente_for_user(user)
    if existing:
        return Response({'id': existing.id, 'nome_empresa': existing.nome_empresa}, status=status.HTTP_200_OK)

    nome_empresa = request.data.get('nome_empresa') or f'Empresa de {user.first_name or user.email.split("@")[0]}'
    cpf_cnpj = request.data.get('cpf_cnpj') or str(uuid.uuid4())[:14]
    telefone = request.data.get('telefone') or ''
    nome_propriedade = request.data.get('nome_propriedade') or f'Propriedade de {nome_empresa}'

    cliente = Cliente.objects.create(
        nome_empresa=nome_empresa,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        email_contato=user.email,
    )

    # Cria uma Propriedade padrão e associa o usuário a ela
    prop = Propriedade.objects.create(
        cliente=cliente,
        nome_propriedade=nome_propriedade,
        cidade=request.data.get('cidade', ''),
        estado=request.data.get('estado', ''),
    )
    user.propriedades.add(prop)

    return Response({
        'id': cliente.id,
        'nome_empresa': cliente.nome_empresa,
        'propriedade_id': prop.id,
    }, status=status.HTTP_201_CREATED)


def _get_cliente_for_user(user):
    """Resolve o Cliente do usuário via propriedades ou email_contato."""
    # Caminho principal: usuário → propriedades → cliente
    prop = user.propriedades.select_related('cliente').first()
    if prop:
        return prop.cliente
    # Fallback: cliente cadastrado com o email do usuário (ex: Proprietário recém-criado)
    return Cliente.objects.filter(email_contato=user.email).first()


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
            data__gte=hoje,
            data__lte=sete_dias,
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

        from datumagro.apps.cadastros.models import RegistroPesagem
        from django.db.models import Avg
        gmd_result = RegistroPesagem.objects.filter(
            animal__propriedade__cliente=cliente,
            data_pesagem=hoje,
            gmd_calculado__isnull=False,
        ).aggregate(media=Avg('gmd_calculado'))
        gmd_medio_hoje = float(gmd_result['media']) if gmd_result['media'] is not None else None
    else:
        total_animais = alertas_criticos = proximos_manejos = 0
        nascimentos_mes = embarques_ativos = pesagens_hoje = 0
        gmd_medio_hoje = None

    return Response({
        'total_animais': total_animais,
        'alertas_criticos': alertas_criticos,
        'proximos_manejos_7_dias': proximos_manejos,
        'nascimentos_mes': nascimentos_mes,
        'embarques_ativos': embarques_ativos,
        'pesagens_hoje': pesagens_hoje,
        'gmd_medio_hoje': gmd_medio_hoje,
    })

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def onboarding_etapa(request):
    """
    GET  → retorna etapa atual e status do onboarding
    PATCH → salva dados da etapa e avança para a próxima
    """
    cliente = _get_cliente_for_user(request.user)

    if not cliente:
        return Response({'detail': 'Cliente não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        prop = Propriedade.objects.filter(cliente=cliente).first()
        return Response({
            'etapa_atual': cliente.onboarding_etapa,
            'onboarding_completo': cliente.onboarding_completo,
            'dados': {
                'nome_empresa': cliente.nome_empresa,
                'tipo_documento': cliente.tipo_documento,
                'cpf_cnpj': cliente.cpf_cnpj,
                'emite_nota_fiscal': cliente.emite_nota_fiscal,
                'inscricao_estadual': cliente.inscricao_estadual,
                'faixa_rebanho': cliente.faixa_rebanho,
                'num_funcionarios': cliente.num_funcionarios,
                'sistema_anterior': cliente.sistema_anterior,
                'principal_desafio': cliente.principal_desafio,
                'propriedade_nome': prop.nome_propriedade if prop else '',
                'propriedade_estado': prop.estado if prop else '',
                'propriedade_cidade': prop.cidade if prop else '',
                'propriedade_hectares': str(prop.hectares) if prop and prop.hectares else '',
                'tipo_operacao': prop.tipo_operacao if prop else 'CORTE',
            }
        })

    # PATCH — salvar dados da etapa
    data = request.data
    etapa = data.get('etapa', cliente.onboarding_etapa)

    if etapa == 2:
        # Dados da fazenda
        if 'nome_empresa' in data:
            cliente.nome_empresa = data['nome_empresa']
        if 'tipo_documento' in data:
            cliente.tipo_documento = data['tipo_documento']
        if 'cpf_cnpj' in data:
            cliente.cpf_cnpj = data['cpf_cnpj']
        if 'emite_nota_fiscal' in data:
            cliente.emite_nota_fiscal = data['emite_nota_fiscal']
        if 'inscricao_estadual' in data:
            cliente.inscricao_estadual = data['inscricao_estadual']

        prop = Propriedade.objects.filter(cliente=cliente).first()
        if prop:
            if 'propriedade_estado' in data:
                prop.estado = data['propriedade_estado']
            if 'propriedade_cidade' in data:
                prop.cidade = data['propriedade_cidade']
            if 'propriedade_hectares' in data:
                try:
                    prop.hectares = float(data['propriedade_hectares'])
                except (ValueError, TypeError):
                    pass
            prop.save()

        cliente.onboarding_etapa = max(cliente.onboarding_etapa, 3)

    elif etapa == 3:
        # Dados da operação
        if 'faixa_rebanho' in data:
            cliente.faixa_rebanho = data['faixa_rebanho']
        if 'num_funcionarios' in data:
            cliente.num_funcionarios = int(data.get('num_funcionarios', 0))
        if 'sistema_anterior' in data:
            cliente.sistema_anterior = data['sistema_anterior']

        prop = Propriedade.objects.filter(cliente=cliente).first()
        if prop and 'tipo_operacao' in data:
            prop.tipo_operacao = data['tipo_operacao']
            prop.save()

        cliente.onboarding_etapa = max(cliente.onboarding_etapa, 4)

    elif etapa == 4:
        # Finalizar onboarding
        if 'principal_desafio' in data:
            cliente.principal_desafio = data['principal_desafio']
        cliente.onboarding_completo = True
        cliente.onboarding_etapa = 4

    cliente.save()

    return Response({
        'etapa_atual': cliente.onboarding_etapa,
        'onboarding_completo': cliente.onboarding_completo,
    })


def home(request):
    return render(request, "home.html")
