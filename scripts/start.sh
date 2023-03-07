#!/bin/bash -l

bash ${BASH_SOURCE%/*}/start-brayns.sh && bash ${BASH_SOURCE%/*}/start-backend.sh
