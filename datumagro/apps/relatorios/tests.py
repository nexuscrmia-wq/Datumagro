# datumagro/apps/relatorios/tests.py
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from .models import Relatorio
from datumagro.apps.usuarios.models import Usuario
from datumagro.apps.cadastros.models import Cliente, Propriedade
from datumagro.apps.operacional.models import Lote


class RelatoriosApiTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='relatorios@teste.com', password='123')
        self.cliente = Cliente.objects.create(perfil_usuario=self.user.perfilusuario, nome_empresa='Fazenda Relatorios')
        self.propriedade = Propriedade.objects.create(cliente=self.cliente, nome_propriedade='Sede')
        self.lote = Lote.objects.create(propriedade=self.propriedade, nome='Lote para Relatório')
        self.client.login(email='relatorios@teste.com', password='123')

    def test_lista_relatorios_view_requer_login(self):
        self.client.logout()
        url = reverse('relatorios:historico-relatorios-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('datumagro.apps.relatorios.views.gerar_pdf_lote_task.delay')
    def test_disparar_geracao_de_relatorio_com_sucesso(self, mock_gerar_task):
        url = reverse('relatorios:historico-relatorios-gerar-pdf-lote')
        dados = {'lote_id': self.lote.id}
        response = self.client.post(url, dados, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_gerar_task.assert_called_once_with(self.lote.id)