# 🚀 GUIA COMPLETO - DEPLOY DATUMAGRO NO RENDER COM PostgreSQL

## 📋 Índice
1. [Preparação Inicial](#preparação-inicial)
2. [Configurar GitHub](#configurar-github)
3. [Configurar Render](#configurar-render)
4. [Variáveis de Ambiente](#variáveis-de-ambiente)
5. [Primeiros Passos no Render](#primeiros-passos-no-render)
6. [Monitoramento](#monitoramento)
7. [Troubleshooting](#troubleshooting)

---

## 1. Preparação Inicial

### 1.1 Verificar que tudo está configurado localmente

```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro

# Verificar que o settings.py está correto para produção
python manage.py check

# Resultado esperado:
# ✅ System check identified no issues (0 silenced)
```

### 1.2 Verificar arquivos de configuração

Você precisa dos seguintes arquivos na raiz do projeto:

```
✅ requirements.txt       - Dependências Python
✅ build.sh              - Script de build do Render
✅ Procfile              - Configuração de processo do Render
✅ runtime.txt           - Versão Python (3.12.3)
✅ .env.example          - Exemplo de variáveis de ambiente
✅ .gitignore            - Arquivos a ignorar no Git
```

Verifique com:

```bash
ls -la build.sh Procfile runtime.txt .env.example requirements.txt
```

### 1.3 Criar arquivo .gitignore se não existir

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Django
*.log
db.sqlite3
/staticfiles/
/media/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
EOF
```

---

## 2. Configurar GitHub

### 2.1 Criar repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `DatumAgro` (ou o que preferir)
3. Descrição: "Sistema de gestão pecuária - Backend Django + Flutter"
4. Visibilidade: **Public** (para integrar com Render free)
5. Inicializar com README: Não
6. Clique em **Create Repository**

### 2.2 Fazer push do código para GitHub

```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro

# Inicializar Git (se não tiver feito)
git init

# Configurar usuário Git
git config user.name "seu-nome"
git config user.email "seu-email@gmail.com"

# Adicionar todos os arquivos
git add .

# Fazer commit inicial
git commit -m "🚀 Deploy inicial - Backend DatumAgro com todas as melhorias globais"

# Adicionar remote do GitHub (substitua seu-usuario)
git remote add origin https://github.com/seu-usuario/DatumAgro.git

# Fazer push para main
git branch -M main
git push -u origin main
```

**Resultado esperado:**
```
Enumerating objects: 450, done.
Counting objects: 100% (450/450), done.
Delta compression using up to 8 threads
Compressing objects: 100% (400/400), done.
Writing objects: 100% (450/450), 12.34 MiB, done.
...
To github.com:seu-usuario/DatumAgro.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from origin.
```

---

## 3. Configurar Render

### 3.1 Conectar GitHub ao Render

1. Acesse https://render.com/
2. Crie uma conta (ou faça login)
3. Clique em **Dashboard** → **New +** → **Web Service**
4. Selecione **Deploy an existing project from a Git repository**
5. Conecte sua conta GitHub
6. Procure por `DatumAgro` e selecione
7. Clique em **Connect**

### 3.2 Configurar Web Service no Render

**Nome:** `datumagro-api`

**Environment:** `Python 3`

**Region:** `North America (Ohio)` ou a mais próxima de você

**Branch:** `main`

**Build Command:** `./build.sh`

**Start Command:** `gunicorn datumagro.wsgi:application --bind 0.0.0.0:$PORT --workers 3`

**Plan:** Free (gratuito para começar)

### 3.3 Adicionar PostgreSQL

1. No Render Dashboard, clique em **New +** → **PostgreSQL**
2. **Nome:** `datumagro-db`
3. **Database:** `datumagro`
4. **User:** `datumagro_user`
5. **Region:** Mesma do Web Service
6. **Plan:** Free (512MB gratuito)
7. Clique em **Create Database**

**Aguarde 2-3 minutos** até a database estar pronta.

Copie a **Internal Database URL** - será automática no Web Service.

### 3.4 Adicionar Redis (Opcional mas Recomendado)

1. Clique em **New +** → **Redis**
2. **Nome:** `datumagro-cache`
3. **Region:** Mesma do Web Service
4. **Plan:** Free
5. Clique em **Create**

Copie a **Internal Redis URL**.

---

## 4. Variáveis de Ambiente

### 4.1 No Render Dashboard do Web Service

Vá para **Environment** e adicione as seguintes variáveis:

```bash
# Django Core
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=gerar-nova-chave-segura

# Database
# DATABASE_URL é automático se você conectou o PostgreSQL
# Não precisa adicionar manualmente

# Redis
REDIS_URL=seu-internal-redis-url

# Hosts
ALLOWED_HOSTS=seu-app.onrender.com,www.seu-app.onrender.com
RENDER_EXTERNAL_HOSTNAME=seu-app.onrender.com
FRONTEND_URL=https://seu-frontend.onrender.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=senha-app-google

# CORS
CORS_ALLOWED_ORIGINS=https://seu-app.onrender.com,https://seu-frontend.onrender.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4.2 Gerar SECRET_KEY Segura

No seu computador local, execute:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie a saída e cole em `SECRET_KEY` no Render.

---

## 5. Primeiros Passos no Render

### 5.1 Deploy Automático

Quando você fazer push para o GitHub:

```bash
git add .
git commit -m "Mensagem de commit"
git push origin main
```

O Render **detecta automaticamente** a mudança e começa o deploy.

Monitore em: **Dashboard** → Seu serviço → **Logs**

### 5.2 Verificar Status

1. Clique no seu Web Service no Render
2. Vá para **Logs**
3. Procure por:

```
✅ Build started...
✅ Installing dependencies...
✅ Running migrations...
✅ Build successful - starting service
```

### 5.3 Acessar sua API

Sua API estará em:

```
https://seu-app.onrender.com
```

Teste com:

```bash
# Sem autenticação (deve retornar 401)
curl https://seu-app.onrender.com/api/cadastros/animais/

# Com token JWT
curl -H "Authorization: Bearer seu-token" \
  https://seu-app.onrender.com/api/cadastros/animais/
```

### 5.4 Acessar Django Admin

```
https://seu-app.onrender.com/admin
```

**Usuário:** Crie com o comando:

```bash
# No Render, vá em sua WebService → Shell
python manage.py createsuperuser
```

### 5.5 Acessar Swagger/Redoc

```
https://seu-app.onrender.com/api/swagger/
https://seu-app.onrender.com/api/redoc/
```

---

## 6. Monitoramento

### 6.1 Logs em Tempo Real

**Dashboard** → Seu serviço → **Logs**

Procure por erros como:
- `ERROR` - Erros da aplicação
- `WARNING` - Avisos importantes
- `Database connection failed` - Problema com banco

### 6.2 Health Check

Render faz health check automático. Para verificar:

```bash
curl https://seu-app.onrender.com/api/health/
```

Resultado esperado:

```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected"
}
```

### 6.3 Monitorar PostgreSQL

No Render Dashboard:
1. Clique em seu banco PostgreSQL
2. Vá para **Logs**
3. Procure por problemas de conexão

---

## 7. Troubleshooting

### Problema: "Build failed"

**Solução:**

```bash
# Verifique o build.sh
cat build.sh

# Deve ter permissão de execução
chmod +x build.sh

# Faça commit e push
git add build.sh
git commit -m "Fix build.sh permissions"
git push origin main
```

### Problema: "Database connection failed"

**Solução:**

1. Verifique se o PostgreSQL está rodando:
   - Dashboard → PostgreSQL → Logs

2. Verifique DATABASE_URL no Web Service:
   - Web Service → Environment
   - Procure por `DATABASE_URL`
   - Deve começar com `postgresql://`

3. Tente migrar manualmente:
   - Web Service → Shell (tab)
   - Execute: `python manage.py migrate`

### Problema: "Static files not found"

**Solução:**

```bash
# Local
python manage.py collectstatic --noinput

# Commit e push
git add .
git commit -m "Update static files"
git push origin main
```

### Problema: "Module not found"

**Solução:**

```bash
# Verifique requirements.txt
cat requirements.txt

# Atualize e faça push
pip install pipreqs
pipreqs . --force

git add requirements.txt
git commit -m "Update requirements"
git push origin main
```

### Problema: "Redis connection failed"

**Solução:**

1. Redis é opcional
2. Se não quiser usar, remova do Render
3. No settings.py, Redis será ignorado se não disponível

### Problema: "CORS errors no Flutter"

**Solução:**

Adicione seu domínio em CORS_ALLOWED_ORIGINS:

```bash
# No Render Environment
CORS_ALLOWED_ORIGINS=https://seu-app.onrender.com,https://seu-flutter-app.com

# Commit e push para trigger deploy
git add .
git commit -m "Update CORS for Flutter"
git push origin main
```

---

## 8. Próximos Passos

### 8.1 Produção Completa

Para uma aplicação de produção:

1. **Upgrade Render** - Use plano pago para melhor performance
2. **CDN** - Use Cloudflare para cache global
3. **Backup** - Configure backup automático do PostgreSQL
4. **Monitoring** - Use Sentry para rastrear erros

### 8.2 Conectar Flutter App

No seu app Flutter, use:

```dart
const String API_BASE_URL = 'https://seu-app.onrender.com';

// Fazer requisição
var response = await http.get(
  Uri.parse('$API_BASE_URL/api/cadastros/animais/'),
  headers: {'Authorization': 'Bearer $token'},
);
```

### 8.3 Domain Customizado

1. No Render, vá para seu Web Service
2. **Settings** → **Custom Domains**
3. Adicione seu domínio (ex: `api.seusite.com`)
4. Siga as instruções de DNS

---

## ✅ Checklist Final

- [ ] Código no GitHub
- [ ] Web Service criado no Render
- [ ] PostgreSQL criado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Build bem-sucedido
- [ ] Migrations rodadas
- [ ] Admin acessível
- [ ] API respondendo
- [ ] Flutter conectado à API
- [ ] CORS configurado
- [ ] Logs monitorados
- [ ] Database backups configured

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os **Logs** no Render
2. Execute `python manage.py check` localmente
3. Teste com `curl` ou Postman
4. Verifique variáveis de ambiente

---

**🎉 Parabéns! Seu backend está em produção no Render!**

Acesse em: `https://seu-app.onrender.com`

