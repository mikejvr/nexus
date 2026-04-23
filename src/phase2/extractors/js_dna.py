"""
js_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .js
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

    # Cap raw to 64 KB for deterministic scanning
    buf = raw[:64 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "js_dna",
        "filename": path.name,
        "format": "JS",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "line_count": 0,
        "has_import": False,
        "has_export": False,
        "has_use_strict": False,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 256 chars)
    # ------------------------------------------------------------
    if text:
        technical["header_snippet"] = text[:256]
        technical["line_count"] = text.count("\n") + 1

        lower = text.lower()

        # Shallow structural hints only
        technical["has_import"] = "import " in lower
        technical["has_export"] = "export " in lower
        technical["has_use_strict"] = "'use strict'" in lower or '"use strict"' in lower

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
    metadata = ext_dna.make_metadata("js_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
