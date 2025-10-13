# datumagro/apps/inteligencia/tests.py

from django.test import TestCase
from unittest.mock import patch
from datetime import date, timedelta
from .services import gerar_alerta_vacina_bezerro
from .models import Alerta
from datumagro.apps.usuarios.models import Usuario
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal


class InteligenciaServicesTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='ia@teste.com', password='123')
        self.cliente = Cliente.objects.create(
            perfil_usuario=self.user.perfilusuario,
            nome_empresa='Fazenda IA',
            cpf_cnpj='11122233344455'
        )
        self.propriedade = Propriedade.objects.create(
            cliente=self.cliente, nome_propriedade='Sede IA', cidade='Campo Grande', estado='MS'
        )
        # Cria um animal na idade certa para o alerta
        data_nasc_certa = date.today() - timedelta(days=4 * 30)  # 4 meses de idade
        self.bezerro_alvo = Animal.objects.create(
            propriedade=self.propriedade, brinco='IA-BEZERRO-01', sexo='M', data_nascimento=data_nasc_certa
        )
        # Cria um animal muito novo para o alerta
        data_nasc_errada = date.today() - timedelta(days=1 * 30)  # 1 mês de idade
        self.bezerro_novo = Animal.objects.create(
            propriedade=self.propriedade, brinco='IA-BEZERRO-02', sexo='M', data_nascimento=data_nasc_errada
        )

    def test_gerar_alerta_de_vacina_para_animal_correto(self):
        """
        Garante que a IA cria um alerta para o animal na faixa de idade correta.
        """
        self.assertEqual(Alerta.objects.count(), 0)

        num_alertas = gerar_alerta_vacina_bezerro(self.cliente)

        self.assertEqual(num_alertas, 1)
        self.assertEqual(Alerta.objects.count(), 1)

        alerta_gerado = Alerta.objects.first()
        self.assertEqual(alerta_gerado.animal, self.bezerro_alvo)
        self.assertEqual(alerta_gerado.tipo_alerta, 'SANITARIO')

    def test_nao_gerar_alerta_para_animal_fora_da_idade(self):
        """
        Garante que a IA não cria alerta para o animal que está fora da faixa de idade.
        """
        # Deleta o bezerro alvo para isolar o teste
        self.bezerro_alvo.delete()

        self.assertEqual(Alerta.objects.count(), 0)

        num_alertas = gerar_alerta_vacina_bezerro(self.cliente)

        self.assertEqual(num_alertas, 0)
        self.assertEqual(Alerta.objects.count(), 0)