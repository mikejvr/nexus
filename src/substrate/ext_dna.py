from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractorDNA:
    name: str
    version: str
    description: str
