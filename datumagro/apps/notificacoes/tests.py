# datumagro/apps/notificacoes/tests.py

from django.test import TestCase
from django.conf import settings
from unittest.mock import patch
from .models import LogNotificacao
from .services import disparar_notificacoes_para_alerta
from datumagro.apps.usuarios.models import Usuario
from datumagro.apps.cadastros.models import Cliente
from datumagro.apps.inteligencia.models import Alerta


class NotificacaoServicesTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='notificacao@teste.com', password='123')
        self.cliente = Cliente.objects.create(
            perfil_usuario=self.user.perfilusuario,
            nome_empresa='Fazenda Notificada',
            email_contato='contato@fazenda.com',
            telefone='+5522999998888'  # Número de exemplo
        )
        self.alerta = Alerta.objects.create(
            cliente=self.cliente,
            tipo_alerta='SANITARIO',
            mensagem='Este é um alerta de teste.'
        )
        # Simula as configurações do Twilio para os testes
        settings.TWILIO_ACCOUNT_SID = 'test_sid'
        settings.TWILIO_AUTH_TOKEN = 'test_token'
        settings.TWILIO_WHATSAPP_NUMBER = '+14155238886'

    @patch('datumagro.apps.notificacoes.services.send_mail')
    def test_envia_notificacao_por_email_com_sucesso(self, mock_send_mail):
        """
        Garante que o serviço de e-mail é chamado e o log é criado corretamente.
        """
        disparar_notificacoes_para_alerta(self.alerta)

        mock_send_mail.assert_called_once()
        log = LogNotificacao.objects.filter(canal='EMAIL').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'ENVIADO')
        self.assertEqual(log.destinatario, 'contato@fazenda.com')

    @patch('datumagro.apps.notificacoes.services.TwilioClient')
    def test_envia_notificacao_por_whatsapp_com_sucesso(self, mock_twilio_client):
        """
        Garante que a API do Twilio é chamada e o log é criado corretamente.
        """
        # Configura o mock para simular o comportamento da API do Twilio
        mock_instance = mock_twilio_client.return_value
        mock_instance.messages.create.return_value.sid = 'mock_sid_123'

        disparar_notificacoes_para_alerta(self.alerta)

        mock_instance.messages.create.assert_called_once()
        log = LogNotificacao.objects.filter(canal='WHATSAPP').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'ENVIADO')
        self.assertIn('mock_sid_123', log.detalhes_retorno)