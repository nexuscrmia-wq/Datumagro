from django.test import TestCase
from django.core.exceptions import ValidationError
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal
from datumagro.apps.assinaturas.models import Plano, Assinatura
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class AnimalLimitTests(TestCase):
    def setUp(self):
        # Criar cliente, plano com limite de 1 animal
        self.cliente = Cliente.objects.create(nome_empresa='Fazenda Y', cpf_cnpj='98765432100', email_contato='owner2@example.com')
        plano = Plano.objects.create(nome='Conectado', descricao='Teste', valor_base_mensal=0, limite_animais=1, max_funcionarios=5)
        Assinatura.objects.create(cliente=self.cliente, plano=plano, data_vencimento=None)

        # Criar propriedade
        self.propriedade = Propriedade.objects.create(cliente=self.cliente, nome_propriedade='Sede Y')

    def test_animal_save_blocks_when_limit_reached(self):
        a1 = Animal.objects.create(propriedade=self.propriedade, brinco='A1', raca='NELORE', sexo='M', data_nascimento='2020-01-01')
        a2 = Animal(propriedade=self.propriedade, brinco='A2', raca='NELORE', sexo='F', data_nascimento='2021-01-01')
        with self.assertRaises(ValidationError):
            a2.full_clean()
        