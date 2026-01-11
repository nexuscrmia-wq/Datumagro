# datumagro/apps/core/tests.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal

# O modelo de usuário customizado que vamos criar no app 'usuarios'
Usuario = get_user_model()


class DashboardViewTest(TestCase):

    def setUp(self):
        # Cria um usuário, cliente e alguns dados para teste
        self.user = Usuario.objects.create_user(email='dashboard@teste.com', password='123')
        self.cliente = Cliente.objects.create(
            perfil_usuario=self.user.perfilusuario,
            nome_empresa='Fazenda Dashboard',
            cpf_cnpj='777888999000100'
        )
        self.propriedade = Propriedade.objects.create(
            cliente=self.cliente,
            nome_propriedade='Sede Dashboard',
            cidade='Brasília',
            estado='DF'
        )
        Animal.objects.create(
            propriedade=self.propriedade,
            brinco='DASH-01',
            sexo='F',
            data_nascimento='2023-01-01'
        )
        self.dashboard_url = reverse('core:dashboard')

    def test_usuario_nao_logado_e_redirecionado(self):
        """
        Garante que um usuário não logado não consegue acessar o dashboard
        e é redirecionado para a página de login.
        """
        response = self.client.get(self.dashboard_url)
        # O status 302 indica um redirecionamento
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={self.dashboard_url}')

    def test_usuario_logado_acessa_dashboard_com_sucesso(self):
        """
        Garante que um usuário logado consegue ver o dashboard.
        """
        self.client.login(email='dashboard@teste.com', password='123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_contexto_do_dashboard_contem_dados_corretos(self):
        """
        Verifica se os dados enviados para o template (o contexto) estão corretos.
        """
        self.client.login(email='dashboard@teste.com', password='123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        # Verifica se os números no contexto correspondem ao que criamos no setUp
        self.assertEqual(response.context['total_propriedades'], 1)
        self.assertEqual(response.context['total_animais_ativos'], 1)
        self.assertEqual(response.context['nome_usuario'], 'dashboard@teste.com')


class HealthAPITest(TestCase):
    def test_health_endpoint(self):
        """Verifica que /api/health/ retorna 200 e JSON com status 'ok'."""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')