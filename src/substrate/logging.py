"""
logging.py

Phase‑1 deterministic logging substrate.

Implements the canonical logging contract defined in:
  - Documentation‑1‑7: Logging Specification Developer Docs
  - Phase‑1 Shard Writer Logging Format
  - Phase‑1 Determinism Rules

Logging goals:
  - Deterministic, stable, machine‑parsable logs
  - Human‑readable ANSI color (allowed in Phase‑1)
  - No timestamps
  - No nondeterministic metadata
  - No environment‑dependent formatting
  - No external dependencies

Log format (machine‑parsable):
  [LEVEL][CATEGORY] message | data=<canonical JSON or null>

Examples:
  [INFO][WRITER] writing shard | data={"asset_id":"foo","extractor":"bar"}
  [ERROR][MERGER] duplicate key detected | data={"key":"x"}

This module MUST remain stable forever.
"""

from __future__ import annotations

import json
import re
import threading
from typing import Any, Dict, Optional, Iterable, Set


# ANSI color codes (allowed in Phase‑1)
COLOR_INFO = "\033[94m"     # blue
COLOR_ERROR = "\033[91m"    # red
COLOR_DEBUG = "\033[90m"    # gray
COLOR_RESET = "\033[0m"

# Default enabled levels and categories (can be changed via configure)
_DEFAULT_LEVELS: Set[str] = {"INFO", "ERROR", "DEBUG"}
_DEFAULT_CATEGORIES: Set[str] = set()  # empty set means "all categories allowed"

# Internal configuration (module-level)
_lock = threading.Lock()
_enabled_levels: Set[str] = set(_DEFAULT_LEVELS)
_enabled_categories: Optional[Set[str]] = None  # None => all categories enabled
_colors_enabled: bool = True

# Progress counter state
_counter_lock = threading.Lock()
_counter_total: Optional[int] = None
_counter_value: int = 0
_counter_emit_every: int = 100  # default emit frequency
_counter_label: str = "PROGRESS"  # category used for progress logs


# Toggle categories if needed
LOG_SWITCH = True

NEXUS_LOG = {
    "ENGINE": LOG_SWITCH,
    "ROUTER": LOG_SWITCH,
    "EXTRACTOR": LOG_SWITCH,
    "SHARD": LOG_SWITCH,
    "ERROR": LOG_SWITCH,
}


def sanitize_metadata_keys(metadata_dict):
    """Remove XML namespaces from keys."""
    if not isinstance(metadata_dict, dict):
        return metadata_dict

    clean = {}
    for k, v in metadata_dict.items():
        clean_key = re.sub(r"\{.*\}", "", k)
        if v is not None:
            clean[clean_key] = v
    return clean


# ---------------------------------------------------------------------------
# Deterministic serialization
# ---------------------------------------------------------------------------

