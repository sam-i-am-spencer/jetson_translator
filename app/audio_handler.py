import io
import numpy as np
import sounddevice as sd
import soundfile as sf


def record_audio(device: str, sample_rate: int, channels: int) -> np.ndarray:
    """Record audio from device until stop_event is set. Returns float32 numpy array."""
    chunks = []

    def callback(indata, frames, time, status):
        chunks.append(indata.copy())

    with sd.InputStream(
        device=device,
        samplerate=sample_rate,
        channels=channels,
        dtype="float32",
        callback=callback,
    ):
        # Caller controls duration via stop_event — this blocks until context exits
        # For push-to-talk, the caller opens this as a context manager externally.
        # Simple synchronous usage: call record_while_held() instead.
        pass

    return np.concatenate(chunks, axis=0) if chunks else np.array([], dtype="float32")


def record_while_held(
    device: str,
    sample_rate: int,
    channels: int,
    stop_event,
) -> np.ndarray:
    """Record from device until stop_event is set. Blocks. Returns float32 array."""
    chunks = []

    def callback(indata, frames, time, status):
        if not stop_event.is_set():
            chunks.append(indata.copy())

    with sd.InputStream(
        device=device,
        samplerate=sample_rate,
        channels=channels,
        dtype="float32",
        callback=callback,
    ):
        stop_event.wait()

    return np.concatenate(chunks, axis=0).flatten() if chunks else np.array([], dtype="float32")


def _resample(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio using linear interpolation (no extra dependencies)."""
    if orig_sr == target_sr:
        return data
    n_samples = int(len(data) * target_sr / orig_sr)
    return np.interp(
        np.linspace(0, len(data) - 1, n_samples),
        np.arange(len(data)),
        data,
    ).astype(np.float32)


def play_audio_bytes(audio_bytes: bytes, device: str) -> None:
    """Play WAV bytes through device, resampling to device native rate if needed."""
    buf = io.BytesIO(audio_bytes)
    data, sr = sf.read(buf, dtype="float32")
    device_info = sd.query_devices(device, "output")
    native_sr = int(device_info["default_samplerate"])
    if sr != native_sr:
        data = _resample(data, sr, native_sr)
    sd.play(data, samplerate=native_sr, device=device, blocking=True)


def list_devices() -> None:
    """Print available audio devices — useful for finding card names/indices."""
    print(sd.query_devices())
