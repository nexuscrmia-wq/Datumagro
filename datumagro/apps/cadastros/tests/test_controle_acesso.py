"""
Teste unitário para validar o sistema de 2 camadas de controle de acesso.

Este teste prova que:
1. Proprietário vê TODAS as propriedades do cliente
2. Funcionário vê APENAS suas propriedades designadas
3. Gerente vê TODAS as propriedades do cliente
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from datumagro.apps.cadastros.models import (
    Cliente, Propriedade, Animal
)
from datumagro.apps.cadastros.views import AnimalViewSet, PropriedadeViewSet
from datumagro.apps.usuarios.models import Usuario, TipoUsuario


class ControleAcessoDuasCamadasTest(TestCase):
    """Testa o sistema de 2 camadas de controle de acesso"""

    def setUp(self):
        """Prepara dados de teste"""
        # 1. Criar cliente
        self.cliente = Cliente.objects.create(
            nome_empresa="Fazenda Teste",
            cpf_cnpj="12345678000190",
            email_contato="fazenda@test.com"
        )

        # 2. Criar 2 propriedades no mesmo cliente
        self.propriedade1 = Propriedade.objects.create(
            nome_propriedade="Propriedade 1",
            cliente=self.cliente,
            estado="SP",
            objetivo_producao="CORTE"
        )

        self.propriedade2 = Propriedade.objects.create(
            nome_propriedade="Propriedade 2",
            cliente=self.cliente,
            estado="MG",
            objetivo_producao="LEITE"
        )

        # 3. Criar usuários
        self.proprietario = Usuario.objects.create_user(
            email="proprietario@test.com",
            password="senha123",
            tipo_usuario=TipoUsuario.PROPRIETARIO
        )

        self.gerente = Usuario.objects.create_user(
            email="gerente@test.com",
            password="senha123",
            tipo_usuario=TipoUsuario.GERENTE
        )

        self.funcionario = Usuario.objects.create_user(
            email="funcionario@test.com",
            password="senha123",
            tipo_usuario=TipoUsuario.FUNCIONARIO
        )

        # 3.1. Associar usuários ao cliente
        self.proprietario.cliente = self.cliente
        self.proprietario.save()
        
        self.gerente.cliente = self.cliente
        self.gerente.save()
        
        self.funcionario.cliente = self.cliente
        self.funcionario.save()

        # 4. Atribuir apenas propriedade1 ao funcionário
        self.funcionario.propriedades.add(self.propriedade1)

        # 5. Criar animais em ambas as propriedades
        from datetime import date
        self.animal_prop1 = Animal.objects.create(
            brinco="001",
            raca="ANGUS",
            sexo="M",
            data_nascimento=date(2023, 1, 15),
            categoria="GARROTE",
            propriedade=self.propriedade1
        )

        self.animal_prop2 = Animal.objects.create(
            brinco="002",
            raca="NELORE",
            sexo="F",
            data_nascimento=date(2022, 6, 20),
            categoria="NOVILHA",
            propriedade=self.propriedade2
        )

        # 6. Setup factory para requisições
        self.factory = APIRequestFactory()
        self.view = AnimalViewSet.as_view({'get': 'list'})

    def test_proprietario_ve_todos_animais(self):
        """
        🟢 TESTE 1: Proprietário vê TODOS os animais de TODAS as propriedades
        """
        # Criar request como proprietário
        request = self.factory.get('/api/cadastros/animais/')
        request.user = self.proprietario

        # Executar view
        response = self.view(request)

        # Verificar: deve ver 2 animais (de ambas as propriedades)
        assert response.status_code == 200, f"Status: {response.status_code}"
        # Response é paginada: {'count': X, 'next': ..., 'previous': ..., 'results': [...]}
        results = response.data.get('results', [])
        assert len(results) == 2, f"Esperado 2 animais, viu {len(results)}"
        print("✅ Proprietário vê todos os animais: 2/2 ✓")

    def test_funcionario_ve_apenas_suas_propriedades(self):
        """
        🟢 TESTE 2: Funcionário vê APENAS os animais de suas propriedades designadas
        """
        # Criar request como funcionário
        request = self.factory.get('/api/cadastros/animais/')
        request.user = self.funcionario

        # Executar view
        response = self.view(request)

        # Verificar: deve ver apenas 1 animal (da propriedade1)
        assert response.status_code == 200, f"Status: {response.status_code}"
        results = response.data.get('results', [])
        assert len(results) == 1, f"Esperado 1 animal, viu {len(results)}"
        
        # Verificar que é o animal correto (brinco 001)
        animal_id = results[0]['id']
        assert animal_id == self.animal_prop1.id, f"Esperado animal {self.animal_prop1.id}, viu {animal_id}"
        print("✅ Funcionário vê apenas seus animais: 1/1 ✓")

    def test_gerente_ve_todos_animais(self):
        """
        🟢 TESTE 3: Gerente vê TODOS os animais (como proprietário)
        """
        # Criar request como gerente
        request = self.factory.get('/api/cadastros/animais/')
        request.user = self.gerente

        # Executar view
        response = self.view(request)

        # Verificar: deve ver 2 animais (de ambas as propriedades)
        assert response.status_code == 200, f"Status: {response.status_code}"
        results = response.data.get('results', [])
        assert len(results) == 2, f"Esperado 2 animais, viu {len(results)}"
        print("✅ Gerente vê todos os animais: 2/2 ✓")

    def test_funcionario_sem_propriedades_ve_nada(self):
        """
        🟢 TESTE 4: Funcionário sem propriedades designadas vê nada
        """
        # Criar novo funcionário SEM propriedades designadas
        funcionario_vazio = Usuario.objects.create_user(
            email="funcionario_vazio@test.com",
            password="senha123",
            tipo_usuario=TipoUsuario.FUNCIONARIO
        )
        funcionario_vazio.cliente = self.cliente
        funcionario_vazio.save()

        # Criar request
        request = self.factory.get('/api/cadastros/animais/')
        request.user = funcionario_vazio

        # Executar view
        response = self.view(request)

        # Verificar: deve ver 0 animais
        assert response.status_code == 200, f"Status: {response.status_code}"
        results = response.data.get('results', [])
        assert len(results) == 0, f"Esperado 0 animais, viu {len(results)}"
        print("✅ Funcionário sem propriedades vê nada: 0/0 ✓")

    def test_propriedade_filtragem(self):
        """
        🟢 TESTE 5: ViewSet de Propriedades também filtra corretamente
        """
        view_prop = PropriedadeViewSet.as_view({'get': 'list'})

        # Teste com proprietário
        request = self.factory.get('/api/cadastros/propriedades/')
        request.user = self.proprietario
        response = view_prop(request)
        results_prop = response.data.get('results', [])
        assert len(results_prop) == 2, f"Proprietário deve ver 2 propriedades, viu {len(results_prop)}"

        # Teste com funcionário (pode ver apenas 1)
        request = self.factory.get('/api/cadastros/propriedades/')
        request.user = self.funcionario
        response = view_prop(request)
        results_func = response.data.get('results', [])
        assert len(results_func) == 1, f"Funcionário deve ver 1 propriedade, viu {len(results_func)}"
        print("✅ Propriedades também filtram corretamente ✓")


# ============================================================================
# RODANDO OS TESTES
# ============================================================================

if __name__ == "__main__":
    """
    Para rodar estes testes:
    
    1. Via pytest:
       pytest datumagro/apps/cadastros/tests/test_controle_acesso.py -v
    
    2. Via Django test:
       python manage.py test datumagro.apps.cadastros.tests.test_controle_acesso -v 2
    """
    print("✅ Arquivo de testes criado e pronto para executar")
