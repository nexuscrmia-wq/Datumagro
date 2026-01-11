#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de teste
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datumagro.settings')
django.setup()

from django.contrib.auth import get_user_model
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal, RegistroPesagem
from datumagro.apps.operacional.models import Lote, Piquete, ManejoSanitario
from datumagro.apps.financeiro.models import CategoriaFinanceira, FluxoCaixa

User = get_user_model()

print("\n" + "="*70)
print("🌱 POPULANDO BANCO DE DADOS COM DADOS DE TESTE")
print("="*70 + "\n")

# ========================================
# 1. Criar usuários
# ========================================
print("👥 Criando usuários...")

users_data = [
    {
        'email': 'admin@datumagro.com',
        'password': 'Admin123!',
        'tipo_usuario': 'admin',
        'first_name': 'Administrador',
    },
    {
        'email': 'proprietario@datumagro.com',
        'password': 'Prop123!',
        'tipo_usuario': 'proprietario',
        'first_name': 'João Silva',
    },
    {
        'email': 'veterinario@datumagro.com',
        'password': 'Vet123!',
        'tipo_usuario': 'veterinario',
        'first_name': 'Dr. Carlos',
    },
    {
        'email': 'demo@example.com',
        'password': 'Testpass123!',
        'tipo_usuario': 'proprietario',
        'first_name': 'Demo User',
    }
]

users = {}
for user_data in users_data:
    email = user_data.pop('email')
    password = user_data.pop('password')
    try:
        user = User.objects.create_user(email=email, password=password, **user_data)
        users[email] = user
        print(f"  ✅ Usuário criado: {email}")
    except Exception as e:
        try:
            user = User.objects.get(email=email)
            users[email] = user
            print(f"  ℹ️  Usuário já existe: {email}")
        except:
            print(f"  ❌ Erro ao criar usuário {email}: {e}")

# ========================================
# 2. Criar clientes
# ========================================
print("\n🏢 Criando clientes...")

clients_data = [
    {
        'nome_empresa': 'Fazenda Santa Clara',
        'cpf_cnpj': '12345678000190',
        'email_contato': 'contato@fazenda-clara.com',
        'telefone': '(11) 99999-0001',
    },
    {
        'nome_empresa': 'Pecuária Silva',
        'cpf_cnpj': '98765432000180',
        'email_contato': 'contato@pecuaria-silva.com',
        'telefone': '(11) 99999-0002',
    },
    {
        'nome_empresa': 'Gado Premium',
        'cpf_cnpj': '11111111000160',
        'email_contato': 'contato@gado-premium.com',
        'telefone': '(11) 99999-0003',
    }
]

clients = {}
for client_data in clients_data:
    try:
        client = Cliente.objects.create(**client_data)
        clients[client_data['nome_empresa']] = client
        print(f"  ✅ Cliente criado: {client_data['nome_empresa']}")
    except Exception as e:
        print(f"  ❌ Erro ao criar cliente: {e}")

# ========================================
# 3. Criar propriedades
# ========================================
print("\n🌾 Criando propriedades...")

