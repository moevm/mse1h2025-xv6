FROM ubuntu:24.04

RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
    	ca-certificates=20240203 \
        python3=3.12.3-0ubuntu2 \
        qemu-user-static=1:8.2.2+ds-0ubuntu1.7 \
        git=1:2.43.0-1ubuntu7.2 \
        gcc=4:13.2.0-7ubuntu1 \
        make=4.3-4.1build2 \
        build-essential=12.10ubuntu1 \
        gdb-multiarch=15.0.50.20240403-0ubuntu1 \
        qemu-system-misc=1:8.2.2+ds-0ubuntu1.7 \
        gcc-riscv64-linux-gnu=4:13.2.0-7ubuntu1 \
        binutils-riscv64-linux-gnu=2.42-4ubuntu2.5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --chown=appuser:appuser scripts /app/scripts
COPY --chown=appuser:appuser solution /app/solution
COPY --chown=appuser:appuser tests /app/tests


RUN find /app/scripts -type f -exec chmod 644 {} + && \
    chmod 755 /app/scripts/run.sh && \
    chown -R appuser:appuser /app
    
USER appuser

ENTRYPOINT ["/app/scripts/run.sh"]
