# datumagro/apps/rastreabilidade/tests.py

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from .models import PerfilPublicoAnimal
from .services import gerar_qr_code_para_perfil
from datumagro.apps.usuarios.models import Usuario
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal


class RastreabilidadeTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='rastreabilidade@teste.com', password='123')
        self.cliente = Cliente.objects.create(perfil_usuario=self.user.perfilusuario, nome_empresa='Fazenda Rastreio')
        self.propriedade = Propriedade.objects.create(cliente=self.cliente, nome_propriedade='Sede Rastreio')
        self.animal = Animal.objects.create(propriedade=self.propriedade, brinco='RASTREIO-01', sexo='M',
                                            data_nascimento='2022-01-01')
        self.perfil = PerfilPublicoAnimal.objects.create(animal=self.animal, is_publico=True)

    def test_view_publica_acessivel(self):
        """ Garante que a página pública de um perfil ativo é acessível por qualquer um. """
        url = reverse('rastreabilidade:perfil-publico-animal', kwargs={'slug': self.perfil.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_publica_inativa_retorna_404(self):
        """ Garante que uma página de um perfil não-público não é encontrada. """
        self.perfil.is_publico = False
        self.perfil.save()
        url = reverse('rastreabilidade:perfil-publico-animal', kwargs={'slug': self.perfil.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch('datumagro.apps.rastreabilidade.services.qrcode.QRCode')
    def test_geracao_de_qr_code_chama_biblioteca_correta(self, mock_qrcode):
        """
        Testa se o nosso serviço chama a biblioteca de QR Code com a URL correta,
        sem de fato gerar uma imagem no teste.
        """
        gerar_qr_code_para_perfil(self.perfil)

        # Verifica se o método 'add_data' da biblioteca foi chamado com a nossa URL
        mock_instance = mock_qrcode.return_value
        url_esperada = reverse('rastreabilidade:perfil-publico-animal', kwargs={'slug': self.perfil.slug})
        mock_instance.add_data.assert_called_with(url_esperada)