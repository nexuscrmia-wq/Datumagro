**Resumo Pendências Frontend e Mercado**

- **Objetivo:**: Resumir o que falta para conectar o backend ao frontend e o que é necessário para levar o aplicativo ao mercado.

**Conexão com o Frontend**
- **Endpoints:**: Validar que todos os endpoints necessários estejam implementados e documentados (ex.: rotas em `datumagro/urls.py`).
- **Documentação da API:**: Gerar/atualizar documentação (OpenAPI/Swagger / README de endpoints) para facilitar consumo pelo frontend e Flutter.
- **CORS:**: Conferir configuração de CORS em `settings.py` para permitir requisições do domínio/hosts do frontend e apps mobile.
- **Autenticação:**: Definir e documentar método de autenticação (JWT/OAuth2/session). Garantir endpoints de login/refresh/logout e exemplos no cliente.
- **Ambientes / Variáveis:**: Padronizar variáveis de ambiente e exemplos `.env.example` com `DEBUG`, `ALLOWED_HOSTS`, `API_URL`, `MEDIA_URL`, `STORAGE`.
- **Uploads / Static / Media:**: Verificar configuração de storage (S3/minio/local) e URLs públicas para assets solicitados pelo frontend.
- **Compatibilidade Flutter:**: Revisar payloads/contratos com os diretórios `flutter/` e `mobile_flutter/` (tipos, formatos de data, status codes).
- **Real-time / WebSockets (se aplicável):**: Confirmar suporte e roteamento para WebSockets/Channels se o app usar notificações em tempo real.
- **Tratamento de Erros:**: Padronizar resposta de erro (códigos, mensagens) para que o frontend exiba feedback consistente.
- **Rate Limiting e Caching:**: Avaliar necessidade de rate limits e headers/cache para performance.

**O que falta para levar o aplicativo ao mercado**
- **Infraestrutura de Produção:**: Definir provedor (Render, Heroku, AWS, GCP), Dockerfile/imagem e scripts de deploy (`Procfile`/`runtime.txt` já presentes — validar).
- **CI/CD:**: Configurar pipeline para testes, lint e deploy automático (GitHub Actions / Render Deploy). Incluir passos: instalar dependências, rodar `pytest`, migrar DB, rodar colet static.
- **Segurança:**: Habilitar HTTPS/SSL, revisar `SECRET_KEY` e armazenamento de segredos (Vault, secrets manager), revisar dependências por vulnerabilidades.
- **Backups e DB:**: Políticas de backup para banco de dados (agendamento), plano de restauração e migrações seguras.
- **Observabilidade:**: Configurar logs centralizados e monitoramento (Sentry para erros, Prometheus/Grafana para métricas, alertas).
- **Testes:**: Cobertura mínima: testes unitários, testes de integração de API, smoke tests e testes E2E do fluxo crítico (login, compra/ação principal).
- **Escalabilidade:**: Ajustes para suportar aumento de carga (pool DB, workers Celery, auto-scale settings), e limites de recursos.
- **Políticas legais e privacidade:**: Política de privacidade, termos de uso, conformidade LGPD (tratamento de dados pessoais) e mecanismo de consentimento quando aplicável.
- **Requisitos de App Stores (se mobile):**: Ajustes para publicação (ícones, telas, política de privacidade, builds assinados, integração com serviços terceiros como analytics e crash reporting).
- **Onboarding e Documentação:**: Documentação para usuários e equipe (README de deploy, guias para integração frontend, API reference, changelog).
- **Suporte e Operação:**: Definir processos de incident response, suporte ao usuário, canais de comunicação e SLA para correções críticas.

**Passos imediatos recomendados**
- **Prioridade alta:**: Criar/atualizar documentação OpenAPI e `README` de integração para frontend.
- **Prioridade alta:**: Verificar e ajustar CORS e auth flows; entregar exemplos de requests para o time frontend.
- **Prioridade média:**: Criar pipeline CI simples que rode `pytest` e checks de lint.
- **Prioridade média:**: Preparar `Dockerfile` e instruções de deploy (ex.: `Procfile` ou `render.yaml`) para ambiente de staging.
- **Prioridade baixa:**: Integrar Sentry/monitoramento e configurar backups automáticos para o banco.

**Arquivos/locais para verificar rapidamente**
- `datumagro/settings.py` — CORS, DEBUG, ALLOWED_HOSTS, storage, auth
- `datumagro/urls.py` — endpoints e roteamento
- `manage.py` / `Procfile` / `runtime.txt` — comandos de execução/produção
- `requirements.txt` — dependências e versões
- `flutter/` e `mobile_flutter/` — clientes que consumirão a API

Se quiser, eu posso: gerar a `OpenAPI` básica a partir dos serializers/rotas, criar um `README` de integração para o frontend, ou preparar um `Dockerfile` + `github-actions` CI inicial. Qual ação prefere que eu faça primeiro?
