#!/bin/bash
echo "Make database migrations at startup of project."
while ! python manage.py makemigrations vpn_app 2>&1; do
  echo "Making migrations is in progress status"
  sleep 3
done
echo "Migrate the database at startup of project."
while ! python manage.py migrate 2>&1; do
  echo "Migration is in progress status."
  sleep 3
done
echo "Create superuser if it had not been created earlier."
while ! python manage.py init_create_superuser 2>&1; do
  echo "Create initial superuser, if it had not been created earlier."
  sleep 3
done
echo "Django docker is fully configured successfully."
gunicorn -b unix:/gunicorn_socket/config config.wsgi --workers 3 --bind 0.0.0.0:8000 &
celery -A config worker -l
exec "$@"