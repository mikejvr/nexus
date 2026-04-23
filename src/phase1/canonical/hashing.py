"""
hashing.py

Phase‑1 deterministic hashing module.

This module implements the ONLY allowed hashing function for the NEXUS
deterministic substrate. All Phase‑1 components MUST use this function
when computing hashes for:

  - payloads
  - merged payloads
  - diff-normalized payloads
  - shard identity

Hashing rules:
  - SHA‑256
  - Hash is computed over canonical JSON bytes
  - Hex digest, lowercase
  - No salts, no randomness, no timestamps
  - No environment‑dependent behavior

This function MUST remain stable forever.
"""

from __future__ import annotations

import hashlib
from typing import Any

from src.phase1.canonical.canonical_json import canonical_json


def compute_hash(obj: Any) -> str:
    """
    Compute a deterministic SHA‑256 hash of a JSON‑serializable object.

    Hash is computed over:
        canonical_json(obj).encode("utf-8")

    Parameters
    ----------
    obj : Any
        JSON‑serializable Python object.

    Returns
    -------
    str
        Hex‑encoded SHA‑256 hash (lowercase).
    """
    canonical = canonical_json(obj)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
