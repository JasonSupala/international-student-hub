#!/bin/sh
# entrypoint.sh — Run migrations then start the server
# This script runs every time the container starts.

set -e  # Exit immediately if any command fails

echo "==> Waiting for PostgreSQL to be ready..."
# Use pg_isready (comes with libpq-dev) — much lighter than loading Django
until pg_isready -h "${PGHOST:-db}" -p "${PGPORT:-5432}" -U "${PGUSER:-ish_user}" -d "${PGDATABASE:-ish_db}" > /dev/null 2>&1; do
    echo "    PostgreSQL not ready yet, retrying in 2s..."
    sleep 2
done
echo "    PostgreSQL is ready ✓"

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
# Use gunicorn in production; Django's runserver in development (overridden by docker-compose)
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -