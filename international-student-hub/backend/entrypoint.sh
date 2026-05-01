#!/bin/sh
# entrypoint.sh — Wait for PostgreSQL, run migrations, start server
set -e

echo "==> Waiting for PostgreSQL to be ready..."

# Pure Python DB check — works without psql client binary installed
until python -c "
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.prod'))
import django
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    sys.exit(0)
except Exception as e:
    print(f'Not ready: {e}', flush=True)
    sys.exit(1)
" 2>/dev/null; do
    echo "    PostgreSQL not ready yet, retrying in 2s..."
    sleep 2
done

echo "    PostgreSQL is ready ✓"

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -