#!/bin/bash

# =============================================
# 🧪 TESTE COMPLETO DO DATUMAGRO 100%
# =============================================

BASE_URL="http://localhost:8000"
ADMIN_EMAIL="admin@datumagro.com"
ADMIN_PASS="Admin123!"

echo "🔗 Testando DatumAgro em: $BASE_URL"
echo "================================================"

# 1. Health check
echo ""
echo "1️⃣  Health Check..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health/")
if [ "$HEALTH" = "200" ]; then
    echo "✅ Health: OK ($HEALTH)"
else
    echo "⚠️  Health: $HEALTH (esperado 200)"
fi

# 2. Swagger
echo ""
echo "2️⃣  Swagger Documentation..."
SWAGGER=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/swagger/")
if [ "$SWAGGER" = "200" ]; then
    echo "✅ Swagger: OK ($SWAGGER)"
else
    echo "⚠️  Swagger: $SWAGGER (esperado 200)"
fi

# 3. Login
echo ""
echo "3️⃣  Autenticação..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASS\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ ! -z "$TOKEN" ] && [ ${#TOKEN} -gt 10 ]; then
    echo "✅ Login: OK - Token obtido"
else
    echo "⚠️  Login falhou"
    echo "Response: $LOGIN_RESPONSE"
    TOKEN=""
fi

# 4. Admin page
echo ""
echo "4️⃣  Admin Dashboard..."
ADMIN=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/")
if [ "$ADMIN" = "302" ] || [ "$ADMIN" = "200" ]; then
    echo "✅ Admin: Acessível ($ADMIN)"
else
    echo "⚠️  Admin: $ADMIN"
fi

# 5. Listar animais
if [ ! -z "$TOKEN" ]; then
    echo ""
    echo "5️⃣  API - Listar Animais..."
    ANIMALS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/cadastros/animais/" \
      -H "Authorization: Bearer $TOKEN")
    if [ "$ANIMALS" = "200" ]; then
        echo "✅ Animais: OK ($ANIMALS)"
    else
        echo "⚠️  Animais: $ANIMALS"
    fi
fi

echo ""
echo "================================================"
echo "✅ TESTES CONCLUÍDOS!"
echo "================================================"
echo ""
echo "🌐 Acesse:"
echo "   📊 Swagger: $BASE_URL/api/swagger/"
echo "   🔐 Admin: $BASE_URL/admin/"
echo "   📈 Health: $BASE_URL/api/health/"
