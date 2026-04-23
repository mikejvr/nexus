"""
diff_engine.py — Phase‑1 deterministic structural diff engine

Phase‑1 rules:
- No hashing
- No timestamps
- No canonical JSON
- No semantic comparison
- No inference
- No nondeterministic ordering
- No extractor/schema logic

This engine:
- Compares two Phase‑1 shard dicts
- Produces a deterministic structural diff
- Never mutates inputs
- Never reorders user data (only diff output is sorted)
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def diff_shards(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministically diff two Phase‑1 shard objects.

    Returns a dict with:
      {
        "added":    {key: value},
        "removed":  {key: value},
        "modified": {key: (old, new)},
      }

    Diff is structural only:
      - dict keys
      - primitive values
      - lists (order‑sensitive)
      - nested dicts

    No semantic interpretation.
    """

    return _diff_dicts(a, b)


# ---------------------------------------------------------------------------
# Internal deterministic diff functions
# ---------------------------------------------------------------------------

def _diff_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    added: Dict[str, Any] = {}
    removed: Dict[str, Any] = {}
    modified: Dict[str, Tuple[Any, Any]] = {}

    a_keys = set(a.keys())
    b_keys = set(b.keys())

    # Deterministic ordering
    for key in sorted(a_keys - b_keys):
        removed[key] = a[key]

    for key in sorted(b_keys - a_keys):
        added[key] = b[key]

    for key in sorted(a_keys & b_keys):
        av = a[key]
        bv = b[key]

        if _values_equal(av, bv):
            continue

        # Nested dict → recurse
        if isinstance(av, dict) and isinstance(bv, dict):
            nested = _diff_dicts(av, bv)
            if nested["added"] or nested["removed"] or nested["modified"]:
                modified[key] = nested
            continue

        # Lists → order‑sensitive comparison
        if isinstance(av, list) and isinstance(bv, list):
            if av != bv:
                modified[key] = (av, bv)
            continue

        # Primitive mismatch
        modified[key] = (av, bv)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
    }


def _values_equal(a: Any, b: Any) -> bool:
    """
    Deterministic equality check for Phase‑1:
    - No hashing
    - No semantic interpretation
    - Strict structural equality
    """
    if type(a) != type(b):
        return False

    if isinstance(a, dict):
        if a.keys() != b.keys():
            return False
        for k in a.keys():
            if not _values_equal(a[k], b[k]):
                return False
        return True

    if isinstance(a, list):
        if len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if not _values_equal(x, y):
                return False
        return True

    return a == b
