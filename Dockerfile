# GPU build — uses dustynv/faster-whisper as base for CUDA-enabled CTranslate2
# JetPack 6.x / R36.4 / CUDA 12.8
FROM dustynv/faster-whisper:r36.4.0-cu128-24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    libasound2-dev \
    portaudio19-dev \
    libsndfile1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install app dependencies (faster-whisper and ctranslate2 already in base image)
COPY requirements.txt .
RUN pip3 install --no-cache-dir \
    --index-url https://pypi.org/simple/ \
    anthropic \
    azure-cognitiveservices-speech \
    piper-tts \
    sounddevice \
    soundfile \
    pydantic-settings

COPY . .

VOLUME ["/app/models"]

CMD ["python3", "-m", "app.main"]
