"""
gif_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .gif
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
        "type": "gif_dna",
        "filename": path.name,
        "format": "GIF",
        "file_size_bytes": size,
        "header_snippet": "",
        "is_gif": False,
        "version": None,
        "has_global_color_table": False,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # GIF signature + version (structural only)
    # ------------------------------------------------------------
    if len(buf) >= 6:
        sig = buf[:3].decode("ascii", errors="ignore")
        ver = buf[3:6].decode("ascii", errors="ignore")

        if sig == "GIF":
            technical["is_gif"] = True
            technical["version"] = ver

    # ------------------------------------------------------------
    # Global Color Table presence (structural only)
    # ------------------------------------------------------------
    if len(buf) >= 11:
        packed = buf[10]
        technical["has_global_color_table"] = bool(packed & 0b10000000)

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
    metadata = ext_dna.make_metadata("gif_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
