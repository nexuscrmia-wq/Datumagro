# 🧪 GUIA DE TESTES - DatumAgro Backend

> Instruções detalhadas para testar o backend DatumAgro

---

## 📋 Índice

1. [Testes com cURL (Manual)](#testes-com-curl)
2. [Testes com Shell Script](#testes-com-shell-script)
3. [Testes com pytest-django](#testes-com-pytest-django)
4. [Testes de Integração](#testes-de-integração)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 Setup Inicial

### Prerequisitos

```bash
# 1. Backend rodando
cd /home/victor-emanuel/PycharmProjects/DatumAgro
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# 2. Em outro terminal, criar usuário de teste
python manage.py createsuperuser
# Email: test@datumagro.com
# Password: Teste123!

# 3. Acessar admin para criar Cliente e Propriedade
# http://localhost:8000/admin/
```

---

## 🧪 Testes com cURL (Manual)

### 1. Teste de Health Check

```bash
# Verificar se o servidor está respondendo
curl -i http://localhost:8000/api/swagger/

# Resposta esperada: 200 OK
```

### 2. Teste de Login

```bash
# Fazer login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@datumagro.com","password":"Teste123!"}'

# Resposta esperada:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
# }

# Salve o token em uma variável
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 3. Teste de Listagem de Animais (Autenticado)

```bash
# Usar o token obtido acima
curl -X GET http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Resposta esperada:
# {
#   "count": 0,
#   "next": null,
#   "previous": null,
#   "results": []
# }
```

### 4. Teste de Criação de Animal

```bash
# Primeiro, você precisa obter um ID de propriedade válido
# Veja no admin: http://localhost:8000/admin/cadastros/propriedade/

curl -X POST http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "ABC-001",
    "raca": "NELORE",
    "sexo": "F",
    "data_nascimento": "2025-01-15"
  }'

# Resposta esperada: 201 Created
# {
#   "id": 1,
#   "propriedade": 1,
#   "brinco": "ABC-001",
#   "raca": "NELORE",
#   "sexo": "F",
#   "data_nascimento": "2025-01-15",
#   "updated_at": "2025-11-13T10:30:00Z"
# }
```

### 5. Teste de Acesso Não Autenticado

```bash
# Tentar acessar endpoint protegido SEM token
curl -i http://localhost:8000/api/cadastros/animais/

# Resposta esperada: 403 Forbidden
# {
#   "detail": "Authentication credentials were not provided."
# }
```

### 6. Teste de Token Inválido

```bash
# Usar um token falso
curl -i http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer invalid_token_here"

# Resposta esperada: 401 Unauthorized
# {
#   "detail": "Given token not valid for any token type"
# }
```

### 7. Teste de Atualização

```bash
# Atualizar animal (ID 1)
curl -X PUT http://localhost:8000/api/cadastros/animais/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "ABC-001-UPDATED",
    "raca": "ANGUS",
    "sexo": "F",
    "data_nascimento": "2025-01-15"
  }'

# Resposta esperada: 200 OK
```

### 8. Teste de Deleção

```bash
# Deletar animal (ID 1)
curl -X DELETE http://localhost:8000/api/cadastros/animais/1/ \
  -H "Authorization: Bearer $TOKEN"

# Resposta esperada: 204 No Content
```

---

## 🚀 Testes com Shell Script

### Executar Script de Testes

```bash
# Tornar script executável
chmod +x run_tests.sh

# Executar testes (servidor deve estar rodando)
./run_tests.sh

# Ou com variáveis personalizadas
BASE_URL=http://localhost:8000 \
TEST_EMAIL=test@datumagro.com \
TEST_PASSWORD=Teste123! \
./run_tests.sh
```

### Exemplo de Output

```
==============================================
DatumAgro Backend - Practical Tests
==============================================
Base URL: http://localhost:8000
Test Email: test@datumagro.com
==============================================

[TEST] Test 1: Check server health
[PASS] Server is running and responding
[TEST] Test 2: Login with valid credentials
[PASS] Login successful. Token: eyJ0eXAiOiJKV1QiLCJhbGc...
[TEST] Test 3: Login with invalid credentials (should fail)
[PASS] Invalid login correctly rejected (status 401)
[TEST] Test 4: Unauthenticated request (should be rejected)
[PASS] Unauthenticated request correctly rejected (status 403)
[TEST] Test 5: List animals (with authentication)
[PASS] List animals successful. Found 0 animals
[TEST] Test 6: List properties (with authentication)
[PASS] List properties successful. Found 1 properties
[TEST] Test 7: Refresh token
[PASS] Token refreshed successfully
[TEST] Test 8: Check CORS headers
[PASS] CORS headers present

==============================================
TEST SUMMARY
==============================================
Total Tests: 8
Passed: 8
Failed: 0
Success Rate: 100%
==============================================

✅ All tests passed!
```

---

## 🔬 Testes com pytest-django

### Instalação

```bash
# Instalar pytest e pytest-django
pip install pytest pytest-django pytest-cov

# Criar arquivo de configuração (se não existir)
# pytest.ini já deve estar configurado
```

### Executar Testes

```bash
# Todos os testes
pytest -v

# Apenas testes de API
pytest datumagro/apps/usuarios/test_api.py -v

# Com cobertura
pytest --cov=datumagro --cov-report=html

# Testes específicos
pytest datumagro/apps/usuarios/test_api.py::AuthenticationTestCase::test_login_success -v

# Modo verbose com output
pytest -v -s
```

### Exemplo de Test Case

```python
# datumagro/apps/usuarios/test_api.py

class AuthenticationTestCase(APITestCase):
    """Test JWT authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'primeiro_nome': 'Test',
            'ultimo_nome': 'User'
        }
        self.user = Usuario.objects.create_user(**self.user_data)

    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = self.client.post('/api/token/', {
            'username': self.user_data['email'],
            'password': self.user_data['password']
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
```

### Relatório de Cobertura

```bash
# Gerar relatório HTML
pytest --cov=datumagro --cov-report=html

# Abrir relatório
open htmlcov/index.html  # Mac
# ou
xdg-open htmlcov/index.html  # Linux
```

---

## 🔄 Testes de Integração

### 1. Teste Offline-First

```bash
# Simular criação offline
# 1. Desabilitar internet do dispositivo
# 2. Criar animal no app Flutter
# 3. Reabilitar internet
# 4. Sincronizar via POST /api/cadastros/sync/
# 5. Verificar se animal foi criado no servidor

# Via cURL (simulando sync):
curl -X POST http://localhost:8000/api/cadastros/sync/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "changes": [
      {
        "op": "create",
        "model": "animal",
        "data": {
          "propriedade": 1,
          "brinco": "OFFLINE-001",
          "raca": "NELORE",
          "sexo": "M"
        }
      }
    ]
  }'
```

### 2. Teste de Conflito de Sincronização

```bash
# 1. Criar 2 mudanças simultâneas
# 2. Enviar ao servidor
# 3. Verificar resolução de conflitos

curl -X POST http://localhost:8000/api/cadastros/sync/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "changes": [
      {
        "op": "update",
        "model": "animal",
        "client_id": "local-id-1",
        "data": {
          "id": 1,
          "brinco": "ABC-001-UPDATE1"
        }
      },
      {
        "op": "update",
        "model": "animal",
        "client_id": "local-id-2",
        "data": {
          "id": 1,
          "brinco": "ABC-001-UPDATE2"
        }
      }
    ]
  }'
```

### 3. Teste de Performance (100+ animais)

```bash
# Script para criar 100 animais
python manage.py shell << EOF
from datumagro.apps.cadastros.models import Cliente, Propriedade, Animal
from datumagro.apps.usuarios.models import Usuario

# Assumindo que usuário e propriedade existem
user = Usuario.objects.first()
cliente = Cliente.objects.first()
prop = Propriedade.objects.first()

# Criar 100 animais
animals = [
    Animal(
        propriedade=prop,
        brinco=f'PERF-{i:03d}',
        raca='NELORE',
        sexo='F' if i % 2 == 0 else 'M'
    )
    for i in range(1, 101)
]

Animal.objects.bulk_create(animals)
print(f"Criados {len(animals)} animais")
EOF
```

```bash
# Testar tempo de resposta
time curl -X GET http://localhost:8000/api/cadastros/animais/?limit=100 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  | jq '.count'

# Resposta esperada: real 0m0.5s (menos de 1 segundo)
```

---

## 📊 Checklist de Testes

### Antes de Produção

- [ ] **Autenticação**
  - [ ] Login com credenciais válidas
  - [ ] Login com credenciais inválidas (deve falhar)
  - [ ] Token refresh funciona
  - [ ] Acesso protegido sem token (deve falhar)
  - [ ] Acesso protegido com token válido (sucesso)
  - [ ] Acesso com token inválido (deve falhar)

- [ ] **CRUD de Animais**
  - [ ] Listar animais
  - [ ] Criar animal com dados válidos
  - [ ] Criar animal com dados inválidos (deve falhar)
  - [ ] Obter detalhes de um animal
  - [ ] Atualizar animal
  - [ ] Deletar animal

- [ ] **CRUD de Propriedades**
  - [ ] Listar propriedades
  - [ ] Criar propriedade
  - [ ] Atualizar propriedade
  - [ ] Deletar propriedade

- [ ] **Sincronização**
  - [ ] Sincronizar criação
  - [ ] Sincronizar atualização
  - [ ] Sincronizar deleção
  - [ ] Resolução de conflitos

- [ ] **Performance**
  - [ ] Resposta com < 100 animais (< 500ms)
  - [ ] Resposta com 100-500 animais (< 1s)
  - [ ] Resposta com > 500 animais (aceitável < 2s)

- [ ] **Segurança**
  - [ ] CORS funcionando corretamente
  - [ ] HTTPS em produção
  - [ ] Headers de segurança presentes
  - [ ] Dados do usuário isolados por cliente

---

## 🐛 Troubleshooting

### Erro: Cannot connect to server

```bash
# Verificar se servidor está rodando
curl -i http://localhost:8000/

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000

# Verificar logs do servidor
tail -f manage_run.txt
```

### Erro: 403 Forbidden (sem token)

```
# Esperado! Endpoints estão protegidos
# Solução: Adicionar header Authorization

curl -X GET http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $TOKEN"
```

### Erro: 401 Unauthorized (token inválido)

```bash
# Obter novo token
TOKEN=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@datumagro.com","password":"Teste123!"}' \
  | jq -r '.access')

echo "New token: $TOKEN"
```

### Erro: 400 Bad Request (dados inválidos)

```bash
# Verificar campos obrigatórios
# Para Animal: propriedade, brinco, raca, sexo

curl -X POST http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "TEST-001",
    "raca": "NELORE",
    "sexo": "F"
  }'  # Todos os campos obrigatórios presentes
```

### Erro: No matching propriedade found

```bash
# Criar propriedade no admin primeiro
# http://localhost:8000/admin/cadastros/propriedade/

# Ou via API:
curl -X POST http://localhost:8000/api/cadastros/propriedades/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Fazenda de Testes",
    "cidade": "Brasília",
    "estado": "DF"
  }'
```

---

## 📚 Ferramentas Úteis

### Postman

1. Importar `datumagro_postman_collection.json`
2. Configurar environment variable: `{{BASE_URL}}`
3. Executar requests pré-configuradas

### Swagger UI

```
http://localhost:8000/api/swagger/
```

Permite testar endpoints diretamente no navegador.

### jq (JSON Parser)

```bash
# Instalar
brew install jq  # Mac
apt install jq   # Linux

# Extrair campo
curl -s http://api/token/ | jq '.access'

# Pretty print
curl -s http://api/animais/ | jq '.'
```

---

## 📞 Support

- **API Docs:** http://localhost:8000/api/swagger/
- **Django Docs:** https://docs.djangoproject.com/
- **DRF Testing:** https://www.django-rest-framework.org/api-guide/testing/

---

**Última atualização:** 13 de novembro de 2025  
**Status:** ✅ Pronto para Testes
