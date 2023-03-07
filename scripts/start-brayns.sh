#!/bin/bash -l

export BCS_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/
export BRAYNS_PORT=5000
export LOG_LEVEL=DEBUG

echo "Starting Brayns..."
${BCS_DIR}brayns-{{BRAYNS_VERSION}} \
  --uri 0.0.0.0:$BRAYNS_PORT \
  --log-level debug \
  --plugin braynsCircuitExplorer \
  --plugin braynsAtlasExplorer >brayns-$1.log 2>&1
