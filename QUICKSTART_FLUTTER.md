# ⚡ QUICK START - Backend Pronto para Flutter

**Status:** ✅ Validado e Pronto  
**Última Atualização:** 12 de novembro de 2025

---

## 🚀 Iniciar em 3 Passos

### Passo 1: Iniciar Servidor Django
```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Esperado:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Passo 2: Obter Token JWT
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste_backend@datumagro.local",
    "password": "Teste123!"
  }'
```

**Resposta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Copie o valor de `access`** para usar nas requisições

### Passo 3: Testar Endpoint
```bash
TOKEN="seu_access_token_aqui"

curl -X GET http://127.0.0.1:8000/api/cadastros/propriedades/ \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "nome_propriedade": "fazenda datum",
      "cidade": "campos",
      "estado": "rj"
    },
    ...
  ]
}
```

---

## 📱 Para Testar no Android Emulator

### Substituir localhost por IP do emulator:
```bash
# Em vez de 127.0.0.1:8000
# Use: 10.0.2.2:8000

curl -X POST http://10.0.2.2:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste_backend@datumagro.local",
    "password": "Teste123!"
  }'
```

---

## 🔑 Credenciais de Teste

```
Email:    teste_backend@datumagro.local
Senha:    Teste123!
Cliente:  Pecuária Silva
```

---

## 📚 URLs Importantes

| Função | URL |
|--------|-----|
| Health Check | http://localhost:8000/api/health/ |
| Swagger UI | http://localhost:8000/api/swagger/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Schema OpenAPI | http://localhost:8000/api/schema/ |
| Admin Django | http://localhost:8000/admin/ |

---

## 🧪 Endpoints Testados ✅

| Método | Endpoint | Status |
|--------|----------|--------|
| POST | /api/token/ | ✅ Funcionando |
| POST | /api/token/refresh/ | ✅ Pronto |
| GET | /api/usuarios/me/ | ✅ Funcionando |
| GET | /api/cadastros/propriedades/ | ✅ Funcionando |
| GET | /api/cadastros/animais/ | ✅ Funcionando |
| POST | /api/cadastros/propriedades/ | ✅ Pronto |
| POST | /api/cadastros/animais/ | ✅ Pronto |

---

## ⚡ Troubleshooting Rápido

### Problema: "Porta 8000 já está em uso"
```bash
# Matar processo
lsof -ti:8000 | xargs kill -9

# Ou usar outra porta
python manage.py runserver 0.0.0.0:8001
```

### Problema: "401 Unauthorized"
```bash
# Verificar se o token foi incluído no header
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/api/usuarios/me/
```

### Problema: "CORS Error"
```bash
# Confirmar que 10.0.2.2:8000 está na lista CORS_ALLOWED_ORIGINS
# Ver arquivo: datumagro/settings.py linha ~160
```

---

## 🎯 Dados de Teste

**Propriedades Disponíveis:**
- ID 1: "fazenda datum" (RJ)
- ID 3: "Fazenda Smoke Test" (SP)
- ID 4-10: Outras propriedades

**Animais Disponíveis:**
- ID 1-11: Diversos animais registrados no banco

---

## 📋 Checklist para Flutter Developer

- [ ] Backend servidor rodando: `python manage.py runserver`
- [ ] Token JWT obtido com sucesso
- [ ] Acesso a `/api/usuarios/me/` funcionando
- [ ] Listagem de propriedades retornando dados
- [ ] Listagem de animais retornando dados
- [ ] Swagger UI acessível em localhost:8000/api/swagger/

---

## 🔗 Links Úteis

- [Documentação Completa](./SUMARIO_EXECUTIVO_INTEGRACAO.md)
- [Análise Técnica](./ANALISE_BACKEND_PARA_FLUTTER.md)
- [Guia de Testes Práticos](./GUIA_TESTES_PRATICOS.md)
- [Correções Aplicadas](./CORRECOES_APLICADAS.md)

---

## 💡 Dicas

1. **Armazenar tokens em secure storage** do Flutter
2. **Implementar refresh automático** quando token expirar
3. **Usar interceptor** para attach Authorization header
4. **Testar sincronização offline** com endpoint `/api/cadastros/sync/`
5. **Validar respostas** e tratare rros HTTP

---

**Status:** ✅ Backend 100% Pronto  
**Próximo Passo:** Iniciar integração Flutter
