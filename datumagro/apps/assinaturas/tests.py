# datumagro/apps/assinaturas/tests.py

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from datumagro.apps.usuarios.models import Usuario  # Dependência do app usuarios
from datumagro.apps.cadastros.models import Cliente  # Dependência do app cadastros
from .models import Plano, Assinatura
from .services import (
    criar_ou_atualizar_assinatura,
    cancelar_assinatura,
    verificar_e_atualizar_status_assinaturas,
)


class AssinaturaServicesTest(TestCase):

    def setUp(self):
        """
        Configura o ambiente inicial para cada teste.
        Cria um usuário, um cliente e dois planos.
        """
        # Cria um usuário base para os testes
        self.user = Usuario.objects.create_user(
            email='cliente@teste.com',
            password='123'
        )
        # Cria um cliente associado ao usuário
        self.cliente = Cliente.objects.create(
            nome_empresa='Fazenda Teste SA',
            cpf_cnpj='12345678000190',
            email_contato='teste@fazenda.com'
        )
        # Cria os planos que serão usados nos testes
        self.plano_digital = Plano.objects.create(
            nome='Digital',
            valor_base_mensal=99.90,
            limite_animais=200
        )
        self.plano_elite = Plano.objects.create(
            nome='Elite',
            valor_base_mensal=499.90,
            limite_animais=5000,
            hardware_incluso=True,
            suporte_especialista=True
        )

    def test_criar_nova_assinatura_com_sucesso(self):
        """
        Garante que uma nova assinatura é criada corretamente para um cliente.
        """
        self.assertEqual(Assinatura.objects.count(), 0)

        assinatura = criar_ou_atualizar_assinatura(self.cliente, self.plano_digital)

        self.assertEqual(Assinatura.objects.count(), 1)
        self.assertEqual(assinatura.cliente, self.cliente)
        self.assertEqual(assinatura.plano, self.plano_digital)
        self.assertEqual(assinatura.status, 'ATIVA')
        self.assertTrue(assinatura.is_ativa)
        self.assertAlmostEqual(
            assinatura.data_vencimento,
            assinatura.data_inicio + timedelta(days=30),
            delta=timedelta(seconds=1)
        )

    def test_atualizar_assinatura_existente_para_novo_plano(self):
        """
        Testa a atualização (upgrade/downgrade) de um plano para um cliente
        que já possui uma assinatura.
        """
        # Cria uma assinatura inicial
        criar_ou_atualizar_assinatura(self.cliente, self.plano_digital)
        self.assertEqual(self.cliente.assinatura.plano, self.plano_digital)

        # Atualiza para o plano Elite
        assinatura_atualizada = criar_ou_atualizar_assinatura(self.cliente, self.plano_elite)

        self.assertEqual(Assinatura.objects.count(), 1)  # Não deve criar uma nova
        self.assertEqual(assinatura_atualizada.plano, self.plano_elite)
        self.assertEqual(assinatura_atualizada.status, 'ATIVA')

    def test_cancelar_assinatura_ativa(self):
        """
        Garante que o serviço de cancelamento funciona corretamente.
        """
        assinatura = criar_ou_atualizar_assinatura(self.cliente, self.plano_digital)
        self.assertTrue(assinatura.is_ativa)

        assinatura_cancelada = cancelar_assinatura(self.cliente)

        self.assertEqual(assinatura_cancelada.status, 'CANCELADA')
        self.assertIsNotNone(assinatura_cancelada.data_cancelamento)
        self.assertFalse(assinatura_cancelada.is_ativa)

    def test_verificar_e_atualizar_status_de_assinaturas_vencidas(self):
        """
        Testa a rotina que atualiza assinaturas vencidas para INADIMPLENTE.
        """
        # Cria uma assinatura que já deveria ter vencido
        data_passada = timezone.now() - timedelta(days=5)
        assinatura = Assinatura.objects.create(
            cliente=self.cliente,
            plano=self.plano_digital,
            status='ATIVA',
            data_inicio=data_passada - timedelta(days=30),
            data_vencimento=data_passada
        )

        # Roda o serviço
        num_atualizadas = verificar_e_atualizar_status_assinaturas()

        assinatura.refresh_from_db()  # Recarrega os dados do banco

        self.assertEqual(num_atualizadas, 1)
        self.assertEqual(assinatura.status, 'INADIMPLENTE')
        self.assertFalse(assinatura.is_ativa)