# Deployment & Monitoring Guide

## Overview
Este guia descreve como fazer deploy da aplicação DatumAgro em produção usando Docker Compose e monitorar com Sentry + Prometheus/Grafana.

## 1) Deploy em VM (Docker Compose + DockerHub)

### 1.1 Preparar servidor (Ubuntu 20.04+)
```bash
# SSH no servidor
ssh user@your-server.com

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Criar diretório para deploy
mkdir -p ~/datumagro && cd ~/datumagro
```

### 1.2 Preparar e executar deploy local
No seu computador (repositório):
```bash
# 1. Build e push de imagem
docker build -t datumagro/app:v1.0 .
docker login -u <usuario> -p <token>
docker push datumagro/app:v1.0

# 2. Preparar .env com segredos de produção
cp .env.example .env
# Editar .env com SECRET_KEY, DATABASE_URL, REDIS_URL, SENTRY_DSN, etc.
# IMPORTANTE: não commitar .env; manter segredos no `.env` local ou env vars do servidor.

# 3. Executar deploy via script
chmod +x deploy.sh
./deploy.sh your-server.com ubuntu datumagro/app:v1.0
# Ou manualmente:
scp docker-compose.prod.yml .env user@your-server.com:~/datumagro/
scp .github/secrets/docker-compose.prod.yml user@your-server.com:~/datumagro/
```

### 1.3 Iniciar serviços no servidor
```bash
# No servidor
cd ~/datumagro
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml logs -f web
```

## 2) Monitoramento com Sentry

### 2.1 Ativar Sentry
1. Criar conta em [sentry.io](https://sentry.io).
2. Criar novo projeto (Django).
3. Copiar `SENTRY_DSN`.
4. Adicionar ao `.env` de produção:
   ```
   SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
   SENTRY_TRACES_SAMPLE_RATE=0.1
   SENTRY_SEND_PII=False
   ```
5. Reiniciar app:
   ```bash
   docker-compose -f docker-compose.prod.yml restart web
   ```

### 2.2 Testar Sentry (dev)
```python
# Em uma shell Django:
python manage.py shell
import sentry_sdk
sentry_sdk.capture_message("Test from shell", level="info")
# Verificar no painel Sentry (alguns segundos de delay)
```

## 3) Monitoramento com Prometheus + Grafana (opcional)

### 3.1 Stack de monitoramento (local)
Crie `docker-compose.monitoring.yml`:
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - '9090:9090'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - '3000:3000'
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - '9100:9100'

volumes:
  prometheus_data:
  grafana_data:
```

### 3.2 Configurar Prometheus
Arquivo `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'gunicorn'
    static_configs:
      - targets: ['localhost:8000']  # se expor métricas
```

### 3.3 Rodar stack
```bash
docker-compose -f docker-compose.monitoring.yml up -d
# Acessar Prometheus: http://localhost:9090
# Acessar Grafana: http://localhost:3000 (admin/admin)
```

## 4) Checklist de produção

- [ ] Imagem Docker buildada e testada localmente.
- [ ] `SECRET_KEY` seguro (não hardcoded).
- [ ] `DEBUG=False` em produção.
- [ ] `ALLOWED_HOSTS` correto (domínio de produção).
- [ ] `DATABASE_URL` aponta para DB de produção (Postgres recomendado).
- [ ] `REDIS_URL` configurado (cache e Celery).
- [ ] Certificado SSL/TLS configurado (nginx reverso proxy recomendado).
- [ ] SENTRY_DSN configurado para capturar erros.
- [ ] Backups automáticos do banco de dados.
- [ ] Rotação de logs configurada.
- [ ] Saúde da aplicação monitorada (healthcheck `/api/health/`).
- [ ] Plano de rollback documentado.

## 5) Troubleshooting

### Erro: "Permissão negada" ao SSH
```bash
# Garantir chave SSH correcta
ssh-copy-id -i ~/.ssh/id_rsa.pub user@your-server.com
```

### Erro: "Container exits with code 1"
```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs web
# Verificar variáveis de ambiente
docker-compose -f docker-compose.prod.yml config | grep SECRET_KEY
```

### Erro: "Database connection refused"
```bash
# Verificar Postgres está rodando
docker-compose -f docker-compose.prod.yml logs db
# Testar conexão
docker-compose -f docker-compose.prod.yml exec web psql $DATABASE_URL -c "SELECT 1"
```

### Erro: "Static files not collected"
```bash
# Rodar manualmente
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 6) Reverter deploy (rollback)

```bash
# Parar versão nova
docker-compose -f docker-compose.prod.yml down

# Voltar para tag anterior
docker pull datumagro/app:v0.9
# Editar docker-compose.prod.yml para usar v0.9
docker-compose -f docker-compose.prod.yml up -d
```

## 7) GitHub Actions CI/CD

O arquivo `.github/workflows/ci.yml` automatiza:
1. Testes (pytest)
2. Scan de segurança (bandit)
3. Build de imagem Docker
4. Push para DockerHub (se secrets configurados)

### Configurar GitHub Secrets
No GitHub (Settings → Secrets):
```
DOCKERHUB_USERNAME = <seu-user>
DOCKERHUB_TOKEN = <seu-token>
```

Após push para `main`, o workflow rodar automaticamente e fazer build+push da imagem.

## Contatos e escalação

- **Erro no deploy**: Verificar logs (`docker-compose logs`), ou contatar DevOps.
- **Erro na aplicação**: Verificar Sentry (erros em produção) ou logs estruturados (JSON logs).
- **Performance**: Monitorar Prometheus/Grafana ou solicitar relatório de métricas.

---

**Última atualização**: 2025-11-20
