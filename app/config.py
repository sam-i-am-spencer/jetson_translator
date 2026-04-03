from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Audio device names as seen by PortAudio/sounddevice
    # Run: python3 -c "import sounddevice; print(sounddevice.query_devices())"
    mic_en: str = "Blue Snowball"       # English mic input
    mic_zh: str = "USB PnP Sound Device"  # Chinese mic input (C-Media, lapel mic)
    out_en: str = "USB PnP Sound Device"  # English speaker output (C-Media)
    out_zh: str = "USB Audio CODEC"       # Chinese speaker output (TI CODEC)
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
