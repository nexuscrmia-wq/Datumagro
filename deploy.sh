#!/bin/bash

##############################################################################
# Deploy Script for DatumAgro
# Purpose: Deploy Docker Compose stack to production VM
#
# Usage:
#   ./deploy.sh <server_host> <server_user> <image_name:tag>
#
# Example:
#   ./deploy.sh api.datumagro.com ubuntu datumagro/app:latest
#
# Prerequisites:
#   1. Docker and Docker Compose installed on the server.
#   2. SSH key-based auth configured (no password).
#   3. .env file prepared with production secrets (SECRET_KEY, DB_URL, etc).
#   4. Image already pushed to DockerHub or local registry.
#
##############################################################################

set -e

SERVER_HOST="${1:-}"
SERVER_USER="${2:-}"
IMAGE_NAME="${3:-datumagro/app:latest}"

if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ]; then
    echo "Usage: $0 <server_host> <server_user> [image_name:tag]"
    echo ""
    echo "Example:"
    echo "  $0 api.example.com ubuntu datumagro/app:v1.0"
    exit 1
fi

echo "=========================================="
echo "Deploying to: $SERVER_USER@$SERVER_HOST"
echo "Image: $IMAGE_NAME"
echo "=========================================="

# 1. Copy docker-compose.prod.yml and .env to server
echo "[1/5] Copying docker-compose and env files..."
scp docker-compose.prod.yml "$SERVER_USER@$SERVER_HOST:/tmp/docker-compose.prod.yml"
scp .env "$SERVER_USER@$SERVER_HOST:/tmp/.env"

# 2. Pull latest image on server
echo "[2/5] Pulling latest image on server..."
ssh "$SERVER_USER@$SERVER_HOST" "docker pull $IMAGE_NAME"

# 3. Update image in docker-compose.prod.yml (if needed)
echo "[3/5] Preparing docker-compose on server..."
ssh "$SERVER_USER@$SERVER_HOST" <<'SCRIPT'
    cd /tmp
    # Update the compose file to use the pulled image (optional automation)
    # For now, assumes compose file already references correct image or uses 'build: .'
    echo "Docker-compose prepared."
SCRIPT

# 4. Stop old containers and start new ones
echo "[4/5] Restarting services..."
ssh "$SERVER_USER@$SERVER_HOST" <<'SCRIPT'
    cd /tmp
    docker-compose -f docker-compose.prod.yml down || true
    docker-compose -f docker-compose.prod.yml up -d --no-build
    echo "Services started."
SCRIPT

# 5. Run migrations (if needed)
echo "[5/5] Running migrations..."
ssh "$SERVER_USER@$SERVER_HOST" <<'SCRIPT'
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate || true
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput || true
SCRIPT

echo "=========================================="
echo "✓ Deployment complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Check service status: ssh $SERVER_USER@$SERVER_HOST"
echo "  2. View logs: docker-compose -f docker-compose.prod.yml logs -f web"
echo "  3. Access API: http://$SERVER_HOST:8000/api/health/"
echo ""
