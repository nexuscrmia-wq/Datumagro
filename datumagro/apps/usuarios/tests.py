# datumagro/apps/usuarios/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import PerfilUsuario
from .services import criar_novo_cliente_e_usuario
from datumagro.apps.cadastros.models import Cliente

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    def test_criar_usuario_com_sucesso(self):
        user = Usuario.objects.create_user(email='normal@user.com', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(hasattr(user, 'perfilusuario'))
        self.assertIsInstance(user.perfilusuario, PerfilUsuario)

    def test_criar_superusuario_com_sucesso(self):
        admin_user = Usuario.objects.create_superuser(email='super@user.com', password='foo')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_nao_criar_usuario_sem_email(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(email=None, password='foo')


class UsuarioServicesTest(TestCase):
    def test_criar_novo_cliente_e_usuario_com_sucesso(self):
        self.assertEqual(Usuario.objects.count(), 0)
        self.assertEqual(Cliente.objects.count(), 0)

        novo_usuario = criar_novo_cliente_e_usuario(
            email='novocliente@fazenda.com',
            password='senha_segura_123',
            nome_completo='João da Silva',
            nome_empresa='Fazenda Nova Esperança',
            cpf_cnpj='12.345.678/0001-99',
            telefone='+5522987654321'
        )

        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(Cliente.objects.count(), 1)

        cliente_criado = Cliente.objects.first()
        self.assertEqual(novo_usuario.perfilusuario.cliente, cliente_criado)
        self.assertEqual(cliente_criado.nome_empresa, 'Fazenda Nova Esperança')
        self.assertEqual(cliente_criado.perfil_usuario, novo_usuario.perfilusuario)