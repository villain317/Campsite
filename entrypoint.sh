#!/bin/sh
set -e

if [ -n "$POSTGRES_DB" ]; then
    echo "Waiting for database at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
    python <<'EOF'
import os
import socket
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Database never became available")
EOF
    echo "Database is up."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
python manage.py seed_groups

# If a command was passed in (e.g. by PyCharm's Docker Compose run/debug
# configuration), run that instead of the default server. This lets you
# override the container's command for `manage.py runserver` + debugger.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn campsite.wsgi:application --bind 0.0.0.0:8000 --workers 3
