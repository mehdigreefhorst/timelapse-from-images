# ────────────────────────────────
# Dockerfile — tiny & reliable
# uses python:3.12-alpine + ffmpeg
# ────────────────────────────────
FROM python:3.11-slim

# add ffmpeg (and curl, certificates) via apk
RUN apt-get update && apt-get install -y ffmpeg curl ca-certificates libheif1 libde265-0 heif-gdk-pixbuf libheif-examples

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    SUPABASE_BUCKET=timelapsevideos

CMD ["python", "worker.py"]