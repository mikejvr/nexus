# Phase‑1 Makefile
# Deterministic, minimal, substrate‑safe.
# No timestamps, no nondeterministic build steps.

PYTHON := python3

ASSETS_ROOT := assets
UMS_ROOT := ums

.PHONY: healthcheck regen e2e clean

# ---------------------------------------------------------------------------
# Healthcheck
# ---------------------------------------------------------------------------

healthcheck:
    @echo "Running Phase‑1 substrate healthcheck..."
    @$(PYTHON) -m src.phase1.orchestrator.orchestrator_v0 healthcheck

# ---------------------------------------------------------------------------
# Regenerate all shards
# ---------------------------------------------------------------------------

regen:
    @echo "Regenerating shards..."
    @$(PYTHON) -m src.phase1.orchestrator.orchestrator_v0 regen \
        --assets-root $(ASSETS_ROOT) \
        --ums-root $(UMS_ROOT)

# ---------------------------------------------------------------------------
# End‑to‑end determinism test
# ---------------------------------------------------------------------------

e2e:
    @echo "Running Phase‑1 E2E determinism test..."
    @$(PYTHON) -m src.phase1.orchestrator.orchestrator_v0 e2e

# ---------------------------------------------------------------------------
# Clean UMS output
# ---------------------------------------------------------------------------

clean:
    @echo "Cleaning UMS output..."
    @rm -rf $(UMS_ROOT)
