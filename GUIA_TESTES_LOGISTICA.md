# 🧪 GUIA DE TESTES PRÁTICOS - API DE LOGÍSTICA

## 📋 PRÉ-REQUISITOS

- Python 3.12+ com virtualenv ativado
- Django 5.0+
- SQLite3
- Postman ou cURL

---

## 🚀 INICIAR O SERVIDOR

```bash
# Navegar para o projeto
cd /home/victor-emanuel/PycharmProjects/DatumAgro

# Ativar o ambiente virtual (se necessário)
source .venv/bin/activate

# Executar o servidor
python manage.py runserver 0.0.0.0:8000
```

Você verá:
```
Watching for file changes with StatReloader
Starting development server at http://0.0.0.0:8000/
```

---

## 🔐 STEP 1: AUTENTICAÇÃO

### 1.1 Criar um usuário (Admin)

```bash
python manage.py createsuperuser
# Email: seu@email.com
# Password: senha123
```

### 1.2 Obter Token JWT

```bash
curl -X POST "http://localhost:8000/api/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu@email.com",
    "password": "senha123"
  }'
```

**Resposta esperada:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

✅ **Salve o token `access` para usar nos próximos testes!**

```bash
export TOKEN="seu_token_aqui"
```

---

## 👤 STEP 2: CRIAR CLIENTE E PROPRIEDADE

### 2.1 Criar Cliente (via Admin)

```bash
# Acesse http://localhost:8000/admin/
# Login com seu usuário admin
# Navegue até: Cadastros > Clientes > Adicionar Cliente
```

Ou use a API:

```bash
curl -X POST "http://localhost:8000/api/usuarios/clientes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_empresa": "Fazenda do João",
    "email_contato": "contato@fazendajoao.com",
    "telefone": "(85) 99999-9999",
    "endereco": "Rodovia BR-116, km 50",
    "cidade": "Fortaleza",
    "estado": "CE",
    "cnpj": "00000000000191"
  }'
```

✅ **Anote o ID do cliente retornado (ex: 1)**

### 2.2 Criar Propriedade

```bash
curl -X POST "http://localhost:8000/api/cadastros/propriedades/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "nome_propriedade": "Fazenda Central",
    "endereco": "Rodovia BR-116, km 50",
    "cidade": "Fortaleza",
    "estado": "CE",
    "hectares": 1000,
    "objetivo_producao": "CRIA",
    "tipo_solo": "ARGILOSO"
  }'
```

✅ **Anote o ID da propriedade (ex: 1)**

---

## 🐄 STEP 3: CRIAR ANIMAIS

```bash
curl -X POST "http://localhost:8000/api/cadastros/animais/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "001",
    "raca": "NELORE",
    "sexo": "M",
    "data_nascimento": "2020-05-15",
    "categoria": "TOURO",
    "temperamento": "MANSO",
    "aptidao": "CORTE",
    "is_reprodutor": true
  }'
```

Crie mais 2-3 animais para o teste:

```bash
# Animal 2
curl -X POST "http://localhost:8000/api/cadastros/animais/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "002",
    "raca": "ANGUS",
    "sexo": "F",
    "data_nascimento": "2021-03-20",
    "categoria": "MATRIZ",
    "temperamento": "MANSO",
    "aptidao": "CORTE",
    "status_reprodutivo": "VAZIA"
  }'

# Animal 3
curl -X POST "http://localhost:8000/api/cadastros/animais/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propriedade": 1,
    "brinco": "003",
    "raca": "BRAHMAN",
    "sexo": "M",
    "data_nascimento": "2022-07-10",
    "categoria": "GARROTE",
    "temperamento": "NORMAL",
    "aptidao": "CORTE"
  }'
```

✅ **Anote os IDs dos animais (ex: 1, 2, 3)**

---

## 📦 STEP 4: CRIAR EMBARQUES

### 4.1 Listar Embarques Vazio

```bash
curl -X GET "http://localhost:8000/api/logistica/embarques/" \
  -H "Authorization: Bearer $TOKEN"
```

**Esperado:** Array vazio `{"count": 0, "results": []}`

