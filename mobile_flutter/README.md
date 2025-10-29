DatumAgro - Mobile (Flutter)

Este diretório contém o scaffold inicial do aplicativo Flutter offline-first (MVP).

Pré-requisitos:
- Flutter SDK instalado

Como rodar (desenvolvimento):

1. Entre no diretório do app:

```bash
cd mobile_flutter
```

2. Instale dependências e gere código do Drift:

```bash
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

3. Rode no emulador ou dispositivo:

```bash
flutter run
```

O scaffold inicial inclui:
- `lib/main.dart` com uma tela inicial
- `pubspec.yaml` com dependências (http, connectivity_plus, drift)

Próximos passos que eu posso implementar:
- Modelos Drift para `animals` e `sync_queue` e repositório local
- Tela de login + autenticação com token DRF
- Implementação de sync automático quando a conectividade for detectada
- Endpoint Django `/api/sync/` foi adicionado (stub) no backend para sincronização

Observações de desenvolvimento
- O scaffold usa `drift` para o banco local. Depois de instalar as dependências, execute o `build_runner` para gerar o código (`database.g.dart`).
- O serviço de sync (`lib/services/sync_service.dart`) usa o endpoint `http://127.0.0.1:8000/api/cadastros/sync/` por padrão — em dispositivos físicos ou builds use a URL pública do seu servidor.
- O MVP atual implementa operações básicas: criar animal offline, enfileirar e sincronizar manualmente via botão. A sincronização automática por conexão será a próxima etapa.
 - No Android emulator use `http://10.0.2.2:8000/api/cadastros` para atingir o servidor local.
 - A sincronização automática foi implementada: o app escuta mudanças de conectividade e, quando volta online, dispara o sync (com debounce de 10s). O token é persistido com `flutter_secure_storage`.

Diga se quer que eu continue e eu implemento o banco local Drift e as telas do MVP.
