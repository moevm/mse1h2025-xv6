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

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt .

RUN python3 -m venv venv

RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

COPY script.sh .

RUN chmod +x script.sh

CMD ["./script.sh"]  

