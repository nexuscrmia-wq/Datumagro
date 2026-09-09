# datumagro/apps/core/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET
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
import os


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


def download_apk(request):
    """Serve o APK do DatumAgro. Aceita GET e HEAD (Chrome Android manda HEAD primeiro)."""
    if request.method not in ('GET', 'HEAD'):
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['GET', 'HEAD'])
    apk_path = _apk_path()
    if not os.path.isfile(apk_path):
        raise Http404("APK não disponível no momento.")
    if request.method == 'HEAD':
        from django.http import HttpResponse
        size = os.path.getsize(apk_path)
        resp = HttpResponse(content_type='application/vnd.android.package-archive')
        resp['Content-Length'] = size
        resp['Content-Disposition'] = 'attachment; filename="DatumAgro.apk"'
        return resp
    return FileResponse(
        open(apk_path, 'rb'),
        as_attachment=True,
        filename='DatumAgro.apk',
        content_type='application/vnd.android.package-archive',
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_apk(request):
    """Admin-only: faz upload do APK para o Railway Volume."""
    if not (request.user.is_superuser or request.user.is_staff):
        return Response({'error': 'Acesso negado.'}, status=status.HTTP_403_FORBIDDEN)
    apk_file = request.FILES.get('apk')
    if not apk_file:
        return Response({'error': 'Envie o arquivo no campo "apk".'}, status=status.HTTP_400_BAD_REQUEST)
    if not apk_file.name.endswith('.apk'):
        return Response({'error': 'Apenas arquivos .apk são aceitos.'}, status=status.HTTP_400_BAD_REQUEST)
    apk_path = _apk_path()
    os.makedirs(os.path.dirname(apk_path), exist_ok=True)
    with open(apk_path, 'wb') as f:
        for chunk in apk_file.chunks():
            f.write(chunk)
    size_mb = os.path.getsize(apk_path) / (1024 * 1024)
    return Response({'status': 'ok', 'path': apk_path, 'size_mb': round(size_mb, 1)})


def _apk_path():
    return str(getattr(
        settings,
        'APK_STORAGE_PATH',
        os.path.join(settings.BASE_DIR, 'static', 'downloads', 'DatumAgro.apk'),
    ))


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
        # Usuários criados fora do fluxo normal (admin, convite) não têm Cliente.
        # Cria um automaticamente para não bloquear o onboarding.
        from datumagro.apps.cadastros.models import Cliente as ClienteModel, Propriedade
        nome = request.user.first_name or request.user.email.split('@')[0]
        cliente = ClienteModel.objects.create(
            email_contato=request.user.email,
            nome_empresa=f'Fazenda de {nome}',
            cpf_cnpj=str(request.user.id).zfill(14),
        )
        prop = Propriedade.objects.create(
            cliente=cliente,
            nome_propriedade=f'Propriedade de {nome}',
            cidade='', estado='',
        )
        request.user.propriedades.add(prop)

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
                'tipo_especie': cliente.tipo_especie,
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
        if 'tipo_especie' in data:
            cliente.tipo_especie = data['tipo_especie']

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


def redefinir_senha(request, token):
    """Página web de redefinição de senha — aberta pelo link do email."""
    from datumagro.apps.usuarios.models import Usuario
    from django.utils import timezone

    try:
        user = Usuario.objects.get(password_reset_token=token)
        expirado = (
            user.token_created_at is None
            or (timezone.now() - user.token_created_at).total_seconds() > 86400
        )
        token_valido = not expirado
    except Usuario.DoesNotExist:
        token_valido = False
        user = None

    ctx = {'token_valido': token_valido, 'sucesso': False, 'erro': ''}

    if request.method == 'POST' and token_valido:
        senha = request.POST.get('senha', '')
        senha2 = request.POST.get('senha2', '')
        if len(senha) < 8:
            ctx['erro'] = 'A senha deve ter pelo menos 8 caracteres.'
        elif senha != senha2:
            ctx['erro'] = 'As senhas não coincidem.'
        else:
            user.set_password(senha)
            user.password_reset_token = None
            user.token_created_at = None
            user.save()
            ctx['sucesso'] = True

    return render(request, 'redefinir_senha.html', ctx)


@api_view(['GET'])
@permission_classes([AllowAny])
def versao_app(request):
    """Retorna a versão atual do APK para checagem in-app."""
    versao = '1.7.0'  # atualizar aqui a cada release
    # Usa sempre o host real da requisição para garantir URL correta em qualquer domínio
    url_base = f"{request.scheme}://{request.get_host()}"
    return Response({
        'versao': versao,
        'url_download': f'{url_base}/baixar/apk/',
        'obrigatorio': os.getenv('UPDATE_OBRIGATORIO', 'false').lower() == 'true',
        'novidades': os.getenv('UPDATE_NOVIDADES', 'Raça livre: ao selecionar "Outra/Mestiço", agora é possível digitar qualquer raça. Sincronização entre dispositivos corrigida para proprietários.'),
    })


# ── Painel de Gestão de Usuários ────────────────────────────────────────────

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from datumagro.apps.assinaturas.models import Plano, Assinatura


@staff_member_required(login_url='/datumagro-gestao/login/')
def painel_usuarios(request):
    filtro = request.GET.get('filtro', 'todos')
    clientes_qs = Cliente.objects.select_related('assinatura__plano').order_by('-data_cadastro')

    def enrich(c):
        assinatura = getattr(c, 'assinatura', None)
        c.assinatura_plano = assinatura.plano.nome if assinatura and assinatura.plano else None
        c.assinatura_plano_id = assinatura.plano_id if assinatura else None
        return c

    todos = [enrich(c) for c in clientes_qs]
    pendentes = [c for c in todos if c.status_assinatura == 'PENDENTE']
    ativos = [c for c in todos if c.status_assinatura == 'ATIVO']

    return render(request, 'core/painel_usuarios.html', {
        'pendentes': pendentes if filtro != 'ativo' else [],
        'ativos': ativos if filtro != 'pendente' else [],
        'pendentes_count': len(pendentes),
        'ativos_count': len(ativos),
        'total_count': len(todos),
        'planos': Plano.objects.filter(ativo=True).order_by('valor_base_mensal'),
        'filtro': filtro,
    })


@staff_member_required(login_url='/datumagro-gestao/login/')
@require_POST
def painel_aprovar_usuario(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    cliente.status_assinatura = 'ATIVO'
    cliente.save(update_fields=['status_assinatura'])
    messages.success(request, f'✓ {cliente.nome_empresa} aprovado com sucesso!')
    return redirect(f'/painel/?filtro=pendente')


@staff_member_required(login_url='/datumagro-gestao/login/')
@require_POST
def painel_suspender_usuario(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    cliente.status_assinatura = 'PENDENTE'
    cliente.save(update_fields=['status_assinatura'])
    messages.success(request, f'Conta de {cliente.nome_empresa} suspensa.')
    return redirect('/painel/')


@staff_member_required(login_url='/datumagro-gestao/login/')
@require_POST
def painel_atribuir_plano(request, cliente_id):
    from datetime import timedelta
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    plano_id = request.POST.get('plano_id')
    if not plano_id:
        messages.error(request, 'Selecione um plano antes de salvar.')
        return redirect('/painel/')
    plano = get_object_or_404(Plano, pk=plano_id)
    assinatura = getattr(cliente, 'assinatura', None)
    if assinatura:
        assinatura.plano = plano
        assinatura.save(update_fields=['plano'])
    else:
        Assinatura.objects.create(
            cliente=cliente,
            plano=plano,
            data_inicio=timezone.now(),
            data_vencimento=timezone.now() + timedelta(days=30),
        )
    messages.success(request, f'Plano {plano.nome} atribuído a {cliente.nome_empresa}.')
    return redirect('/painel/')
