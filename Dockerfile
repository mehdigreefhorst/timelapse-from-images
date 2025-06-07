FROM python:3.11-alpine

# Install build and runtime dependencies
RUN apk add --no-cache \
    ffmpeg \
    curl \
    ca-certificates \
    build-base \
    cmake \
    ninja \
    libffi-dev \
    musl-dev \
    python3-dev

# Install Python build helpers + pycparser early to avoid cffi errors
RUN pip install --no-cache-dir --upgrade pip setuptools wheel pycparser

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    SUPABASE_BUCKET=timelapsevideos

CMD ["python", "worker.py"]