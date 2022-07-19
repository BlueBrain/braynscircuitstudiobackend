NODE_HOSTNAME_FILENAME = "node-hostname.txt"
BCSS_STARTUP_SCRIPT_FILEPATH = "bcsb-start-bcss.sh"
BRAYNS_STARTUP_SCRIPT_FILEPATH = "bcsb-start-brayns.sh"


def get_main_startup_script() -> str:
    return f"""#!/bin/bash
echo $(hostname -f) > {NODE_HOSTNAME_FILENAME}
chmod +x {BRAYNS_STARTUP_SCRIPT_FILEPATH} {BCSS_STARTUP_SCRIPT_FILEPATH}
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

source /etc/profile.d/bb5.sh

export BRAYNS_PORT=5000
export BRAYNS_VERSION=2
export BRAYNS_HOSTNAME=$(hostname -f)
export BRAYNS_LINK="/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/brayns-${{BRAYNS_VERSION}}"

echo ${{BRAYNS_HOSTNAME}}:${{BRAYNS_PORT}}

echo "Launching: ${{BRAYNS_LINK}}"
${{BRAYNS_LINK}} \
    --uri 0.0.0.0:${{BRAYNS_PORT}} \
    --log-level error \
    --plugin braynsCircuitExplorer \
    --plugin braynsCircuitInfo | grep -v 'trigger-jpeg-stream' {tls_command}
"""


def get_bcss_startup_script(
    tls_key_filepath: str = "",
    tls_cert_filepath: str = "",
) -> str:
    if tls_key_filepath and tls_cert_filepath:
        tls_command = f"""--certfile {tls_cert_filepath} \
--keyfile {tls_key_filepath}"""
        service_port = 443
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

export BCSS_HOSTNAME=$(hostname -f)
export BCSS_DJANGO_ALLOWED_HOSTS=${{BCSS_HOSTNAME}}
export BCSS_ENVIRONMENT_MODE=production
export BCSS_DJANGO_DEBUG=0
export BCSS_DJANGO_SECRET_KEY="oh7ew+rs^apujawvl&$)==q#td&48hg9opu%58+%6%z2)sr+%w"
export BCSS_LOG_LEVEL=DEBUG
export DEV_ANONYMOUS_ACCESS=1

module load unstable apptainer

apptainer run \
    --bind /gpfs:/gpfs \
    docker://bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend/bcss:manual \
    sh -c \
    "python apps/bcss/manage.py migrate \
    && bcss-entrypoint.sh gunicorn bcss.asgi:application \
    --bind 0.0.0.0:{service_port} -k uvicorn.workers.UvicornWorker" {tls_command}
"""
