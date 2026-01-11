#!/usr/bin/env python
"""
Script simples para popular o banco de dados
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datumagro.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("\n🌱 CRIANDO BANCO DE DADOS COM DADOS DE TESTE\n")

# Criar usuários
users_data = [
    ('admin@datumagro.com', 'Admin123!', 'admin', 'Administrador'),
    ('proprietario@datumagro.com', 'Prop123!', 'proprietario', 'João Silva'),
    ('veterinario@datumagro.com', 'Vet123!', 'veterinario', 'Dr. Carlos'),
    ('demo@example.com', 'Testpass123!', 'proprietario', 'Demo User'),
]

print("👥 Criando usuários:\n")
for email, password, tipo, name in users_data:
    try:
        user = User.objects.create_user(
            email=email,
            password=password,
            tipo_usuario=tipo,
            first_name=name,
            is_active=True
        )
        print(f"  ✅ {email} ({tipo})")
    except Exception as e:
        if 'already exists' in str(e):
            print(f"  ℹ️  {email} já existe")
        else:
            print(f"  ❌ Erro: {e}")

print("\n" + "="*70)
print("✅ BANCO DE DADOS CRIADO COM SUCESSO!")
print("="*70)
print("""
🔐 Credenciais para teste:

   1. Admin:
      Email: admin@datumagro.com
      Senha: Admin123!

   2. Proprietário:
      Email: proprietario@datumagro.com
      Senha: Prop123!

   3. Veterinário:
      Email: veterinario@datumagro.com
      Senha: Vet123!

   4. Demo (para Flutter):
      Email: demo@example.com
      Senha: Testpass123!

🌐 Endpoints de teste:

   POST /api/token/
      {"email": "demo@example.com", "password": "Testpass123!"}
      
   Resposta:
      {
        "access": "<token_jwt>",
        "refresh": "<refresh_token>"
      }

📱 Acesse no Flutter:
   - Base URL: http://10.0.2.2:8000/api
   - Login: demo@example.com / Testpass123!

""")