def _serialize_data(data: Optional[Dict[str, Any]]) -> str:
    """
    Deterministically serialize structured log data.

    Uses canonical-like JSON rules:
      - sort_keys=True
      - separators=(",", ":")
      - ensure_ascii=False

    Returns "null" if data is None.
    """
    if data is None:
        return "null"

    try:
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except Exception:
        # Fallback: best‑effort stringification (still deterministic)
        return json.dumps(str(data), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _format_line(level: str, category: str, msg: str, data: Optional[Dict[str, Any]], color: str) -> str:
    """
    Build the final log line string without printing.
    """
    payload = _serialize_data(data)
    line = f"[{level}][{category}] {msg} | data={payload}"
    if _colors_enabled:
        return f"{color}{line}{COLOR_RESET}"
    return line


def _should_emit(level: str, category: str) -> bool:
    """
    Determine whether a log line should be emitted based on current config.
    """
    if level not in _enabled_levels:
        return False
    if _enabled_categories is None:
        return True
    return category in _enabled_categories


def _emit(level: str, category: str, msg: str, data: Optional[Dict[str, Any]], color: str) -> None:
    """
    Emit a deterministic log line if allowed by configuration.
    """
    if not _should_emit(level, category):
        return
    line = _format_line(level, category, msg, data, color)
    # Use a single print call to avoid interleaving in multi-threaded runs.
    print(line)


# ---------------------------------------------------------------------------
# Public logging API (leveled)
# ---------------------------------------------------------------------------

def log_info(category: str, msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    _emit("INFO", category, msg, data, COLOR_INFO)


def log_error(category: str, msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    _emit("ERROR", category, msg, data, COLOR_ERROR)


def log_debug(category: str, msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    _emit("DEBUG", category, msg, data, COLOR_DEBUG)


# ---------------------------------------------------------------------------
# Configuration API (deterministic toggles)
# ---------------------------------------------------------------------------

def configure(
    *,
    enabled_levels: Optional[Iterable[str]] = None,
    enabled_categories: Optional[Iterable[str]] = None,
    colors_enabled: Optional[bool] = True,
    progress_emit_every: Optional[int] = True,
    progress_label: Optional[str] = None,
) -> None:
    """
    Configure logging behavior.

    - enabled_levels: iterable of level names to enable (e.g., ["INFO","ERROR"])
      If None, keeps current setting.
    - enabled_categories: iterable of categories to enable. If None => all categories enabled.
      To disable all categories (emit nothing), pass an empty iterable.
    - colors_enabled: True/False to enable ANSI colors. If None, keep current.
    - progress_emit_every: integer frequency for progress emission (>=1).
    - progress_label: category label used for progress logs (default "PROGRESS").
    """
    global _enabled_levels, _enabled_categories, _colors_enabled, _counter_emit_every, _counter_label

    with _lock:
        if enabled_levels is not None:
            _enabled_levels = set(str(x).upper() for x in enabled_levels)
        if enabled_categories is None:
            _enabled_categories = None
        else:
            # empty iterable => empty set (no categories allowed)
            _enabled_categories = set(str(x) for x in enabled_categories)
        if colors_enabled is not None:
            _colors_enabled = bool(colors_enabled)
        if progress_emit_every is not None:
            if int(progress_emit_every) < 1:
                raise ValueError("progress_emit_every must be >= 1")
            _counter_emit_every = int(progress_emit_every)
        if progress_label is not None:
            _counter_label = str(progress_label)


def enable_all_levels() -> None:
    with _lock:
        global _enabled_levels
        _enabled_levels = set(_DEFAULT_LEVELS)


def disable_level(level: str) -> None:
    with _lock:
        _enabled_levels.discard(level.upper())


def enable_category(category: str) -> None:
    with _lock:
        global _enabled_categories
        if _enabled_categories is None:
            # currently all categories enabled; convert to explicit set containing this one
            _enabled_categories = {category}
        else:
            _enabled_categories.add(category)


def disable_category(category: str) -> None:
    with _lock:
        global _enabled_categories
        if _enabled_categories is None:
            # convert to explicit set of all except the disabled one is not possible deterministically,
            # so set to empty set to indicate "no categories" (caller should re-enable desired ones).
            _enabled_categories = set()
        else:
            _enabled_categories.discard(category)


# ---------------------------------------------------------------------------
# Progress counter API (thread-safe, deterministic emission)
# ---------------------------------------------------------------------------

def set_total_count(total: Optional[int]) -> None:
    """
    Set the expected total number of items to process (e.g., 7000).
    Pass None to unset.
    """
    global _counter_total, _counter_value
    with _counter_lock:
        if total is not None and int(total) < 0:
            raise ValueError("total must be non-negative or None")
        _counter_total = None if total is None else int(total)
        _counter_value = 0  # reset progress when total is set/changed


def increment_counter(step: int = 1, emit: bool = True) -> None:
    """
    Increment the progress counter by `step`. If `emit` is True, emit a progress log
    when the counter crosses multiples of the configured emit frequency.
    """
    global _counter_value
    if step < 0:
        raise ValueError("step must be non-negative")
    with _counter_lock:
        _counter_value += int(step)
        current = _counter_value
        total = _counter_total
        emit_every = _counter_emit_every

    if emit and (current % emit_every == 0 or (total is not None and current >= total)):
        # Build deterministic progress payload
        payload: Dict[str, Any] = {"count": current}
        
        if total is not None:
          payload["total"] = total
          pct = (current * 100) // total if total > 0 else 100
          payload["percent"] = pct

          # Add deterministic human-readable counter
          payload["human"] = f"[{current}/{total}]"
        _emit("INFO", _counter_label, "progress update", payload, COLOR_INFO)


def reset_counter() -> None:
    """
    Reset the counter to zero and unset total.
    """
    global _counter_value, _counter_total
    with _counter_lock:
        _counter_value = 0
        _counter_total = None


def get_counter() -> Dict[str, Optional[int]]:
    """
    Return a deterministic snapshot of the counter state.
    """
    with _counter_lock:
        return {"count": _counter_value, "total": _counter_total}


# ---------------------------------------------------------------------------
# Convenience helpers for regen/validator style logs
# ---------------------------------------------------------------------------

def regen_log(msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience wrapper for [regen] style logs; maps to INFO/REGEN category.
    """
    log_info("REGEN", msg, data)


def validator_log_info(msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    log_info("VALIDATOR", msg, data)


def validator_log_error(msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    log_error("VALIDATOR", msg, data)

# ---------------------------------------------------------------------------
# Canonical logging wrappers
# ---------------------------------------------------------------------------

def log_probe(category: str, msg: str, data: Optional[Dict[str, Any]] = None):
    """Phase‑1 deterministic INFO logging."""
    if not NEXUS_LOG.get(category, False):
        return
    log_info(category, msg, data)


def log_error_msg(category: str, msg: str, data: Optional[Dict[str, Any]] = None):
    """Phase‑1 deterministic ERROR logging."""
    if not NEXUS_LOG.get("ERROR", True):
        return
    log_error(category, msg, data)


# ---------------------------------------------------------------------------
# Shard logging
# ---------------------------------------------------------------------------

def log_shard_event(event: str, asset_id: str, extractor: str, filename: str, path: str, extra=None):
    payload = {
        "event": event,
        "asset_id": asset_id,
        "extractor": extractor,
        "filename": filename,
        "path": path,
    }
    if extra:
        payload.update(extra)

    log_info("SHARD", "shard:event", payload)


def log_shard_error(code: str, asset_id: str, extractor: str, detail: str):
    payload = {
        "code": code,
        "asset_id": asset_id,
        "extractor": extractor,
        "detail": detail,
    }
    log_error("SHARD", "shard:error", payload)

