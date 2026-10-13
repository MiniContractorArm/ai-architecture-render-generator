"""One place to configure logging. Rich handler if available, plain otherwise."""
from __future__ import annotations

import logging
import sys


def configure(level: str = "INFO") -> None:
    root = logging.getLogger("aarg")
    root.setLevel(level.upper())
    if root.handlers:
        return
    try:
        from rich.logging import RichHandler
        handler: logging.Handler = RichHandler(rich_tracebacks=True, show_path=False)
    except ImportError:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)