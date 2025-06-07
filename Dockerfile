FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    exiftool build-essential autoconf libtool cmake wget ffmpeg \
    imagemagick libmagickwand-dev curl ca-certificates \
    git && \
  cd /usr/src && \
  git clone https://github.com/strukturag/libde265.git && \
  cd libde265 && ./autogen.sh && ./configure && make -j$(nproc) && make install && \
  cd /usr/src && \
  git clone https://github.com/strukturag/libheif.git && \
  cd libheif && mkdir build && cd build && cmake --preset=release .. && make -j$(nproc) && make install && \
  wget https://github.com/ImageMagick/ImageMagick/archive/refs/tags/7.1.1-26.tar.gz && \
  tar xf 7.1.1-26.tar.gz && \
  cd ImageMagick-7.1.1-26* && ./configure --with-heic=yes && make -j$(nproc) && make install && \
  ldconfig && \
  rm -rf /var/lib/apt/lists/* /usr/src/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY image_convert.py worker.py ./
RUN mkdir /tmp/out

CMD ["python", "worker.py"]