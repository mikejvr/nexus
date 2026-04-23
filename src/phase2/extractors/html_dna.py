"""
html_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .html, .htm
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

    # Cap raw to 128 KB for deterministic scanning
    buf = raw[:128 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "html_dna",
        "filename": path.name,
        "format": "HTML",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "has_doctype": False,
        "has_html_tag": False,
        "has_head_tag": False,
        "has_body_tag": False,
        "script_tag_count": 0,
        "link_tag_count": 0,
    }

    # ------------------------------------------------------------
    # Header snippet (first 256 chars)
    # ------------------------------------------------------------
    if text:
        technical["header_snippet"] = text[:256]

    # ------------------------------------------------------------
    # Structural presence checks (shallow, Phase‑1 safe)
    # ------------------------------------------------------------
    lower = text.lower() if text else ""

    technical["has_doctype"] = "<!doctype" in lower
    technical["has_html_tag"] = "<html" in lower
    technical["has_head_tag"] = "<head" in lower
    technical["has_body_tag"] = "<body" in lower

    # Deterministic tag counts (shallow regex-free scan)
    if lower:
        technical["script_tag_count"] = lower.count("<script")
        technical["link_tag_count"] = lower.count("<link")

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("html_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
