import argparse
from pathlib import Path

from src.substrate.constants import ASSETS_ROOT, UMS_ROOT
from src.substrate.file_io import list_files, write_text
from src.substrate.logging import log_info, log_error


def _cmd_healthcheck() -> int:
    log_info("Phase‑1 healthcheck: OK (stub).")
    return 0


def _cmd_regen(assets_root: str, ums_root: str) -> int:
    log_info(f"Regenerating shards from '{assets_root}' into '{ums_root}' (stub).")
    files = list_files(assets_root)
    for f in files:
        rel = Path(f).relative_to(assets_root)
        out = Path(ums_root) / rel
        write_text(str(out), f"UMS stub for {rel}\n")
    log_info(f"Regenerated {len(files)} shard(s).")
    return 0


def _cmd_e2e() -> int:
    log_info("Running Phase‑1 E2E determinism test (stub).")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="orchestrator_v0")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("healthcheck", help="Run Phase‑1 healthcheck.")

    regen_p = sub.add_parser("regen", help="Regenerate shards.")
    regen_p.add_argument("--assets-root", default=ASSETS_ROOT)
    regen_p.add_argument("--ums-root", default=UMS_ROOT)

    sub.add_parser("e2e", help="Run Phase‑1 E2E determinism test.")

    args = parser.parse_args(argv)

    if args.command == "healthcheck":
        code = _cmd_healthcheck()
    elif args.command == "regen":
        code = _cmd_regen(args.assets_root, args.ums_root)
    elif args.command == "e2e":
        code = _cmd_e2e()
    else:
        log_error(f"Unknown command: {args.command}")
        code = 1

    raise SystemExit(code)


if __name__ == "__main__":
    main()
