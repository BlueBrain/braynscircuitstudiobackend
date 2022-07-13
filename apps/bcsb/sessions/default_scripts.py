DEFAULT_BRAYNS_STARTUP_SCRIPT = """#!/bin/bash

source /etc/profile.d/bb5.sh

export BRAYNS_PORT=5000
export BRAYNS_VERSION=2
export BRAYNS_HOSTNAME=$(hostname -f)
export BRAYNS_LINK="/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/brayns-${BRAYNS_VERSION}"

echo ${BRAYNS_HOSTNAME}:${BRAYNS_PORT}

echo "Launching: ${BRAYNS_LINK}"
${BRAYNS_LINK} \
    --uri 0.0.0.0:${BRAYNS_PORT} \
    --log-level error \
    --plugin braynsCircuitExplorer \
    --plugin braynsCircuitInfo | grep -v 'trigger-jpeg-stream'
"""

DEFAULT_BCSS_STARTUP_SCRIPT = """#!/bin/bash
if [ -n "${TMPDIR}" ] ; then
  export APPTAINER_CACHEDIR=${TMPDIR}/.apptainer/cache
  export SINGULARITY_CACHEDIR=$APPTAINER_CACHEDIR
  export APPTAINER_TMPDIR=${TMPDIR}/.apptainer/tmp
  export APPTAINER_PULLDIR=${TMPDIR}/.apptainer/downloads
  mkdir -p $APPTAINER_PULLDIR $APPTAINER_TMPDIR $APPTAINER_CACHEDIR
fi

export APPTAINER_DOCKER_USERNAME=bbpvizuser
export APPTAINER_DOCKER_PASSWORD=y5U1sVybMaNJ3FZrX-1q

export BCSS_HOSTNAME=$(hostname -f)
export BCSS_DJANGO_ALLOWED_HOSTS=${BCSS_HOSTNAME}
export BCSS_ENVIRONMENT_MODE=production
export BCSS_DJANGO_DEBUG=1
export BCSS_LOG_LEVEL=DEBUG
export DEV_ANONYMOUS_ACCESS=1

module load unstable apptainer

apptainer run \
    --bind /gpfs:/gpfs \
    docker://bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend/bcss:manual \
    python /usr/src/apps/bcss/manage.py runserver 0.0.0.0:8000
"""
