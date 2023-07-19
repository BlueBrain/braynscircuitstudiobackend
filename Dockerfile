FROM python:3.9.5 as builder

ARG WORKDIR=/usr/src/
WORKDIR $WORKDIR

ENV PYTHONPATH "${WORKDIR}:${PYTHONPATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

# Copy and install requirements
COPY requirements.txt .

RUN python -mvenv /venv
RUN . /venv/bin/activate

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install uvicorn[standard]

# Copy application files and install it
COPY . .

RUN pip install --no-cache-dir .
