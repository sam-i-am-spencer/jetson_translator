"""
Input handler abstraction.
KeyboardInputHandler uses raw terminal input (termios) — no root or display required.
To switch to GPIO switches, implement a GPIOInputHandler with the same interface
and swap it in main.py.
"""
import os
import select
import sys
import termios
import threading
import time
import tty
from abc import ABC, abstractmethod

# Must be longer than the kernel's initial key-repeat delay (~250 ms default)
_RELEASE_TIMEOUT = 0.35


class InputHandler(ABC):
    @abstractmethod
    def wait_for_press(self, key_or_pin: str) -> threading.Event:
        """Return a stop_event that gets set when the key/button is released."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...


class KeyboardInputHandler(InputHandler):
    """Push-to-talk via raw terminal — no root or X11 required."""

    def __init__(self):
        self._fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(self._fd)
        # setcbreak: single-char input without needing Enter, but keeps Ctrl+C
        tty.setcbreak(self._fd)

        self._lock = threading.Lock()
        self._press_events: dict[str, threading.Event] = {}
        self._release_events: dict[str, threading.Event] = {}
        self._last_seen: dict[str, float] = {}

        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        while True:
            r, _, _ = select.select([self._fd], [], [], 0.05)
            now = time.monotonic()

            if r:
                try:
                    ch = os.read(self._fd, 1).decode("utf-8", errors="ignore")
                except OSError:
                    break

                if ch == "\x03":  # Ctrl+C
                    with self._lock:
                        for e in self._release_events.values():
                            e.set()
                    raise KeyboardInterrupt

                with self._lock:
                    self._last_seen[ch] = now
                    if ch in self._press_events:
                        self._press_events[ch].set()

            # Detect releases by autorepeat timeout
            with self._lock:
                for key, last_time in list(self._last_seen.items()):
                    if now - last_time > _RELEASE_TIMEOUT:
                        del self._last_seen[key]
                        if key in self._release_events:
                            self._release_events[key].set()
                            del self._release_events[key]

    def wait_for_press(self, key: str) -> threading.Event:
        """Block until key is pressed, return an Event that fires on release."""
        press_event = threading.Event()
        with self._lock:
            self._press_events[key] = press_event

        press_event.wait()

        release_event = threading.Event()
        with self._lock:
            del self._press_events[key]
            self._release_events[key] = release_event

        return release_event

    def cleanup(self) -> None:
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
        print()  # restore cursor to clean line


# --- Future GPIO implementation (skeleton) ---
# class GPIOInputHandler(InputHandler):
#     """Push-to-talk using physical switches via Jetson.GPIO."""
#
#     def __init__(self, pin_map: dict[str, int]):
#         import Jetson.GPIO as GPIO
#         self._GPIO = GPIO
#         self._pin_map = pin_map  # e.g. {"en": 12, "zh": 13}
#         GPIO.setmode(GPIO.BOARD)
#         for pin in pin_map.values():
#             GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#
#     def wait_for_press(self, key: str) -> threading.Event:
#         pin = self._pin_map[key]
#         self._GPIO.wait_for_edge(pin, self._GPIO.FALLING)
#         stop_event = threading.Event()
#         def on_release(ch):
#             stop_event.set()
#         self._GPIO.add_event_detect(pin, self._GPIO.RISING, callback=on_release)
#         return stop_event
#
#     def cleanup(self) -> None:
#         self._GPIO.cleanup()
