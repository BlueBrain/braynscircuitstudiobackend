BCSS_STARTUP_SCRIPT_FILEPATH = "bcsb-start-bcss.sh"
BRAYNS_STARTUP_SCRIPT_FILEPATH = "bcsb-start-brayns.sh"


def get_main_startup_script() -> str:
    return (
        """#!/bin/bash

source /etc/profile.d/bb5.sh

export UNICORE_HOSTNAME=$(hostname -f)
export UNICORE_CERT_FILEPATH=${TMPDIR}/${UNICORE_HOSTNAME}.crt
export UNICORE_PRIVATE_KEY_FILEPATH=${TMPDIR}/${UNICORE_HOSTNAME}.key

export BRAYNS_HOSTNAME=$UNICORE_HOSTNAME
export BRAYNS_PORT=5000
export BRAYNS_WS_URL=wss://${BRAYNS_HOSTNAME}:${BRAYNS_PORT}
export BRAYNS_EXECUTABLE_FILEPATH="/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/144fd0e/braynsService"
export BCSS_HOSTNAME=$UNICORE_HOSTNAME
export BCSS_PORT=8666
export BCSS_WS_URL=wss://${BCSS_HOSTNAME}:${BCSS_PORT}/ws/

echo Brayns Circuit Studio startup script
echo ----------------------
echo UNICORE_HOSTNAME=$UNICORE_HOSTNAME
echo UNICORE_CERT_FILEPATH=$UNICORE_CERT_FILEPATH
echo UNICORE_PRIVATE_KEY_FILEPATH=$UNICORE_PRIVATE_KEY_FILEPATH
echo TMPDIR=$TMPDIR
echo BRAYNS_PORT=$BRAYNS_PORT
echo BRAYNS_WS_URL=$BRAYNS_WS_URL
echo BCSS_PORT=$BCSS_PORT
echo BCSS_WS_URL=$BCSS_WS_URL
echo ----------------------
"""
        + f"""chmod 777 {BRAYNS_STARTUP_SCRIPT_FILEPATH} {BCSS_STARTUP_SCRIPT_FILEPATH}
{BRAYNS_STARTUP_SCRIPT_FILEPATH} & {BCSS_STARTUP_SCRIPT_FILEPATH}
"""
    )


def get_default_brayns_startup_script() -> str:
    return """#!/bin/bash
$BRAYNS_EXECUTABLE_FILEPATH \
--uri 0.0.0.0:$BRAYNS_PORT \
--secure true \
--certificate-file $UNICORE_CERT_FILEPATH \
--private-key-file $UNICORE_PRIVATE_KEY_FILEPATH \
--log-level debug \
--plugin braynsCircuitExplorer \
--plugin braynsCircuitInfo
"""


def get_default_bcss_startup_script() -> str:
    return """#!/bin/bash
source /etc/profile.d/bb5.sh
source /etc/profile.d/modules.sh

if [ -n "${TMPDIR}" ] ; then
  export APPTAINER_CACHEDIR=${TMPDIR}/.apptainer/cache
  export SINGULARITY_CACHEDIR=$APPTAINER_CACHEDIR
  export APPTAINER_TMPDIR=${TMPDIR}/.apptainer/tmp
  export APPTAINER_PULLDIR=${TMPDIR}/.apptainer/downloads
  mkdir -p $APPTAINER_PULLDIR $APPTAINER_TMPDIR $APPTAINER_CACHEDIR
fi

export APPTAINER_DOCKER_USERNAME=bbpvizuser
export APPTAINER_DOCKER_PASSWORD=y5U1sVybMaNJ3FZrX-1q

module load unstable apptainer

apptainer run \
--bind /gpfs:/gpfs \
--bind /nvme:/nvme \
--bind $TMPDIR:/braynscircuitstudio-tmp/ \
--compat \
--env DJANGO_SETTINGS_MODULE=bcss.settings \
--env BCSS_DJANGO_DEBUG=0 \
--env BCSS_PORT=$BCSS_PORT \
--env BCSS_DJANGO_SECRET_KEY="oh7ew+rs^apujawvl&$)==q#td&48hg9opu%58+%6%z2)sr+%w" \
--env BCSS_DJANGO_ALLOWED_HOSTS=$BCSS_HOSTNAME \
--env BCSS_DJANGO_DATABASE_NAME=/braynscircuitstudio-tmp/bcss_db.sqlite \
--env BCSS_ENVIRONMENT_MODE=production \
--env BCSS_HOSTNAME=$UNICORE_HOSTNAME \
--env BCSS_LOG_LEVEL=DEBUG \
--env DEV_ANONYMOUS_ACCESS=1 \
\
/gpfs/bbp.cscs.ch/home/naskret/bcss.sif \
\
sh -c \
"python /usr/src/braynscircuitstudio/apps/bcss/manage.py migrate \
&& /usr/src/braynscircuitstudio/bcss-entrypoint.sh \
gunicorn bcss.asgi:application \
--certfile $UNICORE_CERT_FILEPATH \
--keyfile $UNICORE_PRIVATE_KEY_FILEPATH \
--bind 0.0.0.0:$BCSS_PORT \
-k uvicorn.workers.UvicornWorker"
"""
