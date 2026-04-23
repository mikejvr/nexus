"""
docx_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .docx (OOXML Word)
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
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    # Cap to 128 KB for deterministic structural scanning
    raw = raw[:128 * 1024]
    size = len(raw)

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "docx_dna",
        "filename": path.name,
        "format": "DOCX",
        "file_size_bytes": size,
        "is_zip": False,
        "header_snippet": "",
        "package_entries": [],
        "has_document_xml": False,
        "has_styles_xml": False,
        "has_numbering_xml": False,
        "has_fonttable_xml": False,
        "has_theme_xml": False,
        "has_comments_xml": False,
        "has_footnotes_xml": False,
        "has_endnotes_xml": False,
        "has_settings_xml": False,
        "has_media_folder": False,
        "has_embeddings_folder": False,
    }

    # ------------------------------------------------------------
    # Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    if raw:
        technical["header_snippet"] = raw[:128].decode("latin-1", errors="ignore")

    # ------------------------------------------------------------
    # ZIP container detection
    # ------------------------------------------------------------
    if raw.startswith(b"PK\x03\x04"):
        technical["is_zip"] = True

        try:
            with zipfile.ZipFile(path, "r") as z:
                names = z.namelist()

                # Deterministic cap on file list
                technical["package_entries"] = sorted(names)[:64]

                # Presence flags only — no parsing
                technical["has_document_xml"] = "word/document.xml" in names
                technical["has_styles_xml"] = "word/styles.xml" in names
                technical["has_numbering_xml"] = "word/numbering.xml" in names
                technical["has_fonttable_xml"] = "word/fontTable.xml" in names
                technical["has_theme_xml"] = "word/theme/theme1.xml" in names
                technical["has_comments_xml"] = "word/comments.xml" in names
                technical["has_footnotes_xml"] = "word/footnotes.xml" in names
                technical["has_endnotes_xml"] = "word/endnotes.xml" in names
                technical["has_settings_xml"] = "word/settings.xml" in names

                # Folder presence
                technical["has_media_folder"] = any(n.startswith("word/media/") for n in names)
                technical["has_embeddings_folder"] = any(n.startswith("word/embeddings/") for n in names)

        except Exception as e:
            errors.append(f"zip_error:{e}")

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("docx_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
