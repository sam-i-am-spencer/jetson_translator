from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Audio device names or ALSA hw strings (e.g. "hw:1,0" or "USB Audio Device")
    # Run `python -m sounddevice` to list available devices
    sound_card_en: str = "default"  # English channel: record in, playback out
    sound_card_zh: str = "default"  # Chinese channel: record in, playback out
    sample_rate: int = 16000
    audio_channels: int = 1

    # STT - faster-whisper
    whisper_model: str = "base"  # tiny, base, small, medium, large-v3
    whisper_device: str = "cuda"  # cuda or cpu
    whisper_compute_type: str = "float16"  # float16 (GPU) or int8 (CPU)
    whisper_models_dir: str = "./models/whisper"

    # Translation - Helsinki-NLP opus-mt
    translation_models_dir: str = "./models/translation"

    # TTS - piper
    piper_voice_en: str = "en_US-lessac-medium"
    piper_voice_zh: str = "zh_CN-huayan-medium"
    piper_models_dir: str = "./models/piper"

    # Keyboard input (PTT keys)
    key_record_en: str = "1"  # hold to record English → speak Chinese
    key_record_zh: str = "2"  # hold to record Chinese → speak English

    class Config:
        env_file = ".env"


settings = Settings()
