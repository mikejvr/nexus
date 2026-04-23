"""
gltf_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .gltf, .glb
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import struct


def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []
    ext = path.suffix.lower()

    # ------------------------------------------------------------
    # Deterministic byte/text read (Phase‑1)
    # ------------------------------------------------------------
    raw, raw_errors = ext_dna.read_bytes(path)
    errors.extend(raw_errors)

    text, encoding, text_errors = ext_dna.read_text(path)
    errors.extend(text_errors)

    # Cap raw to 128 KB for deterministic scanning
    buf = raw[:128 * 1024]
    size = len(buf)

    # ------------------------------------------------------------
    # GLB (binary glTF)
    # ------------------------------------------------------------
    if ext == ".glb":
        technical: Dict[str, Any] = {
            "type": "glb_dna",
            "filename": path.name,
            "format": "GLB",
            "file_size_bytes": size,
            "header_snippet": "",
            "is_valid_glb": False,
            "version_field": None,
            "json_chunk_length": None,
            "bin_chunk_length": None,
        }

        # Header snippet
        if buf:
            technical["header_snippet"] = buf[:128].decode("latin-1", errors="ignore")

        # GLB header detection (structural only)
        if len(buf) >= 12:
            try:
                magic, version, total_len = struct.unpack("<III", buf[:12])
                if magic == 0x46546C67:  # 'glTF'
                    technical["is_valid_glb"] = True
                    technical["version_field"] = version

                    # JSON chunk length (structural only)
                    if len(buf) >= 20:
                        json_len, json_type = struct.unpack("<II", buf[12:20])
                        technical["json_chunk_length"] = json_len

                    # BIN chunk length (structural only)
                    bin_offset = 20 + (json_len if "json_len" in locals() else 0)
                    if bin_offset + 8 <= len(buf):
                        bin_len, bin_type = struct.unpack("<II", buf[bin_offset:bin_offset+8])
                        technical["bin_chunk_length"] = bin_len

            except Exception as e:
                errors.append(f"glb_header_error:{e}")

        metadata = ext_dna.make_metadata("glb_dna", path)
        return len(errors) == 0, technical, metadata, errors

    # ------------------------------------------------------------
    # GLTF (JSON-based glTF)
    # ------------------------------------------------------------
    technical = {
        "type": "gltf_dna",
        "filename": path.name,
        "format": "GLTF",
        "file_size_bytes": size,
        "encoding": encoding,
        "header_snippet": "",
        "is_valid_json": False,
        "top_level_key_count": None,
    }

    # Header snippet
    if text:
        technical["header_snippet"] = text[:256]

    # Structural JSON validation only (no parsing)
    if text.strip().startswith("{") and text.strip().endswith("}"):
        technical["is_valid_json"] = True

        # Count top-level keys structurally (shallow heuristic)
        try:
            # Very shallow: count occurrences of `"key":`
            # Deterministic cap
            import re
            keys = re.findall(r'"([^"]+)"\s*:', text[:32 * 1024])
            technical["top_level_key_count"] = len(set(keys))
        except Exception:
            pass

    metadata = ext_dna.make_metadata("gltf_dna", path)
    return len(errors) == 0, technical, metadata, errors
