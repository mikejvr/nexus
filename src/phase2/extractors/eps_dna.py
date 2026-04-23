"""
eps_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .eps, legacy .ai (non‑PDF)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte + text read (Phase‑1)
    # ------------------------------------------------------------
    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    text, encoding, text_errors = ext_dna.read_text(path)
    errors.extend(text_errors)

    # Cap raw to 128 KB for deterministic scanning
    buf = raw[:128 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "eps_dna",
        "filename": path.name,
        "format": "EPS",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "is_epsf": False,
        "has_pdfmark": False,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # EPSF structural hint
    # ------------------------------------------------------------
    if text.startswith("%!PS-Adobe") or "EPSF" in text[:256]:
        technical["is_epsf"] = True

    # ------------------------------------------------------------
    # pdfmark presence (structural only)
    # ------------------------------------------------------------
    if "pdfmark" in text:
        technical["has_pdfmark"] = True

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"\xFF\xD8\xFF": "JPEG",
        b"\x89PNG\r\n\x1a\n": "PNG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
    }

    try:
        found = []
        head = buf[:1024 * 1024]  # deterministic cap
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("eps_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
