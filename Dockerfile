FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (pre-compiled wheels available)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create tmp directory
RUN mkdir -p /app/tmp

ENV PYTHONUNBUFFERED=1 \
    SUPABASE_BUCKET=timelapsevideos

CMD ["python", "worker.py"]