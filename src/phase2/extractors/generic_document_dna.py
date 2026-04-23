"""
generic_dna.py — Phase‑1 generic fallback extractor
Deterministic, stdlib‑only, structural‑only.
"""

from __future__ import annotations

def extract_generic_dna(ext_dna, file_path: str, ext: str):
    """
    Phase‑1 generic fallback extractor.
    Returns: (success, payload, metadata, errors)
    """

    # ------------------------------------------------------------
    # Read entire file (bounded by ext_dna)
    # ------------------------------------------------------------
    raw = ext_dna.read_bytes(file_path, max_bytes=512 * 1024)

    header = raw[:64]
    footer = raw[-64:] if len(raw) >= 64 else raw

    # ------------------------------------------------------------
    # Structural ASCII vs non‑ASCII
    # ------------------------------------------------------------
    ascii_count = sum(1 for b in raw if b < 128)
    unicode_count = len(raw) - ascii_count

    # ------------------------------------------------------------
    # Minimal text‑likeness check (deterministic)
    # ------------------------------------------------------------
    is_text_like = False
    try:
        _ = raw.decode("latin-1")
        is_text_like = True
    except Exception:
        pass

    payload = {
        "spec_id": "generic",
        "Magic_Hex": header[:8].hex(),
        "Header_Hex_64": header.hex(),
        "Footer_Hex_64": footer.hex(),
        "File_Size_Bytes": len(raw),
        "ASCII_Byte_Count": ascii_count,
        "Unicode_Byte_Count": unicode_count,
        "Has_Unicode": unicode_count > 0,
        "Is_Text_Like": is_text_like,
    }

    metadata = ext_dna.make_metadata(file_path, ext)
    return True, payload, metadata, []
