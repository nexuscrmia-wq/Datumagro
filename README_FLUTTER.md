DatumAgro — Flutter Integration Guide

Comprehensive guide for integrating a Flutter app with the DatumAgro API backend.

---

## 1) Base URLs

### Development Environment

| Platform | URL | Notes |
|----------|-----|-------|
| **Android Emulator** | `http://10.0.2.2:8000` | Default emulator gateway |
| **iOS Simulator** | `http://localhost:8000` | Direct localhost |
| **Physical Device** | `http://<HOST_IP>:8000` | Find IP: `hostname -I` |
| **Web** | `http://localhost:8000` | Chrome localhost |

### Production Environment

| Platform | URL |
|----------|-----|
| **All Platforms** | `https://your-domain.com` (Render.com or similar) |

### Starting Django Development Server

```bash
cd /home/victor-emanuel/PycharmProjects/DatumAgro
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

---

## 2) Server-Side Configuration (Already Done ✅)

- ✅ **JWT Authentication:** SimpleJWT endpoints at `/api/token/` and `/api/token/refresh/`
- ✅ **CORS Middleware:** `corsheaders` properly configured for all platforms
- ✅ **Android Emulator Support:** `10.0.2.2` allowed in `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- ✅ **User API:** Custom endpoints at `/api/usuarios/usuarios/`
- ✅ **Security Headers:** HTTPS + SSL ready for production
- ✅ **Database Ready:** Supports SQLite (dev) and PostgreSQL (prod)

---

## 3) Authentication Endpoints

### Login (with email/password)

**Endpoint:** `POST /api/usuarios/usuarios/login/`

```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "primeiro_nome": "João",
    "ultimo_nome": "Silva"
  }
}
```

### Register (new user)

**Endpoint:** `POST /api/usuarios/usuarios/registrar/`

```json
Request:
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "primeiro_nome": "Maria",
  "ultimo_nome": "Santos"
}

Response (201 Created):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

### Refresh Token

**Endpoint:** `POST /api/token/refresh/`

```json
Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 4) Core API Endpoints for Flutter

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

## 5) Dart Implementation Examples

### Setup Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
  dart_jsonwebtoken: ^2.12.0
```

### 5.1) Login Service

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final String baseUrl;
  final storage = const FlutterSecureStorage();

  AuthService({required this.baseUrl});

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/usuarios/usuarios/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await storage.write(key: 'access_token', value: data['access']);
      await storage.write(key: 'refresh_token', value: data['refresh']);
      return {'success': true, 'user': data['user']};
    } else {
      return {'success': false, 'error': 'Login failed'};
    }
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/usuarios/usuarios/registrar/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'primeiro_nome': firstName,
        'ultimo_nome': lastName,
      }),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      await storage.write(key: 'access_token', value: data['access']);
      await storage.write(key: 'refresh_token', value: data['refresh']);
      return {'success': true, 'user': data['user']};
    } else {
      return {'success': false, 'error': jsonDecode(response.body)};
    }
  }

  Future<bool> logout() async {
    await storage.delete(key: 'access_token');
    await storage.delete(key: 'refresh_token');
    return true;
  }

  Future<String?> getAccessToken() async {
    return await storage.read(key: 'access_token');
  }

  Future<bool> isAuthenticated() async {
    final token = await getAccessToken();
    return token != null;
  }
}
```

### 5.2) Authenticated HTTP Client

```dart
import 'package:http/http.dart' as http;

class AuthenticatedHttpClient extends http.BaseClient {
  final String baseUrl;
  final AuthService authService;

  AuthenticatedHttpClient({
    required this.baseUrl,
    required this.authService,
  });

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final token = await authService.getAccessToken();

    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }

    request.headers['Content-Type'] = 'application/json';

    var response = await super.send(request);

    // If 401, try to refresh token and retry
    if (response.statusCode == 401) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        return send(request);
      }
    }

    return response;
  }

  Future<bool> _refreshToken() async {
    final refreshToken = await authService.storage.read(key: 'refresh_token');

    if (refreshToken == null) return false;

    final response = await http.post(
      Uri.parse('$baseUrl/api/token/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': refreshToken}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await authService.storage.write(key: 'access_token', value: data['access']);
      return true;
    }

    // Token refresh failed, user needs to login again
    await authService.logout();
    return false;
  }
}
```

