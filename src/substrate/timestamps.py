from datetime import datetime, timezone


def now_utc_iso() -> str:
    """Return a deterministic UTC ISO timestamp (no microseconds)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
