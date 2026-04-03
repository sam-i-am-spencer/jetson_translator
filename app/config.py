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
    whisper_model: str = "small"  # tiny, base, small, medium, large-v3
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_models_dir: str = "./models/whisper"

    # Translation - Claude API
    anthropic_api_key: str = ""

    # TTS - English: piper (local)
    piper_voice_en: str = "en_US-lessac-medium"
    piper_models_dir: str = "./models/piper"

    # TTS - Chinese: Azure Neural TTS
    azure_tts_key: str = ""
    azure_tts_region: str = "australiaeast"
    azure_voice_zh: str = "zh-TW-HsiaoChenNeural"

    # Keyboard input (PTT keys)
    key_record_en: str = "1"  # hold to record English → speak Chinese
    key_record_zh: str = "2"  # hold to record Chinese → speak English

    class Config:
        env_file = ".env"


settings = Settings()
