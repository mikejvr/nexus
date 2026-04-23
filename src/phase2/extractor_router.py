from src.substrate.logging import log_info
from src.substrate.ext_dna import ExtractorDNA


def run_extractor_router() -> None:
    dna = ExtractorDNA(
        name="router_stub",
        version="0.1.0",
        description="Phase‑2 extractor router stub.",
    )
    log_info(f"Phase‑2 extractor router running with DNA: {dna}")


if __name__ == "__main__":
    run_extractor_router()
