"""Discovers extension dirs, validates manifests, imports entrypoints, registers plugins."""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

from contracts.manifest import ExtensionManifest
from core.registry import PluginRegistry

LOG = logging.getLogger("aarg.loader")


class ExtensionLoadError(RuntimeError):
    pass


class ExtensionLoader:
    """Walks an extension dir, loads each `manifest.toml`, imports the entrypoint.

    Importing is done via `importlib.util.spec_from_file_location` so extensions
    don't have to be installed packages — this is what makes `plugins/local/`
    drop-ins work without a rebuild.
    """

    def __init__(self, registry: PluginRegistry, allow_unsigned: bool) -> None:
        self._registry = registry
        self._allow_unsigned = allow_unsigned

    def discover(self, root: Path) -> None:
        for manifest_path in sorted(root.glob("*/manifest.toml")):
            try:
                self._load_one(manifest_path)
            except ExtensionLoadError as exc:
                LOG.error("skipping %s: %s", manifest_path.parent.name, exc)

    def _load_one(self, manifest_path: Path) -> None:
        manifest = ExtensionManifest.from_path(manifest_path)
        if manifest.api_version != self._registry.api_version:
            raise ExtensionLoadError(
                f"api_version {manifest.api_version!r} != host {self._registry.api_version!r}"
            )
        module_name, _, attr = manifest.entrypoint.partition(":")
        module_path = manifest_path.parent / f"{module_name.replace('.', '/')}.py"
        if not module_path.is_file():
            raise ExtensionLoadError(f"entrypoint module not found: {module_path}")

        spec = importlib.util.spec_from_file_location(
            f"aarg_ext_{manifest.id}", module_path
        )
        if spec is None or spec.loader is None:
            raise ExtensionLoadError(f"cannot build import spec for {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        plugin_cls = getattr(module, attr, None)
        if plugin_cls is None:
            raise ExtensionLoadError(f"{attr!r} not found in {module_path}")
        plugin = plugin_cls()
        plugin.warmup()
        self._registry.register(manifest, plugin)
        LOG.info("loaded extension %s v%s", manifest.id, manifest.version)