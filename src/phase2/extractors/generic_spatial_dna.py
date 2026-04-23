"""
generic_spatial_dna extractor (Phase‑1 safe)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .ext_dna import read_bytes, make_metadata


def extract(path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []
    raw, read_errors = read_bytes(path)
    errors.extend(read_errors)

    technical = {
        "type": "generic_spatial_dna",
        "filename": path.name,
        "Format": "GENERIC_SPATIAL",
        "Magic_Hex": raw[:8].hex(),
        "File_Size_Bytes": len(raw),
    }

    metadata = make_metadata("generic_spatial_dna")
    success = len(errors) == 0
    return success, technical, metadata, errors
