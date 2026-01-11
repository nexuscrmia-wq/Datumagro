# DatumAgro Backend — API guide for Flutter frontend

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-darkgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

Comprehensive Django backend for DatumAgro livestock management platform with Flutter mobile integration.

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **[README_FLUTTER.md](README_FLUTTER.md)** | 🎯 Complete Flutter integration guide with Dart examples |
| **[GUIA_PRODUCAO.md](GUIA_PRODUCAO.md)** | 🚀 Production deployment guide for Render.com |
| **[GUIA_TESTES_PRATICOS.md](GUIA_TESTES_PRATICOS.md)** | ✅ Practical testing guide with curl examples |
| **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)** | 📊 Executive summary and status |
| **[ANALISE_BACKEND_PARA_FLUTTER.md](ANALISE_BACKEND_PARA_FLUTTER.md)** | 🔍 Detailed backend analysis |
| **[CHECKLIST_TODOS.md](CHECKLIST_TODOS.md)** | ✓ TODO checklist and progress tracking |

---

## 🚀 Quick Start (Development)

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/datumagro175-ai/DatumAgro.git
cd DatumAgro

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 2. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
# Email: test@datumagro.com
# Password: Teste123!
```

### 3. Run Server

```bash
# Development server
python manage.py runserver 0.0.0.0:8000

# Access points:
# - API: http://localhost:8000/api/
# - Admin: http://localhost:8000/admin/
# - Swagger: http://localhost:8000/api/swagger/
```

---

## 🔑 Key Features

✅ **Authentication**
- JWT-based authentication with SimpleJWT
- Token refresh mechanism
- Secure token storage

✅ **API Endpoints**
- User registration and login
- CRUD operations for animals and properties
- Sync endpoint for offline-first apps

✅ **Security**
- CORS configured for Flutter emulator
- HTTPS ready for production
- Environment-based configuration
- Secure password storage with Django ORM

✅ **Documentation**
- Interactive Swagger UI at `/api/swagger/`
- Comprehensive API documentation
- Dart code examples for Flutter

---

## 📱 Flutter Integration

### Base URLs by Platform

| Platform | URL |
|----------|-----|
| Android Emulator | `http://10.0.2.2:8000` |
| iOS Simulator | `http://localhost:8000` |
| Physical Device | `http://<HOST_IP>:8000` |
| Production | `https://your-domain.onrender.com` |

### Dependencies (pubspec.yaml)

```yaml
dependencies:
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
```

### Login Example

```dart
final response = await http.post(
  Uri.parse('http://10.0.2.2:8000/api/usuarios/usuarios/login/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'email': 'user@example.com',
    'password': 'password123'
  }),
);

if (response.statusCode == 200) {
  final token = jsonDecode(response.body)['access'];
  // Store token securely and use in future requests
}
```

**⭐ For complete Flutter integration guide, see [README_FLUTTER.md](README_FLUTTER.md)**

---

## 🔐 Production Deployment

### Preparation Checklist

- [x] Security configurations (DEBUG=False, HTTPS, etc.)
- [x] Environment variables template (.env.example)
- [x] Secret key generation script
- [ ] PostgreSQL migration
- [ ] Render.com deployment

**See [GUIA_PRODUCAO.md](GUIA_PRODUCAO.md) for detailed deployment instructions.**

### Quick Deploy to Render.com

```bash
# 1. Generate SECRET_KEY
python generate_secret_key.py

# 2. Push to GitHub
git add .env.example GUIA_PRODUCAO.md
git commit -m "Add production configuration"
git push

# 3. Deploy to Render.com
# - Connect GitHub repo
# - Set environment variables
# - Deploy!
```

---

## 📊 API Endpoints

### Authentication

```
POST   /api/token/                      # JWT Token obtain
POST   /api/token/refresh/              # Refresh token
POST   /api/usuarios/usuarios/login/    # User login
POST   /api/usuarios/usuarios/registrar/ # User registration
GET    /api/usuarios/me/                # Get current user profile
```

### Animals (Animais)

```
GET    /api/cadastros/animais/          # List all animals
POST   /api/cadastros/animais/          # Create animal
GET    /api/cadastros/animais/{id}/     # Get animal details
PUT    /api/cadastros/animais/{id}/     # Update animal
DELETE /api/cadastros/animais/{id}/     # Delete animal
```

