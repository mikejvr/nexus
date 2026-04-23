"""
xlsx_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .xlsx (OOXML ZIP container)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import zipfile
from xml.etree import ElementTree



def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "xlsx_dna",
        "filename": path.name,
        "format": "XLSX",
        "zip_entries": [],
        "has_core_xml": False,
        "has_app_xml": False,
        "has_workbook": False,
        "sheet_names": [],
    }

    # ------------------------------------------------------------
    # ZIP container scan (Phase‑1 allowed)
    # ------------------------------------------------------------
    try:
        with zipfile.ZipFile(path, "r") as z:
            names = z.namelist()
            technical["zip_entries"] = names[:50]  # cap for determinism

            # Structural presence flags
            technical["has_core_xml"] = "docProps/core.xml" in names
            technical["has_app_xml"] = "docProps/app.xml" in names
            technical["has_workbook"] = "xl/workbook.xml" in names

            # --------------------------------------------------------
            # Sheet names (Phase‑1 shallow XML read only)
            # --------------------------------------------------------
            if technical["has_workbook"]:
                try:
                    raw = z.read("xl/workbook.xml")
                    root = ElementTree.fromstring(raw)
                    sheets = root.findall(".//{*}sheet")

                    sheet_list: List[str] = []
                    for s in sheets:
                        name = s.get("name")
                        if name:
                            sheet_list.append(name)

                    # Cap to deterministic limit
                    technical["sheet_names"] = sheet_list[:32]

                except Exception as e:
                    errors.append(f"sheet_parse_error:{e}")

    except Exception as e:
        return False, {}, {}, [f"zip_error:{e}"]

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("xlsx_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
