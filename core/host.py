"""The host loop. Loads extensions, drives the scheduler, exposes a command surface."""
from __future__ import annotations

import logging
from pathlib import Path

from config.schema import RootConfig
from core.loader import ExtensionLoader
from core.registry import PluginRegistry
from core.scheduler import RenderScheduler
from models.render_request import RenderRequest
from models.render_result import RenderResult

LOG = logging.getLogger("aarg.host")


class Host:
    """Owns the lifecycle of every plugin and the render queue.

    Single-threaded dispatch by design; concurrency lives inside the scheduler's
    worker pool. The host itself is cheap to construct and cheap to tear down,
    which keeps hot-reload honest.
    """

    def __init__(self, config: RootConfig, repo_root: Path) -> None:
        self._config = config
        self._repo_root = repo_root
        self._registry = PluginRegistry(api_version=config.host.api_version)
        self._loader = ExtensionLoader(
            registry=self._registry,
            allow_unsigned=config.host.allow_unsigned_extensions,
        )
        self._scheduler = RenderScheduler(
            registry=self._registry,
            default_renderer=config.render.default_renderer,
            max_concurrent=config.model_broker.max_concurrent,
        )

    def boot(self) -> None:
        for rel in self._config.host.extension_dirs:
            ext_dir = (self._repo_root / rel).resolve()
            if not ext_dir.is_dir():
                LOG.warning("extension dir missing: %s", ext_dir)
                continue
            self._loader.discover(ext_dir)
        LOG.info("host booted with %d plugins", len(self._registry))

    def reload(self) -> None:
        for plugin in self._registry.all():
            try:
                plugin.teardown()
            except Exception:  # noqa: BLE001 — teardown must never block reload
                LOG.exception("teardown failed for %s", getattr(plugin, "id", "?"))
        self._registry.clear()
        self.boot()

    def render(self, request: RenderRequest) -> RenderResult:
        return self._scheduler.submit(request)

    def shutdown(self) -> None:
        self._scheduler.drain()
        for plugin in self._registry.all():
            try:
                plugin.teardown()
            except Exception:  # noqa: BLE001
                LOG.exception("teardown failed during shutdown")