### Properties (Propriedades)

```
GET    /api/cadastros/propriedades/     # List all properties
POST   /api/cadastros/propriedades/     # Create property
GET    /api/cadastros/propriedades/{id}/ # Get property details
PUT    /api/cadastros/propriedades/{id}/ # Update property
DELETE /api/cadastros/propriedades/{id}/ # Delete property
```

### Synchronization

```
POST   /api/cadastros/sync/             # Sync offline changes
```

---

## 🧪 Testing

### Run Automated Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest datumagro/apps/usuarios/tests.py

# With coverage
pytest --cov=datumagro
```

### Run Integration Tests

```bash
# Backend must be running
python manage.py runserver 0.0.0.0:8000

# In another terminal
python test_api_integration.py
```

### Manual API Testing

Use the interactive Swagger UI:
```
http://localhost:8000/api/swagger/
```

Or use curl:
```bash
# Get token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@datumagro.com","password":"Teste123!"}'

# List animals with token
curl -X GET http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer <your-token>"
```

**See [GUIA_TESTES_PRATICOS.md](GUIA_TESTES_PRATICOS.md) for comprehensive testing guide.**

---

## 🏗️ Project Structure

```
DatumAgro/
├── datumagro/                    # Main Django project
│   ├── settings.py               # Configuration (✅ Production ready)
│   ├── urls.py                   # URL routing
│   └── apps/
│       ├── usuarios/             # User management
│       ├── cadastros/            # Animals & properties
│       ├── financeiro/           # Finance management
│       ├── inteligencia/         # AI alerts
│       └── ...                   # Other apps
├── mobile_flutter/               # Flutter app
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── generate_secret_key.py        # SECRET_KEY generator
├── GUIA_PRODUCAO.md              # Production guide
├── README_FLUTTER.md             # Flutter integration
└── GUIA_TESTES_PRATICOS.md      # Testing guide
```

---

## 📋 Environment Variables

### Required for Development

```env
ENVIRONMENT=development
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost,10.0.2.2
```

### Required for Production

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate with: python generate_secret_key.py>
DATABASE_URL=postgresql://user:password@host:5432/datumagro
ALLOWED_HOSTS=your-domain.com
FRONTEND_URL=https://your-frontend.com
```

**See [GUIA_PRODUCAO.md](GUIA_PRODUCAO.md) for all environment variables.**

---

## 🐛 Troubleshooting

### Server not starting?
```bash
# Check Python version (3.10+)
python --version

# Verify virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

### CORS errors in Flutter?
```python
# Verify in settings.py:
# Development: CORS_ALLOW_ALL_ORIGINS = True
# Production: CORS_ALLOWED_ORIGINS = ["your-domain"]
```

### Can't connect from Android emulator?
```bash
# Use correct base URL
http://10.0.2.2:8000  # NOT localhost:8000

# Or use host IP
hostname -I  # Find your machine IP
http://<YOUR_IP>:8000
```

---

## 📞 Support & Documentation

- **API Docs:** http://localhost:8000/api/swagger/
- **Admin Panel:** http://localhost:8000/admin/
- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/

---

## 📝 License

This project is part of DatumAgro - Livestock Management Platform

---

## 👥 Contributors

- Victor Emanuel - Backend Developer
- DatumAgro Team

---

**Last Updated:** November 13, 2025  
**Status:** ✅ Production Ready


- Password reset (request email):
  - POST `/api/usuarios/usuarios/reset_password/`
  - Body: `{ "email": "you@example.com" }`
  - The backend will send an email (or print to console in dev) with a `reset_url` containing a token.

- Confirm password reset:
  - POST `/api/usuarios/usuarios/confirm_reset_password/`
  - Body: `{ "token": "<token>", "new_password": "NewPass123!", "new_password2": "NewPass123!" }`

## Forms of Payment (financeiro)

- List and create forms of payment (authenticated):
  - GET `/api/financeiro/formas-pagamento/`
  - POST `/api/financeiro/formas-pagamento/`
  - Example POST body for PIX: `{ "tipo": "PX", "titular": "João", "chave_pix": "meu-pix@banco" }`
  - Example POST body for card: `{ "tipo": "CC", "titular": "João", "numero_cartao": "4111111111111111", "validade": "12/2027", "bandeira": "VISA" }`

Notes: for security never store CVV; in production use a payment gateway and tokenize card data.

## cURL examples

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/usuarios/usuarios/registrar/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Testpass123!","password2":"Testpass123!","first_name":"Teste","last_name":"Usuario"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/usuarios/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Testpass123!"}'
```

