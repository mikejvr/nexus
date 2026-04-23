"""
css_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .css
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic text read (Phase‑1)
    # ------------------------------------------------------------
    text, encoding, text_errors = ext_dna.read_text(path)
    errors.extend(text_errors)

    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    size = len(raw)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "css_dna",
        "filename": path.name,
        "format": "CSS",
        "file_size_bytes": size,
        "encoding": encoding,
        "line_count": 0,
        "rule_count": 0,
        "import_count": 0,
        "media_query_count": 0,
        "header_snippet": "",
        "sample_selectors": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 256 chars)
    # ------------------------------------------------------------
    if text:
        technical["header_snippet"] = text[:256]

    # ------------------------------------------------------------
    # Structural counts
    # ------------------------------------------------------------
    if text:
        lines = text.splitlines()
        technical["line_count"] = len(lines)

        # Very shallow rule heuristic: count '{'
        technical["rule_count"] = text.count("{")

        # @import and @media counts
        technical["import_count"] = text.count("@import")
        technical["media_query_count"] = text.count("@media")

        # --------------------------------------------------------
        # Sample selectors (very shallow heuristic)
        # --------------------------------------------------------
        # Match "selector {"
        selector_pattern = re.compile(r"([^{]+)\{")
        selectors: List[str] = []

        for m in selector_pattern.finditer(text):
            sel = m.group(1).strip()
            if sel:
                selectors.append(sel)
            if len(selectors) >= 16:
                break

        technical["sample_selectors"] = selectors

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("css_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
