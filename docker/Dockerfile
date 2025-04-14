FROM ubuntu:24.04

RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        qemu-user-static \
        git \
        gcc \
        make \
        build-essential \
        gdb-multiarch \
        qemu-system-misc \
        gcc-riscv64-linux-gnu \
        binutils-riscv64-linux-gnu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --chown=appuser:appuser scripts /app/scripts

RUN find /app/scripts -type f -exec chmod 644 {} + && \
    chmod 755 /app/scripts/run.sh && \
    chown -R appuser:appuser /app
    
USER appuser

ENTRYPOINT ["/app/scripts/run.sh"]

