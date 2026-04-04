"""
WebInputHandler — push-to-talk via WebSocket.
Phone/browser connects to ws://<jetson-ip>:8080/ws and sends:
  {"action": "press",   "key": "1"}  — button held down
  {"action": "release", "key": "1"}  — button released
Server broadcasts status back to all connected clients.
"""
import asyncio
import threading

from app.input_handler import InputHandler


class WebInputHandler(InputHandler):

    def __init__(self):
        self._lock = threading.Lock()
        self._press_events: dict[str, threading.Event] = {}
        self._release_events: dict[str, threading.Event] = {}
        self._busy = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._clients: list = []
        self._clients_lock = threading.Lock()

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    # ── called from async (WebSocket handler) ────────────────────────────────

    async def connect(self, ws) -> None:
        with self._clients_lock:
            self._clients.append(ws)
        await ws.send_json({"type": "status", "value": "idle"})

    async def disconnect(self, ws) -> None:
        with self._clients_lock:
            self._clients.discard(ws) if hasattr(self._clients, 'discard') else None
            if ws in self._clients:
                self._clients.remove(ws)

    async def _broadcast(self, data: dict) -> None:
        with self._clients_lock:
            clients = list(self._clients)
        for ws in clients:
            try:
                await ws.send_json(data)
            except Exception:
                pass

    def on_press(self, key: str) -> bool:
        """Returns True if recording started, False if already busy."""
        with self._lock:
            if self._busy:
                return False
            self._busy = True
            if key in self._press_events:
                self._press_events[key].set()
        return True

    def on_release(self, key: str) -> None:
        with self._lock:
            if key in self._release_events:
                self._release_events[key].set()
                del self._release_events[key]
            self._busy = False
        self._push({"type": "status", "value": "idle"})

    # ── called from channel threads ───────────────────────────────────────────

    def notify(self, status: str) -> None:
        self._push({"type": "status", "value": status})

    def show_transcript(self, text: str, translation: str = "") -> None:
        self._push({"type": "transcript", "text": text, "translation": translation})

    def wait_for_press(self, key: str) -> threading.Event:
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
        pass

    # ── internal ─────────────────────────────────────────────────────────────

    def _push(self, data: dict) -> None:
        if self._loop and not self._loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._broadcast(data), self._loop)
