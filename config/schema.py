"""Typed schema for the host config. Loaded once at bootstrap, validated with pydantic."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class HostConfig(BaseModel):
    name: str = "ai-architecture-render-generator"
    api_version: str = "1.2"
    allow_unsigned_extensions: bool = True
    extension_dirs: list[Path] = Field(default_factory=lambda: [Path("extensions")])
    hot_reload: bool = True


class RenderConfig(BaseModel):
    default_renderer: str = "blueprint"
    output_dir: Path = Path("renders")
    image_format: Literal["png", "webp", "exr"] = "png"
    resolution: tuple[int, int] = (2048, 1536)
    dpi: int = 300


class ModelBrokerConfig(BaseModel):
    mirror: str = "https://models.ai-architecture-render-generator.dev/v1"
    cache_dir: Path = Path("models/weights")
    prefer_gpu: bool = False
    max_concurrent: int = 2


class CacheConfig(BaseModel):
    dir: Path = Path("plugins/__cache__")
    max_entries: int = 512
    ttl_seconds: int = 86_400


class IpcConfig(BaseModel):
    pipe_name: str = "aarg_host_v1"
    bind: Literal["loopback", "any"] = "loopback"


class TelemetryConfig(BaseModel):
    enabled: bool = False
    endpoint: str = ""


class RootConfig(BaseModel):
    host: HostConfig = Field(default_factory=HostConfig)
    render: RenderConfig = Field(default_factory=RenderConfig)
    model_broker: ModelBrokerConfig = Field(default_factory=ModelBrokerConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    ipc: IpcConfig = Field(default_factory=IpcConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)