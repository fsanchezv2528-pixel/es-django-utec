#!/bin/sh
# start.sh — arranque del servicio Docker en Render (W12)
# Corre migraciones, crea grupos y superusuario, y luego inicia Gunicorn.
set -e

echo "==> migrate"
python manage.py migrate --noinput

echo "==> crear_grupos"
python manage.py crear_grupos

echo "==> createsuperuser (si hay variables DJANGO_SUPERUSER_*)"
python manage.py createsuperuser --noinput || true

echo "==> gunicorn"
exec gunicorn core.wsgi --bind 0.0.0.0:${PORT:-8000}
