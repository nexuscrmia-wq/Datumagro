// Em produção o BASE_URL é injetado via --dart-define=BASE_URL=https://...
// O default aponta para o Railway para garantir que builds sem --dart-define
// nunca enviem dados em HTTP para uma máquina local de desenvolvimento.
const String kApiBaseUrlEmulator = String.fromEnvironment(
  'BASE_URL',
  defaultValue: 'https://datumagro-web-production.up.railway.app',
);

// Versão do APK instalado — atualizar a cada release junto com pubspec.yaml
const String kAppVersion = '1.6.9';
