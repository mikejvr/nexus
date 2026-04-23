"""
fbx_dna extractor (Phase‑1 safe)
Supports: .fbx
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re
import struct

from .ext_dna import read_bytes, read_text, make_metadata


def extract(path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    ext = path.suffix.lower()
    errors: List[str] = []

    raw, raw_errors = read_bytes(path)
    errors.extend(raw_errors)

    technical = {
        "type": "fbx_dna",
        "filename": path.name,
        "Format": "FBX",
        "Is_Binary": False,
        "Version": None,
    }

    # Binary FBX starts with 'Kaydara FBX Binary'
    if raw.startswith(b"Kaydara FBX Binary"):
        technical["Is_Binary"] = True
        if len(raw) >= 27:
            technical["Version"] = struct.unpack("<I", raw[23:27])[0]
    else:
        # ASCII FBX: version appears in header
        try:
            text = raw.decode("latin-1", errors="ignore")
            m = re.search(r"FBXVersion:\s*(\d+)", text)
            if m:
                technical["Version"] = int(m.group(1))
        except Exception:
            pass

    metadata = make_metadata("fbx_dna")
    success = len(errors) == 0
    return success, technical, metadata, errors
