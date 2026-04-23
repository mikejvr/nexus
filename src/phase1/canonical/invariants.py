"""
invariants.py

Authoritative Phase‑1 deterministic invariants for the NEXUS substrate.

These invariants define the non‑negotiable rules that guarantee:
  - byte‑stable canonical JSON
  - deterministic hashing
  - deterministic shard filenames
  - deterministic shard contents
  - deterministic merging and diffing
  - deterministic lineage
  - environment‑independent execution

This module contains:
  - A structured list of invariants
  - Helper functions for validation modules
  - No side effects
  - No nondeterministic behavior

This file MUST remain stable forever.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------------
# Authoritative Invariant Definitions
# ---------------------------------------------------------------------------

INVARIANTS: Dict[str, str] = {
    "canonical_json_stable": (
        "Canonical JSON must be byte‑stable: sort_keys=True, separators=(',', ':'), "
        "ensure_ascii=False, UTF‑8 encoding, no whitespace, no indentation."
    ),

    "hash_stable": (
        "Hashes must be computed over canonical JSON bytes only, using SHA‑256, "
        "hex‑encoded lowercase, with no salts, randomness, or environment‑dependent behavior."
    ),

    "filename_deterministic": (
        "Shard filenames must follow <extractor>__<sha256>.json and must be derived "
        "solely from the canonical payload hash."
    ),

    "shard_structure_stable": (
        "Shard structure must contain extractor, asset_id, schema_version, "
        "extractor_version, metadata.normalized_hash, and payload. No extra fields allowed."
    ),

    "no_nondeterministic_fields": (
        "Payload must contain no timestamps, UUIDs, random values, environment‑dependent "
        "values, or volatile fields."
    ),

    "merge_deterministic": (
        "Merging must be deterministic: input order must not affect output, and merged "
        "payload must be canonicalized before hashing."
    ),

    "diff_deterministic": (
        "Diffing must be deterministic: comparing canonical payloads only, with stable "
        "ordering and stable diff output."
    ),

    "lineage_idempotent": (
        "Lineage writes must be idempotent: keyed by run_id, no duplicates, no mutation, "
        "no reordering of existing entries."
    ),

    "environment_independent": (
        "Phase‑1 behavior must be identical across machines, OSes, Python versions, "
        "locales, timezones, and hardware architectures."
    ),

    "e2e_repeatable": (
        "Running the same input through Phase‑1 twice must produce identical canonical JSON, "
        "identical hashes, identical shard filenames, identical shard contents, and identical lineage."
    ),
}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def list_invariants() -> List[str]:
    """
    Return a list of invariant keys.
    """
    return list(INVARIANTS.keys())


def describe_invariant(key: str) -> str:
    """
    Return the human‑readable description of an invariant.
    """
    return INVARIANTS.get(key, f"<unknown invariant: {key}>")


def all_invariants() -> Dict[str, str]:
    """
    Return the full invariant dictionary.
    """
    return INVARIANTS.copy()
