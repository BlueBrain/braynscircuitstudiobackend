#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:/usr/src/"

echo "Environment = ${BCSB_ENVIRONMENT_MODE}"

if [ "$BCSB_ENVIRONMENT_MODE" = "production" ]; then
  if [ "$BCSB_DJANGO_DEBUG" = "1" ]; then
    echo "ERROR: BCSB_DJANGO_DEBUG can't be turned on in production mode."
    exit 1
  fi
fi

if [ "$BCSB_ENVIRONMENT_MODE" = "development" ]; then
  exec python apps/bcsb/manage.py runserver ${BCSB_APP_HOST:-0.0.0.0}:${BCSB_APP_PORT:-8000}
fi

if [ -z "$BCSB_ENVIRONMENT_MODE" ]; then
  echo "BCSB_ENVIRONMENT_MODE variable is not set. Please specify either 'development' or 'production'."
fi;

exec "$@"