### 4.2 Criar Primeiro Embarque (Exportação)

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "EXP",
    "porto_destino": "Shanghai",
    "pais_parceiro": "China",
    "navio": "MV Atlantic Star",
    "viagem": "2024-001",
    "data_prevista_embarque": "2024-12-15",
    "data_prevista_chegada": "2025-02-15",
    "responsavel": 1,
    "agente_carga": "TransGlobal Logistics",
    "valor_frete": 50000.00,
    "valor_seguro": 5000.00
  }'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "numero_embarque": "EMP-2024-0001",
  "tipo": "EXP",
  "status": "PLA",
  "total_peso": 0,
  "total_itens": 0,
  "itens": [],
  "rastreamento": []
}
```

✅ **Anote o ID do embarque (ex: 1) e o numero_embarque (EMP-2024-0001)**

### 4.3 Criar Segundo Embarque (Importação)

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "IMP",
    "porto_destino": "Recife",
    "pais_parceiro": "Paraguai",
    "navio": "MV Brasil Express",
    "data_prevista_embarque": "2024-12-20",
    "data_prevista_chegada": "2025-01-05",
    "responsavel": 1,
    "agente_carga": "Logística BR",
    "valor_frete": 35000.00,
    "valor_seguro": 3500.00
  }'
```

---

## 📦 STEP 5: ADICIONAR ITENS AOS EMBARQUES

### 5.1 Adicionar Item Vivo (Animal 1)

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/adicionar_item/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_produto": "VIVO",
    "animal": 1,
    "peso_total_kg": 600,
    "valor_unitario": 1500.00
  }'
```

### 5.2 Adicionar Item de Carne

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/adicionar_item/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_produto": "CARNE",
    "descricao_produto": "Carcaça Nelore Grade Premium",
    "quantidade": 50,
    "peso_total_kg": 15000,
    "categoria_carne": "Prime Cut",
    "certificacao": "Halal",
    "gta_numero": "GTA-2024-001",
    "valor_unitario": 250.00
  }'
```

### 5.3 Adicionar Item de Cortes

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/adicionar_item/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_produto": "CORTES",
    "descricao_produto": "Cortes Traseiros Congelados",
    "quantidade": 100,
    "peso_total_kg": 20000,
    "categoria_carne": "Choice",
    "certificacao": "Kosher",
    "valor_unitario": 150.00
  }'
```

---

## 🔄 STEP 6: ATUALIZAR STATUS DO EMBARQUE

### 6.1 Quarentena

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/atualizar_status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "PRE",
    "descricao": "Animais em quarentena sanitária",
    "localizacao": "Quarentena Porto do Açu"
  }'
```

### 6.2 Em Trânsito

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/atualizar_status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "NAV",
    "descricao": "Navio saiu do porto do Açu",
    "localizacao": "Atlântico Norte, coordenadas 05°S 35°W"
  }'
```

### 6.3 Chegada

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/atualizar_status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "POR",
    "descricao": "Navio chegou no porto de Shanghai",
    "localizacao": "Porto de Shanghai, Terminal 3"
  }'
```

### 6.4 Finalizado

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/atualizar_status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "FIN",
    "descricao": "Desembaraço aduaneiro concluído",
    "localizacao": "Destino final - Cliente em Shanghai"
  }'
```

---

## 📊 STEP 7: CONSULTAR DADOS

### 7.1 Detalhes do Embarque (com histórico)

```bash
curl -X GET "http://localhost:8000/api/logistica/embarques/1/" \
  -H "Authorization: Bearer $TOKEN"
```

**Esperado:** Embarque com:
- ✅ 3 itens
- ✅ Total de peso: 35.600 kg
- ✅ 4 eventos de rastreamento
- ✅ Status: FIN

### 7.2 Listar com Filtros

```bash
# Por tipo
curl -X GET "http://localhost:8000/api/logistica/embarques/?tipo=EXP" \
  -H "Authorization: Bearer $TOKEN"

# Por status
curl -X GET "http://localhost:8000/api/logistica/embarques/?status=FIN" \
  -H "Authorization: Bearer $TOKEN"

# Por destino
curl -X GET "http://localhost:8000/api/logistica/embarques/?porto_destino=Shanghai" \
  -H "Authorization: Bearer $TOKEN"

# Busca por navio
curl -X GET "http://localhost:8000/api/logistica/embarques/?search=MV" \
  -H "Authorization: Bearer $TOKEN"

# Combinado
curl -X GET "http://localhost:8000/api/logistica/embarques/?tipo=EXP&status=NAV&page=1" \
  -H "Authorization: Bearer $TOKEN"
```

### 7.3 Resumo Estatístico

```bash
curl -X GET "http://localhost:8000/api/logistica/embarques/resumo/" \
  -H "Authorization: Bearer $TOKEN"
```

**Esperado:**
```json
{
  "total_embarques": 2,
  "embarques_planejados": 0,
  "embarques_em_transito": 0,
  "embarques_finalizados": 1,
  "total_peso_kg": 35600,
  "total_animais_vivos": 1,
  "proximos_embarques": 1
}
```

### 7.4 Listar Itens

```bash
curl -X GET "http://localhost:8000/api/logistica/itens-embarque/?embarque=1" \
  -H "Authorization: Bearer $TOKEN"
