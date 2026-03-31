"""
Input handler abstraction.
Currently implemented with the `keyboard` library (push-to-talk via keyboard keys).
To switch to GPIO switches, implement a GPIOInputHandler with the same interface
and swap it in main.py.
"""
import threading
from abc import ABC, abstractmethod

import keyboard


class InputHandler(ABC):
    @abstractmethod
    def wait_for_press(self, key_or_pin: str) -> threading.Event:
        """Return a stop_event that gets set when the key/button is released."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...


class KeyboardInputHandler(InputHandler):
    """Push-to-talk using keyboard keys. Requires root/sudo on Linux."""

    def wait_for_press(self, key: str) -> threading.Event:
        """Block until key is pressed, then return an Event that fires on release."""
        keyboard.wait(key)  # blocks until pressed
        stop_event = threading.Event()

        def on_release(e):
            if e.name == key:
                stop_event.set()

        keyboard.on_release(on_release)
        return stop_event

    def cleanup(self) -> None:
        keyboard.unhook_all()


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
