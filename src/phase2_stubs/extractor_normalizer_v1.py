
"""
Extractor-Specific Normalizer v1 — Phase‑2
Applies extractor-specific normalization rules BEFORE Phase‑1 normalization.

Uses:
  - EXTRACTOR_SCHEMAS from extractor_schema_registry.py

Normalization rules supported:
  - lowercase
  - uppercase
  - int
  - float
  - list sorting (future extension)
  - enum normalization (future extension)

This module is:
  - deterministic
  - pure
  - side-effect free
  - schema-driven
"""

from extractor_schema_registry import EXTRACTOR_SCHEMAS


# ------------------------------------------------------------
# Primitive normalization helpers
# ------------------------------------------------------------
def _normalize_lowercase(value):
    if isinstance(value, str):
        return value.lower()
    return value


def _normalize_uppercase(value):
    if isinstance(value, str):
        return value.upper()
    return value


def _normalize_int(value):
    try:
        return int(value)
    except Exception:
        return value


def _normalize_float(value):
    try:
        return float(value)
    except Exception:
        return value


NORMALIZATION_FUNCS = {
    "lowercase": _normalize_lowercase,
    "uppercase": _normalize_uppercase,
    "int": _normalize_int,
    "float": _normalize_float,
}


# ------------------------------------------------------------
# Apply normalization rules to a single field
# ------------------------------------------------------------
def _apply_field_normalization(value, rule):
    if rule not in NORMALIZATION_FUNCS:
        return value
    return NORMALIZATION_FUNCS[rule](value)


# ------------------------------------------------------------
# Main entrypoint
# ------------------------------------------------------------
def normalize_extractor_payload(extractor: str, payload: dict) -> dict:
    """
    Applies extractor-specific normalization rules from ESR v1.

    Example:
      technical_dna:
        extension_original → lowercase
        color_space → uppercase
    """

    if extractor not in EXTRACTOR_SCHEMAS:
        # Unknown extractor → return payload unchanged
        return payload

    schema = EXTRACTOR_SCHEMAS[extractor]
    rules = schema.get("normalization", {})

    # Make a shallow copy to avoid mutating caller data
    normalized = dict(payload)

    for field, rule in rules.items():
        if field not in normalized:
            continue

        normalized[field] = _apply_field_normalization(
            normalized[field],
            rule
        )

    return normalized
