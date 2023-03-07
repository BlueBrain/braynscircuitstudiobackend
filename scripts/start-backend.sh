#!/bin/bash -l

export BACKEND_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/backend/
export BACKEND_PORT=8000
export LOG_LEVEL=DEBUG
export USE_TLS=0

HOSTNAME=$(hostname -f)

echo "Activating Python virtual environment..."
source ${BACKEND_DIR}venv/bin/activate
echo "Starting backend at ${HOSTNAME}:${BACKEND_PORT}"

python ${BACKEND_DIR}src/main.py --port=$BACKEND_PORT >backend-${HOSTNAME}.log 2>&1
