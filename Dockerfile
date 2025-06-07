FROM python:3.11-slim

# Install system dependencies for HEIC, JPEG, OpenCV, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libheif-dev \
    libjpeg-dev \
    libgl1 \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create tmp directory
RUN mkdir -p /app/tmp

ENV PYTHONUNBUFFERED=1 \
    SUPABASE_BUCKET=timelapsevideos

CMD ["python", "worker.py"]