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


def play_audio_bytes(audio_bytes: bytes, device: str, sample_rate: int) -> None:
    """Play raw PCM bytes (wav) through device."""
    buf = io.BytesIO(audio_bytes)
    data, sr = sf.read(buf, dtype="float32")
    sd.play(data, samplerate=sr, device=device, blocking=True)


def list_devices() -> None:
    """Print available audio devices — useful for finding card names/indices."""
    print(sd.query_devices())
