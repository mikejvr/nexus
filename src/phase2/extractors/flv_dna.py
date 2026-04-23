"""
flv_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .flv
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read (Phase‑1)
    # ------------------------------------------------------------
    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    # Cap to 128 KB for deterministic structural scanning
    buf = raw[:128 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "flv_dna",
        "filename": path.name,
        "format": "FLV",
        "file_size_bytes": size,
        "header_snippet": "",
        "is_valid_flv": False,
        "has_audio": False,
        "has_video": False,
        "version": None,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # FLV header detection (structural only)
    # ------------------------------------------------------------
    if len(buf) >= 9 and buf[:3] == b"FLV":
        technical["is_valid_flv"] = True
        technical["version"] = buf[3]

        flags = buf[4]
        technical["has_audio"] = bool(flags & 0b100)
        technical["has_video"] = bool(flags & 0b001)

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"\x89PNG": "PNG",
        b"\xFF\xD8\xFF": "JPEG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
    }

    try:
        found = []
        head = buf[:128 * 1024]  # deterministic cap
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("flv_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
