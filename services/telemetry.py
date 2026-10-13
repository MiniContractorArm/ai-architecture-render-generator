"""Opt-in, fire-and-forget telemetry. No-op unless `telemetry.enabled` is true."""
from __future__ import annotations

import logging
import threading
import urllib.request

from config.schema import TelemetryConfig

LOG = logging.getLogger("aarg.telemetry")


class Telemetry:
    def __init__(self, config: TelemetryConfig) -> None:
        self._config = config

    def emit(self, event: str, payload: dict[str, object]) -> None:
        if not self._config.enabled or not self._config.endpoint:
            return
        threading.Thread(
            target=self._post, args=(event, payload), daemon=True
        ).start()

    def _post(self, event: str, payload: dict[str, object]) -> None:
        import json
        body = json.dumps({"event": event, "payload": payload}).encode("utf-8")
        req = urllib.request.Request(
            self._config.endpoint, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            urllib.request.urlopen(req, timeout=5).read()
        except Exception:  # noqa: BLE001 — telemetry must never surface
            LOG.debug("telemetry drop: %s", event)