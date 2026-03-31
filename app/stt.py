import numpy as np
from faster_whisper import WhisperModel

from app.config import settings

_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            download_root=settings.whisper_models_dir,
        )
    return _model


def transcribe(audio: np.ndarray, language: str) -> str:
    """Transcribe audio array to text. language: 'en' or 'zh'."""
    model = get_model()
    segments, _ = model.transcribe(
        audio,
        language=language,
        beam_size=5,
        vad_filter=True,
    )
    return " ".join(seg.text.strip() for seg in segments).strip()
