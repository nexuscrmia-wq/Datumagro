from django.test import TestCase
from datumagro.apps.logistica.models import Embarque, ItemEmbarque
from datumagro.apps.cadastros.models import Cliente
from datetime import date


class LogisticaModelsTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome_empresa='Cliente Teste', cpf_cnpj='12345678901234', email_contato='cliente@test.com')

    def test_itemembarque_defaults_and_str(self):
        embarque = Embarque.objects.create(
            numero_embarque='TEST123', tipo='EXP', porto_destino='China', navio='Navio Teste',
            data_prevista_embarque=date(2025, 12, 1), data_prevista_chegada=date(2025, 12, 20),
            responsavel=self.cliente
        )

        item = ItemEmbarque.objects.create(
            embarque=embarque,
            descricao_produto='Carcaça Nelore',
            peso_total_kg=1500.50,
            valor_unitario=5000.00,
            quantidade=1
        )

        self.assertEqual(str(item), 'Carcaça Nelore - 1 un - 1500.5kg')
        self.assertEqual(float(item.peso_total_kg), 1500.50)

    def test_serializer_totals(self):
        embarque = Embarque.objects.create(
            numero_embarque='TOT123', tipo='EXP', porto_destino='Turquia', navio='Navio X',
            data_prevista_embarque=date(2025, 12, 5), data_prevista_chegada=date(2025, 12, 25),
            responsavel=self.cliente
        )
        ItemEmbarque.objects.create(embarque=embarque, descricao_produto='P1', peso_total_kg=100, valor_unitario=10, quantidade=1)
        ItemEmbarque.objects.create(embarque=embarque, descricao_produto='P2', peso_total_kg=200, valor_unitario=20, quantidade=1)

        # Totals computed via related manager
        itens = embarque.itens.all()
        total_peso = sum(i.peso_total_kg for i in itens)
        total_valor = sum(i.valor_total for i in itens)

        self.assertEqual(float(total_peso), 300.0)
        self.assertEqual(float(total_valor), 30.0)
