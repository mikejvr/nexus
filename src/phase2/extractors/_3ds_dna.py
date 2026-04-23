"""
3ds_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .3ds
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import struct


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # 1. Read raw bytes (Phase‑1 deterministic)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    size = len(raw)

    # ------------------------------------------------------------
    # 2. ASCII ratio (coarse structural hint)
    # ------------------------------------------------------------
    if size > 0:
        ascii_bytes = sum(1 for b in raw if b < 128)
        ascii_ratio = ascii_bytes / size
    else:
        ascii_ratio = 0.0

    # ------------------------------------------------------------
    # 3. Header snippet (first 128 bytes, latin‑1 safe)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # 4. Minimal 3DS structural hints (no deep chunk walk)
    # ------------------------------------------------------------
    first_chunk_id = None
    first_chunk_length = None

    if len(raw) >= 6:
        try:
            first_chunk_id = struct.unpack("<H", raw[0:2])[0]
            first_chunk_length = struct.unpack("<I", raw[2:6])[0]
        except Exception as e:  # noqa: BLE001
            errors.append(f"3ds_header_parse_error:{e}")

    has_3ds_header_hint = first_chunk_id is not None and first_chunk_length is not None

    # ------------------------------------------------------------
    # 5. Phase‑1 payload (strict, structural‑only)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "3ds",
        "Format": "3DS",
        "File_Size_Bytes": size,
        "ASCII_Ratio": ascii_ratio,
        "Has_3DS_Header_Hint": has_3ds_header_hint,
        "First_Chunk_ID_Hint": first_chunk_id,
        "First_Chunk_Length_Hint": first_chunk_length,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 6. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("3ds_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
