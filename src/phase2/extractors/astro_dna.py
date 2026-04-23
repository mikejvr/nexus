"""
astro_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .astro
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re


FRONTMATTER_RE = re.compile(r"^---(.*?)---", flags=re.DOTALL | re.MULTILINE)


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # 1. Read text (Phase‑1 deterministic)
    # ------------------------------------------------------------
    text, _, read_errors = ext_dna.read_text(path)
    errors.extend(read_errors)

    if not text:
        text = ""

    # ------------------------------------------------------------
    # 2. ASCII ratio (structural hint)
    # ------------------------------------------------------------
    raw_bytes = text.encode("latin-1", errors="ignore")
    size = len(raw_bytes)

    if size > 0:
        ascii_bytes = sum(1 for b in raw_bytes if b < 128)
        ascii_ratio = ascii_bytes / size
    else:
        ascii_ratio = 0.0

    # ------------------------------------------------------------
    # 3. Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    header_snippet = raw_bytes[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # 4. Minimal structural hints (Phase‑1 only)
    # ------------------------------------------------------------
    has_frontmatter = FRONTMATTER_RE.search(text) is not None

    # ------------------------------------------------------------
    # 5. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "astro",
        "Format": "ASTRO",
        "File_Size_Bytes": size,
        "ASCII_Ratio": ascii_ratio,
        "Has_Frontmatter_Hint": has_frontmatter,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 6. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("astro_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
