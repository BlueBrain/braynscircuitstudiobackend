#!/bin/bash -l

export BRAYNS_PATH=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/ab2704b/braynsService
export BCS_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/
export BRAYNS_PORT=5000
export LOG_LEVEL=DEBUG

echo "Starting Brayns..."
${BCS_DIR}${BRAYNS_PATH} \
  --uri 0.0.0.0:$BRAYNS_PORT \
  --log-level debug \
  --plugin braynsCircuitExplorer \
  --plugin braynsAtlasExplorer >brayns-$1.log 2>&1
