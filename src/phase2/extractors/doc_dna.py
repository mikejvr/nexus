"""
doc_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .doc (OLE2 Word)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read (Phase‑1)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    # Cap to 128 KB for deterministic structural scanning
    raw = raw[:128 * 1024]
    size = len(raw)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "doc_dna",
        "filename": path.name,
        "format": "DOC",
        "file_size_bytes": size,
        "is_ole": False,
        "header_snippet": "",
        "has_worddocument_token": False,
        "has_table_token": False,
        "has_list_token": False,
        "has_section_token": False,
    }

    # ------------------------------------------------------------
    # OLE2 header detection
    # ------------------------------------------------------------
    if raw.startswith(b"\xD0\xCF\x11\xE0"):
        technical["is_ole"] = True

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes, deterministic)
    # ------------------------------------------------------------
    if raw:
        technical["header_snippet"] = raw[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # Structural ASCII token hints (Phase‑1 shallow only)
    # ------------------------------------------------------------
    try:
        text = raw.decode("latin-1", errors="ignore")

        if "WordDocument" in text:
            technical["has_worddocument_token"] = True

        if "Table" in text or "Tbl" in text:
            technical["has_table_token"] = True

        if "List" in text:
            technical["has_list_token"] = True

        if "Section" in text:
            technical["has_section_token"] = True

    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("doc_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
