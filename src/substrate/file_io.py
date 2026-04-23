"""
file_io.py

Phase‑1 deterministic file I/O utilities.

This module provides the ONLY allowed primitives for reading and writing JSON
within the Phase‑1 deterministic substrate.

Rules:
  - All writes MUST use canonical_json()
  - No timestamps, UUIDs, or nondeterministic metadata
  - No partial writes
  - No schema logic (Phase‑2)
  - No governance logic (Phase‑5)

This module MUST remain stable forever.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from src.phase1.canonical.canonical_json import canonical_json

# ---------------------------------------------------------------------------
# Directory utilities
# ---------------------------------------------------------------------------
def ensure_dir(path: str | Path) -> None:
    """
    Deterministic directory creation.
    Accepts str or Path. Always converts to Path before mkdir.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# JSON read/write utilities
# ---------------------------------------------------------------------------
def read_json(path: str | Path) -> Any:
    """
    Deterministic JSON read.
    """
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"failed to read JSON '{path}': {e}")
def write_json_canonical(path: str | Path, obj: Any) -> None:
    """
    Write an object to disk using canonical JSON.

    - Accepts str or Path
    - Writes are atomic: write to a temp file then replace
    - Deterministic byte‑for‑byte output
    """
    path = Path(path)
    ensure_dir(path.parent)

    tmp = path.with_suffix(path.suffix + ".tmp")

    with tmp.open("w", encoding="utf-8") as f:
        f.write(canonical_json(obj))

    tmp.replace(path)

def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def list_files(root: str, suffixes: Iterable[str] | None = None) -> list[str]:
    base = Path(root)
    if not base.exists():
        return []
    if suffixes is None:
        return [str(p) for p in base.rglob("*") if p.is_file()]
    suffixes = tuple(suffixes)
    return [str(p) for p in base.rglob("*") if p.is_file() and p.suffix in suffixes]
