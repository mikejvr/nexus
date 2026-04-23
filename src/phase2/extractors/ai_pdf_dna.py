"""
ai_pdf_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Targets: PDF‑compatible .ai files and generic PDFs
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re


# Minimal structural regexes (Phase‑1 safe)
_PDF_HEADER_RE = re.compile(r"%PDF-([0-9]\.[0-9])")
_XREF_RE = re.compile(r"\bxref\b", re.IGNORECASE)
_TRAILER_RE = re.compile(r"trailer", re.IGNORECASE)
_ENCRYPT_RE = re.compile(r"/Encrypt\b", re.IGNORECASE)


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # 1. Read raw bytes (Phase‑1 deterministic)
    # ------------------------------------------------------------
    raw, read_errors = ext_dna.read_bytes(path)
    errors.extend(read_errors)

    # Also get a text view for structural regex scanning
    text, _, text_errors = ext_dna.read_text(path)
    errors.extend(text_errors)

    # ------------------------------------------------------------
    # 2. Header snippet (first 128 bytes)
    # ------------------------------------------------------------
    header_snippet = raw[:128].decode("latin-1", errors="ignore") if raw else ""

    # ------------------------------------------------------------
    # 3. Structural PDF hints (Phase‑1 only)
    # ------------------------------------------------------------
    pdf_version = None
    has_xref = False
    has_trailer = False
    is_encrypted = False

    if text:
        m = _PDF_HEADER_RE.search(text)
        if m:
            pdf_version = m.group(1)

        if _XREF_RE.search(text):
            has_xref = True

        if _TRAILER_RE.search(text):
            has_trailer = True

        if _ENCRYPT_RE.search(text):
            is_encrypted = True

    # ------------------------------------------------------------
    # 4. Determine format label (AI_PDF vs PDF)
    # ------------------------------------------------------------
    ext = path.suffix.lower()
    if ext == ".ai" and pdf_version is not None:
        fmt = "AI_PDF"
    else:
        fmt = "PDF" if pdf_version is not None else "UNKNOWN"

    # ------------------------------------------------------------
    # 5. Phase‑1 payload (strict)
    # ------------------------------------------------------------
    payload: Dict[str, Any] = {
        "spec_id": "ai_pdf",
        "Format": fmt,
        "PDF_Version": pdf_version,
        "Has_XRef_Hint": has_xref,
        "Has_Trailer_Hint": has_trailer,
        "Is_Encrypted_Hint": is_encrypted,
        "Header_Snippet": header_snippet,
    }

    # ------------------------------------------------------------
    # 6. Metadata
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("ai_pdf_dna", path)

    success = len(errors) == 0
    return success, payload, metadata, errors
