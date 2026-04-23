"""
csv_dna extractor — Phase‑1 deterministic, stdlib‑only, structural‑only
Supports: .csv
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import csv




def extract(ext_dna, path: Path) -> Tuple[bool, Dict[str, Any], Dict[str, Any], List[str]]:
    errors: List[str] = []

    # ------------------------------------------------------------
    # Technical DNA (Phase‑1 structural only)
    # ------------------------------------------------------------
    technical: Dict[str, Any] = {
        "type": "csv_dna",
        "filename": path.name,
        "format": "CSV",
        "row_count": 0,
        "column_count": None,
        "sample_rows": [],
    }

    # ------------------------------------------------------------
    # Deterministic CSV read (no dialect inference, no sniffing)
    # ------------------------------------------------------------
    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.reader(f)

            sample: List[List[str]] = []

            for i, row in enumerate(reader):
                # Capture first 5 rows only
                if i < 5:
                    sample.append(row)

                technical["row_count"] += 1

                # First row determines column count
                if technical["column_count"] is None:
                    technical["column_count"] = len(row)

            technical["sample_rows"] = sample

    except Exception as e:
        errors.append(f"csv_read_error:{e}")

    # ------------------------------------------------------------
    # Phase‑1 metadata (extractor + asset_id only)
    # ------------------------------------------------------------
    metadata = ext_dna.make_metadata("csv_dna", path)

    success = len(errors) == 0
    return success, technical, metadata, errors
