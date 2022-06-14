FROM python:3.9.5 as builder

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/apps/"

# Copy and install requirements
WORKDIR /usr/src/
COPY bcss-requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r bcss-requirements.txt
RUN pip install -i https://bbpteam.epfl.ch/repository/devpi/simple/ bluepy

# Copy application files and install it
COPY . .
RUN pip install --no-cache-dir .
