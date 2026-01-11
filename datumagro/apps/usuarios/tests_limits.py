from django.test import TestCase
from types import SimpleNamespace
from django.contrib.auth import get_user_model
from datumagro.apps.cadastros.models import Cliente, Propriedade
from datumagro.apps.assinaturas.models import Plano, Assinatura
from datumagro.apps.usuarios.serializers import FuncionarioRegistroSerializer

Usuario = get_user_model()


class FuncionarioLimitTests(TestCase):
    def setUp(self):
        # Criar proprietário / cliente / plano
        self.owner = Usuario.objects.create_user(email='owner@example.com', password='pass')
        # Perfil criado automaticamente pelo sinal/fluxo do projeto (assegure)
        cliente = Cliente.objects.create(nome_empresa='Fazenda X', cpf_cnpj='12345678901', email_contato='owner@example.com')
        # Criar plano com limite de 1 funcionario
        plano = Plano.objects.create(nome='Digital', descricao='Teste', valor_base_mensal=0, limite_animais=10, max_funcionarios=1)
        assinatura = Assinatura.objects.create(cliente=cliente, plano=plano, data_vencimento=None)
        # Associar cliente ao perfil do owner
        try:
            self.owner.perfilusuario.cliente = cliente
            self.owner.perfilusuario.save()
        except Exception:
            pass

        # Criar propriedade e vincular ao owner
        self.propriedade = Propriedade.objects.create(cliente=cliente, nome_propriedade='Sede')
        self.owner.propriedades.add(self.propriedade)

        # Criar um funcionário já existente para atingir o limite
        self.existing = Usuario.objects.create_user(email='func1@example.com', password='pass', tipo_usuario='funcionario')
        self.existing.propriedades.add(self.propriedade)

    def test_serializer_blocks_when_limit_reached(self):
        data = {
            'email': 'novo_func@example.com',
            'first_name': 'Novo',
            'last_name': 'Funcionario',
            'telefone': '99999999',
            'password': 'Senha12345!',
            'password2': 'Senha12345!',
        }
        fake_request = SimpleNamespace(user=self.owner)
        serializer = FuncionarioRegistroSerializer(data=data, context={'request': fake_request})
        self.assertFalse(serializer.is_valid())
        # Deve conter mensagem de limite
        errors = serializer.errors
        self.assertTrue(any('limite' in str(v).lower() or 'limite' in k.lower() for k, v in errors.items()))