#!/usr/bin/env bash
set -euo pipefail

echo "[Phase‑1] Running shard lifecycle..."
python3 -m src.phase1.orchestrator.orchestrator_v0 healthcheck
python3 -m src.phase1.orchestrator.orchestrator_v0 regen
python3 -m src.phase1.orchestrator.orchestrator_v0 e2e

echo "[Phase‑2] Running extractor router..."
python3 -m src.phase2.extractor_router

echo "[Phase‑4] Running lineage engine..."
python3 -m src.phase4.lineage_engine

echo "E2E pipeline completed successfully."
