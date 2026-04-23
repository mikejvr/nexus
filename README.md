# NEXUS MVP (Phase‑1 → Phase‑2 → Phase‑4)

Deterministic, substrate‑safe pipeline with:

- Phase‑1: shard orchestration via `orchestrator_v0`
- Phase‑2: extractor router
- Phase‑4: lineage engine

## Commands

- `make lint` — static checks via ruff
- `make format` — deterministic formatting
- `make test` — unit tests
- `make pipeline` — Phase‑1 → Phase‑2 → Phase‑4 E2E
- `make drift-check` — fails if repo has uncommitted changes

Phase‑1 specific:

- `make healthcheck`
- `make regen`
- `make e2e`
- `make clean`
