"""
healthcheck.py

Minimal Phase‑1 health probe for the deterministic substrate.

This module verifies:
  - canonical_json() is stable
  - compute_hash() is stable
  - shard_writer can perform a dry-run roundtrip
  - no nondeterministic behavior is detected

This is NOT a governance healthcheck (Phase‑5).
This is NOT a lineage healthcheck (Phase‑4).
This is NOT a distributed healthcheck (Phase‑6).

This is a substrate‑level integrity probe.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, Any

from src.phase1.canonical.canonical_json import canonical_json
from src.phase1.canonical.hashing import compute_hash
from src.phase1.shard.shard_writer import write_shard


def _check_canonical_json() -> bool:
    """
    Verify canonical JSON roundtrip stability.
    """
    sample = {"b": 2, "a": 1}
    first = canonical_json(sample)
    reparsed = canonical_json({"a": 1, "b": 2})
    return first == reparsed


def _check_hash_stability() -> bool:
    """
    Verify hashing is stable across identical objects.
    """
    obj1 = {"x": 1, "y": 2}
    obj2 = {"y": 2, "x": 1}
    return compute_hash(obj1) == compute_hash(obj2)


def _check_shard_roundtrip() -> bool:
    """
    Write a temporary shard and ensure it is produced deterministically.
    """
    payload: Dict[str, Any] = {"foo": "bar", "value": 123}

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shard_path = write_shard(
            root,
            extractor="healthcheck",
            asset_id="hc",
            payload=payload,
        )

        if not shard_path.exists():
            return False

        # Write again and ensure same filename
        shard_path2 = write_shard(
            root,
            extractor="healthcheck",
            asset_id="hc",
            payload=payload,
        )

        return shard_path.name == shard_path2.name


def run_healthcheck() -> Dict[str, bool]:
    """
    Run all Phase‑1 substrate health checks.

    Returns
    -------
    dict
        Mapping of check_name -> boolean result.
    """
    return {
        "canonical_json_stable": _check_canonical_json(),
        "hash_stable": _check_hash_stability(),
        "shard_roundtrip_deterministic": _check_shard_roundtrip(),
    }


def is_healthy() -> bool:
    """
    Return True if all health checks pass.
    """
    results = run_healthcheck()
    return all(results.values())
