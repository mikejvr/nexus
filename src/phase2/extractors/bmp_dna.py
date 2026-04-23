"""
bmp_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .bmp
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
    # 2. ASCII ratio (structural hint)
    # ------------------------------------------------------------
    if size > 0:
        ascii_bytes = sum(1 for b in raw if b < 128)
        ascii_ratio = ascii_bytes / size
    else:
        ascii_ratio = 0.0

    # ------------------------------------------------------------
    # 3. Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore") if raw else ""

    # ------------------------------------------------------------
    # 4. Minimal BMP structural hints (Phase‑1 only)
    # ------------------------------------------------------------
    # BMP signature is ASCII "BM"
    has_bmp_header = raw.startswith(b"BM")

    # ------------------------------------------------------------
    # 5. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "bmp",
        "Format": "BMP",
        "File_Size_Bytes": size,
        "ASCII_Ratio": ascii_ratio,
        "Has_BMP_Header_Hint": has_bmp_header,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 6. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("bmp_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
