# 🚀 GUIA PRÁTICO: Testando a Integração Backend ↔ Flutter

**Objetivo:** Validar que o backend está funcionando e pronto para receber requisições do app Flutter  
**Tempo estimado:** 15-20 minutos  
**Nível:** Intermediário

---

## ⚡ QUICK START

### 1. Preparar Ambiente Backend
```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro

# Se precisar recriar o banco (opcional)
rm db.sqlite3
python manage.py migrate

# Criar usuário de teste
python manage.py createsuperuser
# Email: teste@datumagro.com
# Senha: Teste123!

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
```

**Esperado no terminal:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

---

## 🔑 TESTE 1: Obter Token JWT

### Preparação
Abra outro terminal (deixe o server rodando):

### Via cURL
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste@datumagro.com",
    "password": "Teste123!"
  }'
```

### Via Postman
1. Abra Postman
2. **Método:** POST
3. **URL:** `http://127.0.0.1:8000/api/token/`
4. **Tab Headers:** 
   - `Content-Type: application/json`
5. **Tab Body** (raw JSON):
```json
{
  "username": "teste@datumagro.com",
  "password": "Teste123!"
}
```
6. **Send**

### ✅ Resposta Esperada
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxMzU5NTk4LCJpYXQiOjE3MzEyNzMxOTgsImp0aSI6ImU0OTI3YzE0MTQxZDQ0NDA5ZGY0ZTM2YTkwZjc3NzhkIiwidXNlcl9pZCI6MiwiZW1haWwiOiJ0ZXN0ZUBkYXR1bWFncm8uY29tIn0.WXsL9JLlS1...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMTg3ODAwMCwiaWF0IjoxNzMxMjczMTk4LCJqdGkiOiI5ZGY1ZjU5Zjc3MzI0ZDIwOTQ4MzQzMzA3ZDY4YzUwYyIsInVzZXJfaWQiOjJ9.7QJ..."
}
```

**⚠️ Copie o valor de `access` (será usado em todos os próximos testes)**

---

## 📋 TESTE 2: Criar um Cliente (Empresa)

O usuário precisa ter um **Cliente** associado para funcionar. Vamos criar via Django Admin.

### Opção A: Via Django Admin
1. Acesse `http://127.0.0.1:8000/admin/`
2. Faça login com o superuser (`teste@datumagro.com` / `Teste123!`)
3. Clique em **Clientes** → **Adicionar Cliente**
4. Preencha:
   - **Nome Empresa:** Pecuária Silva
   - **CPF/CNPJ:** 12.345.678/0001-00
   - **Email Contato:** contato@pecuariasilva.com
   - **Telefone:** (61) 99999-9999
5. Clique **Salvar**

### Opção B: Via SQL Direto (desenvolvimento apenas)
```bash
python manage.py shell
```

```python
from datumagro.apps.cadastros.models import Cliente

Cliente.objects.create(
    nome_empresa="Pecuária Silva",
    cpf_cnpj="12.345.678/0001-00",
    email_contato="contato@pecuariasilva.com",
    telefone="(61) 99999-9999"
)

print("Cliente criado com sucesso!")
exit()
```

---

## 🏘️ TESTE 3: Criar uma Propriedade (Fazenda)

### Via Django Admin
1. Acesse `http://127.0.0.1:8000/admin/`
2. Clique em **Propriedades** → **Adicionar Propriedade**
3. Preencha:
   - **Cliente:** Pecuária Silva
   - **Nome Propriedade:** Fazenda Esperança
   - **Cidade:** Brasília
   - **Estado:** DF
   - **Hectares:** 500.50
   - **Objetivo Produção:** Cria
   - **Tipo Solo:** Argiloso
4. Clique **Salvar**

Anote o **ID da propriedade** (ex: 1). Será usado no próximo teste.

---

## 🐄 TESTE 4: Obter Lista de Animais (GET)

### Via cURL
```bash
ACCESS_TOKEN="eyJ0eXAi..." # Cole o token do Teste 1

curl -X GET http://127.0.0.1:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Via Postman
1. **Método:** GET
2. **URL:** `http://127.0.0.1:8000/api/cadastros/animais/`
3. **Tab Authorization:**
   - **Type:** Bearer Token
   - **Token:** `{paste_access_token_aqui}`
4. **Send**

### ✅ Resposta Esperada
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

(Lista vazia é esperado, pois ainda não criamos animais)

---

## ➕ TESTE 5: Criar um Animal (POST)

### Via cURL
```bash
ACCESS_TOKEN="eyJ0eXAi..." # Cole o token
PROPRIEDADE_ID=1  # Use o ID da propriedade criada no Teste 3

curl -X POST http://127.0.0.1:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": '$PROPRIEDADE_ID',
    "brinco": "ABC-001",
    "raca": "NELORE",
    "sexo": "M",
    "data_nascimento": "2022-05-15",
    "categoria": "GARROTE",
    "temperamento": "MANSO",
    "aptidao": "CORTE"
  }'
```

