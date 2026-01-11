# 🚀 REFERÊNCIA RÁPIDA - API DE LOGÍSTICA

## 📝 ENDPOINTS PRINCIPAIS

### 🏗️ EMBARQUES

```bash
# LISTAR COM FILTROS
curl -X GET "http://localhost:8000/api/logistica/embarques/?status=NAV&tipo=EXP" \
  -H "Authorization: Bearer YOUR_TOKEN"

# CRIAR EMBARQUE
curl -X POST "http://localhost:8000/api/logistica/embarques/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "EXP",
    "porto_destino": "Shanghai",
    "pais_parceiro": "China",
    "navio": "MV Atlantic Star",
    "data_prevista_embarque": "2024-12-15",
    "data_prevista_chegada": "2025-02-15",
    "responsavel": 1,
    "agente_carga": "TransGlobal",
    "valor_frete": 50000.00,
    "valor_seguro": 5000.00
  }'

# OBTER DETALHES
curl -X GET "http://localhost:8000/api/logistica/embarques/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# ADICIONAR ITEM
curl -X POST "http://localhost:8000/api/logistica/embarques/1/adicionar_item/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_produto": "VIVO",
    "animal": 123,
    "peso_total_kg": 600,
    "valor_unitario": 1500.00
  }'

# ATUALIZAR STATUS
curl -X POST "http://localhost:8000/api/logistica/embarques/1/atualizar_status/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "NAV",
    "descricao": "Navio saiu do porto",
    "localizacao": "Atlântico Norte"
  }'

# RESUMO ESTATÍSTICO
curl -X GET "http://localhost:8000/api/logistica/embarques/resumo/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 📦 ITENS DE EMBARQUE

```bash
# LISTAR ITENS
curl -X GET "http://localhost:8000/api/logistica/itens-embarque/?embarque=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# CRIAR ITEM
curl -X POST "http://localhost:8000/api/logistica/itens-embarque/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "embarque": 1,
    "tipo_produto": "CARNE",
    "descricao_produto": "Carcaça Nelore",
    "quantidade": 50,
    "peso_total_kg": 15000,
    "categoria_carne": "Prime Cut",
    "certificacao": "Halal",
    "valor_unitario": 300.00
  }'
```

### 📍 RASTREAMENTO

```bash
# LISTAR HISTÓRICO
curl -X GET "http://localhost:8000/api/logistica/rastreamento/?embarque=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔐 AUTENTICAÇÃO

1. **Obter Token:**
```bash
curl -X POST "http://localhost:8000/api/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu@email.com",
    "password": "sua_senha"
  }'
```

2. **Usar Token nos Headers:**
```bash
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 FILTROS DISPONÍVEIS

### Embarques:
- `tipo` → EXP, IMP
- `status` → PLA, PRE, NAV, POR, FIN, CAN
- `porto_destino` → nome do porto
- `pais_parceiro` → país
- `responsavel` → ID do cliente
- `search` → busca em numero_embarque, navio, viagem, bl_numero

### Itens:
- `embarque` → ID do embarque
- `tipo_produto` → VIVO, CARNE, CORTES, SUB
- `animal` → ID do animal

### Rastreamento:
- `embarque` → ID do embarque

---

## 📱 RESPOSTAS ESPERADAS

### Listar Embarques (200 OK):
```json
{
  "count": 30,
  "next": "http://localhost:8000/api/logistica/embarques/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero_embarque": "EMP-2024-0001",
      "tipo": "EXP",
      "status": "NAV",
      "porto_origem": "Porto do Açu",
      "porto_destino": "Shanghai",
      "pais_parceiro": "China",
      "navio": "MV Atlantic Star",
      "viagem": "2024-001",
      "data_prevista_embarque": "2024-12-15",
      "data_prevista_chegada": "2025-02-15",
      "data_real_embarque": "2024-12-16",
      "data_real_chegada": null,
      "responsavel": 1,
      "responsavel_nome": "Fazenda do João",
      "agente_carga": "TransGlobal Logistics",
      "bl_numero": "BL123456789",
      "conhecimento_carga": "CNTR123456",
      "valor_frete": 50000.00,
      "valor_seguro": 5000.00,
      "valor_total": 55000.00,
      "total_peso": 450000,
      "total_itens": 750,
      "total_animais_vivos": 750,
      "valor_total_carga": 1125000.00,
      "itens": [
        {
          "id": 1,
          "tipo_produto": "VIVO",
          "animal": 123,
          "animal_details": { "brinco": "001", ... },
          "descricao_produto": null,
          "quantidade": 750,
          "peso_total_kg": 450000,
          "categoria_carne": null,
          "certificacao": null,
          "gta_numero": "GTA-2024-001",
          "valor_unitario": 1500.00,
          "valor_total": 1125000.00
        }
      ],
      "rastreamento": [
        {
          "id": 1,
          "embarque": 1,
          "status_anterior": "PLA",
          "status_novo": "PRE",
          "descricao": "Animais em quarentena",
          "localizacao": "Quarentena Porto do Açu",
          "data_evento": "2024-12-10T10:30:00Z",
          "arquivo": null
        },
        {
          "id": 2,
          "embarque": 1,
          "status_anterior": "PRE",
          "status_novo": "NAV",
          "descricao": "Navio saiu do porto",
          "localizacao": "Atlântico Norte",
          "data_evento": "2024-12-16T14:00:00Z",
          "arquivo": null
        }
      ],
      "created_at": "2024-12-08T09:00:00Z",
      "updated_at": "2024-12-16T14:00:00Z"
    }
  ]
}
```

### Resumo Estatístico (GET embarques/resumo/):
```json
{
  "total_embarques": 150,
  "embarques_planejados": 45,
  "embarques_em_transito": 30,
  "embarques_finalizados": 75,
  "total_peso_kg": 450000,
  "total_animais_vivos": 2500,
  "proximos_embarques": 20
}
```

---

## ⚠️ CÓDIGOS DE ERRO

| Código | Significado | Solução |
|--------|-------------|---------|
| 400 | Bad Request | Verifique os dados enviados |
| 401 | Unauthorized | Verifique o token JWT |
| 403 | Forbidden | Você não tem permissão |
| 404 | Not Found | Recurso não encontrado |
| 500 | Server Error | Contate o suporte |

---

## 🧪 TESTAR COM POSTMAN

1. **Variáveis de Ambiente:**
```
BASE_URL = http://localhost:8000
TOKEN = seu_jwt_token
```

2. **Import Collection:**
Usar o arquivo `datumagro_postman_collection.json` do projeto

3. **Executar Testes:**
```bash
# Ter o servidor rodando
python manage.py runserver

# Em outro terminal, executar a collection
newman run datumagro_postman_collection.json
```

---

## 💡 DICAS

- Sempre use `?page=1` para paginação
- Use `?page_size=50` para mudar itens por página
- Combine filtros: `?status=NAV&tipo=EXP&page=1`
- Use `search=` para busca textual
- Use `ordering=campo` ou `ordering=-campo` para ordenar

---

Última atualização: 13 de novembro de 2025
