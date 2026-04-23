"""
avi_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: AVI / RIFF containers
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

    # Limit to first 128 KB for structural scanning
    raw = raw[:128 * 1024]
    size = len(raw)

    # ------------------------------------------------------------
    # 2. Header snippet (first 128 bytes, latin‑1 safe)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore") if raw else ""

    # ------------------------------------------------------------
    # 3. Minimal AVI structural hints (Phase‑1 only)
    # ------------------------------------------------------------
    has_riff_header = False
    if len(raw) >= 12 and raw.startswith(b"RIFF") and raw[8:12] == b"AVI ":
        has_riff_header = True

    # Minimal embedded signature hints (structural only)
    sig_hints = []
    signatures = {
        b"AVI": "AVI",
        b"RIFF": "RIFF",
        b"LIST": "LIST",
    }
    for sig, name in signatures.items():
        if sig in raw:
            sig_hints.append(name)

    # ------------------------------------------------------------
    # 4. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "avi",
        "Format": "AVI",
        "File_Size_Bytes": size,
        "Has_RIFF_AVI_Header_Hint": has_riff_header,
        "Embedded_Signature_Hints": sig_hints,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 5. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("avi_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
