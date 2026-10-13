"""Result model. Success carries artifacts; failure carries a typed error string."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RenderResult(BaseModel):
    request_id: str
    ok: bool
    artifacts: list[Path] = Field(default_factory=list)
    error: str | None = None
    duration_ms: int = 0
    renderer: str = ""

    @classmethod
    def success(
        cls,
        request_id: str,
        artifacts: list[Path],
        renderer: str,
        duration_ms: int,
    ) -> "RenderResult":
        return cls(
            request_id=request_id,
            ok=True,
            artifacts=artifacts,
            renderer=renderer,
            duration_ms=duration_ms,
        )

    @classmethod
    def failure(cls, request_id: str, error: str) -> "RenderResult":
        return cls(request_id=request_id, ok=False, error=error)