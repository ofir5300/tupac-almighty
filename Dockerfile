# syntax=docker/dockerfile:1.4

# First stage: builder
FROM python:3.13-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake pkg-config libprotobuf-dev protobuf-compiler libgomp1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Final stage: minimal runtime
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    sshpass openssh-client libgomp1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]