"""
cdr_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .cdr
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read (Phase‑1)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    # Cap to 128 KB for deterministic structural scanning
    raw = raw[:128 * 1024]
    size = len(raw)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "cdr_dna",
        "filename": path.name,
        "format": "CDR",
        "file_size_bytes": size,
        "ascii_ratio": 0.0,
        "is_zip_container": False,
        "is_riff_container": False,
        "header_snippet": "",
    }

    # ------------------------------------------------------------
    # ASCII ratio (structural hint)
    # ------------------------------------------------------------
    if size > 0:
        ascii_bytes = sum(1 for b in raw if b < 128)
        technical["ascii_ratio"] = ascii_bytes / size

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes, deterministic)
    # ------------------------------------------------------------
    if raw:
        technical["header_snippet"] = raw[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # Minimal container hints (Phase‑1 structural only)
    # ------------------------------------------------------------
    # ZIP‑based CDR (CorelDRAW X4+)
    if raw.startswith(b"PK\x03\x04"):
        technical["is_zip_container"] = True

    # RIFF‑based CDR (CorelDRAW 5–13)
    if raw.startswith(b"RIFF"):
        technical["is_riff_container"] = True

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("cdr_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
