from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .ext_dna import read_bytes, make_metadata


def extract(path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []
    raw, read_errors = read_bytes(path)
    errors.extend(read_errors)

    header = raw[:64]
    footer = raw[-64:] if len(raw) >= 64 else raw

    ascii_bytes = sum(1 for b in raw if b < 128)
    unicode_bytes = len(raw) - ascii_bytes

    technical: Dict[str, Any] = {
        "type": "generic_raster_dna",
        "filename": path.name,
        "Format": "GENERIC",
        "Magic_Hex": header[:8].hex(),
        "Header_Hex_64": header.hex(),
        "Footer_Hex_64": footer.hex(),
        "File_Size_Bytes": len(raw),
        "ASCII_Byte_Count": ascii_bytes,
        "Unicode_Byte_Count": unicode_bytes,
        "High_ASCII_Flag": unicode_bytes > 0,
        "Is_Text_Like": False,
    }

    # simple text‑like heuristic
    try:
        raw.decode("utf-8")
        technical["Is_Text_Like"] = True
    except Exception:
        try:
            raw.decode("latin-1")
            technical["Is_Text_Like"] = True
        except Exception:
            pass

    metadata = make_metadata("generic_raster_dna")
    success = len(errors) == 0
    return success, technical, metadata, errors
