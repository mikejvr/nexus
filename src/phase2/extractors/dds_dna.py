from __future__ import annotations
"""
dds_dna.py
Phase‑1 deterministic DDS Technical DNA extractor.

Rules:
- stdlib only
- deterministic forever
- no timestamps, no randomness
- no hashing, no entropy
- no provenance, no thumbnails
- returns Phase‑1 4‑tuple: (success, technical, metadata, errors)
"""


from pathlib import Path
from typing import Any, Dict, List, Tuple

from .ext_dna import read_bytes, make_metadata


DDS_MAGIC = b"DDS "  # 0x44 0x44 0x53 0x20


def parse_dds_header(raw: bytes) -> Tuple[Dict[str, Any], List[str]]:
    """
    Minimal deterministic DDS header parser.
    Only extracts Phase‑1 safe technical fields.
    """
    errors: List[str] = []
    tech: Dict[str, Any] = {}

    if len(raw) < 128:
        errors.append("dds_header_too_small")
        return tech, errors

    # Magic
    magic = raw[0:4]
    if magic != DDS_MAGIC:
        errors.append("dds_bad_magic")
        return tech, errors

    # DDS_HEADER structure (first 128 bytes)
    # https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    try:
        import struct

        # DWORD size, flags, height, width, pitchOrLinearSize, depth, mipMapCount
        header = struct.unpack("<I I I I I I I", raw[4:4 + 28])

        size, flags, height, width, pitch, depth, mipmaps = header

        tech["magic"] = "DDS "
        tech["header_size"] = size
        tech["flags"] = flags
        tech["height"] = height
        tech["width"] = width
        tech["pitch_or_linear_size"] = pitch
        tech["depth"] = depth
        tech["mipmap_count"] = mipmaps

        # Pixel format (DDS_PIXELFORMAT) at offset 76
        pf_size, pf_flags, fourcc, rgb_bitcount = struct.unpack(
            "<I I I I", raw[76:76 + 16]
        )

        tech["pixel_format"] = {
            "size": pf_size,
            "flags": pf_flags,
            "fourcc": fourcc,
            "rgb_bitcount": rgb_bitcount,
        }

    except Exception as e:
        errors.append(f"dds_parse_error:{e}")

    return tech, errors


def extract_dds_dna(path: str) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    """
    Phase‑1 DDS extractor entrypoint.
    """
    p = Path(path)

    raw, read_errors = read_bytes(p)
    errors: List[str] = list(read_errors)

    if not raw:
        return False, {}, make_metadata("dds"), errors

    tech, header_errors = parse_dds_header(raw)
    errors.extend(header_errors)

    success = len(errors) == 0

    metadata = make_metadata("dds")
    metadata["asset_id"] = p.name  # Phase‑1 allowed

    return success, tech, metadata, errors


# Canonical Phase‑1 entrypoint
def extract(path: str):
    return extract_dds_dna(path)
