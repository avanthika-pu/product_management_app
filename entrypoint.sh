#!/bin/bash

# Print debug info
echo "Python executable:"
which python
python --version

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting supervisor..."
# -c points to our specific config file
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf