FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    qemu-user-static \
    git \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY scripts /app/scripts

RUN chmod +x /app/scripts/run.sh && \
    chown -R root:root /app/scripts

COPY docker/requirements.txt .

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/app/scripts/run.sh"]

