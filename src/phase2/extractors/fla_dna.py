"""
fla_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .fla (ZIP-based and legacy binary Adobe Animate/Flash)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import zipfile


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Deterministic byte read (Phase‑1)
    # ------------------------------------------------------------
    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    # Cap to 128 KB for deterministic scanning
    buf = raw[:128 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "fla_dna",
        "filename": path.name,
        "format": "FLA",
        "file_size_bytes": size,
        "is_zip_container": False,
        "is_legacy_binary_fla": False,
        "header_snippet": "",
        "package_entries": [],
        "has_domdocument_xml": False,
        "has_publishsettings_xml": False,
        "has_library_folder": False,
        "has_meta_inf": False,
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # ZIP container detection (modern FLA only)
    # ------------------------------------------------------------
    is_zip = len(raw) >= 4 and raw[0:4] == b"PK\x03\x04"
    technical["is_zip_container"] = is_zip

    if is_zip:
        try:
            with zipfile.ZipFile(path, "r") as z:
                names = z.namelist()

                # Deterministic cap on file list
                technical["package_entries"] = sorted(names)[:64]

                # Structural presence flags only
                technical["has_domdocument_xml"] = "DOMDocument.xml" in names
                technical["has_publishsettings_xml"] = "PublishSettings.xml" in names
                technical["has_library_folder"] = any(n.startswith("LIBRARY/") for n in names)
                technical["has_meta_inf"] = any(n.startswith("META-INF/") for n in names)

        except Exception as e:
            # DO NOT FAIL — record and continue
            errors.append(f"zip_error:{e}")
            technical["is_zip_container"] = False
            technical["is_legacy_binary_fla"] = True

    else:
        # ------------------------------------------------------------
        # Legacy binary FLA (Flash 8 / CS3 / CS4)
        # ------------------------------------------------------------
        technical["is_legacy_binary_fla"] = True

        sigs = {
            b"FWS": "FLASH_FWS_HEADER",
            b"CWS": "FLASH_CWS_HEADER",
            b"ZWS": "FLASH_ZWS_HEADER",
            b"SWF": "FLASH_SWF_HINT",
            b"\x89PNG": "PNG",
            b"\xFF\xD8\xFF": "JPEG",
        }

        found = []
        head = buf
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)

        technical["embedded_signatures"] = sorted(found)[:16]

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("fla_dna", path)

    # IMPORTANT:
    # Phase‑1 extractors only fail if read_bytes failed.
    success = len(raw_errors) == 0

    return success, technical, metadata, errors