### 5.3) Animal API Service

```dart
class AnimalService {
  final http.BaseClient httpClient;
  final String baseUrl;

  AnimalService({
    required this.httpClient,
    required this.baseUrl,
  });

  Future<List<Map<String, dynamic>>> getAnimals() async {
    final response = await httpClient.get(
      Uri.parse('$baseUrl/api/cadastros/animais/'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data['results'] ?? []);
    }
    throw Exception('Failed to load animals');
  }

  Future<Map<String, dynamic>> createAnimal({
    required int propertyId,
    required String brinco,
    required String raca,
    required String sexo,
    String? dataNascimento,
  }) async {
    final response = await httpClient.post(
      Uri.parse('$baseUrl/api/cadastros/animais/'),
      body: jsonEncode({
        'propriedade': propertyId,
        'brinco': brinco,
        'raca': raca,
        'sexo': sexo,
        'data_nascimento': dataNascimento,
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to create animal');
  }

  Future<bool> updateAnimal({
    required int animalId,
    required Map<String, dynamic> data,
  }) async {
    final response = await httpClient.put(
      Uri.parse('$baseUrl/api/cadastros/animais/$animalId/'),
      body: jsonEncode(data),
    );

    return response.statusCode == 200;
  }

  Future<bool> deleteAnimal(int animalId) async {
    final response = await httpClient.delete(
      Uri.parse('$baseUrl/api/cadastros/animais/$animalId/'),
    );

    return response.statusCode == 204;
  }
}
```

---

## 6) Troubleshooting

### Issue: Emulator Cannot Reach Server

**Solution:**
```bash
# Method 1: Ensure firewall allows port 8000
sudo ufw allow 8000

# Method 2: Run server on all interfaces
python manage.py runserver 0.0.0.0:8000

# Method 3: Find your host IP and use it
hostname -I  # e.g., 192.168.1.100
# Then in Flutter: http://192.168.1.100:8000
```

### Issue: CORS Errors

**Solution:**
```python
# Verify in datumagro/settings.py:
# Development:
CORS_ALLOW_ALL_ORIGINS = True

# Production:
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com"
]
```

### Issue: 401 Unauthorized

**Solution:**
```dart
// 1. Check if token is being sent
final token = await authService.getAccessToken();
print('Token: $token');

// 2. Ensure Authorization header format
headers['Authorization'] = 'Bearer $token';  // Correct
// NOT: headers['Authorization'] = token;    // Wrong

// 3. Token might be expired
await authService.refreshToken();
```

### Issue: 400 Bad Request

**Solution:**
```dart
// Check request body is JSON
headers['Content-Type'] = 'application/json';

// Verify all required fields are sent
// Example for animal: propriedade, brinco, raca, sexo are required
```

---

## 7) Next Steps

1. **Implement Health Check Endpoint** (Optional)
   - Add GET `/api/health/` that returns `{"status": "ok"}`
   - Use in app to verify connectivity before operations

2. **Add Offline-First Support**
   - Use Drift (SQLite) for local caching
   - Sync queue for changes made offline
   - Conflict resolution strategy

3. **Production Ready**
   - Use HTTPS in production
   - Implement token refresh logic robustly
   - Add proper error handling and logging
   - Test with real devices

4. **Monitoring**
   - Track API response times
   - Log authentication failures
   - Monitor sync success rate

---

## 8) Documentation Links

- **Full API Docs:** `http://your-backend:8000/api/swagger/`
- **Production Guide:** See `GUIA_PRODUCAO.md`
- **Test Guide:** See `GUIA_TESTES_PRATICOS.md`

---

**Last Updated:** November 13, 2025  
**Status:** ✅ Ready for Flutter Integration
