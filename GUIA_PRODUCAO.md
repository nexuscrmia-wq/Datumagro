# 🚀 GUIA DE PRODUÇÃO - DatumAgro Backend

> Instruções para preparar o backend DatumAgro para produção no Render.com

---

## 📋 Checklist de Segurança

### Configurações Django (✅ Implementadas)

- [x] **DEBUG = False** - Modo debug desativado em produção
- [x] **SECRET_KEY Segura** - Gerada aleatoriamente via `.env`
- [x] **HTTPS/SSL** - Configurado com HSTS
- [x] **CORS Restritivo** - Apenas origens autorizadas
- [x] **Security Headers** - XSS, CSP configurados
- [x] **Cookie Security** - Secure + HttpOnly

### Variáveis de Ambiente (`.env`)

```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<gerar com: python generate_secret_key.py>
ALLOWED_HOSTS=datumagro.onrender.com,www.datumagro.onrender.com
DATABASE_URL=postgresql://user:password@host:5432/datumagro
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-app-password
FRONTEND_URL=https://seu-frontend.com
TWILIO_ACCOUNT_SID=<optional>
TWILIO_AUTH_TOKEN=<optional>
```

---

## 🗄️ PASSO 1: Configurar PostgreSQL

### Opção A: PostgreSQL Gerenciado (Recomendado)

Use o PostgreSQL do Render.com (incluso no plano):

```bash
# No Render.com:
# 1. Vá para Dashboard
# 2. Clique em "New +"
# 3. Selecione "PostgreSQL"
# 4. Preencha:
#    - Name: datumagro-db
#    - PostgreSQL Version: 15
# 5. Copie a DATABASE_URL
```

### Opção B: PostgreSQL Local (para testes)

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Criar database
sudo -u postgres createdb datumagro
sudo -u postgres createuser datumagro -P

# DATABASE_URL local:
# postgresql://datumagro:password@localhost:5432/datumagro
```

---

## 📦 PASSO 2: Migrar dados SQLite → PostgreSQL

### Backup SQLite

```bash
cp db.sqlite3 db.sqlite3.backup
```

### Instalar psycopg2 (driver PostgreSQL para Python)

```bash
pip install psycopg2-binary
# ou
pip install psycopg2
```

### Executar Migrations em PostgreSQL

```bash
# 1. Atualizar .env com DATABASE_URL PostgreSQL
export DATABASE_URL='postgresql://user:password@host:5432/datumagro'

# 2. Executar migrations
python manage.py migrate

# 3. Criar superuser
python manage.py createsuperuser

# 4. Carregar dados (opcional)
python manage.py dumpdata --format=json > data.json  # Backup da base SQLite
python manage.py loaddata data.json                   # Carregar em PostgreSQL
```

---

## 🌐 PASSO 3: Configurar Render.com

### Criar Web Service

1. **Conectar GitHub:**
   ```
   Render.com Dashboard → Services → New → Web Service
   Conectar repo: datumagro175-ai/DatumAgro
   Branch: feat/flutter-integration
   ```

2. **Configurar Build & Deploy:**
   ```
   Build Command:   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   Start Command:   gunicorn datumagro.wsgi:application --bind 0.0.0.0:$PORT
   ```

3. **Environment Variables (.env):**
   ```
   ENVIRONMENT=production
   DEBUG=False
   SECRET_KEY=<gerar>
   ALLOWED_HOSTS=datumagro.onrender.com
   DATABASE_URL=<PostgreSQL do Render>
   EMAIL_HOST_USER=seu-email
   EMAIL_HOST_PASSWORD=seu-app-password
   FRONTEND_URL=https://seu-frontend.onrender.com
   RENDER_EXTERNAL_HOSTNAME=datumagro.onrender.com
   ```

4. **Variáveis PostgreSQL (auto-configuradas):**
   - Se usar PostgreSQL do Render, a variável `DATABASE_URL` é automaticamente criada

### Habilitar SSL (Automático)

- Render.com fornece SSL automático com Let's Encrypt
- Certificado é renovado automaticamente

---

## 🔐 PASSO 4: Variáveis de Ambiente

### Gerar SECRET_KEY

```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro
python generate_secret_key.py

