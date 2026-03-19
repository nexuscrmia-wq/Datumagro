#!/bin/bash

##############################################################################
# 🚀 SCRIPT DE PREPARAÇÃO PARA PUBLICAÇÃO NO GITHUB
#
# Este script prepara o projeto DatumAgro para publicação no GitHub
# e nas stores móveis (App Store e Play Store).
#
# O que faz:
# - Remove arquivos temporários
# - Limpa cache e arquivos de desenvolvimento
# - Verifica se não há dados sensíveis
# - Prepara estrutura final para commit
#
##############################################################################

set -e

echo "================================================"
echo "🚀 PREPARANDO DATUMAGRO PARA PUBLICAÇÃO"
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
if [ ! -f "manage.py" ] || [ ! -f "mobile_flutter/pubspec.yaml" ]; then
    log_error "Este script deve ser executado na raiz do projeto DatumAgro"
    exit 1
fi

log_info "Verificando estrutura do projeto..."

# 1. LIMPAR ARQUIVOS TEMPORÁRIOS
echo ""
log_info "🧹 Limpando arquivos temporários..."

# Arquivos Python
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Arquivos Flutter
if [ -d "mobile_flutter" ]; then
    cd mobile_flutter
    flutter clean >/dev/null 2>&1 || true
    rm -rf build/ .dart_tool/ >/dev/null 2>&1 || true
    cd ..
fi

# Logs e arquivos temporários
rm -f *.log server.log runserver.log
rm -f smoke_tests_report.json smoke_verbose_report.json
rm -rf logs/ 2>/dev/null || true

log_success "Arquivos temporários removidos"

# 2. VERIFICAR SEGURANÇA
echo ""
log_info "🔒 Verificando segurança..."

# Verificar se .env não será commitado
if git ls-files | grep -q "^\.env$"; then
    log_error "ARQUIVO .env ESTÁ SENDO TRACKED PELO GIT!"
    log_error "Execute: git rm --cached .env"
    exit 1
fi

# Verificar se há chaves hardcoded
if grep -r "API_KEY\|SECRET\|TOKEN.*=.*["'][^"']*["']" mobile_flutter/lib/ >/dev/null 2>&1; then
    log_warning "Possíveis chaves hardcoded encontradas no Flutter app"
    log_info "Verifique manualmente os arquivos em mobile_flutter/lib/"
fi

# Verificar se há senhas no código Python
if grep -r "PASSWORD\|SECRET.*=.*["'][^"']*["']" datumagro/ >/dev/null 2>&1; then
    log_warning "Possíveis senhas hardcoded encontradas no backend"
    log_info "Verifique manualmente os arquivos em datumagro/"
fi

log_success "Verificações de segurança concluídas"

# 3. PREPARAR ESTRUTURA FINAL
echo ""
log_info "📁 Preparando estrutura final..."

# Criar .env.example se não existir
if [ ! -f ".env.example" ]; then
    log_warning ".env.example não encontrado, criando..."
    cp .env.example.backup .env.example 2>/dev/null || {
        cat > .env.example << 'EOF'
# Copie este arquivo para .env e preencha com suas configurações
SECRET_KEY=your-secret-key-here
DEBUG=False
ENVIRONMENT=production
DATABASE_URL=postgres://user:password@host:port/database
REDIS_URL=redis://host:port
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EOF
    }
fi

# Verificar se README principal existe
if [ ! -f "README.md" ]; then
    log_warning "README.md não encontrado"
fi

# Verificar se há documentação de deploy
if [ ! -f "DEPLOY_FINAL_README.md" ]; then
    log_warning "DEPLOY_FINAL_README.md não encontrado"
fi

log_success "Estrutura preparada"

# 4. VERIFICAÇÃO FINAL
echo ""
log_info "✅ Verificação final..."

# Verificar arquivos críticos
REQUIRED_FILES=("requirements.txt" "Dockerfile" "render.yaml" "mobile_flutter/pubspec.yaml")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "Arquivo obrigatório não encontrado: $file"
        exit 1
    fi
done

# Verificar se há arquivos grandes que não deveriam ir para Git
LARGE_FILES=$(find . -type f -size +50M 2>/dev/null | grep -v ".git" | grep -v "__pycache__" | grep -v "venv" | head -5)
if [ -n "$LARGE_FILES" ]; then
    log_warning "Arquivos grandes encontrados:"
    echo "$LARGE_FILES"
    log_info "Considere adicionar ao .gitignore se não forem necessários"
fi

log_success "Verificação final concluída"

# 5. STATUS FINAL
echo ""
echo "================================================"
echo "🎉 PROJETO PRONTO PARA PUBLICAÇÃO!"
echo "================================================"
echo ""
echo "✅ Arquivos temporários removidos"
echo "✅ Segurança verificada"
echo "✅ Estrutura preparada"
echo "✅ Arquivos obrigatórios presentes"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. 📤 FAZER COMMIT:"
echo "   git add ."
echo "   git commit -m 'feat: MVP completo pronto para publicação'"
echo ""
echo "2. 📤 CRIAR REPOSITÓRIO GITHUB:"
echo "   https://github.com/new"
echo "   Nome: DatumAgro"
echo "   Visibilidade: Público"
echo ""
echo "3. 📤 FAZER PUSH:"
echo "   git remote add origin https://github.com/SEU_USERNAME/DatumAgro.git"
echo "   git push -u origin main"
echo ""
echo "4. 🚀 DEPLOY BACKEND:"
echo "   Seguir DEPLOY_FINAL_README.md"
echo ""
echo "5. 📱 PUBLICAR APP:"
echo "   flutter build apk --dart-define=BASE_URL=https://SEU_APP.onrender.com"
echo "   flutter build ios --dart-define=BASE_URL=https://SEU_APP.onrender.com"
echo ""
echo "================================================"
log_success "Script concluído com sucesso!"
echo ""
log_info "Tempo estimado para publicação: 2-3 horas"