if clients:
    first_client = list(clients.values())[0]
    properties_data = [
        {
            'cliente': first_client,
            'nome': 'Propriedade Principal',
            'endereco': 'Rod. BR-116, km 50',
            'municipio': 'Sorocaba',
            'estado': 'SP',
        },
        {
            'cliente': first_client,
            'nome': 'Propriedade Secundária',
            'endereco': 'Rod. BR-116, km 60',
            'municipio': 'Itu',
            'estado': 'SP',
        }
    ]

    properties = {}
    for prop_data in properties_data:
        try:
            prop = Propriedade.objects.create(**prop_data)
            properties[prop_data['nome']] = prop
            print(f"  ✅ Propriedade criada: {prop_data['nome']}")
        except Exception as e:
            print(f"  ❌ Erro ao criar propriedade: {e}")

    # ========================================
    # 4. Criar piquetes
    # ========================================
    print("\n📍 Criando piquetes...")

    if properties:
        first_property = list(properties.values())[0]
        piquetes_data = [
            {'propriedade': first_property, 'nome': 'Piquete A', 'area_hectares': 5.0, 'status': 'DISPONIVEL'},
            {'propriedade': first_property, 'nome': 'Piquete B', 'area_hectares': 4.5, 'status': 'DISPONIVEL'},
            {'propriedade': first_property, 'nome': 'Piquete C', 'area_hectares': 6.0, 'status': 'EM_USO'},
        ]

        piquetes = {}
        for piquete_data in piquetes_data:
            try:
                piquete = Piquete.objects.create(**piquete_data)
                piquetes[piquete_data['nome']] = piquete
                print(f"  ✅ Piquete criado: {piquete_data['nome']}")
            except Exception as e:
                print(f"  ❌ Erro ao criar piquete: {e}")

    # ========================================
    # 5. Criar lotes
    # ========================================
    print("\n🐄 Criando lotes...")

    if properties:
        first_property = list(properties.values())[0]
        lotes_data = [
            {
                'propriedade': first_property,
                'nome': 'Lote 001',
                'quantidade_animais': 20,
                'raca_predominante': 'Nelore',
                'data_criacao': datetime.now(),
            },
            {
                'propriedade': first_property,
                'nome': 'Lote 002',
                'quantidade_animais': 15,
                'raca_predominante': 'Angus',
                'data_criacao': datetime.now() - timedelta(days=30),
            }
        ]

        lotes = {}
        for lote_data in lotes_data:
            try:
                lote = Lote.objects.create(**lote_data)
                lotes[lote_data['nome']] = lote
                print(f"  ✅ Lote criado: {lote_data['nome']}")
            except Exception as e:
                print(f"  ❌ Erro ao criar lote: {e}")

    # ========================================
    # 6. Criar animais
    # ========================================
    print("\n🐮 Criando animais...")

    if lotes:
        first_lote = list(lotes.values())[0]
        animals_data = [
            {
                'lote': first_lote,
                'brinco': 'NE-001',
                'data_nasc': datetime.now() - timedelta(days=365),
                'sexo': 'M',
                'raca': 'Nelore',
                'peso_kg': 450.0,
            },
            {
                'lote': first_lote,
                'brinco': 'NE-002',
                'data_nasc': datetime.now() - timedelta(days=300),
                'sexo': 'F',
                'raca': 'Nelore',
                'peso_kg': 380.0,
            },
            {
                'lote': first_lote,
                'brinco': 'NE-003',
                'data_nasc': datetime.now() - timedelta(days=200),
                'sexo': 'M',
                'raca': 'Nelore',
                'peso_kg': 350.0,
            }
        ]

        animals = []
        for animal_data in animals_data:
            try:
                animal = Animal.objects.create(**animal_data)
                animals.append(animal)
                print(f"  ✅ Animal criado: {animal_data['brinco']} ({animal_data['raca']})")
            except Exception as e:
                print(f"  ❌ Erro ao criar animal: {e}")

# ========================================
# 7. Criar categorias financeiras
# ========================================
print("\n💰 Criando categorias financeiras...")

categorias_data = [
    {'nome': 'Alimentação', 'tipo': 'DESPESA'},
    {'nome': 'Veterinário', 'tipo': 'DESPESA'},
    {'nome': 'Venda de Gado', 'tipo': 'RECEITA'},
    {'nome': 'Leite', 'tipo': 'RECEITA'},
    {'nome': 'Transporte', 'tipo': 'DESPESA'},
]

categorias = []
for cat_data in categorias_data:
    try:
        cat = CategoriaFinanceira.objects.create(**cat_data)
        categorias.append(cat)
        print(f"  ✅ Categoria criada: {cat_data['nome']} ({cat_data['tipo']})")
    except Exception as e:
        print(f"  ❌ Erro ao criar categoria: {e}")

print("\n" + "="*70)
print("✅ BANCO DE DADOS POPULADO COM SUCESSO!")
print("="*70)
print(f"""
📊 Dados criados:
   - {len(users)} usuários
   - {len(clients)} clientes
   - {len(properties)} propriedades
   - {len(piquetes)} piquetes
   - {len(lotes)} lotes
   - {len(animals)} animais
   - {len(categorias)} categorias financeiras

🔐 Credenciais para teste:
   
   Admin:
     Email: admin@datumagro.com
     Senha: Admin123!

   Proprietário:
     Email: proprietario@datumagro.com
     Senha: Prop123!

   Demo:
     Email: demo@example.com
     Senha: Testpass123!

📱 Para Flutter, use:
   Email: demo@example.com
   Senha: Testpass123!

""")