# Output:
# SECRET_KEY=django-insecure-xyz...
```

### Variáveis Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `ENVIRONMENT` | Modo de execução | `production` |
| `DEBUG` | Django debug mode | `False` |
| `SECRET_KEY` | Chave segura | `<gerada>` |
| `DATABASE_URL` | String de conexão | `postgresql://...` |
| `ALLOWED_HOSTS` | Hosts autorizados | `datumagro.onrender.com` |

### Variáveis Opcionais

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `EMAIL_HOST_USER` | Email para notificações | Console backend |
| `EMAIL_HOST_PASSWORD` | Senha do email | - |
| `FRONTEND_URL` | URL do frontend | `https://datumagro.com` |
| `TWILIO_*` | Credenciais SMS/WhatsApp | - |

---

## ✅ PASSO 5: Validar Produção

### Health Check

```bash
# Verificar se o servidor está respondendo
curl https://datumagro.onrender.com/api/swagger/

# Deve retornar 200 OK com documentação Swagger
```

### Testar Endpoints

```bash
# 1. Login
curl -X POST https://datumagro.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"seu-usuario","password":"sua-senha"}'

# Response: {"access":"token...","refresh":"token..."}

# 2. Listar animais (com token)
curl -X GET https://datumagro.onrender.com/api/cadastros/animais/ \
  -H "Authorization: Bearer <seu-token>"

# Response: {"count":10,"results":[...]}
```

### Testar Email

```bash
# Entrar no shell Django
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'DatumAgro Test Email',
    'This is a test from production',
    'seu-email@gmail.com',
    ['seu-email@gmail.com'],
)
```

---

## 🐛 TROUBLESHOOTING

### Erro: "No database found"

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Executar migrations novamente
python manage.py migrate

# Criar superuser
python manage.py createsuperuser
```

### Erro: 502 Bad Gateway

```bash
# Verificar logs no Render.com Dashboard
# Pode ser: SECRET_KEY não configurado, DATABASE_URL inválido, etc.

# Testar localmente:
ENVIRONMENT=production python manage.py runserver 0.0.0.0:8000
```

### Erro: CORS Blocked

```bash
# Verificar se FRONTEND_URL está correto em settings.py
# Certificar que CORS_ALLOWED_ORIGINS inclui seu frontend

# Testar:
curl -X OPTIONS https://seu-backend.com/api/token/ \
  -H "Origin: https://seu-frontend.com" \
  -H "Access-Control-Request-Method: POST"
```

### Erro: Static files not loading

```bash
# Executar collectstatic
python manage.py collectstatic --noinput

# Verificar STATIC_URL e STATIC_ROOT em settings.py
```

---

## 📊 Monitoramento (Opcional)

### Render.com Monitoring

- Dashboard → Logs: Ver logs em tempo real
- Metrics: CPU, Memory, HTTP requests
- Alerts: Configurar alertas por email

### Sentry (Optional Error Tracking)

```bash
pip install sentry-sdk

# settings.py
import sentry_sdk
sentry_sdk.init(
    dsn="https://key@sentry.io/project",
    traces_sample_rate=1.0,
    environment="production"
)
```

---

## 🔄 Processo de Deploy Contínuo

### GitHub Actions (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main, feat/flutter-integration]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }} \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

---

## 🎯 Checklist Final

Antes de colocar em produção:

- [ ] `ENVIRONMENT=production` em .env
- [ ] `DEBUG=False` (nunca False)
- [ ] `SECRET_KEY` gerada e segura
- [ ] PostgreSQL configurado e migrado
- [ ] `ALLOWED_HOSTS` correto
- [ ] `CORS_ALLOWED_ORIGINS` restritivo
- [ ] SSL/HTTPS habilitado
- [ ] Email configurado
- [ ] Logs configurados
- [ ] Backup do SQLite realizado
- [ ] Testes de endpoints passando
- [ ] Admin funcional (`/admin/`)
- [ ] Swagger funcional (`/api/swagger/`)
- [ ] CORS testado com frontend

---

## 📞 Support

- Render.com Docs: https://render.com/docs
- Django Production: https://docs.djangoproject.com/en/5.0/howto/deployment/
- DRF Security: https://www.django-rest-framework.org/topics/security/

---

**Última atualização:** 13 de novembro de 2025  
**Status:** ✅ Pronto para Produção
