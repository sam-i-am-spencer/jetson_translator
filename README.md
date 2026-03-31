# Jetson Translator

Bidirectional **English ↔ Traditional Chinese** speech translator running on a Jetson Orin Nano.

Two USB sound cards are used simultaneously — speak into one, hear the translation from the other.

## How it works

| Channel | Record from | Speak in | Translate to | Play on |
|---------|------------|----------|--------------|---------|
| EN→ZH | `SOUND_CARD_EN` | English | Chinese | `SOUND_CARD_ZH` |
| ZH→EN | `SOUND_CARD_ZH` | Chinese | English | `SOUND_CARD_EN` |

**Pipeline:** Audio → [faster-whisper STT] → [Helsinki-NLP translation] → [piper TTS] → Audio

## Hardware

- Jetson Orin Nano (JetPack 6.x)
- 2× USB sound cards (e.g. USB-C audio adapters)
- Keyboard (development) or GPIO switches (portable mode)

## Setup

### 1. Clone and configure

```bash
git clone https://github.com/sam-i-am-spencer/jetson_translator
cd jetson_translator
cp .env.example .env
```

Edit `.env` — set your sound card device strings:

```bash
# Find device names/indices
python3 -m app.main --list-devices
# or: python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

### 2. Download models

```bash
chmod +x scripts/download_models.sh
./scripts/download_models.sh
```

Translation (Helsinki-NLP) and Whisper models download automatically on first run.

### 3a. Run with Docker (recommended)

```bash
docker compose up --build
```

### 3b. Run directly

```bash
# Install PyTorch for Jetson first — see Dockerfile for NVIDIA wheel URL
pip3 install -r requirements.txt
python3 -m app.main
```

## Usage

- **Hold `1`** — record in English → hear Chinese translation
- **Hold `2`** — record in Chinese → hear English translation
- **Ctrl+C** — quit

Keys are configurable via `KEY_RECORD_EN` / `KEY_RECORD_ZH` in `.env`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SOUND_CARD_EN` | `hw:1,0` | ALSA device for English side |
| `SOUND_CARD_ZH` | `hw:2,0` | ALSA device for Chinese side |
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`→`large-v3`) |
| `WHISPER_DEVICE` | `cuda` | `cuda` or `cpu` |
| `WHISPER_COMPUTE_TYPE` | `float16` | `float16` (GPU) or `int8` (CPU) |
| `PIPER_VOICE_EN` | `en_US-lessac-medium` | English TTS voice |
| `PIPER_VOICE_ZH` | `zh_CN-huayan-medium` | Chinese TTS voice |
| `KEY_RECORD_EN` | `1` | Push-to-talk key for English |
| `KEY_RECORD_ZH` | `2` | Push-to-talk key for Chinese |

## Notes

- **Traditional Chinese input:** faster-whisper transcribes in Traditional Chinese when the input is Traditional Chinese speech. The Helsinki-NLP `opus-mt-zh-en` model handles both simplified and traditional characters.
- **GPIO mode:** `app/input_handler.py` contains a commented `GPIOInputHandler` skeleton. Swap it into `main.py` when moving to physical switches.
- **Keyboard in Docker:** requires `privileged: true` and a TTY (`stdin_open: true`, `tty: true`).
- **JetPack version:** update the base image in `Dockerfile` to match your JetPack — check with `cat /etc/nv_tegra_release`.

## Roadmap

- [ ] GPIO switch support for portable/compact build
- [ ] Home Assistant integration (voice commands via LLM)
- [ ] Web status UI
