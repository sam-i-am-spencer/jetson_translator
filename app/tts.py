"""
TTS using piper-tts.
Voices are downloaded separately via scripts/download_models.sh.
Expected layout:
  models/piper/en_US-lessac-medium.onnx
  models/piper/en_US-lessac-medium.onnx.json
  models/piper/zh_CN-huayan-medium.onnx
  models/piper/zh_CN-huayan-medium.onnx.json
"""
import io
import wave
from pathlib import Path

from piper import PiperVoice

from app.config import settings

_voices: dict[str, PiperVoice] = {}


def _get_voice(voice_name: str) -> PiperVoice:
    if voice_name not in _voices:
        model_path = Path(settings.piper_models_dir) / f"{voice_name}.onnx"
        if not model_path.exists():
            raise FileNotFoundError(
                f"Piper model not found: {model_path}\n"
                "Run scripts/download_models.sh to download voices."
            )
        _voices[voice_name] = PiperVoice.load(str(model_path))
    return _voices[voice_name]


def synthesize(text: str, language: str) -> bytes:
    """Synthesize text to WAV bytes. language: 'en' or 'zh'."""
    voice_name = settings.piper_voice_en if language == "en" else settings.piper_voice_zh
    voice = _get_voice(voice_name)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    return buf.getvalue()
