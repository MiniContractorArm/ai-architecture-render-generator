"""Stable hashing for cache keys and seed derivation."""
from __future__ import annotations

import hashlib


def brief_seed(brief: str) -> int:
    """Derive a deterministic 31-bit seed from a brief. Used when request.seed == 0."""
    digest = hashlib.blake2b(brief.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") & 0x7FFF_FFFF