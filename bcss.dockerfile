FROM python:3.9.5

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/"

# Copy and install requirements
WORKDIR /usr/src/
COPY bcss-requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r bcss-requirements.txt

# Copy application files and install it
COPY . .
RUN pip install --no-cache-dir .

ENTRYPOINT ["python"]
