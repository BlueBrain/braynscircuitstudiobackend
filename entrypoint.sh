#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:/usr/src/braynscircuitstudiobackend/"

echo "Environment = ${ENVIRONMENT_MODE}"

if [ "$ENVIRONMENT_MODE" = "production" ]; then
  if [ "$DJANGO_DEBUG" = "1" ]; then
    echo "ERROR: DJANGO_DEBUG can't be turned on in production mode."
    exit 1
  fi
  exec gunicorn bcsb.asgi:application --bind ${COMPOSE_BACKEND_HOST:-0.0.0.0}:${COMPOSE_BACKEND_PORT:-8000} -k uvicorn.workers.UvicornWorker
fi

if [ "$ENVIRONMENT_MODE" = "development" ]; then
  exec python /usr/src/braynscircuitstudiobackend/manage.py runserver ${COMPOSE_BACKEND_HOST:-0.0.0.0}:${COMPOSE_BACKEND_PORT:-8000}
fi

if [ -z "$ENVIRONMENT_MODE"]; then
  echo "ENVIRONMENT_MODE variable is not set. Please specify either 'development' or 'production'."
fi;

exec "$@"
