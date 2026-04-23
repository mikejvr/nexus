from pathlib import Path
from typing import Iterable


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def list_files(root: str, suffixes: Iterable[str] | None = None) -> list[str]:
    base = Path(root)
    if not base.exists():
        return []
    if suffixes is None:
        return [str(p) for p in base.rglob("*") if p.is_file()]
    suffixes = tuple(suffixes)
    return [str(p) for p in base.rglob("*") if p.is_file() and p.suffix in suffixes]
