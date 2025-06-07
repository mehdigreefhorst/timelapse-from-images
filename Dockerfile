FROM python:3.12-alpine

# 1. everything opencv-python + pyheif expect
RUN apk add --no-cache \
      build-base      \
      gcc g++         \
      musl-dev        \
      ffmpeg curl ca-certificates \
      jpeg-dev        \
      openjpeg-dev    \
      libpng-dev      \
      libwebp-dev     \
      libxml2-dev     \
      libheif-dev     \
      tiff-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1 SUPABASE_BUCKET=timelapsevideos
CMD ["python", "worker.py"]