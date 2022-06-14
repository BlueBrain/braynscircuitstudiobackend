#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:/usr/src/"

echo "Environment = ${ENVIRONMENT_MODE}"

if [ "$ENVIRONMENT_MODE" = "production" ]; then
  if [ "$DEBUG" = "1" ]; then
    echo "ERROR: DEBUG variable can't be turned on in production mode."
    exit 1
  fi
fi

if [ "$ENVIRONMENT_MODE" = "development" ]; then
  exec python apps/bcss/manage.py runserver ${BCSS_HOST:-0.0.0.0}:${BCSS_PORT:-8666}
fi

if [ -z "$ENVIRONMENT_MODE" ]; then
  echo "ENVIRONMENT_MODE variable is not set. Please specify either 'development' or 'production'."
fi;

exec "$@"
