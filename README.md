# DatumAgro Backend — API guide for Flutter frontend

This README documents how to run and use the Django backend so you can connect the Flutter frontend (auth, password reset, forms of payment, etc.). It also includes sample Flutter and curl requests.

## Quick start (development)

1. Create and activate a virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Migrate and create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Run server

```bash
python manage.py runserver
```

Server runs on `http://127.0.0.1:8000/` by default.

## Auth endpoints

All user endpoints are under `/api/usuarios/usuarios/` because the `UsuarioViewSet` is registered with the `usuarios` router.

- Register (creates user + returns JWT tokens):
  - POST `/api/usuarios/usuarios/registrar/`
  - Body (JSON): `{ "email": "you@example.com", "password": "Pass123!", "password2": "Pass123!", "first_name": "Nome", "last_name": "Sobrenome" }`

- Login (returns JWT tokens):
  - POST `/api/usuarios/usuarios/login/`
  - Body (JSON): `{ "email": "you@example.com", "password": "Pass123!" }`

- Get profile (requires Authorization: Bearer <access_token>):
  - GET `/api/usuarios/me/`

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
