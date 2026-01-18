# 🚀 DEPLOY DATUMAGRO NO RENDER.COM - GUIA COMPLETO

## ✅ STATUS ATUAL
- ✅ Backend Django 100% funcional
- ✅ Correções críticas aplicadas (financeiro, cache)
- ✅ Arquivos de configuração prontos
- ✅ Script de deploy automatizado criado

## 🎯 PRÓXIMOS PASSOS PARA DEPLOY

### 1. CRIAR REPOSITÓRIO GITHUB

1. Acesse: https://github.com/new
2. **Nome do repositório:** `DatumAgro` ou `datumagro-backend`
3. **Descrição:** `Backend Django para DatumAgro - Gestão Pecuária Completa`
4. **Visibilidade:** Público ou Privado
5. **Não inicializar** com README, .gitignore ou license
6. Clique: **"Create repository"**

### 2. CONECTAR REPOSITÓRIO LOCAL

```bash
# No terminal, execute:
cd /home/victor-emanuel/PycharmProjects/DatumAgro

# Adicionar remote (substitua SEU_USERNAME pelo seu GitHub username)
git remote add origin https://github.com/SEU_USERNAME/DatumAgro.git

# Fazer push inicial
git push -u origin feat/flutter-integration
```

### 3. DEPLOY NO RENDER.COM

#### 3.1 Criar Conta no Render.com
1. Acesse: https://render.com
2. **Sign up** com GitHub (recomendado)
3. Verifique seu email

#### 3.2 Conectar Repositório
1. No Dashboard, clique: **"New +"** → **"Web Service"**
2. Selecione: **"Connect GitHub"**
3. Procure por: `DatumAgro` (ou seu nome do repo)
4. Clique: **"Connect"**

#### 3.3 Configurar Serviço
```
Name: datumagro-api
Environment: Docker
Branch: feat/flutter-integration (ou main/master)
Root Directory: (vazio)
Dockerfile Path: ./Dockerfile
```

#### 3.4 Configurar Banco PostgreSQL
1. Vá para: https://render.com/new/database
2. Selecione: **PostgreSQL**
3. Configure:
   - Name: `datumagro-db`
   - Database: `datumagro_prod`
   - User: `datumagro_user`
4. Clique: **"Create Database"**
5. **COPIE** a `DATABASE_URL` fornecida

#### 3.5 Configurar Redis (Opcional)
1. Vá para: https://render.com/new/redis
2. Selecione: **Redis**
3. Name: `datumagro-redis`
4. Clique: **"Create Redis"**
5. **COPIE** a `REDIS_URL` fornecida

### 4. CONFIGURAR VARIÁVEIS DE AMBIENTE

No painel do Render → Seu Web Service → **Environment**:

#### OBRIGATÓRIAS:
```
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=gere-uma-chave-secreta-aqui
DATABASE_URL=postgres://... (copiada do passo 3.4)
```

#### GERE SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### OPCIONAIS (mas recomendadas):
```
REDIS_URL=redis://... (copiada do passo 3.5)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
FRONTEND_URL=https://seusite.com
```

### 5. DEPLOY AUTOMÁTICO

1. Clique: **"Create Web Service"**
2. Render irá:
   - Fazer build da imagem Docker
   - Executar migrations
   - Iniciar o servidor Gunicorn
3. **Tempo estimado:** 5-10 minutos

### 6. VERIFICAR DEPLOY

Após o deploy, teste os endpoints:

```bash
# Substitua YOUR_APP_NAME pelo nome do seu app no Render
curl https://YOUR_APP_NAME.onrender.com/api/health/

# Deve retornar: {"status": "ok"}
```

### 7. CONFIGURAR FLUTTER APP

Atualize a base URL no Flutter app:

```dart
// Em suas configurações do Flutter
const String baseUrl = 'https://YOUR_APP_NAME.onrender.com';
```

## 🔧 COMANDOS DE VERIFICAÇÃO

### Teste Completo da API:
```bash
# 1. Health check
curl https://YOUR_APP_NAME.onrender.com/api/health/

# 2. Login (substitua as credenciais)
curl -X POST -H "Content-Type: application/json" \
  -d '{"email": "admin@datumagro.com", "password": "admin123"}' \
  https://YOUR_APP_NAME.onrender.com/api/token/

# 3. Propriedades
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://YOUR_APP_NAME.onrender.com/api/cadastros/propriedades/

# 4. Categorias Financeiras
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://YOUR_APP_NAME.onrender.com/api/financeiro/categorias/
```

## 🚨 POSSÍVEIS PROBLEMAS

### Erro de Build:
- Verifique se todos os arquivos estão no GitHub
- Confirme que o Dockerfile está correto

### Erro de Database:
- Verifique se DATABASE_URL está correta
- Execute migrations manualmente se necessário

### Erro de CORS:
- Configure FRONTEND_URL corretamente
- Adicione domínios permitidos em CORS_ALLOWED_ORIGINS

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique os logs no painel do Render
2. Teste localmente primeiro: `python manage.py runserver`
3. Consulte: `GUIA_DEPLOY_RENDER.md` (arquivo completo)

## ✅ CHECKLIST FINAL

- [ ] Repositório GitHub criado
- [ ] Código enviado para GitHub
- [ ] Conta Render.com criada
- [ ] Repositório conectado ao Render
- [ ] PostgreSQL criado no Render
- [ ] Redis criado no Render (opcional)
- [ ] Variáveis de ambiente configuradas
- [ ] Web Service criado e deployado
- [ ] Endpoints testados e funcionando
- [ ] Flutter app configurado com nova URL

---

**🎉 PARABÉNS!** Seu backend DatumAgro estará online em minutos!

**Tempo total estimado:** 15-20 minutos