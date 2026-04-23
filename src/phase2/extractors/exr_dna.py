"""
exr_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .exr
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import struct


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read (Phase‑1)
    # ------------------------------------------------------------
    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    # Cap to 4 KB for deterministic structural scanning
    header = raw[:4096]
    size = len(header)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "exr_dna",
        "filename": path.name,
        "format": "EXR",
        "file_size_bytes": size,
        "header_snippet": "",
        "is_valid_exr": False,
        "version_field": None,
        "flags": {
            "tiled": False,
            "long_names": False,
            "multipart": False,
            "non_image": False,
        },
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if header:
        technical["header_snippet"] = header[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # EXR magic + version field (structural only)
    # ------------------------------------------------------------
    if len(header) >= 8:
        try:
            magic, version_field = struct.unpack("<II", header[:8])
            if magic == 20000630:
                technical["is_valid_exr"] = True
                technical["version_field"] = version_field

                # Structural flag bits (no semantic interpretation)
                technical["flags"]["tiled"] = bool(version_field & (1 << 9))
                technical["flags"]["long_names"] = bool(version_field & (1 << 10))
                technical["flags"]["multipart"] = bool(version_field & (1 << 12))
                technical["flags"]["non_image"] = bool(version_field & (1 << 13))

        except Exception as e:
            errors.append(f"exr_header_error:{e}")

    # ------------------------------------------------------------
    # Embedded signatures (structural only)
    # ------------------------------------------------------------
    sigs = {
        b"\x89PNG": "PNG",
        b"\xFF\xD8\xFF": "JPEG",
        b"II*\x00": "TIFF_LE",
        b"MM\x00*": "TIFF_BE",
        b"PK\x03\x04": "ZIP",
        b"%PDF-": "PDF",
    }

    try:
        found = []
        head = header[:4096]  # deterministic cap
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("exr_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
