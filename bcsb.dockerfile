FROM python:3.9.5-alpine as builder

RUN apk add --virtual .build-deps build-base linux-headers g++ gcc musl-dev gpgme-dev libc-dev
RUN apk add postgresql-libs postgresql postgresql-dev
RUN apk add python3-dev jpeg-dev zlib-dev libjpeg py3-pillow
RUN apk add gettext

# Set user and paths
ARG BCS_USERNAME=bcsusr

WORKDIR /home/$BCS_USERNAME/src/

ENV PYTHONPATH "/home/${BCS_USERNAME}/src/apps:/home/${BCS_USERNAME}/.local/bin:${PYTHONPATH}"
ENV PATH "/home/${BCS_USERNAME}/.local/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

# Install base Python packages
COPY ./bcsb-requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r bcsb-requirements.txt \
    && pip install uvicorn[standard]

FROM builder

# Set user and paths
ARG BCS_USERNAME=bcsusr

ENV PYTHONPATH "/home/${BCS_USERNAME}/src/apps:/home/${BCS_USERNAME}/.local/bin:${PYTHONPATH}"
ENV PATH "/home/${BCS_USERNAME}/.local/bin:${PATH}"

RUN apk --purge del .build-deps

WORKDIR /home/$BCS_USERNAME/src

# Copy application files and install it
COPY . .

RUN pip install --no-cache-dir .

RUN python -m pytest apps/bcsb
