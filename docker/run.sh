#!/bin/bash

# 1. Exit immediately if a command exits with a non-zero status
set -e

cd src
echo "🔍 Checking for Django migrations..."
# Optional: Uncomment if you want auto-migrations on startup
python manage.py migrate --noinput

echo "🗂️   Collecting static files..."
python manage.py collectstatic --noinput

echo "⚡ Starting Django server..."
# Run Django in the foreground
exec gunicorn settings.wsgi:application --bind 0.0.0.0:8000
