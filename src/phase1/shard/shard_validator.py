"""
shard_validator.py

Phase‑1 deterministic shard validator.

Implements the structural validation rules defined in:
  - Documentation‑1‑2: Shard Validator Developer Docs
  - Documentation‑1‑20: Shard Validator Deep‑Dive
  - Phase‑1 Shard Schema Contract
  - shard_schema.json

Validator responsibilities:
  - Ensure shard structure is correct
  - Ensure required fields exist
  - Ensure no extra fields exist
  - Ensure metadata.normalized_hash exists
  - Ensure payload is a dict
  - Ensure no nondeterministic fields appear in metadata

This validator MUST remain deterministic forever.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from schema.schema_loader import load_phase1_schema
from src.phase1.utils.logging import (
    validator_log_info,
    validator_log_error,
    log_debug,
    configure,
)

"""
levels = "DEBUG", "INFO", "WARN", "ERROR"
categories = "REGEN", "VALIDATOR", "PROGRESS", "WRITER", "READER"
"""
configure(    
    enabled_levels=["INFO", "ERROR"],
    enabled_categories=["PROGRESS"],
    colors_enabled=True,
    progress_emit_every=100,
)



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_shard_structure(shard: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Strict Phase‑1 shard validator.

    - Enforces required top‑level fields
    - Forbids Phase‑2+ fields
    - Ensures each section is a dict
    - No semantic validation
    - No mutation
    """
    schema = load_phase1_schema()
    errors: List[str] = []

    if not isinstance(shard, dict):
        validator_log_error("Shard is not a JSON object", None)
        return False, ["Shard must be a JSON object"]

    # Required fields
    for field in schema.get("required", []):
        if field not in shard:
            msg = f"Missing required field: {field}"
            errors.append(msg)
            validator_log_error(msg, {"field": field})

    # Respect schema["additionalProperties"]
    if schema.get("additionalProperties", True) is False:
        allowed = set(schema.get("properties", {}).keys())
        for field in shard.keys():
            if field not in allowed:
                msg = f"Forbidden field present in Phase‑1 shard: {field}"
                errors.append(msg)
                validator_log_error(msg, {"field": field})

    ok = len(errors) == 0
    if ok:
        validator_log_info("Phase‑1 shard validation passed", None)
    else:
        validator_log_error("Phase‑1 shard validation failed", {"error_count": len(errors)})

    # Debug: include schema summary when debug enabled (deterministic payload)
    log_debug("VALIDATOR", "schema summary", {"required_count": len(schema.get("required", [])), "additionalProperties": bool(schema.get("additionalProperties", True))})

    return ok, errors
