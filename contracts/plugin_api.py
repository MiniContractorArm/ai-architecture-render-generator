"""The one interface every extension implements. Widen this before widening the host."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from models.render_request import RenderRequest
from models.render_result import RenderResult


@runtime_checkable
class RenderPlugin(Protocol):
    """A renderer, grammar, or exporter that the host can drive.

    Implementations must be pure with respect to the request: given the same
    `RenderRequest` and the same seed, they must produce byte-identical output.
    Side effects are limited to writing into the `RenderResult.artifacts`
    paths the host hands them.
    """

    id: str
    api_version: str

    def warmup(self) -> None:
        """Called once after load. Load weights, compile shaders, open handles."""
        ...

    def render(self, request: RenderRequest) -> RenderResult:
        """Produce artifacts for a single request. Must not raise on bad input;
        return a `RenderResult` with `ok=False` and a populated `error` instead."""
        ...

    def teardown(self) -> None:
        """Called on unload or hot-reload. Release everything `warmup` acquired."""
        ...


@runtime_checkable
class GrammarPlugin(Protocol):
    """Optional: turns a natural-language brief into a structured scene graph."""

    id: str
    api_version: str

    def parse(self, brief: str) -> dict[str, object]:
        ...