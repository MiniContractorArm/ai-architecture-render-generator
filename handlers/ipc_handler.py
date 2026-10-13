"""Loopback named-pipe handler. Lets the desktop shell drive the host without a rebuild."""
from __future__ import annotations

import json
import logging
import threading
from typing import Any

from core.host import Host
from models.render_request import RenderRequest

LOG = logging.getLogger("aarg.ipc")


class IpcHandler:
    """Line-delimited JSON over a named pipe (Windows) or unix socket (dev).

    Protocol: one JSON object per line. Request: `{"cmd": "render", "brief": "..."}`.
    Response: `{"ok": true, "artifacts": [...]}` or `{"ok": false, "error": "..."}`.
    """

    def __init__(self, host: Host, pipe_name: str) -> None:
        self._host = host
        self._pipe_name = pipe_name
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._serve, name="aarg-ipc", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _serve(self) -> None:
        try:
            import win32pipe  # type: ignore[import-not-found]
        except ImportError:
            LOG.info("win32pipe unavailable; IPC disabled on this platform")
            return
        while not self._stop.is_set():
            handle = win32pipe.CreateNamedPipe(
                rf"\\.\pipe\{self._pipe_name}",
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                1, 65536, 65536, 0, None,
            )
            try:
                win32pipe.ConnectNamedPipe(handle, None)
                raw = win32pipe.ReadFile(handle, 65536, None)[0]
                self._dispatch(raw, handle)
            except Exception:  # noqa: BLE001 — IPC boundary
                LOG.exception("ipc dispatch failed")
            finally:
                win32pipe.DisconnectNamedPipe(handle)
                win32pipe.CloseHandle(handle)

    def _dispatch(self, raw: bytes, handle: Any) -> None:
        try:
            msg = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._reply(handle, {"ok": False, "error": "bad json"})
            return
        cmd = msg.get("cmd")
        if cmd == "render":
            result = self._host.render(RenderRequest(**{k: v for k, v in msg.items() if k != "cmd"}))
            self._reply(handle, result.model_dump(mode="json"))
        elif cmd == "list-plugins":
            self._reply(handle, {"ok": True, "plugins": self._host._registry.ids()})  # noqa: SLF001
        else:
            self._reply(handle, {"ok": False, "error": f"unknown cmd {cmd!r}"})

    @staticmethod
    def _reply(handle: Any, payload: dict[str, Any]) -> None:
        import win32file  # type: ignore[import-not-found]
        win32file.WriteFile(handle, json.dumps(payload).encode("utf-8"))