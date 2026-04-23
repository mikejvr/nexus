"""
lineage_store.py

Phase‑1 minimal, deterministic, append‑only lineage store.

Responsibilities:
  - Maintain an append‑only list of lineage entries
  - Enforce idempotency by run_id
  - Never mutate or reorder existing entries
  - Never introduce nondeterministic fields
  - Persist lineage as canonical JSON using Phase‑1 canonical_json()

This is a constitutional substrate component.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.phase1.canonical.canonical_json import canonical_json


LINEAGE_FILENAME = "lineage.json"


@dataclass(frozen=True)
class LineageEntry:
    """
    Minimal Phase‑1 lineage entry.

    Matches lineage_schema.json:

      - run_id
      - extractor
      - asset_id
      - schema_version
      - extractor_version
      - normalized_hash
      - shard_path
    """

    run_id: str
    extractor: str
    asset_id: str
    schema_version: str
    extractor_version: str
    normalized_hash: str
    shard_path: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LineageStore:
    """
    Append‑only, idempotent lineage store.

    Backed by a single JSON file:

        { "entries": [ ... ] }

    Invariants:
      - entries are never reordered
      - entries are never mutated
      - entries are never deleted
      - run_id is unique (idempotency)
    """

    def __init__(self, root: Path) -> None:
        """
        Parameters
        ----------
        root : Path
            Directory under which lineage.json will be stored.
        """
        self._root = root
        self._path = root / LINEAGE_FILENAME
        self._entries: List[Dict[str, Any]] = []
        self._index_by_run_id: Dict[str, Dict[str, Any]] = {}

        self._load()

    # ------------------------------------------------------------------ #
    # Internal I/O
    # ------------------------------------------------------------------ #

    def _load(self) -> None:
        if not self._path.exists():
            self._entries = []
            self._index_by_run_id = {}
            return

        with self._path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        entries = data.get("entries", [])
        if not isinstance(entries, list):
            raise ValueError("lineage.json: 'entries' must be a list")

        self._entries = []
        self._index_by_run_id = {}

        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("lineage.json: each entry must be an object")
            run_id = entry.get("run_id")
            if not isinstance(run_id, str):
                raise ValueError("lineage.json: each entry must have string run_id")
            if run_id in self._index_by_run_id:
                # This should never happen if invariants are respected
                raise ValueError(f"lineage.json: duplicate run_id detected: {run_id}")
            self._entries.append(entry)
            self._index_by_run_id[run_id] = entry

    def _flush(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        payload = {"entries": self._entries}
        with self._path.open("w", encoding="utf-8") as f:
            f.write(canonical_json(payload))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def record_entry(self, entry: LineageEntry) -> None:
        """
        Record a new lineage entry in an append‑only, idempotent way.

        If an entry with the same run_id already exists, this is a no‑op.

        Parameters
        ----------
        entry : LineageEntry
            The lineage entry to record.
        """
        if entry.run_id in self._index_by_run_id:
            # Idempotent: do not append, do not modify existing entry
            return

        entry_dict = entry.to_dict()
        self._entries.append(entry_dict)
        self._index_by_run_id[entry.run_id] = entry_dict
        self._flush()

    def get_entry(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a lineage entry by run_id.

        Parameters
        ----------
        run_id : str
            The run identifier.

        Returns
        -------
        dict | None
            The lineage entry, or None if not found.
        """
        return self._index_by_run_id.get(run_id)

    def list_entries(self) -> List[Dict[str, Any]]:
        """
        Return all lineage entries in append‑only order.

        Returns
        -------
        list[dict]
            List of lineage entries.
        """
        # Return a shallow copy to avoid external mutation
        return list(self._entries)
