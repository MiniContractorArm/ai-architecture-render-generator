"""Fetches + caches model weights for renderers that need them.

Extensions never hit the network directly; they ask the broker. The broker
pins to a configured mirror, caches under `models/weights/`, and refuses to
serve a file whose sha256 doesn't match the manifest's declared hash.
"""
from __future__ import annotations

import hashlib
import logging
import urllib.request
from pathlib import Path

from config.schema import ModelBrokerConfig

LOG = logging.getLogger("aarg.model_broker")
_CHUNK = 1 << 20


class ModelBrokerError(RuntimeError):
    pass


class ModelBroker:
    def __init__(self, config: ModelBrokerConfig) -> None:
        self._config = config
        self._config.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self, name: str, sha256: str) -> Path:
        dest = self._config.cache_dir / name
        if dest.is_file() and self._digest(dest) == sha256:
            return dest
        url = f"{self._config.mirror.rstrip('/')}/{name}"
        LOG.info("fetching %s", url)
        tmp = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(url, timeout=60) as resp, tmp.open("wb") as fh:
            while chunk := resp.read(_CHUNK):
                fh.write(chunk)
        if self._digest(tmp) != sha256:
            tmp.unlink(missing_ok=True)
            raise ModelBrokerError(f"sha256 mismatch for {name}")
        tmp.replace(dest)
        return dest

    @staticmethod
    def _digest(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(_CHUNK), b""):
                h.update(chunk)
        return h.hexdigest()