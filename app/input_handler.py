"""
Input handler abstraction.
Currently implemented with pynput (no root required).
To switch to GPIO switches, implement a GPIOInputHandler with the same interface
and swap it in main.py.
"""
import threading
from abc import ABC, abstractmethod

from pynput import keyboard


class InputHandler(ABC):
    @abstractmethod
    def wait_for_press(self, key_or_pin: str) -> threading.Event:
        """Return a stop_event that gets set when the key/button is released."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...


class KeyboardInputHandler(InputHandler):
    """Push-to-talk using keyboard keys. Works without root via pynput."""

    def __init__(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()
        self._press_events: dict[str, threading.Event] = {}
        self._release_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def _key_char(self, key) -> str | None:
        try:
            return key.char
        except AttributeError:
            return None

    def _on_press(self, key):
        char = self._key_char(key)
        if char is None:
            return
        with self._lock:
            if char in self._press_events:
                self._press_events[char].set()

    def _on_release(self, key):
        char = self._key_char(key)
        if char is None:
            return
        with self._lock:
            if char in self._release_events:
                self._release_events[char].set()

    def wait_for_press(self, key: str) -> threading.Event:
        """Block until key is pressed, then return an Event that fires on release."""
        press_event = threading.Event()
        release_event = threading.Event()
        with self._lock:
            self._press_events[key] = press_event
            self._release_events[key] = release_event
        press_event.wait()
        with self._lock:
            del self._press_events[key]
        return release_event

    def cleanup(self) -> None:
        self._listener.stop()


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
