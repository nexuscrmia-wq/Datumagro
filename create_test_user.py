#!/usr/bin/env python
"""
Script para criar dados de teste para integração completa.
Cria: Usuario -> PerfilUsuario -> Cliente -> Propriedade -> Animal
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datumagro.settings')
django.setup()

from django.contrib.auth import get_user_model
from datumagro.apps.usuarios.models import PerfilUsuario
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal
from datumagro.apps.logistica.models import Embarque, ItemEmbarque

User = get_user_model()

def create_test_data():
    print("Criando dados de teste...")

    # 1. Criar usuário
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'nome_completo': 'Usuário Teste',
            'tipo_usuario': 'proprietario',
            'is_active': True
        }
    )
    if created:
        user.set_password('test123')
        user.save()
        print(f"✓ Usuário criado: {user.email}")
    else:
        print(f"✓ Usuário já existe: {user.email}")

    # 2. Criar perfil do usuário
    perfil, created = PerfilUsuario.objects.get_or_create(
        usuario=user,
        defaults={
            'bio': 'Perfil de teste',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'ativo': True
        }
    )
    if created:
        print("✓ Perfil do usuário criado")
    else:
        print("✓ Perfil do usuário já existe")

    # 3. Criar cliente (sem vínculo direto com perfil)
    cliente, created = Cliente.objects.get_or_create(
        email_contato='test@example.com',
        defaults={
            'nome_empresa': 'Empresa Teste Ltda',
            'cpf_cnpj': '12345678000199',
            'telefone': '11999999999'
        }
    )
    if created:
        print(f"✓ Cliente criado: {cliente.nome_empresa}")
    else:
        print(f"✓ Cliente já existe: {cliente.nome_empresa}")

    # 4. Criar propriedade vinculada ao cliente
    propriedade, created = Propriedade.objects.get_or_create(
        cliente=cliente,
        nome_propriedade='Fazenda Teste',
        defaults={
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234567',
            'hectares': 100.0,
            'objetivo_producao': 'CRIA',
            'tipo_solo': 'ARGILOSO',
            'topografia': 'PLANO'
        }
    )
    if created:
        print(f"✓ Propriedade criada: {propriedade.nome_propriedade}")
    else:
        print(f"✓ Propriedade já existe: {propriedade.nome_propriedade}")

    # 5. Vincular usuário à propriedade
    if not user.propriedades.filter(id=propriedade.id).exists():
        user.propriedades.add(propriedade)
        print("✓ Usuário vinculado à propriedade")
    else:
        print("✓ Usuário já vinculado à propriedade")

    # 6. Criar animal de teste
    animal, created = Animal.objects.get_or_create(
        propriedade=propriedade,
        brinco='TEST001',
        defaults={
            'raca': 'NELORE',
            'sexo': 'M',
            'categoria': 'TOURO',
            'data_nascimento': '2020-01-01',
            'is_reprodutor': True,
            'ativo': True
        }
    )
    if created:
        print(f"✓ Animal criado: {animal.brinco}")
    else:
        print(f"✓ Animal já existe: {animal.brinco}")

    # 7. Criar embarque de teste
    embarque, created = Embarque.objects.get_or_create(
        numero_embarque='EMB001',
        defaults={
            'tipo': 'EXP',
            'status': 'PLA',
            'porto_origem': 'Porto do Açu',
            'porto_destino': 'Rotterdam',
            'pais_parceiro': 'Países Baixos',
            'data_prevista_embarque': '2024-01-15',
            'data_prevista_chegada': '2024-02-15',
            'responsavel': cliente,
            'valor_frete': 5000.00,
            'valor_seguro': 1000.00,
            'valor_total': 6000.00
        }
    )
    if created:
        print(f"✓ Embarque criado: {embarque.numero_embarque}")
    else:
        print(f"✓ Embarque já existe: {embarque.numero_embarque}")

    # 8. Criar item do embarque
    item, created = ItemEmbarque.objects.get_or_create(
        embarque=embarque,
        animal=animal,
        defaults={
            'peso_total_kg': 480.0,
            'valor_unitario': 15.50,
            'quantidade': 1
        }
    )
    if created:
        print("✓ Item do embarque criado")
    else:
        print("✓ Item do embarque já existe")

    print("\n✅ Dados de teste criados com sucesso!")
    print(f"Usuário: {user.email} / Senha: test123")
    print(f"Cliente: {cliente.nome_empresa}")
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Animal: {animal.brinco}")

if __name__ == '__main__':
    create_test_data()