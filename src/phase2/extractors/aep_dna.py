"""
aep_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # 1. Read raw bytes (Phase‑1 deterministic)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    size = len(raw)

    # ------------------------------------------------------------
    # 2. ASCII ratio + text hint (Phase‑1 structural)
    # ------------------------------------------------------------
    if size > 0:
        ascii_bytes = sum(1 for b in raw if b < 128)
        ascii_ratio = ascii_bytes / size
    else:
        ascii_ratio = 0.0

    is_text = ascii_ratio > 0.80

    # ------------------------------------------------------------
    # 3. Header snippet (first 128 bytes, latin‑1 safe)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # 4. Minimal structural hints (Phase‑1 only)
    # ------------------------------------------------------------
    # AEP files often begin with "Adobe After Effects" or binary project signatures.
    has_after_effects_hint = "After Effects" in header_snippet

    # ------------------------------------------------------------
    # 5. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "aep",
        "Format": "AEP",
        "File_Size_Bytes": size,
        "ASCII_Ratio": ascii_ratio,
        "Is_Text_File_Hint": is_text,
        "Has_AfterEffects_Hint": has_after_effects_hint,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 6. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("aep_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
