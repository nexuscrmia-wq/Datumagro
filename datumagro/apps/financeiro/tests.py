# datumagro/apps/financeiro/tests.py

from django.test import TestCase
from datetime import date, timedelta
from decimal import Decimal
from datumagro.apps.usuarios.models import Usuario
from datumagro.apps.cadastros.models import Cliente
from .models import Categoria, Transacao
from .services import get_fluxo_caixa


class FinanceiroServicesTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='financeiro@teste.com', password='123')
        self.cliente = Cliente.objects.create(
            perfil_usuario=self.user.perfilusuario,
            nome_empresa='Fazenda Financeira',
            cpf_cnpj='987654321000199'
        )

        # Cria categorias para usar nos testes
        self.cat_venda = Categoria.objects.create(
            cliente=self.cliente, nome='Venda de Gado', tipo='RECEITA'
        )
        self.cat_racao = Categoria.objects.create(
            cliente=self.cliente, nome='Compra de Ração', tipo='CUSTO'
        )
        self.cat_vacina = Categoria.objects.create(
            cliente=self.cliente, nome='Vacinas', tipo='CUSTO'
        )

        # Cria transações de exemplo no mês atual
        hoje = date.today()
        Transacao.objects.create(
            cliente=self.cliente, categoria=self.cat_venda, descricao='Venda lote 20 bezerros',
            valor=Decimal('50000.00'), data=hoje - timedelta(days=15)
        )
        Transacao.objects.create(
            cliente=self.cliente, categoria=self.cat_racao, descricao='Compra sal proteinado',
            valor=Decimal('3500.00'), data=hoje - timedelta(days=10)
        )
        Transacao.objects.create(
            cliente=self.cliente, categoria=self.cat_vacina, descricao='Vacina aftosa',
            valor=Decimal('1200.00'), data=hoje - timedelta(days=5)
        )
        # Transação do mês passado (não deve entrar no cálculo)
        Transacao.objects.create(
            cliente=self.cliente, categoria=self.cat_racao, descricao='Compra antiga',
            valor=Decimal('1000.00'), data=hoje - timedelta(days=40)
        )

    def test_get_fluxo_caixa_calcula_corretamente(self):
        """
        Garante que o serviço de fluxo de caixa calcula os totais e o saldo corretamente.
        """
        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)

        fluxo = get_fluxo_caixa(self.cliente, primeiro_dia_mes, hoje)

        self.assertEqual(fluxo['total_receitas'], Decimal('50000.00'))
        self.assertEqual(fluxo['total_custos'], Decimal('4700.00'))  # 3500 + 1200
        self.assertEqual(fluxo['saldo_periodo'], Decimal('45300.00'))  # 50000 - 4700

        # Garante que a transação antiga não foi incluída
        self.assertEqual(len(fluxo['transacoes']), 3)