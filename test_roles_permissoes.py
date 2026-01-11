"""
Test Cases - Sistema de Roles e Permissões
Exemplos práticos de como usar os endpoints de login e permissões
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"


# ============================================
# 1. REGISTRAR NOVO PROPRIETÁRIO
# ============================================

def test_registrar_proprietario():
    """Registra um novo proprietário (acesso total)."""
    print("\n=== REGISTRANDO NOVO PROPRIETÁRIO ===")
    
    response = requests.post(
        f"{BASE_URL}/usuarios/registrar/",
        json={
            "email": "proprietario@agro.com",
            "password": "senha123",
            "password2": "senha123",
            "first_name": "João",
            "last_name": "Silva",
            "telefone": "11999999999"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()


# ============================================
# 2. LOGIN COM PROPRIETÁRIO
# ============================================

def test_login_proprietario():
    """Faz login como proprietário e retorna token + permissões."""
    print("\n=== LOGIN PROPRIETÁRIO ===")
    
    response = requests.post(
        f"{BASE_URL}/usuarios/login/",
        json={
            "email": "proprietario@agro.com",
            "password": "senha123"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print("\n📋 INFORMAÇÕES DO USUÁRIO:")
    print(f"  Email: {data['user']['email']}")
    print(f"  Nome: {data['user']['nome_completo']}")
    print(f"  Tipo: {data['user']['tipo_usuario_display']}")
    
    print("\n🔐 PERMISSÕES:")
    for perm, valor in data['user']['permissoes'].items():
        icon = "✅" if valor else "❌"
        print(f"  {icon} {perm}: {valor}")
    
    print(f"\n🔑 TOKENS:")
    print(f"  Access Token (primeiros 50 chars): {data['access'][:50]}...")
    print(f"  Refresh Token (primeiros 50 chars): {data['refresh'][:50]}...")
    
    return data


# ============================================
# 3. CRIAR FUNCIONÁRIO (APENAS PROPRIETÁRIOS)
# ============================================

def test_criar_funcionario(access_token):
    """Proprietário cria um funcionário (acesso limitado)."""
    print("\n=== CRIANDO FUNCIONÁRIO ===")
    
    response = requests.post(
        f"{BASE_URL}/usuarios/registrar_funcionario/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "email": "funcionario@agro.com",
            "first_name": "Maria",
            "last_name": "Santos",
            "telefone": "11988888888",
            "password": "senha123",
            "password2": "senha123",
            "setor": "producao",
            "cargo": "Assistente de Produção"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Funcionário criado!")
        print(f"  Email: {data['user']['email']}")
        print(f"  Tipo: {data['user']['tipo_usuario_display']}")
        print(f"  Cargo: Assistente de Produção")
        print(f"  Setor: Produção")
    else:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))


# ============================================
# 4. LOGIN COM FUNCIONÁRIO
# ============================================

def test_login_funcionario():
    """Faz login como funcionário e mostra permissões limitadas."""
    print("\n=== LOGIN FUNCIONÁRIO ===")
    
    response = requests.post(
        f"{BASE_URL}/usuarios/login/",
        json={
            "email": "funcionario@agro.com",
            "password": "senha123"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print("\n📋 INFORMAÇÕES DO USUÁRIO:")
    print(f"  Email: {data['user']['email']}")
    print(f"  Nome: {data['user']['nome_completo']}")
    print(f"  Tipo: {data['user']['tipo_usuario_display']}")
    
    print("\n🔐 PERMISSÕES (Limitadas):")
    permissoes_criticas = [
        'can_view_animais',
        'can_edit_animais',
        'can_view_financeiro',
        'can_edit_financeiro',
        'can_manage_lotes',
        'can_manage_usuarios'
    ]
    
    for perm in permissoes_criticas:
        valor = data['user']['permissoes'].get(perm, False)
        icon = "✅" if valor else "❌"
        print(f"  {icon} {perm}: {valor}")
    
    return data


# ============================================
# 5. CRIAR GERENTE
# ============================================

def test_criar_gerente(access_token):
    """Proprietário cria um gerente (acesso parcial)."""
    print("\n=== CRIANDO GERENTE ===")
    
    # Para gerente, precisaríamos de um endpoint separado
    # ou usar tipo_usuario diferente
    # Por enquanto, vamos simular com um funcionário
    response = requests.post(
        f"{BASE_URL}/usuarios/registrar_funcionario/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "email": "gerente@agro.com",
            "first_name": "Pedro",
            "last_name": "Oliveira",
            "telefone": "11987654321",
            "password": "senha123",
            "password2": "senha123",
            "setor": "administrativo",
            "cargo": "Gerente de Operações"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Gerente criado!")
        print(f"  Email: {data['user']['email']}")


# ============================================
# 6. TESTE DE PERMISSÃO - VISUALIZAR ANIMAIS
# ============================================

def test_visualizar_animais(access_token, tipo_usuario="funcionario"):
    """Testa se o usuário pode visualizar animais."""
    print(f"\n=== TESTANDO: Visualizar Animais ({tipo_usuario}) ===")
    
    response = requests.get(
        f"{BASE_URL}/cadastros/animais/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Acesso permitido para visualizar animais")
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            print(f"  Total de animais: {data['count']}")
        else:
            print(f"  Animais encontrados: {len(data)}")
    elif response.status_code == 403:
        print(f"❌ Acesso negado para visualizar animais")
        print(f"  Mensagem: {response.json()}")
    else:
        print(f"⚠️ Status inesperado: {response.status_code}")


# ============================================
# 7. TESTE DE PERMISSÃO - EDITAR ANIMAIS
# ============================================

def test_editar_animal(access_token, animal_id=1, tipo_usuario="funcionario"):
    """Testa se o usuário pode editar um animal."""
    print(f"\n=== TESTANDO: Editar Animal ({tipo_usuario}) ===")
    
    response = requests.put(
        f"{BASE_URL}/cadastros/animais/{animal_id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"peso": 500}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Acesso permitido para editar animais")
    elif response.status_code == 403:
        print(f"❌ Acesso negado para editar animais")
        print(f"  Mensagem: {response.json().get('detail', response.json())}")
    else:
        print(f"⚠️ Status: {response.status_code}")
        print(f"  Resposta: {response.json()}")


# ============================================
# 8. TESTE DE PERMISSÃO - ACESSAR FINANCEIRO
# ============================================

def test_acessar_financeiro(access_token, tipo_usuario="funcionario"):
    """Testa se o usuário pode acessar financeiro."""
    print(f"\n=== TESTANDO: Acessar Financeiro ({tipo_usuario}) ===")
    
    response = requests.get(
        f"{BASE_URL}/financeiro/transacoes/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Acesso permitido para ver financeiro")
    elif response.status_code == 403:
        print(f"❌ Acesso negado para ver financeiro")
        print(f"  Mensagem: {response.json().get('detail', response.json())}")
    else:
        print(f"⚠️ Status: {response.status_code}")


# ============================================
# 9. OBTER INFORMAÇÕES DO USUÁRIO LOGADO
# ============================================

def test_me_endpoint(access_token):
    """Retorna informações do usuário logado com todas as permissões."""
    print(f"\n=== ENDPOINT: /api/usuarios/me/ ===")
    
    response = requests.get(
        f"{BASE_URL}/usuarios/me/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Erro: {response.json()}")


# ============================================
# 10. TESTE COMPLETO - FLUXO NORMAL
# ============================================

def test_fluxo_completo():
    """Executa todo o fluxo de teste."""
    print("=" * 60)
    print("TESTE COMPLETO - SISTEMA DE ROLES E PERMISSÕES")
    print("=" * 60)
    
    # 1. Registrar proprietário
    print("\n[1/7] Registrando proprietário...")
    proprietario = test_registrar_proprietario()
    
    # 2. Login como proprietário
    print("\n[2/7] Fazendo login como proprietário...")
    login_prop = test_login_proprietario()
    access_token_prop = login_prop['access']
    
    # 3. Criar funcionário
    print("\n[3/7] Criando funcionário...")
    test_criar_funcionario(access_token_prop)
    
    # 4. Login como funcionário
    print("\n[4/7] Fazendo login como funcionário...")
    login_func = test_login_funcionario()
    access_token_func = login_func['access']
    
    # 5. Testar permissões - Funcionário vê animais
    print("\n[5/7] Testando permissões do funcionário...")
    test_visualizar_animais(access_token_func, "funcionario")
    test_editar_animal(access_token_func, 1, "funcionario")
    test_acessar_financeiro(access_token_func, "funcionario")
    
    # 6. Testar /me endpoint
    print("\n[6/7] Testando endpoint /me...")
    test_me_endpoint(access_token_func)
    
    # 7. Testar permissões - Proprietário pode editar
    print("\n[7/7] Testando permissões do proprietário...")
    test_editar_animal(access_token_prop, 1, "proprietario")
    
    print("\n" + "=" * 60)
    print("TESTE COMPLETO FINALIZADO")
    print("=" * 60)


# ============================================
# EXECUTAR TESTES
# ============================================

if __name__ == "__main__":
    """
    Para executar este arquivo:
    
    1. Certifique-se de que o servidor Django está rodando:
       python manage.py runserver
    
    2. Execute o teste:
       python test_roles_permissoes.py
    
    Ou execute testes específicos:
       python -c "from test_roles_permissoes import test_login_proprietario; test_login_proprietario()"
    """
    
    # Executar fluxo completo
    test_fluxo_completo()
    
    # Ou executar testes individuais:
    # test_registrar_proprietario()
    # login_data = test_login_proprietario()
    # test_criar_funcionario(login_data['access'])
