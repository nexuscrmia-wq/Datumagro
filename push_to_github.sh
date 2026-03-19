#!/bin/bash

##############################################################################
# 🚀 SCRIPT AUTOMATIZADO PARA PUSH NO GITHUB
#
# Este script configura o repositório remoto e faz push automático
#
# Uso:
#   ./push_to_github.sh SEU_USERNAME
#
# Exemplo:
#   ./push_to_github.sh victor-emanuel
#
##############################################################################

set -e

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

# Verificar parâmetro
if [ $# -eq 0 ]; then
    log_error "Uso: $0 SEU_USERNAME_GITHUB"
    log_info "Exemplo: $0 victor-emanuel"
    log_info ""
    log_info "Primeiro crie o repositório em: https://github.com/new"
    log_info "Nome: DatumAgro"
    log_info "Visibilidade: Público"
    exit 1
fi

USERNAME="$1"
REPO_URL="https://github.com/$USERNAME/DatumAgro.git"

log_info "Configurando push para: $REPO_URL"

# Verificar se estamos no diretório correto
if [ ! -d ".git" ] || [ ! -f "manage.py" ]; then
    log_error "Execute este script na raiz do projeto DatumAgro"
    exit 1
fi

# Verificar se há commits para push
if [ -z "$(git log --oneline -1)" ]; then
    log_error "Nenhum commit encontrado. Faça commit primeiro:"
    log_info "git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Configurar remote
log_info "Configurando repositório remoto..."
git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"

# Verificar se o repositório existe
log_info "Verificando conexão com GitHub..."
if ! git ls-remote --heads origin main >/dev/null 2>&1 && ! git ls-remote --heads origin master >/dev/null 2>&1; then
    log_error "Repositório não encontrado ou sem acesso"
    log_info "Certifique-se de que:"
    log_info "1. O repositório '$USERNAME/DatumAgro' existe no GitHub"
    log_info "2. Você tem permissão para fazer push"
    log_info "3. Está logado no GitHub"
    exit 1
fi

# Fazer push
log_info "Fazendo push do código..."
if git push -u origin main 2>/dev/null; then
    BRANCH="main"
elif git push -u origin master 2>/dev/null; then
    BRANCH="master"
else
    log_error "Falha ao fazer push"
    log_info "Possíveis soluções:"
    log_info "1. Verifique suas credenciais GitHub"
    log_info "2. Use token de acesso pessoal se necessário"
    log_info "3. Execute: git config --global credential.helper store"
    exit 1
fi

log_success "🎉 PUSH REALIZADO COM SUCESSO!"
echo ""
echo "================================================"
echo "📤 CÓDIGO ENVIADO PARA GITHUB"
echo "================================================"
echo ""
echo "🌐 URL do Repositório:"
echo "   https://github.com/$USERNAME/DatumAgro"
echo ""
echo "📊 Status do Push:"
echo "   ✅ Branch: $BRANCH"
echo "   ✅ Arquivos enviados"
echo "   ✅ Histórico preservado"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. 🚀 DEPLOY BACKEND:"
echo "   Seguir DEPLOY_FINAL_README.md"
echo ""
echo "2. 📱 BUILD APPS:"
echo "   cd mobile_flutter"
echo "   flutter build apk --dart-define=BASE_URL=https://SEU_APP.onrender.com"
echo "   flutter build ios --dart-define=BASE_URL=https://SEU_APP.onrender.com"
echo ""
echo "3. 🏪 PUBLICAR STORES:"
echo "   - Google Play: https://play.google.com/console/"
echo "   - App Store: https://developer.apple.com/"
echo ""
echo "================================================"
log_success "DatumAgro está agora público no GitHub! 🚀"