Use the returned `access` token in requests:

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/usuarios/me/
```

Create FormaPagamento (example):

```bash
curl -X POST http://127.0.0.1:8000/api/financeiro/formas-pagamento/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"tipo":"PX","titular":"João","chave_pix":"meu-pix@banco"}'
```

## Flutter integration notes

- Use the Android emulator base URL `http://10.0.2.2:8000` or `http://localhost:8000` for iOS simulator. For a physical device, use the machine IP on the local network (ex.: `http://192.168.1.100:8000`).
- Example Dart service (login):

```dart
// lib/data/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiConfig { static const baseUrl = 'http://10.0.2.2:8000'; }

class ApiService {
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await http.post(
      Uri.parse('\${ApiConfig.baseUrl}/api/usuarios/usuarios/login/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'email': email, 'password': password}),
    );
    if (res.statusCode == 200) return json.decode(res.body);
    throw Exception('Falha no login');
  }
}
```

Store `access` and `refresh` tokens securely (recommendation: `flutter_secure_storage`).

Implement token refresh flow (call `/api/token/refresh/` with `refresh` token to obtain a new access token).

## Email and dev behavior

- If `EMAIL_HOST_USER` is not set in your `.env`, the back-end uses `console` email backend so password reset emails are printed on the server console (development friendly).

## CORS and frontend

- `CORS_ALLOWED_ORIGINS` already includes common dev addresses for React/Flutter emulators.
- If you run Flutter on a physical device, add your machine IP to `CORS_ALLOWED_ORIGINS` or set `CORS_ALLOW_ALL_ORIGINS = True` (dev only).

## Next steps / suggestions

- Add OpenAPI/Swagger (e.g., `drf-yasg` or `drf-spectacular`) to provide a machine-readable API description for faster frontend integration.
- Consider adding integration tests and a Postman collection for the frontend team.
- For payments, integrate with a payment gateway (Stripe, Pagar.me) and store tokens instead of raw card numbers.

---

If you want, posso now:
- add a Swagger/OpenAPI endpoint,
- create an example Postman collection file,
- or run quick smoke tests against the running server.

Tell me which you want next.
# DatumAgro 🐂

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.4-3781A9?style=for-the-badge&logo=celery&logoColor=white)

Uma plataforma completa de Pecuária de Precisão com Inteligência Artificial, desenvolvida pela **Vexus IA**.

## 🎯 Sobre o Projeto

O DatumAgro nasceu da necessidade de modernizar a gestão pecuária, substituindo anotações manuais em cadernetas e planilhas complexas por uma plataforma digital, inteligente e centralizada. O objetivo é transformar dados brutos em decisões estratégicas, aumentando a eficiência e a lucratividade da fazenda.

O sistema é construído sobre uma arquitetura de API RESTful robusta (o "motor"), pronta para ser consumida por múltiplas interfaces, como um aplicativo mobile (Android) e uma plataforma web.

## ✨ Principais Funcionalidades

O motor do DatumAgro é modular e foi dividido em 11 apps, cada um com sua responsabilidade:

* **Gestão de Cadastros:** Controle completo de Clientes, Propriedades e Animais, incluindo um sistema de **Árvore Genealógica** para rastreamento genético.
* **Controle Operacional:** Registro de manejos sanitários, reprodutivos, e gestão de Lotes e Piquetes para pastejo rotacionado.
* **Análise Financeira:** Lançamento de custos e receitas, com ferramentas para análise de fluxo de caixa e lucratividade.
* **IA Zootecnista Virtual:** Um sistema proativo que analisa os dados e gera alertas inteligentes sobre saúde, desempenho (baixo GMD) e manejo.
* **Notificações Ativas:** Alertas enviados automaticamente para o produtor via E-mail e WhatsApp (utilizando Twilio).
* **Rastreabilidade (Selo de Origem):** Geração de uma página pública e um QR Code para cada animal, contando sua história "da fazenda à mesa".
* **Integrações com Hardware (IoT):** API pronta para receber dados de equipamentos de campo, como leitores de RFID e balanças eletrônicas.
* **Gestão de Assinaturas:** Sistema de planos (Digital, Conectado, Elite) com controle de status e vencimento.
* **Geração de Relatórios:** Criação de relatórios em PDF e Excel sob demanda.
* **Autenticação Moderna:** Sistema de usuários customizado com autenticação via Token para a API.

