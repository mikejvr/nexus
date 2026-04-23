"""
dwg_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .dwg
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read (Phase‑1)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    # Cap to 4 MB for deterministic structural scanning
    buf = raw[:4 * 1024 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "dwg_dna",
        "filename": path.name,
        "format": "DWG",
        "file_size_bytes": size,
        "header_snippet": "",
        "dwg_version": None,
        "has_preview": False,
        "preview_type": None,
        "xrefs": [],
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # Version signature (AC10xx) — shallow structural hint
    # ------------------------------------------------------------
    try:
        m = re.search(rb"AC10\d\d", buf[:256])
        if m:
            technical["dwg_version"] = m.group(0).decode("latin-1", errors="ignore")
    except Exception as e:
        errors.append(f"version_parse_error:{e}")

    # ------------------------------------------------------------
    # Preview detection (PNG/BMP signatures)
    # ------------------------------------------------------------
    try:
        if b"\x89PNG" in buf:
            technical["has_preview"] = True
            technical["preview_type"] = "PNG"
        elif b"BM" in buf:
            technical["has_preview"] = True
            technical["preview_type"] = "BMP"
    except Exception:
        pass

    # ------------------------------------------------------------
    # XRef path tokens (ASCII heuristic, deterministic cap)
    # ------------------------------------------------------------
    try:
        xrefs = re.findall(rb"[A-Za-z]:\ \\[^\x00]{1,128}?\.dwg", buf, flags=re.IGNORECASE)
        decoded = sorted(set(x.decode("latin-1", errors="ignore") for x in xrefs))
        technical["xrefs"] = decoded[:16]
    except Exception as e:
        errors.append(f"xref_parse_error:{e}")

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"\x89PNG": "PNG",
        b"BM": "BMP",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
    }

    try:
        found = []
        for sig, name in sigs.items():
            if sig in buf:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("dwg_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
