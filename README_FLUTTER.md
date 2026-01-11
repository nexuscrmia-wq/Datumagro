DatumAgro — Flutter integration notes

This document shows the recommended settings and minimal Dart snippets to connect a Flutter app to the DatumAgro development API.

1) Base URLs (development)
- Android emulator: http://10.0.2.2:8000
- iOS simulator: http://localhost:8000
- Device on same network: http://<HOST_IP>:8000  (find host IP with `hostname -I`)

We run Django devserver with:

```bash
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

2) Important server-side settings (already configured):
- JWT via Simple JWT: endpoints available at `/api/token/` and `/api/token/refresh/` and the custom users viewset at `/api/usuarios/usuarios/`.
- CORS: `corsheaders` middleware must be present. For development CORS_ALLOW_ALL_ORIGINS may be True; in production restrict origins.
- If using Android emulator, make sure `ALLOWED_HOSTS` and CORS allow `10.0.2.2` (done in settings).

3) Endpoints most relevant for Flutter
- POST /api/usuarios/usuarios/registrar/  -> register (returns `access` and `refresh` tokens)
- POST /api/usuarios/usuarios/login/      -> login (returns `access` and `refresh` tokens)
- POST /api/token/                        -> alternative token obtain (SimpleJWT)
- POST /api/token/refresh/                -> refresh token
- Use `Authorization: Bearer <access>` header for protected endpoints.

4) Minimal Dart snippets
- Add `http` and `flutter_secure_storage` to pubspec.yaml:

  dependencies:
    http: ^0.13.0
    flutter_secure_storage: ^8.0.0

- Login and storing tokens (example):

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage();
final baseUrl = 'http://10.0.2.2:8000'; // adjust per platform

Future<bool> login(String email, String password) async {
  final resp = await http.post(Uri.parse('$baseUrl/api/usuarios/usuarios/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}));

  if (resp.statusCode == 200) {
    final body = jsonDecode(resp.body);
    final access = body['access'];
    final refresh = body['refresh'];
    await storage.write(key: 'access', value: access);
    await storage.write(key: 'refresh', value: refresh);
    return true;
  }
  return false;
}
```

- Making authenticated requests with automatic refresh (simplified):

```dart
Future<http.Response> authGet(String path) async {
  String? access = await storage.read(key: 'access');
  final headers = {'Content-Type': 'application/json'};
  if (access != null) headers['Authorization'] = 'Bearer $access';

  final resp = await http.get(Uri.parse('$baseUrl$path'), headers: headers);

  if (resp.statusCode == 401) {
    // try refresh once
    final refreshed = await tryRefresh();
    if (refreshed) {
      access = await storage.read(key: 'access');
      headers['Authorization'] = 'Bearer $access';
      return await http.get(Uri.parse('$baseUrl$path'), headers: headers);
    }
  }

  return resp;
}

Future<bool> tryRefresh() async {
  final refresh = await storage.read(key: 'refresh');
  if (refresh == null) return false;
  final resp = await http.post(Uri.parse('$baseUrl/api/token/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': refresh}));
  if (resp.statusCode == 200) {
    final body = jsonDecode(resp.body);
    await storage.write(key: 'access', value: body['access']);
    return true;
  }
  return false;
}
```

5) Troubleshooting
- If emulator cannot reach server: ensure dev machine firewall allows inbound to port 8000 or use `python manage.py runserver 0.0.0.0:8000` and use host IP.
- If CORS errors appear in web builds, confirm `corsheaders.middleware.CorsMiddleware` is present and origin is allowed.

6) Next steps
- Consider implementing a small `/health` endpoint that returns 200 for the Flutter app to probe before heavy operation.
- Add client-side retries and robust refresh logic.

---
File created by the local integration helper. Adjust baseUrl in Flutter per your testing platform.