"""
Jetson Translator — bidirectional EN ↔ ZH speech translator.

Two channels run concurrently in separate threads:
  Channel EN: press KEY_RECORD_EN → record from SOUND_CARD_EN → transcribe (EN)
              → translate EN→ZH → synthesize ZH → play on SOUND_CARD_ZH
  Channel ZH: press KEY_RECORD_ZH → record from SOUND_CARD_ZH → transcribe (ZH)
              → translate ZH→EN → synthesize EN → play on SOUND_CARD_EN

Usage:
    python -m app.main           # normal run
    python -m app.main --list-devices  # list audio devices and exit
"""
import argparse
import logging
import threading

from app.audio_handler import list_devices, play_audio_bytes, record_while_held
from app.config import settings
from app.input_handler import KeyboardInputHandler
from app.stt import transcribe
from app.translation import translate
from app.tts import synthesize

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
    log.info(f"[{name}] Ready — hold '{trigger_key}' to speak")

    while not stop_app.is_set():
        try:
            stop_recording = input_handler.wait_for_press(trigger_key)
            if stop_app.is_set():
                break

            log.info(f"[{name}] Recording...")
            audio = record_while_held(
                device=record_device,
                sample_rate=settings.sample_rate,
                channels=settings.audio_channels,
                stop_event=stop_recording,
            )

            if audio.size < settings.sample_rate * 0.3:
                log.info(f"[{name}] Too short, skipping")
                continue

            log.info(f"[{name}] Transcribing ({src_lang})...")
            text = transcribe(audio, language=src_lang)
            if not text:
                log.info(f"[{name}] No speech detected")
                continue
            log.info(f"[{name}] Transcribed: {text}")

            log.info(f"[{name}] Translating {src_lang}→{tgt_lang}...")
            translated = translate(text, src_lang=src_lang, tgt_lang=tgt_lang)
            log.info(f"[{name}] Translated: {translated}")

            log.info(f"[{name}] Synthesizing ({tgt_lang})...")
            audio_bytes = synthesize(translated, language=tgt_lang)

            log.info(f"[{name}] Playing on {playback_device}")
            play_audio_bytes(audio_bytes, device=playback_device)

        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"[{name}] Error: {e}", exc_info=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true", help="List audio devices and exit")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        return

    log.info("Starting Jetson Translator")
    log.info(f"  EN card: {settings.sound_card_en}  ZH card: {settings.sound_card_zh}")
    log.info(f"  Keys: EN={settings.key_record_en}  ZH={settings.key_record_zh}")
    log.info("Press Ctrl+C to quit")

    input_handler = KeyboardInputHandler()
    stop_app = threading.Event()

    channel_en = threading.Thread(
        target=run_channel,
        name="channel-en",
        kwargs=dict(
            name="EN→ZH",
            record_device=settings.sound_card_en,
            playback_device=settings.sound_card_zh,
            src_lang="en",
            tgt_lang="zh",
            trigger_key=settings.key_record_en,
            input_handler=input_handler,
            stop_app=stop_app,
        ),
        daemon=True,
    )
    channel_zh = threading.Thread(
        target=run_channel,
        name="channel-zh",
        kwargs=dict(
            name="ZH→EN",
            record_device=settings.sound_card_zh,
            playback_device=settings.sound_card_en,
            src_lang="zh",
            tgt_lang="en",
            trigger_key=settings.key_record_zh,
            input_handler=input_handler,
            stop_app=stop_app,
        ),
        daemon=True,
    )

    channel_en.start()
    channel_zh.start()

    try:
        channel_en.join()
        channel_zh.join()
    except KeyboardInterrupt:
        log.info("Shutting down...")
        stop_app.set()
        input_handler.cleanup()


if __name__ == "__main__":
    main()