```

### 7.5 Listar Rastreamento

```bash
curl -X GET "http://localhost:8000/api/logistica/rastreamento/?embarque=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 STEP 8: TESTAR VALIDAÇÕES

### 8.1 Datas Inválidas (Deve falhar)

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "EXP",
    "porto_destino": "Los Angeles",
    "pais_parceiro": "USA",
    "data_prevista_embarque": "2025-02-15",
    "data_prevista_chegada": "2025-01-15",
    "responsavel": 1
  }'
```

**Esperado:** Erro 400 - "Data de chegada deve ser após o embarque"

### 8.2 Item sem animal ou descrição (Deve falhar)

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/adicionar_item/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_produto": "VIVO",
    "peso_total_kg": 600,
    "valor_unitario": 1500.00
  }'
```

**Esperado:** Erro 400 - "Informe um animal ou a descrição do produto"

### 8.3 Peso inválido (Deve falhar)

```bash
curl -X POST "http://localhost:8000/api/logistica/embarques/1/adicionar_item/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_produto": "VIVO",
    "animal": 1,
    "peso_total_kg": 0,
    "valor_unitario": 1500.00
  }'
```

**Esperado:** Erro 400 - "Peso deve ser maior que zero"

---

## 🧪 STEP 9: TESTAR PERFORMANCE

### 9.1 Criar múltiplos embarques

```bash
#!/bin/bash
for i in {3..10}; do
  curl -X POST "http://localhost:8000/api/logistica/embarques/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"tipo\": \"EXP\",
      \"porto_destino\": \"Port-$i\",
      \"pais_parceiro\": \"Country-$i\",
      \"navio\": \"Ship-$i\",
      \"data_prevista_embarque\": \"2024-12-25\",
      \"data_prevista_chegada\": \"2025-03-25\",
      \"responsavel\": 1,
      \"valor_frete\": $((40000 + i * 1000))
    }"
  echo "Embarque $i criado"
done
```

### 9.2 Testar paginação

```bash
# Página 1 (20 itens)
curl -X GET "http://localhost:8000/api/logistica/embarques/?page=1" \
  -H "Authorization: Bearer $TOKEN"

# Página customizada
curl -X GET "http://localhost:8000/api/logistica/embarques/?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN"
```

### 9.3 Medir tempo de resposta

```bash
time curl -X GET "http://localhost:8000/api/logistica/embarques/1/" \
  -H "Authorization: Bearer $TOKEN"
```

**Esperado:** < 100ms (com otimizações de query)

---

## 📝 CHECKLIST DE VALIDAÇÃO

- [ ] ✅ Servidor iniciado sem erros
- [ ] ✅ Token JWT obtido com sucesso
- [ ] ✅ Cliente criado
- [ ] ✅ Propriedade criada
- [ ] ✅ 3+ animais criados
- [ ] ✅ Embarque criado (EXP)
- [ ] ✅ Embarque criado (IMP)
- [ ] ✅ 3 itens adicionados
- [ ] ✅ Status atualizado 4x
- [ ] ✅ Detalhes com histórico correto
- [ ] ✅ Filtros funcionando
- [ ] ✅ Resumo estatístico correto
- [ ] ✅ Validações funcionando
- [ ] ✅ Performance < 100ms

---

## 🐛 TROUBLESHOOTING

### Erro: 401 Unauthorized
```
Solução: Verifique o token JWT. Execute o step 1.2 novamente.
```

### Erro: 400 Bad Request (campo obrigatório)
```
Solução: Verifique se todos os campos obrigatórios foram enviados.
Consulte o modelo para campos required=True.
```

### Erro: 404 Not Found
```
Solução: Verifique se o ID do recurso existe.
Use um ID válido dos steps anteriores.
```

### Erro: 500 Internal Server Error
```
Solução: Verifique o console do servidor para mais detalhes.
Pode ser um erro na validação de dados.
```

---

## 📚 Recursos Adicionais

- [Documentação OpenAPI](http://localhost:8000/api/swagger/)
- [ReDoc](http://localhost:8000/api/redoc/)
- [Admin Django](http://localhost:8000/admin/)
- [Postman Collection](./datumagro_postman_collection.json)

---

**Teste concluído com sucesso! 🎉**

Para próximos passos, veja: `IMPLEMENTACAO_LOGISTICA_COMPLETA.md`
