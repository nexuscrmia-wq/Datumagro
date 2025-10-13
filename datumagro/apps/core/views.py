# datumagro/apps/core/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
# O import do 'ObjectDoesNotExist' foi REMOVIDO, pois não é mais necessário.
from datumagro.apps.cadastros.models import Animal, Propriedade
from datumagro.apps.assinaturas.models import Assinatura


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