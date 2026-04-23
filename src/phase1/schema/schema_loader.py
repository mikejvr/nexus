"""
schema_loader.py

Deterministic loader for Phase‑1 shard schema.
All modules must import the schema through this file.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

SCHEMA_PATH = Path(__file__).resolve().parent / "phase1_schema.json"


def load_phase1_schema() -> Dict[str, Any]:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
