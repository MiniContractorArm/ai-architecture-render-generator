"""Content-addressed cache for render artifacts. Keyed by (brief, renderer, seed, resolution)."""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path

from config.schema import CacheConfig

LOG = logging.getLogger("aarg.cache")


class RenderCache:
    def __init__(self, config: CacheConfig) -> None:
        self._config = config
        self._config.dir.mkdir(parents=True, exist_ok=True)

    def key(self, brief: str, renderer: str, seed: int, resolution: tuple[int, int]) -> str:
        payload = json.dumps(
            {"brief": brief, "renderer": renderer, "seed": seed, "res": list(resolution)},
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.blake2b(payload, digest_size=16).hexdigest()

    def lookup(self, key: str) -> Path | None:
        entry = self._config.dir / f"{key}.json"
        if not entry.is_file():
            return None
        meta = json.loads(entry.read_text(encoding="utf-8"))
        if time.time() - meta["ts"] > self._config.ttl_seconds:
            entry.unlink(missing_ok=True)
            return None
        artifact = Path(meta["artifact"])
        return artifact if artifact.is_file() else None

    def store(self, key: str, artifact: Path) -> None:
        entry = self._config.dir / f"{key}.json"
        entry.write_text(
            json.dumps({"ts": time.time(), "artifact": str(artifact)}),
            encoding="utf-8",
        )
        self._evict()

    def _evict(self) -> None:
        entries = sorted(self._config.dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        overflow = len(entries) - self._config.max_entries
        for stale in entries[: max(0, overflow)]:
            stale.unlink(missing_ok=True)