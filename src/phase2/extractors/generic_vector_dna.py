"""
generic_vector_dna extractor (Phase‑1 safe)
Fallback for unknown vector formats.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .ext_dna import read_bytes, read_text, make_metadata


def extract(path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # Read raw bytes (deterministic, no hashing/entropy)
    raw, raw_errors = read_bytes(path)
    errors.extend(raw_errors)

    # Try to read text (for structural hints)
    text, encoding, text_errors = read_text(path)
    errors.extend(text_errors)

    technical: Dict[str, Any] = {
        "type": "generic_vector_dna",
        "filename": path.name,
        "Format": "GENERIC_VECTOR",
        "Encoding": encoding,
        "Header_Snippet": raw[:128].decode("latin-1", errors="ignore") if raw else "",
        "File_Size_Bytes": len(raw),
        "Is_Text_Like": bool(text),
        "Detected_Tokens": [],
    }

    # Simple structural token scan (deterministic, no parsing)
    if text:
        tokens = []
        for t in ("<svg", "%!", "%%", "obj", "xref", "stream", "endobj"):
            if t in text[:5000]:
                tokens.append(t)
        technical["Detected_Tokens"] = tokens

    metadata = make_metadata("generic_vector_dna")
    success = len(errors) == 0
    return success, technical, metadata, errors
