#!/bin/sh
set -e

export PROXYWAKE_DATA_DIR="${PROXYWAKE_DATA_DIR:-/app/backend/data}"
mkdir -p "$PROXYWAKE_DATA_DIR"

exec gunicorn \
  --chdir /app/backend \
  --bind 0.0.0.0:5001 \
  --workers 2 \
  --threads 4 \
  --timeout 30 \
  --access-logfile - \
  --error-logfile - \
  app:app
