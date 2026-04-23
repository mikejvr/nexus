"""
shard_merger.py — Phase‑1 deterministic shard merger

Phase‑1 rules:
- No hashing
- No canonical JSON
- No timestamps
- No lineage mutation
- No metadata injection
- No extractor_version / schema_version logic
- No multi‑extractor payload merging
- No inference
- No nondeterministic ordering

Phase‑1 shards contain:
  asset_type
  format
  family
  structural_summary
  content_summary
  lineage
  audit
  raw_features

The Phase‑1 merger:
- Loads shards
- Ensures invariants across required fields
- Merges ONLY structural_summary, content_summary, raw_features
- Never overwrites keys
- Never introduces new fields
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List

from .shard_validator import validate_shard_structure


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def merge_shards(shard_paths: List[Path]) -> Dict[str, Any]:
    """
    Deterministically merge Phase‑1 shards.

    Phase‑1 merge semantics:
      - All shards must share identical:
            asset_type, format, family
      - structural_summary fields must not conflict
      - content_summary fields must not conflict
      - raw_features keys must not conflict
      - lineage and audit are taken from the first shard
      - No hashing, no metadata, no timestamps

    Returns a merged Phase‑1 shard object.
    """

    if not shard_paths:
        raise ValueError("merge_shards: no shard paths provided")

    # Deterministic ordering of input paths
    ordered_paths = sorted(shard_paths, key=lambda p: p.as_posix())

    # Load + validate shards
    shards = [_load_and_validate(p) for p in ordered_paths]

    # Extract invariants from first shard
    base = shards[0]
    asset_type = base["asset_type"]
    format_ = base["format"]
    family = base["family"]

    # Enforce invariants across all shards
    for shard in shards:
        _assert_invariant(shard, "asset_type", asset_type)
        _assert_invariant(shard, "format", format_)
        _assert_invariant(shard, "family", family)

    # Deterministic merge containers
    merged_struct: Dict[str, Any] = {}
    merged_content: Dict[str, Any] = {}
    merged_raw: Dict[str, Any] = {}

    # Merge sections deterministically
    for shard in shards:
        _merge_section(merged_struct, shard["structural_summary"], "structural_summary")
        _merge_section(merged_content, shard["content_summary"], "content_summary")
        _merge_section(merged_raw, shard.get("raw_features", {}), "raw_features")

    # Build merged shard (Phase‑1 envelope)
    merged = {
        "asset_type": asset_type,
        "format": format_,
        "family": family,
        "structural_summary": merged_struct,
        "content_summary": merged_content,
        "lineage": base["lineage"],   # Phase‑1: lineage is not merged
        "audit": base["audit"],       # Phase‑1: audit is not merged
        "raw_features": merged_raw,
    }

    return merged


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_and_validate(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            shard = json.load(f)
    except Exception as e:
        raise ValueError(f"failed to load shard '{path}': {e}")

    ok, errors = validate_shard_structure(shard)
    if not ok:
        raise ValueError(f"invalid shard '{path}': {errors}")

    return shard


def _assert_invariant(shard: Dict[str, Any], field: str, expected: Any) -> None:
    actual = shard.get(field)
    if actual != expected:
        raise ValueError(
            f"merge_shards: invariant mismatch for '{field}': expected={expected}, got={actual}"
        )


def _merge_section(target: Dict[str, Any], incoming: Dict[str, Any], section: str) -> None:
    # Deterministic key ordering
    for key in sorted(incoming.keys()):
        if key in target:
            raise ValueError(
                f"merge_shards: duplicate key '{key}' in section '{section}'"
            )
        target[key] = incoming[key]