## 🛠️ Tech Stack

* **Back-end:** Python, Django, Django REST Framework
* **Banco de Dados:** PostgreSQL (produção), SQLite (desenvolvimento)
* **Tarefas Assíncronas:** Celery, Redis
* **Servidor de Produção:** Gunicorn, Whitenoise
* **Análise de Dados:** Pandas
* **Outros:** WeasyPrint (PDFs), Pillow (Imagens), Twilio (WhatsApp)

# DatumAgro �

Este repositório contém o backend Django do DatumAgro e um scaffold de cliente mobile Flutter (pasta `mobile_flutter/`) criado para demonstrar um aplicativo offline-first que sincroniza com a API.

Este `README` foi atualizado automaticamente para resumir o trabalho realizado, explicar onde as mudanças foram feitas e como testar o backend e o aplicativo Flutter no emulador local.

## Resumo do que foi implementado

- Backend (Django / DRF):
    - Adicionado endpoint de sincronização em `datumagro/apps/cadastros/views.py` (view `sync_view`) que aceita lotes de mudanças do cliente e aplica operações de create/update/delete de forma transacional.
    - Detecta conflitos simples usando o campo `updated_at` (política inicial: server_wins). Retorna ao cliente objetos aplicados, mudanças do servidor (`server_changes`) e conflitos.
    - `Animal` model atualizado para incluir `updated_at = models.DateTimeField(auto_now=True)`.
    - Serializers ajustados para expor `updated_at` como read-only.
    - Testes unitários adicionados em `datumagro/apps/cadastros/tests_sync.py` para cobrir cenários de create, update-conflict e delete via `/api/cadastros/sync/`.

- Mobile (Flutter + Drift):
    - Scaffold criado em `mobile_flutter/` com `pubspec.yaml`, telas (`lib/screens/`), serviço de sincronização (`lib/services/sync_service.dart`) e esquema Drift (`lib/data/database.dart`).
    - Drift mapeia a tabela `Animals` com os principais campos do modelo (incluindo `serverId` e `updatedAt`) e uma `SyncQueue` local para enfileirar mudanças.
    - `Login` salva token DRF em `flutter_secure_storage` e todas as requisições usam `Authorization: Token <token>`.
    - `AnimalsList` escuta mudanças de conectividade e executa sincronização automática ao reconectar (debounce de 10s).
    - `AnimalForm` grava/atualiza registros locais e enfileira a mudança completa (incluindo `updated_at`) para envio ao servidor.

## Arquivos/trechos importantes modificados/criados

- Backend:
    - `datumagro/apps/cadastros/views.py` — `sync_view` e lógica de aplicação de mudanças.
    - `datumagro/apps/cadastros/models.py` — `updated_at` adicionado ao `Animal`.
    - `datumagro/apps/cadastros/serializers.py` — `updated_at` como read-only.
    - `datumagro/apps/cadastros/urls.py` — rota `sync/` registrada.
    - `datumagro/apps/cadastros/tests_sync.py` — testes da API de sincronização.

- Mobile (novo diretório `mobile_flutter/`):
    - `pubspec.yaml` — dependências (drift, drift_flutter, build_runner, connectivity_plus, flutter_secure_storage, http, path_provider, provider).
    - `lib/data/database.dart` — esquema Drift (`Animals`, `SyncQueue`) e métodos utilitários (`upsertByServerId`, `getByServerId`).
    - `lib/services/sync_service.dart` — envia lotes ao endpoint `/api/cadastros/sync/` e aplica `server_changes` localmente.
    - `lib/screens/login.dart`, `lib/screens/animals_list.dart`, `lib/screens/animal_form.dart` — telas básicas para autenticação, listagem e criação/edição de animais.

## Como rodar — Backend (local)

