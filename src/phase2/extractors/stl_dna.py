"""
svg_dna extractor (Phase‑1 safe)
Supports: .svg
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re
import xml.etree.ElementTree as ET

from .ext_dna import read_bytes, read_text, make_metadata


# SVG namespace
SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def _count(root, tag):
    return len(root.findall(f".//{SVG_NS}{tag}"))


def _extract_viewbox(root):
    vb = root.get("viewBox")
    if not vb:
        return None
    parts = vb.replace(",", " ").split()
    try:
        nums = [float(x) for x in parts]
        if len(nums) == 4:
            return nums
    except Exception:
        pass
    return vb


def _extract_path_stats(root):
    paths = root.findall(f".//{SVG_NS}path")
    cmd_re = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]")
    total_cmds = 0
    for p in paths:
        d = p.get("d", "")
        total_cmds += len(cmd_re.findall(d))
    count = len(paths)
    avg = total_cmds / count if count > 0 else 0
    return {
        "Path_Count": count,
        "Total_Commands": total_cmds,
        "Avg_Commands_Per_Path": round(avg, 2),
    }


def _extract_fonts(root):
    fonts = set()

    # <text font-family="...">
    for t in root.findall(f".//{SVG_NS}text"):
        ff = t.get("font-family")
        if ff:
            fonts.add(ff.strip())

    # CSS inside <style>
    for style in root.findall(f".//{SVG_NS}style"):
        txt = style.text or ""
        matches = re.findall(r"font-family\s*:\s*([^;]+);", txt)
        for m in matches:
            fonts.add(m.strip())

    return sorted(fonts)


def _extract_colors(root):
    colors = {}
    for elem in root.iter():
        for attr in ("fill", "stroke"):
            val = elem.get(attr)
            if val and not val.startswith("url("):
                colors[val] = colors.get(val, 0) + 1
    return colors


def _detect_embedded_images(root):
    """
    Phase‑1: detect presence of embedded images, but do NOT decode.
    """
    images = []
    for img in root.findall(f".//{SVG_NS}image"):
        href = img.get(XLINK_HREF) or img.get("href")
        if not href:
            continue
        entry = {"href": href}
        if href.startswith("data:image/"):
            entry["Embedded"] = True
        else:
            entry["Embedded"] = False
        images.append(entry)
    return images


def extract(path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    raw, raw_errors = read_bytes(path)
    errors.extend(raw_errors)

    text, encoding, text_errors = read_text(path)
    errors.extend(text_errors)

    technical: Dict[str, Any] = {
        "type": "svg_dna",
        "filename": path.name,
        "Format": "SVG",
        "Encoding": encoding,
        "Header_Snippet": raw[:128].decode("latin-1", errors="ignore") if raw else "",
        "XML_Valid": False,
        "Root_Attributes": {},
        "ViewBox": None,
        "Width": None,
        "Height": None,
        "Element_Counts": {},
        "Path_Stats": {},
        "Fonts": [],
        "Colors": {},
        "Embedded_Images": [],
    }

    if not text:
        metadata = make_metadata("svg_dna")
        return False, technical, metadata, errors

    # Parse XML
    try:
        root = ET.fromstring(text)
        technical["XML_Valid"] = True
    except Exception as e:
        errors.append(f"xml_error:{e}")
        metadata = make_metadata("svg_dna")
        return False, technical, metadata, errors

    # Root attributes
    technical["Root_Attributes"] = {k: v for k, v in root.attrib.items()}

    # Width / Height
    technical["Width"] = root.get("width")
    technical["Height"] = root.get("height")

    # ViewBox
    technical["ViewBox"] = _extract_viewbox(root)

    # Element counts
    technical["Element_Counts"] = {
        "path": _count(root, "path"),
        "rect": _count(root, "rect"),
        "circle": _count(root, "circle"),
        "ellipse": _count(root, "ellipse"),
        "line": _count(root, "line"),
        "polyline": _count(root, "polyline"),
        "polygon": _count(root, "polygon"),
        "group": _count(root, "g"),
        "text": _count(root, "text"),
        "image": _count(root, "image"),
        "linearGradient": _count(root, "linearGradient"),
        "radialGradient": _count(root, "radialGradient"),
        "filter": _count(root, "filter"),
        "mask": _count(root, "mask"),
        "clipPath": _count(root, "clipPath"),
    }

    # Path stats
    technical["Path_Stats"] = _extract_path_stats(root)

    # Fonts
    technical["Fonts"] = _extract_fonts(root)

    # Colors
    technical["Colors"] = _extract_colors(root)

    # Embedded images (presence only)
    technical["Embedded_Images"] = _detect_embedded_images(root)

    metadata = make_metadata("svg_dna")
    success = len(errors) == 0
    return success, technical, metadata, errors
