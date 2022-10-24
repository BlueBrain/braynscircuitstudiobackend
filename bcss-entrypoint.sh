#!/bin/sh

echo "Environment = ${BCSS_ENVIRONMENT_MODE}"
echo "PYTHONPATH = ${PYTHONPATH}"

export DJANGO_SETTINGS_MODULE="bcss.settings"

if [ "$BCSS_ENVIRONMENT_MODE" = "production" ]; then
  if [ "$BCSS_DJANGO_DEBUG" = "1" ]; then
    echo "ERROR: BCSS_DJANGO_DEBUG variable can't be turned on in production mode."
    exit 1
  fi
fi

if [ "$BCSS_ENVIRONMENT_MODE" = "development" ]; then
  python apps/bcss/manage.py migrate
  exec python apps/bcss/manage.py runserver ${BCSS_APP_HOST:-0.0.0.0}:${BCSS_APP_PORT:-8666}
fi

if [ -z "$BCSS_ENVIRONMENT_MODE" ]; then
  echo "BCSS_ENVIRONMENT_MODE variable is not set. Please specify either 'development' or 'production'."
fi;

exec "$@"
