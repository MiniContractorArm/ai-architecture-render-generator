"""Render queue. Bounded worker pool, per-plugin serialization, deterministic ordering."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from core.registry import PluginRegistry
from models.render_request import RenderRequest
from models.render_result import RenderResult

LOG = logging.getLogger("aarg.scheduler")


class RenderScheduler:
    """Dispatches requests to the plugin named in `request.renderer`.

    Plugins are assumed non-reentrant, so we serialize per plugin id with a
    lock table. Global concurrency is bounded by `max_concurrent`.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        default_renderer: str,
        max_concurrent: int,
    ) -> None:
        self._registry = registry
        self._default = default_renderer
        self._pool = ThreadPoolExecutor(max_workers=max_concurrent, thread_name_prefix="aarg-render")
        self._locks: dict[str, Lock] = {}
        self._locks_guard = Lock()

    def _lock_for(self, plugin_id: str) -> Lock:
        with self._locks_guard:
            return self._locks.setdefault(plugin_id, Lock())

    def submit(self, request: RenderRequest) -> RenderResult:
        plugin_id = request.renderer or self._default
        plugin = self._registry.get(plugin_id)
        if plugin is None:
            return RenderResult.failure(
                request_id=request.request_id,
                error=f"renderer {plugin_id!r} not registered",
            )
        with self._lock_for(plugin_id):
            try:
                return plugin.render(request)
            except Exception as exc:  # noqa: BLE001 — plugin boundary
                LOG.exception("renderer %s raised", plugin_id)
                return RenderResult.failure(request_id=request.request_id, error=str(exc))

    def drain(self) -> None:
        self._pool.shutdown(wait=True, cancel_futures=False)