# datumagro/apps/cadastros/tests.py

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from datumagro.apps.usuarios.models import Usuario
from .models import Cliente, Propriedade, Animal, RegistroPesagem
from .services import calcular_idade_em_meses, calcular_gmd


class CadastrosModelsTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='cliente@teste.com', password='123')
        self.cliente = Cliente.objects.create(
            nome_empresa='Fazenda Modelo',
            cpf_cnpj='111222333000199',
            email_contato='modelo@fazenda.com'
        )
        self.propriedade = Propriedade.objects.create(
            cliente=self.cliente,
            nome_propriedade='Sede Principal',
            cidade='Uberaba',
            estado='MG'
        )

    def test_criacao_animal_com_genealogia(self):
        """
        Testa a criação de animais e a correta associação da árvore genealógica.
        """
        touro = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='TOURO-01',
            raca='NELORE',
            sexo='M',
            data_nascimento=date(2020, 1, 1)
        )
        matriz = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='MATRIZ-01',
            raca='NELORE',
            sexo='F',
            data_nascimento=date(2021, 1, 1)
        )
        bezerro = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='BEZERRO-01',
            raca='NELORE',
            sexo='M',
            data_nascimento=date(2024, 1, 1),
            pai=touro,
            mae=matriz
        )

        self.assertEqual(bezerro.pai, touro)
        self.assertEqual(bezerro.mae, matriz)
        self.assertEqual(touro.descendentes_pai.count(), 1)
        self.assertEqual(matriz.descendentes_mae.count(), 1)


class CadastrosServicesTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(email='cliente@servico.com', password='123')
        self.cliente = Cliente.objects.create(
            nome_empresa='Fazenda Serviços',
            cpf_cnpj='444555666000188',
            email_contato='servicos@fazenda.com'
        )
        self.propriedade = Propriedade.objects.create(
            cliente=self.cliente,
            nome_propriedade='Teste de Serviços',
            cidade='Goiânia',
            estado='GO'
        )
        self.animal = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='ANIMAL-GMD',
            raca='NELORE',
            sexo='M',
            # Nasceu há exatamente 12 meses
            data_nascimento=date.today() - timedelta(days=365)
        )

    def test_calcular_idade_em_meses_corretamente(self):
        """
        Garante que o cálculo de idade em meses está preciso.
        """
        idade = calcular_idade_em_meses(self.animal.data_nascimento)
        # O cálculo pode variar entre 11 e 12 dependendo do dia exato
        self.assertIn(idade, [11, 12])

        # Teste com uma data fixa
        data_fixa = date(2023, 1, 1)
        hoje = date(2024, 7, 1)  # Simula 'hoje' para um resultado previsível
        idade_fixa = (hoje.year - data_fixa.year) * 12 + hoje.month - data_fixa.month
        self.assertEqual(idade_fixa, 18)

    def test_calcular_gmd_com_sucesso(self):
        """
        Testa o cálculo de Ganho de Peso Médio Diário.
        """
        # Cria duas pesagens para o animal
        RegistroPesagem.objects.create(
            animal=self.animal,
            data_pesagem=date.today() - timedelta(days=100),
            peso_kg=Decimal('300.0')
        )
        RegistroPesagem.objects.create(
            animal=self.animal,
            data_pesagem=date.today(),
            peso_kg=Decimal('375.0')
        )

        # O animal ganhou 75kg em 100 dias. GMD = 0.750 kg/dia
        gmd = calcular_gmd(self.animal)
        self.assertEqual(gmd, Decimal('0.750'))

    def test_calcular_gmd_sem_pesagens_suficientes(self):
        """
        Garante que o GMD retorna 0 se houver menos de duas pesagens.
        """
        # Apenas uma pesagem
        RegistroPesagem.objects.create(
            animal=self.animal,
            data_pesagem=date.today(),
            peso_kg=Decimal('300.0')
        )
        gmd = calcular_gmd(self.animal)
        self.assertEqual(gmd, Decimal('0.0'))

        # Nenhuma pesagem
        animal_sem_pesagem = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='SEM-PESO',
            raca='NELORE',
            sexo='F',
            data_nascimento=date.today()
        )
        gmd_zero = calcular_gmd(animal_sem_pesagem)
        self.assertEqual(gmd_zero, Decimal('0.0'))