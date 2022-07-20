NODE_HOSTNAME_FILENAME = "node-hostname.txt"
BCSS_STARTUP_SCRIPT_FILEPATH = "bcsb-start-bcss.sh"
BRAYNS_STARTUP_SCRIPT_FILEPATH = "bcsb-start-brayns.sh"


def get_main_startup_script() -> str:
    return f"""#!/bin/bash

source /etc/profile.d/bb5.sh

export UNICORE_HOSTNAME=$(hostname -f)
export UNICORE_HOSTNAME=$UNICORE_HOSTNAME
export UNICORE_CERT_FILEPATH=${{TMPDIR}}/${{UNICORE_HOSTNAME}}.crt
export UNICORE_PRIVATE_KEY_FILEPATH=${{TMPDIR}}/${{UNICORE_HOSTNAME}}.key

echo Brayns Circuit Studio startup script
echo TMPDIR=$TMPDIR
echo Cert filepath=$UNICORE_CERT_FILEPATH
echo Cert=$(cat $UNICORE_CERT_FILEPATH)
echo Private key filepath=$UNICORE_PRIVATE_KEY_FILEPATH
echo Private key=$(cat $UNICORE_PRIVATE_KEY_FILEPATH)
echo -----
echo $(hostname -f) > {NODE_HOSTNAME_FILENAME}
chmod 777 {BRAYNS_STARTUP_SCRIPT_FILEPATH} {BCSS_STARTUP_SCRIPT_FILEPATH}
{BRAYNS_STARTUP_SCRIPT_FILEPATH} & {BCSS_STARTUP_SCRIPT_FILEPATH}
"""


def get_brayns_startup_script(
    tls_key_filepath: str = "",
    tls_cert_filepath: str = "",
) -> str:
    if tls_key_filepath and tls_cert_filepath:
        tls_command = f"""--secure true \
--certificate-file {tls_cert_filepath} \
--private-key-file {tls_key_filepath}"""
    else:
        tls_command = ""

    return f"""#!/bin/bash
export BRAYNS_PORT=5000
export BRAYNS_VERSION=2
export BRAYNS_HOSTNAME=$(hostname -f)
export BRAYNS_LINK="/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/brayns-${{BRAYNS_VERSION}}"

echo ${{BRAYNS_HOSTNAME}}:${{BRAYNS_PORT}}

echo "Launching: ${{BRAYNS_LINK}}"
${{BRAYNS_LINK}} \
    {tls_command} --uri 0.0.0.0:${{BRAYNS_PORT}} \
    --log-level debug \
    --plugin braynsCircuitExplorer \
    --plugin braynsCircuitInfo | grep -v 'trigger-jpeg-stream'
"""


def get_bcss_startup_script(
    tls_key_filepath: str = "",
    tls_cert_filepath: str = "",
) -> str:
    if tls_key_filepath and tls_cert_filepath:
        tls_command = f"""--certfile {tls_cert_filepath} \
--keyfile {tls_key_filepath}"""
        service_port = 8666
    else:
        tls_command = ""
        service_port = 8666

    return f"""#!/bin/bash
source /etc/profile.d/bb5.sh
source /etc/profile.d/modules.sh

if [ -n "${{TMPDIR}}" ] ; then
  export APPTAINER_CACHEDIR=${{TMPDIR}}/.apptainer/cache
  export SINGULARITY_CACHEDIR=$APPTAINER_CACHEDIR
  export APPTAINER_TMPDIR=${{TMPDIR}}/.apptainer/tmp
  export APPTAINER_PULLDIR=${{TMPDIR}}/.apptainer/downloads
  mkdir -p $APPTAINER_PULLDIR $APPTAINER_TMPDIR $APPTAINER_CACHEDIR
fi

export APPTAINER_DOCKER_USERNAME=bbpvizuser
export APPTAINER_DOCKER_PASSWORD=y5U1sVybMaNJ3FZrX-1q

module load unstable apptainer

echo "Starting BCSS on: ${{UNICORE_HOSTNAME}}"

apptainer run \
    --bind /gpfs:/gpfs \
    --bind /nvme:/nvme \
    --bind $TMPDIR:/braynscircuitstudio-tmp/ \
    --compat \
    --env DJANGO_SETTINGS_MODULE=bcss.settings \
    --env BCSS_DJANGO_DEBUG=0 \
    --env BCSS_DJANGO_SECRET_KEY="oh7ew+rs^apujawvl&$)==q#td&48hg9opu%58+%6%z2)sr+%w" \
    --env BCSS_DJANGO_ALLOWED_HOSTS=$UNICORE_HOSTNAME \
    --env BCSS_DJANGO_DATABASE_NAME=/braynscircuitstudio-tmp/bcss_db.sqlite \
    --env BCSS_ENVIRONMENT_MODE=production \
    --env BCSS_HOSTNAME=$UNICORE_HOSTNAME \
    --env BCSS_LOG_LEVEL=DEBUG \
    --env DEV_ANONYMOUS_ACCESS=1 \
    docker://bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend/bcss:manual \
    sh -c \
    "python /usr/src/braynscircuitstudio/apps/bcss/manage.py migrate \
    && /usr/src/braynscircuitstudio/bcss-entrypoint.sh gunicorn bcss.asgi:application \
    {tls_command} --bind 0.0.0.0:{service_port} -k uvicorn.workers.UvicornWorker"
"""
