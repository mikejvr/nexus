"""
ico_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .ico
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

    # Cap to 32 KB for deterministic scanning
    buf = raw[:32 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "ico_dna",
        "filename": path.name,
        "format": "ICO",
        "file_size_bytes": size,
        "header_snippet": "",
        "is_ico": False,
        "image_entry_count": None,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # ICO header detection (structural only)
    # ------------------------------------------------------------
    if len(buf) >= 6:
        try:
            # Reserved (2 bytes), Type (2 bytes), Count (2 bytes)
            reserved = int.from_bytes(buf[0:2], "little")
            icon_type = int.from_bytes(buf[2:4], "little")
            count = int.from_bytes(buf[4:6], "little")

            if reserved == 0 and icon_type == 1:
                technical["is_ico"] = True
                technical["image_entry_count"] = count

        except Exception as e:
            errors.append(f"ico_header_error:{e}")

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"\x89PNG": "PNG",
        b"BM": "BMP",
        b"\xFF\xD8\xFF": "JPEG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"%PDF-": "PDF",
        b"PK\x03\x04": "ZIP",
    }

    try:
        found = []
        head = buf[:32 * 1024]  # deterministic cap
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("ico_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
