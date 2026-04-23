"""
ext_dna.py — Phase‑1 shared deterministic helpers

Rules:
- Stdlib only
- Deterministic
- No timestamps
- No randomness
- No environment-dependent fields
- No side effects
- No logging
- No global state
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ------------------------------------------------------------
# Deterministic byte reader
# ------------------------------------------------------------
def read_bytes(path: Path) -> Tuple[bytes, List[str]]:
    errors: List[str] = []
    try:
        return path.read_bytes(), errors
    except Exception as e:
        errors.append(f"read_bytes_error:{e}")
        return b"", errors

# ------------------------------------------------------------
# Deterministic text reader (multi-encoding)
# ------------------------------------------------------------
def read_text(path: Path, encodings=("utf-8", "latin-1")) -> Tuple[str, str, List[str]]:
    """
    Try multiple encodings, return (text, encoding_used, errors).
    Deterministic: always tries encodings in the same order.
    """
    errors: List[str] = []
    raw, raw_errors = read_bytes(path)
    errors.extend(raw_errors)

    if not raw:
        return "", None, errors

    for enc in encodings:
        try:
            return raw.decode(enc, errors="ignore"), enc, errors
        except Exception as e:
            errors.append(f"decode_error:{enc}:{e}")

    # Fallback: empty text
    return "", None, errors

# ------------------------------------------------------------
# Canonical Phase‑1 metadata
# ------------------------------------------------------------
def make_metadata(extractor_name: str, path: Path) -> Dict[str, Any]:
    """
    Phase‑1 metadata is minimal:
      - extractor: name of extractor
      - asset_id: deterministic asset identifier (filename)
    No version, no schema_version, no spec_id, no timestamps.
    """
    return {
        "extractor": extractor_name,
        "asset_id": path.name,
    }
