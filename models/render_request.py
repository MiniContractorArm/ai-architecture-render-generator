"""Request model. Everything the host needs to route + reproduce a render."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    brief: str = Field(..., min_length=1, description="Natural-language architecture brief.")
    renderer: str | None = Field(default=None, description="Plugin id; falls back to config default.")
    seed: int = Field(default=0, description="Deterministic seed. 0 = host picks from brief hash.")
    resolution: tuple[int, int] = (2048, 1536)
    output_dir: Path = Path("renders")
    scene_graph: dict[str, Any] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: uuid4().hex)