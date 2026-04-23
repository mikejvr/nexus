"""
Phase-1 shard writer

Canonical Phase-1 shard schema:

{
  "extractor": "3ds_dna",
  "asset_id": "2006-sow-Intro-3D-Animation-Ass-1-Name01.3ds",
  "schema_version": "1",
  "extractor_version": "1",
  "metadata": {
      "normalized_hash": "<sha256 of payload>",
      "deterministic_name": "assets__3ds_dna__2006-sow-Intro-3D-Animation-Ass-1-Name01.3ds__<hash>",
      "source_file": "tests/data/assets/...",
      "created_at": "0000-01-01T00:00:00Z"
  },
  "payload": {
      ... extractor technical payload ...
  }
}

No lineage, audit, summaries, or other Phase-2+ fields.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Any, Dict

from src.phase1.utils.file_io import ensure_dir, write_json_canonical
from src.phase1.canonical.canonical_json import canonical_json
from src.phase1.canonical.hashing import compute_hash
from logging import getLogger

LOGGER = getLogger(__name__)

SCHEMA_VERSION = "1"


def _normalized_payload_hash(payload: Dict[str, Any]) -> str:
    """
    Compute a deterministic hash of the payload.

    Delegates to the Phase‑1 canonical hashing substrate so that
    writer and invariant checker share the exact same definition.
    """
    return compute_hash(payload)


def _deterministic_name(extractor: str, asset_id: str, normalized_hash: str) -> str:
    """
    Deterministic shard name component (without directory or extension).
    """
    return f"{extractor}__{asset_id}__{normalized_hash}"


def build_phase1_shard(
    *,
    extractor: str,
    extractor_version: str,
    asset_id: str,
    source_file: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a Phase-1 shard object from extractor output.

    This function is pure and deterministic:
    - No wall-clock time
    - No randomness
    - All derived fields depend only on inputs
    """
    normalized_hash = _normalized_payload_hash(payload)
    deterministic_name = _deterministic_name(extractor, asset_id, normalized_hash)

    shard: Dict[str, Any] = {
        "extractor": extractor,
        "asset_id": asset_id,
        "schema_version": SCHEMA_VERSION,
        "extractor_version": extractor_version,
        "metadata": {
            "normalized_hash": normalized_hash,
            "deterministic_name": deterministic_name,
            "source_file": source_file,
            # Fixed, deterministic placeholder to avoid time-based nondeterminism
            "created_at": "0000-01-01T00:00:00Z",
        },
        "payload": payload,
    }

    return shard


def write_phase1_shard(
    *,
    extractor: str,
    extractor_version: str,
    asset_id: str,
    source_file: str,
    payload: Dict[str, Any],
    out_root: str,
) -> Path:
    """
    Build and write a Phase-1 shard to disk.

    Returns:
        Absolute path to the written shard file.
    """
    shard = build_phase1_shard(
        extractor=extractor,
        extractor_version=extractor_version,
        asset_id=asset_id,
        source_file=source_file,
        payload=payload,
    )

    normalized_hash = shard["metadata"]["normalized_hash"]
    deterministic_name = shard["metadata"]["deterministic_name"]

    # Directory layout: <out_root>/shards/assets/<deterministic_name>.json
    shards_dir = os.path.join(out_root, "shards", "assets")
    ensure_dir(shards_dir)

    shard_path = Path(shards_dir) / f"{deterministic_name}.json"

    LOGGER.info(
        "Writing Phase-1 shard",
        extra={
            "extractor": extractor,
            "asset_id": asset_id,
            "normalized_hash": normalized_hash,
            "shard_path": shard_path,
        },
    )

    write_json_canonical(shard_path, shard)
    return shard_path
