#!/bin/bash -l

export HOSTNAME=$(hostname -f)
export USE_TLS=1
export LOG_LEVEL=DEBUG
export UNICORE_CERT_FILEPATH=${TMPDIR}/${HOSTNAME}.crt
export UNICORE_PRIVATE_KEY_FILEPATH=${TMPDIR}/${HOSTNAME}.key
export BACKEND_DIR=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/backend/
export BACKEND_PORT=8000
export BRAYNS_PATH=/gpfs/bbp.cscs.ch/project/proj3/software/BraynsCircuitStudio/ab2704b/braynsService
export BRAYNS_PORT=5000

# Parsing command options
LONG=brayns-path::,brayns-port::,backend-port::
OPTS=$(getopt -a -n BraynsCircuitStudio --longoptions $LONG -- -- $@)

eval set -- "$OPTS"

while :; do
  case "$1" in
  --brayns-port )
    BRAYNS_PORT="$2"
    echo "Using a non-default Brayns port: $BRAYNS_PORT"
    shift 2
    ;;
  --backend-port)
    BACKEND_PORT="$2"
    echo "Using a non-default Backend port: $BACKEND_PORT"
    shift 2
    ;;
  --brayns-path)
    BRAYNS_PATH="$2"
    echo "Using a non-default Brayns path: $BRAYNS_PATH"
    shift 2
    ;;
  --)
    shift
    break
    ;;
  *)
    echo "Unexpected option: $1"
    break
    ;;
  esac
done

# This functions waits until Brayns and Backend start using their assigned ports
check_ports_are_in_use() {
  i=1
  while [ "$i" -ne 0 ]; do
    if [[ $(ss -tulpn | grep $1 | grep $2) ]] >/dev/null 2>&1; then
      break
    else
      sleep 0.2
    fi
  done
}

# Activate Python virtual environment
source ${BACKEND_DIR}venv/bin/activate

# This command allows to terminate all processes with single Ctrl+C
(
  trap 'kill 0' SIGINT

  python ${BACKEND_DIR}braynscircuitstudio/main.py \
    --port=$BACKEND_PORT \
    --certificate-file=$UNICORE_CERT_FILEPATH \
    --private-key-file=$UNICORE_PRIVATE_KEY_FILEPATH >backend-${HOSTNAME}.log 2>&1 &

  ${BRAYNS_PATH} \
    --uri 0.0.0.0:$BRAYNS_PORT \
    --log-level debug \
    --secure true \
    --certificate-file $UNICORE_CERT_FILEPATH \
    --private-key-file $UNICORE_PRIVATE_KEY_FILEPATH \
    --plugin braynsCircuitExplorer \
    --plugin braynsAtlasExplorer >brayns-${HOSTNAME}.log 2>&1 &

  check_ports_are_in_use $BACKEND_PORT "python" &&
    check_ports_are_in_use $BRAYNS_PORT "brayns" &&
    echo -e "\nBrayns Circuit Studio is ready!" &&
    echo -e "\n\033[1;32mNow, copy the host name below and paste it on the Brayns Circuit Studio page:\n$HOSTNAME\n\033[0m" &&
    echo -e "Press [Ctrl+C] to terminate Brayns services\n" &

  wait
)
