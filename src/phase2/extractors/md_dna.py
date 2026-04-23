"""
md_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .md (Markdown text files)
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
        "type": "md_dna",
        "filename": path.name,
        "format": "MD",
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
    # Header snippet + line count
    # ------------------------------------------------------------
    if text:
        technical["header_snippet"] = text[:256]
        technical["line_count"] = text.count("\n") + 1

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"# ": "MD_HEADING_HINT",
        b"##": "MD_HEADING_HINT",
        b"- ": "MD_LIST_HINT",
        b"* ": "MD_LIST_HINT",
        b"[": "MD_LINK_HINT",
        b"![": "MD_IMAGE_HINT",
        b"```": "MD_CODEBLOCK_HINT",
        b"---": "MD_RULE_HINT",
        b"<!--": "HTML_COMMENT_HINT",
        b"<?xml": "XML_HINT",
        b"<html": "HTML_HINT",
        b"\x89PNG": "PNG",
        b"\xFF\xD8\xFF": "JPEG",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
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
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("md_dna", path)

    success = len(raw_errors) == 0
    return success, technical, metadata, errors
