FROM python:3.9.5-alpine as builder

RUN apk add --virtual .build-deps build-base linux-headers g++ gcc musl-dev gpgme-dev libc-dev
RUN apk add postgresql-libs postgresql postgresql-dev
RUN apk add python3-dev jpeg-dev zlib-dev libjpeg py3-pillow
RUN apk add gettext

# Set user and paths
ARG BCS_WORKDIR=/usr/src/braynscircuitstudio
WORKDIR $BCS_WORKDIR

ENV PYTHONPATH "${BCS_WORKDIR}/apps:${PYTHONPATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

# Install base Python packages
COPY ./bcsb-requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r bcsb-requirements.txt \
    && pip install uvicorn[standard]

FROM builder

ARG BCS_WORKDIR=/usr/src/braynscircuitstudio
WORKDIR $BCS_WORKDIR

ENV PYTHONPATH "${BCS_WORKDIR}/apps:${PYTHONPATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

RUN apk --purge del .build-deps

COPY . .

RUN pip install --no-cache-dir .

RUN python -m pytest apps/bcsb
