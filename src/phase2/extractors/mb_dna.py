"""
mb_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .mb (Autodesk Maya Binary Scene)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic text + byte read (Phase‑1)
    # ------------------------------------------------------------
    text, encoding, text_errors = ext_dna.read_text(path)
    errors.extend(text_errors)

    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    # Cap raw to 128 KB (MB files can be large)
    buf = raw[:128 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "mb_dna",
        "filename": path.name,
        "format": "MB",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "line_count": 0,

        # Structural text hints (MB is binary, but we still compute ratios)
        "is_text_file": False,
        "ascii_ratio": 0.0,
        "unicode_ratio": 0.0,

        # Structural binary hints
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Text structural hints (even though .mb is binary)
    # ------------------------------------------------------------
    if raw:
        ascii_bytes = sum(1 for b in buf if b < 128)
        unicode_bytes = len(buf) - ascii_bytes

        technical["ascii_ratio"] = ascii_bytes / len(buf)
        technical["unicode_ratio"] = unicode_bytes / len(buf)

        # MB files are binary → unicode_ratio usually high
        technical["is_text_file"] = technical["unicode_ratio"] < 0.20

    # ------------------------------------------------------------
    # Header snippet + line count (if any text-like content)
    # ------------------------------------------------------------
    if text:
        technical["header_snippet"] = text[:256]
        technical["line_count"] = text.count("\n") + 1

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"maya": "MAYA_HINT",
        b"FBX": "FBX_HINT",
        b"PNG": "PNG_HINT",
        b"JPEG": "JPEG_HINT",
        b"\x89PNG": "PNG",
        b"\xFF\xD8\xFF": "JPEG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
        b"Rar!\x1A\x07\x00": "RAR4",
        b"Rar!\x1A\x07\x01\x00": "RAR5",
        b"OBJ": "OBJ_HINT",
        b"BLENDER": "BLEND_HINT",
    }

    try:
        found = []
        head = buf[:128 * 1024]
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("mb_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