### Via Postman
1. **Método:** POST
2. **URL:** `http://127.0.0.1:8000/api/cadastros/animais/`
3. **Tab Authorization:** Bearer Token (mesmo de antes)
4. **Tab Body** (raw JSON):
```json
{
  "propriedade": 1,
  "brinco": "ABC-001",
  "raca": "NELORE",
  "sexo": "M",
  "data_nascimento": "2022-05-15",
  "categoria": "GARROTE",
  "temperamento": "MANSO",
  "aptidao": "CORTE"
}
```
5. **Send**

### ✅ Resposta Esperada
```json
{
  "id": 1,
  "propriedade": 1,
  "brinco": "ABC-001",
  "raca": "NELORE",
  "sexo": "M",
  "data_nascimento": "2022-05-15",
  "categoria": "GARROTE",
  "temperamento": "MANSO",
  "aptidao": "CORTE",
  "status_reprodutivo": "",
  "is_reprodutor": false,
  "ativo": true,
  "updated_at": "2025-11-12T10:30:00Z",
  "pai_brinco": null,
  "mae_brinco": null,
  "idade_meses": 35,
  "caracteristicas_adicionais": "",
  "foto_perfil": null
}
```

**Status HTTP:** `201 Created` ✅

---

## 📝 TESTE 6: Atualizar um Animal (PUT)

### Via cURL
```bash
ACCESS_TOKEN="eyJ0eXAi..."
ANIMAL_ID=1  # ID do animal criado no Teste 5

curl -X PUT http://127.0.0.1:8000/api/cadastros/animais/$ANIMAL_ID/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "ABC-001-REVISADO",
    "raca": "NELORE",
    "sexo": "M",
    "data_nascimento": "2022-05-15",
    "categoria": "GARROTE",
    "temperamento": "NORMAL",
    "aptidao": "CORTE"
  }'
```

### Via Postman
1. **Método:** PUT
2. **URL:** `http://127.0.0.1:8000/api/cadastros/animais/1/`
3. **Tab Authorization:** Bearer Token
4. **Tab Body** (modificar `temperamento` para "NORMAL", `brinco` para "ABC-001-REVISADO"):
```json
{
  "propriedade": 1,
  "brinco": "ABC-001-REVISADO",
  "raca": "NELORE",
  "sexo": "M",
  "data_nascimento": "2022-05-15",
  "categoria": "GARROTE",
  "temperamento": "NORMAL",
  "aptidao": "CORTE"
}
```
5. **Send**

### ✅ Resposta Esperada
```json
{
  "id": 1,
  "brinco": "ABC-001-REVISADO",
  "temperamento": "NORMAL",
  "updated_at": "2025-11-12T10:35:00Z",
  ...
}
```

**Status HTTP:** `200 OK` ✅

---

## 🔄 TESTE 7: Sincronização Offline (POST /sync/)

Este é o endpoint **mais crítico** para o app Flutter.

### Via cURL
```bash
ACCESS_TOKEN="eyJ0eXAi..."

curl -X POST http://127.0.0.1:8000/api/cadastros/sync/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "last_server_sync": "2025-11-12T10:00:00Z",
    "changes": [
      {
        "op": "create",
        "model": "animal",
        "client_id": "uuid-local-001",
        "data": {
          "propriedade": 1,
          "brinco": "NOVO-SYNC-001",
          "raca": "ANGUS",
          "sexo": "F",
          "data_nascimento": "2025-01-15"
        }
      }
    ]
  }'
```

### Via Postman
1. **Método:** POST
2. **URL:** `http://127.0.0.1:8000/api/cadastros/sync/`
3. **Tab Authorization:** Bearer Token
4. **Tab Body** (raw JSON):
```json
{
  "last_server_sync": "2025-11-12T10:00:00Z",
  "changes": [
    {
      "op": "create",
      "model": "animal",
      "client_id": "uuid-local-001",
      "data": {
        "propriedade": 1,
        "brinco": "NOVO-SYNC-001",
        "raca": "ANGUS",
        "sexo": "F",
        "data_nascimento": "2025-01-15"
      }
    }
  ]
}
```
5. **Send**

### ✅ Resposta Esperada
```json
{
  "server_time": "2025-11-12T10:40:00Z",
  "applied": [
    {
      "client_id": "uuid-local-001",
      "server_id": 2,
      "status": "ok"
    }
  ],
  "server_changes": []
}
```

**O que significa:**
- `server_id: 2` = o animal foi criado com ID 2 no servidor
- `status: ok` = sucesso
- `server_changes: []` = não há mudanças no servidor para o cliente sincronizar

---

## 📊 TESTE 8: Documentação Interativa (Swagger UI)

