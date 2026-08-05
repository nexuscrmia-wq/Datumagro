#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Creating superuser (se não existir)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '${DJANGO_SUPERUSER_EMAIL:-nexuscrmia@gmail.com}'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password='${DJANGO_SUPERUSER_PASSWORD:-DatumAgro@2026}', first_name='Victor', last_name='Admin')
    print('Superuser criado: ' + email)
else:
    print('Superuser já existe.')
" || echo "Aviso: criação do superuser falhou (não crítico)"

echo "==> Starting Gunicorn..."
exec gunicorn datumagro.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
