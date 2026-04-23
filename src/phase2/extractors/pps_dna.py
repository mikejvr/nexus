"""
pps_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .pps (PowerPoint Slide Show — legacy OLE2 format)
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

    # Cap raw to 64 KB (PPS files can be large)
    buf = raw[:64 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "pps_dna",
        "filename": path.name,
        "format": "PPS",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "line_count": 0,

        # Structural text hints (PPS is binary, but ratios still computed)
        "is_text_file": False,
        "ascii_ratio": 0.0,
        "unicode_ratio": 0.0,

        # Structural binary hints
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Text structural hints
    # ------------------------------------------------------------
    if raw:
        ascii_bytes = sum(1 for b in buf if b < 128)
        unicode_bytes = len(buf) - ascii_bytes

        technical["ascii_ratio"] = ascii_bytes / len(buf)
        technical["unicode_ratio"] = unicode_bytes / len(buf)

        # PPS is binary → unicode_ratio usually high
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
        b"\xD0\xCF\x11\xE0": "OLE2_HEADER",
        b"PPS": "PPS_HINT",
        b"PowerPoint": "PPS_TEXT_HINT",
        b"\x00\x6E\x1E\xF0": "PPT_ATOM_HINT",   # common record header pattern
        b"\x89PNG": "PNG",
        b"\xFF\xD8\xFF": "JPEG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"PK\x03\x04": "ZIP",                  # sometimes embedded
        b"%PDF-": "PDF",
        b"Rar!\x1A\x07\x00": "RAR4",
        b"Rar!\x1A\x07\x01\x00": "RAR5",
    }

    try:
        found = []
        head = buf[:64 * 1024]
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)

        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("pps_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
