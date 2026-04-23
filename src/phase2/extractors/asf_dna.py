"""
asf_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: ASF / WMV / WMA container signatures
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


# ASF header GUID (16 bytes)
ASF_HEADER_GUID = b"\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C"


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # 1. Read raw bytes (Phase‑1 deterministic)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    # Limit to first 128 KB for structural scanning
    raw = raw[:128 * 1024]
    size = len(raw)

    # ------------------------------------------------------------
    # 2. Header snippet (first 128 bytes, latin‑1 safe)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore") if raw else ""

    # ------------------------------------------------------------
    # 3. Minimal ASF structural hints (Phase‑1 only)
    # ------------------------------------------------------------
    has_asf_header = raw.startswith(ASF_HEADER_GUID)

    # Minimal embedded signature hints (structural only)
    sig_hints = []
    signatures = {
        b"WMV": "WMV",
        b"WMA": "WMA",
        b"ASF": "ASF",
    }
    for sig, name in signatures.items():
        if sig in raw:
            sig_hints.append(name)

    # ------------------------------------------------------------
    # 4. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "asf",
        "Format": "ASF",
        "File_Size_Bytes": size,
        "Has_ASF_Header_Hint": has_asf_header,
        "Embedded_Signature_Hints": sig_hints,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 5. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("asf_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
