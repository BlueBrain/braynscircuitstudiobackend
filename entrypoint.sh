#!/bin/sh

echo "Environment = ${ENVIRONMENT_MODE}"
echo "PYTHONPATH = ${PYTHONPATH}"
echo "LOG_LEVEL = ${LOG_LEVEL}"

RUN_COMMAND="$@"

if [ -z "$RUN_COMMAND" ]; then
  python /usr/src/src/main.py --port=${APP_PORT:-8000}
fi;

exec "$@"
