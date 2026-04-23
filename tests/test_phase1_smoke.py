from src.phase1.orchestrator.orchestrator_v0 import _cmd_healthcheck


def test_phase1_healthcheck_smoke() -> None:
    assert _cmd_healthcheck() == 0
