"""
idml_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .idml
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
        "type": "idml_dna",
        "filename": path.name,
        "format": "IDML",
        "file_size_bytes": size,
        "header_snippet": "",
        "is_zip_container": False,
        "package_entries": [],
        "has_designmap": False,
        "has_resources_folder": False,
        "has_stories_folder": False,
        "story_file_count": None,
        "embedded_signatures": [],
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if buf:
        technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # ZIP container detection
    # ------------------------------------------------------------
    if raw.startswith(b"PK\x03\x04"):
        technical["is_zip_container"] = True

        try:
            with zipfile.ZipFile(path, "r") as z:
                names = z.namelist()

                # Deterministic cap on file list
                technical["package_entries"] = sorted(names)[:64]

                # Structural presence flags only
                technical["has_designmap"] = "designmap.xml" in names
                technical["has_resources_folder"] = any(n.startswith("Resources/") for n in names)
                technical["has_stories_folder"] = any(n.startswith("Stories/") for n in names)

                # Story file count (structural only)
                story_files = [n for n in names if n.startswith("Stories/") and n.endswith(".xml")]
                technical["story_file_count"] = len(story_files)

        except Exception as e:
            errors.append(f"zip_error:{e}")

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
        head = buf[:128 * 1024]  # deterministic cap
        for sig, name in sigs.items():
            if sig in head:
                found.append(name)
        technical["embedded_signatures"] = sorted(found)[:16]
    except Exception:
        pass

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("idml_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
