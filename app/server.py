"""
FastAPI server — serves the web UI and WebSocket endpoint.
"""
import asyncio
import pathlib

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

_STATIC = pathlib.Path(__file__).parent / "static"


def create_app(input_handler) -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    async def _startup():
        input_handler.set_loop(asyncio.get_running_loop())

    @app.get("/")
    async def index():
        return HTMLResponse((_STATIC / "index.html").read_text())

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket):
        await ws.accept()
        await input_handler.connect(ws)
        try:
            while True:
                try:
                    data = await ws.receive_json()
                except Exception:
                    break
                action = data.get("action")
                key = data.get("key")
                if action == "press":
                    if not input_handler.on_press(key):
                        await ws.send_json({"type": "status", "value": "busy"})
                elif action == "release":
                    input_handler.on_release(key)
        except WebSocketDisconnect:
            pass
        finally:
            await input_handler.disconnect(ws)

    return app
