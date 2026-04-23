"""
phase1_orchestrator.py (updated to use Phase‑1 deterministic logging)

Phase‑1 deterministic extractor orchestrator.

This module:
- Performs extension‑based routing only
- Calls Phase‑1 DNA extractors
- Produces a canonical 4‑tuple: (success, technical, metadata, errors)
- No hashing, no entropy, no timestamps, no provenance, no forensic
- No CLIP, no PIL, no thumbnails, no relationships
- No logging side effects beyond deterministic logs
- No inference, no MIME detection, no heuristics
"""

from __future__ import annotations
from pathlib import Path
from typing import Tuple, Dict, Any, List

from src.phase1.utils.logging import log_info, log_error, log_debug, regen_log

# Routers (all Phase‑1 deterministic)
from src.extractors.raster_router import route as route_raster
from src.extractors.vector_router import route as route_vector
from src.extractors.document_router import route as route_document
from src.extractors.presentation_router import route as route_presentation
from src.extractors.spatial_router import route as route_spatial
from src.extractors.archive_router import route as route_archive
from src.extractors.logic_router import route as route_logic


# ---------------------------------------------------------------------------
# Extension → spec_id map (Phase‑1: static, deterministic)
# ---------------------------------------------------------------------------

SPEC_MAP = {
    "document": {".doc", ".docx", ".pdf", ".txt", ".rtf", ".xls", ".pub"},
    "visual": {".tga", ".xcf"},
    "raster": {
        ".psd", ".ps",".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
        ".gif", ".bmp", ".ico", ".psb", ".dds", ".dwg", ".exr"
    },
    "spatial": {
        ".obj", ".3ds", ".stl", ".fbx", ".ply", ".glb", ".gltf",
        ".mtl", ".max"
    },
    "vector": {".ai", ".cdr", ".svg", ".eps", ".fla"},
    "logic": {
        ".sql", ".js", ".php", ".py", ".json", ".xml", ".csv",
        ".xlsx", ".css", ".html", ".htm",  ".swf", ".sld",
        ".wmv", ".wma", ".flv", ".astro", ".ts"
    },
    "archive": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "presentation": {".pptx", ".ppt", ".ppj"},
}


def get_spec_id(ext: str) -> str:
    ext = ext.lower()
    for spec, exts in SPEC_MAP.items():
        if ext in exts:
            return spec
    return "logic"  # Phase‑1 fallback, deterministic


# ---------------------------------------------------------------------------
# Master router (Phase‑1 deterministic)
# ---------------------------------------------------------------------------

def route(ext_dna: Dict[str, Any], file_path: str) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    """
    Phase‑1 master router.
    Returns: (success, technical, metadata, errors)
    Deterministic logs are emitted via the Phase‑1 logging substrate.
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    spec_id = get_spec_id(ext)

    # Probe log: high level dispatch info
    log_info("ROUTER", "Master router dispatch", {"file": file_path, "extension": ext, "spec_id": spec_id})

    try:
        if spec_id == "raster":
            regen_log("route dispatch", {"spec": "raster", "file": file_path})
            return route_raster(ext_dna, file_path)

        if spec_id == "vector":
            regen_log("route dispatch", {"spec": "vector", "file": file_path})
            return route_vector(ext_dna, file_path)

        if spec_id == "document":
            regen_log("route dispatch", {"spec": "document", "file": file_path})
            return route_document(ext_dna, file_path)

        if spec_id == "presentation":
            regen_log("route dispatch", {"spec": "presentation", "file": file_path})
            return route_presentation(ext_dna, file_path)

        if spec_id == "spatial":
            regen_log("route dispatch", {"spec": "spatial", "file": file_path})
            return route_spatial(ext_dna, file_path)

        if spec_id == "archive":
            regen_log("route dispatch", {"spec": "archive", "file": file_path})
            return route_archive(ext_dna, file_path)

        # Default deterministic fallback
        regen_log("route dispatch", {"spec": "logic", "file": file_path})
        return route_logic(ext_dna, file_path)

    except Exception as exc:  # noqa: BLE001
        # Deterministic error logging; do not include nondeterministic metadata.
        log_error("ROUTER", "routing exception", {"file": file_path, "spec_id": spec_id, "error": str(exc)})
        # Return a deterministic failure tuple: (False, empty technical, empty metadata, errors list)
        return False, {}, {}, [f"routing exception: {str(exc)}"]
