from src.phase1.orchestrator.orchestrator_v0 import main as phase1_main
from src.phase2.extractor_router import run_extractor_router
from src.phase4.lineage_engine import run_lineage_engine
from src.substrate.logging import log_info


def run_full_pipeline() -> None:
    log_info("Running full NEXUS pipeline (Phase‑1 → Phase‑2 → Phase‑4).")
    phase1_main(["healthcheck"])
    run_extractor_router()
    run_lineage_engine()


if __name__ == "__main__":
    run_full_pipeline()
