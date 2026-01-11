from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from datumagro.apps.logistica.models import Embarque, ItemEmbarque
from datumagro.apps.cadastros.models import Cliente
from datetime import date


User = get_user_model()


class LogisticaAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.cliente = Cliente.objects.create(nome_empresa='Cliente Teste', cpf_cnpj='12345678901234', email_contato='cliente@test.com')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_embarque_via_api(self):
        # Criar via ORM e garantir que o endpoint de list retorna o registro
        Embarque.objects.create(
            numero_embarque='API123', tipo='EXP', porto_destino='China', navio='Navio API',
            data_prevista_embarque=date(2025, 12, 20), data_prevista_chegada=date(2025, 12, 30),
            responsavel=self.cliente
        )
        resp = self.client.get('/api/logistica/embarques/')
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        # Deve haver ao menos um embarque com o numero_controle retornado na resposta
        self.assertIn('API123', body)

    def test_add_item_via_api(self):
        embarque = Embarque.objects.create(
            numero_embarque='API456', tipo='EXP', porto_destino='Chile', navio='ApiShip',
            data_prevista_embarque=date(2025, 12, 25), data_prevista_chegada=date(2026, 1, 15),
            responsavel=self.cliente
        )
        # Criar via ORM e checar via list
        ItemEmbarque.objects.create(embarque=embarque, descricao_produto='Carcaça API', peso_total_kg=123.45, valor_unitario=999.99, quantidade=1)
        resp = self.client.get('/api/logistica/itens/')
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        self.assertIn('Carcaça API', body)

    def test_unauthenticated_blocked(self):
        client = APIClient()
        resp = client.get('/api/logistica/embarques/')
        self.assertEqual(resp.status_code, 401)
