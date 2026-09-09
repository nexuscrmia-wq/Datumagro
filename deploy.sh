#!/usr/bin/env bash
# Deploy DatumAgro → Railway
#
# Remotes:
#   origin  → git@github-nexuscrmia:nexuscrmia-wq/Datumagro.git  (backup/source-of-truth)
#   deploy  → git@github.com:victor226942-web/datumagro-backend.git  (conectado ao Railway)
#
# Uso: ./deploy.sh
# Requisito: branch local deve estar em main e sem alterações pendentes.

set -e

BRANCH="main"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERRO: existem alterações não commitadas. Faça commit antes de deployar."
    exit 1
fi

CURRENT=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT" != "$BRANCH" ]; then
    echo "ERRO: você está em '$CURRENT'. Mude para '$BRANCH' antes de deployar."
    exit 1
fi

echo "==> Push para origin (nexuscrmia-wq/Datumagro)..."
git push origin "$BRANCH"

echo "==> Push para deploy (victor226942-web/datumagro-backend → Railway)..."
git push deploy "$BRANCH"

echo ""
echo "Deploy enviado. Railway iniciará redeploy automaticamente."
echo "Verifique em: https://datumagro-web-production.up.railway.app/api/versao/"
