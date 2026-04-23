"""
generic_presentation_dna extractor (Phase‑1 safe)
Fallback for unknown presentation formats.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .ext_dna import read_bytes, read_text, make_metadata


def extract(path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    raw, raw_errors = read_bytes(path)
    errors.extend(raw_errors)

    text, encoding, text_errors = read_text(path)
    errors.extend(text_errors)

    technical = {
        "type": "generic_presentation_dna",
        "filename": path.name,
        "Format": "GENERIC_PRESENTATION",
        "Encoding": encoding,
        "Header_Snippet": raw[:128].decode("latin-1", errors="ignore") if raw else "",
        "File_Size_Bytes": len(raw),
        "Is_Text_Like": bool(text),
    }

    metadata = make_metadata("generic_presentation_dna")
    success = len(errors) == 0
    return success, technical, metadata, errors
