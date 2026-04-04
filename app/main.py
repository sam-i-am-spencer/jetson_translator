"""
Jetson Translator — bidirectional EN ↔ ZH speech translator.

Two channels run concurrently in separate threads:
  Channel EN: hold EN→ZH button → record from mic_en → transcribe (EN)
              → translate EN→ZH → synthesize ZH → play on out_zh
  Channel ZH: hold ZH→EN button → record from mic_zh → transcribe (ZH)
              → translate ZH→EN → synthesize EN → play on out_en

Web UI served at http://<jetson-ip>:8080 — open on any phone on the same network.

Usage:
    python -m app.main               # start with web UI
    python -m app.main --list-devices  # list audio devices and exit
"""
import argparse
import logging
import threading

import numpy as np
import sounddevice as sd
import uvicorn

from app.audio_handler import list_devices, play_audio_bytes, record_while_held
from app.config import settings
from app.server import create_app
from app.stt import transcribe
from app.translation import translate
from app.tts import synthesize
from app.web_input_handler import WebInputHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def run_channel(
    name: str,
    record_device: str,
    playback_device: str,
    src_lang: str,
    tgt_lang: str,
    trigger_key: str,
    input_handler,
    stop_app: threading.Event,
) -> None:
    """Run a single translator channel in a loop until stop_app is set."""
    log.info(f"[{name}] Ready")

    while not stop_app.is_set():
        try:
            stop_recording = input_handler.wait_for_press(trigger_key)
            if stop_app.is_set():
                break

            log.info(f"[{name}] Recording...")
            input_handler.notify("recording")
            audio = record_while_held(
                device=record_device,
                target_sample_rate=settings.sample_rate,
                channels=settings.audio_channels,
                stop_event=stop_recording,
            )

            if audio.size < settings.sample_rate * 0.3:
                log.info(f"[{name}] Too short, skipping")
                input_handler.notify("idle")
                continue

            log.info(f"[{name}] Transcribing ({src_lang})...")
            input_handler.notify("translating")
            text = transcribe(audio, language=src_lang)
            if not text:
                log.info(f"[{name}] No speech detected")
                input_handler.notify("idle")
                continue
            log.info(f"[{name}] Transcribed: {text}")

            log.info(f"[{name}] Translating {src_lang}→{tgt_lang}...")
            input_handler.show_transcript(text)
            translated = translate(text, src_lang=src_lang, tgt_lang=tgt_lang)
            log.info(f"[{name}] Translated: {translated}")
            input_handler.show_transcript(text, translated)

            log.info(f"[{name}] Synthesizing ({tgt_lang})...")
            input_handler.notify("synthesizing")
            audio_bytes = synthesize(translated, language=tgt_lang)

            log.info(f"[{name}] Playing on {playback_device}")
            input_handler.notify("playing")
            play_audio_bytes(audio_bytes, device=playback_device)

            input_handler.notify("idle")

        except Exception as e:
            log.error(f"[{name}] Error: {e}", exc_info=True)
            input_handler.notify("idle")


def _play_ready_tone(device: str) -> None:
    try:
        device_info = sd.query_devices(device, "output")
        sr = int(device_info["default_samplerate"])
        t = np.linspace(0, 0.2, int(sr * 0.2), endpoint=False)
        tone = (np.sin(2 * np.pi * 440 * t) * 0.3).astype(np.float32)
        sd.play(tone, samplerate=sr, device=device, blocking=True)
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        return

    log.info("Starting Jetson Translator")
    log.info(f"  EN mic: {settings.mic_en}  EN out: {settings.out_en}")
    log.info(f"  ZH mic: {settings.mic_zh}  ZH out: {settings.out_zh}")

    log.info("Loading models...")
    transcribe(np.zeros(16000, dtype=np.float32), language="en")
    translate("hello", src_lang="en", tgt_lang="zh")
    synthesize("ready", language="en")
    log.info("Models loaded.")

    _play_ready_tone(settings.out_en)
    _play_ready_tone(settings.out_zh)

    input_handler = WebInputHandler()
    stop_app = threading.Event()

    channel_en = threading.Thread(
        target=run_channel,
        name="channel-en",
        daemon=True,
        kwargs=dict(
            name="EN→ZH",
            record_device=settings.mic_en,
            playback_device=settings.out_zh,
            src_lang="en",
            tgt_lang="zh",
            trigger_key=settings.key_record_en,
            input_handler=input_handler,
            stop_app=stop_app,
        ),
    )
    channel_zh = threading.Thread(
        target=run_channel,
        name="channel-zh",
        daemon=True,
        kwargs=dict(
            name="ZH→EN",
            record_device=settings.mic_zh,
            playback_device=settings.out_en,
            src_lang="zh",
            tgt_lang="en",
            trigger_key=settings.key_record_zh,
            input_handler=input_handler,
            stop_app=stop_app,
        ),
    )

    channel_en.start()
    channel_zh.start()

    log.info(f"Web UI: http://0.0.0.0:{args.port}  (open on your phone)")

    try:
        uvicorn.run(create_app(input_handler), host="0.0.0.0", port=args.port, log_level="warning")
    except KeyboardInterrupt:
        pass
    finally:
        stop_app.set()


if __name__ == "__main__":
    main()
