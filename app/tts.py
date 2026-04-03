"""
TTS:
  English  — piper-tts (local, en_US-lessac-medium)
  Chinese  — Azure Cognitive Services Neural TTS (zh-TW-HsiaoChenNeural)

Piper voices are downloaded via scripts/download_models.sh.
Expected layout:
  models/piper/en_US-lessac-medium.onnx
  models/piper/en_US-lessac-medium.onnx.json
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


def _synthesize_azure(text: str) -> bytes:
    """Synthesize Chinese text via Azure Neural TTS. Returns WAV bytes."""
    import azure.cognitiveservices.speech as speechsdk

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.azure_tts_key,
        region=settings.azure_tts_region,
    )
    speech_config.speech_synthesis_voice_name = settings.azure_voice_zh
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None
    )
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return bytes(result.audio_data)
    raise RuntimeError(
        f"Azure TTS failed: {result.reason} — {result.cancellation_details.error_details if result.reason == speechsdk.ResultReason.Canceled else ''}"
    )


def synthesize(text: str, language: str) -> bytes:
    """Synthesize text to WAV bytes. language: 'en' or 'zh'."""
    if language == "zh":
        return _synthesize_azure(text)

    voice_name = settings.piper_voice_en
    voice = _get_voice(voice_name)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    return buf.getvalue()
