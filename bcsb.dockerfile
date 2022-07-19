FROM python:3.9.5-alpine as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

RUN apk add --virtual .build-deps build-base linux-headers g++ gcc musl-dev gpgme-dev libc-dev
RUN apk add postgresql-libs postgresql postgresql-dev
RUN apk add python3-dev jpeg-dev zlib-dev libjpeg py3-pillow
RUN apk add gettext

# Set user and paths
ARG BCS_USERNAME=bcsusr

RUN adduser -D $BCS_USERNAME
USER $BCS_USERNAME
WORKDIR /home/$BCS_USERNAME/

ENV PYTHONPATH "${PYTHONPATH}:/home/${BCS_USERNAME}/apps/"
ENV PATH "/home/${BCS_USERNAME}/.local/bin:${PATH}"

# Install base Python packages
COPY ./bcsb-requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r bcsb-requirements.txt \
    && pip install uvicorn[standard]

FROM builder

USER root
RUN apk --purge del .build-deps

# Set user and paths
ARG BCS_USERNAME=bcsusr

#RUN adduser -D $BCS_USERNAME
USER $BCS_USERNAME
WORKDIR /home/$BCS_USERNAME/

ENV PYTHONPATH "${PYTHONPATH}:/home/${BCS_USERNAME}/apps/"
ENV PATH "/home/${BCS_USERNAME}/.local/bin:${PATH}"

# Copy application files and install it
COPY --chown=$BCS_USERNAME . .

RUN pip install --no-cache-dir .

RUN python -m pytest apps/bcsb
