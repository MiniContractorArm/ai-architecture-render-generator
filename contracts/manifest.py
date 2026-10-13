"""Extension manifest loader. Every extension dir ships a manifest.toml."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ExtensionManifest:
    id: str
    version: str
    api_version: str
    entrypoint: str
    kind: str = "renderer"
    requires: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    @classmethod
    def from_path(cls, manifest_path: Path) -> "ExtensionManifest":
        raw = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        ext = raw.get("extension", raw)
        return cls(
            id=str(ext["id"]),
            version=str(ext["version"]),
            api_version=str(ext["api_version"]),
            entrypoint=str(ext["entrypoint"]),
            kind=str(ext.get("kind", "renderer")),
            requires=tuple(ext.get("requires", ())),
            description=str(ext.get("description", "")),
        )