#!/bin/sh

echo "Waiting for the database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

echo "!! Applying migrations..."
python manage.py migrate

echo "!! Creating default admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='admin@admin.com').exists():
    User.objects.create_superuser(email='admin@admin.com', password='1qazcde3')
"

echo "!! Starting Django server..."
python manage.py runserver 0.0.0.0:8000