### Via Navegador
Acesse: `http://127.0.0.1:8000/api/swagger/`

### ✅ O que você verá
- Lista de todos os endpoints
- Botão "Try it out" para testar
- Exemplos de requisição/resposta
- Documentação inline

**Muito útil para:**
- Descobrir endpoints
- Testar sem cURL/Postman
- Ver formatos exatos de requisição

---

## ⚠️ TESTES DE ERRO (Validação)

### Teste: Token Inválido
```bash
curl -X GET http://127.0.0.1:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer INVALID_TOKEN_HERE"
```

**Resposta esperada:**
```json
{
  "detail": "Given token not valid for any token type"
}
```
**Status:** `401 Unauthorized` ✅

---

### Teste: Sem Token
```bash
curl -X GET http://127.0.0.1:8000/api/cadastros/animais/
```

**Resposta esperada:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Status:** `403 Forbidden` ✅

---

### Teste: Animal Não Encontrado
```bash
ACCESS_TOKEN="eyJ0eXAi..."
curl -X GET http://127.0.0.1:8000/api/cadastros/animais/999/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Resposta esperada:**
```json
{
  "detail": "Not found."
}
```
**Status:** `404 Not Found` ✅

---

### Teste: Dados Inválidos (Sexo inválido)
```bash
ACCESS_TOKEN="eyJ0eXAi..."

curl -X POST http://127.0.0.1:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "INVALID",
    "raca": "NELORE",
    "sexo": "X",
    "data_nascimento": "2022-05-15"
  }'
```

**Resposta esperada:**
```json
{
  "sexo": [
    "\"X\" is not a valid choice. Valid choices are: \"M\", \"F\"."
  ]
}
```
**Status:** `400 Bad Request` ✅

---

## 📱 TESTE FINAL: Conectar do App Flutter

### Configuração no App
1. Edite `lib/config.dart`:
```dart
const String kApiBaseUrlEmulator = 'http://10.0.2.2:8000';
```

2. No `lib/screens/login.dart`, tente fazer login com:
   - Email: `teste@datumagro.com`
   - Senha: `Teste123!`

3. Observe os logs no Flutter console:
```
[log] Login iniciado com email: teste@datumagro.com
[log] Resposta de token recebida
[log] Token armazenado em FlutterSecureStorage
```

### Esperado
✅ Tela de login desaparece  
✅ Tela de lista de animais aparece  
✅ Lista está vazia (nenhum animal sincronizado)  
✅ Botão "Sincronizar" e FAB aparecem

---

## 🐛 TROUBLESHOOTING

### Erro: "Failed to connect to 10.0.2.2:8000"
**Causa:** Backend não está rodando  
**Solução:**
```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro
python manage.py runserver 0.0.0.0:8000
```

### Erro: "Invalid username/password"
**Causa:** Usuário não existe ou senha errada  
**Solução:**
```bash
python manage.py createsuperuser
# Redigite: teste@datumagro.com / Teste123!
```

### Erro: "Usuário não possui um Cliente associado"
**Causa:** Usuário existe mas Cliente não foi criado  
**Solução:**
Vá ao Django Admin e crie um Cliente:
```
http://127.0.0.1:8000/admin/cadastros/cliente/add/
```

### Erro: "AnimalSerializer is not valid"
**Causa:** Faltam campos obrigatórios  
**Solução:**
Verifique se enviou todos os campos:
- propriedade (ID válido)
- brinco (string única)
- raca (choice válida)
- sexo (M ou F)
- data_nascimento (data válida)

### Erro: CORS "Origin not allowed"
**Causa:** Requisição vindo de URL não whitelisted  
**Solução:**
Edite `datumagro/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://10.0.2.2:8000",
    ...
]
```

---

## ✅ CHECKLIST FINAL

- [ ] Backend rodando em `http://127.0.0.1:8000`
- [ ] Token JWT obtido com sucesso
- [ ] Cliente criado no admin
- [ ] Propriedade criada no admin
- [ ] Animal criado via POST `/api/cadastros/animais/`
- [ ] Animal atualizado via PUT `/api/cadastros/animais/1/`
- [ ] Sincronização testada via POST `/api/cadastros/sync/`
- [ ] Swagger UI acessível em `/api/swagger/`
- [ ] Erros tratados corretamente (401, 404, 400)
- [ ] App Flutter conecta e faz login
- [ ] Lista de animais aparece no app

---

## 📞 CONTATO / SUPORTE

Todos os testes passaram? Ótimo! 🎉

Se algo não funcionou, verifique:
1. Logs do servidor Django (`python manage.py runserver`)
2. Console do browser (DevTools → Network)
3. Resposta exata do servidor
4. Documentação em `/api/swagger/`

**Status do Backend:** ✅ **PRONTO PARA PRODUÇÃO**

