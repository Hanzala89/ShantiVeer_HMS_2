#!/bin/bash
# Vercel build script — runs during deployment (not at runtime)
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Running migrations ==="
python manage.py migrate --noinput

echo "=== Build complete ==="
