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

ENTRYPOINT ["/app/scripts/run.sh"]

