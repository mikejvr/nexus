"""
Phase‑1 Orchestrator (v0)
Deterministic, substrate‑safe, CI‑compatible.

This unifies all prototype Phase‑1 behaviors:
- healthcheck
- regen (reader → validator → writer)
- e2e (determinism test)
- diff (optional)
"""

import argparse
from pathlib import Path

from src.substrate.logging import log_info, log_error
from src.substrate.constants import ASSETS_ROOT, UMS_ROOT
from src.substrate.file_io import list_files, read_text, write_text

# Phase‑1 modules
from src.phase1.shard_reader import read_shard
from src.phase1.shard_writer import write_shard
from src.phase1.shard_validator import validate_shard
from src.phase1.shard_merger import merge_shards
from src.phase1.shard_diff import diff_shards

# Canonical + invariants
from src.phase1.canonical.canonical_json import canonicalize_json
from src.phase1.canonical.hashing import compute_hash
from src.phase1.canonical.invariants import verify_invariants

# Schema
from src.phase1.schema.schema_loader import load_phase1_schema


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _cmd_healthcheck() -> int:
    log_info("Running Phase‑1 healthcheck...")

    # Check schema loads
    try:
        _ = load_phase1_schema()
        log_info("✓ Schema load OK")
    except Exception as e:
        log_error(f"Schema load failed: {e}")
        return 1

    # Check substrate helpers
    try:
        _ = canonicalize_json({"x": 1})
        _ = compute_hash("test")
        log_info("✓ Canonical + hashing OK")
    except Exception as e:
        log_error(f"Canonical/hashing failed: {e}")
        return 1

    log_info("Phase‑1 healthcheck PASSED")
    return 0


def _cmd_regen(assets_root: str, ums_root: str) -> int:
    log_info(f"Regenerating shards from '{assets_root}' → '{ums_root}'")

    files = list_files(assets_root, suffixes=[".json"])
    if not files:
        log_error("No input assets found.")
        return 1

    schema = load_phase1_schema()

    for f in files:
        rel = Path(f).relative_to(assets_root)
        out_path = Path(ums_root) / rel

        # 1. Read
        raw = read_text(f)
        shard = read_shard(raw)

        # 2. Canonicalize
        shard = canonicalize_json(shard)

        # 3. Validate
        validate_shard(shard, schema)

        # 4. Invariants
        verify_invariants(shard)

        # 5. Hash + write
        shard_hash = compute_hash(shard)
        write_shard(out_path, shard, shard_hash)

        log_info(f"✓ {rel} regenerated")

    log_info(f"Regenerated {len(files)} shard(s).")
    return 0


def _cmd_e2e(assets_root: str, ums_root: str) -> int:
    """
    Determinism test:
    - regen twice
    - diff outputs
    """
    log_info("Running Phase‑1 E2E determinism test...")

    tmpA = Path("tmp_e2e_A")
    tmpB = Path("tmp_e2e_B")

    for tmp in (tmpA, tmpB):
        if tmp.exists():
            for p in tmp.rglob("*"):
                if p.is_file():
                    p.unlink()
        tmp.mkdir(exist_ok=True)

    # First run
    _cmd_regen(assets_root, tmpA)

    # Second run
    _cmd_regen(assets_root, tmpB)

    # Diff
    diffs = diff_shards(tmpA, tmpB)
    if diffs:
        log_error("❌ Determinism FAILED: shard outputs differ")
        for d in diffs:
            log_error(f"DIFF: {d}")
        return 1

    log_info("✓ Determinism PASSED")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="orchestrator_v0")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("healthcheck")

    regen_p = sub.add_parser("regen")
    regen_p.add_argument("--assets-root", default=ASSETS_ROOT)
    regen_p.add_argument("--ums-root", default=UMS_ROOT)

    e2e_p = sub.add_parser("e2e")
    e2e_p.add_argument("--assets-root", default=ASSETS_ROOT)
    e2e_p.add_argument("--ums-root", default=UMS_ROOT)

    args = parser.parse_args(argv)

    if args.command == "healthcheck":
        code = _cmd_healthcheck()
    elif args.command == "regen":
        code = _cmd_regen(args.assets_root, args.ums_root)
    elif args.command == "e2e":
        code = _cmd_e2e(args.assets_root, args.ums_root)
    else:
        log_error(f"Unknown command: {args.command}")
        code = 1

    raise SystemExit(code)


if __name__ == "__main__":
    main()
