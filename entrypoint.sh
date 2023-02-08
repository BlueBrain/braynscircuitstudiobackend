#!/bin/sh

echo "Environment = ${ENVIRONMENT_MODE}"
echo "PYTHONPATH = ${PYTHONPATH}"

RUN_COMMAND="$@"

if [ -z "$RUN_COMMAND" ]; then
  python src/main.py --port=${APP_PORT:-8000}
fi;

exec "$@"