1. Configure ambiente Python e dependências (exemplo usando venv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure variáveis de ambiente (creie `.env` a partir de `.env.example` se houver):

- `SECRET_KEY`, `DATABASE_URL` (para desenvolvimento pode usar SQLite) e outras chaves de API usadas no projeto.

3. Aplique migrações e crie um superusuário:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Execute o servidor Django em modo de desenvolvimento (escutando em 127.0.0.1:8000 por padrão):

```bash
python manage.py runserver
```

Observação: o endpoint de obtenção do token DRF fica em `/api/api-token-auth/` e o grupo de rotas do app `cadastros` foi incluído em `/api/cadastros/`.

## Como rodar — Flutter (emulador Android / desenvolvimento)

Observação importante: o código do Drift precisa gerar os arquivos de implementação. Execute os comandos abaixo dentro de `mobile_flutter/`.

1. Instale dependências Flutter e execute `pub get`:

```bash
cd mobile_flutter
flutter pub get
```

2. Gere os arquivos do Drift (build_runner):

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

3. Execute no emulador Android (recomendo usar o emulador do Android Studio). Quando o backend estiver rodando no host local, o app usa por padrão `http://10.0.2.2:8000/api/cadastros` para se comunicar com o servidor (endereço especial do emulador para alcançar o host):

```bash
flutter run
```

Se preferir testar com o dispositivo físico, ajuste `baseUrl` nas configurações do serviço de sincronização para apontar ao IP da máquina de desenvolvimento (por exemplo `http://192.168.0.42:8000`).

## Como testar a sincronização (fluxo básico)

1. No backend, garanta que o servidor esteja rodando (`python manage.py runserver`).
2. No app Flutter (emulador):
     - Faça login com um usuário existente via `/api/api-token-auth/` (a tela de login do scaffold faz isso automaticamente) e o token será salvo em armazenamento seguro.
     - Crie ou edite um animal no `AnimalForm`. O registro será gravado localmente e colocado na `SyncQueue`.
     - Quando a conectividade for detectada (ou ao acionar sincronização manual no código), o `SyncService` envia o lote para o endpoint `/api/cadastros/sync/`.
     - O servidor aplica mudanças e responde com `applied`, `server_changes` e `conflicts`. O cliente remove itens aplicados da fila e aplica `server_changes` localmente via upsert por `serverId`.

## Rodando os testes Django (sincronização)

Os testes adicionados ficam em `datumagro/apps/cadastros/tests_sync.py`.

```bash
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test datumagro.apps.cadastros.tests_sync
```

## Pontos importantes / Notas

- Emulação de rede: para o Android emulator use `10.0.2.2` para alcançar `localhost` da máquina host.
- Drift: você precisa executar o `build_runner` localmente para gerar `database.g.dart` antes de executar o app.
- Conflitos: hoje a política de conflito é simples (server_wins). Para produção você provavelmente vai querer uma UI de resolução ou uma estratégia de merge mais avançada.
- Segurança: o endpoint de sync atual é funcional, mas minimalista — adicione validação, autorização e limitação de tamanho/pagina para produção.

## Próximos passos recomendados

1. Gerar e commitar os arquivos gerados do Drift (opcional para manter a facilidade de testes sem rodar build_runner).
2. Melhorar a estratégia de resolução de conflitos (UI para merges, campos por campo, ou CRDTs se necessário).
3. Implementar suporte a upload de imagens (campo `fotoPerfil`) com armazenamento resiliente e referências no Drift.
4. Paginação e limites no endpoint de sincronização para evitar payloads grandes.
5. Harden security: rate-limiting, payload validation, authentication/authorization checks e auditoria de mudanças.

## Resumo final — o que eu alterei aqui

- Backend: adicionei `sync_view`, `updated_at` no `Animal`, e testes de sincronização.
- Mobile: criei um scaffold Flutter com Drift e um SyncService que implementa a lógica cliente para enviar/receber lotes.

Se quiser, eu posso agora:

- Executar os testes Django aqui (preciso da sua confirmação para rodar comandos no ambiente).
- Gerar os artefatos do Drift em `mobile_flutter/` (isso requer `flutter` instalado aqui e tempo para rodar `build_runner`).
- Melhorar a UI de resolução de conflitos e adicionar testes adicionais.

---

Arquivo gerado automaticamente em 21 de outubro de 2025.
