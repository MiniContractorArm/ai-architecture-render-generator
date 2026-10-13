"""In-memory registry of loaded plugins, keyed by manifest id."""
from __future__ import annotations

from collections.abc import Iterator

from contracts.manifest import ExtensionManifest
from contracts.plugin_api import RenderPlugin


class PluginRegistry:
    def __init__(self, api_version: str) -> None:
        self.api_version = api_version
        self._by_id: dict[str, tuple[ExtensionManifest, RenderPlugin]] = {}

    def register(self, manifest: ExtensionManifest, plugin: RenderPlugin) -> None:
        if manifest.id in self._by_id:
            raise ValueError(f"duplicate plugin id: {manifest.id}")
        self._by_id[manifest.id] = (manifest, plugin)

    def get(self, plugin_id: str) -> RenderPlugin | None:
        entry = self._by_id.get(plugin_id)
        return entry[1] if entry else None

    def manifest(self, plugin_id: str) -> ExtensionManifest | None:
        entry = self._by_id.get(plugin_id)
        return entry[0] if entry else None

    def all(self) -> Iterator[RenderPlugin]:
        for _, plugin in self._by_id.values():
            yield plugin

    def ids(self) -> list[str]:
        return sorted(self._by_id)

    def clear(self) -> None:
        self._by_id.clear()

    def __len__(self) -> int:
        return len(self._by_id)