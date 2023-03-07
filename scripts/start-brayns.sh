#!/bin/bash -l

export BRAYNS_PATH=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/ab2704b/braynsService
export BRAYNS_PORT=5000
export LOG_LEVEL=DEBUG
export HOSTNAME=$(hostname -f)

echo "Starting Brayns on port ${BRAYNS_PORT}..."

${BRAYNS_PATH} \
  --uri 0.0.0.0:$BRAYNS_PORT \
  --log-level debug \
  --plugin braynsCircuitExplorer \
  --plugin braynsAtlasExplorer >brayns-${HOSTNAME}.log 2>&1
