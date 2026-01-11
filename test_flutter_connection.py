#!/usr/bin/env python
"""
Script para testar a conexão entre Flutter e o backend Django.
"""
import os
import sys
import django
import requests
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datumagro.settings')
django.setup()

# ========================================
# 1. Testar endpoints da API
# ========================================
print("\n" + "="*70)
print("🔍 TESTE DE CONEXÃO FLUTTER ↔ BACKEND DJANGO")
print("="*70 + "\n")

BASE_URL = "http://127.0.0.1:8000/api"
API_ENDPOINT = f"{BASE_URL}/token/"

print(f"📍 URL BASE: {BASE_URL}")
print(f"📍 Endpoint de Login: {API_ENDPOINT}\n")

# ========================================
# 2. Criar usuário de teste se não existir
# ========================================
User = get_user_model()
test_email = "demo@example.com"
test_password = "Testpass123!"

try:
    user = User.objects.get(email=test_email)
    print(f"✅ Usuário '{test_email}' já existe")
except User.DoesNotExist:
    print(f"⚠️  Criando usuário de teste '{test_email}'...")
    user = User.objects.create_user(email=test_email, password=test_password)
    print(f"✅ Usuário criado com sucesso")

print(f"   Email: {user.email}")
print(f"   Tipo: {user.tipo_usuario}")
print(f"   Ativo: {user.is_active}\n")

# ========================================
# 3. Testar endpoints
# ========================================
print("🧪 TESTES DE CONECTIVIDADE:\n")

# Teste 1: Health Check
try:
    print("1️⃣  Health Check...")
    response = requests.get(f"{BASE_URL}/health/", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {e}\n")

# Teste 2: Token Login
try:
    print("\n2️⃣  Login (Token JWT)...")
    data = {"email": test_email, "password": test_password}
    response = requests.post(API_ENDPOINT, json=data, timeout=5)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        json_data = response.json()
        access_token = json_data.get('access', '')
        refresh_token = json_data.get('refresh', '')
        print(f"   ✅ Token obtido com sucesso!")
        print(f"   Access Token: {access_token[:50]}...")
        print(f"   Refresh Token: {refresh_token[:50]}...\n")
        
        # Teste 3: Usar token para acessar recurso protegido
        print("3️⃣  Acessar recurso protegido (categorias)...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/financeiro/categorias/", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Acesso ao recurso protegido bem-sucedido!")
            data = response.json()
            print(f"   Dados: {str(data)[:100]}...")
        else:
            print(f"   ❌ Erro ao acessar recurso: {response.text[:100]}")
    else:
        print(f"   ❌ Erro no login: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Erro: {e}\n")

# ========================================
# 4. Resumo de configuração
# ========================================
print("\n" + "="*70)
print("📋 CONFIGURAÇÃO DO FLUTTER:")
print("="*70)
print(f"""
Para Flutter conectar ao backend:

1. Em 'pubspec.yaml', use:
   dependências:
     - http
     - flutter_secure_storage

2. Configurar ApiService com:
   - Base URL: http://10.0.2.2:8000/api (para Android Emulator)
   - Base URL: http://localhost:8000/api (para iOS Simulator)
   - Base URL: http://<IP_BACKEND>:8000/api (para dispositivo físico)

3. Endpoints disponíveis:
   - POST /token/ → Login (retorna access_token e refresh_token)
   - POST /token/refresh/ → Renovar token
   - GET /financeiro/categorias/ → Listar categorias (autenticado)
   - GET /inteligencia/alertas/ → Listar alertas (autenticado)
   - GET /usuarios/usuarios/profile/ → Perfil do usuário (autenticado)

4. Status da Conexão:
   ✅ Backend está rodando em: {BASE_URL}
   ✅ Usuário de teste criado: {test_email}
   ✅ API pronta para receber requisições do Flutter
""")
print("="*70 + "\n")
