#!/bin/bash

##############################################################################
# 🚀 DEPLOY DATUMAGRO NO RENDER.COM - SCRIPT AUTOMATIZADO
#
# Este script automatiza o deploy completo do DatumAgro no Render.com
#
# Pré-requisitos:
# 1. Conta no Render.com criada
# 2. Repositório GitHub criado e conectado
# 3. Chaves API do Render configuradas (opcional)
#
# Uso:
#   ./deploy_render.sh
#
##############################################################################

set -e

echo "================================================"
echo "🚀 INICIANDO DEPLOY DATUMAGRO NO RENDER.COM"
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ] || [ ! -f "render.yaml" ]; then
    log_error "Este script deve ser executado na raiz do projeto DatumAgro"
    log_error "Arquivos manage.py e render.yaml são necessários"
    exit 1
fi

log_info "Verificando arquivos de configuração..."

# Verificar arquivos necessários
REQUIRED_FILES=("requirements.txt" "render.yaml" "Dockerfile" "runtime.txt" "Procfile")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "Arquivo obrigatório não encontrado: $file"
        exit 1
    fi
done

log_success "Todos os arquivos de configuração estão presentes"

# Verificar se o projeto está limpo para commit
if [ -n "$(git status --porcelain)" ]; then
    log_warning "Há mudanças não commitadas no repositório"
    log_info "Fazendo commit das mudanças pendentes..."

    git add .
    git commit -m "feat: Preparação para deploy Render.com - $(date)" || true
fi

# Verificar se temos um repositório remoto
if ! git remote get-url origin > /dev/null 2>&1; then
    log_error "Nenhum repositório remoto configurado"
    log_info "Configure um repositório GitHub primeiro:"
    echo ""
    echo "1. Crie um repositório no GitHub: https://github.com/new"
    echo "2. Configure o remote:"
    echo "   git remote add origin https://github.com/SEU_USERNAME/SEU_REPO.git"
    echo "3. Execute novamente: ./deploy_render.sh"
    exit 1
fi

log_info "Fazendo push para GitHub..."
git push origin main 2>/dev/null || git push origin master 2>/dev/null || {
    log_error "Falha ao fazer push para GitHub"
    log_info "Verifique se o repositório remoto está correto e você tem permissões"
    exit 1
}

log_success "Código enviado para GitHub com sucesso!"

echo ""
echo "================================================"
echo "🎯 PRÓXIMOS PASSOS NO RENDER.COM"
echo "================================================"
echo ""
echo "1. ACESSE: https://render.com"
echo "2. FAÇA LOGIN na sua conta"
echo "3. CLIQUE: 'New +' → 'Web Service'"
echo "4. CONECTE SEU REPOSITÓRIO GITHUB:"
echo "   - Procure por: $(basename $(git remote get-url origin) .git)"
echo "   - Conecte o repositório"
echo ""
echo "5. CONFIGURE O SERVIÇO:"
echo "   - Name: datumagro-api"
echo "   - Environment: Docker"
echo "   - Branch: main (ou master)"
echo "   - Build Command: ./build.sh"
echo "   - Start Command: gunicorn datumagro.wsgi:application --bind 0.0.0.0:8000 --workers 3"
echo ""
echo "6. VARIÁVEIS DE AMBIENTE (Environment):"
echo "   SECRET_KEY: $(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo 'gere-uma-chave-secreta')"
echo "   DEBUG: False"
echo "   ENVIRONMENT: production"
echo "   DATABASE_URL: [Configure PostgreSQL no Render primeiro]"
echo "   REDIS_URL: [Configure Redis no Render primeiro]"
echo ""
echo "7. BANCO DE DADOS:"
echo "   - Vá para: https://render.com/new/database"
echo "   - Crie: PostgreSQL"
echo "   - Copie a DATABASE_URL para as variáveis de ambiente"
echo ""
echo "8. REDIS (OPCIONAL):"
echo "   - Vá para: https://render.com/new/redis"
echo "   - Crie: Redis"
echo "   - Copie a REDIS_URL para as variáveis de ambiente"
echo ""
echo "9. CLIQUE: 'Create Web Service'"
echo ""
echo "================================================"
echo "⏱️  TEMPO ESTIMADO: 10-15 minutos"
echo "================================================"
echo ""
log_success "Script concluído! Siga os passos acima no Render.com"
echo ""
log_info "Após o deploy, teste os endpoints:"
echo "  curl https://your-app-name.onrender.com/api/health/"
echo "  curl https://your-app-name.onrender.com/api/token/ (para login)"
echo ""
echo "Para conectar o Flutter app, atualize a base URL para:"
echo "  https://your-app-name.onrender.com"