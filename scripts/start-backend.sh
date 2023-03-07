#!/bin/bash -l

export BACKEND_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/backend/
export BACKEND_PORT=8000
export LOG_LEVEL=DEBUG

echo "Activating Python virtual environment..."
source ${BACKEND_DIR}venv/bin/activate
echo "Starting backend..."

${BACKEND_DIR}src/main.py --port=$BACKEND_PORT >backend-$1.log 2>&1
