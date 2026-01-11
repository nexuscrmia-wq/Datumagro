# datumagro/apps/operacional/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

# --- CORREÇÃO PRINCIPAL ESTÁ AQUI ---
# Importa Lote e Piquete da pasta local (.models)
from .models import Lote, Piquete
# Importa Propriedade e Cliente da sua casa correta: 'cadastros'
from datumagro.apps.cadastros.models import Propriedade, Cliente
# --- FIM DA CORREÇÃO ---

from .services import mover_lote_para_piquete

Usuario = get_user_model()


class OperacionalServicesTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='operacional@teste.com', password='123')

        self.cliente = Cliente.objects.create(
            nome_empresa='Fazenda Operacional',
            cpf_cnpj='11.222.333/0001-44',
            email_contato='operacional@teste.com'
        )

        self.user.perfilusuario.cliente = self.cliente
        self.user.perfilusuario.save()

        # Agora o teste consegue encontrar a classe Propriedade para criar o objeto
        self.propriedade = Propriedade.objects.create(cliente=self.cliente, nome_propriedade='Sede Operacional')
        self.lote = Lote.objects.create(propriedade=self.propriedade, nome='Lote de Engorda 01')

        self.piquete_a = Piquete.objects.create(
            propriedade=self.propriedade, nome='Piquete A', tipo_capim='PIATA', status='EM_USO', lote_atual=self.lote
        )
        self.piquete_b = Piquete.objects.create(
            propriedade=self.propriedade, nome='Piquete B', tipo_capim='PIATA', status='PRONTO'
        )
        self.piquete_c = Piquete.objects.create(
            propriedade=self.propriedade, nome='Piquete C', tipo_capim='PIATA', status='DESCANSANDO'
        )

    def test_mover_lote_para_piquete_atualiza_status_corretamente(self):
        self.assertEqual(self.piquete_a.lote_atual, self.lote)

        mover_lote_para_piquete(self.lote, self.piquete_b)

        self.piquete_a.refresh_from_db()
        self.piquete_b.refresh_from_db()
        self.lote.refresh_from_db()

        self.assertEqual(self.piquete_b.lote_atual, self.lote)
        self.assertEqual(self.piquete_a.status, 'DESCANSANDO')
        self.assertEqual(self.piquete_b.status, 'EM_USO')
        self.assertIsNone(self.piquete_a.lote_atual)