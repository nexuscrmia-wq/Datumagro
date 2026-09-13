// Em produção o BASE_URL é injetado via --dart-define=BASE_URL=https://...
// O default usa o domínio customizado (datumagro.com.br) em vez do domínio
// interno do Railway — assim o app não quebra se o domínio interno mudar.
const String kApiBaseUrlEmulator = String.fromEnvironment(
  'BASE_URL',
  defaultValue: 'https://datumagro.com.br',
);

// Versão do APK instalado — atualizar a cada release junto com pubspec.yaml
const String kAppVersion = '1.7.0';
