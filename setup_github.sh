#!/bin/bash
# Script para facilitar setup do GitHub e push para Render

set -o errexit

echo "🚀 DatumAgro - GitHub Setup Script"
echo "===================================="
echo ""

# 1. Verificar se Git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado. Instale com: sudo apt install git"
    exit 1
fi

echo "✅ Git encontrado"
echo ""

# 2. Configurar Git se necessário
if [ -z "$(git config --global user.name)" ]; then
    echo "📝 Configurando Git..."
    read -p "Digite seu nome: " git_name
    read -p "Digite seu email: " git_email
    
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
    echo "✅ Git configurado"
    echo ""
fi

# 3. Inicializar repositório Git
if [ ! -d .git ]; then
    echo "📦 Inicializando repositório Git..."
    git init
    git branch -M main
    echo "✅ Repositório inicializado"
    echo ""
fi

# 4. Adicionar remote
read -p "Digite a URL do repositório GitHub (ex: https://github.com/seu-usuario/DatumAgro.git): " github_url

if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' já existe. Atualizando..."
    git remote set-url origin "$github_url"
else
    echo "📍 Adicionando remote..."
    git remote add origin "$github_url"
fi

echo "✅ Remote configurado: $github_url"
echo ""

# 5. Adicionar arquivos
echo "📝 Adicionando arquivos ao Git..."
git add .
echo "✅ Arquivos adicionados"
echo ""

# 6. Criar commit
echo "💾 Criando commit inicial..."
git commit -m "🚀 Deploy inicial - Backend DatumAgro com todas as melhorias globais

- ✅ Dependências: Django, DRF, Redis, PostgreSQL
- ✅ Performance: Cache Redis, Query optimization
- ✅ Segurança: JWT, Rate limiting, CORS
- ✅ Logging: JSON profissional
- ✅ Módulo: Logística (Porto do Açu)
- ✅ Ready for Render.com deployment" || echo "⚠️  Commit pode ter falhado (pode já existir)"

echo ""

# 7. Push para GitHub
echo "📤 Enviando para GitHub (main)..."
git push -u origin main

echo ""
echo "✅ GitHub setup completo!"
echo ""
echo "📋 Próximas etapas:"
echo "1. Acesse https://render.com/"
echo "2. Crie uma nova Web Service"
echo "3. Conecte ao repositório GitHub"
echo "4. Siga as instruções do GUIA_DEPLOY_RENDER.md"
echo ""
echo "🎉 Sucesso!"
