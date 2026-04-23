"""
xls_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .xls (OLE2 / BIFF)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read
    # ------------------------------------------------------------
    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "xls_dna",
        "filename": path.name,
        "format": "XLS",
        "header_snippet": raw[:64].hex() if raw else "",
        "file_size_bytes": len(raw),
        "is_ole": False,
        "has_biff_bof": False,
        "has_biff_eof": False,
        "sheet_name_tokens": [],
    }

    # ------------------------------------------------------------
    # OLE2 header detection
    # ------------------------------------------------------------
    if raw.startswith(b"\xD0\xCF\x11\xE0"):
        technical["is_ole"] = True

    # ------------------------------------------------------------
    # BIFF structural markers (BOF/EOF)
    # ------------------------------------------------------------
    if b"\x09\x08" in raw or b"\x08\x09" in raw:
        technical["has_biff_bof"] = True

    if b"\x0A\x00" in raw:
        technical["has_biff_eof"] = True

    # ------------------------------------------------------------
    # Heuristic sheet name tokens (ASCII only, deterministic cap)
    # ------------------------------------------------------------
    try:
        text = raw.decode("latin-1", errors="ignore")

        # Very shallow heuristic: "Sheet" + printable chars
        tokens = re.findall(r"Sheet[^\x00-\x1F]{0,32}", text)

        # Deduplicate + deterministic cap
        unique = sorted(set(tokens))
        technical["sheet_name_tokens"] = unique[:16]

    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("xls_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
