"""
Unified Extractor Router (Phase‑1 safe, deterministic)
Routes ALL extractors: spatial, raster, vector, document, generic.

Return contract:
    (success, technical, metadata, errors)
"""

from __future__ import annotations
from pathlib import Path
from typing import Tuple, Dict, Any, List

# -----------------------------
# Import ALL extractors
# -----------------------------
from src.phase2.extractors import (
    _3ds_dna,
    aep_dna,
    ai_pdf_dna,
    archive_dna,
    asf_dna,
    astro_dna,
    avi_dna,
    bmp_dna,
    cdr_dna,
    css_dna,
    csv_dna,
    dds_dna,
    doc_dna,
    docx_dna,
    dwg_dna,
    eps_dna,
    exr_dna,
    fbx_dna,
    fla_dna,
    flv_dna,
    gif_dna,
    gltf_dna,
    html_dna,
    ico_dna,
    idml_dna,
    jpeg_dna,
    js_dna,
    json_dna,
    max_dna,
    mb_dna,
    mcr_dna,
    md_dna,
    mel_dna,
    mtl_dna,
    mzp_dna,
    obj_dna,
    pdf_dna,
    php_dna,
    ply_dna,
    png_dna,
    ppj_dna,
    pps_dna,
    ppt_dna,
    psd_dna,
    pub_dna,
    py_dna,
    qxp_dna,
    rps_dna,
    rtf_dna,
    sld_dna,
    step_dna,
    stl_dna,
    svg_dna,
    swf_dna,
    text_dna,
    tiff_dna,
    ts_dna,
    txt_dna,
    wav_dna,
    webp_dna,
    xls_dna,
    xlsx_dna,
    xml_dna,
    yaml_dna,
    generic_dna,
    generic_raster_dna,
    generic_spatial_dna,
    generic_vector_dna,
    generic_document_dna,
    generic_presentation_dna,
)


# ---------------------------------------------------------------------------
# Unified Router
# ---------------------------------------------------------------------------

def route(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    """
    Deterministic unified router.
    Dispatches based on file extension only.
    """

    ext = path.suffix.lower()

    # -----------------------------
    # Spatial formats
    # -----------------------------
    if ext == ".3ds":
        return _3ds_dna.extract(ext_dna, path)
    if ext == ".obj":
        return obj_dna.extract(ext_dna, path)
    if ext == ".stl":
        return stl_dna.extract(ext_dna, path)
    if ext == ".ply":
        return ply_dna.extract(ext_dna, path)
    if ext in (".glb", ".gltf"):
        return gltf_dna.extract(ext_dna, path)
    if ext == ".fbx":
        return fbx_dna.extract(ext_dna, path)
    if ext == ".max":
        return max_dna.extract(ext_dna, path)
    if ext == ".mb":
        return mb_dna.extract(ext_dna, path)
    if ext == ".mtl":
        return mtl_dna.extract(ext_dna, path)

    # -----------------------------
    # Raster formats
    # -----------------------------
    if ext in (".jpg", ".jpeg"):
        return jpeg_dna.extract(ext_dna, path)
    if ext == ".png":
        return png_dna.extract(ext_dna, path)
    if ext == ".gif":
        return gif_dna.extract(ext_dna, path)
    if ext == ".bmp":
        return bmp_dna.extract(ext_dna, path)
    if ext in (".tif", ".tiff"):
        return tiff_dna.extract(ext_dna, path)
    if ext == ".webp":
        return webp_dna.extract(ext_dna, path)
    if ext in (".psd", ".ps"):
        return psd_dna.extract(ext_dna, path)
    if ext == ".exr":
        return exr_dna.extract(ext_dna, path)
    if ext == ".ico":
        return ico_dna.extract(ext_dna, path)
    if ext == ".dds":
        return dds_dna.extract(ext_dna, path)
    if ext == ".dwg":
        return dwg_dna.extract(ext_dna, path)

    # -----------------------------
    # Vector formats
    # -----------------------------
    if ext in (".ai", ".pdf"):
        return ai_pdf_dna.extract(ext_dna, path)
    if ext == ".eps":
        return eps_dna.extract(ext_dna, path)
    if ext == ".svg":
        return svg_dna.extract(ext_dna, path)
    if ext == ".cdr":
        return cdr_dna.extract(ext_dna, path)

    # -----------------------------
    # Document formats
    # -----------------------------
    if ext == ".txt":
        return txt_dna.extract(ext_dna, path)
    if ext == ".json":
        return json_dna.extract(ext_dna, path)
    if ext == ".xml":
        return xml_dna.extract(ext_dna, path)
    if ext in (".yml", ".yaml"):
        return yaml_dna.extract(ext_dna, path)
    if ext == ".pdf":
        return pdf_dna.extract(ext_dna, path)

    # -----------------------------
    # Fallbacks
    # -----------------------------
    # Spatial fallback
    if ext in (".mesh", ".geo", ".geom"):
        return generic_spatial_dna.extract(ext_dna, path)

    # Raster fallback
    if ext in (".raw", ".bin"):
        return generic_raster_dna.extract_generic_raster_dna(ext_dna, path, ext)

    # Vector fallback
    if ext in (".vec", ".vct"):
        return generic_vector_dna.extract(ext_dna, path)

    # Document fallback
    return generic_document_dna.extract(ext_dna, path)
