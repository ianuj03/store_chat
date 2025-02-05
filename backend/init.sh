#!/bin/bash

echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser (if not exists)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
EOF

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 storechat.wsgi:application

