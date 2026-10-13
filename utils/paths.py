"""Repo-relative path helpers. Everything resolves against the repo root, not cwd."""
from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def renders_dir() -> Path:
    return repo_root() / "renders"


def user_config_path() -> Path:
    import os
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "ai-architecture-render-generator" / "config.toml"
    return Path.home() / ".config" / "ai-architecture-render-generator" / "config.toml"