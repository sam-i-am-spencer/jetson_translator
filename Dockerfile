# Jetson Orin Nano — JetPack 6.x (L4T r36.x)
# Adjust the base image tag to match your JetPack version:
#   JetPack 6.x → nvcr.io/nvidia/l4t-base:r36.2.0
#   JetPack 5.x → nvcr.io/nvidia/l4t-base:r35.4.1
# Check your JetPack version: cat /etc/nv_tegra_release
FROM nvcr.io/nvidia/l4t-base:r36.2.0

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    libportaudio2 \
    libasound2-dev \
    portaudio19-dev \
    libsndfile1 \
    espeak-ng \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch for Jetson — use NVIDIA's wheel index
# https://developer.download.nvidia.com/compute/redist/jp/
RUN pip3 install --no-cache-dir \
    --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v60 \
    torch torchvision torchaudio

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Models directory is mounted as a volume to persist downloads
VOLUME ["/app/models"]

CMD ["python3", "-m", "app.main"]
