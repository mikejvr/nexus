"""
timestamps.py

Phase‑1 deterministic timestamp utilities.

Phase‑1 rules:
  - ABSOLUTELY NO wall‑clock timestamps
  - ABSOLUTELY NO timezone dependence
  - ABSOLUTELY NO datetime.now(), time.time(), or OS clock access
  - Genesis timestamp is fixed and constitutional
  - All timestamps must be deterministic, stable, and environment‑independent

This module provides:
  - GENESIS_TIMESTAMP: the canonical Phase‑1 timestamp
  - get_genesis_timestamp(): accessor for deterministic use

This file MUST remain stable forever.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Canonical Genesis Timestamp (constitutionally locked)
# ---------------------------------------------------------------------------

GENESIS_TIMESTAMP: str = "2026-01-01T00:00:00Z"


def get_genesis_timestamp() -> str:
    """
    Return the canonical Phase‑1 genesis timestamp.

    This is the ONLY timestamp allowed in Phase‑1.
    It is deterministic, stable, and environment‑independent.

    Returns
    -------
    str
        The canonical genesis timestamp.
    """
    return GENESIS_TIMESTAMP
