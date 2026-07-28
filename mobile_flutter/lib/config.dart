// IP da máquina na rede local — celular físico usa esse endereço para alcançar o backend
const String kApiBaseUrlEmulator =
    String.fromEnvironment('BASE_URL', defaultValue: 'http://192.168.0.11:8000');
