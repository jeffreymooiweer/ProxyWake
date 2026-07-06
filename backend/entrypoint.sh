#!/bin/sh
set -e

export PROXYWAKE_DATA_DIR="${PROXYWAKE_DATA_DIR:-/app/backend/data}"
mkdir -p "$PROXYWAKE_DATA_DIR"

GUNICORN_ARGS="--chdir /app/backend --bind 0.0.0.0:5001 --workers 2 --threads 4 --timeout 30 --access-logfile - --error-logfile - app:app"

# Unraid and other hosts often create the appdata mount as root. Fix ownership
# when the entrypoint runs as root, then drop privileges for gunicorn.
if [ "$(id -u)" = "0" ]; then
  chown -R proxywake:proxywake "$PROXYWAKE_DATA_DIR"
  exec su -s /bin/sh proxywake -c "exec gunicorn $GUNICORN_ARGS"
fi

exec gunicorn $GUNICORN_ARGS
