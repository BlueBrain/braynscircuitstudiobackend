#!/bin/bash -l

#SBATCH --account={{ACCOUNT}}
#SBATCH -p prod
#SBATCH -t 8:00:00
#SBATCH --exclusive
#SBATCH --constraint=cpu
#SBATCH -c 80
#SBATCH --mem 0
#SBATCH -N 1

export BCS_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/
export BACKEND_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/backend/

export BACKEND_PORT=8000
export BRAYNS_PORT=5000

export LOG_LEVEL=DEBUG
export UNICORE_HOSTNAME=$(hostname -f)

echo "Starting Brayns..."
${BCS_DIR}brayns-{{BRAYNS_VERSION}} \
  --uri 0.0.0.0:$BRAYNS_PORT \
  --log-level debug \
  --plugin braynsCircuitExplorer \
  --plugin braynsAtlasExplorer >./output/logs/brayns-$1.log 2>&1 &

echo "Activating Python virtual environment..."
source ${BACKEND_DIR}venv/bin/activate
echo "Starting backend..."

${BACKEND_DIR}src/main.py --port=$BACKEND_PORT >./output/logs/backend-$1.log 2>&1

deactivate

echo "Terminating the current job..."
scancel --name="BraynsAgent$1"
