FROM python:3.9.5 as builder

# Set user and paths
ARG BCS_USERNAME=bcsusr

RUN useradd -ms /bin/bash $BCS_USERNAME
WORKDIR /home/$BCS_USERNAME/src/

ENV PYTHONPATH "/home/${BCS_USERNAME}/src/apps:/home/${BCS_USERNAME}/.local/bin:${PYTHONPATH}"
ENV PATH "/home/${BCS_USERNAME}/.local/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING "UTF-8"

# Copy and install requirements
COPY bcss-requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r bcss-requirements.txt \
    && pip install uvicorn[standard] \
    && pip install -i https://bbpteam.epfl.ch/repository/devpi/simple/ bluepy[all]

# Copy application files and install it
COPY . .

RUN pip install --no-cache-dir .
