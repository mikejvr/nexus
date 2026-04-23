# ---------------------------------------------------------------------------
# Repo‑Level Makefile (Phase‑1 → Phase‑2 → Phase‑4)
# Deterministic, minimal, CI‑safe.
# ---------------------------------------------------------------------------

PYTHON := python3

# Phase‑1 passthrough
healthcheck:
    $(MAKE) -C src/phase1 healthcheck

regen:
    $(MAKE) -C src/phase1 regen

e2e:
    $(MAKE) -C src/phase1 e2e

clean:
    $(MAKE) -C src/phase1 clean

# ---------------------------------------------------------------------------
# Lint / Format / Tests
# ---------------------------------------------------------------------------

lint:
    ruff check src tests

format:
    ruff format src tests

test:
    pytest -q

# ---------------------------------------------------------------------------
# Full deterministic pipeline (Phase‑1 → Phase‑2 → Phase‑4)
# ---------------------------------------------------------------------------

pipeline:
    bash scripts/run_e2e.sh

# ---------------------------------------------------------------------------
# Drift detection (CI)
# ---------------------------------------------------------------------------

drift-check:
    git diff --exit-code || \
    ( echo "❌ Drift detected. Commit required." && exit 1 )
