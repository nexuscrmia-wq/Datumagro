web: python manage.py migrate --noinput && gunicorn datumagro.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --worker-class sync --timeout 60 --access-logfile -
