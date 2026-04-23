"""
step_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .step, .stp (ISO‑10303 STEP files)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re


# Deterministic timestamp scrubber (Phase‑1 invariant)
_TIMESTAMP_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\b"
)


def _sanitize(text: str) -> str:
    # Replace timestamp-like values with deterministic placeholder
    return _TIMESTAMP_RE.sub("<TS>", text)


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic text + byte read
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
        "type": "step_dna",
        "filename": path.name,
        "format": "STEP",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "line_count": 0,

        # Structural text hints
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
        technical["is_text_file"] = technical["unicode_ratio"] < 0.20

    # ------------------------------------------------------------
    # Header snippet (sanitized) + line count
    # ------------------------------------------------------------
    if text:
        snippet = text[:256]
        snippet = _sanitize(snippet)
        technical["header_snippet"] = snippet
        technical["line_count"] = text.count("\n") + 1

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"ISO-10303-21": "STEP_HEADER",
        b"HEADER;": "STEP_HEADER_BLOCK",
        b"ENDSEC;": "STEP_ENDSEC",
        b"DATA;": "STEP_DATA_BLOCK",
        b"FILE_DESCRIPTION": "STEP_FILE_DESCRIPTION",
        b"FILE_NAME": "STEP_FILE_NAME",
        b"FILE_SCHEMA": "STEP_FILE_SCHEMA",
        b"AP214": "STEP_AP214_HINT",
        b"AP203": "STEP_AP203_HINT",
        b"\x89PNG": "PNG",
        b"\xFF\xD8\xFF": "JPEG",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
        b"Rar!\x1A\x07\x00": "RAR4",
        b"Rar!\x1A\x07\x01\x00": "RAR5",
    }

    try:
        found = []
        head = buf
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("step_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
