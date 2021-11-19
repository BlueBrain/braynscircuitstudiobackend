FROM python:3.9.5-alpine as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

RUN apk add --virtual .build-deps build-base linux-headers g++ gcc musl-dev gpgme-dev libc-dev
RUN apk add postgresql-libs postgresql postgresql-dev
RUN apk add python3-dev jpeg-dev zlib-dev libjpeg py3-pillow
RUN apk add gettext

# Install base Python packages
COPY ./requirements.txt .
RUN \
  pip install --upgrade pip && \
  pip install -r requirements.txt
RUN pip install uvicorn[standard]

FROM builder

ENV PYTHONPATH "${PYTHONPATH}:/usr/src"

WORKDIR /usr/src/app/
RUN apk --purge del .build-deps
COPY ./entrypoint.sh /usr/src/
COPY . /usr/src/
