**Segurança & Conformidade (LGPD) — Checklist e passos práticos**

Este documento descreve ações imediatas e recomendações para preparar o backend e o produto para produção, considerando segurança operacional e conformidade com proteção de dados (LGPD).

1) Gestão de segredos e chaves
- **Não** commitar `SECRET_KEY`, keystores, certificados ou `key.properties` no repositório.
- Usar variáveis de ambiente gerenciadas pelo provedor (Render/GCP/AWS Secrets Manager) ou CI secrets.
- Forneça `.env.example` (já incluído) para documentar variáveis necessárias.

2) HTTPS e transporte seguro
- Habilitar HTTPS em produção (certificados válidos). Usar `SECURE_SSL_REDIRECT`, cookies seguros e `SECURE_HSTS_SECONDS` (já presente em `settings.py`).
- Se atrás de proxy/load balancer, garantir `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`.

3) Monitoramento e resposta a incidentes
- Integrar Sentry (ou similar) para capturar erros em produção. Configurar `SENTRY_DSN` via env var.
- Configurar alertas e runbook de incident response.

4) Proteção de dados / LGPD
- Inventariar dados pessoais coletados e armazenados (usuários, telefones, documentos).
- Implementar políticas de retenção (ex.: eliminar dados pessoais após X anos) e endpoints para requisições de acesso/remoção quando necessário.
- Publicar Política de Privacidade e termos de uso; garantir link na Play Console / App Store.

5) Acesso e privilégios
- Usar gestão de acesso baseada em funções (RBAC) no admin e serviços críticos.
- Rotas administrativas protegidas por IP allowlist ou autenticação forte.

6) Backup e recuperação
- Agendar backups periódicos do banco e testar restore em ambiente separado.

7) Testes de segurança automáticos
- Incluir varredura de dependências (ex.: `pip-audit`, `safety`) no CI.
- Rodar `bandit` para análise estática de segurança no Python.

8) Hardening Django
- Forçar `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY` em produção.
- Verificar `X-Content-Type-Options`, `X-Frame-Options` e `Referrer-Policy` via middleware ou proxy.

9) Logs e PII
- Evitar logar dados sensíveis (senhas, tokens completos, dados pessoais desnecessários).
- Usar rotação de logs e retenção controlada.

10) Processo e documentação
- Documentar o plano de deploy, rollback e contatos de privacidade.
- Realizar avaliação de impacto (DPIA) se processar dados sensíveis em grande escala.

Passos imediatos (prioridade)
- 1: Mover segredos para secrets manager e criar `.env` a partir de `.env.example`.
- 2: Instalar `sentry-sdk` e configurar `SENTRY_DSN` no ambiente de staging/prod.
- 3: Adicionar scanners (`bandit`, `pip-audit`) no pipeline CI.
- 4: Verificar políticas de retenção de dados e criar endpoints para remoção/consulta conforme LGPD.

Recursos e links úteis
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- LGPD overview: (adicionar link da autoridade local)

Se quiser, eu posso:
- adicionar `bandit` e `pip-audit` ao CI (GitHub Actions) e criar jobs de segurança;
- configurar Sentry no `settings.py` (já adicionei inicialização condicional) e gerar instruções para ativação;
- criar um playbook de resposta a incidentes e template de Política de Privacidade.
