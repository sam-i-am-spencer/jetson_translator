#!/usr/bin/env bash
# Download piper TTS voice models.
# Translation and Whisper models are downloaded automatically on first run.
set -euo pipefail

PIPER_DIR="${PIPER_MODELS_DIR:-./models/piper}"
PIPER_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main"

mkdir -p "$PIPER_DIR"

download_voice() {
    local voice="$1"
    local url_path="$2"
    echo "Downloading $voice..."
    if command -v curl &>/dev/null; then
        curl -L --progress-bar "${PIPER_BASE}/${url_path}/${voice}.onnx" -o "${PIPER_DIR}/${voice}.onnx"
        curl -L --progress-bar "${PIPER_BASE}/${url_path}/${voice}.onnx.json" -o "${PIPER_DIR}/${voice}.onnx.json"
    else
        wget -q --show-progress "${PIPER_BASE}/${url_path}/${voice}.onnx" -O "${PIPER_DIR}/${voice}.onnx"
        wget -q --show-progress "${PIPER_BASE}/${url_path}/${voice}.onnx.json" -O "${PIPER_DIR}/${voice}.onnx.json"
    fi
}

# English voice
download_voice "en_US-lessac-medium" "en/en_US/lessac/medium"

# Chinese voice
download_voice "zh_CN-huayan-medium" "zh/zh_CN/huayan/medium"

echo "Done. Voices saved to $PIPER_DIR"
