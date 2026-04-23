from src.phase2.extractor_router import run_extractor_router


def test_phase2_router_smoke() -> None:
    # Just ensure it runs without raising.
    run_extractor_router()
