"""
jpeg_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .jpg, .jpeg
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

    # Cap to 64 KB for deterministic scanning
    buf = raw[:64 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "jpeg_dna",
        "filename": path.name,
        "format": "JPEG",
        "file_size_bytes": size,
        "header_snippet": "",
        "is_jpeg": False,
        "has_exif": False,
        "has_jfif": False,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # JPEG signature detection (structural only)
    # ------------------------------------------------------------
    if len(buf) >= 4 and buf[0:2] == b"\xFF\xD8":
        technical["is_jpeg"] = True

    # ------------------------------------------------------------
    # EXIF / JFIF structural hints
    # ------------------------------------------------------------
    if b"Exif" in buf[:4096]:
        technical["has_exif"] = True

    if b"JFIF" in buf[:4096]:
        technical["has_jfif"] = True

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"\x89PNG": "PNG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
    }

    try:
        found = []
        head = buf[:64 * 1024]  # deterministic cap
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("jpeg_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
