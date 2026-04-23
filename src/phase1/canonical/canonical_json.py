"""
canonical_json.py

Phase‑1 canonical JSON serializer.

This module implements the ONLY allowed JSON serialization format for the
deterministic NEXUS substrate. All Phase‑1 components MUST use this function
when writing JSON to disk or computing hashes.

Canonical JSON rules:
  - UTF‑8
  - sort_keys=True
  - separators=(",", ":")
  - ensure_ascii=False
  - no whitespace
  - stable ordering
  - stable encoding

This function MUST remain stable forever.
"""

from __future__ import annotations

import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """
    Serialize an object into canonical JSON.

    Parameters
    ----------
    obj : Any
        JSON‑serializable Python object.

    Returns
    -------
    str
        Canonical JSON string with deterministic ordering and formatting.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
