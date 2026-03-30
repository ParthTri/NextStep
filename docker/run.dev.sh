#!/bin/bash

# 1. Exit immediately if a command exits with a non-zero status
set -e

echo "🔍 Checking for Django migrations..."
# Optional: Uncomment if you want auto-migrations on startup
# python manage.py migrate --noinput

echo "⚡ Starting Django development server..."
# Run Django in the foreground
exec uv run python src/manage.py runserver 0.0.0.0:8000
