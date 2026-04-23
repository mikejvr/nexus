"""
shard_diff.py — Phase‑1 structural diff

Deterministic, stdlib‑only, structural‑only.

Phase‑1 rules:
- No hashing
- No timestamps
- No entropy
- No semantic / fuzzy comparison
- No logging, no I/O, no side effects

Diff model (minimal, deterministic):
{
  "added":    {<path>: <value>},
  "removed":  {<path>: <value>},
  "changed":  {<path>: {"before": <primitive>, "after": <primitive>}}
}

- <path> is a dot‑separated string (e.g. "structural_summary.width")
- "changed" is emitted only for primitive mismatches
- Nested structures are traversed recursively
"""

from __future__ import annotations
from typing import Any, Dict


DiffResult = Dict[str, Dict[str, Any]]


def diff_payloads(a: Any, b: Any) -> DiffResult:
    """
    Compute a strict, structural diff between two JSON‑serializable payloads.

    Returns:
      {
        "added":   path -> value (present only in b)
        "removed": path -> value (present only in a)
        "changed": path -> {"before": v1, "after": v2} (primitives only)
      }
    """
    result: DiffResult = {
        "added": {},
        "removed": {},
        "changed": {},
    }

    _diff_recursive(a, b, path="", out=result)
    return result


def _diff_recursive(a: Any, b: Any, path: str, out: DiffResult) -> None:
    """
    Internal deterministic recursive diff.

    Dicts  → compare keys, recurse
    Lists  → compare by index, recurse
    Primitives → record changed if unequal
    Type mismatch → removed + added at same path
    """
    # Dict vs dict
    if isinstance(a, dict) and isinstance(b, dict):
        _diff_dicts(a, b, path, out)
        return

    # List vs list
    if isinstance(a, list) and isinstance(b, list):
        _diff_lists(a, b, path, out)
        return

    # Primitive vs primitive
    if _is_primitive(a) and _is_primitive(b):
        if a != b:
            out["changed"][path or "$"] = {"before": a, "after": b}
        return

    # Structural mismatch (dict/list vs primitive or type mismatch)
    key = path or "$"
    out["removed"][key] = a
    out["added"][key] = b


def _diff_dicts(a: Dict[str, Any], b: Dict[str, Any], base_path: str, out: DiffResult) -> None:
    a_keys = set(a.keys())
    b_keys = set(b.keys())

    # Removed keys
    for key in sorted(a_keys - b_keys):
        out["removed"][_join_path(base_path, key)] = a[key]

    # Added keys
    for key in sorted(b_keys - a_keys):
        out["added"][_join_path(base_path, key)] = b[key]

    # Common keys
    for key in sorted(a_keys & b_keys):
        _diff_recursive(a[key], b[key], _join_path(base_path, key), out)


def _diff_lists(a: Any, b: Any, base_path: str, out: DiffResult) -> None:
    len_a = len(a)
    len_b = len(b)
    max_len = max(len_a, len_b)

    for idx in range(max_len):
        path = _join_path(base_path, str(idx))

        if idx >= len_a:
            out["added"][path] = b[idx]
            continue

        if idx >= len_b:
            out["removed"][path] = a[idx]
            continue

        _diff_recursive(a[idx], b[idx], path, out)


def _join_path(base: str, key: str) -> str:
    return key if not base else f"{base}.{key}"


def _is_primitive(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None
