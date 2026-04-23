"""
archive_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: ZIP, RAR4/5, 7Z, GZIP, TAR, and Unknown archives
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple


def extract_archive_dna(ext_dna, file_path: str, ext: str) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    path = Path(file_path)
    ext = ext.lower()

    # ------------------------------------------------------------
    # 1. Read first 128 KB (Phase‑1 structural limit)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)
    raw = raw[:128 * 1024]

    # ------------------------------------------------------------
    # 2. Header‑level archive type detection (no deep parsing)
    # ------------------------------------------------------------
    if raw.startswith(b"PK\x03\x04"):
        archive_type = "ZIP"
    elif raw.startswith(b"Rar!\x1A\x07\x00"):
        archive_type = "RAR4"
    elif raw.startswith(b"Rar!\x1A\x07\x01\x00"):
        archive_type = "RAR5"
    elif raw.startswith(b"7z\xBC\xAF\x27\x1C"):
        archive_type = "7Z"
    elif raw.startswith(b"\x1F\x8B"):
        archive_type = "GZIP"
    elif ext in (".tar", ".tgz", ".tbz2", ".txz"):
        archive_type = "TAR"
    else:
        archive_type = "Unknown"

    # ------------------------------------------------------------
    # 3. Minimal embedded signature hints (structural only)
    # ------------------------------------------------------------
    sig_hints = []
    signatures = {
        b"\xFF\xD8\xFF": "JPEG",
        b"\x89PNG": "PNG",
        b"%PDF-": "PDF",
    }
    for sig, name in signatures.items():
        if sig in raw:
            sig_hints.append(name)

    # ------------------------------------------------------------
    # 4. Minimal version hints (RAR/7Z only)
    # ------------------------------------------------------------
    rar_version = None
    if archive_type == "RAR4":
        rar_version = "4"
    elif archive_type == "RAR5":
        rar_version = "5"

    seven_z_version = None
    if archive_type == "7Z" and len(raw) >= 8:
        major = raw[6]
        minor = raw[7]
        seven_z_version = f"{major}.{minor}"

    # ------------------------------------------------------------
    # 5. Header snippet (first 128 bytes, latin‑1 safe)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # 6. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "archive",
        "Archive_Type": archive_type,
        "RAR_Version_Hint": rar_version,
        "SevenZ_Version_Hint": seven_z_version,
        "Embedded_Signature_Hints": sig_hints,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 7. Metadata (Phase‑1 minimal)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("archive_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
