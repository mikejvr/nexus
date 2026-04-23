"""
shard_reader.py — Phase‑1 deterministic shard reader

Phase‑1 rules:
- No hashing
- No timestamps
- No canonical JSON
- No metadata injection
- No inference
- No mutation of payloads

This reader:
- Loads a shard JSON file from disk
- Validates it structurally (strict Phase‑1)
- Returns the parsed shard and any validation errors
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List

from .shard_validator import validate_shard_structure


def read_shard(path: Path) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Read and validate a Phase‑1 shard from disk.

    Parameters
    ----------
    path : Path
        Shard JSON file path.

    Returns
    -------
    (success: bool, shard: dict, errors: list[str])
      - success == True  → shard is valid, errors is []
      - success == False → shard may be partial, errors populated
    """
    errors: List[str] = []
    shard: Dict[str, Any] = {}

    # ------------------------------------------------------------
    # 1. Deterministic JSON load
    # ------------------------------------------------------------
    try:
        with path.open("r", encoding="utf-8") as f:
            shard = json.load(f)
    except Exception as e:
        return False, {}, [f"read_shard: failed to load '{path}': {e}"]

    # ------------------------------------------------------------
    # 2. Structural validation (strict Phase‑1)
    # ------------------------------------------------------------
    ok, v_errors = validate_shard_structure(shard)
    if not ok:
        errors.extend(v_errors)
        return False, shard, errors

    return True, shard, []
