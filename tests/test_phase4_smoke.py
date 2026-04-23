from src.phase4.lineage_engine import run_lineage_engine


def test_phase4_lineage_smoke() -> None:
    # Just ensure it runs without raising.
    run_lineage_engine()
